#pylint: disable-all
#Detect RedShift GPUs
self.rsGPUs = hydra_utils.get_redshift_preference("SelectedCudaDevices")
if self.rsGPUs:
    self.rsGPUs = self.rsGPUs.split(",")[:-1]
    self.rsGPUids = [x.split(":")[0] for x in self.rsGPUs]
    if len(self.rsGPUs) != len(self.rsGPUids):
        logger.warning("Problems parsing Redshift Preferences")
    logger.info("%s Redshift Enabled GPU(s) found on this node", len(self.rsGPUs))
    logger.debug("GPUs available for rendering are %s", self.rsGPUs)
else:
    logger.warning("Could not find available Redshift GPUs")

def softwareUpdaterLoop():
    """Checks for a new verison in the HYDRA environ, if one is found it starts
    a batch process to start the new verison and kills the current one running."""
    logger.debug("Checking for updates...")
    updateAnswer = hydra_utils.software_updater()
    if updateAnswer:
        logger.debug("Update found!")
        hydra_utils.launch_hydra_app("RenderNodeConsole", 10)
        socketServer.shutdown()
        sys.exit(0)
    else:
        logger.debug("No updates found")

def change_hydra_environ(newEnviron):
    if sys.platform == "win32":
        logger.info("Changing Hydra Environ to %s", newEnviron)
        proc = subprocess.Popen(["setx", "HYDRA", newEnviron], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        if out.find("SUCCESS") > 0:
            os.environ["HYDRA"] = newEnviron
            return True
        else:
            logger.critical("Could not change enviromental variable!")
            return False
    else:
        raise "Not Implemented!"

def launch_hydra_app(app, wait=0):
    """Primarily for killing the app and restarting it"""
    hydraPath = os.getenv("HYDRA")

    if not hydraPath:
        logger.error("HYDRA enviromental variable does not exit!")
        return None

    if sys.platform == "win32":
        execs = os.listdir(hydraPath)
        if not any([x.startswith(app) for x in execs]):
            logger.error("%s is not a vaild Hydra Win32 App", app)
            return None

    distFolder, _ = os.path.split(hydraPath)
    shortcutPath = os.path.join(distFolder, "_shortcuts")
    ext = ".bat" if sys.platform == "win32" else ".sh"
    script = "StartHydraApp{}".format(ext)
    scriptPath = os.path.join(shortcutPath, script)

    command = [scriptPath, app]
    if wait > 0:
        command += [str(int(wait))]
    subprocess.Popen(command, stdout=False)

def software_updater():
    hydraPath = os.getenv("HYDRA")

    if not hydraPath:
        logger.error("HYDRA enviromental variable does not exit!")
        return False

    hydraPath, thisVersion = os.path.split(hydraPath)
    try:
        currentVersion = float(thisVersion.split("_")[-1])
    except ValueError:
        logger.warning("Unable to obtain version number from file path. Assuming version number from Constants")
        currentVersion = Constants.VERSION

    versions = os.listdir(hydraPath)
    versions = [float(x.split("_")[-1]) for x in versions if x.startswith("dist_")]
    if not versions:
        return False
    highestVersion = max(versions)
    logger.debug("Comparing versions. Env: %s Latest: %s", currentVersion, highestVersion)
    if highestVersion > currentVersion:
        logger.info("Update found! Current Version is %s / New Version is %s", currentVersion, highestVersion)
        newPath = os.path.join(hydraPath, "dist_{}".format(highestVersion))
        response = change_hydra_environ(newPath)
        if not response:
            logger.critical("Could not update to newest environ for some reason!")
        return response
    else:
        return False


import xml.etree.ElementTree as ET

def get_redshift_preference(attribute):
    """Return an attribute from the Redshift preferences.xml file"""
    if sys.platform == "win32":
        try:
            tree = ET.parse("C:\\ProgramData\\Redshift\\preferences.xml")
        except IOError:
            logger.error("Could not find Redshift Preferences!")
            return None
    else:
        #TODO:Other platforms
        return None
    root = tree.getroot()
    perfDict = {c.attrib["name"]:c.attrib["value"] for c in root}
    try:
        return perfDict[attribute]
    except KeyError:
        logger.error("Could not find %s in Redshift Preferences!", attribute)
        return None
