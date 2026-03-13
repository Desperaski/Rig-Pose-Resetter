# Rig Pose Resetter

A simple Blender addon that adds a panel with buttons in the sidebar (N key) in the **Pose Resetter** tab.

The main reason this addon was made - you can select the desired rig in a dropdown menu in advance, and then work with the buttons — no need to reselect it or switch modes every time.

![screenshot](234235235.jpg)

## Buttons:
- **Pose Position / Rest Position** — toggle pose display mode (similar to buttons in Armature Data Properties).
- **Reset Selected to Rest** — reset only **selected** bones to rest position (Alt+G / Alt+R / Alt+S).
- **Reset All to Rest** — reset all rig bones to rest position.
- **Apply Current as Rest** — makes the current pose the new rest pose. Disabled by default, can be enabled via checkbox and requires confirmation.

## Installation
1. Download the ZIP archive.
2. Blender 4.2+: `Edit` -> `Preferences` -> `Add-ons` -> `Install from Disk...` -> select the ZIP.  
   Or simply drag the archive into the Blender window.
3. Enjoy.
