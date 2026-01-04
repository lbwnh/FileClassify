# FileClassify

一个基于 PyQt6 的 Windows 文件分类工具。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python src/main.py
```

## 编译成 .exe 可执行文件

### 方法 1：使用批处理脚本（推荐）
双击运行 `build.bat` 文件，或在命令行中执行：
```bash
build.bat
```

### 方法 2：手动编译
```bash
pip install pyinstaller
pyinstaller --name=FileClassify --windowed --onefile src/main.py
```

编译完成后，可执行文件位于 `dist/FileClassify.exe`