<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Design

This page lists every color of the suite, where it is defined and what it is for. A text color shows a sample
sentence in that color. Any other color shows a block. These are the surfaces, fills, borders and lines. The samples
are SVG files in `design/colors/`. A text sample sits on a dark or a light backdrop, whichever its color reads on. A
color with an opacity shows over a checkerboard. This page writes it as `#rrggbbaa`, and the Qt code as `#aarrggbb`.
`tools/make_design.py` writes this page. Change the listing there and run it.

The page has three parts:

- The rules say what makes each design recognizable.
- The color families say why each tint of a hue is there.
- The listings after them say where each color is used.

## The rules

A design is recognizable by a few colors used the same way everywhere. A palette that holds every color does not
make it recognizable. The suite and the development apps each have their own design. Neither is carried over to the
other.

### BC250 Bazzite Suite

- **The identity** is the purple of the board icon and the wiki, `#5835ce` with `#8a2be2`. The logo's purple is
  `#6a1b9a`. The apps' Gunmetal theme is part of it too, steel gray with the steel-blue accent `#7e97ad`. The font
  is Inter, with heavy titles. Every app has the icon of its category.
- **One theme for every app** comes from `core/bc250_core/theme.py`. The user chooses Gunmetal, Silver or Warm. The
  theme gives the surfaces, text and accent below. A border that shows under the mouse, with the focus or on what is
  chosen is silver, never the accent (owner, 05-11-2026). The thin border of every tooltip is silver too (owner,
  07-11-2026). An app adds no surface or text color of its own.
- **One state family** is the same in every theme. A state is an edge or a dot on the theme's surface. The family
  has these colors:
  - green `#2e7d32` for ok
  - orange `#ef6c00` for warn
  - red `#c62828` for bad
  - blue `#1565c0` for info
  - yellow `#fdd835` for running
  - gray `#3a3f4b` for neutral

  A header box or pill in the neutral state shows the blue as its edge (owner, 26-10-2026). It never shows the
  theme's dark edge color. The portal's pills are the exception (owner, 01-11-2026). They are rounded rectangles in a
  row that ends level with the suite's icon. They take the theme's window color at 59 %, so the wallpaper shows
  through. An active pill is solid and framed in the silver outline. A red button is the red, and `#b71c1c` when
  pressed. Active red `#8b0000` is a toggled-on state, never an error. Under the pointer it is `#a00000`.
- **Text in a state color sits on a dark surface** in the next lighter tint of the same hue. These are Material's 300
  tints:
  - red `#e57373`
  - orange `#ffb74d`
  - green `#81c784`
  - blue `#64b5f6`
  - purple `#ce93d8`

  They are there because the state fills read poorly as text on the dark views. The log in the check app uses them.
  A second tint of a hue is a deviation.
- **Brand and hardware colors stay what they are.** These are:
  - PlayStation blue and the face-button colors in the PlayStation apps
  - the pure colors of the light bar and the color wheel in BC-250 Controller
  - a game's own artwork
  - the gaming blue `#0a55b0` of the gaming apps, in the emulator managers

  The emulator managers' icon has been a silver controller with a blue light since 13-11-2026.
- **Anything else is a deviation.** Color families below lists each one with the app it is in. A new color goes
  into the family it belongs to, or it needs a reason here.

### The development apps

- **Nexus's design** is near-black ink `#010101`, silver text `#c0c0c0` and one teal `#17b6a7`. The teal is the
  icon's, and it colors every link, title and icon. Nothing else is used. A Nexus app takes Nexus's design (owner,
  26-10-2026). The font is Inter, with heavy titles.
- **The apps in `dev/`** have this design in their windows, and the Nexus icon. Nexus Release Tool is one of them.
  Their design comes from core's `nexus.py`, a theme for core's widgets. An app sets it with
  `create_app(theme=NEXUS)`. The theme has ink surfaces, silver text and the teal accent.
- **Their states**, such as the working tree and a build, use the apps' state family, since a build passes or fails
  there too.

## Color families

This part lists every tint of each hue in the BC250 Bazzite Suite, and why it is there. The **Kind** column says what a tint is:

- *the family* is the suite's state color
- *text tint* is its lighter tint for text on a dark surface
- *brand or icon* is a color that belongs to something else, such as PlayStation, a ported tool or an icon
- *hardware* is a color the device shows
- *deviation* is a second color for a job the family already has a color for

There is no deviation. The last ones were unified on 26-10-2026.

