"""
DeskFlip
Standalone, modern, sleek dark-themed Windows 11 Profile & App Migration Utility.

Migrates:
- Microsoft Edge (Favorites, Profiles, Passwords, History, Extensions, Local State)
- Google Chrome (Favorites, Profiles, Passwords, History, Extensions, Local State)
- Mozilla Firefox (Profiles, Places, Logins, Extensions, Prefs)
- Windows Personalization: Desktop Wallpaper, Mouse Settings, Keyboard Settings, Theme & Accent Colors
- Wi-Fi Profiles & Saved Passwords (all-user & current-user)
- File Explorer Preferences (hidden files, extensions, compact view, launch target)
- Sound & Audio Settings (per-app volume policies and sound schemes)
- Windows Credentials & Vault store
- User Custom Fonts
- Microsoft Outlook: Profiles, Accounts, Signatures, RoamCache / Autocomplete
- Windows Quick Launch shortcuts
- Windows 11 Taskbar pinned icons (Shortcuts + Taskband layout)
- Windows Terminal profiles & PowerShell scripts
- Git & SSH configurations (.gitconfig, .ssh keys/hosts)
- Remote Desktop (RDP) connections & Default.rdp
- PuTTY, WinSCP & FileZilla site manager and sessions
- Notepad++ configuration, custom macros, and active session
"""

import os
import errno
import sys
import json
import shutil
import base64
import ctypes
import zipfile
import uuid
import threading
import subprocess
import winreg
import platform
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
try:
    import pyzipper
except ImportError:
    pyzipper = None

# Win32 Constants
SPI_SETDESKWALLPAPER = 0x0014
SPI_GETDESKWALLPAPER = 0x0073
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

APP_TITLE = "DeskFlip"
APP_VERSION = "v1.3"
EMBEDDED_ICON_GZIP_BASE64 = (
    "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"
    "YnJMMNPf1tp8o6+v3xNrOTbMf/9PHl6VP3vngfj4jdvyxvGdAvyh6SSRNyVariI6zUoYopB+FXsqlsra4rk8vzNojUQM6CtSYkKY"
    "Pu1tLGv053ftYBufODzwfklmvFI+J0HZtHyGKJubJDPGhIkZ8ZEiK3EIxi82LZos189PovUWIZakjxJZRJPZE4Yx/dNIp48K9xOk"
    "2/n5HWytttPzWXbFDx2457Uze+TJrSuJDhm0bibK4lljWZctTY+V4O1VOQlyI+lp6PLCmWNZz2Jt0XqTs0gvT6dnQkdjrU8fHS47"
    "2bfd4+vryzosLNDfaOWc5LdfOU3vqC4U+9fOFbtIr1YvnSrWzJ0gltNzyAYQkEmlmePF+rxJYm3ORFFGa7to9jj8XyxJi5ULpowU"
    "M+OHCKzfzvbW9X5+fk06spOdVeeG9cv/ePPoduXM9nIBe6y+PEuQ/SYgIwtmjhWZRA+SC7Rupwqyy8TGhZNl5bxJoix7vMCY8J45"
    "E4Yyfbp1tGt0dHR8QgdPTxxx/NHNk/JaYzXZZmslyQnwjcwlmwHyd9qYwXLHijRq6XLHynS+Qw5VkV0CO2RVdiLTC+vLoUu7I/RI"
    "0+bPr1iW9fpPXr0hX7tyTGAtXyTePFK1SCwim5LGL6YRXXeR3KsvmSEbSmdx21c6U7NTpsva/DS5NG2UnEpz3aOzfSM98on+79tS"
    "9uvPPnpL3jy6Q5wk+fDw/D557eAWpZTso2U0z0MDPH4x0KPnwhGhXvOig72zR1KLCvTMHB7kOXt4gMesmEHeMxOGDZw8Jtx3QsKo"
    "4T7Nn+3StZ3JvXMH/naX5hhydM/axX/xdOm6et+G5X+qK51LuiBOxoX5fmZuZmJr+DsuL9du9jtKcuQlstOK56b8gv7kjb93sLFs"
    "N2Rgn+NJ0YG/iQv3+Tn96Skf42Wu2JFRRlYWJj2sLcxc6ddWfZm/55JkaElpZ/i60NzwuYOd4TPy024bHrdirT3+m8HwmeFJO0z/"
    "m9roM+bScIfaPXo27DAXapGGx3ZYsf0P1fv//tfgweGQYXZOTo7WFWvXPNe2+qEvV1c3Y3rhSJIVu+jXbGrBhr+P/6ypOWmtvV1b"
    "C9MXfB6XmaW5aXri8ICvsicMg38q+rp0gw3n88JvapeRkZGxXVvLyWF+7m+PHzbwr7Fhvn/s69zttpmp6Ur6dyi1Tu1t27Zm31p1"
    "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"
    "cJbL3kFX4Xejo8pUqpB9uHwwHwe+9qhcofz8rm2bfI9+YfoQl0wZpfWq9I9MGNqD2Z+x66Fz84zgBfRHF0H/vl1avyfvMyX1T5R/"
    "v5dNjzZt1bju+T3aNX+9f9c2fxw/tHvMjPc5E4cyX1Drl+nXo2+aPr3zxg/OpXd2wlCdNf91hxYNf9eobo0f1apW+bkqFctfWyor"
    "i3lwJ6ec3mIuk82cL7HPLfuR18M/bE6XWtWrLO/VocWnQntmrqJz6Nlx5/nTxmjNObrGZio4+p+o9Of+Jwv95e9fSeXNNa5dv9Y/"
    "nP567i6rvuiRvu1bNLxxcI924CHGs04drBjZbt7uCMUaWOh1qM7Vnhycz8uaTS/qyOPpY4+7t20at2laP2raoNavG9Su/kp2ubLr"
    "hRczUm4+cidPQ/ZacXhge5NjpJbyPkMb162xaWjv9l/S3wpd/Yx7P8t9rPZw0JPv6Z9eNrMK+WdmRZecJs/Je56RcliXtatVqfiP"
    "pj9yX6tGlYpDRa8/dMJxHf7KPMNF4i8gT9RW+z5P11euGAKul9f8Cr7j+fTOOV5E9Kgy75hZ+V1ymuYy+0Xsx2/q1qz6gvAYDI2T"
    "Us5GWJ1KgTwQvpkPxt5sUbpUqRFic+4Qn/4P6Bb0PPOMoberZRmt/SjIPPa1IPmH/uhR0ZvgrE5OOfrjx5lPXd5/Ln7I34snvHc1"
    "8YXbyj58bETfzl+By6I9nW4Ose7lZdO0tzO6UL7jBWeN0vlVC4UX9CNrn6d8x3m+t9PmrtBLcWKfjlHfzq10JvXgnu1ye3Zo/nWz"
    "BrX+S2gKzgIz37ENDVMFYAYFtMefal2mdNYQ0Y0Pjujb8c+zJwzJ9fgFvpbR1VpZvRU0R/8XRn/kX96Penn0D74dWLEN/D0RQ2Nj"
    "sFnVPD/KVKtU/qjwQuwr301cw3Lturdrtgt5hdZX0C8/x/XwMtP/cp2N7maMW53U0qmjY+sdZb6a6iRk388VmO/1E3NXhh/XQWer"
    "nnh8J9VLQ3q1BxPhj2J/6XMjD4DfgS6q6DEq7GH+Jf5vZ/HTp3Zo2eg1arAXy+deMmOc9v3SX3epX5d4LOlLHP11VlFB+of+2dNP"
    "6B01rV+Lfo55sk4SKzhMbAz+G/EYPVSDPV/AL2amfD3Pi8PCN008JPwr00j0/UUin/8PmaE36qoFEyP6dbT30veprppzSnT5eSdH"
    "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"
)
EMBEDDED_README = r'''# DeskFlip - Windows 11 Profile & App Migration Assistant

A standalone, modern, dark-themed User Profile and Application Migration Utility designed to migrate user configurations, browser data, developer tools, and personalized desktop environments between Windows 11 installations.

---

## 🚀 Features & What It Migrates

### 1. Web Browsers
- **Microsoft Edge**:
    - Bookmarks & Favorites
  - Profiles (`Default`, `Profile 1`, etc.)
  - Passwords & Saved Login Data
  - Browsing History & Web Data
  - Installed Extensions & Extension Storage
  - Local State Master Configuration
- **Google Chrome**:
  - Bookmarks & Favorites
  - Profiles & Preferences
  - Passwords & Login Sessions
  - Browsing History & Cookies
  - Installed Extensions & Web Data
- **Mozilla Firefox**:
  - `profiles.ini` & `installs.ini`
  - Places (Bookmarks & History SQLite databases)
  - Key4 and Saved Logins (`logins.json`)
  - Add-ons, Extensions, and Extension Settings

### 2. Windows 11 Settings & Personalization
- **Desktop Wallpaper**:
  - Active wallpaper image backed up with its original format/extension (for example, `.jpg`, `.png`, or `.webp`)
  - Wallpaper display style (Fit, Fill, Stretch, Tile, Center, Span)
  - Applies automatically via Windows API (`SystemParametersInfoW`) on restore
- **Mouse Settings**:
  - Sensitivity, Pointer speed, Double-click speed, Mouse hover dimensions, Pointer curves, Wheel scrolling preferences
- **Keyboard Settings**:
  - Key repeat speed, Repeat delay, and Indicator state
- **Theme & Colors**:
  - Dark / Light Mode preference for Apps and Windows System
  - Windows Accent Color, Transparency effects, and DWM window colorization
- **Wi-Fi Profiles & Saved Passwords (A:1)**:
  - All-user Wi-Fi profiles, SSIDs, and decrypted WPA2/WPA3 security keys via `netsh wlan export/add`
- **File Explorer Preferences (A:2)**:
  - Hidden files/folders view, file extension visibility, navigation pane behavior, compact mode, and launch target ("This PC" vs "Home")
- **Sound & Audio Settings (A:3)**:
  - Per-application volume mixer policies, default communications devices, and Windows sound schemes
- **Network Drive Mappings**:
  - Persistent mapped network drive letters (e.g. `Z:`, `Y:`) and remote UNC share configurations from `HKCU\Network`
- **Windows Credentials & Vault (A:6)**:
  - Generic Windows credentials, network share logins, and Vault store files
- **User Custom Fonts (A:7)**:
  - Custom fonts installed for the current user in `%LOCALAPPDATA%\Microsoft\Windows\Fonts` and registry registrations

### 3. Microsoft Outlook
- **Outlook Profiles & Accounts**:
  - Outlook 16.0 / 15.0 registry account profiles hierarchy (MAPI account setups)
  - Email Signatures (`%APPDATA%\Microsoft\Signatures`)
  - Autocomplete Nicknames & Stream Caches (`%LOCALAPPDATA%\Microsoft\Outlook\RoamCache`)
  - Personal Storage Tables (`*.pst` data files; offline `.ost` synchronization caches are strictly excluded)

### 4. Shortcuts & Pins
- **Quick Launch Shortcuts**:
  - Custom user shortcuts in `%APPDATA%\Microsoft\Internet Explorer\Quick Launch`
- **Locked Taskbar Icons**:
  - Pinned application shortcuts (`User Pinned\TaskBar`)
  - Windows Taskband layout registry configuration

### 5. Developer & Power User Tools
- **Visual Studio Code**:
  - User settings (`settings.json`), custom keybindings (`keybindings.json`), tasks (`tasks.json`), user code snippets, and installed extensions (code projects strictly excluded)
- **Windows Terminal & PowerShell Profiles (A:4)**:
  - Windows Terminal stable/preview profiles, custom color schemes, keybindings (`settings.json`), and PowerShell profile scripts
- **Git & SSH Configurations (B:2)**:
  - Global Git config (`~/.gitconfig`, `~/.gitignore_global`) and SSH keys, host configs, and known hosts (`~/.ssh/`)
- **Remote Desktop (RDP) Connections (B:3)**:
  - Saved RDP server connections, MRU history, and `Default.rdp` connection file
- **PuTTY, WinSCP & FileZilla (B:4)**:
  - PuTTY stored sessions & host keys, WinSCP registry/ini sites, and FileZilla site manager (`sitemanager.xml`)
- **Notepad++ Settings & Sessions (B:5)**:
  - Custom macros & shortcuts (`shortcuts.xml`), general configuration (`config.xml`), and active tab sessions (`session.xml`)

### 6. Personal Data & Custom Folders
- **Desktop Files & Icon Layout**:
  - Current user's Desktop files and shortcuts, including redirected/OneDrive Desktop locations
  - Explorer desktop icon layout settings from the current user's registry
- **User Downloads Folder**:
  - Files and folders from the current user's redirected or standard Downloads known folder
- **User Documents Folder**:
  - Personal documents and files stored in `%USERPROFILE%\Documents` (excluding offline `.ost` files and temporary caches)
- **User Pictures Folder**:
  - Photos, media, and images stored in `%USERPROFILE%\Pictures`
- **Custom Folders & Locations**:
  - Dynamic user-defined folders: click **"➕ Add Custom Folder..."** in the UI to select and add any arbitrary directories on your drive, with individual toggles and removal options

---

## 🛑 Pre-Backup Application Conflict Detection

Prior to starting any backup that involves running applications (browsers like Edge, Chrome, Firefox, or productivity apps like Outlook, Notepad++, and VS Code):
- **Instant In-Memory Detection**: DeskFlip queries Windows process snapshots via native Win32 APIs (no hanging subprocesses or console pipes).
- **Interactive Termination Dialog**: If any conflicting application is open, a dialog displays the list of running executables and warns that active locks will prevent complete migration.
- **One-Click Close & Proceed**: Clicking **"🛑 Close Applications & Proceed"** terminates the conflicting processes and continues the backup seamlessly, or the user can choose **"Cancel Backup"**.

## ⏹ Stop an Active Job

- Use **"■ Stop Job"** in the bottom status bar or **"■ Stop"** in the live progress window to cancel an active backup or restore.
- Cancellation is cooperative: DeskFlip stops at the next file/module checkpoint rather than force-killing its worker thread. A single file currently being copied may finish first.
- Cancelled backups remove their temporary data and partial archive; restore jobs remove their temporary extraction folder. Existing completed backups are left untouched.
- ZIP extraction checks cancellation between chunks and rejects unsafe paths outside the extraction folder.

---

## 📋 Export Reference File & Auto-Detection on Import

When creating an export backup, **DeskFlip** generates two reference files:
1. `migration_reference.json` (embedded inside the root of the `.zip` package).
2. `<BackupName>.reference.json` (saved alongside the `.zip` archive as a companion file).

### What the Reference File Contains:
- **Timestamp & Hardware Details**: Time of backup, computer name, username, and Windows 11 build info.
- **Selected Options**: List of all modules that were selected during export.
- **Archive Protection**: `encrypted` flag and encryption algorithm are stored in the JSON reference so the import screen knows to request a password.
- **Settings Metadata & Summaries**: Captured parameters such as theme dark/light modes, accent colors, wallpaper style & size, mouse sensitivity curve parameters, keyboard repeat rates, browser profile counts, extension counts, and shortcut names.

### Auto-Detection during Import:
When opening a backup archive on the target PC:
- The app parses the reference manifest.
- **Pre-selects only the items that were included in the export**.
- Updates the badge indicators to `● Available in backup` (green) or `○ Not in this backup` (muted gray).
- Displays a summary caption for each component describing the exact settings packaged from the source PC (e.g. `Exported settings: 1 profile(s), 9 extension(s)` or `Exported settings: Apps=Light, System=Dark`).
- You can still freely tick or untick any item before clicking **Import**.
- A matching **Extract All...** button appears after a valid archive is loaded. It extracts all contents to a chosen folder; password-protected archives prompt for their password first and restore original filenames from the encrypted index.

---

## 📝 Dedicated Step-by-Step Logging & In-App Progress Window

- **Small Live Progress Window**: When creating a backup or running an import, a dedicated, sleek dark sub-window pops up automatically displaying:
  - Current step and operation progress (e.g. `[STEP 3/10] Packaging Microsoft Edge...`).
  - Animated activity progress bar.
  - Streaming color-highlighted activity logs (`[START]`, `[STEP]`, `[SUCCESS]`, `[WARN]`, `[ERROR]`).
  - Quick action buttons to open the raw log file or view the logs directory.
  - Can be toggled open or closed anytime via the **`📊 Live Progress Window`** buttons in the header and status bar.
- **Dual-Stream Logging**: Logs are rendered in real-time in both the main window and the live progress window, and simultaneously written to timestamped disk log files in the `logs/` directory (`DeskFlip_backup_YYYYMMDD_HHMMSS.log` / `DeskFlip_restore_YYYYMMDD_HHMMSS.log`).
- **Instant File Access**:
  - `📄 Open Log File`: Launches the active log file immediately in Notepad.
  - `📁 Logs Folder`: Opens the logs directory in Windows Explorer.

## 🔐 Password-Protected Backups

- Enable **Password-protect archive (AES-256)** before creating a backup; DeskFlip prompts for the password twice.
- Backup payload files and the index mapping them back to their original paths are encrypted with AES-256. ZIP payload entry names are randomized, so original filenames and folder structure do not appear in the ZIP listing.
- The small reference manifest remains readable inside the ZIP so import can detect encryption and prompt for the password; it contains package metadata and the selected custom-folder locations.
- The password is not stored in the archive or reference file. Keep it safe: a lost password cannot be recovered.
- Password-protected archives require `pyzipper` (`python -m pip install pyzipper`). Standard unprotected backups still work without it. When packaging an executable, include the installed dependency.

---

## 🎨 UI & User Experience
- **Single-File Application**: Application code and the logo image are contained in [DeskFlip.py](DeskFlip.py), so no separate image file is needed when packaging; optional AES-256 archive encryption uses `pyzipper`.
- **Modern Sleek Dark Interface**: Styled with `#303944` palette, custom cards, dynamic text wrapping, and integrated logo banner.
- **Selective Migration**: Full tick-box selection for both **Backup** and **Import** phases. You can choose exactly which items to backup and which items to restore.
- **Fast Portable Package**: Bundles everything into an uncompressed, portable `.zip` file containing a `migration_reference.json` metadata tag.

'''

ACTIVE_JOB_CANCEL_EVENT = None
ACTIVE_BACKUP_OUTPUT_PATH = None
ACTIVE_JOB_LOGGER = None
EMBEDDED_LOGO = (
    "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"
    "2slLdwQDArYoXWdrfS0La9XmPRg/fRFOXLgtiQN5uXj7MTbsOiTZrpRLtLzcP57xwEb0RidOwJ0n5Siq60VJwwuUS0D4EqWNLzS9"
    "lOPbz2TPtE2OfedXdcrz8uZX4su5pUIqqe9FWfMrnL39WGI/dSxFKUsy0/ixuPYgX87B7Th4QoqMdAertqhMbuXmPVi5aY8wpsg+"
    "W7lpr/zmc6b5Ow/8JPO687jEDzYNbo5FRdEdUhAeaPWxaJOtccWT1DFpZWGNfGSVujFqvNpzZbZljlXzG7p19mGAqmImuvKRMq7K"
    "lFMxRA4+JEpMp877p0rCM5inQ7jIeISbBxhoyXXowDG+9BYe3ydg+Mhx8tzzQOLy9Z6kF4roZMtYt4SxGMSj/MJvrHzD/s3ZNXNU"
    "nnPmvijByphWHcx8I5n3x32Gy/yoV45PXviN4c8ALDRmc2IbWij+Acrpaw/lCPfpqxk4c+0hTl99IL95ukOOb3MbpKgBN7OK5B3p"
    "lGl/PRPnbz6SY+AzF63VOxF2HLVSk3D+1hOUt7xBBU/LdrxHZdtbVLS+kWt1xzuUNPQir7pLjpeTuLXFd5Wtb1DV9laoknuOjS9R"
    "1vRK6nbqhEXgj289csBC0hbLHNMmUFkoNgD5fyGOw/G4gFg+kX1WUazj9p3yEBUge8PaNRv35r/X8/Ri4uC49r07D8VzgEchpwBv"
    "vgv+xZoDRq9P+fcNKgTiIVlmo3T9LPEQqGoBKK/l70vvyHhJpAc2TsQcy2GRVG0TqW2hRLF4tAisGPM48akr9+WER0ZeLQpruvHt"
    "D6fx3z8ZIBvUCun6cF/0aL3tpFLwoADYP8+y/XThLn6+dF+uJy6S7sn90XO3cDOrWFw6Exb+Ec3NRyX46cId/HxJtWH74+fv4Ph5"
    "dWVx2JZrDKNacAHFeomGEb4T09h2tvTi9mcVG57U9p5VsDo4as622fm4c/tgv/r7oJWV9sZN6kOKwe99/Pr4IlkQWHLmrL8xW43M"
    "2JmNMnlYv/2g/BGN0asZU/09sfYoLvi0fOVP+ezg6p6mk+Z8SCyPpSQhadxM2YpgNZr7j4+Lm/AwvxY5pS04d+uxnPZg8TIuebKY"
    "UTGt0drChKxKSwO598m/ImJWNSxBuaXBsXKm7N8+7o+Dxy+IRXtYUCex3cETl/HvBHa/SDkObdJ/ui5+T8tsFBAUZFAJRkkeuIxC"
    "teJUW7sdF1z1pp9wz814MqZ+H2xrxvXPy4DT9KHnF5xrmPF844a1hqEUBLadr62fmtM6PGnS3Ps3tL38J7Z8e0RcZgh4BWT63tev"
    "mo/zNwgG6eb/YuhAPi4Vt7KKUdn2DsX1vSio7ZbMjxvKtHDMJrkLUNH6VqwN/TwHNcK2DKntIL/wVBwyJEb9XQJjLRYsZy5ci9lL"
    "N+DmwwIBdGZBvRwlupFZhFmL10twy2Knic3MijJj+RTou+qVa+bhkFKydnXG4pl5mv4CwPPzZ3/7itG+by1gXOC4fRhZeX17bY0l"
    "tsfr5Z03T/9c3e89kJvxXJA4C8zHi56ruMf4VOz58TR+On8XP1+8h7nLNsoit/zq7wzQAu7TtAkLNtOIR755/faHX3D8wh0cPnUN"
    "35+8isMnr8pfTh36WV9PXcWxc7exZe9RXSawf3bmTcgIJyA8o2SOw2+v3c9FXdfvKGt+LeBm/YyZJgHO7S8mHbVdv+Hy3adiPWU1"
    "hVgEowh7LFvGcmp0PgVqJal5Bp45/biKD1Gi4cdrp8dwwGHkYRXtyEj6CloE26+RnwKC7d+dk48Ppw/Vdzgycgjzvelfz5/Hy5iQ"
    "sOwlx4bCjGXJ76KN7Dw3aj8w1k0hlQGg2mNj5sYiosri7FW/Y+o+QsdnRoAOo24FOxyZg5X8+9Mjv9zAweOXse/YBRw4flGI9/uP"
    "XcDB4xfxw+lr2Lr3mFp1ki25rs8y5/3+k3EtmbbOMw+clhf+dl2t98yM6QHAfm/kYdpY5VPWjqvWFjHsvB3FegCR/vT8wl4dvpx+"
    "PXLnaq76NInl2/Dq/hmn/5/TBOVtxgvuPH0UnIxtpE2gHkiyKPNnfQaQzt+WupOwgnIm4ROAn9R7dS//J0QKxeYf0jiFYykuM72P"
    "V0VLh1mPaW/8oCX7v5EzTydmMe8shfttntn+3DkYMLmyVnM1/zTGfq/mH9qnX452jtbyuYvDfebKw8hHg8Dry+0nlE8zZ0+23m+n"
    "vb63YwTbem7UxinuAIZBd6Bwv922rmAVEwGBhGXKeWb6C6bSGtzmvxOZuZr5+4QTMpbmj+Q7paLJcXV+HsK09ZHDa+CdjQ/N71B5"
    "eX343Jnbl+HHyt397T13La2nQ7dPA35NRofOvW1jx3ZjueDY5r2yfI5ld3h0Zcp7+ZdZRjjuC69jPZh7DelY7gMMuYILOYbkMK3v"
    "jfDV1RFIGFLv3Pn6GfbGDShMfgdXv8Or/c6dv3+OnhzCWB8fkWfhW38bmL+rNEvqW+75+uZqZCuLIujCjeytJ3L/EaF/jmH4CZGp"
    "/xsPcA7/xnUrWfgXami/9ntxox5DRpCOUF2geeBwheRjOihA/ad5HtjMRF0BWCG4lsDt31WUkDs3l1FvbFdo/rHd/o3gvDlL366F"
    "V20tT7Y/I/DQcfxj+tr43I7hRYPH+UbAkpBmF6mzkNVV96OVqear4j/eS3HaAbpvfEe/bp+238DcXQB6fVpejNxdvXvPApjQlk11"
    "4L7w3XuM2U6sQlyG/IP5Jh/Wuvmfuf16IDCxiQs0h8wzd65KgcHxnLjHJyC/pbBzD8OHx3M4Cxk6nm1rx5JnQdkY3n3PFJnnrj6M"
    "fCxfTj+mjQsMQ3qOXhvnauUbaO/JyvSnx3d0YbyaJy/vG6NT1Z/eQTCDhftP2JYRj8yzMELzBOGtOP1OH0EKgs5MKDjxoMJ9FtF8"
    "41OAtVoWbO78zL0zR/PfIE0bry/dn88qG9B8uF9fW5+c7LiGJzXvQHvf7w+/M6DwFp7RoZajd+/IJjgv2yZgZHzf+UFjx1T9qOdG"
    "hkZnZvE6z7Vu/g/137/+dr/nyQAAAABJRU5ErkJggg=="
)


