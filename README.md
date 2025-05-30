# RePrompt – Repository-Context Generator

**RePrompt** creates a single `repo-context.txt` file that gives AI coding assistants
(e.g. ChatGPT) a concise, opinionated snapshot of your repository.  
It combines an overview, directory tree, highlighted file contents, and optional static
sections such as to-do lists—all configurable through a Streamlit UI.

> **Works great with**  
> [mckaywrigley’s XML parser](https://github.com/mckaywrigley/o1-xml-parser/tree/main).

---

## ✨ Features

| Category | What it does |
|----------|--------------|
| **Streamlit UI** | Choose a target repo, set include/exclude rules, and generate the context file in one screen. |
| **Context builder** | Produces `repo-context.txt` tailored for AI assistants. |
| **Configurable tree** | Exclude or include directories/files interactively (defaults skip noisy folders like `node_modules`, `.git`, etc.). |
| **File highlights** | Embeds syntax-highlighted contents of “important” files you pick. |
| **Static sections** | Auto-appends `overview.txt`, `to-do_list.txt`, or any custom text snippets. |
| **Save & load config** | Persist your include/exclude selections for future sessions. |

---

## 🛠 Prerequisites

* **Python 3.7 +** – [download](https://www.python.org/downloads/)  
* **Git** – [download](https://git-scm.com/downloads)

---

## 🗂 Directory layout

```

RePrompt/
├── src/
│   ├── app.py                   # Streamlit entry-point
│   ├── generate\_repo\_context.py # Core context-builder
│   ├── config.yaml              # Default config (auto-generated if absent)
│   ├── index.html               # Single-page static explanation
│   └── requirements.txt         # Python dependencies
└── README.md

````

---

## 🚀 Installation

### 1  Clone the repo

```bash
git clone https://github.com/PR0M3TH3AN/RePrompt.git
cd RePrompt
````

### 2  Create & activate a virtual-environment

<details>
<summary>Windows (PowerShell)</summary>

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

</details>

<details>
<summary>macOS / Linux</summary>

```bash
python3 -m venv venv
source venv/bin/activate
```

</details>

### 3  Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

`requirements.txt` contains only three packages:

```text
streamlit
PyYAML
pyperclip
```

---

## ▶️ Running the app

```bash
streamlit run src/app.py
```

The UI opens at **[http://localhost:8501](http://localhost:8501)**.

---

## 📝 Usage walk-through

1. **Config file**
   A starter `config.yaml` is created in `src/`:

   ```yaml
   exclude_dirs:
     - node_modules
     - venv
     - __pycache__
     - .git
     - dist
     - build
     - logs
     - .idea
     - .vscode

   important_files: []
   custom_sections: []
   ```

2. **Select repo**
   Click **“Choose Folder”** in the sidebar, navigate to the repository you
   want to summarise, and select it.

3. **Fine-tune files**

   * Tick directories to *include* in the rendered tree.
   * Exclude noisy or irrelevant files.
   * Review the final list.

4. **Generate**
   Hit **“Generate Context File”**.
   Download or copy the result; optionally save the configuration for later.

---

## 🔧 Customisation tips

### Change default exclusions

Edit these constants in `src/app.py`:

```python
DEFAULT_EXCLUDED_DIRS = [
    "node_modules", "venv", "__pycache__", ".git",
    "dist", "build", "logs", ".idea", ".vscode"
]
DEFAULT_EXCLUDED_FILES = ["repo-context.txt"]
```

### Different port

If port 8501 is busy:

```bash
streamlit run src/app.py --server.port 8502
```

---

## ❓ Troubleshooting

| Problem                                | Fix                                                           |
| -------------------------------------- | ------------------------------------------------------------- |
| `Tcl_AsyncDelete` warning              | Harmless—ignore it.                                           |
| “Permission denied” when creating dirs | Run your terminal as admin or check folder write permissions. |
| Packages won’t install                 | `python -m pip install --upgrade pip` then reinstall.         |
| Port already in use                    | Kill other Streamlit processes or use `--server.port`.        |

---

## 🤝 Contributing

1. Fork → create a feature branch
2. Commit & push your changes
3. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License** – see `LICENSE` for details.
