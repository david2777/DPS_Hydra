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

a.datas += [("styleSheet.css", "styleSheet.css", "DATA"),
            ("HydraSettings.cfg", "HydraSettings.cfg", "DATA"),
            ("Images/FarmView.png", "Images/FarmView.png", "DATA")]

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
          icon = "Images/FarmView.ico")