### Red

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#c62828](design/colors/block-c62828.svg) | `#c62828` | the family | Bad: failed, an error or a problem. The red buttons use it too. |
| ![#b71c1c](design/colors/block-b71c1c.svg) | `#b71c1c` | the family | A red button pressed or under the pointer, in the bisect apps and **Clean up logs**. |
| ![#8b0000](design/colors/block-8b0000.svg) | `#8b0000` | the family | Active red: a toggle button while its state is on, in BC-250 GPU Manager and BC-250 ACE Queues. It is not an error. |
| ![#a00000](design/colors/block-a00000.svg) | `#a00000` | the family | Active red under the pointer. |
| ![#e57373](design/colors/block-e57373.svg) | `#e57373` | text tint | Red text on a dark surface. The check app uses it for findings, the log, in-game checks, history and scores. ACPI, CU Unlock and Core Unlock use it for error labels. SFTP Tools uses it for password advice not followed. |
| ![#e8505b](design/colors/block-e8505b.svg) | `#e8505b` | brand or icon | PlayStation's circle, for BC-250 Controller's circle button and DatStation's circle symbol. |
| ![#ff2020](design/colors/block-ff2020.svg) | `#ff2020` | hardware | The light bar's red. The color wheel's red is `#ff0000`. |

### Orange and yellow

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#ef6c00](design/colors/block-ef6c00.svg) | `#ef6c00` | the family | Warn. |
| ![#fdd835](design/colors/block-fdd835.svg) | `#fdd835` | the family | Running. |
| ![#ffb74d](design/colors/block-ffb74d.svg) | `#ffb74d` | text tint | Orange text on a dark surface. The check app uses it for warnings, the log, in-game checks and middle scores. SFTP Tools uses it for its password warning. |
| ![#ffd166](design/colors/block-ffd166.svg) | `#ffd166` | brand or icon | DatStation's PS News symbol. |
| ![#ffd700](design/colors/block-ffd700.svg) | `#ffd700` | brand or icon | DatStation's gold, for trophies and stars. Its silver is `#c0c0c0` and its bronze `#cd7f32`. |
| ![#ffff00](design/colors/block-ffff00.svg) | `#ffff00` | hardware | The color wheel's yellow. |

### Green

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#2e7d32](design/colors/block-2e7d32.svg) | `#2e7d32` | the family | Ok: passed, valid, unlocked and a pressed controller button. It also marks a right answer. |
| ![#81c784](design/colors/block-81c784.svg) | `#81c784` | text tint | Green text on a dark surface. The check app uses it for log success, in-game ok, a better result in its history and full scores. SFTP Tools uses it for password advice followed. |
| ![#3dbf9c](design/colors/block-3dbf9c.svg) | `#3dbf9c` | brand or icon | PlayStation's triangle, for BC-250 Controller's triangle button and DatStation's triangle symbol. |
| ![#10d040](design/colors/block-10d040.svg) | `#10d040` | hardware | The light bar's green. The color wheel's green is `#00ff00`. |

### Blue

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#1565c0](design/colors/block-1565c0.svg) | `#1565c0` | the family | Info. It also colors the check app's GPU score box and HDMI CEC's adapter and display boxes. |
| ![#64b5f6](design/colors/block-64b5f6.svg) | `#64b5f6` | text tint | Blue text on a dark surface, for the check app's info and hint findings. |
| ![#0a55b0](design/colors/block-0a55b0.svg) | `#0a55b0` | brand or icon | Gaming blue, the gaming apps' color. It is the emulator managers' primary button. The button is `#2a6cc4` under the pointer and `#08448d` pressed. Their links are `#5b93da`. |
| ![#003791](design/colors/block-003791.svg) | `#003791` | brand or icon | PlayStation blue, in DatStation. Its light blue is `#0072ce`. It is `#1a85e0` under the pointer and `#00589f` pressed. Its links are `#4da3ef`. |
| ![#6f9fe8](design/colors/block-6f9fe8.svg) | `#6f9fe8` | brand or icon | PlayStation's cross, for BC-250 Controller's cross button and DatStation's cross symbol. The square is `#e48fc0` in both. |
| ![#1f3e9c](design/colors/block-1f3e9c.svg) | `#1f3e9c` | brand or icon | BIOS Reader's bar and selection, with `#0b2a8a` and `#10205a`. Together they look like a classic BIOS screen. |
| ![#0050ff](design/colors/block-0050ff.svg) | `#0050ff` | hardware | The light bar's blue, the default. The color wheel's blue is `#0000ff`. |

### Purple

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#6a1b9a](design/colors/block-6a1b9a.svg) | `#6a1b9a` | the family | The logo's purple, the suite's own state color. |
| ![#5835ce](design/colors/block-5835ce.svg) | `#5835ce` | the family | The wiki's purple, with `#8a2be2`. It is the suite's identity on the web. |
| ![#ce93d8](design/colors/block-ce93d8.svg) | `#ce93d8` | text tint | Purple text on a dark surface. The check app uses it for log hints, the **Show in log** link and the in-game accent. The overlay uses it for its frame rate and border. |
| ![#8b4fd8](design/colors/block-8b4fd8.svg) | `#8b4fd8` | the family | The stage pill under the claim on the wiki's home page. |
| ![#a020f0](design/colors/block-a020f0.svg) | `#a020f0` | hardware | The light bar's purple. The color wheel's magenta is `#ff00ff`. |

### Palettes of their own

| Color | Hex | Kind | Where and why |
| --- | --- | --- | --- |
| ![#8a5a2e](design/colors/block-8a5a2e.svg) | `#8a5a2e` | brand or icon | Upscaler's copper boxes. Its teal `#0e6f75` boxes and cyan `#26a9b0` outlines go with them. These are the icon's colors. |
| ![#ad1457](design/colors/block-ad1457.svg) | `#ad1457` | brand or icon | The check app's System overview, a chart with a color for each series. Cores use this color. Threads use `#00796b`, upload `#3949ab` and NVMe `#6d4c41`. Packages use `#5e35b1`, BIOS `#00838f` and a seventh series `#5d4037`. Each series stands apart from the others. |

## The apps

The theme, the state colors and the style sheets are in `core/bc250_core/theme.py`. Core is bundled per app. The
apps that are not on core yet carry a copy. The user picks one theme, and it holds for every app. The themes are
Gunmetal, Silver and Warm.

### Gunmetal (dark, the default)

Text colors:

- `#d9dde2` Text on every surface.

  ![Sample text in #d9dde2](design/colors/text-d9dde2.svg)

- `#82868b` Muted text: versions, hints, placeholders and disabled buttons. It mixes the text and window colors.

  ![Sample text in #82868b](design/colors/text-82868b.svg)

- `#ffffff` Text on the accent (selected rows and items).

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

- `#7e97ad` Links.

  ![Sample text in #7e97ad](design/colors/text-7e97ad.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#2b2f34](design/colors/block-2b2f34.svg) | `#2b2f34` | Window and dialog background, and the selected tab. |
| ![#22262a](design/colors/block-22262a.svg) | `#22262a` | Text fields, lists, tables, tooltips, progress bars and scroll bars. |
| ![#292d32](design/colors/block-292d32.svg) | `#292d32` | Every other row of a list or table. |
| ![#4a5058](design/colors/block-4a5058.svg) | `#4a5058` | Button face, top of its sheen. Scroll bar handles use it too. |
| ![#3b4048](design/colors/block-3b4048.svg) | `#3b4048` | Button face, bottom of its sheen. |
| ![#606872](design/colors/block-606872.svg) | `#606872` | Palette light, the button face 30 % lighter. |
| ![#14171a](design/colors/block-14171a.svg) | `#14171a` | Borders and shadows. |
| ![#7e97ad](design/colors/block-7e97ad.svg) | `#7e97ad` | Accent: selection, progress. |
| ![#c0c4c9](design/colors/block-c0c4c9.svg) | `#c0c4c9` | Silver outline: the border under the mouse, with the focus and of the chosen tab or item (owner, 05-11-2026). |

### Silver (light)

Text colors:

- `#1e2226` Text on every surface.

  ![Sample text in #1e2226](design/colors/text-1e2226.svg)

- `#7a7d81` Muted text: versions, hints, placeholders and disabled buttons.

  ![Sample text in #7a7d81](design/colors/text-7a7d81.svg)

- `#ffffff` Text on the accent.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

- `#5f7f9c` Links.

  ![Sample text in #5f7f9c](design/colors/text-5f7f9c.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#d5d8dc](design/colors/block-d5d8dc.svg) | `#d5d8dc` | Window and dialog background, and the selected tab. |
| ![#eceef0](design/colors/block-eceef0.svg) | `#eceef0` | Text fields, lists, tables, tooltips, progress bars and scroll bars. |
| ![#e2e5e8](design/colors/block-e2e5e8.svg) | `#e2e5e8` | Every other row of a list or table. |
| ![#eef0f2](design/colors/block-eef0f2.svg) | `#eef0f2` | Button face, top of its sheen. Scroll bar handles use it too. |
| ![#c4c8cd](design/colors/block-c4c8cd.svg) | `#c4c8cd` | Button face, bottom of its sheen. |
| ![#ffffff](design/colors/block-ffffff.svg) | `#ffffff` | Palette light, the button face 30 % lighter. |
| ![#8d9298](design/colors/block-8d9298.svg) | `#8d9298` | Borders and shadows. |
| ![#5f7f9c](design/colors/block-5f7f9c.svg) | `#5f7f9c` | Accent: selection, progress. |
| ![#7d8389](design/colors/block-7d8389.svg) | `#7d8389` | Silver outline, darker on the light theme. It colors the border under the mouse, the border with the focus and the border of the chosen tab or item. |

### Warm (dark)

Text colors:

- `#e3dfd8` Text on every surface.

  ![Sample text in #e3dfd8](design/colors/text-e3dfd8.svg)

- `#8c8984` Muted text: versions, hints, placeholders and disabled buttons.

  ![Sample text in #8c8984](design/colors/text-8c8984.svg)

- `#1b1a18` Text on the accent.

  ![Sample text in #1b1a18](design/colors/text-1b1a18.svg)

- `#b59a6e` Links.

  ![Sample text in #b59a6e](design/colors/text-b59a6e.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#35332f](design/colors/block-35332f.svg) | `#35332f` | Window and dialog background, and the selected tab. |
| ![#292826](design/colors/block-292826.svg) | `#292826` | Text fields, lists, tables, tooltips, progress bars and scroll bars. |
| ![#302e2b](design/colors/block-302e2b.svg) | `#302e2b` | Every other row of a list or table. |
| ![#57534d](design/colors/block-57534d.svg) | `#57534d` | Button face, top of its sheen. Scroll bar handles use it too. |
| ![#45423d](design/colors/block-45423d.svg) | `#45423d` | Button face, bottom of its sheen. |
| ![#716c64](design/colors/block-716c64.svg) | `#716c64` | Palette light, the button face 30 % lighter. |
| ![#181716](design/colors/block-181716.svg) | `#181716` | Borders and shadows. |
| ![#b59a6e](design/colors/block-b59a6e.svg) | `#b59a6e` | Accent: selection, progress. |
| ![#c0c4c9](design/colors/block-c0c4c9.svg) | `#c0c4c9` | Silver outline: the border under the mouse, with the focus and of the chosen tab or item (owner, 05-11-2026). |

### State colors

A state shows as a colored edge or dot on the theme's surfaces. It looks the same in every theme.

Text colors:

- `#2e7d32` Green: Passed, a valid entry.

  ![Sample text in #2e7d32](design/colors/text-2e7d32.svg)

- `#c62828` Red: Failed, errors and problems in every app. Examples are the emulator managers' status lines, the Nexus Release Tool's bad tags, the upscaler's problems and a folder that is missing.

  ![Sample text in #c62828](design/colors/text-c62828.svg)

- `#ffffff` Bright text, the palette's BrightText. It is the text on the state colors.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#2e7d32](design/colors/block-2e7d32.svg) | `#2e7d32` | Green, ok. It colors a state's edge or dot, an unlocked CU and a pressed controller button. |
| ![#ef6c00](design/colors/block-ef6c00.svg) | `#ef6c00` | Orange, warn. |
| ![#c62828](design/colors/block-c62828.svg) | `#c62828` | Red, bad. It also colors the red buttons of the bisect apps and **Clean up logs**. |
| ![#b71c1c](design/colors/block-b71c1c.svg) | `#b71c1c` | The red buttons under the pointer or pressed, in the bisect apps and **Clean up logs**. |
| ![#1565c0](design/colors/block-1565c0.svg) | `#1565c0` | Blue, info. |
| ![#3a3f4b](design/colors/block-3a3f4b.svg) | `#3a3f4b` | Gray, neutral. |
| ![#6a1b9a](design/colors/block-6a1b9a.svg) | `#6a1b9a` | Purple, the logo's purple. |
| ![#fdd835](design/colors/block-fdd835.svg) | `#fdd835` | Yellow, running: never confused with a failed (red) state. |
| ![#8b0000](design/colors/block-8b0000.svg) | `#8b0000` | Active red: a toggle button while its state is on, in BC-250 GPU Manager and BC-250 ACE Queues. |
| ![#a00000](design/colors/block-a00000.svg) | `#a00000` | Active red on hover. |
| ![#424242](design/colors/block-424242.svg) | `#424242` | Off: a locked CU, a core without a state. |
| ![#1d4f91](design/colors/block-1d4f91.svg) | `#1d4f91` | Steam artwork: the accent when an icon gives no bright color. |

## The wiki

`docs/stylesheets/suite.css`, Material's slate scheme with the suite's purple.

### Wiki

Text colors:

- `#ffffff` Text in the header, hero, cards and footer. It also colors table headings, the stage pill and the buttons on the dark and accent sections.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

- `#ffffffb3` Dimmed text on the main and the hover color, for the search field's hint.

  ![Sample text in #ffffffb3](design/colors/text-ffffffb3.svg)

- `#a98bff` Suite soft: links in the dark scheme, hover on the dark section and footer column headings.

  ![Sample text in #a98bff](design/colors/text-a98bff.svg)

- `#c9bfee` Suite mist: card text and footer links.

  ![Sample text in #c9bfee](design/colors/text-c9bfee.svg)

- `#1e1340` Suite deep: a button's text on hover in the dark and accent sections.

  ![Sample text in #1e1340](design/colors/text-1e1340.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#5835ce](design/colors/block-5835ce.svg) | `#5835ce` | Suite primary: Material's primary color, table headings, page icons, the hero and Get started gradients. |
| ![#7a5ce0](design/colors/block-7a5ce0.svg) | `#7a5ce0` | Primary, light. |
| ![#4426a8](design/colors/block-4426a8.svg) | `#4426a8` | Primary, dark. |
| ![#8a2be2](design/colors/block-8a2be2.svg) | `#8a2be2` | Suite secondary: the accent and the end of the gradients. The accent shows as hover rings on linked images. |
| ![#8a2be21a](design/colors/block-8a2be21a.svg) | `#8a2be21a` | The accent at 10 %. |
| ![#1e1340](design/colors/block-1e1340.svg) | `#1e1340` | Suite deep: header and tabs, the hero's top, the Download button. |
| ![#120c22](design/colors/block-120c22.svg) | `#120c22` | Suite ink: the dark section and the home page's footer. |
| ![#120c2273](design/colors/block-120c2273.svg) | `#120c2273` | The shadow under the board and the controller at the top of the home page (45 %). |
| ![#17141f](design/colors/block-17141f.svg) | `#17141f` | Page background (the dark scheme). |
| ![#8b4fd8](design/colors/block-8b4fd8.svg) | `#8b4fd8` | The stage pill under the claim. |
| ![#ffffff](design/colors/block-ffffff.svg) | `#ffffff` | Button background on hover in the dark and accent sections. |
| ![#ffffff1f](design/colors/block-ffffff1f.svg) | `#ffffff1f` | Behind a link in the header under the pointer (12 %). |
| ![#00000040](design/colors/block-00000040.svg) | `#00000040` | The shadow under a button under the pointer (25 %). |
| ![#00000059](design/colors/block-00000059.svg) | `#00000059` | The strip with the notice at the bottom of the home page's footer (35 %). |

## The development apps

Nexus's design, in the windows of the apps in `dev/`.

### Nexus Release Tool

The release tool's window takes Nexus's colors as a theme for core's widgets. It sets them with `create_app(theme=NEXUS)`. Its style is in `dev/nrt/nexus_release_tool/style.py`. Its states are the apps' state family.

Text colors:

- `#c0c0c0` Silver: the text, the title, the boxes' values and captions, the buttons, the tabs and the fields.

  ![Sample text in #c0c0c0](design/colors/text-c0c0c0.svg)

- `#010101` Ink: text on the teal accent (a selected row).

  ![Sample text in #010101](design/colors/text-010101.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#010101](design/colors/block-010101.svg) | `#010101` | Ink: the window, the header, the dialogs and every other row of a table. It is also the bottom of a button's or a box's sheen. |
| ![#0f0f0f](design/colors/block-0f0f0f.svg) | `#0f0f0f` | Main color: the fields, lists and tables. It is also the top of a button's or a box's sheen. |
| ![#17b6a7](design/colors/block-17b6a7.svg) | `#17b6a7` | Teal, the accent. It colors the selection and the outline of a selected cell or a focused field. A button or pill under the pointer takes it too. So do the main actions, such as **Commit**, **Start new release** and **Retract**, and the progress bar. |
| ![#80808066](design/colors/block-80808066.svg) | `#80808066` | Dimmed silver at 40 %. It colors the borders of the fields, boxes, tabs and buttons, and a box's neutral edge. |

## The apps' own colors

These colors come on top of the theme. They are in each app's `style.py` or in the code that uses them.

### Gaming apps

PS Remote Play, XB Remote Play, BC-250 Controller, PCSX2, PPSSPP, RPCS3, shadPS4, Vita3K and Xenia.

Text colors:

- `#5b93da` Links on a dark window in PS Remote Play, XB Remote Play, PCSX2, PPSSPP, RPCS3, shadPS4, Vita3K and Xenia. BC-250 Controller uses it for its lit parts.

  ![Sample text in #5b93da](design/colors/text-5b93da.svg)

- `#ffffff` Text on the blue primary button and on the shortcut artwork.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#0a55b0](design/colors/block-0a55b0.svg) | `#0a55b0` | Gaming blue: the primary button and hover borders. It is the gaming apps' color. Their icon has been a silver controller since 13-11-2026. |
| ![#2a6cc4](design/colors/block-2a6cc4.svg) | `#2a6cc4` | Gaming blue on hover. |
| ![#08448d](design/colors/block-08448d.svg) | `#08448d` | Gaming blue while pressed. |
| ![#0a55b01a](design/colors/block-0a55b01a.svg) | `#0a55b01a` | Blue tint at 10 %. It colors hover and every other table row. |
| ![#0a55b059](design/colors/block-0a55b059.svg) | `#0a55b059` | Blue line at 35 %. It colors outlines and a pressed button. |
| ![#80808080](design/colors/block-80808080.svg) | `#80808080` | Disabled (50 % gray). |
| ![#5b93da](design/colors/block-5b93da.svg) | `#5b93da` | BC-250 Controller: lit parts of the controller, the chosen card. |
| ![#0b1d3a](design/colors/block-0b1d3a.svg) | `#0b1d3a` | shadPS4 shortcut artwork, top of the gradient. |
| ![#030810](design/colors/block-030810.svg) | `#030810` | shadPS4 shortcut artwork, bottom. |
| ![#16123a](design/colors/block-16123a.svg) | `#16123a` | RPCS3 shortcut artwork, top. |
| ![#05040f](design/colors/block-05040f.svg) | `#05040f` | RPCS3 shortcut artwork, bottom. |
| ![#0d2a4a](design/colors/block-0d2a4a.svg) | `#0d2a4a` | PPSSPP shortcut artwork, top. |
| ![#04080f](design/colors/block-04080f.svg) | `#04080f` | PPSSPP shortcut artwork, bottom. |
| ![#3a2c0d](design/colors/block-3a2c0d.svg) | `#3a2c0d` | Vita3K shortcut artwork, top. |
| ![#0f0b03](design/colors/block-0f0b03.svg) | `#0f0b03` | Vita3K shortcut artwork, bottom. |
| ![#000000](design/colors/block-000000.svg) | `#000000` | PS Remote Play's stream view. |

### DatStation

Text colors:

- `#4da3ef` Links on a dark window.

  ![Sample text in #4da3ef](design/colors/text-4da3ef.svg)

- `#0072ce` Links on a light window.

  ![Sample text in #0072ce](design/colors/text-0072ce.svg)

- `#3dbf9c` Triangle: the Quiz symbol. The symbols take the face-button colors, as BC-250 Controller draws them.

  ![Sample text in #3dbf9c](design/colors/text-3dbf9c.svg)

- `#e8505b` Circle: the History symbol.

  ![Sample text in #e8505b](design/colors/text-e8505b.svg)

- `#6f9fe8` Cross: the System Version History symbol.

  ![Sample text in #6f9fe8](design/colors/text-6f9fe8.svg)

- `#e48fc0` Square: the Region Codes symbol.

  ![Sample text in #e48fc0](design/colors/text-e48fc0.svg)

- `#ffd166` The PS News symbol.

  ![Sample text in #ffd166](design/colors/text-ffd166.svg)

- `#ffd700` Gold: the Scores & Trophies symbol, a perfect quiz, gold stars.

  ![Sample text in #ffd700](design/colors/text-ffd700.svg)

- `#c0c0c0` Silver stars.

  ![Sample text in #c0c0c0](design/colors/text-c0c0c0.svg)

- `#cd7f32` Bronze stars.

  ![Sample text in #cd7f32](design/colors/text-cd7f32.svg)

- `#2e7d32` Right answers: the count and the feedback.

  ![Sample text in #2e7d32](design/colors/text-2e7d32.svg)

- `#c62828` Wrong answers: the count. It also shows that little time is left.

  ![Sample text in #c62828](design/colors/text-c62828.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#003791](design/colors/block-003791.svg) | `#003791` | PlayStation blue. |
| ![#0072ce](design/colors/block-0072ce.svg) | `#0072ce` | PlayStation light blue: hover borders. |
| ![#1a85e0](design/colors/block-1a85e0.svg) | `#1a85e0` | Blue on hover. |
| ![#00589f](design/colors/block-00589f.svg) | `#00589f` | Blue while pressed. |
| ![#2e7d32](design/colors/block-2e7d32.svg) | `#2e7d32` | A right answer's button. |
| ![#c62828](design/colors/block-c62828.svg) | `#c62828` | A wrong answer's button. |

### Upscaler

Text colors:

- `#3fc8cf` Links on a dark window.

  ![Sample text in #3fc8cf](design/colors/text-3fc8cf.svg)

- `#0e6f75` Links on a light window.

  ![Sample text in #0e6f75](design/colors/text-0e6f75.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#8a5a2e](design/colors/block-8a5a2e.svg) | `#8a5a2e` | Copper: boxes, white text on them. |
| ![#0e6f75](design/colors/block-0e6f75.svg) | `#0e6f75` | Teal: boxes, white text on them. |
| ![#26a9b0](design/colors/block-26a9b0.svg) | `#26a9b0` | Cyan, the icon's: button outlines. |

### BC-250 Board Test (check)

Text colors:

- `#9aa0a6` Muted: versions, hints, notes, baselines, the in-game and overlay labels.

  ![Sample text in #9aa0a6](design/colors/text-9aa0a6.svg)

- `#e6e6e6` Text in the results and history views, on idle buttons, the overlay's values.

  ![Sample text in #e6e6e6](design/colors/text-e6e6e6.svg)

- `#e8e8e8` Code blocks in the README view.

  ![Sample text in #e8e8e8](design/colors/text-e8e8e8.svg)

- `#d0d0d0` The log, and a disabled **Clean up logs** button.

  ![Sample text in #d0d0d0](design/colors/text-d0d0d0.svg)

- `#1a1a1a` Text on the yellow running button.

  ![Sample text in #1a1a1a](design/colors/text-1a1a1a.svg)

- `#222222` Text on the system score boxes.

  ![Sample text in #222222](design/colors/text-222222.svg)

- `#333333` Labels on the graph's bars.

  ![Sample text in #333333](design/colors/text-333333.svg)

- `#e57373` Error findings, a worse result in the history, a low score and the log's errors. It also colors error labels and the in-game error. ACPI, CU Unlock and Core Unlock use it for error labels too.

  ![Sample text in #e57373](design/colors/text-e57373.svg)

- `#ffb74d` Warning findings, a middle score, the log's warnings and the in-game warning.

  ![Sample text in #ffb74d](design/colors/text-ffb74d.svg)

- `#64b5f6` Info and hint findings.

  ![Sample text in #64b5f6](design/colors/text-64b5f6.svg)

- `#81c784` A better result in the history, the log's success, a full score and the in-game ok.

  ![Sample text in #81c784](design/colors/text-81c784.svg)

- `#fdd835` A score's warning, in the running yellow.

  ![Sample text in #fdd835](design/colors/text-fdd835.svg)

- `#ce93d8` The log's hints, the **Show in log** link and the in-game accent. The overlay uses it for its frame rate and thin border.

  ![Sample text in #ce93d8](design/colors/text-ce93d8.svg)

- `#90a4ae` Log: note.

  ![Sample text in #90a4ae](design/colors/text-90a4ae.svg)

- `#ffffff` README table headings.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#111418](design/colors/block-111418.svg) | `#111418` | The log and the overlay's background at 82 %. |
| ![#1e1f24](design/colors/block-1e1f24.svg) | `#1e1f24` | The results and history views, and code blocks in the README view. |
| ![#14161c](design/colors/block-14161c.svg) | `#14161c` | The results card and the score dialog. |
| ![#2a2d36](design/colors/block-2a2d36.svg) | `#2a2d36` | The empty part of a score ring. |
| ![#2a2f37](design/colors/block-2a2f37.svg) | `#2a2f37` | The log's border. |
| ![#3a3f4a](design/colors/block-3a3f4a.svg) | `#3a3f4a` | The borders of the preview, setup, checks and stat cards. |
| ![#555555](design/colors/block-555555.svg) | `#555555` | The screenshot's border. |
| ![#888888](design/colors/block-888888.svg) | `#888888` | README table borders. |
| ![#3a3f4b](design/colors/block-3a3f4b.svg) | `#3a3f4b` | Idle buttons, README table headings and a disabled **Clean up logs** button. |
| ![#b71c1c](design/colors/block-b71c1c.svg) | `#b71c1c` | Clean up logs under the pointer and pressed. |
| ![#f8fafc](design/colors/block-f8fafc.svg) | `#f8fafc` | The system score boxes. |
| ![#1565c0](design/colors/block-1565c0.svg) | `#1565c0` | The GPU score box, in the info blue. |
| ![#ad1457](design/colors/block-ad1457.svg) | `#ad1457` | System overview: cores. |
| ![#00796b](design/colors/block-00796b.svg) | `#00796b` | System overview: threads. |
| ![#3949ab](design/colors/block-3949ab.svg) | `#3949ab` | System overview: upload speed. |
| ![#6d4c41](design/colors/block-6d4c41.svg) | `#6d4c41` | System overview: NVMe. |
| ![#5e35b1](design/colors/block-5e35b1.svg) | `#5e35b1` | System overview: packages. |
| ![#00838f](design/colors/block-00838f.svg) | `#00838f` | System overview: BIOS. It is also the graph's sixth series. |
| ![#5d4037](design/colors/block-5d4037.svg) | `#5d4037` | The graph's seventh series. |

### Other apps

Text colors:

- `#888888` Busy and hint labels in italics (ACPI).

  ![Sample text in #888888](design/colors/text-888888.svg)

- `#ef6c00` An incomplete ACPI override, and a CU mask that needs checking.

  ![Sample text in #ef6c00](design/colors/text-ef6c00.svg)

- `#b8b8c8` System Overlay: the names of the values.

  ![Sample text in #b8b8c8](design/colors/text-b8b8c8.svg)

- `#dddddd` PS Remote Play's stream view.

  ![Sample text in #dddddd](design/colors/text-dddddd.svg)

- `#ffb74d` SFTP: the password warning.

  ![Sample text in #ffb74d](design/colors/text-ffb74d.svg)

- `#e57373` SFTP: password advice not followed.

  ![Sample text in #e57373](design/colors/text-e57373.svg)

- `#81c784` SFTP: password advice followed.

  ![Sample text in #81c784](design/colors/text-81c784.svg)

- `#ffffff` BIOS Reader: tabs, crumbs, the legend and the selection.

  ![Sample text in #ffffff](design/colors/text-ffffff.svg)

- `#0b2a8a` BIOS Reader: the screen's text.

  ![Sample text in #0b2a8a](design/colors/text-0b2a8a.svg)

- `#10205a` BIOS Reader: subtitles.

  ![Sample text in #10205a](design/colors/text-10205a.svg)

- `#6e6e6e` BIOS Reader: hidden items.

  ![Sample text in #6e6e6e](design/colors/text-6e6e6e.svg)

- `#7d7d8c` BIOS Reader: locked items.

  ![Sample text in #7d7d8c](design/colors/text-7d7d8c.svg)

- `#2e7d32` Installer Tests: passed.

  ![Sample text in #2e7d32](design/colors/text-2e7d32.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#1f3e9c](design/colors/block-1f3e9c.svg) | `#1f3e9c` | BIOS Reader: the bar and the selection. |
| ![#c6c6c6](design/colors/block-c6c6c6.svg) | `#c6c6c6` | BIOS Reader: the screen. |
| ![#1565c0](design/colors/block-1565c0.svg) | `#1565c0` | HDMI-CEC: the adapter and display boxes. |
| ![#000000](design/colors/block-000000.svg) | `#000000` | BC-250 Controller: the light bar off. |
| ![#c62828](design/colors/block-c62828.svg) | `#c62828` | SFTP: the errors button. |
| ![#5f6368](design/colors/block-5f6368.svg) | `#5f6368` | VRAM: firmware in the memory map. |
| ![#00838f](design/colors/block-00838f.svg) | `#00838f` | VRAM: zswap in the memory map. |
| ![#3dbf9c](design/colors/block-3dbf9c.svg) | `#3dbf9c` | BC-250 Controller: the triangle button. |
| ![#e8505b](design/colors/block-e8505b.svg) | `#e8505b` | BC-250 Controller: the circle button. |
| ![#6f9fe8](design/colors/block-6f9fe8.svg) | `#6f9fe8` | BC-250 Controller: the cross button. |
| ![#e48fc0](design/colors/block-e48fc0.svg) | `#e48fc0` | BC-250 Controller: the square button. |
| ![#0050ff](design/colors/block-0050ff.svg) | `#0050ff` | BC-250 Controller: the light bar's blue, the default. |
| ![#ff2020](design/colors/block-ff2020.svg) | `#ff2020` | Light bar: red. |
| ![#10d040](design/colors/block-10d040.svg) | `#10d040` | Light bar: green. |
| ![#a020f0](design/colors/block-a020f0.svg) | `#a020f0` | Light bar: purple. |
| ![#ffffff](design/colors/block-ffffff.svg) | `#ffffff` | Light bar: white. |
| ![#ff0000](design/colors/block-ff0000.svg) | `#ff0000` | The color wheel's red, for the light bar. |
| ![#ffff00](design/colors/block-ffff00.svg) | `#ffff00` | Color wheel: yellow. |
| ![#00ff00](design/colors/block-00ff00.svg) | `#00ff00` | Color wheel: green. |
| ![#00ffff](design/colors/block-00ffff.svg) | `#00ffff` | Color wheel: cyan. |
| ![#0000ff](design/colors/block-0000ff.svg) | `#0000ff` | Color wheel: blue. |
| ![#ff00ff](design/colors/block-ff00ff.svg) | `#ff00ff` | Color wheel: magenta. |
| ![#04060c](design/colors/block-04060c.svg) | `#04060c` | Portal: the intro's backdrop. |
| ![#1b1b1b](design/colors/block-1b1b1b.svg) | `#1b1b1b` | Portal: the outline of the update badge on a tile. |
| ![#808080](design/colors/block-808080.svg) | `#808080` | Portal: a category tab on hover (16 %). |

## Tools

### Portal screenshots

`tools/portal_screenshot.py` paints the portal in a fixed dark palette, so screenshots look the same on every machine. The palette is Breeze Dark, as Bazzite's desktop shows the portal.

Text colors:

- `#fcfcfc` Window, field, button and tooltip text.

  ![Sample text in #fcfcfc](design/colors/text-fcfcfc.svg)

- `#a1a9b1` Placeholders.

  ![Sample text in #a1a9b1](design/colors/text-a1a9b1.svg)

- `#1d99f3` Links.

  ![Sample text in #1d99f3](design/colors/text-1d99f3.svg)

Background colors:

| Color | Hex | Used for |
| --- | --- | --- |
| ![#202326](design/colors/block-202326.svg) | `#202326` | Window. |
| ![#141618](design/colors/block-141618.svg) | `#141618` | Fields and lists. |
| ![#1d1f22](design/colors/block-1d1f22.svg) | `#1d1f22` | Every other row. |
| ![#292c30](design/colors/block-292c30.svg) | `#292c30` | Buttons and tooltips. |
| ![#3daee9](design/colors/block-3daee9.svg) | `#3daee9` | Selection. |
| ![#43474d](design/colors/block-43474d.svg) | `#43474d` | Mid. |
| ![#33373b](design/colors/block-33373b.svg) | `#33373b` | Midlight. |
| ![#101113](design/colors/block-101113.svg) | `#101113` | Dark. |
| ![#3d4146](design/colors/block-3d4146.svg) | `#3d4146` | Light. |

## Icons

Every icon of the suite and where it is used. `tools/design_icons.py` reads most of this from the repository, so it stays current.

### The suite's icon

| Icon | File | Used for |
| --- | --- | --- |
| <img src="portal/images/bc250-bazzite-suite.webp" width="48" alt=""> | `portal/images/bc250-bazzite-suite.webp` | The portal's header (a click opens the wiki), its window icon and its tray icon. |
| <img src="portal/images/bc250-bazzite-suite-1024.webp" width="48" alt=""> | `portal/images/bc250-bazzite-suite-1024.webp` | The portal's intro. |
| <img src="portal/images/bc250-bazzite-suite-128.png" width="48" alt=""> | `portal/images/bc250-bazzite-suite-128.png` | The portal's menu entry and Desktop icon. |
| <img src="portal/images/apps/portal.webp" width="48" alt=""> | `portal/images/apps/portal.webp` | The portal's own tile. |
| <img src="docs/images/wiki-icon.webp" width="48" alt=""> | `docs/images/wiki-icon.webp` | The wiki's header logo, its home page's footer and its favicon (with the .png). |
| <img src="dev/nrt/images/nexus-release-tool.webp" width="48" alt=""> | `dev/nrt/images/nexus-release-tool.webp` | Every development app's icon in dev/<name>/images/: the Nexus drawing, as Nexus's apps have it. |

### The category icons

Every app has the icon of its category. `icons/categories.toml` assigns them, and `tools/sync_icons.py` copies each category's icon from `icons/<category>/` to the app's `images/`, the portal's `images/apps/` and `images/categories/`, and the wiki. The wiki's App categories page shows each app with its icon.

| Icon | Category | Apps |
| --- | --- | --- |
| <img src="icons/gaming/gaming-128.png" width="64" alt=""> | Gaming | BC-250 PS Remote Play (`consoles`)<br>BC-250 XB Remote Play (`clb`)<br>Bazzite DatStation (`datstation`)<br>PCSX2 Manager (`pcsx2`)<br>PPSSPP Manager (`ppsspp`)<br>RPCS3 Manager (`rpcs3`)<br>Vita3K Manager (`vita3k`)<br>Xenia Manager (`xenia`)<br>shadPS4 Manager (`shadps4`) |
| <img src="icons/graphics/graphics-128.png" width="64" alt=""> | Graphics | BC-250 ACE Queues (`ace`)<br>BC-250 Mesh Shaders (`mesh`)<br>BC-250 Upscaler Manager (`upscaler`) |
| <img src="icons/sustainable/sustainable-128.png" width="64" alt=""> | Sustainable | BC-250 Board Test (`check`)<br>BC-250 CU Unlock (`compute`)<br>BC-250 Core Unlock (`cores`)<br>BC-250 Fan Control (`fan`)<br>BC-250 GPU Manager (`gpu`)<br>BC-250 Memory Manager (`vram`)<br>BC-250 Persistent ACPI (`acpi`) |
| <img src="icons/utilities/utilities-128.png" width="64" alt=""> | Utilities | BC-250 BIOS Reader (`bios`)<br>BC-250 Bluetooth Pairing (`btpair`)<br>BC-250 CEC Manager (`cec`)<br>BC-250 Controller (`controller`)<br>BC-250 Password Generator (`password`)<br>BC-250 Quickfix (`quickfix`)<br>BC-250 SFTP Tools (`sftp`)<br>BC-250 SSD Check (`ssd`)<br>BC-250 System Overlay (`overlay`)<br>BC-250 Turing Screen (`turing`)<br>BC-250 Webcam (`webcam`) |

### The portal's symbols

Drawn with QPainter in the portal's `glyphs.py`, in the theme's text color. Each function draws one.

| Name | What it shows |
| --- | --- |
| `install` | An arrow down into a tray. |
| `reinstall` | A circular arrow. |
| `uninstall` | A waste bin. |
| `refresh` | Two arrows that chase each other around a circle. |
| `chip` | A processor: a square with pins on every side. |
| `install_apps` | Three apps of a grid of four, an arrow down in the place of the fourth. |
| `install_updates` | A circular arrow around an arrow down. |
| `menu` | ☰: three bars. |
| `close` | A cross: the portal's exit. |
| `steam` | Steam: a disc with a piston's rod cut out of it, a large ring at its head and a small one at its foot. |
| `folder` | A folder: the file manager. |
| `youtube` | A screen with a play triangle. |
| `github` | GitHub: a disc with a cat cut out of it, its head with two ears, its body and its tail. |
| `bluetooth` | The Bluetooth rune. |
| `network` | Three arcs over a dot: the network. |
| `volume` | A loudspeaker with two waves of sound: the volume. |
| `screen` | A screen on its foot: the display. |

### The desktop style's icons

Icons the apps take from the desktop's style or icon theme, so they look different on every desktop. The name is Qt's standard pixmap or the icon theme's name.

| Name | Used by |
| --- | --- |
| `SP_BrowserReload` | Nexus Deps |
| `SP_MessageBoxInformation` | BC-250 Board Test, Nexus Deps |
| `SP_MessageBoxWarning` | BC-250 Board Test |
| `view-refresh` | Nexus Deps |

### Material Design icons in the wiki

Drawn by MkDocs Material in the wiki's colors.

| Icon | Name | Pages |
| --- | --- | --- |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/chip.svg" width="24" alt=""> | `material-chip` | What is the BC-250? |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/clipboard-check-outline.svg" width="24" alt=""> | `material-clipboard-check-outline` | Board Test: the script |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/clipboard-list-outline.svg" width="24" alt=""> | `material-clipboard-list-outline` | Basic tests and additional requirements to streamline the Qt GUI version |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/code-braces.svg" width="24" alt=""> | `material-code-braces` | Development |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/cog-outline.svg" width="24" alt=""> | `material-cog-outline` | BC-250 Board Test - development |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/download.svg" width="24" alt=""> | `material-download` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/expansion-card.svg" width="24" alt=""> | `material-expansion-card` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/eye-off-outline.svg" width="24" alt=""> | `material-eye-off-outline` | Privacy |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/gamepad-variant.svg" width="24" alt=""> | `material-gamepad-variant` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/github.svg" width="24" alt=""> | `material-github` | GitHub settings |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/image-multiple-outline.svg" width="24" alt=""> | `material-image-multiple-outline` | Covers from SteamGridDB |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/linux.svg" width="24" alt=""> | `material-linux` | What is Bazzite? |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/lock-open-variant.svg" width="24" alt=""> | `material-lock-open-variant` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/memory.svg" width="24" alt=""> | `material-memory` | Memory Manager internals |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/play-circle-outline.svg" width="24" alt=""> | `material-play-circle-outline` | Portal Tour |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/shape-outline.svg" width="24" alt=""> | `material-shape-outline` | App categories |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/shield-lock-outline.svg" width="24" alt=""> | `material-shield-lock-outline` | Security |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/sitemap-outline.svg" width="24" alt=""> | `material-sitemap-outline` | Architecture and consistency |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/speedometer.svg" width="24" alt=""> | `material-speedometer` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/stethoscope.svg" width="24" alt=""> | `material-stethoscope` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/tag-outline.svg" width="24" alt=""> | `material-tag-outline` | Releases |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/television.svg" width="24" alt=""> | `material-television` | Tools for every part of the board. { .home-hero__lead } |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/tray-arrow-down.svg" width="24" alt=""> | `material-tray-arrow-down` | Install |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/video-wireless-outline.svg" width="24" alt=""> | `material-video-wireless-outline` | PS Remote Play: the stream's threads |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/view-dashboard-outline.svg" width="24" alt=""> | `material-view-dashboard-outline` | Dashboard |
| <img src="https://cdn.jsdelivr.net/npm/@mdi/svg@7.4.47/svg/view-grid-outline.svg" width="24" alt=""> | `material-view-grid-outline` | The apps |

### Characters as icons

Characters of the font that the apps use as icons in labels and buttons.

| App | Characters |
| --- | --- |
| Portal | ● ☰ |
| BC-250 BIOS Reader | ▶ ↓ ↑ ← › |
| BC-250 Board Test | ✔ ✖ ✕ ⚠ ▶ ■ ↓ ↑ › 💡 🎮 |
| BC-250 CU Unlock | ■ |
| BC-250 Controller | ✓ ✕ › △ ○ □ |
| BC-250 Core Unlock | ✔ ✖ ▶ ■ |
| BC-250 GPU Manager | ✔ ✖ ⚠ ▶ ● |
| BC-250 PS Remote Play | ✓ ✗ |
| BC-250 Persistent ACPI | ● |
| BC-250 Quickfix | ● ○ |
| BC-250 SFTP Tools | ✓ ✗ ⚠ ↓ ↑ ← |
| BC-250 System Overlay | ↓ ↑ |
| BC-250 Turing Screen | ↓ ↑ |
| BC-250 Webcam | ✓ ● |
| Bazzite DatStation | ← △ ○ □ ◇ ◆ ★ |
| Every app on core | ✓ ● ↻ |
| Nexus Deps | ✓ ✗ |
| Nexus Installer Tests | ✓ ✗ |
| Nexus Release Tool | ✓ ▶ ● ↓ ↑ |
