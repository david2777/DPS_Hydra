from distutils.core import setup
import py2exe
from os.path import expanduser, join

home = expanduser("~")

dataFiles = [("", [join(home, "Documents\\GitHub\\DPS_Hydra\\HydraSettings.cfg"),
                    join(home, "Documents\\GitHub\\DPS_Hydra\\styleSheet.css")]),

            ("Images", [join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\refresh.png"),
                        join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\RIcon.png")]),

            ("Images\\status", [join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\status\\done.png"),
                                join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\status\\inProgress.png"),
                                join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\status\\needsAttention.png"),
                                join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\status\\none.png"),
                                join(home, "Documents\\GitHub\\DPS_Hydra\\Images\\status\\notStarted.png")])]

setup(options = {
        "py2exe": {
            'unbuffered':True,
            'optimize':2,
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
      skip_archive = True,
      data_files = dataFiles,
      windows=["RenderNodeMain.py"],
      zipfile = None)
