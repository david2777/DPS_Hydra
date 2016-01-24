#Standard
import pythoncom 
import win32serviceutil 
import win32service 
import win32event 
import servicemanager 
import socket
import sys
import logging.handlers
import logging
import subprocess
import os
import signal

#Hydra
from RenderNodeMain import *
from LoggingSetup import logger
 
#logger.setLevel(logging.INFO)

class NoSQLFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('SELECT * FROM')

logger.addFilter(NoSQLFilter())
 
class AppServerSvc (win32serviceutil.ServiceFramework): 
    _svc_name_ = "HydraRender" 
    _svc_display_name_ = "Hydra Render Service" 
 
    def __init__(self,args): 
        win32serviceutil.ServiceFramework.__init__(self,args) 
        self.hWaitStop = win32event.CreateEvent(None,0,0,None) 
        socket.setdefaulttimeout(60) 
 
    def SvcStop(self):
        logger.debug("SVC Stop")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        win32event.SetEvent(self.hWaitStop) 
 
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                              servicemanager.PYS_SERVICE_STARTED, 
                              (self._svc_name_,'')) 
        self.main()
        
 
    def main(self): 
        logger.info('Starting in {0}'.format(os.getcwd()))
        logger.info('arglist {0}'.format(sys.argv))
        
        socketServer = RenderTCPServer()
        socketServer.createIdleLoop(5, socketServer.processRenderTasks)
        logger.info("socketServer started!")
        
        self.externals = None
        try:
            command = sys.argv[0].replace("RenderNodeService.exe", "RenderNodeExternals.exe")
            self.externals = subprocess.Popen(command)
            logger.info("Externals Started @ {0}".format(command))
        except Exception, e:
            logger.error(e)
        
        logger.info("-------->Live!<--------")
        
        while True:
            if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                socketServer.shutdown()
                os.kill(self.externals.pid, signal.SIGTERM)
                logger.info("RIP [*]")
                sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)
