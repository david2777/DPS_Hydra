# -*- mode: python -*-
a = Analysis(['FarmView.py'],
             pathex = ["\\"],
             hiddenimports = [],
             runtime_hooks = None)

a.datas += [("styleSheet.css", "styleSheet.css", "DATA")]
a.datas += [("Images/FarmView.png", "Images/FarmView.png", "DATA")]

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = "FarmView.exe",
          debug = False,
          strip = None,
          upx = True,
          console = False,
          icon = "Images/FarmView.ico")
