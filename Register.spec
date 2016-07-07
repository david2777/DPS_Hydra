# -*- mode: python -*-
block_cipher = None

a = Analysis(['Register.py'],
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

a.datas += [("HydraSettings.cfg", "HydraSettings.cfg", "DATA")]

pyz = PYZ(a.pure,
            a.zipped_data,
            cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name = 'Register',
          debug = False,
          strip = False,
          upx = True,
          console = True,
          icon = "Images/Register.ico")