def check_job_cancelled():
    """Return whether the active job should stop; never raises an exception."""
    return ACTIVE_JOB_CANCEL_EVENT is not None and ACTIVE_JOB_CANCEL_EVENT.is_set()


def report_permission_failure(operation: str, path, error, log_fn=None):
    if isinstance(error, str):
        message = error.lower()
        is_permission_failure = any(
            marker in message
            for marker in (
                "access is denied",
                "permission denied",
                "requires elevation",
                "error 5",
                "winerror 1314",
                "privilege is not held",
            )
        )
    else:
        is_permission_failure = (
            isinstance(error, PermissionError)
            or getattr(error, "errno", None) in (errno.EACCES, errno.EPERM)
            or getattr(error, "winerror", None) in (5, 1314)
        )
    if not is_permission_failure:
        return False

    logger = log_fn or ACTIVE_JOB_LOGGER
    if logger:
        try:
            logger(f"Permission failure during {operation} for '{path}': {error}", level="WARN")
        except Exception:
            pass
    return True


def extract_archive_with_cancel(archive: zipfile.ZipFile, destination: Path):
    """Extract archive members in chunks, rejecting path traversal and checking Stop requests."""
    root = destination.resolve()
    for member in archive.infolist():
        if check_job_cancelled():
            return False
        target = (destination / member.filename).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Unsafe archive path rejected: {member.filename}")
        try:
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member, "r") as source, target.open("wb") as output:
                while True:
                    if check_job_cancelled():
                        return False
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
        except OSError as exc:
            if not report_permission_failure("extracting archive member", target, exc) and ACTIVE_JOB_LOGGER:
                ACTIVE_JOB_LOGGER(f"Could not extract '{target}': {exc}", level="WARN")
            continue
    return True


def extract_encrypted_archive_with_cancel(archive, destination: Path):
    """Decrypt opaque AES ZIP entries and restore their original relative paths."""
    try:
        encrypted_index = archive.read("payload-index")
        entries = json.loads(encrypted_index.decode("utf-8"))
    except Exception as exc:
        raise ValueError("Could not read encrypted archive index; check the password and archive integrity.") from exc

    root = destination.resolve()
    for item in entries:
        if check_job_cancelled():
            return False
        archive_name = item.get("archive_name")
        relative_path = Path(item.get("relative_path", ""))
        if not archive_name or relative_path.is_absolute():
            raise ValueError("Invalid encrypted archive index entry.")
        target = (destination / relative_path).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Unsafe archive path rejected: {relative_path}")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(archive_name, "r") as source, target.open("wb") as output:
                while True:
                    if check_job_cancelled():
                        return False
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
        except OSError as exc:
            if not report_permission_failure("extracting encrypted archive member", target, exc) and ACTIVE_JOB_LOGGER:
                ACTIVE_JOB_LOGGER(f"Could not extract '{target}': {exc}", level="WARN")
            continue
    return True

# Styling Palette - #303944 Theme
THEME = {
    "bg": "#303944",
    "surface": "#303944",
    "surface_alt": "#3a4451",
    "card_bg": "#28303a",
    "accent": "#0078d4",
    "accent_hover": "#1a8ad9",
    "accent_active": "#006cbd",
    "text": "#f3f4f6",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8",
    "border": "#424d5b",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#38bdf8",
    "log_bg": "#1e242b",
}

