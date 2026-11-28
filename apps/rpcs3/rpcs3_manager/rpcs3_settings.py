# SPDX-License-Identifier: GPL-3.0-or-later
"""The settings of the Settings tab (owner, 24-10-2026: the picture settings BC-250 PCSX2 Manager has, and what goes with
them), each one key of RPCS3's config.yml, which RPCS3 reads when a game starts: the picture (Video), the emulation
(Core), the sound (Audio) and the messages RPCS3 shows in a game (Miscellaneous). The values and defaults are RPCS3
0.0.43's (system_config.h, system_config_types.cpp). A setting is read from the file (RPCS3's default while the
file, or the line, is not there) and written one line at a time, every other line kept (userdata.yaml_set); RPCS3
writes the whole file itself when its own settings are saved. Never while RPCS3 runs. A game's own settings in
RPCS3 (custom_configs, the Screen setting column) come before these."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import userdata

CONFIG = "config.yml"
CHOICE, SWITCH, PERCENT = "choice", "switch", "percent"


@dataclass(frozen=True)
class Setting:
    """One setting: *key* of the top-level map *section* in config.yml. A CHOICE offers *choices* (value, as
    shown); a SWITCH is true or false; a PERCENT 0 to *top*."""
    key: str                            # the app's own name for it
    group: str                          # the box it is shown in
    label: str
    section: str
    name: str                           # the key in config.yml
    default: str
    kind: str = CHOICE
    choices: tuple[tuple[str, str], ...] = ()
    tip: str = ""
    top: int = 100


PICTURE, EMULATION, SOUND, MESSAGES = "Picture", "Emulation", "Sound", "Messages in a game"
RENDERERS = (("Vulkan", "Vulkan"), ("OpenGL", "OpenGL"))
SCALES = (("100", "Native (720p)"), ("150", "150 % (1080p)"), ("200", "200 % (1440p)"), ("300", "300 % (2160p)"))
ANISOTROPY = (("0", "As the game"), ("2", "2x"), ("4", "4x"), ("8", "8x"), ("16", "16x"))
MSAA = (("Auto", "As the game"), ("Disabled", "Off"))
VSYNC = (("Disabled", "Off"), ("Full", "On"), ("Adaptive", "Adaptive"))
FRAME_LIMITS = (("Auto", "Automatic"), ("Off", "Off"), ("30", "30"), ("50", "50"), ("60", "60"), ("120", "120"),
                ("Display", "The screen's rate"), ("PS3 Native", "As the PS3"), ("Infinite", "No limit"))
SCALING = (("Bilinear", "Bilinear"), ("Nearest", "Nearest"), ("FidelityFX Super Resolution", "FidelityFX Super "
                                                                                              "Resolution"))
PPU = (("Recompiler (LLVM)", "Recompiler (LLVM)"), ("Interpreter (static)", "Interpreter"))
SPU = (("Recompiler (LLVM)", "Recompiler (LLVM)"), ("Recompiler (ASMJIT)", "Recompiler (ASMJIT)"),
       ("Interpreter (dynamic)", "Interpreter (dynamic)"), ("Interpreter (static)", "Interpreter (static)"))
AUDIO = (("Cubeb", "Cubeb"), ("FAudio", "FAudio"), ("Null", "No sound"))
SETTINGS: tuple[Setting, ...] = (
    Setting("renderer", PICTURE, "Renderer", "Video", "Renderer", "Vulkan", CHOICE, RENDERERS,
            "How RPCS3 draws: Vulkan on the BC-250. OpenGL is slower and helps only when Vulkan fails."),
    Setting("scale", PICTURE, "Resolution scale", "Video", "Resolution Scale", "100", CHOICE, SCALES,
            "The size RPCS3 draws the picture at, in percent of the PS3's 1280 × 720. 150 % fills a 1080p screen "
            "sharply, 300 % a 4K one. A higher one asks more of the GPU and breaks some games."),
    Setting("anisotropy", PICTURE, "Anisotropic filtering", "Video", "Anisotropic Filter Override", "0", CHOICE,
            ANISOTROPY, "Sharper textures seen at an angle, such as a road ahead. As the game leaves it to the game."),
    Setting("msaa", PICTURE, "Anti-aliasing (MSAA)", "Video", "MSAA", "Auto", CHOICE, MSAA,
            "Smooths jagged edges as the game asks for it. Off draws without it, which is faster."),
    Setting("vsync", PICTURE, "VSync", "Video", "VSync Mode", "Disabled", CHOICE, VSYNC,
            "Waits for the screen's refresh before it shows a frame. That stops tearing and adds a little delay. "
            "Adaptive waits only while the game keeps up."),
    Setting("framelimit", PICTURE, "Frame limit", "Video", "Frame limit", "Auto", CHOICE, FRAME_LIMITS,
            "How many frames a second RPCS3 lets a game draw. Automatic follows the game, and As the PS3 keeps "
            "the PS3's own pace."),
    Setting("scaling", PICTURE, "Output scaling", "Video", "Output Scaling Mode", "Bilinear", CHOICE, SCALING,
            "How RPCS3 scales the drawn picture to the screen. Bilinear is smooth, and Nearest keeps sharp pixels. "
            "FidelityFX Super Resolution is AMD's upscaler, sharper from a lower resolution scale."),
    Setting("stretch", PICTURE, "Fill the screen", "Video", "Stretch To Display Area", "false", SWITCH,
            tip="The picture stretched to fill the window for every game that has no Screen setting of its own "
                "in the Your games tab."),
    Setting("ppu", EMULATION, "PPU decoder", "Core", "PPU Decoder", "Recompiler (LLVM)", CHOICE, PPU,
            "How RPCS3 runs the PS3's main processor. The recompiler is fast, the interpreter exact and slow."),
    Setting("spu", EMULATION, "SPU decoder", "Core", "SPU Decoder", "Recompiler (LLVM)", CHOICE, SPU,
            "How RPCS3 runs the PS3's SPU cores. The LLVM recompiler is fastest once it has compiled a game's "
            "code. ASMJIT compiles quicker. An interpreter is slow."),
    Setting("audio", SOUND, "Sound output", "Audio", "Renderer", "Cubeb", CHOICE, AUDIO,
            "The library RPCS3 plays sound through. Cubeb is RPCS3's own choice on Linux."),
    Setting("volume", SOUND, "Volume", "Audio", "Master Volume", "100", PERCENT, top=200,
            tip="The game's sound, in percent. Above 100 is louder than the game."),
    Setting("buffering", SOUND, "Buffering", "Audio", "Enable Buffering", "true", SWITCH,
            tip="Keeps the sound a little ahead, so it does not crackle. Off gives less delay."),
    Setting("trophies", MESSAGES, "Trophy messages", "Miscellaneous", "Show trophy popups", "true", SWITCH,
            tip="A message in the game when you win a trophy."),
    Setting("shaders", MESSAGES, "Shader compilation message", "Miscellaneous", "Show shader compilation hint",
            "false", SWITCH, tip="A message in the game while RPCS3 compiles shaders, which it does the first "
                                 "time a game shows something new."),
)


def settings_path(home: Path) -> Path:
    return home / CONFIG


def _lines(home: Path) -> list[str]:
    path = settings_path(home)
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []


def read_settings(home: Path) -> dict[str, str]:
    """Every setting's value, the app's key to config.yml's value (RPCS3's default while it is not there)."""
    lines = _lines(home)
    values = {}
    for setting in SETTINGS:
        found = userdata.yaml_value(lines, setting.section, setting.name)
        values[setting.key] = found if found is not None else setting.default
    return values


def write_setting(home: Path, setting: Setting, value: str) -> None:
    """One line of config.yml set; the file made when there is none. OSError is the caller's; the caller makes
    sure RPCS3 does not run."""
    lines = _lines(home)
    userdata.yaml_set(lines, setting.section, setting.name, value)
    userdata.write_lines(settings_path(home), lines)
