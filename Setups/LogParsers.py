#Standard
import re
import os
import datetime

#Hydra
from Setups.LoggingSetup import logger

def getLog(hydraJob, logPath):
    jobType = hydraJob.jobType
    if jobType == "RedshiftRender":
        return RedshiftMayaLog(logPath)
    elif jobType == "MentalRayRender":
        return MentalRayMayaLog(logPath)
    else:
        return None

class Log(object):
    def __init__(self, filePath):
        self.fp = filePath
        with open(self.fp, "r") as f:
            self.logFileContents = f.read()
            self.filteredLines = None
        #Placeholders
        self.filterRegex = None
        self.savedFileRegex = None

    def __repr__(self):
        return "Hydra Log File @ {}".format(self.fp)

    def filterLines(self):
        """Filters lines not realted to rendering so subsequent regexs run faster.
        Requires a filterRegex to be defined in the target class."""
        reg = re.compile(self.filterRegex)
        lines = reg.findall(self.logFileContents)
        if not lines:
            logger.critical("Could not find any filtered lines in %s", self.fp)
            return None
        self.filteredLines = lines
        return lines

    def getSavedFiles(self, fullPath=False):
        """Gets a list of files from the log. Requires a savedFileRegex to be
        defined in the target class."""
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(self.savedFileRegex)
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if not fullPath:
            matches = [os.path.split(m)[-1] for m in matches]
        #pylint: disable=E0601
        uniqueMatches = [m for m in matches if m not in uniqueMatches]

        return uniqueMatches

    def getSavedFrameNumbers(self):
        """Gets a list of frame numbers assuing name.number.ext naming scheme."""
        frameNumbers = [int(f.split(".")[-2]) for f in self.getSavedFiles()]
        #pylint: disable=E0601
        uniqueFrames = [f for f in frameNumbers if f not in uniqueFrames]
        return uniqueFrames


class RedshiftMayaLog(Log):
    """A class for parsing Maya Render logs when rendering with Redshift4Maya"""
    filterRegex = r"\[Redshift\]\s.*[\r\n]"
    savedFileRegex = r"Saved file '(.*)'"

    def getEachFrameRenderTime(self, returnDateTime=True):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"Rendering time: .*\n*")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        reg = re.compile(r"(\d+[hms])")
        timeMatches = []
        for line in matches:
            tm = reg.findall(line)
            if returnDateTime:
                timeDict = {x[-1] : int(x[:-1]) for x in tm}
                s = timeDict["s"] if "s" in timeDict.keys() else 0
                m = timeDict["m"] if "m" in timeDict.keys() else 0
                h = timeDict["h"] if "h" in timeDict.keys() else 0
                timeMatches.append(datetime.timedelta(hours=h, minutes=m, seconds=s))
            else:
                timeMatches.append(str(datetime.timedelta(hours=h, minutes=m, seconds=s)))

        return timeMatches

    def getTotalRenderTime(self, returnDateTime=True):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"total time for \d+ frames:.*")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if len(matches) > 1:
            logger.critical("More than one total time found in %s", self.fp)
            return None

        elif len(matches) < 1:
            logger.info("No total frame time found in %s", self.fp)
            return None

        line = matches[0].strip()

        reg = re.compile(r"(\d+[hms])")
        tm = reg.findall(line)
        #pylint: disable=R0204
        if returnDateTime:
            timeDict = {x[-1] : int(x[:-1]) for x in tm}
            s = timeDict["s"] if "s" in timeDict.keys() else 0
            m = timeDict["m"] if "m" in timeDict.keys() else 0
            h = timeDict["h"] if "h" in timeDict.keys() else 0
            if h > 24:
                logger.critical("Critical! Log Parser is not setup to handle times longer than 24 hours yet...")
                return None
            totalTime = datetime.timedelta(hours=h, minutes=m, seconds=s)
        else:
            totalTime = ":".join(tm)

        return totalTime

    def getTotalFrameCount(self):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"total time for (\d+) frames:.*")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if len(matches) > 1:
            logger.critical("More than one total time found in %s", self.fp)
            return None

        elif len(matches) < 1:
            matches = [max(self.getSavedFrameNumbers())]

        return int(matches[0])

    def getAverageRenderTime(self):
        totalTime = self.getTotalRenderTime()
        if totalTime:
            frameCount = self.getTotalFrameCount()
            frameTime = totalTime / frameCount
            seconds = int(frameTime.total_seconds())

        else:
            frameTimes = self.getEachFrameRenderTime()
            if not frameTimes:
                logger.info("Could not find any frame render times in %s", self.fp)
                return None
            #Add up seconds, divide by frame count
            seconds = sum([int(ft.total_seconds()) for ft in frameTimes]) / len(frameTimes)

        frameTime = datetime.timedelta(seconds=seconds)

        return frameTime