# ==============================================================================
# Helper Utilities
# ==============================================================================

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = max(0, (window.winfo_screenwidth() - width) // 2)
    y = max(0, (window.winfo_screenheight() - height) // 2)
    window.geometry(f"+{x}+{y}")

def get_program_dir() -> Path:
    """Get the directory of the running script or frozen executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_logs_dir() -> Path:
    """Get a writable logs folder, falling back to LocalAppData if needed."""
    candidate = get_program_dir() / "logs"
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        test_file = candidate / ".test_write"
        test_file.touch()
        test_file.unlink()
        return candidate
    except Exception:
        fallback = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "DeskFlip" / "logs"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def get_appdata_paths():
    """Retrieve standard user environment paths."""
    appdata = Path(os.environ.get("APPDATA", ""))
    localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
    userprofile = Path(os.environ.get("USERPROFILE", ""))
    return appdata, localappdata, userprofile


def get_user_folder(value_name: str, fallback_name: str) -> Path:
    """Resolve a Windows user-known folder, including OneDrive/profile redirection."""
    _, _, userprofile = get_appdata_paths()
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            resolved = Path(os.path.expandvars(value))
            if resolved.is_absolute():
                return resolved
    except Exception as exc:
        report_permission_failure("reading user-folder registry settings", value_name, exc)
        pass
    return userprofile / fallback_name


def get_selected_backup_source_dirs(selected_ids, active_custom):
    appdata, localappdata, userprofile = get_appdata_paths()
    quick_launch = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch"
    source_dirs_by_module = {
        "edge": [localappdata / "Microsoft" / "Edge" / "User Data"],
        "chrome": [localappdata / "Google" / "Chrome" / "User Data"],
        "firefox": [appdata / "Mozilla" / "Firefox"],
        "credentials": [
            localappdata / "Microsoft" / "Credentials",
            appdata / "Microsoft" / "Credentials",
            appdata / "Microsoft" / "Vault",
        ],
        "user_fonts": [localappdata / "Microsoft" / "Windows" / "Fonts"],
        "outlook": [
            appdata / "Microsoft" / "Signatures",
            localappdata / "Microsoft" / "Outlook" / "RoamCache",
            userprofile / "Documents" / "Outlook Files",
            localappdata / "Microsoft" / "Outlook",
            appdata / "Microsoft" / "Outlook",
        ],
        "quick_launch": [quick_launch],
        "taskbar": [quick_launch / "User Pinned" / "TaskBar"],
        "user_desktop": [get_user_folder("Desktop", "Desktop")],
        "user_downloads": [get_user_folder("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads")],
        "user_documents": [userprofile / "Documents"],
        "user_pictures": [userprofile / "Pictures"],
        "terminal_powershell": [
            localappdata / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState",
            localappdata / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState",
            userprofile / "Documents" / "PowerShell",
            userprofile / "Documents" / "WindowsPowerShell",
        ],
        "git_ssh": [userprofile / ".ssh"],
        "ssh_ftp_clients": [appdata / "FileZilla"],
        "notepad_plus_plus": [appdata / "Notepad++"],
        "vscode": [appdata / "Code" / "User", userprofile / ".vscode" / "extensions"],
    }
    source_dirs = [path for module_id in selected_ids for path in source_dirs_by_module.get(module_id, [])]
    source_dirs.extend(Path(item["path"]) for item in active_custom)
    return source_dirs


def get_backup_destination_conflict(output_path: Path, selected_ids, active_custom):
    resolved_output = output_path.resolve()
    for source_dir in get_selected_backup_source_dirs(selected_ids, active_custom):
        try:
            if resolved_output.is_relative_to(source_dir.resolve()):
                return source_dir
        except (OSError, RuntimeError):
            continue
    return None


def detect_image_extension(image_path: Path) -> str:
    """Return an image extension from its filename or common image signature."""
    suffix = image_path.suffix.lower()
    if suffix in {".bmp", ".gif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    try:
        with image_path.open("rb") as image_file:
            header = image_file.read(16)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        if header.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        if header.startswith((b"GIF87a", b"GIF89a")):
            return ".gif"
        if header.startswith(b"BM"):
            return ".bmp"
        if header.startswith((b"II*\x00", b"MM\x00*")):
            return ".tif"
        if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
            return ".webp"
    except OSError as exc:
        report_permission_failure("reading image header", image_path, exc)
        pass
    return ".img"


def get_running_process_names() -> set[str]:
    """Retrieve all running process .exe names on Windows in memory without subprocess or tasklist."""
    running = set()
    try:
        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ('dwSize', ctypes.c_ulong),
                ('cntUsage', ctypes.c_ulong),
                ('th32ProcessID', ctypes.c_ulong),
                ('th32DefaultHeapID', ctypes.c_size_t),
                ('th32ModuleID', ctypes.c_ulong),
                ('cntThreads', ctypes.c_ulong),
                ('th32ParentProcessID', ctypes.c_ulong),
                ('pcPriClassBase', ctypes.c_long),
                ('dwFlags', ctypes.c_ulong),
                ('szExeFile', ctypes.c_wchar * 260)
            ]

        kernel32 = ctypes.windll.kernel32
        hSnap = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
        if hSnap in (-1, 0xFFFFFFFFFFFFFFFF):
            return running

        pe = PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        if kernel32.Process32FirstW(hSnap, ctypes.byref(pe)):
            running.add(pe.szExeFile.lower())
            while kernel32.Process32NextW(hSnap, ctypes.byref(pe)):
                running.add(pe.szExeFile.lower())
        kernel32.CloseHandle(hSnap)
    except Exception:
        pass
    return running


def is_process_running(process_names):
    """Check if any of the given process names are currently running in memory."""
    if isinstance(process_names, str):
        process_names = [process_names]
    active_set = get_running_process_names()
    return any(p.lower() in active_set for p in process_names)


def terminate_processes(process_names, log_fn=None):
    """Attempt graceful taskkill on given processes with timeout protection."""
    if isinstance(process_names, str):
        process_names = [process_names]
    for p in process_names:
        try:
            if log_fn:
                log_fn(f"Closing process '{p}' to release file locks...", level="STEP")
            result = subprocess.run(
                ["taskkill", "/f", "/im", p],
                capture_output=True,
                text=True,
                errors="ignore",
                timeout=5
            )
            if result.returncode != 0:
                report_permission_failure("terminating process", p, f"{result.stdout}\n{result.stderr}", log_fn)
        except Exception as exc:
            report_permission_failure("terminating process", p, exc, log_fn)


def export_registry_key(reg_path, out_file_path):
    """Export an HKCU registry key using reg.exe export."""
    try:
        out_file = Path(out_file_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(
            ["reg", "export", f"HKCU\\{reg_path}", str(out_file), "/y"],
            capture_output=True,
            text=True,
            errors="ignore"
        )
        if res.returncode != 0:
            report_permission_failure("exporting registry key", reg_path, f"{res.stdout}\n{res.stderr}")
        return res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 0
    except Exception as exc:
        report_permission_failure("exporting registry key", reg_path, exc)
        return False


def import_registry_key(reg_file_path):
    """Import an exported registry .reg file using reg.exe import."""
    try:
        p = Path(reg_file_path)
        if not p.exists():
            return False
        res = subprocess.run(
            ["reg", "import", str(p)],
            capture_output=True,
            text=True,
            errors="ignore"
        )
        if res.returncode != 0:
            report_permission_failure("importing registry file", p, f"{res.stdout}\n{res.stderr}")
        return res.returncode == 0
    except Exception as exc:
        report_permission_failure("importing registry file", reg_file_path, exc)
        return False


def safe_copy_file(src_path: Path, target_path: Path) -> bool:
    """Safely copy file using Windows API without triggering debugger PermissionError pauses."""
    name = src_path.name.lower()
    if name == "lock" or name.endswith(".lock") or name.endswith("-lock") or name.endswith(".tmp"):
        return False
    try:
        kernel32 = ctypes.windll.kernel32
        res = kernel32.CopyFileW(str(src_path), str(target_path), False)
        if not res:
            error_code = kernel32.GetLastError()
            if error_code in (5, 32, 33) and ACTIVE_JOB_LOGGER:
                error_message = ctypes.FormatError(error_code).strip()
                ACTIVE_JOB_LOGGER(
                    f"Could not copy '{src_path}' to '{target_path}': {error_message}",
                    level="WARN"
                )
        return bool(res)
    except Exception as exc:
        report_permission_failure("copying file", src_path, exc)
        return False


def is_deskflip_backup_artifact(path: Path) -> bool:
    filename = path.name.lower()
    if filename.endswith(".reference.json"):
        reference_path = path
    elif path.suffix.lower() == ".zip":
        if filename.startswith("win11_profilebackup_"):
            return True
        reference_path = path.with_suffix(".reference.json")
    else:
        return False

    try:
        metadata = json.loads(reference_path.read_text(encoding="utf-8"))
        return metadata.get("app_title") == APP_TITLE
    except Exception:
        return False


def copy_folder_filtered(src_dir: Path, dst_dir: Path, exclude_patterns=None, log_cb=None):
    """Copy directory contents recursively, skipping caches and locked temporary files."""
    if not src_dir.exists():
        return 0, 0
    
    if exclude_patterns is None:
        exclude_patterns = [
            "cache", "code cache", "gpucache", "shadercache", "gralloc",
            "service worker\\cachestorage", "service worker\\scriptcache",
            ".tmp", ".lock", "parent.lock", "lockfile"
        ]

    copied_count = 0
    bytes_count = 0

    def log_walk_error(error):
        report_permission_failure("reading directory", error.filename or src_dir, error, log_cb)

    for root, dirs, files in os.walk(src_dir, onerror=log_walk_error):
        if check_job_cancelled():
            return copied_count, bytes_count
        root_path = Path(root)
        rel_path = root_path.relative_to(src_dir)
        rel_path_str = str(rel_path).lower()

        # Filter out directories
        skip_dir = False
        for pat in exclude_patterns:
            if pat in rel_path_str:
                skip_dir = True
                break
        if skip_dir:
            dirs[:] = []
            continue

        target_root = dst_dir / rel_path
        target_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            if check_job_cancelled():
                return copied_count, bytes_count
            src_file = root_path / f
            if ACTIVE_BACKUP_OUTPUT_PATH is not None:
                try:
                    if src_file.resolve() == ACTIVE_BACKUP_OUTPUT_PATH:
                        continue
                except (OSError, RuntimeError):
                    pass
                if is_deskflip_backup_artifact(src_file):
                    continue
            file_rel_str = str(rel_path / f).lower()

            skip_file = False
            for pat in exclude_patterns:
                if pat in file_rel_str:
                    skip_file = True
                    break
            if skip_file:
                continue

            target_file = target_root / f
            if safe_copy_file(src_file, target_file):
                try:
                    copied_count += 1
                    bytes_count += target_file.stat().st_size
                except Exception:
                    pass

    return copied_count, bytes_count


def reg_key_exists(sub_key_path: str, hkey_root=0x80000001) -> bool:
    """Check if an HKCU registry key exists using Win32 API without raising Python exceptions."""
    try:
        from ctypes import wintypes
        advapi32 = ctypes.windll.advapi32
        hkey = wintypes.HKEY()
        res = advapi32.RegOpenKeyExW(wintypes.HKEY(hkey_root), sub_key_path, 0, 0x20019, ctypes.byref(hkey))
        if res == 0:
            advapi32.RegCloseKey(hkey)
            return True
        if res in (5, 1314):
            report_permission_failure("checking registry key", sub_key_path, f"WinError {res}: {ctypes.FormatError(res)}")
    except Exception as exc:
        report_permission_failure("checking registry key", sub_key_path, exc)
        pass
    return False


def reg_key_subkeys_count(sub_key_path: str, hkey_root=0x80000001) -> int:
    """Return number of subkeys in an HKCU key safely without raising Python exceptions."""
    try:
        from ctypes import wintypes
        advapi32 = ctypes.windll.advapi32
        hkey = wintypes.HKEY()
        res = advapi32.RegOpenKeyExW(wintypes.HKEY(hkey_root), sub_key_path, 0, 0x20019, ctypes.byref(hkey))
        if res != 0:
            if res in (5, 1314):
                report_permission_failure("reading registry subkeys", sub_key_path, f"WinError {res}: {ctypes.FormatError(res)}")
            return 0
        num_subkeys = wintypes.DWORD()
        num_values = wintypes.DWORD()
        advapi32.RegQueryInfoKeyW(
            hkey, None, None, None,
            ctypes.byref(num_subkeys), None, None,
            ctypes.byref(num_values), None, None, None, None
        )
        advapi32.RegCloseKey(hkey)
        return num_subkeys.value
    except Exception as exc:
        report_permission_failure("reading registry subkeys", sub_key_path, exc)
        return 0


def backup_registry_dict(key_path, subkeys_to_read=None):
    """Read values from an HKCU registry path into a JSON-serializable dictionary."""
    data = {}
    if not reg_key_exists(key_path):
        return data
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            num_vals = winreg.QueryInfoKey(k)[1]
            for i in range(num_vals):
                name, val, typ = winreg.EnumValue(k, i)
                if subkeys_to_read is None or name in subkeys_to_read:
                    if isinstance(val, bytes):
                        data[name] = {"val": base64.b64encode(val).decode("ascii"), "type": typ, "is_bytes": True}
                    else:
                        data[name] = {"val": val, "type": typ, "is_bytes": False}
    except Exception as exc:
        report_permission_failure("reading registry values", key_path, exc)
        pass
    return data


def restore_registry_dict(key_path, data):
    """Write dictionary values back into HKCU registry."""
    if not data:
        return 0
    count = 0
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            for name, item in data.items():
                val = item.get("val")
                typ = item.get("type", winreg.REG_SZ)
                if item.get("is_bytes"):
                    val = base64.b64decode(val.encode("ascii"))
                try:
                    winreg.SetValueEx(k, name, 0, typ, val)
                    count += 1
                except Exception as exc:
                    report_permission_failure("writing registry value", f"{key_path}\\{name}", exc)
                    pass
    except Exception as exc:
        report_permission_failure("writing registry key", key_path, exc)
        pass
    return count


# ==============================================================================
# Migration Modules
# ==============================================================================

class MigrationCategory:
    CAT_BROWSERS = "Web Browsers"
    CAT_WINDOWS = "Windows Settings & Theme"
    CAT_SHORTCUTS = "Taskbar & Quick Launch"
    CAT_OFFICE = "Outlook & Mail"
    CAT_DEV_TOOLS = "Developer & Power User Tools"
    CAT_USER_DATA = "Personal Data & User Folders"


class ModuleEdge:
    ID = "edge"
    NAME = "Microsoft Edge"
    CATEGORY = MigrationCategory.CAT_BROWSERS
    DESCRIPTION = "Favorites, profiles, passwords, login sessions, history, and browser extensions"
    PROCESSES = ["msedge.exe"]

    @staticmethod
    def detect():
        _, localappdata, _ = get_appdata_paths()
        edge_data = localappdata / "Microsoft" / "Edge" / "User Data"
        if not edge_data.exists():
            return False, "Not installed"
        
        profiles = [p.name for p in edge_data.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile "))]
        total_ext = 0
        for pr in profiles:
            ext_dir = edge_data / pr / "Extensions"
            if ext_dir.exists():
                total_ext += len([x for x in ext_dir.iterdir() if x.is_dir()])
        return True, f"{len(profiles)} profile(s), {total_ext} extension(s) found"

    @staticmethod
    def backup(dest_dir: Path, log):
        _, localappdata, _ = get_appdata_paths()
        src = localappdata / "Microsoft" / "Edge" / "User Data"
        if not src.exists():
            log("Microsoft Edge User Data not found, skipping.", level="WARN")
            return {"status": "not_found"}

        dest = dest_dir / "Edge" / "User Data"
        dest.mkdir(parents=True, exist_ok=True)

        log("Backing up Edge Local State master configuration...", level="STEP")
        local_state = src / "Local State"
        if local_state.exists():
            try:
                shutil.copy2(local_state, dest / "Local State")
                log("Edge Local State saved.", level="INFO")
            except Exception as e:
                log(f"Warning backing up Local State: {e}", level="WARN")

        profiles_backed = []
        total_ext_count = 0
        total_files = 0

        for item in src.iterdir():
            if item.is_dir() and (item.name == "Default" or item.name.startswith("Profile ")):
                p_dest = dest / item.name
                p_dest.mkdir(parents=True, exist_ok=True)
                log(f"Processing Edge profile '{item.name}'...", level="STEP")

                vital_files = [
                    "Bookmarks", "Bookmarks.bak", "Preferences", "Secure Preferences",
                    "History", "History-journal", "Login Data", "Login Data-journal",
                    "Login Data For Account", "Web Data", "Web Data-journal",
                    "Favicons", "Top Sites", "Shortcuts", "Cookies", "Network Action Predictor"
                ]
                vf_count = 0
                for vf in vital_files:
                    fpath = item / vf
                    if fpath.exists():
                        try:
                            shutil.copy2(fpath, p_dest / vf)
                            vf_count += 1
                        except Exception as exc:
                            report_permission_failure("copying Edge profile file", fpath, exc, log)
                            pass
                log(f"Profile '{item.name}': saved {vf_count} database/settings files (Favorites, Logins, History).", level="INFO")

                vital_dirs = [
                    "Extensions", "Extension Rules", "Extension State",
                    "Local Storage", "Sync Data", "Accounts", "Network"
                ]
                p_files = 0
                for vd in vital_dirs:
                    dpath = item / vd
                    if dpath.exists():
                        cnt, _ = copy_folder_filtered(dpath, p_dest / vd, log_cb=log)
                        p_files += cnt

                ext_dir = item / "Extensions"
                ext_count = len([x for x in ext_dir.iterdir() if x.is_dir()]) if ext_dir.exists() else 0
                total_ext_count += ext_count
                total_files += (vf_count + p_files)
                profiles_backed.append(item.name)
                log(f"Profile '{item.name}' complete: {ext_count} extensions, {p_files} supporting data files.", level="INFO")

        return {
            "profiles": profiles_backed,
            "extensions_count": total_ext_count,
            "total_files": total_files,
            "summary": f"{len(profiles_backed)} profile(s), {total_ext_count} extension(s)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        edge_backup = src_dir / "Edge" / "User Data"
        if not edge_backup.exists():
            log("No Edge backup data found in archive.", level="WARN")
            return

        if is_process_running(ModuleEdge.PROCESSES):
            terminate_processes(ModuleEdge.PROCESSES, log_fn=log)

        _, localappdata, _ = get_appdata_paths()
        target = localappdata / "Microsoft" / "Edge" / "User Data"
        target.mkdir(parents=True, exist_ok=True)

        log("Restoring Edge profiles, favorites, passwords, and extensions...", level="STEP")
        copied, _ = copy_folder_filtered(edge_backup, target, log_cb=log)
        log(f"Microsoft Edge restore completed successfully ({copied} files restored).", level="SUCCESS")


class ModuleChrome:
    ID = "chrome"
    NAME = "Google Chrome"
    CATEGORY = MigrationCategory.CAT_BROWSERS
    DESCRIPTION = "Favorites, profiles, passwords, login sessions, history, and browser extensions"
    PROCESSES = ["chrome.exe"]

    @staticmethod
    def detect():
        _, localappdata, _ = get_appdata_paths()
        chrome_data = localappdata / "Google" / "Chrome" / "User Data"
        if not chrome_data.exists():
            return False, "Not installed"
        
        profiles = [p.name for p in chrome_data.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile "))]
        total_ext = 0
        for pr in profiles:
            ext_dir = chrome_data / pr / "Extensions"
            if ext_dir.exists():
                total_ext += len([x for x in ext_dir.iterdir() if x.is_dir()])
        return True, f"{len(profiles)} profile(s), {total_ext} extension(s) found"

    @staticmethod
    def backup(dest_dir: Path, log):
        _, localappdata, _ = get_appdata_paths()
        src = localappdata / "Google" / "Chrome" / "User Data"
        if not src.exists():
            log("Google Chrome User Data not found, skipping.", level="WARN")
            return {"status": "not_found"}

        dest = dest_dir / "Chrome" / "User Data"
        dest.mkdir(parents=True, exist_ok=True)

        log("Backing up Chrome Local State master configuration...", level="STEP")
        local_state = src / "Local State"
        if local_state.exists():
            try:
                shutil.copy2(local_state, dest / "Local State")
                log("Chrome Local State saved.", level="INFO")
            except Exception as e:
                log(f"Warning backing up Local State: {e}", level="WARN")

        profiles_backed = []
        total_ext_count = 0
        total_files = 0

        for item in src.iterdir():
            if item.is_dir() and (item.name == "Default" or item.name.startswith("Profile ")):
                p_dest = dest / item.name
                p_dest.mkdir(parents=True, exist_ok=True)
                log(f"Processing Chrome profile '{item.name}'...", level="STEP")

                vital_files = [
                    "Bookmarks", "Bookmarks.bak", "Preferences", "Secure Preferences",
                    "History", "History-journal", "Login Data", "Login Data-journal",
                    "Login Data For Account", "Web Data", "Web Data-journal",
                    "Favicons", "Top Sites", "Shortcuts", "Cookies"
                ]
                vf_count = 0
                for vf in vital_files:
                    fpath = item / vf
                    if fpath.exists():
                        try:
                            shutil.copy2(fpath, p_dest / vf)
                            vf_count += 1
                        except Exception as exc:
                            report_permission_failure("copying Chrome profile file", fpath, exc, log)
                            pass
                log(f"Profile '{item.name}': saved {vf_count} database/settings files.", level="INFO")

                vital_dirs = [
                    "Extensions", "Extension Rules", "Extension State",
                    "Local Storage", "Sync Data", "Accounts", "Network"
                ]
                p_files = 0
                for vd in vital_dirs:
                    dpath = item / vd
                    if dpath.exists():
                        cnt, _ = copy_folder_filtered(dpath, p_dest / vd, log_cb=log)
                        p_files += cnt

                ext_dir = item / "Extensions"
                ext_count = len([x for x in ext_dir.iterdir() if x.is_dir()]) if ext_dir.exists() else 0
                total_ext_count += ext_count
                total_files += (vf_count + p_files)
                profiles_backed.append(item.name)
                log(f"Profile '{item.name}' complete: {ext_count} extensions, {p_files} supporting data files.", level="INFO")

        return {
            "profiles": profiles_backed,
            "extensions_count": total_ext_count,
            "total_files": total_files,
            "summary": f"{len(profiles_backed)} profile(s), {total_ext_count} extension(s)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        chrome_backup = src_dir / "Chrome" / "User Data"
        if not chrome_backup.exists():
            log("No Chrome backup data found in archive.", level="WARN")
            return

        if is_process_running(ModuleChrome.PROCESSES):
            terminate_processes(ModuleChrome.PROCESSES, log_fn=log)

        _, localappdata, _ = get_appdata_paths()
        target = localappdata / "Google" / "Chrome" / "User Data"
        target.mkdir(parents=True, exist_ok=True)

        log("Restoring Chrome profiles, favorites, passwords, and extensions...", level="STEP")
        copied, _ = copy_folder_filtered(chrome_backup, target, log_cb=log)
        log(f"Google Chrome restore completed successfully ({copied} files restored).", level="SUCCESS")


class ModuleFirefox:
    ID = "firefox"
    NAME = "Mozilla Firefox"
    CATEGORY = MigrationCategory.CAT_BROWSERS
    DESCRIPTION = "Favorites, bookmarks, logins, passwords, browsing history, and extensions"
    PROCESSES = ["firefox.exe"]

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        ff_data = appdata / "Mozilla" / "Firefox"
        if not ff_data.exists():
            return False, "Not installed"
        profiles_ini = ff_data / "profiles.ini"
        if profiles_ini.exists():
            return True, "Firefox configuration and profiles found"
        return False, "Not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        appdata, _, _ = get_appdata_paths()
        src = appdata / "Mozilla" / "Firefox"
        if not src.exists():
            log("Firefox directory not found, skipping.", level="WARN")
            return {"status": "not_found"}

        dest = dest_dir / "Firefox"
        dest.mkdir(parents=True, exist_ok=True)

        log("Backing up Firefox profile index (profiles.ini)...", level="STEP")
        for ini_name in ["profiles.ini", "installs.ini"]:
            ini_path = src / ini_name
            if ini_path.exists():
                try:
                    shutil.copy2(ini_path, dest / ini_name)
                except Exception as exc:
                    report_permission_failure("copying Firefox profile index", ini_path, exc, log)
                    pass

        profiles_dir = src / "Profiles"
        profiles_backed = []
        total_files = 0

        if profiles_dir.exists():
            for p_dir in profiles_dir.iterdir():
                if p_dir.is_dir():
                    log(f"Processing Firefox profile '{p_dir.name}'...", level="STEP")
                    target_p = dest / "Profiles" / p_dir.name
                    target_p.mkdir(parents=True, exist_ok=True)

                    vital_files = [
                        "places.sqlite", "places.sqlite-wal", "key4.db", "logins.json",
                        "logins-backup.json", "prefs.js", "favicons.sqlite",
                        "permissions.sqlite", "handlers.json", "search.json.mozlz4",
                        "containers.json", "formhistory.sqlite"
                    ]
                    vf_count = 0
                    for vf in vital_files:
                        fp = p_dir / vf
                        if fp.exists():
                            try:
                                shutil.copy2(fp, target_p / vf)
                                vf_count += 1
                            except Exception as exc:
                                report_permission_failure("copying Firefox profile file", fp, exc, log)
                                pass

                    dir_files = 0
                    for vd in ["extensions", "extension-data", "extension-settings", "storage"]:
                        dp = p_dir / vd
                        if dp.exists():
                            cnt, _ = copy_folder_filtered(dp, target_p / vd, log_cb=log)
                            dir_files += cnt

                    total_files += (vf_count + dir_files)
                    profiles_backed.append(p_dir.name)
                    log(f"Firefox profile '{p_dir.name}': saved {vf_count} core DBs and {dir_files} extension files.", level="INFO")

        return {
            "profiles": profiles_backed,
            "total_files": total_files,
            "summary": f"{len(profiles_backed)} profile(s) ({total_files} files)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        ff_backup = src_dir / "Firefox"
        if not ff_backup.exists():
            log("No Firefox backup data found in archive.", level="WARN")
            return

        if is_process_running(ModuleFirefox.PROCESSES):
            terminate_processes(ModuleFirefox.PROCESSES, log_fn=log)

        appdata, _, _ = get_appdata_paths()
        target = appdata / "Mozilla" / "Firefox"
        target.mkdir(parents=True, exist_ok=True)

        log("Restoring Firefox profiles, bookmarks (places.sqlite), logins, and add-ons...", level="STEP")
        copied, _ = copy_folder_filtered(ff_backup, target, log_cb=log)
        log(f"Mozilla Firefox restore completed successfully ({copied} files restored).", level="SUCCESS")


class ModuleWallpaper:
    ID = "wallpaper"
    NAME = "Desktop Wallpaper"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Current Windows 11 desktop wallpaper image, position style, and tiling"

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        tc = appdata / "Microsoft" / "Windows" / "Themes" / "TranscodedWallpaper"
        if tc.exists():
            return True, f"Detected ({round(tc.stat().st_size / 1024)} KB)"
        return True, "Default wallpaper"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Wallpaper"
        dest.mkdir(parents=True, exist_ok=True)

        log("Locating active Windows 11 desktop wallpaper...", level="STEP")
        appdata, _, _ = get_appdata_paths()
        copied = False
        img_size_kb = 0
        wallpaper_path = None
        try:
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 512, buf, 0)
            candidate = Path(buf.value)
            if candidate.is_file():
                wallpaper_path = candidate
        except Exception:
            pass

        if wallpaper_path is None:
            transcoded = appdata / "Microsoft" / "Windows" / "Themes" / "TranscodedWallpaper"
            if transcoded.is_file():
                wallpaper_path = transcoded

        if wallpaper_path and wallpaper_path.stat().st_size > 0:
            try:
                ext = detect_image_extension(wallpaper_path)
                shutil.copy2(wallpaper_path, dest / f"wallpaper{ext}")
                copied = True
                img_size_kb = round(wallpaper_path.stat().st_size / 1024, 1)
                log(f"Active wallpaper backed up as {ext} ({img_size_kb} KB).", level="INFO")
            except Exception as e:
                log(f"Warning backing up active wallpaper: {e}", level="WARN")

        reg_data = backup_registry_dict(r"Control Panel\Desktop", ["WallpaperStyle", "TileWallpaper"])
        (dest / "wallpaper_settings.json").write_text(json.dumps(reg_data, indent=2), encoding="utf-8")
        style_val = reg_data.get("WallpaperStyle", {}).get("val", "10")
        log(f"Wallpaper positioning style saved (WallpaperStyle={style_val}).", level="INFO")

        return {
            "has_image": copied,
            "image_size_kb": img_size_kb,
            "style_settings": reg_data,
            "summary": f"Image saved ({img_size_kb} KB, Style {style_val})"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Wallpaper"
        if not dest.exists():
            log("No wallpaper backup found.", level="WARN")
            return

        log("Restoring desktop wallpaper style registry configuration...", level="STEP")
        settings_file = dest / "wallpaper_settings.json"
        if settings_file.exists():
            try:
                reg_data = json.loads(settings_file.read_text(encoding="utf-8"))
                restore_registry_dict(r"Control Panel\Desktop", reg_data)
            except Exception as e:
                log(f"Warning restoring wallpaper registry settings: {e}", level="WARN")

        wp_candidates = list(dest.glob("wallpaper*"))
        target_img = None
        for cand in wp_candidates:
            if cand.suffix != ".json":
                target_img = cand
                break

        if target_img and target_img.exists():
            log("Copying wallpaper image to Windows Themes directory...", level="STEP")
            appdata, _, _ = get_appdata_paths()
            theme_dir = appdata / "Microsoft" / "Windows" / "Themes"
            theme_dir.mkdir(parents=True, exist_ok=True)
            ext = detect_image_extension(target_img)
            target_wallpaper = theme_dir / f"DeskFlipWallpaper{ext}"
            try:
                shutil.copy2(target_img, target_wallpaper)
            except Exception as exc:
                report_permission_failure("restoring wallpaper image", target_img, exc, log)
                pass

            log("Applying wallpaper to desktop via Win32 SystemParametersInfoW...", level="STEP")
            try:
                img_path_str = str(target_wallpaper.resolve())
                res = ctypes.windll.user32.SystemParametersInfoW(
                    SPI_SETDESKWALLPAPER,
                    0,
                    img_path_str,
                    SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
                )
                if res:
                    log("Wallpaper image and layout successfully applied to Windows 11 desktop!", level="SUCCESS")
                else:
                    log("Wallpaper copied; requested desktop refresh.", level="INFO")
            except Exception as e:
                log(f"Error applying wallpaper: {e}", level="ERROR")


class ModuleMouse:
    ID = "mouse"
    NAME = "Mouse Settings"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Cursor sensitivity, double-click speed, mouse wheel, acceleration, and button swapping"

    @staticmethod
    def detect():
        return True, "Configured in Windows"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Mouse"
        dest.mkdir(parents=True, exist_ok=True)
        log("Querying mouse sensitivity curves and settings from HKCU\\Control Panel\\Mouse...", level="STEP")
        data = backup_registry_dict(r"Control Panel\Mouse")
        (dest / "mouse_settings.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        sensitivity = data.get("MouseSensitivity", {}).get("val", "Default")
        log(f"Backed up {len(data)} mouse parameters (Sensitivity={sensitivity}).", level="INFO")

        return {
            "parameters_count": len(data),
            "sensitivity": sensitivity,
            "summary": f"{len(data)} parameters (Sensitivity {sensitivity})"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Mouse" / "mouse_settings.json"
        if not dest.exists():
            log("No mouse settings backup found.", level="WARN")
            return
        log("Restoring mouse sensitivity and button preferences...", level="STEP")
        try:
            data = json.loads(dest.read_text(encoding="utf-8"))
            restored = restore_registry_dict(r"Control Panel\Mouse", data)
            ctypes.windll.user32.SystemParametersInfoW(0x0071, 0, 0, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            log(f"Restored {restored} mouse parameters into Windows and broadcasted change.", level="SUCCESS")
        except Exception as e:
            log(f"Error restoring mouse settings: {e}", level="ERROR")


class ModuleKeyboard:
    ID = "keyboard"
    NAME = "Keyboard Settings"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Key repeat rate, repeat delay, and initial indicators"

    @staticmethod
    def detect():
        return True, "Configured in Windows"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Keyboard"
        dest.mkdir(parents=True, exist_ok=True)
        log("Reading keyboard repeat rate and delay parameters...", level="STEP")
        data = backup_registry_dict(r"Control Panel\Keyboard")
        (dest / "keyboard_settings.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        speed = data.get("KeyboardSpeed", {}).get("val", "Default")
        delay = data.get("KeyboardDelay", {}).get("val", "Default")
        log(f"Backed up {len(data)} keyboard settings (Speed={speed}, Delay={delay}).", level="INFO")

        return {
            "parameters_count": len(data),
            "speed": speed,
            "delay": delay,
            "summary": f"Speed={speed}, Delay={delay}"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Keyboard" / "keyboard_settings.json"
        if not dest.exists():
            log("No keyboard settings backup found.", level="WARN")
            return
        log("Restoring keyboard delay and repeat rates...", level="STEP")
        try:
            data = json.loads(dest.read_text(encoding="utf-8"))
            restored = restore_registry_dict(r"Control Panel\Keyboard", data)
            ctypes.windll.user32.SystemParametersInfoW(0x001F, 0, 0, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            log(f"Restored {restored} keyboard parameters into Windows.", level="SUCCESS")
        except Exception as e:
            log(f"Error restoring keyboard settings: {e}", level="ERROR")


class ModuleThemes:
    ID = "themes"
    NAME = "Theme & Colors"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Light/Dark mode preferences, accent colors, transparency, and DWM window effects"

    @staticmethod
    def detect():
        return True, "Configured in Windows"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Themes"
        dest.mkdir(parents=True, exist_ok=True)

        log("Reading Windows 11 Personalization, Theme and DWM colorization settings...", level="STEP")
        personalize_data = backup_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        dwm_data = backup_registry_dict(r"Software\Microsoft\Windows\DWM")

        full_data = {
            "Personalize": personalize_data,
            "DWM": dwm_data
        }
        (dest / "theme_settings.json").write_text(json.dumps(full_data, indent=2), encoding="utf-8")

        apps_light = personalize_data.get("AppsUseLightTheme", {}).get("val", 1)
        sys_light = personalize_data.get("SystemUsesLightTheme", {}).get("val", 0)
        mode_str = f"Apps={'Light' if apps_light == 1 else 'Dark'}, System={'Light' if sys_light == 1 else 'Dark'}"
        log(f"Saved Theme preferences: {mode_str}.", level="INFO")

        return {
            "mode": mode_str,
            "apps_light": apps_light,
            "sys_light": sys_light,
            "summary": mode_str
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Themes" / "theme_settings.json"
        if not dest.exists():
            log("No theme backup found.", level="WARN")
            return
        log("Restoring Windows 11 Dark/Light theme mode and accent colors...", level="STEP")
        try:
            full_data = json.loads(dest.read_text(encoding="utf-8"))
            if "Personalize" in full_data:
                restore_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", full_data["Personalize"])
            if "DWM" in full_data:
                restore_registry_dict(r"Software\Microsoft\Windows\DWM", full_data["DWM"])
            
            # Broadcast setting change
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.PostMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "ImmersiveColorSet")
            log("Theme, Dark/Light modes, and Accent colors restored successfully.", level="SUCCESS")
        except Exception as e:
            log(f"Error restoring theme settings: {e}", level="ERROR")


class ModuleOutlook:
    ID = "outlook"
    NAME = "Outlook Profiles, Accounts & PSTs"
    CATEGORY = MigrationCategory.CAT_OFFICE
    DESCRIPTION = "MAPI profiles, accounts, email signatures, autocomplete cache, and personal .pst files (offline .ost excluded)"
    PROCESSES = ["outlook.exe"]

    @staticmethod
    def detect():
        n16 = reg_key_subkeys_count(r"Software\Microsoft\Office\16.0\Outlook\Profiles")
        if n16 > 0:
            return True, f"{n16} profile(s) found"
        n15 = reg_key_subkeys_count(r"Software\Microsoft\Office\15.0\Outlook\Profiles")
        if n15 > 0:
            return True, f"{n15} profile(s) (Office 2013) found"
        return False, "No Outlook profiles found"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Outlook"
        dest.mkdir(parents=True, exist_ok=True)

        appdata, localappdata, userprofile = get_appdata_paths()

        log("Exporting Outlook MAPI profile and account registry hierarchy (16.0)...", level="STEP")
        p16 = r"Software\Microsoft\Office\16.0\Outlook\Profiles"
        exported_16 = export_registry_key(p16, dest / "Outlook_Profiles_16.0.reg")
        if exported_16:
            log("Outlook 16.0 registry profiles successfully exported.", level="INFO")
        else:
            log("No Outlook 16.0 registry profiles found to export.", level="INFO")

        p15 = r"Software\Microsoft\Office\15.0\Outlook\Profiles"
        export_registry_key(p15, dest / "Outlook_Profiles_15.0.reg")

        # 2. Email Signatures
        log("Checking for Outlook email signatures...", level="STEP")
        sig_dir = appdata / "Microsoft" / "Signatures"
        sig_count = 0
        if sig_dir.exists() and any(sig_dir.iterdir()):
            sig_count, _ = copy_folder_filtered(sig_dir, dest / "Signatures", log_cb=log)
            log(f"Backed up {sig_count} email signature files.", level="INFO")
        else:
            log("No email signatures found.", level="INFO")

        # 3. RoamCache / Autocomplete Nicknames
        log("Checking for Outlook autocomplete stream caches (RoamCache)...", level="STEP")
        roam_dir = localappdata / "Microsoft" / "Outlook" / "RoamCache"
        roam_count = 0
        if roam_dir.exists() and any(roam_dir.iterdir()):
            roam_count, _ = copy_folder_filtered(roam_dir, dest / "RoamCache", log_cb=log)
            log(f"Backed up {roam_count} RoamCache autocomplete stream files.", level="INFO")
        else:
            log("No RoamCache files found.", level="INFO")

        # 4. Personal Storage Tables (.pst files only - STRICTLY EXCLUDE .ost files)
        log("Searching for Outlook Personal Folders (.pst files, excluding .ost)...", level="STEP")
        pst_dest = dest / "PST_Files"
        pst_count = 0
        total_pst_bytes = 0
        search_dirs = [
            userprofile / "Documents" / "Outlook Files",
            localappdata / "Microsoft" / "Outlook",
            appdata / "Microsoft" / "Outlook"
        ]
        seen_psts = set()
        for sdir in search_dirs:
            if sdir.exists():
                for item in sdir.iterdir():
                    if item.is_file() and item.suffix.lower() == ".pst":
                        # STRICTLY EXCLUDE any .ost files!
                        canon = str(item.resolve()).lower()
                        if canon not in seen_psts:
                            seen_psts.add(canon)
                            pst_dest.mkdir(parents=True, exist_ok=True)
                            if safe_copy_file(item, pst_dest / item.name):
                                pst_count += 1
                                total_pst_bytes += item.stat().st_size
                                log(f"Backed up Outlook PST file: {item.name} ({round(item.stat().st_size / (1024*1024), 1)} MB).", level="INFO")

        pst_summary = f"{pst_count} PST file(s) ({round(total_pst_bytes / (1024*1024), 1)} MB)" if pst_count else "0 PSTs (OSTs skipped)"
        log(f"Outlook data files check complete: {pst_summary}.", level="INFO")

        summary = f"Profiles: {'Yes' if exported_16 else 'No'}, Signatures: {sig_count}, PSTs: {pst_count}"
        return {
            "has_registry_16": exported_16,
            "signatures_count": sig_count,
            "roamcache_count": roam_count,
            "pst_count": pst_count,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Outlook"
        if not dest.exists():
            log("No Outlook backup found in archive.", level="WARN")
            return

        if is_process_running(ModuleOutlook.PROCESSES):
            terminate_processes(ModuleOutlook.PROCESSES, log_fn=log)

        appdata, localappdata, userprofile = get_appdata_paths()

        r16 = dest / "Outlook_Profiles_16.0.reg"
        if r16.exists():
            log("Importing Outlook 16.0 account profiles into registry...", level="STEP")
            if import_registry_key(r16):
                log("Outlook 16.0 profiles & account configurations imported into registry.", level="SUCCESS")
            else:
                log("Failed to import Outlook 16.0 registry file.", level="ERROR")

        r15 = dest / "Outlook_Profiles_15.0.reg"
        if r15.exists():
            import_registry_key(r15)

        sig_backup = dest / "Signatures"
        if sig_backup.exists():
            log("Restoring Outlook email signatures...", level="STEP")
            target_sig = appdata / "Microsoft" / "Signatures"
            target_sig.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(sig_backup, target_sig, log_cb=log)
            log(f"Restored {copied} signature files.", level="SUCCESS")

        roam_backup = dest / "RoamCache"
        if roam_backup.exists():
            log("Restoring Outlook autocomplete RoamCache streams...", level="STEP")
            target_roam = localappdata / "Microsoft" / "Outlook" / "RoamCache"
            target_roam.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(roam_backup, target_roam, log_cb=log)
            log(f"Restored {copied} autocomplete RoamCache files.", level="SUCCESS")

        # Restore PST files to Documents\Outlook Files
        pst_backup = dest / "PST_Files"
        if pst_backup.exists():
            log("Restoring Outlook .pst personal data files...", level="STEP")
            target_pst_dir = userprofile / "Documents" / "Outlook Files"
            target_pst_dir.mkdir(parents=True, exist_ok=True)
            pst_restored = 0
            for pf in pst_backup.iterdir():
                if pf.is_file() and pf.suffix.lower() == ".pst":
                    if safe_copy_file(pf, target_pst_dir / pf.name):
                        pst_restored += 1
                        log(f"Restored {pf.name} to {target_pst_dir}.", level="SUCCESS")
            log(f"Restored {pst_restored} Outlook .pst file(s).", level="INFO")


class ModuleQuickLaunch:
    ID = "quick_launch"
    NAME = "Quick Launch Shortcuts"
    CATEGORY = MigrationCategory.CAT_SHORTCUTS
    DESCRIPTION = "Shortcuts stored in the Windows Quick Launch directory"

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        ql_dir = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch"
        if ql_dir.exists():
            files = [f for f in ql_dir.iterdir() if f.is_file() and f.name.lower() != "desktop.ini"]
            return True, f"{len(files)} shortcut(s) found"
        return False, "Not found"

    @staticmethod
    def backup(dest_dir: Path, log):
        appdata, _, _ = get_appdata_paths()
        src = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch"
        if not src.exists():
            log("Quick Launch directory not found, skipping.", level="WARN")
            return {"shortcuts_count": 0, "summary": "0 shortcuts"}

        dest = dest_dir / "Shortcuts" / "Quick Launch"
        dest.mkdir(parents=True, exist_ok=True)

        log("Backing up Quick Launch shortcuts...", level="STEP")
        copied = 0
        names = []
        for item in src.iterdir():
            if item.is_file() and item.name.lower() != "desktop.ini":
                try:
                    shutil.copy2(item, dest / item.name)
                    copied += 1
                    names.append(item.name)
                except Exception as exc:
                    report_permission_failure("copying Quick Launch shortcut", item, exc, log)
                    pass
        log(f"Backed up {copied} Quick Launch shortcuts ({', '.join(names[:4])}).", level="INFO")

        return {
            "shortcuts_count": copied,
            "names": names,
            "summary": f"{copied} shortcut(s) ({', '.join(names[:3])}{'...' if len(names) > 3 else ''})"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Shortcuts" / "Quick Launch"
        if not dest.exists():
            log("No Quick Launch backup found.", level="WARN")
            return

        log("Restoring Quick Launch shortcuts...", level="STEP")
        appdata, _, _ = get_appdata_paths()
        target = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch"
        target.mkdir(parents=True, exist_ok=True)

        copied = 0
        for item in dest.iterdir():
            if item.is_file():
                try:
                    shutil.copy2(item, target / item.name)
                    copied += 1
                except Exception as exc:
                    report_permission_failure("restoring Quick Launch shortcut", item, exc, log)
                    pass
        log(f"Restored {copied} Quick Launch shortcuts.", level="SUCCESS")


class ModuleTaskbar:
    ID = "taskbar"
    NAME = "Taskbar Pinned Icons"
    CATEGORY = MigrationCategory.CAT_SHORTCUTS
    DESCRIPTION = "Pinned application shortcuts on the Windows 11 Taskbar and Taskband layout"

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        tb_dir = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch" / "User Pinned" / "TaskBar"
        if tb_dir.exists():
            files = [f for f in tb_dir.iterdir() if f.is_file() and f.name.lower() != "desktop.ini"]
            return True, f"{len(files)} pinned app(s) found"
        return False, "No pinned shortcuts found"

    @staticmethod
    def backup(dest_dir: Path, log):
        appdata, _, _ = get_appdata_paths()
        src = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch" / "User Pinned" / "TaskBar"
        dest = dest_dir / "Shortcuts" / "Taskbar"
        dest.mkdir(parents=True, exist_ok=True)

        log("Backing up locked taskbar pinned shortcut icons...", level="STEP")
        copied = 0
        names = []
        if src.exists():
            for item in src.iterdir():
                if item.is_file() and item.name.lower() != "desktop.ini":
                    try:
                        shutil.copy2(item, dest / item.name)
                        copied += 1
                        names.append(item.name)
                    except Exception as exc:
                        report_permission_failure("copying taskbar shortcut", item, exc, log)
                        pass
        log(f"Backed up {copied} pinned taskbar shortcut icons ({', '.join(names[:4])}).", level="INFO")

        log("Exporting Windows 11 Taskband layout registry configuration...", level="STEP")
        tb_reg = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband"
        exported_reg = export_registry_key(tb_reg, dest / "Taskband_Layout.reg")
        if exported_reg:
            log("Taskband registry layout exported successfully.", level="INFO")

        return {
            "pinned_count": copied,
            "names": names,
            "registry_exported": exported_reg,
            "summary": f"{copied} pinned icon(s) ({', '.join(names[:3])}{'...' if len(names) > 3 else ''})"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Shortcuts" / "Taskbar"
        if not dest.exists():
            log("No Taskbar pinned backup found.", level="WARN")
            return

        log("Restoring pinned taskbar shortcut icons...", level="STEP")
        appdata, _, _ = get_appdata_paths()
        target = appdata / "Microsoft" / "Internet Explorer" / "Quick Launch" / "User Pinned" / "TaskBar"
        target.mkdir(parents=True, exist_ok=True)

        copied = 0
        for item in dest.iterdir():
            if item.is_file() and not item.name.endswith(".reg"):
                try:
                    shutil.copy2(item, target / item.name)
                    copied += 1
                except Exception as exc:
                    report_permission_failure("restoring taskbar shortcut", item, exc, log)
                    pass
        log(f"Restored {copied} pinned taskbar shortcut icons.", level="SUCCESS")

        reg_file = dest / "Taskband_Layout.reg"
        if reg_file.exists():
            log("Importing Taskband layout registry configuration...", level="STEP")
            if import_registry_key(reg_file):
                log("Imported Taskband layout configuration into Windows Explorer.", level="SUCCESS")

        log("Tip: Restarting Windows Explorer (taskkill /f /im explorer.exe & start explorer.exe) refreshes taskbar pins immediately.", level="INFO")


class ModuleWiFi:
    ID = "wifi"
    NAME = "Wi-Fi Profiles & Saved Passwords"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Saved wireless network SSIDs, encryption settings, and security keys (WPA2/WPA3)"

    @staticmethod
    def detect():
        try:
            res = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, errors="ignore")
            profiles = []
            for line in res.stdout.splitlines():
                if ":" in line and ("All User Profile" in line or "Profile" in line):
                    p_name = line.split(":", 1)[1].strip()
                    if p_name:
                        profiles.append(p_name)
            if profiles:
                return True, f"{len(profiles)} network profile(s) found"
        except Exception:
            pass
        return False, "No Wi-Fi profiles found"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Network" / "WiFi"
        dest.mkdir(parents=True, exist_ok=True)
        log("Exporting Wi-Fi network profiles and keys via netsh wlan export...", level="STEP")
        try:
            res = subprocess.run(
                ["netsh", "wlan", "export", "profile", f"folder={str(dest)}", "key=clear"],
                capture_output=True,
                text=True,
                errors="ignore"
            )
            if res.returncode != 0:
                report_permission_failure("exporting Wi-Fi profiles", dest, f"{res.stdout}\n{res.stderr}", log)
            xml_files = list(dest.glob("*.xml"))
            names = [f.stem.replace("Wi-Fi-", "") for f in xml_files]
            log(f"Exported {len(xml_files)} Wi-Fi profile(s) ({', '.join(names[:4])}).", level="INFO")
            return {
                "count": len(xml_files),
                "profiles": names,
                "summary": f"{len(xml_files)} network(s) ({', '.join(names[:3])}{'...' if len(names) > 3 else ''})"
            }
        except Exception as e:
            log(f"Error exporting Wi-Fi profiles: {e}", level="ERROR")
            return {"count": 0, "summary": "0 networks exported"}

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "Network" / "WiFi"
        if not src.exists():
            log("No Wi-Fi backup data found.", level="WARN")
            return
        xml_files = list(src.glob("*.xml"))
        if not xml_files:
            log("No Wi-Fi XML profiles found in backup.", level="INFO")
            return
        log(f"Restoring {len(xml_files)} Wi-Fi profile(s)...", level="STEP")
        restored = 0
        for xf in xml_files:
            try:
                res = subprocess.run(
                    ["netsh", "wlan", "add", "profile", f"filename={str(xf)}", "user=all"],
                    capture_output=True,
                    text=True,
                    errors="ignore"
                )
                if res.returncode == 0:
                    restored += 1
                    log(f"Imported Wi-Fi profile: {xf.name}", level="INFO")
                else:
                    report_permission_failure("importing Wi-Fi profile", xf, f"{res.stdout}\n{res.stderr}", log)
            except Exception as e:
                log(f"Warning importing {xf.name}: {e}", level="WARN")
        log(f"Restored {restored} Wi-Fi network profiles successfully.", level="SUCCESS")


class ModuleExplorerPrefs:
    ID = "explorer_prefs"
    NAME = "File Explorer Preferences"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Folder view options (show hidden files, file extensions, compact view, launch folder, navigation pane)"

    @staticmethod
    def detect():
        return True, "Configured in Windows"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Explorer"
        dest.mkdir(parents=True, exist_ok=True)
        log("Reading File Explorer Advanced and CabinetState registry preferences...", level="STEP")
        adv_data = backup_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
        cab_data = backup_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState")
        combined = {
            "Advanced": adv_data,
            "CabinetState": cab_data
        }
        (dest / "explorer_settings.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
        hidden = adv_data.get("Hidden", {}).get("val", 2)
        hide_ext = adv_data.get("HideFileExt", {}).get("val", 1)
        launch_to = adv_data.get("LaunchTo", {}).get("val", 1)
        summary = f"Hidden={'Show' if hidden == 1 else 'Hide'}, Ext={'Show' if hide_ext == 0 else 'Hide'}, LaunchTo={'Home' if launch_to == 2 else 'This PC'}"
        log(f"Saved File Explorer settings: {summary}.", level="INFO")
        return {
            "summary": summary,
            "values": {"hidden": hidden, "hide_ext": hide_ext, "launch_to": launch_to}
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Explorer" / "explorer_settings.json"
        if not dest.exists():
            log("No Explorer preferences backup found.", level="WARN")
            return
        log("Restoring File Explorer preferences and folder options...", level="STEP")
        try:
            combined = json.loads(dest.read_text(encoding="utf-8"))
            if "Advanced" in combined:
                restore_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", combined["Advanced"])
            if "CabinetState" in combined:
                restore_registry_dict(r"Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState", combined["CabinetState"])
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.PostMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "ShellState")
            log("File Explorer preferences restored successfully.", level="SUCCESS")
        except Exception as e:
            log(f"Error restoring Explorer preferences: {e}", level="ERROR")


class ModuleSoundPrefs:
    ID = "sound_prefs"
    NAME = "Sound & Audio Settings"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Per-application volume mixer preferences, communications devices, and Windows sound schemes"

    @staticmethod
    def detect():
        num = reg_key_subkeys_count(r"Software\Microsoft\Internet Explorer\LowRegistry\Audio\PolicyConfig\PropertyStore")
        if num > 0:
            return True, f"{num} audio policy subkey(s) found"
        return True, "Configured in Windows"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Audio"
        dest.mkdir(parents=True, exist_ok=True)
        log("Exporting Audio PolicyConfig PropertyStore and sound schemes...", level="STEP")
        reg_policy = r"Software\Microsoft\Internet Explorer\LowRegistry\Audio\PolicyConfig\PropertyStore"
        exp1 = export_registry_key(reg_policy, dest / "Audio_PolicyConfig.reg")
        reg_schemes = r"AppEvents\Schemes"
        exp2 = export_registry_key(reg_schemes, dest / "Audio_Schemes.reg")
        log(f"Audio registry exported (PolicyConfig: {'Yes' if exp1 else 'No'}, Schemes: {'Yes' if exp2 else 'No'}).", level="INFO")
        return {
            "policy_exported": exp1,
            "schemes_exported": exp2,
            "summary": "Application volume policies and sound schemes saved"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Audio"
        if not dest.exists():
            log("No audio settings backup found.", level="WARN")
            return
        log("Restoring sound preferences and audio policies...", level="STEP")
        p1 = dest / "Audio_PolicyConfig.reg"
        if p1.exists():
            import_registry_key(p1)
        p2 = dest / "Audio_Schemes.reg"
        if p2.exists():
            import_registry_key(p2)
        log("Sound and audio settings restored.", level="SUCCESS")


class ModuleTerminalPS:
    ID = "terminal_powershell"
    NAME = "Windows Terminal & PowerShell"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "Windows Terminal profiles, color schemes, keybindings (settings.json), and PowerShell user profile scripts"

    @staticmethod
    def detect():
        _, localappdata, userprofile = get_appdata_paths()
        wt_stable = localappdata / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json"
        wt_preview = localappdata / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json"
        ps_prof = userprofile / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
        wps_prof = userprofile / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
        
        has_wt = wt_stable.exists() or wt_preview.exists()
        has_ps = ps_prof.exists() or wps_prof.exists() or (userprofile / "Documents" / "PowerShell").exists()
        if has_wt or has_ps:
            msg = []
            if has_wt:
                msg.append("Windows Terminal")
            if has_ps:
                msg.append("PowerShell profile(s)")
            return True, f"{' & '.join(msg)} found"
        return False, "Not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "Terminal_PowerShell"
        dest.mkdir(parents=True, exist_ok=True)
        _, localappdata, userprofile = get_appdata_paths()
        
        items_backed = []
        for tag, pkg in [
            ("Stable", "Microsoft.WindowsTerminal_8wekyb3d8bbwe"),
            ("Preview", "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe")
        ]:
            wt_set = localappdata / "Packages" / pkg / "LocalState" / "settings.json"
            if wt_set.exists():
                t_dest = dest / f"Terminal_{tag}"
                t_dest.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(wt_set, t_dest / "settings.json")
                    items_backed.append(f"Terminal ({tag})")
                    log(f"Backed up Windows Terminal ({tag}) settings.json.", level="INFO")
                except Exception as e:
                    log(f"Warning backing up Windows Terminal ({tag}): {e}", level="WARN")

        for ps_dir_name in ["PowerShell", "WindowsPowerShell"]:
            src_ps = userprofile / "Documents" / ps_dir_name
            if src_ps.exists() and any(src_ps.iterdir()):
                target_ps = dest / ps_dir_name
                target_ps.mkdir(parents=True, exist_ok=True)
                copied, _ = copy_folder_filtered(src_ps, target_ps, log_cb=log)
                items_backed.append(f"{ps_dir_name} ({copied} files)")
                log(f"Backed up {copied} {ps_dir_name} files/profiles.", level="INFO")

        summary = ", ".join(items_backed) if items_backed else "No terminal/PowerShell files found"
        return {
            "items": items_backed,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "DevTools" / "Terminal_PowerShell"
        if not src.exists():
            log("No Terminal/PowerShell backup data found.", level="WARN")
            return
        _, localappdata, userprofile = get_appdata_paths()

        for tag, pkg in [
            ("Stable", "Microsoft.WindowsTerminal_8wekyb3d8bbwe"),
            ("Preview", "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe")
        ]:
            bk_set = src / f"Terminal_{tag}" / "settings.json"
            if bk_set.exists():
                target_dir = localappdata / "Packages" / pkg / "LocalState"
                target_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(bk_set, target_dir / "settings.json")
                    log(f"Restored Windows Terminal ({tag}) settings.json.", level="SUCCESS")
                except Exception as e:
                    log(f"Warning restoring Windows Terminal ({tag}): {e}", level="WARN")

        for ps_dir_name in ["PowerShell", "WindowsPowerShell"]:
            ps_bk = src / ps_dir_name
            if ps_bk.exists():
                target_ps = userprofile / "Documents" / ps_dir_name
                target_ps.mkdir(parents=True, exist_ok=True)
                copied, _ = copy_folder_filtered(ps_bk, target_ps, log_cb=log)
                log(f"Restored {copied} {ps_dir_name} profile files.", level="SUCCESS")


class ModuleCredentials:
    ID = "credentials"
    NAME = "Windows Credentials & Vault"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Generic Windows credentials, network share logins, and Vault store files"

    @staticmethod
    def detect():
        appdata, localappdata, _ = get_appdata_paths()
        loc_cred = localappdata / "Microsoft" / "Credentials"
        roam_cred = appdata / "Microsoft" / "Credentials"
        roam_vault = appdata / "Microsoft" / "Vault"

        count = 0
        for p in [loc_cred, roam_cred, roam_vault]:
            if p.exists():
                count += len([f for f in p.iterdir() if f.is_file()])
        if count > 0:
            return True, f"{count} credential store file(s) found"
        return False, "No stored credentials"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Security" / "Credentials"
        dest.mkdir(parents=True, exist_ok=True)
        appdata, localappdata, _ = get_appdata_paths()

        log("Backing up Windows generic credentials and vault stores...", level="STEP")
        c1, _ = copy_folder_filtered(localappdata / "Microsoft" / "Credentials", dest / "Local_Credentials", log_cb=log)
        c2, _ = copy_folder_filtered(appdata / "Microsoft" / "Credentials", dest / "Roaming_Credentials", log_cb=log)
        c3, _ = copy_folder_filtered(appdata / "Microsoft" / "Vault", dest / "Roaming_Vault", log_cb=log)

        total = c1 + c2 + c3
        log(f"Backed up {total} credential store files.", level="INFO")
        return {
            "total_files": total,
            "summary": f"{total} credential store file(s)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "Security" / "Credentials"
        if not src.exists():
            log("No Credentials backup data found.", level="WARN")
            return
        appdata, localappdata, _ = get_appdata_paths()

        log("Restoring Windows credentials and vault stores...", level="STEP")
        if (src / "Local_Credentials").exists():
            t = localappdata / "Microsoft" / "Credentials"
            t.mkdir(parents=True, exist_ok=True)
            copy_folder_filtered(src / "Local_Credentials", t, log_cb=log)

        if (src / "Roaming_Credentials").exists():
            t = appdata / "Microsoft" / "Credentials"
            t.mkdir(parents=True, exist_ok=True)
            copy_folder_filtered(src / "Roaming_Credentials", t, log_cb=log)

        if (src / "Roaming_Vault").exists():
            t = appdata / "Microsoft" / "Vault"
            t.mkdir(parents=True, exist_ok=True)
            copy_folder_filtered(src / "Roaming_Vault", t, log_cb=log)

        log("Windows credentials restored.", level="SUCCESS")


class ModuleUserFonts:
    ID = "user_fonts"
    NAME = "User Custom Fonts"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Custom fonts installed for current user and font registry registrations"

    @staticmethod
    def detect():
        _, localappdata, _ = get_appdata_paths()
        fonts_dir = localappdata / "Microsoft" / "Windows" / "Fonts"
        if fonts_dir.exists():
            font_files = [f for f in fonts_dir.iterdir() if f.is_file() and f.suffix.lower() in [".ttf", ".otf", ".fon", ".ttc"]]
            if font_files:
                return True, f"{len(font_files)} custom font(s) found"
        return False, "No user fonts installed"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "Fonts"
        dest.mkdir(parents=True, exist_ok=True)
        _, localappdata, _ = get_appdata_paths()
        fonts_dir = localappdata / "Microsoft" / "Windows" / "Fonts"

        log("Backing up user-installed custom fonts and registry registrations...", level="STEP")
        copied = 0
        names = []
        if fonts_dir.exists():
            for f in fonts_dir.iterdir():
                if f.is_file():
                    try:
                        shutil.copy2(f, dest / f.name)
                        copied += 1
                        names.append(f.name)
                    except Exception as exc:
                        report_permission_failure("copying user font", f, exc, log)
                        pass

        reg_data = backup_registry_dict(r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
        (dest / "fonts_registry.json").write_text(json.dumps(reg_data, indent=2), encoding="utf-8")

        log(f"Backed up {copied} custom font file(s).", level="INFO")
        return {
            "font_count": copied,
            "fonts": names,
            "summary": f"{copied} font(s) ({', '.join(names[:3])}{'...' if len(names) > 3 else ''})" if copied else "0 fonts"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "Fonts"
        if not dest.exists():
            log("No fonts backup found.", level="WARN")
            return
        _, localappdata, _ = get_appdata_paths()
        target_dir = localappdata / "Microsoft" / "Windows" / "Fonts"
        target_dir.mkdir(parents=True, exist_ok=True)

        log("Restoring user custom fonts...", level="STEP")
        copied = 0
        for f in dest.iterdir():
            if f.is_file() and f.suffix != ".json":
                try:
                    target_file = target_dir / f.name
                    shutil.copy2(f, target_file)
                    try:
                        ctypes.windll.gdi32.AddFontResourceW(str(target_file))
                    except Exception:
                        pass
                    copied += 1
                except Exception as exc:
                    report_permission_failure("restoring user font", f, exc, log)
                    pass

        reg_json = dest / "fonts_registry.json"
        if reg_json.exists():
            try:
                data = json.loads(reg_json.read_text(encoding="utf-8"))
                restore_registry_dict(r"Software\Microsoft\Windows NT\CurrentVersion\Fonts", data)
            except Exception:
                pass

        HWND_BROADCAST = 0xFFFF
        WM_FONTCHANGE = 0x001D
        ctypes.windll.user32.PostMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
        log(f"Restored {copied} custom font(s) and notified Windows.", level="SUCCESS")


class ModuleGitSSH:
    ID = "git_ssh"
    NAME = "Git & SSH Configurations"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "Git global configuration (.gitconfig, .gitignore_global) and SSH keys & host configuration (.ssh)"

    @staticmethod
    def detect():
        _, _, userprofile = get_appdata_paths()
        has_git = (userprofile / ".gitconfig").exists()
        ssh_dir = userprofile / ".ssh"
        has_ssh = ssh_dir.exists() and any(ssh_dir.iterdir())
        if has_git or has_ssh:
            parts = []
            if has_git:
                parts.append(".gitconfig")
            if has_ssh:
                parts.append(".ssh")
            return True, f"{' & '.join(parts)} found"
        return False, "Not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "Git_SSH"
        dest.mkdir(parents=True, exist_ok=True)
        _, _, userprofile = get_appdata_paths()

        log("Backing up Git and SSH user configurations...", level="STEP")
        items_backed = []

        for g_file in [".gitconfig", ".gitignore_global"]:
            src_f = userprofile / g_file
            if src_f.exists():
                try:
                    shutil.copy2(src_f, dest / g_file)
                    items_backed.append(g_file)
                    log(f"Saved {g_file}.", level="INFO")
                except Exception as e:
                    log(f"Warning saving {g_file}: {e}", level="WARN")

        ssh_dir = userprofile / ".ssh"
        if ssh_dir.exists() and any(ssh_dir.iterdir()):
            target_ssh = dest / ".ssh"
            target_ssh.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(ssh_dir, target_ssh, log_cb=log)
            items_backed.append(f".ssh ({copied} files)")
            log(f"Backed up .ssh folder ({copied} keys/configs).", level="INFO")

        summary = ", ".join(items_backed) if items_backed else "No Git/SSH files found"
        return {
            "items": items_backed,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "DevTools" / "Git_SSH"
        if not src.exists():
            log("No Git/SSH backup data found.", level="WARN")
            return
        _, _, userprofile = get_appdata_paths()

        log("Restoring Git and SSH configurations...", level="STEP")
        for g_file in [".gitconfig", ".gitignore_global"]:
            bk_f = src / g_file
            if bk_f.exists():
                try:
                    shutil.copy2(bk_f, userprofile / g_file)
                    log(f"Restored {g_file}.", level="SUCCESS")
                except Exception as e:
                    log(f"Warning restoring {g_file}: {e}", level="WARN")

        ssh_bk = src / ".ssh"
        if ssh_bk.exists():
            target_ssh = userprofile / ".ssh"
            target_ssh.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(ssh_bk, target_ssh, log_cb=log)
            log(f"Restored .ssh configuration and keys ({copied} files).", level="SUCCESS")


class ModuleRDP:
    ID = "rdp_connections"
    NAME = "Remote Desktop (RDP) Connections"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "Remote Desktop (MSTSC) saved servers, MRU history, and Default.rdp connection file"

    @staticmethod
    def detect():
        _, _, userprofile = get_appdata_paths()
        has_file = (userprofile / "Documents" / "Default.rdp").exists()
        server_count = reg_key_subkeys_count(r"Software\Microsoft\Terminal Server Client\Servers")

        if has_file or server_count > 0:
            return True, f"{server_count} server(s) & Default.rdp found"
        return False, "No RDP history"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "RDP"
        dest.mkdir(parents=True, exist_ok=True)
        _, _, userprofile = get_appdata_paths()

        log("Backing up Remote Desktop history and Default.rdp...", level="STEP")
        def_rdp = userprofile / "Documents" / "Default.rdp"
        copied_file = False
        if def_rdp.exists():
            try:
                shutil.copy2(def_rdp, dest / "Default.rdp")
                copied_file = True
                log("Backed up Default.rdp.", level="INFO")
            except Exception as e:
                log(f"Warning copying Default.rdp: {e}", level="WARN")

        reg_path = r"Software\Microsoft\Terminal Server Client"
        exp_reg = export_registry_key(reg_path, dest / "RDP_Registry.reg")
        log(f"Exported RDP registry servers: {'Yes' if exp_reg else 'No'}.", level="INFO")

        return {
            "has_default_rdp": copied_file,
            "registry_exported": exp_reg,
            "summary": f"Default.rdp: {'Yes' if copied_file else 'No'}, Registry: {'Yes' if exp_reg else 'No'}"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "DevTools" / "RDP"
        if not dest.exists():
            log("No RDP backup data found.", level="WARN")
            return
        _, _, userprofile = get_appdata_paths()

        log("Restoring Remote Desktop connections...", level="STEP")
        bk_rdp = dest / "Default.rdp"
        if bk_rdp.exists():
            docs = userprofile / "Documents"
            docs.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(bk_rdp, docs / "Default.rdp")
                log("Restored Default.rdp.", level="SUCCESS")
            except Exception as e:
                log(f"Warning restoring Default.rdp: {e}", level="WARN")

        reg_file = dest / "RDP_Registry.reg"
        if reg_file.exists():
            if import_registry_key(reg_file):
                log("Imported Remote Desktop server configurations and MRU into registry.", level="SUCCESS")


class ModuleSSHAndFTP:
    ID = "ssh_ftp_clients"
    NAME = "PuTTY, WinSCP & FileZilla"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "PuTTY saved sessions & host keys, WinSCP stored sites, and FileZilla site manager"

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        found = []
        if reg_key_subkeys_count(r"Software\SimonTatham\PuTTY\Sessions") > 0:
            found.append("PuTTY")

        if reg_key_subkeys_count(r"Software\Martin Prikryl\WinSCP 2\Sessions") > 0:
            found.append("WinSCP")
        elif (appdata / "WinSCP.ini").exists():
            found.append("WinSCP")

        if (appdata / "FileZilla" / "sitemanager.xml").exists():
            found.append("FileZilla")

        if found:
            return True, f"{', '.join(found)} session(s) found"
        return False, "Not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "SSH_FTP_Clients"
        dest.mkdir(parents=True, exist_ok=True)
        appdata, _, _ = get_appdata_paths()

        log("Backing up PuTTY, WinSCP, and FileZilla sessions...", level="STEP")
        items = []

        putty_reg = r"Software\SimonTatham"
        if export_registry_key(putty_reg, dest / "PuTTY.reg"):
            items.append("PuTTY")
            log("Exported PuTTY registry sessions & host keys.", level="INFO")

        winscp_reg = r"Software\Martin Prikryl\WinSCP 2"
        if export_registry_key(winscp_reg, dest / "WinSCP.reg"):
            items.append("WinSCP")
            log("Exported WinSCP registry sessions.", level="INFO")
        winscp_ini = appdata / "WinSCP.ini"
        if winscp_ini.exists():
            try:
                shutil.copy2(winscp_ini, dest / "WinSCP.ini")
                items.append("WinSCP.ini")
            except Exception as exc:
                report_permission_failure("copying WinSCP configuration", winscp_ini, exc, log)
                pass

        fz_dir = appdata / "FileZilla"
        if fz_dir.exists():
            target_fz = dest / "FileZilla"
            target_fz.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(fz_dir, target_fz, log_cb=log)
            if copied > 0:
                items.append("FileZilla")
                log(f"Backed up FileZilla configuration & site manager ({copied} files).", level="INFO")

        summary = ", ".join(items) if items else "No client configurations found"
        return {
            "clients": items,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "DevTools" / "SSH_FTP_Clients"
        if not dest.exists():
            log("No SSH/FTP client backup found.", level="WARN")
            return
        appdata, _, _ = get_appdata_paths()

        log("Restoring PuTTY, WinSCP, and FileZilla sessions...", level="STEP")
        if (dest / "PuTTY.reg").exists():
            import_registry_key(dest / "PuTTY.reg")
            log("Restored PuTTY sessions & host keys.", level="SUCCESS")

        if (dest / "WinSCP.reg").exists():
            import_registry_key(dest / "WinSCP.reg")
            log("Restored WinSCP registry configurations.", level="SUCCESS")

        if (dest / "WinSCP.ini").exists():
            try:
                shutil.copy2(dest / "WinSCP.ini", appdata / "WinSCP.ini")
            except Exception as exc:
                report_permission_failure("restoring WinSCP configuration", dest / "WinSCP.ini", exc, log)
                pass

        if (dest / "FileZilla").exists():
            target_fz = appdata / "FileZilla"
            target_fz.mkdir(parents=True, exist_ok=True)
            copied, _ = copy_folder_filtered(dest / "FileZilla", target_fz, log_cb=log)
            log(f"Restored FileZilla site manager and configs ({copied} files).", level="SUCCESS")


class ModuleNotepadPlusPlus:
    ID = "notepad_plus_plus"
    NAME = "Notepad++ Settings & Sessions"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "Notepad++ configurations (config.xml), custom macros & shortcuts (shortcuts.xml), and active tab session (session.xml)"
    PROCESSES = ["notepad++.exe"]

    @staticmethod
    def detect():
        appdata, _, _ = get_appdata_paths()
        npp_dir = appdata / "Notepad++"
        if npp_dir.exists() and (npp_dir / "config.xml").exists():
            return True, "Notepad++ configurations & session found"
        return False, "Not installed / not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "Notepad++"
        dest.mkdir(parents=True, exist_ok=True)
        appdata, _, _ = get_appdata_paths()
        npp_dir = appdata / "Notepad++"

        if not npp_dir.exists():
            log("Notepad++ configuration directory not found.", level="WARN")
            return {"status": "not_found", "summary": "Not found"}

        log("Backing up Notepad++ settings, shortcuts, macros, and tab session...", level="STEP")
        copied, _ = copy_folder_filtered(npp_dir, dest, log_cb=log)
        log(f"Backed up {copied} Notepad++ configuration files.", level="INFO")

        has_session = (dest / "session.xml").exists()
        has_shortcuts = (dest / "shortcuts.xml").exists()
        summary = f"{copied} file(s) (Session: {'Yes' if has_session else 'No'}, Macros: {'Yes' if has_shortcuts else 'No'})"
        return {
            "files_count": copied,
            "has_session": has_session,
            "has_shortcuts": has_shortcuts,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "DevTools" / "Notepad++"
        if not src.exists():
            log("No Notepad++ backup data found.", level="WARN")
            return

        if is_process_running(ModuleNotepadPlusPlus.PROCESSES):
            terminate_processes(ModuleNotepadPlusPlus.PROCESSES, log_fn=log)

        appdata, _, _ = get_appdata_paths()
        target = appdata / "Notepad++"
        target.mkdir(parents=True, exist_ok=True)

        log("Restoring Notepad++ settings, custom macros, and active session...", level="STEP")
        copied, _ = copy_folder_filtered(src, target, log_cb=log)
        log(f"Notepad++ restored successfully ({copied} files).", level="SUCCESS")


class ModuleDriveMappings:
    ID = "drive_mappings"
    NAME = "Network Drive Mappings"
    CATEGORY = MigrationCategory.CAT_WINDOWS
    DESCRIPTION = "Persistent mapped network share drives (e.g. Z:, Y:) and remote UNC paths"

    @staticmethod
    def detect():
        count = reg_key_subkeys_count(r"Network")
        if count > 0:
            return True, f"{count} mapped drive(s) found"
        return False, "No mapped drives"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "Windows" / "NetworkDrives"
        dest.mkdir(parents=True, exist_ok=True)

        log("Exporting persistent network drive mappings from HKCU\\Network...", level="STEP")
        exp_reg = export_registry_key(r"Network", dest / "NetworkDrives.reg")

        mappings = []
        if reg_key_exists(r"Network"):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Network") as k:
                    num_subkeys = winreg.QueryInfoKey(k)[0]
                    for i in range(num_subkeys):
                        dr_letter = winreg.EnumKey(k, i)
                        try:
                            with winreg.OpenKey(k, dr_letter) as sk:
                                rpath = winreg.QueryValueEx(sk, "RemotePath")[0]
                                mappings.append({"drive": f"{dr_letter.upper()}:", "remote_path": rpath})
                        except Exception:
                            pass
            except Exception:
                pass

        (dest / "drive_mappings.json").write_text(json.dumps(mappings, indent=2), encoding="utf-8")
        mapping_desc = [f"{m['drive']} -> {m['remote_path']}" for m in mappings]
        log(f"Backed up {len(mappings)} drive mapping(s): {', '.join(mapping_desc[:3])}.", level="INFO")
        return {
            "count": len(mappings),
            "mappings": mappings,
            "registry_exported": exp_reg,
            "summary": f"{len(mappings)} drive(s) ({', '.join([m['drive'] for m in mappings])})" if mappings else "0 mappings"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        dest = src_dir / "Windows" / "NetworkDrives"
        if not dest.exists():
            log("No drive mappings backup found in archive.", level="WARN")
            return

        log("Restoring persistent network drive mappings...", level="STEP")
        reg_file = dest / "NetworkDrives.reg"
        if reg_file.exists():
            import_registry_key(reg_file)

        json_file = dest / "drive_mappings.json"
        if json_file.exists():
            try:
                mappings = json.loads(json_file.read_text(encoding="utf-8"))
                for m in mappings:
                    dr = m.get("drive")
                    rp = m.get("remote_path")
                    if dr and rp:
                        try:
                            result = subprocess.run(
                                ["net", "use", dr, rp, "/persistent:yes"],
                                capture_output=True,
                                text=True,
                                errors="ignore",
                                timeout=4
                            )
                            if result.returncode != 0:
                                report_permission_failure("restoring network drive mapping", dr, f"{result.stdout}\n{result.stderr}", log)
                        except Exception as exc:
                            report_permission_failure("restoring network drive mapping", dr, exc, log)
            except Exception:
                pass
        log("Network drive mappings restored.", level="SUCCESS")


class ModuleVSCode:
    ID = "vscode"
    NAME = "Visual Studio Code"
    CATEGORY = MigrationCategory.CAT_DEV_TOOLS
    DESCRIPTION = "Settings (settings.json), custom keybindings, snippets, UI state, and installed extensions (code projects excluded)"
    PROCESSES = ["code.exe"]

    @staticmethod
    def detect():
        appdata, _, userprofile = get_appdata_paths()
        has_settings = (appdata / "Code" / "User" / "settings.json").exists()
        ext_dir = userprofile / ".vscode" / "extensions"
        has_ext = ext_dir.exists() and any(ext_dir.iterdir())
        if has_settings or has_ext:
            ext_count = len([x for x in ext_dir.iterdir() if x.is_dir()]) if ext_dir.exists() else 0
            return True, f"Settings & {ext_count} extension(s) found"
        return False, "Not configured"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "DevTools" / "VSCode"
        dest.mkdir(parents=True, exist_ok=True)
        appdata, _, userprofile = get_appdata_paths()

        log("Backing up Visual Studio Code user configuration (code projects excluded)...", level="STEP")
        code_user = appdata / "Code" / "User"
        user_dest = dest / "User"
        user_dest.mkdir(parents=True, exist_ok=True)

        user_files_copied = 0
        if code_user.exists():
            for conf_file in ["settings.json", "keybindings.json", "tasks.json", "locale.json"]:
                cfp = code_user / conf_file
                if cfp.exists():
                    safe_copy_file(cfp, user_dest / conf_file)
                    user_files_copied += 1

            snippets_dir = code_user / "snippets"
            if snippets_dir.exists():
                copy_folder_filtered(snippets_dir, user_dest / "snippets", log_cb=log)

            storage_file = code_user / "globalStorage" / "storage.json"
            if storage_file.exists():
                (user_dest / "globalStorage").mkdir(parents=True, exist_ok=True)
                safe_copy_file(storage_file, user_dest / "globalStorage" / "storage.json")

        log("Backing up VS Code installed extensions (code projects excluded)...", level="STEP")
        ext_dir = userprofile / ".vscode" / "extensions"
        ext_dest = dest / "extensions"
        ext_count = 0
        ext_files = 0
        if ext_dir.exists():
            ext_dest.mkdir(parents=True, exist_ok=True)
            ext_json = ext_dir / "extensions.json"
            if ext_json.exists():
                safe_copy_file(ext_json, ext_dest / "extensions.json")
            c_cnt, _ = copy_folder_filtered(ext_dir, ext_dest, exclude_patterns=[".git", ".tmp", "cache", "node_modules\\.cache"], log_cb=log)
            ext_files = c_cnt
            ext_count = len([x for x in ext_dir.iterdir() if x.is_dir()])
            log(f"Backed up {ext_count} VS Code extensions ({c_cnt} files).", level="INFO")

        summary = f"Settings saved, {ext_count} extension(s) ({ext_files} files)"
        return {
            "user_files": user_files_copied,
            "extensions_count": ext_count,
            "summary": summary
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "DevTools" / "VSCode"
        if not src.exists():
            log("No VS Code backup data found in archive.", level="WARN")
            return

        if is_process_running(ModuleVSCode.PROCESSES):
            terminate_processes(ModuleVSCode.PROCESSES, log_fn=log)

        appdata, _, userprofile = get_appdata_paths()
        target_user = appdata / "Code" / "User"
        target_user.mkdir(parents=True, exist_ok=True)

        log("Restoring Visual Studio Code settings, keybindings, and snippets...", level="STEP")
        if (src / "User").exists():
            copy_folder_filtered(src / "User", target_user, log_cb=log)

        if (src / "extensions").exists():
            target_ext = userprofile / ".vscode" / "extensions"
            target_ext.mkdir(parents=True, exist_ok=True)
            log("Restoring VS Code installed extensions...", level="STEP")
            copy_folder_filtered(src / "extensions", target_ext, log_cb=log)

        log("Visual Studio Code configuration and extensions restored successfully.", level="SUCCESS")


class ModuleDesktop:
    ID = "user_desktop"
    NAME = "Desktop Files & Icon Layout"
    CATEGORY = MigrationCategory.CAT_USER_DATA
    DESCRIPTION = "User Desktop files and shortcuts, plus Explorer desktop icon layout settings"

    @staticmethod
    def detect():
        desktop = get_user_folder("Desktop", "Desktop")
        count = len(list(desktop.iterdir())) if desktop.exists() else 0
        has_layout = reg_key_exists(r"Software\Microsoft\Windows\Shell\Bags\1\Desktop")
        if count or has_layout:
            return True, f"{count} desktop item(s)" + (", icon layout found" if has_layout else "")
        return False, "Empty or not found"

    @staticmethod
    def backup(dest_dir: Path, log):
        desktop = get_user_folder("Desktop", "Desktop")
        dest = dest_dir / "UserData" / "Desktop"
        dest.mkdir(parents=True, exist_ok=True)

        log(f"Backing up current user's Desktop files and shortcuts from {desktop}...", level="STEP")
        copied, bytes_count = copy_folder_filtered(
            desktop, dest / "Files",
            exclude_patterns=["cache", ".tmp", ".lock", ".ost"],
            log_cb=log
        )
        mb = round(bytes_count / (1024 * 1024), 1)

        layout_keys = [
            r"Software\Microsoft\Windows\Shell\Bags\1\Desktop",
            r"Software\Microsoft\Windows\Shell\BagMRU"
        ]
        exported = []
        for index, key_path in enumerate(layout_keys, 1):
            if reg_key_exists(key_path):
                reg_file = dest / f"desktop_layout_{index}.reg"
                if export_registry_key(key_path, reg_file):
                    exported.append(reg_file.name)

        log(f"Backed up {copied} Desktop files/shortcuts ({mb} MB) and {len(exported)} icon-layout registry key(s).", level="INFO")
        return {
            "files_count": copied,
            "size_mb": mb,
            "layout_keys": exported,
            "summary": f"{copied} files ({mb} MB), {len(exported)} icon layout key(s)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "UserData" / "Desktop"
        if not src.exists():
            log("No Desktop backup found.", level="WARN")
            return

        desktop = get_user_folder("Desktop", "Desktop")
        desktop.mkdir(parents=True, exist_ok=True)
        files_dir = src / "Files"
        if files_dir.exists():
            log(f"Restoring Desktop files and shortcuts to {desktop}...", level="STEP")
            copied, _ = copy_folder_filtered(files_dir, desktop, log_cb=log)
            log(f"Restored {copied} Desktop files/shortcuts.", level="SUCCESS")

        for reg_file in sorted(src.glob("desktop_layout_*.reg")):
            if import_registry_key(reg_file):
                log(f"Restored desktop icon layout settings from {reg_file.name}.", level="SUCCESS")


class ModuleDownloads:
    ID = "user_downloads"
    NAME = "User Downloads Folder"
    CATEGORY = MigrationCategory.CAT_USER_DATA
    DESCRIPTION = "Files and folders in the current user's Downloads known folder"

    @staticmethod
    def detect():
        downloads = get_user_folder("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads")
        if downloads.exists() and any(downloads.iterdir()):
            return True, f"{len(list(downloads.iterdir()))} item(s) in Downloads"
        return False, "Empty or not found"

    @staticmethod
    def backup(dest_dir: Path, log):
        downloads = get_user_folder("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads")
        dest = dest_dir / "UserData" / "Downloads"
        dest.mkdir(parents=True, exist_ok=True)

        log(f"Backing up current user's Downloads folder from {downloads}...", level="STEP")
        copied, bytes_count = copy_folder_filtered(
            downloads, dest,
            exclude_patterns=["cache", ".tmp", ".lock", ".ost"],
            log_cb=log
        )
        mb = round(bytes_count / (1024 * 1024), 1)
        log(f"Backed up {copied} Downloads files ({mb} MB).", level="INFO")
        return {"copied_files": copied, "size_mb": mb, "summary": f"{copied} files ({mb} MB)"}

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "UserData" / "Downloads"
        if not src.exists():
            log("No Downloads backup found.", level="WARN")
            return

        downloads = get_user_folder("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads")
        downloads.mkdir(parents=True, exist_ok=True)
        log(f"Restoring Downloads to {downloads}...", level="STEP")
        copied, _ = copy_folder_filtered(src, downloads, log_cb=log)
        log(f"Restored {copied} Downloads files.", level="SUCCESS")


class ModuleDocuments:
    ID = "user_documents"
    NAME = "User Documents Folder"
    CATEGORY = MigrationCategory.CAT_USER_DATA
    DESCRIPTION = "Files, folders, and personal documents stored in user's Documents directory (OSTs excluded)"

    @staticmethod
    def detect():
        _, _, userprofile = get_appdata_paths()
        docs = userprofile / "Documents"
        if docs.exists() and any(docs.iterdir()):
            count = len(list(docs.iterdir()))
            return True, f"{count} item(s) in Documents"
        return False, "Empty or not found"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "UserData" / "Documents"
        dest.mkdir(parents=True, exist_ok=True)
        _, _, userprofile = get_appdata_paths()
        src = userprofile / "Documents"

        log("Backing up User Documents folder (skipping .ost caches)...", level="STEP")
        copied, bytes_cnt = copy_folder_filtered(
            src, dest,
            exclude_patterns=["cache", ".tmp", ".lock", ".ost"],
            log_cb=log
        )
        mb = round(bytes_cnt / (1024 * 1024), 1)
        log(f"Backed up {copied} document file(s) ({mb} MB).", level="INFO")
        return {
            "copied_files": copied,
            "size_mb": mb,
            "summary": f"{copied} file(s) ({mb} MB)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "UserData" / "Documents"
        if not src.exists():
            log("No Documents backup found in archive.", level="WARN")
            return
        _, _, userprofile = get_appdata_paths()
        target = userprofile / "Documents"
        target.mkdir(parents=True, exist_ok=True)
        log("Restoring User Documents folder...", level="STEP")
        copied, _ = copy_folder_filtered(src, target, log_cb=log)
        log(f"Restored {copied} document files to {target}.", level="SUCCESS")


class ModulePictures:
    ID = "user_pictures"
    NAME = "User Pictures Folder"
    CATEGORY = MigrationCategory.CAT_USER_DATA
    DESCRIPTION = "Photos, images, and folders stored in user's Pictures directory"

    @staticmethod
    def detect():
        _, _, userprofile = get_appdata_paths()
        pics = userprofile / "Pictures"
        if pics.exists() and any(pics.iterdir()):
            count = len(list(pics.iterdir()))
            return True, f"{count} item(s) in Pictures"
        return False, "Empty or not found"

    @staticmethod
    def backup(dest_dir: Path, log):
        dest = dest_dir / "UserData" / "Pictures"
        dest.mkdir(parents=True, exist_ok=True)
        _, _, userprofile = get_appdata_paths()
        src = userprofile / "Pictures"

        log("Backing up User Pictures folder...", level="STEP")
        copied, bytes_cnt = copy_folder_filtered(
            src, dest,
            exclude_patterns=["cache", ".tmp", ".lock"],
            log_cb=log
        )
        mb = round(bytes_cnt / (1024 * 1024), 1)
        log(f"Backed up {copied} picture file(s) ({mb} MB).", level="INFO")
        return {
            "copied_files": copied,
            "size_mb": mb,
            "summary": f"{copied} file(s) ({mb} MB)"
        }

    @staticmethod
    def restore(src_dir: Path, log):
        src = src_dir / "UserData" / "Pictures"
        if not src.exists():
            log("No Pictures backup found in archive.", level="WARN")
            return
        _, _, userprofile = get_appdata_paths()
        target = userprofile / "Pictures"
        target.mkdir(parents=True, exist_ok=True)
        log("Restoring User Pictures folder...", level="STEP")
        copied, _ = copy_folder_filtered(src, target, log_cb=log)
        log(f"Restored {copied} picture files to {target}.", level="SUCCESS")


# Register all migration modules
MODULES = [
    ModuleEdge,
    ModuleChrome,
    ModuleFirefox,
    ModuleWallpaper,
    ModuleMouse,
    ModuleKeyboard,
    ModuleThemes,
    ModuleWiFi,
    ModuleExplorerPrefs,
    ModuleSoundPrefs,
    ModuleDriveMappings,
    ModuleCredentials,
    ModuleUserFonts,
    ModuleOutlook,
    ModuleQuickLaunch,
    ModuleTaskbar,
    ModuleDesktop,
    ModuleDocuments,
    ModulePictures,
    ModuleDownloads,
    ModuleVSCode,
    ModuleTerminalPS,
    ModuleGitSSH,
    ModuleRDP,
    ModuleSSHAndFTP,
    ModuleNotepadPlusPlus,
]

MODULE_MAP = {m.ID: m for m in MODULES}


# ==============================================================================
# Modern Sleek Dark GUI
# ==============================================================================

class ModernMigratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_TITLE} {APP_VERSION}")
        self.root.geometry("1280x880")
        self.root.minsize(1080, 720)
        self.root.configure(bg=THEME["bg"])
        center_window(self.root)

        # Dedicated log file tracking
        self.current_log_file: Path | None = None
        self._init_session_log_file()

        # State Variables
        self.selected_backup_path = tk.StringVar(value="")
        self.backup_vars = {}        # module_id -> BooleanVar (Backup tab)
        self.restore_vars = {}       # module_id -> BooleanVar (Restore tab)
        self.restore_badges = {}     # module_id -> Label (Restore tab badges)
        self.restore_summaries = {}  # module_id -> Label (Restore tab settings details)
        self.status_text = tk.StringVar(value="Ready")
        self.encrypt_archive_var = tk.BooleanVar(value=True)
        self.backup_requires_password = False
        self.backup_filenames_encrypted = False
        self.backup_archive_loaded = False
        self.is_busy = False
        self.cancel_event = threading.Event()

        # Custom Folders State
        self.custom_folders = []         # list of {"path": Path, "var": BooleanVar}
        self.restored_custom_folders = [] # list of {"name": str, "archive_subpath": str, "original_path": str, "var": BooleanVar}
        self.custom_folders_cards_frame = None
        self.restore_custom_cards_frame = None

        # Live Progress Sub-Window state
        self.progress_win = None
        self.txt_win_log = None
        self.win_progress_bar = None
        self.progress_stop_button = None
        self.progress_title_var = tk.StringVar(value="Operation Progress")
        self.progress_step_var = tk.StringVar(value="Ready")
        self.flip_logo = None

        self._configure_styles()
        self._build_ui()
        self.log(f"{APP_TITLE} {APP_VERSION} initialized.", level="INFO")
        self.log(f"Session log file: {self.current_log_file}", level="INFO")

    def _init_session_log_file(self, prefix="session"):
        """Initialize a new disk log file for the session."""
        logs_dir = get_logs_dir()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = logs_dir / f"DeskFlip_{prefix}_{ts}.log"
        try:
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(f"=== {APP_TITLE} {APP_VERSION} Log Started at {datetime.now().isoformat()} ===\n")
                f.write(f"System: {platform.platform()} ({platform.architecture()[0]})\n")
                f.write(f"Host: {os.environ.get('COMPUTERNAME', 'Unknown')} | User: {os.environ.get('USERNAME', 'Unknown')}\n")
                f.write("=" * 70 + "\n\n")
        except Exception:
            pass

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=THEME["bg"], foreground=THEME["text"], font=("Segoe UI", 10))
        
        # Tabs - Selected tab is large and prominent; unselected tab is smaller
        style.configure(
            "TNotebook",
            background=THEME["bg"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0]
        )
        style.configure(
            "TNotebook.Tab",
            background=THEME["surface"],
            foreground=THEME["text_secondary"],
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            padding=[("selected", [36, 14]), ("!selected", [20, 8])],
            font=[("selected", ("Segoe UI", 11, "bold")), ("!selected", ("Segoe UI", 9))],
            background=[("selected", THEME["accent"]), ("active", THEME["surface_alt"])],
            foreground=[("selected", "#ffffff"), ("active", THEME["text"])]
        )

        # Progress bar
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=THEME["surface_alt"],
            background=THEME["accent"],
            borderwidth=0,
            thickness=6
        )

    def _build_ui(self):
        # Header Bar
        header = tk.Frame(self.root, bg=THEME["surface"], height=76, bd=0)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # Header Subtitle / Description (Logo serves as primary visual title)
        title_frame = tk.Frame(header, bg=THEME["surface"])
        title_frame.pack(side=tk.LEFT, padx=24, pady=26)

        subtitle_lbl = tk.Label(
            title_frame,
            text="Windows 11 Profile & App Migration Assistant",
            font=("Segoe UI", 10),
            fg=THEME["text_secondary"],
            bg=THEME["surface"]
        )
        subtitle_lbl.pack(anchor="w")

        # Top Right: embedded logo
        try:
            self.flip_logo = tk.PhotoImage(data=EMBEDDED_LOGO)
        except tk.TclError:
            self.flip_logo = None

        if self.flip_logo:
            logo_lbl = tk.Label(header, image=self.flip_logo, bg=THEME["surface"], bd=0)
            logo_lbl.pack(side=tk.RIGHT, padx=24, pady=14)

        about_button = tk.Button(
            header,
            text="About",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._show_about_window
        )
        about_button.pack(side=tk.RIGHT, padx=(0, 16), pady=20)

        # Status Bar (Docked at bottom first)
        status_bar = tk.Frame(self.root, bg=THEME["surface"], height=34)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        status_lbl = tk.Label(
            status_bar,
            textvariable=self.status_text,
            font=("Segoe UI", 9),
            fg=THEME["text_secondary"],
            bg=THEME["surface"]
        )
        status_lbl.pack(side=tk.LEFT, padx=16)

        btn_win_toggle = tk.Button(
            status_bar,
            text="📊 Progress Window",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["surface_alt"],
            fg=THEME["info"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self._show_progress_window
        )
        btn_win_toggle.pack(side=tk.RIGHT, padx=12, pady=3)

        self.btn_stop_job = tk.Button(
            status_bar,
            text="■ Stop Job",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["danger"],
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self._request_cancel
        )

        self.progress_bar = ttk.Progressbar(status_bar, mode="indeterminate", style="Horizontal.TProgressbar", length=160)

        # Activity Log Area (Persistent at bottom, right above status bar)
        self._build_log_area()

        # Notebook (Tabs - expanded to fill central region)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 10))

        self.tab_backup = tk.Frame(self.notebook, bg=THEME["bg"])
        self.tab_restore = tk.Frame(self.notebook, bg=THEME["bg"])

        self.notebook.add(self.tab_backup, text="  1. CREATE BACKUP  ")
        self.notebook.add(self.tab_restore, text="  2. IMPORT TO THIS PC  ")

        self._build_backup_tab()
        self._build_restore_tab()

    # --------------------------------------------------------------------------
    # Backup Tab UI
    # --------------------------------------------------------------------------
    def _show_about_window(self):
        window = tk.Toplevel(self.root)
        window.title(f"About {APP_TITLE}")
        window.geometry("900x700")
        window.minsize(640, 480)
        window.configure(bg=THEME["bg"])
        window.transient(self.root)
        center_window(window)

        readme_view = ScrolledText(
            window,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=THEME["log_bg"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            selectbackground=THEME["accent"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=16,
            pady=14
        )
        readme_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 8))
        readme_view.insert("1.0", EMBEDDED_README)
        readme_view.configure(state=tk.DISABLED)

        close_button = tk.Button(
            window,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#ffffff",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=window.destroy
        )
        close_button.pack(side=tk.RIGHT, padx=12, pady=(0, 12))

    def _build_backup_tab(self):
        parent = self.tab_backup

        top_bar = tk.Frame(parent, bg=THEME["bg"])
        top_bar.pack(fill=tk.X, pady=(10, 8))

        info_lbl = tk.Label(
            top_bar,
            text="Select items to package. DeskFlip will generate an archive and an export reference manifest.",
            font=("Segoe UI", 9),
            fg=THEME["text_secondary"],
            bg=THEME["bg"]
        )
        info_lbl.pack(side=tk.LEFT, anchor="w")

        btn_select_all = tk.Button(
            top_bar,
            text="Select All",
            font=("Segoe UI", 9),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._select_all_backup
        )
        btn_select_all.pack(side=tk.RIGHT, padx=(6, 0))

        btn_select_none = tk.Button(
            top_bar,
            text="Deselect All",
            font=("Segoe UI", 9),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._deselect_all_backup
        )
        btn_select_none.pack(side=tk.RIGHT)

        cards_frame = self._create_scrollable_card_area(parent)
        self._populate_backup_cards(cards_frame)

        action_bar = tk.Frame(parent, bg=THEME["bg"])
        action_bar.pack(fill=tk.X, pady=(12, 5))

        chk_encrypt = tk.Checkbutton(
            action_bar,
            text="Password-protect archive (AES-256)",
            variable=self.encrypt_archive_var,
            font=("Segoe UI", 9),
            fg=THEME["text"],
            bg=THEME["bg"],
            selectcolor=THEME["surface"],
            activebackground=THEME["bg"],
            activeforeground=THEME["text"],
            bd=0,
            cursor="hand2",
            command=self._on_encryption_toggle
        )
        chk_encrypt.pack(side=tk.LEFT, padx=8)

        self.btn_run_backup = tk.Button(
            action_bar,
            text="📦 CREATE BACKUP ARCHIVE & REFERENCE FILE",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["accent"],
            fg="#ffffff",
            activebackground=THEME["accent_hover"],
            activeforeground="#ffffff",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._start_backup_flow
        )
        self.btn_run_backup.pack(side=tk.RIGHT)

    def _populate_backup_cards(self, parent):
        categories = {}
        for mod in MODULES:
            categories.setdefault(mod.CATEGORY, []).append(mod)

        for cat_name, mods in categories.items():
            cat_hdr = tk.Label(
                parent,
                text=cat_name.upper(),
                font=("Segoe UI", 9, "bold"),
                fg=THEME["text_muted"],
                bg=THEME["bg"],
                anchor="w"
            )
            cat_hdr.pack(fill=tk.X, padx=4, pady=(12, 4))

            for mod in mods:
                detected, msg = mod.detect()
                var = tk.BooleanVar(value=detected)
                self.backup_vars[mod.ID] = var

                card = tk.Frame(parent, bg=THEME["card_bg"], bd=1, relief="solid")
                card.pack(fill=tk.X, padx=2, pady=4)

                chk = tk.Checkbutton(
                    card,
                    text=f" {mod.NAME}",
                    variable=var,
                    font=("Segoe UI", 10, "bold"),
                    fg=THEME["text"],
                    bg=THEME["card_bg"],
                    selectcolor=THEME["surface"],
                    activebackground=THEME["card_bg"],
                    activeforeground=THEME["text"],
                    bd=0,
                    cursor="hand2"
                )
                chk.pack(side=tk.LEFT, padx=12, pady=8)

                det_color = THEME["success"] if detected else THEME["text_muted"]
                det_lbl = tk.Label(
                    card,
                    text=f"● {msg}",
                    font=("Segoe UI", 8),
                    fg=det_color,
                    bg=THEME["card_bg"]
                )
                det_lbl.pack(side=tk.RIGHT, padx=16, pady=8)

                desc_frame = tk.Frame(card, bg=THEME["card_bg"])
                desc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

                desc_lbl = tk.Label(
                    desc_frame,
                    text=mod.DESCRIPTION,
                    font=("Segoe UI", 8),
                    fg=THEME["text_secondary"],
                    bg=THEME["card_bg"],
                    anchor="w",
                    justify=tk.LEFT
                )
                desc_lbl.pack(fill=tk.X, expand=True, anchor="w")

        # Custom Folders & Locations Section
        cf_hdr_bar = tk.Frame(parent, bg=THEME["bg"])
        cf_hdr_bar.pack(fill=tk.X, padx=4, pady=(20, 6))

        cf_hdr_lbl = tk.Label(
            cf_hdr_bar,
            text="CUSTOM FOLDERS & LOCATIONS",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["text_muted"],
            bg=THEME["bg"],
            anchor="w"
        )
        cf_hdr_lbl.pack(side=tk.LEFT)

        btn_add_custom = tk.Button(
            cf_hdr_bar,
            text="➕ Add Custom Folder...",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["accent"],
            fg="#ffffff",
            activebackground=THEME["accent_hover"],
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._on_add_custom_folder
        )
        btn_add_custom.pack(side=tk.RIGHT)

        self.custom_folders_cards_frame = tk.Frame(parent, bg=THEME["bg"])
        self.custom_folders_cards_frame.pack(fill=tk.X)
        self._refresh_custom_folders_cards()

    def _on_add_custom_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Include in Backup", parent=self.root)
        if not folder:
            return
        f_path = Path(folder)
        if any(item["path"] == f_path for item in self.custom_folders):
            messagebox.showinfo("Already Added", f"The folder '{f_path}' is already in your backup list.", parent=self.root)
            return
        var = tk.BooleanVar(value=True)
        self.custom_folders.append({"path": f_path, "var": var})
        self._refresh_custom_folders_cards()
        self.log(f"Added custom folder to backup list: {f_path}", level="INFO")

    def _remove_custom_folder(self, idx):
        if 0 <= idx < len(self.custom_folders):
            removed = self.custom_folders.pop(idx)
            self._refresh_custom_folders_cards()
            self.log(f"Removed custom folder: {removed['path']}", level="INFO")

    def _refresh_custom_folders_cards(self):
        if not self.custom_folders_cards_frame:
            return
        for w in self.custom_folders_cards_frame.winfo_children():
            w.destroy()

        if not self.custom_folders:
            empty_lbl = tk.Label(
                self.custom_folders_cards_frame,
                text="No custom folders added yet. Click '➕ Add Custom Folder...' above to include additional directories.",
                font=("Segoe UI", 8, "italic"),
                fg=THEME["text_muted"],
                bg=THEME["bg"],
                anchor="w"
            )
            empty_lbl.pack(fill=tk.X, padx=12, pady=6)
            return

        for idx, item in enumerate(self.custom_folders):
            f_path = item["path"]
            var = item["var"]

            card = tk.Frame(self.custom_folders_cards_frame, bg=THEME["card_bg"], bd=1, relief="solid")
            card.pack(fill=tk.X, padx=2, pady=4)

            chk = tk.Checkbutton(
                card,
                text=f" {f_path.name or str(f_path)}",
                variable=var,
                font=("Segoe UI", 10, "bold"),
                fg=THEME["text"],
                bg=THEME["card_bg"],
                selectcolor=THEME["surface"],
                activebackground=THEME["card_bg"],
                activeforeground=THEME["text"],
                bd=0,
                cursor="hand2"
            )
            chk.pack(side=tk.LEFT, padx=12, pady=8)

            btn_rem = tk.Button(
                card,
                text="❌ Remove",
                font=("Segoe UI", 8),
                bg=THEME["surface_alt"],
                fg=THEME["danger"],
                activebackground=THEME["card_bg"],
                activeforeground="#fff",
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda i=idx: self._remove_custom_folder(i)
            )
            btn_rem.pack(side=tk.RIGHT, padx=16, pady=8)

            path_lbl = tk.Label(
                card,
                text=str(f_path),
                font=("Segoe UI", 8),
                fg=THEME["text_secondary"],
                bg=THEME["card_bg"],
                anchor="w"
            )
            path_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

    # --------------------------------------------------------------------------
    # Restore Tab UI
    # --------------------------------------------------------------------------
    def _build_restore_tab(self):
        parent = self.tab_restore

        picker_frame = tk.Frame(parent, bg=THEME["surface"], bd=1, relief="solid")
        picker_frame.pack(fill=tk.X, pady=(10, 8), padx=2)

        lbl = tk.Label(
            picker_frame,
            text="Select Backup Package (.zip):",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["text"],
            bg=THEME["surface"]
        )
        lbl.pack(side=tk.LEFT, padx=14, pady=12)

        self.entry_backup = tk.Entry(
            picker_frame,
            textvariable=self.selected_backup_path,
            font=("Segoe UI", 9),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            insertbackground="#fff",
            bd=0,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"]
        )
        self.entry_backup.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=12, ipady=5)

        btn_browse = tk.Button(
            picker_frame,
            text="Browse...",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent"],
            fg="#fff",
            activebackground=THEME["accent_hover"],
            activeforeground="#fff",
            bd=0,
            padx=16,
            pady=5,
            cursor="hand2",
            command=self._browse_backup_file
        )
        btn_browse.pack(side=tk.RIGHT, padx=12, pady=12)

        # Meta Header Banner for Detected Settings
        self.meta_card = tk.Frame(parent, bg=THEME["surface_alt"], bd=1, relief="solid")
        self.meta_card.pack(fill=tk.X, pady=(0, 8), padx=2)

        self.lbl_origin_info = tk.Label(
            self.meta_card,
            text="No backup selected yet. Browse and open a backup .zip above to detect settings.",
            font=("Segoe UI", 9),
            fg=THEME["text_secondary"],
            bg=THEME["surface_alt"],
            padx=12,
            pady=8
        )
        self.lbl_origin_info.pack(side=tk.LEFT)

        btn_select_avail = tk.Button(
            self.meta_card,
            text="Select All Available",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["surface"],
            fg=THEME["info"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._select_all_available_restore
        )
        btn_select_avail.pack(side=tk.RIGHT, padx=(0, 10), pady=6)

        btn_desel_restore = tk.Button(
            self.meta_card,
            text="Deselect All",
            font=("Segoe UI", 8),
            bg=THEME["surface"],
            fg=THEME["text_muted"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._deselect_all_restore
        )
        btn_desel_restore.pack(side=tk.RIGHT, padx=6, pady=6)

        self.btn_extract_all = tk.Button(
            self.meta_card,
            text="Extract All...",
            font=("Segoe UI", 8),
            bg=THEME["surface"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._start_extract_all
        )

        # Scrollable Cards Canvas for restore items
        restore_cards_frame = self._create_scrollable_card_area(parent)
        self._populate_restore_cards(restore_cards_frame)

        action_bar = tk.Frame(parent, bg=THEME["bg"])
        action_bar.pack(fill=tk.X, pady=(12, 5))

        self.btn_run_restore = tk.Button(
            action_bar,
            text="🚀 IMPORT SELECTED ITEMS TO THIS PC",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["success"],
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._start_restore_flow
        )
        self.btn_run_restore.pack(side=tk.RIGHT)

    def _populate_restore_cards(self, parent):
        categories = {}
        for mod in MODULES:
            categories.setdefault(mod.CATEGORY, []).append(mod)

        for cat_name, mods in categories.items():
            cat_hdr = tk.Label(
                parent,
                text=cat_name.upper(),
                font=("Segoe UI", 9, "bold"),
                fg=THEME["text_muted"],
                bg=THEME["bg"],
                anchor="w"
            )
            cat_hdr.pack(fill=tk.X, padx=4, pady=(12, 4))

            for mod in mods:
                var = tk.BooleanVar(value=False)
                self.restore_vars[mod.ID] = var

                card = tk.Frame(parent, bg=THEME["card_bg"], bd=1, relief="solid")
                card.pack(fill=tk.X, padx=2, pady=4)

                chk = tk.Checkbutton(
                    card,
                    text=f" {mod.NAME}",
                    variable=var,
                    font=("Segoe UI", 10, "bold"),
                    fg=THEME["text"],
                    bg=THEME["card_bg"],
                    selectcolor=THEME["surface"],
                    activebackground=THEME["card_bg"],
                    activeforeground=THEME["text"],
                    bd=0,
                    cursor="hand2"
                )
                chk.pack(side=tk.LEFT, padx=12, pady=8)

                badge_lbl = tk.Label(
                    card,
                    text="○ Awaiting package",
                    font=("Segoe UI", 8),
                    fg=THEME["text_muted"],
                    bg=THEME["card_bg"]
                )
                badge_lbl.pack(side=tk.RIGHT, padx=16, pady=8)
                self.restore_badges[mod.ID] = badge_lbl

                desc_frame = tk.Frame(card, bg=THEME["card_bg"])
                desc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

                desc_lbl = tk.Label(
                    desc_frame,
                    text=mod.DESCRIPTION,
                    font=("Segoe UI", 8),
                    fg=THEME["text_secondary"],
                    bg=THEME["card_bg"],
                    anchor="w",
                    justify=tk.LEFT
                )
                desc_lbl.pack(fill=tk.X, expand=True, anchor="w")

                summary_lbl = tk.Label(
                    desc_frame,
                    text="Select backup file above to detect settings",
                    font=("Segoe UI", 8, "italic"),
                    fg=THEME["text_muted"],
                    bg=THEME["card_bg"],
                    anchor="w",
                    justify=tk.LEFT
                )
                summary_lbl.pack(fill=tk.X, expand=True, anchor="w", pady=(2, 0))
                self.restore_summaries[mod.ID] = summary_lbl

        # Custom Folders Container on Restore Tab
        self.restore_custom_cards_frame = tk.Frame(parent, bg=THEME["bg"])
        self.restore_custom_cards_frame.pack(fill=tk.X)
        self._refresh_restore_custom_cards()

    def _refresh_restore_custom_cards(self):
        if not self.restore_custom_cards_frame:
            return
        for w in self.restore_custom_cards_frame.winfo_children():
            w.destroy()

        if not self.restored_custom_folders:
            return

        cat_hdr = tk.Label(
            self.restore_custom_cards_frame,
            text="CUSTOM FOLDERS & LOCATIONS IN BACKUP",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["text_muted"],
            bg=THEME["bg"],
            anchor="w"
        )
        cat_hdr.pack(fill=tk.X, padx=4, pady=(20, 6))

        for item in self.restored_custom_folders:
            var = item["var"]
            c_name = item["name"]
            orig_p = item["original_path"]
            f_count = item.get("files_count", 0)
            f_mb = item.get("size_mb", 0)

            card = tk.Frame(self.restore_custom_cards_frame, bg=THEME["card_bg"], bd=1, relief="solid")
            card.pack(fill=tk.X, padx=2, pady=4)

            chk = tk.Checkbutton(
                card,
                text=f" {c_name}",
                variable=var,
                font=("Segoe UI", 10, "bold"),
                fg=THEME["text"],
                bg=THEME["card_bg"],
                selectcolor=THEME["surface"],
                activebackground=THEME["card_bg"],
                activeforeground=THEME["text"],
                bd=0,
                cursor="hand2"
            )
            chk.pack(side=tk.LEFT, padx=12, pady=8)

            badge_lbl = tk.Label(
                card,
                text="● In backup",
                font=("Segoe UI", 8),
                fg=THEME["success"],
                bg=THEME["card_bg"]
            )
            badge_lbl.pack(side=tk.RIGHT, padx=16, pady=8)

            desc_frame = tk.Frame(card, bg=THEME["card_bg"])
            desc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

            path_lbl = tk.Label(
                desc_frame,
                text=f"Original Location: {orig_p}  ({f_count} files, {f_mb} MB)",
                font=("Segoe UI", 8),
                fg=THEME["text_secondary"],
                bg=THEME["card_bg"],
                anchor="w",
                justify=tk.LEFT
            )
            path_lbl.pack(fill=tk.X, expand=True, anchor="w")

    def _create_scrollable_card_area(self, parent):
        container = tk.Frame(parent, bg=THEME["bg"])
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=THEME["bg"], bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME["bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_resize(event):
            canvas.itemconfig(frame_window, width=event.width)
            wrap_width = max(320, event.width - 480)
            for widget in scrollable_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    try:
                                        subchild.configure(wraplength=wrap_width)
                                    except Exception:
                                        pass

        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return scrollable_frame

    def _build_log_area(self):
        log_frame = tk.Frame(self.root, bg=THEME["log_bg"], height=160, bd=1, relief="solid")
        log_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        log_frame.pack_propagate(False)

        # Log Header Bar
        log_hdr = tk.Frame(log_frame, bg=THEME["surface_alt"], height=26)
        log_hdr.pack(fill=tk.X)

        hdr_lbl = tk.Label(
            log_hdr,
            text="ACTIVITY & STEP EXECUTION LOG",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["surface_alt"]
        )
        hdr_lbl.pack(side=tk.LEFT, padx=10, pady=3)

        btn_open_file = tk.Button(
            log_hdr,
            text="📄 Open Log File",
            font=("Segoe UI", 8),
            bg=THEME["surface"],
            fg=THEME["info"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=1,
            cursor="hand2",
            command=self._open_current_log_file
        )
        btn_open_file.pack(side=tk.RIGHT, padx=6, pady=2)

        btn_open_dir = tk.Button(
            log_hdr,
            text="📁 Logs Folder",
            font=("Segoe UI", 8),
            bg=THEME["surface"],
            fg=THEME["text_secondary"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=1,
            cursor="hand2",
            command=self._open_logs_dir
        )
        btn_open_dir.pack(side=tk.RIGHT, padx=4, pady=2)

        btn_clear = tk.Button(
            log_hdr,
            text="Clear",
            font=("Segoe UI", 8),
            bg=THEME["surface"],
            fg=THEME["text_muted"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self._clear_log
        )
        btn_clear.pack(side=tk.RIGHT, padx=4, pady=2)

        self.txt_log = tk.Text(
            log_frame,
            bg=THEME["log_bg"],
            fg="#e5e7eb",
            insertbackground="#fff",
            font=("Consolas", 9),
            bd=0,
            padx=10,
            pady=6,
            wrap=tk.WORD
        )
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.txt_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.config(yscrollcommand=scrollbar.set)
        self._setup_log_tags(self.txt_log)

    def _setup_log_tags(self, text_widget: tk.Text):
        """Configure color tags for log message levels."""
        text_widget.tag_configure("STEP", foreground=THEME["info"], font=("Consolas", 9, "bold"))
        text_widget.tag_configure("SUCCESS", foreground=THEME["success"], font=("Consolas", 9, "bold"))
        text_widget.tag_configure("START", foreground="#60a5fa", font=("Consolas", 9, "bold"))
        text_widget.tag_configure("WARN", foreground=THEME["warning"], font=("Consolas", 9))
        text_widget.tag_configure("ERROR", foreground=THEME["danger"], font=("Consolas", 9, "bold"))
        text_widget.tag_configure("INFO", foreground="#d1d5db", font=("Consolas", 9))
        text_widget.tag_configure("TIME", foreground=THEME["text_muted"], font=("Consolas", 9))

    def _show_progress_window(self, title="Action Progress & Live Log"):
        """Display a dedicated, sleek floating sub-window showing live step progress and log stream."""
        if self.progress_win is not None and self.progress_win.winfo_exists():
            self.progress_win.title(title)
            self.progress_win.deiconify()
            center_window(self.progress_win)
            self.progress_win.lift()
            self.progress_win.focus_force()
            return

        self.progress_win = tk.Toplevel(self.root)
        self.progress_win.title(title)
        self.progress_win.geometry("740x480")
        self.progress_win.minsize(580, 360)
        self.progress_win.configure(bg=THEME["bg"])
        center_window(self.progress_win)

        # Top Header in sub-window
        top_frame = tk.Frame(self.progress_win, bg=THEME["surface"], height=68)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)

        top_info = tk.Frame(top_frame, bg=THEME["surface"])
        top_info.pack(side=tk.LEFT, padx=18, pady=10)

        lbl_t = tk.Label(
            top_info,
            textvariable=self.progress_title_var,
            font=("Segoe UI", 11, "bold"),
            fg=THEME["text"],
            bg=THEME["surface"]
        )
        lbl_t.pack(anchor="w")

        lbl_s = tk.Label(
            top_info,
            textvariable=self.progress_step_var,
            font=("Segoe UI", 9),
            fg=THEME["info"],
            bg=THEME["surface"]
        )
        lbl_s.pack(anchor="w", pady=(2, 0))

        # Top Action Buttons in sub-window
        btn_box = tk.Frame(top_frame, bg=THEME["surface"])
        btn_box.pack(side=tk.RIGHT, padx=16, pady=16)

        btn_log_file = tk.Button(
            btn_box,
            text="📄 Open Raw Log",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["surface_alt"],
            fg=THEME["info"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._open_current_log_file
        )
        btn_log_file.pack(side=tk.LEFT, padx=(0, 6))

        btn_log_dir = tk.Button(
            btn_box,
            text="📁 Logs Folder",
            font=("Segoe UI", 8),
            bg=THEME["surface_alt"],
            fg=THEME["text_secondary"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._open_logs_dir
        )
        btn_log_dir.pack(side=tk.LEFT)

        self.progress_stop_button = tk.Button(
            btn_box,
            text="■ Stop",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["danger"],
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._request_cancel
        )
        self.progress_stop_button.pack(side=tk.LEFT, padx=(6, 0))
        self.progress_stop_button.config(state=tk.NORMAL if self.is_busy else tk.DISABLED)

        # Progress bar in sub-window
        self.win_progress_bar = ttk.Progressbar(
            self.progress_win,
            mode="indeterminate",
            style="Horizontal.TProgressbar"
        )
        self.win_progress_bar.pack(fill=tk.X)
        if self.is_busy:
            self.win_progress_bar.start(10)

        # Log Text Box Area in sub-window
        log_box_frame = tk.Frame(self.progress_win, bg=THEME["log_bg"])
        log_box_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        self.txt_win_log = tk.Text(
            log_box_frame,
            bg=THEME["log_bg"],
            fg="#e5e7eb",
            insertbackground="#fff",
            font=("Consolas", 9),
            bd=0,
            padx=10,
            pady=8,
            wrap=tk.WORD
        )
        self.txt_win_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sc = tk.Scrollbar(log_box_frame, command=self.txt_win_log.yview)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_win_log.config(yscrollcommand=sc.set)

        self._setup_log_tags(self.txt_win_log)

        # Copy existing log text into sub-window
        existing = self.txt_log.get("1.0", tk.END).strip()
        if existing:
            self.txt_win_log.insert(tk.END, existing + "\n")
            self.txt_win_log.see(tk.END)

        # Bottom Bar in sub-window
        btm_bar = tk.Frame(self.progress_win, bg=THEME["surface"], height=34)
        btm_bar.pack(fill=tk.X, side=tk.BOTTOM)
        btm_bar.pack_propagate(False)

        lbl_file = tk.Label(
            btm_bar,
            text=f"Active Log: {self.current_log_file.name if self.current_log_file else 'None'}",
            font=("Segoe UI", 8),
            fg=THEME["text_muted"],
            bg=THEME["surface"]
        )
        lbl_file.pack(side=tk.LEFT, padx=12)

        btn_close = tk.Button(
            btm_bar,
            text="Close Window",
            font=("Segoe UI", 8),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.progress_win.destroy
        )
        btn_close.pack(side=tk.RIGHT, padx=12, pady=3)

    # --------------------------------------------------------------------------
    # Central Logger: Disk File + GUI Consoles
    # --------------------------------------------------------------------------
    def log(self, message: str, level: str = "INFO"):
        """Append a message to the GUI consoles and the persistent disk log file."""
        now = datetime.now()
        time_short = now.strftime("%H:%M:%S")
        time_full = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        prefix = f"[{level.upper()}]"
        tag = level.upper()
        
        # Update current step display
        if tag in ["STEP", "START"]:
            self.progress_step_var.set(message)
        elif tag == "SUCCESS":
            self.progress_step_var.set(f"✓ {message}")

        # 1. Write to Disk Log File immediately
        if self.current_log_file:
            try:
                with open(self.current_log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{time_full}] {prefix:<9} {message}\n")
                    f.flush()
            except Exception:
                pass

        # 2. Write to GUI Consoles on Main Thread
        def _append_gui():
            use_tag = tag if tag in ["STEP", "SUCCESS", "START", "WARN", "ERROR"] else "INFO"
            # Main window text console
            if hasattr(self, "txt_log") and self.txt_log:
                self.txt_log.insert(tk.END, f"[{time_short}] ", "TIME")
                self.txt_log.insert(tk.END, f"{prefix} {message}\n", use_tag)
                self.txt_log.see(tk.END)
            # Progress sub-window text console
            if self.txt_win_log and self.progress_win and self.progress_win.winfo_exists():
                try:
                    self.txt_win_log.insert(tk.END, f"[{time_short}] ", "TIME")
                    self.txt_win_log.insert(tk.END, f"{prefix} {message}\n", use_tag)
                    self.txt_win_log.see(tk.END)
                except Exception:
                    pass

        if hasattr(self, "root") and self.root:
            self.root.after(0, _append_gui)

    def _open_current_log_file(self):
        if self.current_log_file and self.current_log_file.exists():
            try:
                os.startfile(str(self.current_log_file))
            except Exception as e:
                messagebox.showerror("Error", f"Could not open log file:\n{e}", parent=self.root)
        else:
            messagebox.showinfo("Log File", "No log file has been created yet.", parent=self.root)

    def _open_logs_dir(self):
        logs_dir = get_logs_dir()
        try:
            os.startfile(str(logs_dir))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs directory:\n{e}", parent=self.root)

    def _clear_log(self):
        self.txt_log.delete("1.0", tk.END)
        if self.txt_win_log and self.progress_win and self.progress_win.winfo_exists():
            self.txt_win_log.delete("1.0", tk.END)

    def _select_all_backup(self):
        for v in self.backup_vars.values():
            v.set(True)

    def _deselect_all_backup(self):
        for v in self.backup_vars.values():
            v.set(False)

    def _select_all_available_restore(self):
        """Select all items that are present in the current backup package."""
        for mid, var in self.restore_vars.items():
            badge = self.restore_badges.get(mid)
            if badge and "Available" in badge.cget("text"):
                var.set(True)

    def _deselect_all_restore(self):
        for v in self.restore_vars.values():
            v.set(False)

    def _request_cancel(self):
        if not self.is_busy or self.cancel_event.is_set():
            return
        self.cancel_event.set()
        self.status_text.set("Stopping after the current file...")
        self.progress_step_var.set("Cancellation requested; finishing the current file...")
        self.log("Stop requested. The job will stop safely at the next checkpoint.", level="WARN")
        self.btn_stop_job.config(state=tk.DISABLED)
        if self.progress_stop_button and self.progress_win and self.progress_win.winfo_exists():
            self.progress_stop_button.config(state=tk.DISABLED)

    def _set_busy(self, busy: bool, status="Ready"):
        self.is_busy = busy
        self.status_text.set(status)
        if busy:
            self.btn_stop_job.pack(side=tk.RIGHT, padx=(0, 8), pady=3)
            self.btn_stop_job.config(state=tk.NORMAL)
            self.progress_bar.pack(side=tk.RIGHT, padx=16, pady=5)
            self.progress_bar.start(10)
            if self.win_progress_bar and self.progress_win and self.progress_win.winfo_exists():
                self.win_progress_bar.start(10)
            if self.progress_stop_button and self.progress_win and self.progress_win.winfo_exists():
                self.progress_stop_button.config(state=tk.NORMAL)
            self.btn_run_backup.config(state=tk.DISABLED)
            self.btn_run_restore.config(state=tk.DISABLED)
            if hasattr(self, "btn_extract_all") and self.btn_extract_all.winfo_manager():
                self.btn_extract_all.config(state=tk.DISABLED)
        else:
            self.btn_stop_job.pack_forget()
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            if self.win_progress_bar and self.progress_win and self.progress_win.winfo_exists():
                self.win_progress_bar.stop()
            if self.progress_stop_button and self.progress_win and self.progress_win.winfo_exists():
                self.progress_stop_button.config(state=tk.DISABLED)
            self.progress_step_var.set(status)
            self.btn_run_backup.config(state=tk.NORMAL)
            self.btn_run_restore.config(state=tk.NORMAL)
            if hasattr(self, "btn_extract_all") and self.btn_extract_all.winfo_manager():
                self.btn_extract_all.config(state=tk.NORMAL)

    def _on_encryption_toggle(self):
        if self.encrypt_archive_var.get() and pyzipper is None:
            messagebox.showerror(
                "Encryption Support Missing",
                "Password-protected archives require pyzipper. Install it with:\n\npython -m pip install pyzipper",
                parent=self.root
            )
            self.encrypt_archive_var.set(False)

    def _prompt_new_archive_password(self):
        password = simpledialog.askstring(
            "Protect Backup Archive",
            "Enter a password for this AES-256 encrypted archive:",
            parent=self.root,
            show="*"
        )
        if password is None:
            return None
        if len(password) < 8:
            messagebox.showwarning("Password Too Short", "Use a password of at least 8 characters.", parent=self.root)
            return None
        confirmation = simpledialog.askstring(
            "Confirm Archive Password",
            "Re-enter the archive password:",
            parent=self.root,
            show="*"
        )
        if confirmation is None:
            return None
        if password != confirmation:
            messagebox.showerror("Passwords Do Not Match", "The passwords did not match. Backup cancelled.", parent=self.root)
            return None
        return password

    def _prompt_archive_password(self):
        return simpledialog.askstring(
            "Unlock Backup Archive",
            "This backup is password-protected. Enter its password to import:",
            parent=self.root,
            show="*"
        )

    def _check_running_processes_for_backup(self, selected_ids):
        """Find any running processes among the selected modules using fast in-memory snapshot."""
        running_set = get_running_process_names()
        conflicts = []
        for mid in selected_ids:
            mod = MODULE_MAP.get(mid)
            if not mod:
                continue
            procs = getattr(mod, "PROCESSES", [])
            active = [p for p in procs if p.lower() in running_set]
            if active:
                conflicts.append((mod.NAME, active))
        return conflicts

    def _prompt_close_conflicting_apps(self, conflicts):
        """Display modern dialog listing running apps and offering to terminate them before backup."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Applications Must Be Closed")
        dialog.geometry("560x370")
        dialog.minsize(500, 320)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self.root)
        center_window(dialog)
        dialog.grab_set()

        result = {"proceed": False}

        hdr = tk.Frame(dialog, bg=THEME["surface"], height=60)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        lbl_icon = tk.Label(hdr, text="⚠️", font=("Segoe UI", 18), bg=THEME["surface"])
        lbl_icon.pack(side=tk.LEFT, padx=(18, 8))

        lbl_hdr = tk.Label(
            hdr,
            text="Running Applications Detected",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["warning"],
            bg=THEME["surface"]
        )
        lbl_hdr.pack(side=tk.LEFT, pady=16)

        body = tk.Frame(dialog, bg=THEME["bg"], padx=20, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        msg_lbl = tk.Label(
            body,
            text="The following applications are currently open and must be closed\nbefore the backup can proceed safely:",
            font=("Segoe UI", 10),
            fg=THEME["text"],
            bg=THEME["bg"],
            justify=tk.LEFT
        )
        msg_lbl.pack(anchor="w", pady=(0, 10))

        list_card = tk.Frame(body, bg=THEME["card_bg"], bd=1, relief="solid", padx=12, pady=10)
        list_card.pack(fill=tk.BOTH, expand=True)

        all_proc_names = []
        for mod_name, proc_list in conflicts:
            all_proc_names.extend(proc_list)
            row = tk.Label(
                list_card,
                text=f"•  {mod_name}  ({', '.join(proc_list)})",
                font=("Segoe UI", 10, "bold"),
                fg="#fca5a5",
                bg=THEME["card_bg"],
                anchor="w"
            )
            row.pack(fill=tk.X, pady=2)

        note_lbl = tk.Label(
            body,
            text="Active applications hold locks on databases and session caches.\nThe backup cannot run while they are open.",
            font=("Segoe UI", 8, "italic"),
            fg=THEME["text_muted"],
            bg=THEME["bg"],
            justify=tk.LEFT
        )
        note_lbl.pack(anchor="w", pady=(8, 0))

        btn_bar = tk.Frame(dialog, bg=THEME["surface"], height=52)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)
        btn_bar.pack_propagate(False)

        def _on_close_and_proceed():
            terminate_processes(all_proc_names, log_fn=self.log)
            import time
            time.sleep(0.5)
            active_after = get_running_process_names()
            still_open = [p for p in all_proc_names if p.lower() in active_after]
            if still_open:
                messagebox.showwarning(
                    "Applications Still Open",
                    f"The following process(es) could not be closed automatically:\n{', '.join(still_open)}\n\nPlease close them manually, then try backup again.",
                    parent=dialog
                )
                dialog.destroy()
                return
            result["proceed"] = True
            dialog.destroy()

        def _on_cancel():
            result["proceed"] = False
            dialog.destroy()

        btn_cancel = tk.Button(
            btn_bar,
            text="Cancel Backup",
            font=("Segoe UI", 9),
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground="#fff",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=_on_cancel
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(6, 16), pady=10)

        btn_close_apps = tk.Button(
            btn_bar,
            text="🛑 Close Applications & Proceed",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["danger"],
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            bd=0,
            padx=18,
            pady=6,
            cursor="hand2",
            command=_on_close_and_proceed
        )
        btn_close_apps.pack(side=tk.RIGHT, padx=6, pady=10)

        self.root.wait_window(dialog)
        return result["proceed"]

    # --------------------------------------------------------------------------
    # Backup Flow (Generates Archive + Reference Manifest)
    # --------------------------------------------------------------------------
    def _start_backup_flow(self):
        if self.is_busy:
            return

        selected_ids = [mid for mid, v in self.backup_vars.items() if v.get()]
        active_custom = [cf for cf in self.custom_folders if cf["var"].get()]
        if not selected_ids and not active_custom:
            messagebox.showwarning("No Items Selected", "Please select at least one item or custom folder to include in the backup.", parent=self.root)
            return

        # Check for open conflicting applications prior to backup
        conflicts = self._check_running_processes_for_backup(selected_ids)
        if conflicts:
            proceed = self._prompt_close_conflicting_apps(conflicts)
            if not proceed:
                self.log("Backup cancelled: running applications must be closed first.", level="WARN")
                return

        default_name = f"Win11_ProfileBackup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        while True:
            save_path = filedialog.asksaveasfilename(
                title="Save Migration Backup Archive",
                initialfile=default_name,
                defaultextension=".zip",
                filetypes=[("Zip Archive", "*.zip"), ("All Files", "*.*")],
                parent=self.root
            )
            if not save_path:
                return
            conflict = get_backup_destination_conflict(Path(save_path), selected_ids, active_custom)
            if conflict is None:
                break
            messagebox.showwarning(
                "Choose a Different Backup Location",
                f"The selected destination is inside a folder being included in this backup:\n\n{conflict}\n\nChoose a location outside the selected backup folders to prevent recursive backups.",
                parent=self.root
            )

        archive_password = None
        if self.encrypt_archive_var.get():
            if pyzipper is None:
                messagebox.showerror("Encryption Support Missing", "Install pyzipper with: python -m pip install pyzipper", parent=self.root)
                return
            archive_password = self._prompt_new_archive_password()
            if archive_password is None:
                self.log("Password-protected backup cancelled before it started.", level="WARN")
                return

        self._init_session_log_file(prefix="backup")
        self.cancel_event.clear()
        self.progress_title_var.set("📦 Creating Migration Backup Archive")
        self.progress_step_var.set("Initializing backup...")
        self._show_progress_window(title="Backup Progress & Live Log")
        self._set_busy(True, "Creating migration backup package...")
        threading.Thread(target=self._backup_worker, args=(Path(save_path), selected_ids, active_custom, archive_password), daemon=True).start()

    def _backup_worker(self, output_zip: Path, selected_ids: list, active_custom: list = None, archive_password: str | None = None):
        global ACTIVE_JOB_CANCEL_EVENT, ACTIVE_BACKUP_OUTPUT_PATH, ACTIVE_JOB_LOGGER
        ACTIVE_JOB_CANCEL_EVENT = self.cancel_event
        ACTIVE_BACKUP_OUTPUT_PATH = output_zip.resolve()
        ACTIVE_JOB_LOGGER = self.log
        start_time = datetime.now()
        active_custom = active_custom or []
        self.log(f"Starting Profile Backup operation -> {output_zip.name}", level="START")
        self.log(f"Selected {len(selected_ids)} component(s) and {len(active_custom)} custom folder(s).", level="INFO")

        temp_dir = output_zip.parent / f"_temp_migrate_{datetime.now().strftime('%H%M%S')}"
        partial_zip = output_zip.with_name(output_zip.name + ".partial")
        final_status = "Backup finished."

        def cancel_backup():
            nonlocal final_status
            final_status = "Backup cancelled."
            self.log("Backup cancelled by user; removing temporary and partial files.", level="WARN")
            shutil.rmtree(temp_dir, ignore_errors=True)
            partial_zip.unlink(missing_ok=True)
            output_zip.with_suffix(".reference.json").unlink(missing_ok=True)

        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
            module_settings_summary = {}

            # Execute step for each selected module
            for idx, mid in enumerate(selected_ids, 1):
                if check_job_cancelled():
                    cancel_backup()
                    return
                mod = MODULE_MAP.get(mid)
                if not mod:
                    continue

                self.log(f"[STEP {idx}/{len(selected_ids)}] Packaging {mod.NAME}...", level="STEP")
                try:
                    summary_data = mod.backup(temp_dir, self.log)
                    if check_job_cancelled():
                        cancel_backup()
                        return
                    if summary_data is None:
                        summary_data = {"status": "completed"}
                    module_settings_summary[mid] = {
                        "name": mod.NAME,
                        "category": mod.CATEGORY,
                        "summary": summary_data.get("summary", "Captured successfully"),
                        "details": summary_data
                    }
                    self.log(f"[STEP {idx}/{len(selected_ids)}] Successfully finished {mod.NAME}.", level="SUCCESS")
                except Exception as e:
                    self.log(f"Error packaging {mod.NAME}: {e}", level="ERROR")
                    module_settings_summary[mid] = {
                        "name": mod.NAME,
                        "category": mod.CATEGORY,
                        "summary": f"Error: {e}",
                        "details": {"error": str(e)}
                    }

            # Process custom folders
            custom_manifest_entries = []
            if active_custom:
                self.log(f"--- Packaging {len(active_custom)} Custom Folder(s) ---", level="STEP")
                for idx, item in enumerate(active_custom, 1):
                    if check_job_cancelled():
                        cancel_backup()
                        return
                    folder_path = Path(item["path"])
                    if folder_path.exists():
                        clean_name = folder_path.name or f"Folder_{idx}"
                        dest_sub = temp_dir / "CustomFolders" / f"cf_{idx}_{clean_name}"
                        dest_sub.mkdir(parents=True, exist_ok=True)
                        self.log(f"Backing up custom folder: {folder_path}...", level="STEP")
                        c_cnt, c_bytes = copy_folder_filtered(folder_path, dest_sub, log_cb=self.log)
                        if check_job_cancelled():
                            cancel_backup()
                            return
                        mb = round(c_bytes / (1024 * 1024), 1)
                        self.log(f"Backed up custom folder '{clean_name}': {c_cnt} files ({mb} MB).", level="INFO")
                        custom_manifest_entries.append({
                            "name": clean_name,
                            "original_path": str(folder_path),
                            "archive_subpath": f"CustomFolders/cf_{idx}_{clean_name}",
                            "files_count": c_cnt,
                            "size_mb": mb
                        })

            # Build comprehensive Reference File
            if check_job_cancelled():
                cancel_backup()
                return
            reference_data = {
                "reference_version": "1.2",
                "app_title": APP_TITLE,
                "app_version": APP_VERSION,
                "created_at": datetime.now().isoformat(),
                "created_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_machine": {
                    "computer_name": os.environ.get("COMPUTERNAME", "Unknown"),
                    "username": os.environ.get("USERNAME", "Unknown"),
                    "os": platform.platform(),
                    "architecture": platform.architecture()[0]
                },
                "selected_modules": selected_ids,
                "module_settings": module_settings_summary,
                "custom_folders": custom_manifest_entries,
                "encrypted": bool(archive_password),
                "encryption_algorithm": "AES-256" if archive_password else None,
                "filenames_encrypted": bool(archive_password)
            }

            # 1. Write reference file inside backup package
            ref_path = temp_dir / "migration_reference.json"
            ref_path.write_text(json.dumps(reference_data, indent=2), encoding="utf-8")

            # Also keep legacy manifest name for backwards compatibility
            (temp_dir / "migration_manifest.json").write_text(json.dumps(reference_data, indent=2), encoding="utf-8")
            self.log("Generated migration_reference.json inside archive.", level="INFO")

            # 2. Write companion reference file alongside the .zip
            companion_ref = output_zip.with_suffix(".reference.json")
            try:
                companion_ref.write_text(json.dumps(reference_data, indent=2), encoding="utf-8")
                self.log(f"Created companion reference file: {companion_ref.name}", level="INFO")
            except Exception as e:
                self.log(f"Note: Could not write companion reference file: {e}", level="WARN")

            # 3. Create uncompressed portable zip package
            self.log("Bundling files into portable archive...", level="STEP")
            reference_names = {"migration_reference.json", "migration_manifest.json"}
            archive_cancelled = False
            if archive_password:
                if pyzipper is None:
                    raise RuntimeError("pyzipper is required to create a password-protected archive")
                with zipfile.ZipFile(partial_zip, "w", compression=zipfile.ZIP_STORED) as zf:
                    for name in reference_names:
                        zf.write(temp_dir / name, arcname=name)

                self.log("Encrypting archive data and filename index with AES-256; ZIP payload names are randomized.", level="INFO")
                with pyzipper.AESZipFile(
                    partial_zip,
                    "a",
                    compression=zipfile.ZIP_STORED,
                    encryption=pyzipper.WZ_AES
                ) as zf:
                    zf.setpassword(archive_password.encode("utf-8"))
                    zf.setencryption(pyzipper.WZ_AES, nbits=256)
                    encrypted_index = []
                    for root, _, files in os.walk(temp_dir):
                        for f in files:
                            if check_job_cancelled():
                                archive_cancelled = True
                                break
                            full_f = Path(root) / f
                            rel_f = full_f.relative_to(temp_dir)
                            if str(rel_f).replace("\\", "/") in reference_names:
                                continue
                            archive_name = f"payload/{uuid.uuid4().hex}.bin"
                            zf.write(full_f, arcname=archive_name)
                            encrypted_index.append({
                                "archive_name": archive_name,
                                "relative_path": rel_f.as_posix()
                            })
                        if archive_cancelled:
                            break
                    if not archive_cancelled:
                        zf.writestr("payload-index", json.dumps(encrypted_index).encode("utf-8"))
            else:
                with zipfile.ZipFile(partial_zip, "w", compression=zipfile.ZIP_STORED) as zf:
                    for root, _, files in os.walk(temp_dir):
                        for f in files:
                            if check_job_cancelled():
                                archive_cancelled = True
                                break
                            full_f = Path(root) / f
                            rel_f = full_f.relative_to(temp_dir)
                            zf.write(full_f, arcname=str(rel_f))
                        if archive_cancelled:
                            break

            if archive_cancelled or check_job_cancelled():
                cancel_backup()
                return
            os.replace(partial_zip, output_zip)

            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

            elapsed = round((datetime.now() - start_time).total_seconds(), 1)
            file_size_mb = round(output_zip.stat().st_size / (1024 * 1024), 2)
            self.log(f"✓ Backup complete in {elapsed}s! Archive size: {file_size_mb} MB", level="SUCCESS")
            self.log(f"Output File: {output_zip}", level="INFO")
            self.log(f"Log File: {self.current_log_file}", level="INFO")

            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Backup Completed",
                    f"Migration backup successfully created!\n\nFile: {output_zip.name}\nSize: {file_size_mb} MB\nDuration: {elapsed} seconds\n\nReference settings metadata has been packaged into the archive.",
                    parent=self.root
                ))
        except Exception as e:
            self.log(f"Fatal error during backup: {e}", level="ERROR")
            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda: messagebox.showerror("Backup Failed", f"An error occurred:\n{e}", parent=self.root))
        finally:
            ACTIVE_JOB_CANCEL_EVENT = None
            ACTIVE_BACKUP_OUTPUT_PATH = None
            ACTIVE_JOB_LOGGER = None

            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda status=final_status: self._set_busy(False, status))

    # --------------------------------------------------------------------------
    # Restore Flow (Auto-Detects Exported Settings from Reference File)
    # --------------------------------------------------------------------------
    def _browse_backup_file(self):
        f = filedialog.askopenfilename(
            title="Open Migration Backup Archive",
            filetypes=[("Zip Archive", "*.zip"), ("All Files", "*.*")],
            parent=self.root
        )
        if f:
            self.selected_backup_path.set(f)
            self._inspect_backup_archive(Path(f))

    def _inspect_backup_archive(self, zip_path: Path):
        """Read reference settings from archive and pre-select matching options."""
        self.log(f"Inspecting backup package: {zip_path.name}...", level="STEP")
        ref_data = None
        self.backup_archive_loaded = False

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                self.backup_archive_loaded = True
                namelist = zf.namelist()
                for candidate in ["migration_reference.json", "migration_manifest.json"]:
                    if candidate in namelist:
                        ref_data = json.loads(zf.read(candidate).decode("utf-8"))
                        self.log(f"Loaded reference settings metadata from '{candidate}'.", level="INFO")
                        break

            if not ref_data:
                companion = zip_path.with_suffix(".reference.json")
                if companion.exists():
                    ref_data = json.loads(companion.read_text(encoding="utf-8"))
                    self.log(f"Loaded reference metadata from companion file '{companion.name}'.", level="INFO")

        except Exception as e:
            self.backup_archive_loaded = False
            self.log(f"Warning inspecting backup package: {e}", level="WARN")

        if self.backup_archive_loaded:
            if not self.btn_extract_all.winfo_manager():
                self.btn_extract_all.pack(side=tk.RIGHT, padx=6, pady=6)
        else:
            self.btn_extract_all.pack_forget()

        if ref_data:
            src_info = ref_data.get("source_machine", {})
            src_comp = src_info.get("computer_name", "Unknown PC")
            src_user = src_info.get("username", "Unknown User")
            ts = ref_data.get("created_timestamp") or ref_data.get("created_at", "Unknown Date")
            selected_mods = ref_data.get("selected_modules") or ref_data.get("included_modules", [])
            module_settings = ref_data.get("module_settings", {})
            self.backup_requires_password = bool(ref_data.get("encrypted", False))
            filenames_encrypted = bool(ref_data.get("filenames_encrypted", False))
            self.backup_filenames_encrypted = filenames_encrypted

            # Update Header Banner
            protection = " | AES-256 password protected" if self.backup_requires_password else ""
            hidden_names = " | filenames protected" if filenames_encrypted else ""
            info_text = f"Origin: {src_user}@{src_comp} | Exported: {ts} | {len(selected_mods)} component(s) packaged{protection}{hidden_names}"
            self.lbl_origin_info.config(text=info_text, fg=THEME["info"])
            if self.backup_requires_password:
                self.log("Reference manifest indicates that payload entries are AES-256 encrypted.", level="INFO")

            # Update each module card according to export reference
            for mod in MODULES:
                mid = mod.ID
                is_included = mid in selected_mods
                var = self.restore_vars.get(mid)
                badge = self.restore_badges.get(mid)
                summary_lbl = self.restore_summaries.get(mid)

                if is_included:
                    if var:
                        var.set(True)
                    if badge:
                        badge.config(text="● Available in backup", fg=THEME["success"])

                    mod_meta = module_settings.get(mid, {})
                    mod_summary = mod_meta.get("summary") or "Settings captured in export"
                    if summary_lbl:
                        summary_lbl.config(text=f"Exported settings: {mod_summary}", fg=THEME["text"])
                else:
                    if var:
                        var.set(False)
                    if badge:
                        badge.config(text="○ Not in this backup", fg=THEME["text_muted"])
                    if summary_lbl:
                        summary_lbl.config(text="Not captured during export on source machine", fg=THEME["text_muted"])

            # Restore custom folders detection
            cf_list = ref_data.get("custom_folders", [])
            self.restored_custom_folders = []
            for item in cf_list:
                var = tk.BooleanVar(value=True)
                self.restored_custom_folders.append({
                    "name": item.get("name", "CustomFolder"),
                    "original_path": item.get("original_path", ""),
                    "archive_subpath": item.get("archive_subpath", ""),
                    "files_count": item.get("files_count", 0),
                    "size_mb": item.get("size_mb", 0),
                    "var": var
                })
            self._refresh_restore_custom_cards()

            self.log(f"Auto-detected settings: pre-selected {len(selected_mods)} item(s) from {src_user}@{src_comp}.", level="SUCCESS")
        else:
            self.backup_requires_password = False
            self.backup_filenames_encrypted = False
            self.lbl_origin_info.config(text="Custom archive (No reference metadata found). Select items manually.", fg=THEME["warning"])
            for mid in self.restore_vars:
                self.restore_badges[mid].config(text="● Package selected", fg=THEME["info"])

    def _start_extract_all(self):
        if self.is_busy:
            return
        archive_path = Path(self.selected_backup_path.get().strip())
        if not self.backup_archive_loaded or not archive_path.is_file():
            messagebox.showwarning("Select Backup", "Load a valid backup archive before extracting it.", parent=self.root)
            return

        destination = filedialog.askdirectory(title="Choose a folder to extract the backup into", parent=self.root)
        if not destination:
            return

        archive_password = None
        if self.backup_requires_password:
            if pyzipper is None:
                messagebox.showerror("Encryption Support Missing", "This backup requires AES ZIP support. Install pyzipper with: python -m pip install pyzipper", parent=self.root)
                return
            archive_password = self._prompt_archive_password()
            if not archive_password:
                return

        self._init_session_log_file(prefix="extract")
        self.cancel_event.clear()
        self.progress_title_var.set("Extracting Backup Archive")
        self.progress_step_var.set("Preparing extraction...")
        self._show_progress_window(title="Extract Progress & Live Log")
        self._set_busy(True, "Extracting backup archive...")
        threading.Thread(
            target=self._extract_all_worker,
            args=(archive_path, Path(destination), archive_password),
            daemon=True
        ).start()

    def _extract_all_worker(self, archive_path: Path, destination: Path, archive_password: str | None = None):
        global ACTIVE_JOB_CANCEL_EVENT, ACTIVE_JOB_LOGGER
        ACTIVE_JOB_CANCEL_EVENT = self.cancel_event
        ACTIVE_JOB_LOGGER = self.log
        final_status = "Extraction finished."
        self.log(f"Extracting all archive contents from {archive_path.name} to {destination}.", level="START")
        try:
            destination.mkdir(parents=True, exist_ok=True)
            if archive_password:
                with pyzipper.AESZipFile(archive_path, "r") as archive:
                    archive.setpassword(archive_password.encode("utf-8"))
                    if self.backup_filenames_encrypted:
                        extracted = extract_encrypted_archive_with_cancel(archive, destination)
                        if extracted:
                            for manifest_name in ("migration_reference.json", "migration_manifest.json"):
                                check_job_cancelled()
                                if manifest_name in archive.namelist():
                                    (destination / manifest_name).write_bytes(archive.read(manifest_name))
                    else:
                        extracted = extract_archive_with_cancel(archive, destination)
            else:
                with zipfile.ZipFile(archive_path, "r") as archive:
                    extracted = extract_archive_with_cancel(archive, destination)

            if not extracted or check_job_cancelled():
                final_status = "Extraction cancelled."
                self.log("Extraction cancelled by user; files already extracted remain in the chosen folder.", level="WARN")
                return

            self.log(f"Archive extracted successfully to {destination}.", level="SUCCESS")
            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda: messagebox.showinfo("Extraction Complete", f"Archive contents extracted to:\n{destination}", parent=self.root))
        except Exception as exc:
            final_status = "Extraction failed."
            self.log(f"Archive extraction failed: {exc}", level="ERROR")
            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda error=str(exc): messagebox.showerror("Extraction Failed", f"Could not extract the backup. Check the password and archive.\n\n{error}", parent=self.root))
        finally:
            ACTIVE_JOB_CANCEL_EVENT = None
            ACTIVE_JOB_LOGGER = None

            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda status=final_status: self._set_busy(False, status))

    def _start_restore_flow(self):
        if self.is_busy:
            return

        zip_str = self.selected_backup_path.get().strip()
        if not zip_str or not Path(zip_str).exists():
            messagebox.showwarning("Select Backup", "Please browse and select a valid backup .zip file first.", parent=self.root)
            return

        selected_ids = [mid for mid, v in self.restore_vars.items() if v.get()]
        active_custom_restore = [cf for cf in self.restored_custom_folders if cf["var"].get()]
        if not selected_ids and not active_custom_restore:
            messagebox.showwarning("No Items Selected", "Please select at least one item or custom folder to import.", parent=self.root)
            return

        confirm = messagebox.askyesno(
            "Confirm Import",
            f"Are you ready to restore {len(selected_ids)} component(s) and {len(active_custom_restore)} custom folder(s) to this Windows 11 machine?\n\nTarget browsers/apps will be closed to release file locks before import.",
            parent=self.root
        )
        if not confirm:
            return

        archive_password = None
        if self.backup_requires_password:
            if pyzipper is None:
                messagebox.showerror("Encryption Support Missing", "This backup requires AES ZIP support. Install pyzipper with: python -m pip install pyzipper", parent=self.root)
                return
            archive_password = self._prompt_archive_password()
            if archive_password is None or not archive_password:
                return

        self._init_session_log_file(prefix="restore")
        self.cancel_event.clear()
        self.progress_title_var.set("🚀 Restoring Profile Items to This PC")
        self.progress_step_var.set("Initializing restore...")
        self._show_progress_window(title="Import Progress & Live Log")
        self._set_busy(True, "Restoring profile items...")
        threading.Thread(target=self._restore_worker, args=(Path(zip_str), selected_ids, active_custom_restore, archive_password), daemon=True).start()

    def _restore_worker(self, zip_path: Path, selected_ids: list, active_custom_restore: list = None, archive_password: str | None = None):
        global ACTIVE_JOB_CANCEL_EVENT, ACTIVE_JOB_LOGGER
        ACTIVE_JOB_CANCEL_EVENT = self.cancel_event
        ACTIVE_JOB_LOGGER = self.log
        start_time = datetime.now()
        active_custom_restore = active_custom_restore or []
        self.log(f"Starting Profile Import operation from -> {zip_path.name}", level="START")
        self.log(f"Selected {len(selected_ids)} component(s) and {len(active_custom_restore)} custom folder(s) to restore.", level="INFO")

        temp_dir = zip_path.parent / f"_temp_restore_{datetime.now().strftime('%H%M%S')}"
        final_status = "Restore finished."

        def cancel_restore():
            nonlocal final_status
            final_status = "Restore cancelled."
            self.log("Restore cancelled by user; removing temporary extracted files.", level="WARN")
            shutil.rmtree(temp_dir, ignore_errors=True)

        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.log("Extracting migration archive...", level="STEP")
            if archive_password:
                with pyzipper.AESZipFile(zip_path, "r") as zf:
                    zf.setpassword(archive_password.encode("utf-8"))
                    if self.backup_filenames_encrypted:
                        extraction_complete = extract_encrypted_archive_with_cancel(zf, temp_dir)
                    else:
                        extraction_complete = extract_archive_with_cancel(zf, temp_dir)
            else:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    extraction_complete = extract_archive_with_cancel(zf, temp_dir)
            if not extraction_complete or check_job_cancelled():
                cancel_restore()
                return
            self.log("Archive extracted successfully.", level="INFO")

            # Restore each selected item with step logging
            for idx, mid in enumerate(selected_ids, 1):
                if check_job_cancelled():
                    cancel_restore()
                    return
                mod = MODULE_MAP.get(mid)
                if not mod:
                    continue

                self.log(f"[STEP {idx}/{len(selected_ids)}] Restoring {mod.NAME}...", level="STEP")
                try:
                    mod.restore(temp_dir, self.log)
                    if check_job_cancelled():
                        cancel_restore()
                        return
                    self.log(f"[STEP {idx}/{len(selected_ids)}] Successfully restored {mod.NAME}.", level="SUCCESS")
                except Exception as e:
                    self.log(f"Error restoring {mod.NAME}: {e}", level="ERROR")

            # Restore custom folders
            if active_custom_restore:
                self.log(f"--- Restoring {len(active_custom_restore)} Custom Folder(s) ---", level="STEP")
                for cf in active_custom_restore:
                    if check_job_cancelled():
                        cancel_restore()
                        return
                    orig_p = Path(cf["original_path"])
                    arch_sub = temp_dir / Path(cf["archive_subpath"])
                    if arch_sub.exists():
                        self.log(f"Restoring custom folder '{cf['name']}' to {orig_p}...", level="STEP")
                        orig_p.mkdir(parents=True, exist_ok=True)
                        copied, _ = copy_folder_filtered(arch_sub, orig_p, log_cb=self.log)
                        if check_job_cancelled():
                            cancel_restore()
                            return
                        self.log(f"Restored custom folder '{cf['name']}' ({copied} files).", level="SUCCESS")

            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

            elapsed = round((datetime.now() - start_time).total_seconds(), 1)
            self.log(f"✓ Profile migration restore completed in {elapsed}s!", level="SUCCESS")
            self.log(f"Log File: {self.current_log_file}", level="INFO")

            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Migration Complete",
                    f"Your selected profile items, browser favorites, passwords, extensions, and Windows settings have been restored successfully in {elapsed} seconds!\n\nCheck the log file for step-by-step details:\n{self.current_log_file.name}",
                    parent=self.root
                ))
        except Exception as e:
            self.log(f"Fatal error during restore: {e}", level="ERROR")
            shutil.rmtree(temp_dir, ignore_errors=True)
            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda: messagebox.showerror("Restore Failed", f"An error occurred:\n{e}", parent=self.root))
        finally:
            ACTIVE_JOB_CANCEL_EVENT = None
            ACTIVE_JOB_LOGGER = None

            if hasattr(self, "root") and self.root:
                self.root.after(0, lambda status=final_status: self._set_busy(False, status))


