#pylint: disable-all
#Detect RedShift GPUs
self.rsGPUs = hydra_utils.getRedshiftPreference("SelectedCudaDevices")
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
    updateAnswer = hydra_utils.softwareUpdater()
    if updateAnswer:
        logger.debug("Update found!")
        hydra_utils.launchHydraApp("RenderNodeConsole", 10)
        socketServer.shutdown()
        sys.exit(0)
    else:
        logger.debug("No updates found")
