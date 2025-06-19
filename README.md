# 🚀 AutoCleaner

**AutoCleaner** is a sleek, fast, and feature-packed file organization tool  
that helps you keep your directories clean — effortlessly.

---

## ✨ Features

- 📁 Scans specified directories for files  
- 🧠 Categorizes files by extension  
- 📒 Sorts files into neatly organized folders  
- 👀 Preview changes before applying them  
- 📊 Generates detailed reports of what was organized  

---

## 🔧 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/borgox/AutoCleaner.git
   ```

2. Navigate to the project directory:

   ```bash
   cd AutoCleaner
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Usage

Run the app and pass one or more folders:
⚠️MAKE SURE YOUR TERMINAL IS SET TO USE UTF-8 CHARMAP (`chcp 65001` on windows⚠️
```bash
python src/main.py [folders] [options]
```

### ⚙️ Options

| Option            | Description |
|-------------------|-------------|
| `--dry-run`       | Simulates changes without moving files |
| `--auto-organize` | Automatically resolves ambiguous file types |
| `--no-backup`     | Skips backup creation |
| `--delete-empty`  | Removes empty folders after sorting |
| `--log-level`     | Sets log verbosity (`DEBUG`, `INFO`, etc.) |

---

## 🤝 Contributing

Got an idea or fix? Open an [issue](https://github.com/borgox/AutoCleaner/issues) or submit a pull request 🚀

---

## 📄 License

Licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---
