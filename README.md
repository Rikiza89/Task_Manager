# 日次タスク管理 / Daily Task Manager

A lightweight Windows desktop app (tkinter) to manage your daily recurring tasks.

## Features

- Morning prompt for finish time on every login
- Auto-reset task checkboxes each new day
- Blinking end-of-day reminder popup
- 優先順位 / task name / clickable link columns + unlimited custom columns
- Check/uncheck via double-click or spacebar
- Auto-start bat file generator (place in Windows Startup folder manually)

---

## Building the EXE with PyInstaller

### 1. Install PyInstaller

```
pip install pyinstaller
```

### 2. Build

Run this from the project folder:

```
pyinstaller --onefile --windowed --name task_manager ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module PIL ^
  --exclude-module scipy ^
  --exclude-module pandas ^
  task_manager.py
```

| Flag | Purpose |
|------|---------|
| `--onefile` | Single exe, no folder |
| `--windowed` | No console window |
| `--exclude-module` | Strip unused heavy packages (reduces size) |

The exe is produced at `dist\task_manager.exe`.

### 3. Optional — further size reduction with UPX

Download UPX from https://upx.github.io and add it to PATH, then add `--upx-dir <path>` to the command above. Typically saves 30–50% on the exe size.

### 4. First run

Copy `dist\task_manager.exe` wherever you want to keep it permanently, then launch it.  
`tasks.json` will be created in the **same folder as the exe**.

### 5. Auto-start on login

Click **⚙ 自動起動** in the toolbar. The app will:
1. Generate `起動_タスク管理.bat` next to the exe
2. Open that folder in Explorer
3. Show you the exact Startup folder to copy it into

Startup folder path:
```
C:\Users\<you>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```
