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

a.datas += [("assets/styleSheet.css", "assets/styleSheet.css", "DATA"),
            ("HydraSettings.cfg", "HydraSettings.cfg", "DATA"),
            ("assets/RenderNodeMain.png", "assets/RenderNodeMain.png", "DATA"),
            ("assets/Refresh.png", "assets/Refresh.png", "DATA"),
            ("assets/status/done.png", "assets/status/done.png", "DATA"),
            ("assets/status/inProgress.png", "assets/status/inProgress.png", "DATA"),
            ("assets/status/needsAttention.png", "assets/status/needsAttention.png", "DATA"),
            ("assets/status/none.png", "assets/status/none.png", "DATA"),
            ("assets/status/notStarted.png", "assets/status/notStarted.png", "DATA")]

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
          icon = "assets/RenderNodeMain.ico")
