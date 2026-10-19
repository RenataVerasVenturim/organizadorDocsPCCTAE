# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('app.py', '.'), ('servidor.py', '.'), ('compactar_dossie.py', '.'), ('gerar_requerimento.py', '.'), ('requirements.txt', '.'), ('requerimentoSolicitacaoModelo.html', '.'), ('templates', 'templates'), ('static', 'static'), ('static\\script.js', 'static'), ('static\\style.css', 'static'), ('dadosdoServidor', 'dadosdoServidor'), ('documentosdoServidor', 'documentosdoServidor'), ('processoArquivos', 'processoArquivos'), ('requerimentoRSC', 'requerimentoRSC')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OrganizadorRSC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
