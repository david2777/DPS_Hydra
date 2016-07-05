# -*- mode: python -*-
a = Analysis(['RenderNodeMain.py'],
             pathex = ["C:/Users/DPSPurple/Documents/GitHub/DPS_Hydra"],
             hiddenimports = [])

#a.datas += [("styleSheet.css", "styleSheet.css", "DATA")]
#a.datas += [("Images", "Images", "DIR")]
a.datas += [("LocalIcon", "Images/RIcon.png", "DATA")]
#a.datas += [("Images\\status", "Images\\status", "DIR")]

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
          console = False,
          icon = "Images/RenderNodeMain.ico")
