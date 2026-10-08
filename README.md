# DeskFlip

DeskFlip is a Windows 11 desktop utility for creating portable backups of a Windows user profile and selected application data, then importing those backups on another PC. It provides a graphical interface for choosing what to back up and restore, so a migration can include only the items you need.

DeskFlip is distributed as a compiled Windows executable. The application and its logo are implemented in the single source file [`DeskFlip.py`](DeskFlip.py).

## What DeskFlip can migrate

Select individual categories in the app's backup and import screens. Available data includes:

- **Web browsers:** Microsoft Edge, Google Chrome, and Mozilla Firefox profiles, bookmarks, history, extensions, preferences, and related profile data.
- **Windows settings and personalization:** wallpaper, mouse and keyboard settings, theme and accent colors, File Explorer preferences, sound settings, Wi-Fi profiles, network drive mappings, Windows credentials and Vault data, and user-installed fonts.
- **Microsoft Outlook:** profiles and account configuration, signatures, autocomplete data, and PST files. Offline OST caches are excluded.
- **Shortcuts and taskbar pins:** Quick Launch shortcuts, pinned taskbar shortcuts, and taskbar layout settings.
- **Developer and power-user tools:** Visual Studio Code user settings and extensions, Windows Terminal profiles and PowerShell scripts, Git and SSH configuration, Remote Desktop connection data, PuTTY, WinSCP, FileZilla, Devolutions Remote Desktop Manager local settings and data sources, and Notepad++ configuration and sessions.
- **Personal files:** Desktop, Downloads, Documents, Pictures, and any additional folders you choose in the app.

Some data depends on the applications and Windows features installed on the source or destination PC. Review the selection in the app before running a migration.

**Registry settings:** each module also exports the HKCU registry keys it depends on (for example pointer schemes, accent colors, keyboard layouts, Outlook options, console settings, browser policies and OpenSSH agent keys). They are stored in the archive under `Registry\<module>` and are re-imported automatically whenever that module is selected on import. Only keys that exist on the source PC are captured, and per-user (HKCU) keys only.

**Remote Desktop Manager note:** DeskFlip copies the local `%LOCALAPPDATA%\Devolutions\RemoteDesktopManager` folder and its registry settings. Install Remote Desktop Manager on the new PC before restoring. Entries held in a remote or shared data source are not covered; for those, and as a fail-safe, also use RDM's own export (File > Settings > Export).

## Backups and restore

DeskFlip packages selected data in a portable ZIP archive. The archive includes a migration reference manifest, and a companion reference JSON file is saved next to it. When you open an archive to import, DeskFlip reads the manifest to identify the included categories and preselects them; you can change the selection before restoring. An **Extract All** option is also available for extracting archive contents to a folder.

Right-clicking a module name on the Backup or Import screen opens a floating bulleted list of the folders and registry keys that module reads from. It stays visible while the cursor is over it and fades out when the cursor leaves.

When a backup is opened, DeskFlip compares the username recorded in it with the current Windows username (domain ignored). A mismatch is flagged in the header banner and the log, and repeated in the Confirm Import dialog.

The app detects when relevant applications are running before a backup or an import and lets you close them or cancel. On the import screen each component also shows whether the application is detected on the current PC ("This PC: ●/○"), so you can tell whether restoring it is worthwhile. Backup and restore jobs show live progress and write timestamped logs. Active jobs can be stopped; cancellation is cooperative and happens at file or module checkpoints.

### Sensitive data

Profile migrations can include sensitive information such as saved browser logins, Wi-Fi passwords, Windows credentials, SSH keys, and personal files. Protect the archive and its companion reference file, and transfer them only through a trusted channel.

You can enable **Password-protect archive (AES-256)** when creating a backup. The backup payload and its path index are encrypted, and payload entry names are randomized. The small reference manifest remains readable and contains package metadata and selected custom-folder locations. The password is not saved in the archive; a lost password cannot be recovered.

## Run DeskFlip

Run `DeskFlip.exe` from the packaged distribution on Windows 11. Python does not need to be installed: the compiled executable packages the Python runtime and the dependencies included in that build. No VS Code setup or separate Tkinter installation is required.

AES-256 password-protected archives use the optional `pyzipper` dependency. It must be included when the executable is built for password-protected backup and restore to be available. If it is not included, unprotected backups and imports still work, but the app cannot create or open AES-encrypted archives.

The Python source is available for developers who want to inspect or build the application; end users can run the packaged executable without installing Python packages.
