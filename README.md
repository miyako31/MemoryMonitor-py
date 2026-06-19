# MemoryMonitor-py

**Memory & Swap Monitor** — a lightweight Windows desktop widget that shows
real-time physical memory and swap usage together with a 60-second history
graph. Inspired by the GNOME *Resources* app, but built with plain `tkinter`
Canvas drawing so the packaged `.exe` stays tiny (≈ 8–12 MiB instead of
≈ 38 MiB when using matplotlib).

> ⚠️ **Disclaimer — please read before using.**
>
> Every line of source code in this repository was generated **entirely by
> Claude Sonnet 4.6** (an Anthropic large language model) without any
> hand-written edits. The project is published for reference and educational
> purposes only.
>
> **The software is provided "AS IS", without warranty of any kind, express or
> implied, including but not limited to the warranties of merchantability,
> fitness for a particular purpose, and non-infringement.** There is **no
> guarantee that the program will operate correctly**, and the author
> **assumes no responsibility whatsoever for any damages or data loss**
> (direct, indirect, incidental, consequential, or otherwise) arising from the
> use of, or inability to use, this software. Use it at your own risk.

---

## ✨ Features

- **Real-time monitoring** of physical memory and swap usage, updated every
  second.
- **Self-drawn history graph** (last 60 seconds) rendered with native
  `tkinter` Canvas primitives — no `matplotlib`, no `numpy`.
- **Compact footprint** — packaged binary is roughly one-third the size of a
  matplotlib-based equivalent.
- **Dark theme UI** inspired by modern system resource monitors.
- **Single-file application** — `memory_monitor.py` is the whole program.
- **Cross-process safe** — read-only metrics via `psutil`, does not modify any
  system state.

## 📷 UI Overview

```
┌──────────────────────────────────────────────────────┐
│  ● Physical Memory        ● Swap                     │
│  42.3%                    1.2%                       │
│  6.7 / 15.9 GiB           0.1 / 8.0 GiB             │
│                                                      │
│  100% ┤                                              │
│   75% ┤        ──────── Physical Memory              │
│   50% ┤   ──── ──────  ── Swap                       │
│   25% ┤ ──      ──                                     │
│    0% └────────────────────────────────────────────  │
│             Last 60 seconds                          │
└──────────────────────────────────────────────────────┘
```

## 🧰 Requirements

- **OS:** Windows 10 / 11 (Tk is bundled with the official CPython installer)
- **Python:** 3.8 or newer
- **Dependencies:** [`psutil`](https://pypi.org/project/psutil/) only

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/miyako31/MemoryMonitor-py.git
cd MemoryMonitor-py

# 2. (Optional) create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux

# 3. Install the single runtime dependency
pip install psutil
```

## 🖥️ Usage

Run the GUI:

```bash
python memory_monitor.py
```

The window will open at **760 × 520** (minimum 560 × 380) and refresh once
per second. Resize the window freely — the canvas redraws itself to fit.

### Building a standalone `.exe` (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MemoryMonitor memory_monitor.py
# The binary will be in dist\MemoryMonitor.exe
```

## ⚙️ Configuration

All tunable parameters live at the top of `memory_monitor.py`:

| Constant              | Default | Description                          |
|-----------------------|---------|--------------------------------------|
| `UPDATE_INTERVAL_MS`  | `1000`  | Refresh interval in milliseconds.    |
| `HISTORY_SECONDS`     | `60`    | Number of seconds kept in the graph. |
| `BG_COLOR`            | `#1e1e1e` | Window background.                 |
| `MEM_COLOR`           | `#4fc3f7` | Physical-memory line color.        |
| `SWAP_COLOR`          | `#ff8a65` | Swap line color.                   |

## 🗂️ Project Structure

```
MemoryMonitor-py/
├── memory_monitor.py     # The whole application (GUI + graph + polling)
├── LICENSE               # GNU GPL v3
└── README.md             # This file
```

## 📜 License

This project is licensed under the **GNU General Public License v3.0** — see
[`LICENSE`](LICENSE) for the full text.

## 🤖 Authorship & Attribution

- **Code author:** Claude Sonnet 4.6 (large language model by Anthropic)
- **Prompt engineering & repository ownership:** [`miyako31`](https://github.com/miyako31)
- **No human-written source code** is present in this repository; every line
  was produced by the AI model and accepted as-is.

## ⚖️ Disclaimer (full text)

The author provides this software "AS IS" and makes **no representations or
warranties of any kind** concerning the software, express, implied, statutory
or otherwise, including without limitation warranties of title,
merchantability, fitness for a particular purpose, non-infringement, or the
absence of latent or other defects, accuracy, or the presence or absence of
errors, whether or not discoverable.

In no event will the author be **liable for any direct, indirect, special,
incidental, consequential, punitive, or exemplary damages**, including but
not limited to **data loss or data corruption**, loss of profits, loss of
business, or loss of opportunity, arising out of or in connection with the
use of, or inability to use, this software, even if advised of the
possibility of such damages.

Because the source code was generated entirely by an AI language model, it
may contain **bugs, logical errors, security vulnerabilities, or
platform-specific issues** that have not been reviewed by a human engineer.
You are solely responsible for verifying the safety and suitability of this
software before running it on any production or critical system.
