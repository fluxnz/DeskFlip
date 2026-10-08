# DeskFlip

DeskFlip is a Windows 11 desktop utility for creating portable backups of a Windows user profile and selected application data, then importing those backups on another PC. It provides a graphical interface for choosing what to back up and restore, so a migration can include only the items you need.

The application is implemented as a single Python file, [`DeskFlip.py`](DeskFlip.py), with its logo embedded in the source.

## What DeskFlip can migrate

Select individual categories in the app's backup and import screens. Available data includes:

- **Web browsers:** Microsoft Edge, Google Chrome, and Mozilla Firefox profiles, bookmarks, history, extensions, preferences, and related profile data.
- **Windows settings and personalization:** wallpaper, mouse and keyboard settings, theme and accent colors, File Explorer preferences, sound settings, Wi-Fi profiles, network drive mappings, Windows credentials and Vault data, and user-installed fonts.
- **Microsoft Outlook:** profiles and account configuration, signatures, autocomplete data, and PST files. Offline OST caches are excluded.
- **Shortcuts and taskbar pins:** Quick Launch shortcuts, pinned taskbar shortcuts, and taskbar layout settings.
- **Developer and power-user tools:** Visual Studio Code user settings and extensions, Windows Terminal profiles and PowerShell scripts, Git and SSH configuration, Remote Desktop connection data, PuTTY, WinSCP, FileZilla, and Notepad++ configuration and sessions.
- **Personal files:** Desktop, Downloads, Documents, Pictures, and any additional folders you choose in the app.

Some data depends on the applications and Windows features installed on the source or destination PC. Review the selection in the app before running a migration.

## Backups and restore

DeskFlip packages selected data in a portable ZIP archive. The archive includes a migration reference manifest, and a companion reference JSON file is saved next to it. When you open an archive to import, DeskFlip reads the manifest to identify the included categories and preselects them; you can change the selection before restoring. An **Extract All** option is also available for extracting archive contents to a folder.

The app detects when relevant applications are running before a backup and lets you close them or cancel. Backup and restore jobs show live progress and write timestamped logs. Active jobs can be stopped; cancellation is cooperative and happens at file or module checkpoints.

### Sensitive data

Profile migrations can include sensitive information such as saved browser logins, Wi-Fi passwords, Windows credentials, SSH keys, and personal files. Protect the archive and its companion reference file, and transfer them only through a trusted channel.

You can enable **Password-protect archive (AES-256)** when creating a backup. The backup payload and its path index are encrypted, and payload entry names are randomized. The small reference manifest remains readable and contains package metadata and selected custom-folder locations. The password is not saved in the archive; a lost password cannot be recovered.

## Run from source

DeskFlip requires Windows 11 and a Python installation that includes Tkinter.

1. Install Python for Windows with Tkinter enabled.
2. Open PowerShell in this folder.
3. Run:

   ```powershell
   python .\DeskFlip.py
   ```

Password-protected archives require the optional `pyzipper` package. Install it with:

```powershell
python -m pip install pyzipper
```

Without `pyzipper`, unprotected backups and imports remain available, but AES-256 archive support is unavailable.
