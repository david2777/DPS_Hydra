# -*- mode: python -*-
block_cipher = None

a = Analysis(['FarmView.py'],
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
            ("assets/FarmView.png", "assets/FarmView.png", "DATA")]

pyz = PYZ(a.pure,
            a.zipped_data,
            cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = 'FarmView',
          debug = False,
          strip = False,
          upx = True,
          console = False,
          icon = "assets/FarmView.ico")
