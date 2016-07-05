# -*- mode: python -*-
a = Analysis(['SubmitterMain.py'],
             pathex = ["\\"],
             hiddenimports = [],
             runtime_hooks = None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = "SubmitterMain.exe",
          debug = False,
          strip = None,
          upx = True,
          console = False)
