# SheetStack

**SheetStack** is a lightweight PaperMC server manager that helps you install, manage, and run your Minecraft servers with ease — all from the terminal.

> [!NOTE]
> This tool is intended for power users who are comfortable with shells and CLI/TUI workflows.
> Also, this application requires Python 3.13. Availability: Any system that supports unix-like symlinks.
> (Sorry, Windows users, you must use WSL in this case~)

---

## ✨ Features

### 🔧 Easy Installation

- Quickly install any available PaperMC version.
- No need to manually fetch JARs.

### 📂 Profile Manager

- Manage multiple server versions.
- Switch between versions seamlessly.

### ▶️ Simple Runner

- Launch your active server directly from the TUI.

### 🖥️ Minimalist UI

- Text-based User Interface (TUI).
- No heavy web dashboards or extra memory overhead.

---

## 📥 Installation

The installation process looks like this:

```bash
git clone https://github.com/RimuEirnarn/SheetStack
cd SheetStack

python -m venv .venv
source .venv/bin/activate
pip install -r ./requirements.txt
python main.py # <-- This runs the app
```

The app will prompt you where the server directory should be.

## 📜 License

Licensed under the **BSD 3-Clause "New" or "Revised" License**.
See the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome!
Please check out the [CONTRIBUTING.md](./CONTRIBUTING.md) (coming soon) for guidelines.

---

## 🚀 Roadmap (Planned)

- Plugin manager integration
- Auto-updater for PaperMC builds
- Configurable JVM flags per profile
- Better logging and server monitoring

---
