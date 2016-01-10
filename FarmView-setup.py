from distutils.core import setup
import py2exe

setup(options = {
        "py2exe": {
            'bundle_files': 1,
            'compressed': True,
            "includes":["sip"],
            "dll_excludes": ["MSVCP90.dll", 
                             "API-MS-Win-Core-DelayLoad-L1-1-0.dll",
                             "API-MS-Win-Core-ErrorHandling-L1-1-0.dll",
                             "API-MS-Win-Core-File-L1-1-0.dll",
                             "API-MS-Win-Core-Handle-L1-1-0.dll",
                             "API-MS-Win-Core-Heap-L1-1-0.dll",
                             "API-MS-Win-Core-Interlocked-L1-1-0.dll",
                             "API-MS-Win-Core-IO-L1-1-0.dll",
                             "API-MS-Win-Core-LibraryLoader-L1-1-0.dll",
                             "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
                             "API-MS-Win-Core-Misc-L1-1-0.dll",
                             "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
                             "API-MS-Win-Core-Profile-L1-1-0.dll",
                             "API-MS-Win-Core-String-L1-1-0.dll",
                             "API-MS-Win-Core-Synch-L1-1-0.dll",
                             "API-MS-Win-Core-SysInfo-L1-1-0.dll",
                             "API-MS-Win-Core-ThreadPool-L1-1-0.dll",
                             "API-MS-Win-Core-Security-Base-L1-1-0.dll",
                             "IPHLPAPI.DLL",
                             "NSI.dll",
                             "WINNSI.DLL",
                             "WTSAPI32.dll",
                             "w9xpopen.exe"]
            }
      },
      console=["FarmView.py"],
      zipfile = None)
