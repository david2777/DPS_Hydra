# -*- mode: python -*-
a = Analysis(['RenderNodeMain.py'],
             pathex = ["\\"],
             hiddenimports = [],
             runtime_hooks = None)

a.datas += [("styleSheet.css", "styleSheet.css", "DATA")]
a.datas += [("Images/refresh.png", "Images/refresh.png", "DATA")]
a.datas += [("Images/refresh.png", "Images/refresh.png", "DATA")]
a.datas += [("Images/RIcon.png", "Images/RIcon.png", "DATA")]
a.datas += [("Images/status/done.png", "Images/status/done.png", "DATA")]
a.datas += [("Images/status/inProgress.png", "Images/status/inProgress.png", "DATA")]
a.datas += [("Images/status/needsAttention.png", "Images/status/needsAttention.png", "DATA")]
a.datas += [("Images/status/none.png", "Images/status/none.png", "DATA")]
a.datas += [("Images/status/notStarted.png", "Images/status/notStarted.png", "DATA")]

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = "RenderNodeMain.exe",
          debug = False,
          strip = None,
          upx = True,
          console = True,
          icon = "Images/RenderNodeMain.ico")