# ==============================================================================
# Main Entry Point
# ==============================================================================

def main():
    global SINGLE_INSTANCE_MUTEX

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        SINGLE_INSTANCE_MUTEX = acquire_single_instance_mutex()
    except Exception:
        return
    if SINGLE_INSTANCE_MUTEX is None:
        return

    try:
        root = tk.Tk()
        root.withdraw()
        ModernMigratorApp(root)
        center_window(root)
        root.deiconify()
        root.mainloop()
    finally:
        release_single_instance_mutex(SINGLE_INSTANCE_MUTEX)
        SINGLE_INSTANCE_MUTEX = None


SINGLE_INSTANCE_MUTEX = None


def acquire_single_instance_mutex(name: str | None = None):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_mutex = kernel32.CreateMutexW
    create_mutex.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
    create_mutex.restype = ctypes.c_void_p
    ctypes.set_last_error(0)
    handle = create_mutex(None, 0, name or rf"Local\{APP_TITLE}")
    error_code = ctypes.get_last_error()
    if not handle:
        raise ctypes.WinError(error_code)
    if error_code == 183:
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [ctypes.c_void_p]
        close_handle.restype = ctypes.c_int
        close_handle(handle)
        return None
    return handle


def release_single_instance_mutex(handle):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [ctypes.c_void_p]
    close_handle.restype = ctypes.c_int
    close_handle(handle)


if __name__ == "__main__":
    main()
