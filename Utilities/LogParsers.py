import re
import os
import datetime

class Log:
    def __init__(self, filePath):
        self.fp = filePath
        with open(self.fp, "r") as f:
            self.logFileContents = f.read()
            self.filteredLines = None

class RedshiftMayaLog(Log):
    def getRedshiftLines(self):
        reg = re.compile(r"\[Redshift\]\s.*\r")
        lines = reg.findall(self.logFileContents)
        if lines == []:
            logger.critical("Could not find any redshift lines in {}".format(self.fp))
            return None
        self.filteredLines = lines
        return lines

    def getEachFrameRenderTime(self, returnDateTime = True):
        if not self.filteredLines:
            self.getRedshiftLines()
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
                timeMatches.append(datetime.time(hour = h, minute = m, second = s))
            else:
                timeMatches.append(":".join(tm))

        return timeMatches

    def getSavedFiles(self, fullPath = False):
        if not self.filteredLines:
            self.getRedshiftLines()

        reg = re.compile(r"Saved file '(.*)'")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if not fullPath:
            matches = [os.path.split(m)[-1] for m in matches]

        return matches

    def getSavedFrameNumbers(self):
        fileNames = self.getSavedFiles()
        return [int(f.split(".")[-2]) for f in fileNames]

    def getTotalRenderTime(self, returnDateTime = True):
        if not self.filteredLines:
            self.getRedshiftLines()

        reg = re.compile(r"total time for \d+ frames:.*")
        matches = []
        for line in self.filteredLines:
            matches += reg.findall(line)

        if len(matches) > 1:
            logger.critical("More than one total time found in {}".format(self.fp))
            return None

        line = matches[0].strip()

        reg = re.compile(r"(\d+[hms])")
        timeMatches = []
        tm = reg.findall(line)
        if returnDateTime:
            timeDict = {x[-1] : int(x[:-1]) for x in tm}
            s = timeDict["s"] if "s" in timeDict.keys() else 0
            m = timeDict["m"] if "m" in timeDict.keys() else 0
            h = timeDict["h"] if "h" in timeDict.keys() else 0
            totalTime = datetime.time(hour = h, minute = m, second = s)
        else:
            totalTime = ":".join(tm)

        return totalTime
