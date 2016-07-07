# -*- mode: python -*-
block_cipher = None

a = Analysis(['RenderNodeMain.py'],
             pathex = ['.'],
             binaries = None,
             datas = None,
             hiddenimports = [],
             hookspath = [],
             runtime_hooks = [],
             excludes = [],
             win_no_prefer_redirects = False,
             win_private_assemblies = False,
             cipher = block_cipher)

a.datas += [("styleSheet.css", "styleSheet.css", "DATA"),
            ("HydraSettings.cfg", "HydraSettings.cfg", "DATA"),
            ("Images/RenderNodeMain.png", "Images/RenderNodeMain.png", "DATA"),
            ("Images/Refresh.png", "Images/Refresh.png", "DATA"),
            ("Images/status/done.png", "Images/status/done.png", "DATA"),
            ("Images/status/inProgress.png", "Images/status/inProgress.png", "DATA"),
            ("Images/status/needsAttention.png", "Images/status/needsAttention.png", "DATA"),
            ("Images/status/none.png", "Images/status/none.png", "DATA"),
            ("Images/status/notStarted.png", "Images/status/notStarted.png", "DATA")]

pyz = PYZ(a.pure,
            a.zipped_data,
            cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = 'RenderNodeMain',
          debug = False,
          strip = False,
          upx = True,
          console = False,
          icon = "Images/RenderNodeMain.ico")
