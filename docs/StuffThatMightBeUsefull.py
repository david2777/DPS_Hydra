
#Send a message from the Service
import win32ts
try:
    win32ts.WTSSendMessage(Server = win32ts.WTS_CURRENT_SERVER_HANDLE,
                            SessionId = win32ts.WTSGetActiveConsoleSessionId(),
                            Title = "Test Window",
                            Message = "This is just a test. There is nothing to worry about, human.",
                            Style = 1,
                            Timeout = 10,
                            Wait = True)
except:
    logger.error("Exception caught: {0}".format(traceback.format_exc()))
    raise
