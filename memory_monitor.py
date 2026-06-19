#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory & Swap Monitor

A Windows GUI application that displays current physical memory and swap
usage along with a real-time history graph, similar to the GNOME Resources
app.

Requirements:
    pip install psutil matplotlib

Run:
    python memory_monitor.py
"""

import tkinter as tk
from tkinter import ttk
from collections import deque
import psutil

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- Settings ----------
UPDATE_INTERVAL_MS = 1000      # Update interval (milliseconds)
HISTORY_SECONDS = 60            # How many seconds of history to keep
BG_COLOR = "#1e1e1e"
FG_COLOR = "#e0e0e0"
MEM_COLOR = "#4fc3f7"
SWAP_COLOR = "#ff8a65"
GRID_COLOR = "#3a3a3a"


def bytes_to_gib(value_bytes: float) -> float:
    return value_bytes / (1024 ** 3)


class MemoryMonitorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Memory & Swap Monitor")
        self.root.geometry("760x520")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(560, 420)

        # History data (percentages)
        self.mem_history = deque([0.0] * HISTORY_SECONDS, maxlen=HISTORY_SECONDS)
        self.swap_history = deque([0.0] * HISTORY_SECONDS, maxlen=HISTORY_SECONDS)

        self._build_style()
        self._build_top_labels()
        self._build_chart()

        self.update_stats()

    # ---------------- UI construction ----------------
    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG_COLOR)
        style.configure(
            "Title.TLabel",
            background=BG_COLOR,
            foreground=FG_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Value.TLabel",
            background=BG_COLOR,
            foreground=FG_COLOR,
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Sub.TLabel",
            background=BG_COLOR,
            foreground="#9e9e9e",
            font=("Segoe UI", 9),
        )

    def _build_top_labels(self):
        top = ttk.Frame(self.root, style="TFrame")
        top.pack(fill="x", padx=20, pady=(16, 8))

        # Memory display block
        mem_block = ttk.Frame(top, style="TFrame")
        mem_block.pack(side="left", expand=True, fill="x")

        mem_title = ttk.Label(mem_block, text="● Physical Memory", style="Title.TLabel")
        mem_title.configure(foreground=MEM_COLOR)
        mem_title.pack(anchor="w")

        self.mem_value_label = ttk.Label(mem_block, text="--%", style="Value.TLabel")
        self.mem_value_label.pack(anchor="w")

        self.mem_detail_label = ttk.Label(mem_block, text="-- / -- GiB", style="Sub.TLabel")
        self.mem_detail_label.pack(anchor="w")

        # Swap display block
        swap_block = ttk.Frame(top, style="TFrame")
        swap_block.pack(side="left", expand=True, fill="x")

        swap_title = ttk.Label(swap_block, text="● Swap", style="Title.TLabel")
        swap_title.configure(foreground=SWAP_COLOR)
        swap_title.pack(anchor="w")

        self.swap_value_label = ttk.Label(swap_block, text="--%", style="Value.TLabel")
        self.swap_value_label.pack(anchor="w")

        self.swap_detail_label = ttk.Label(swap_block, text="-- / -- GiB", style="Sub.TLabel")
        self.swap_detail_label.pack(anchor="w")

    def _build_chart(self):
        chart_frame = ttk.Frame(self.root, style="TFrame")
        chart_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        self.fig = Figure(figsize=(7, 4), dpi=100, facecolor=BG_COLOR)
        self.ax = self.fig.add_subplot(111)
        self._style_axes()

        x = list(range(-HISTORY_SECONDS + 1, 1))
        (self.mem_line,) = self.ax.plot(
            x, list(self.mem_history), color=MEM_COLOR, linewidth=2, label="Physical Memory"
        )
        (self.swap_line,) = self.ax.plot(
            x, list(self.swap_history), color=SWAP_COLOR, linewidth=2, label="Swap"
        )
        self.ax.fill_between(x, list(self.mem_history), color=MEM_COLOR, alpha=0.15)
        self.ax.fill_between(x, list(self.swap_history), color=SWAP_COLOR, alpha=0.15)

        self.ax.legend(
            loc="upper left",
            facecolor=BG_COLOR,
            edgecolor=GRID_COLOR,
            labelcolor=FG_COLOR,
            fontsize=9,
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _style_axes(self):
        self.ax.set_facecolor(BG_COLOR)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(-HISTORY_SECONDS + 1, 0)
        self.ax.set_xlabel(f"Last {HISTORY_SECONDS} seconds", color=FG_COLOR, fontsize=9)
        self.ax.set_ylabel("Usage (%)", color=FG_COLOR, fontsize=9)
        self.ax.tick_params(colors=FG_COLOR, labelsize=8)
        self.ax.grid(True, color=GRID_COLOR, linewidth=0.6)
        for spine in self.ax.spines.values():
            spine.set_color(GRID_COLOR)

    # ---------------- Data update ----------------
    def update_stats(self):
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()

        self.mem_history.append(vm.percent)
        self.swap_history.append(sm.percent)

        # Update labels
        self.mem_value_label.configure(text=f"{vm.percent:.1f}%")
        self.mem_detail_label.configure(
            text=f"{bytes_to_gib(vm.used):.1f} / {bytes_to_gib(vm.total):.1f} GiB"
        )

        self.swap_value_label.configure(text=f"{sm.percent:.1f}%")
        self.swap_detail_label.configure(
            text=f"{bytes_to_gib(sm.used):.1f} / {bytes_to_gib(sm.total):.1f} GiB"
        )

        # Update chart
        x = list(range(-HISTORY_SECONDS + 1, 1))
        self.mem_line.set_data(x, list(self.mem_history))
        self.swap_line.set_data(x, list(self.swap_history))

        # fill_between needs to be regenerated each time
        for coll in list(self.ax.collections):
            coll.remove()
        self.ax.fill_between(x, list(self.mem_history), color=MEM_COLOR, alpha=0.15)
        self.ax.fill_between(x, list(self.swap_history), color=SWAP_COLOR, alpha=0.15)

        self.canvas.draw_idle()

        self.root.after(UPDATE_INTERVAL_MS, self.update_stats)


def main():
    root = tk.Tk()
    app = MemoryMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
