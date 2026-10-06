# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Halo's desktop wrapper.

Builds a Windows app folder (onedir, not onefile): Streamlit ships many
static/runtime data files that onefile's single-archive extraction handles
poorly, so onedir is the reliable choice here.

Build:
    pyinstaller desktop/halo.spec

Output: dist/Halo/Halo.exe plus its supporting files. Copy or shortcut the
whole "dist/Halo" folder; do not move Halo.exe out on its own.

Uses the original ring icon in assets/halo-shortcut.ico for the executable and
the native window/taskbar icon.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

PROJECT_ROOT = Path(SPECPATH).resolve().parent
ICON_PATH = PROJECT_ROOT / "assets" / "halo-shortcut.ico"

streamlit_datas, streamlit_binaries, streamlit_hidden = collect_all("streamlit")
halo_hidden = [
    "agent",
    "settings",
    "llm",
    "tools.ai_model",
    "tools.calendar_file",
    "tools.email_inbox",
    "tools.engineering_file",
    "tools.env_file",
    "tools.intent_router",
    "tools.notes_file",
    "tools.planner",
    "tools.search",
    "tools.task_file",
    "ui.components",
    "ui.styles",
]

project_datas = [
    (str(PROJECT_ROOT / "ui"), "ui"),
    (str(PROJECT_ROOT / "src"), "src"),
    (str(PROJECT_ROOT / "data"), "data"),
    (str(PROJECT_ROOT / ".streamlit"), ".streamlit"),
    (str(PROJECT_ROOT / "assets"), "assets"),
]

a = Analysis(
    [str(PROJECT_ROOT / "desktop" / "launcher.py")],
    pathex=[str(PROJECT_ROOT), str(PROJECT_ROOT / "desktop"), str(PROJECT_ROOT / "src")],
    binaries=streamlit_binaries,
    datas=streamlit_datas + project_datas,
    hiddenimports=streamlit_hidden + halo_hidden,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Halo",
    console=False,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
)

COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="Halo",
)