class MentalRayMayaLog(Log):
    """A class for parsing Maya Render logs when rendering with MentalRay"""
    filterRegex = r"\d+\sMB.*[\r\n]"
    savedFileRegex = r"to image file (.*)\s\(frame"

    def getTotalFrameCount(self):
        return len(self.getSavedFrameNumbers())

    def getEachFrameRenderTime(self, returnDateTime=True):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"wallclock  (\d:\d{2}:\d{2}.\d{2})")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        frameCount = self.getTotalFrameCount()
        clockPerFrame = len(matches) / frameCount
        matches = matches[:(clockPerFrame * frameCount)]
        matchSplit = [matches[i:i + clockPerFrame] for i in xrange(0, len(matches), clockPerFrame)]

        timePerFrame = []
        for timeList in matchSplit:
            renderTimeList = []
            timeList = [l.split(":") for l in timeList]
            for t in timeList:
                h2s = 60 * 60 * int(t[0])
                m2s = 60 * int(t[1])
                s2s = int(t[2].split(".")[0])
                renderTimeList.append(sum([h2s, m2s, s2s]))
            timePerFrame.append(sum(renderTimeList))

        returnList = []
        if returnDateTime:
            for frame in timePerFrame:
                returnList.append(datetime.timedelta(seconds=frame))
        else:
            for frame in timePerFrame:
                returnList.append(str(datetime.timedelta(seconds=frame)))

        return returnList

    def getAverageRenderTime(self):
        timeList = self.getEachFrameRenderTime()
        timeList = [int(t.total_seconds()) for t in timeList]
        tSecs = sum(timeList) / len(timeList)
        return datetime.timedelta(seconds=tSecs)

    def getTotalRenderTime(self):
        timeList = self.getEachFrameRenderTime()
        timeList = [int(t.total_seconds()) for t in timeList]
        tSecs = sum(timeList)
        return datetime.timedelta(seconds=tSecs)

class FusionCompLog(Log):
    """Class for loading Fusion logs. NOTE: getSavedFiles returns a list of
    frames rather than file names since the Fusion log doesn't say file names."""

    filterRegex = r".*[\r\n]"
    savedFileRegex = r"Rendered frame (\d*) "

    def getTotalFrameCount(self):
        return len(self.getSavedFrameNumbers())

    def getAverageRenderTime(self):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"Average: (\d*.\d*) ")
        for line in self.filteredLines:
            search = reg.findall(line)
            if len(search) == 1:
                return datetime.timedelta(seconds=int(float(search[0])))

    def getTotalRenderTime(self):
        if not self.filteredLines:
            self.filterLines()

        if len(self.filteredLines) < 1:
            return None

        reg = re.compile(r"Total Time: (\d*h) (\d*m) (\d*.\d*s),")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if len(matches) == 1:
            match = matches[0]
        else:
            return None

        hour = int(match[0][:-1])
        minute = int(match[1][:-1])
        second = int(float(match[2][:-1]))

        second += hour * 60 * 60
        second += minute * 60

        return datetime.timedelta(seconds=second)