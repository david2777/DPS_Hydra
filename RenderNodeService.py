import pythoncom 
import win32serviceutil 
import win32service 
import win32event 
import servicemanager 
import socket
import sys

from RenderNodeMain import *
from LoggingSetup import logger
 
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
        
    def heartbeatSVC(self, interval = 5000):
        host = Utils.myHostName()
        while True:
            try:
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = '%s'" % host)
            except Exception, e:
                logger.error(traceback.format_exc(e))
            
            if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                logger.debug("heartbeatSVC Break")
                break
 
    def main(self): 
        logger.info ('Starting in %s', os.getcwd())
        logger.info ('arglist %s', sys.argv)
        socketServer = RenderTCPServer()
        socketServer.createIdleLoop(5, socketServer.processRenderTasks)
        pulseThread = threading.Thread(target = self.heartbeatSVC, name = "heartbeatSVC", args = (60000,))
        pulseThread.start()
        logger.debug("Live! Live! Live!")
        while True:
            if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                socketServer.shutdown()
                logger.debug("RIP [*]")
                sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)
