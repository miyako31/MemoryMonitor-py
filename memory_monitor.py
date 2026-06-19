#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory & Swap Monitor (lightweight, no matplotlib)

A Windows GUI application that displays current physical memory and swap
usage along with a real-time history graph, similar to the GNOME Resources
app. The graph is drawn with plain tkinter Canvas drawing primitives, so
there is no dependency on matplotlib/numpy. This keeps the packaged .exe
much smaller (roughly 8-12 MiB instead of ~38 MiB).

Requirements:
    pip install psutil

Run:
    python memory_monitor.py
"""

import tkinter as tk
from tkinter import ttk
from collections import deque
import psutil

# ---------- Settings ----------
UPDATE_INTERVAL_MS = 1000      # Update interval (milliseconds)
HISTORY_SECONDS = 60            # How many seconds of history to keep
BG_COLOR = "#1e1e1e"
FG_COLOR = "#e0e0e0"
SUB_COLOR = "#9e9e9e"
GRID_COLOR = "#3a3a3a"
MEM_COLOR = "#4fc3f7"
SWAP_COLOR = "#ff8a65"


def bytes_to_gib(value_bytes: float) -> float:
    return value_bytes / (1024 ** 3)


class GraphCanvas(tk.Canvas):
    """A minimal self-drawn line-chart widget (0-100% on the Y axis)."""

    PAD_LEFT = 40
    PAD_RIGHT = 12
    PAD_TOP = 14
    PAD_BOTTOM = 24

    def __init__(self, master, history_len: int, **kwargs):
        super().__init__(master, bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.history_len = history_len
        self.bind("<Configure>", lambda _e: self.redraw())
        self._mem_data = [0.0] * history_len
        self._swap_data = [0.0] * history_len

    def update_data(self, mem_data, swap_data):
        self._mem_data = list(mem_data)
        self._swap_data = list(swap_data)
        self.redraw()

    # ---- internal helpers ----
    def _plot_area(self):
        w = self.winfo_width()
        h = self.winfo_height()
        x0 = self.PAD_LEFT
        y0 = self.PAD_TOP
        x1 = max(x0 + 10, w - self.PAD_RIGHT)
        y1 = max(y0 + 10, h - self.PAD_BOTTOM)
        return x0, y0, x1, y1

    def _to_xy(self, index, value, x0, y0, x1, y1):
        n = self.history_len
        x = x0 + (x1 - x0) * (index / max(1, n - 1))
        y = y1 - (y1 - y0) * (max(0.0, min(100.0, value)) / 100.0)
        return x, y

    def redraw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return

        x0, y0, x1, y1 = self._plot_area()

        # Grid lines + Y axis labels (0/25/50/75/100 %)
        for pct in (0, 25, 50, 75, 100):
            _, y = self._to_xy(0, pct, x0, y0, x1, y1)
            self.create_line(x0, y, x1, y, fill=GRID_COLOR, width=1)
            self.create_text(
                x0 - 6, y, text=f"{pct}%", fill=SUB_COLOR, anchor="e", font=("Segoe UI", 8)
            )

        # X axis label
        self.create_text(
            (x0 + x1) / 2, y1 + 14,
            text=f"Last {self.history_len} seconds",
            fill=SUB_COLOR, font=("Segoe UI", 8),
        )

        # Plot lines
        self._draw_series(self._mem_data, MEM_COLOR, x0, y0, x1, y1)
        self._draw_series(self._swap_data, SWAP_COLOR, x0, y0, x1, y1)

        # Legend
        legend_x, legend_y = x0 + 8, y0 + 6
        self.create_line(legend_x, legend_y, legend_x + 18, legend_y, fill=MEM_COLOR, width=3)
        self.create_text(
            legend_x + 24, legend_y, text="Physical Memory", fill=FG_COLOR,
            anchor="w", font=("Segoe UI", 8),
        )
        self.create_line(legend_x + 150, legend_y, legend_x + 168, legend_y, fill=SWAP_COLOR, width=3)
        self.create_text(
            legend_x + 174, legend_y, text="Swap", fill=FG_COLOR,
            anchor="w", font=("Segoe UI", 8),
        )

    def _draw_series(self, data, color, x0, y0, x1, y1):
        points = []
        for i, v in enumerate(data):
            x, y = self._to_xy(i, v, x0, y0, x1, y1)
            points.extend([x, y])
        if len(points) >= 4:
            self.create_line(*points, fill=color, width=2, smooth=False)


class MemoryMonitorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Memory & Swap Monitor")
        self.root.geometry("760x520")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(560, 380)

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
            "Title.TLabel", background=BG_COLOR, foreground=FG_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Value.TLabel", background=BG_COLOR, foreground=FG_COLOR,
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Sub.TLabel", background=BG_COLOR, foreground=SUB_COLOR,
            font=("Segoe UI", 9),
        )

    def _build_top_labels(self):
        top = ttk.Frame(self.root, style="TFrame")
        top.pack(fill="x", padx=20, pady=(16, 8))

        mem_block = ttk.Frame(top, style="TFrame")
        mem_block.pack(side="left", expand=True, fill="x")
        mem_title = ttk.Label(mem_block, text="● Physical Memory", style="Title.TLabel")
        mem_title.configure(foreground=MEM_COLOR)
        mem_title.pack(anchor="w")
        self.mem_value_label = ttk.Label(mem_block, text="--%", style="Value.TLabel")
        self.mem_value_label.pack(anchor="w")
        self.mem_detail_label = ttk.Label(mem_block, text="-- / -- GiB", style="Sub.TLabel")
        self.mem_detail_label.pack(anchor="w")

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
        self.graph = GraphCanvas(chart_frame, history_len=HISTORY_SECONDS)
        self.graph.pack(fill="both", expand=True)

    # ---------------- Data update ----------------
    def update_stats(self):
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()

        self.mem_history.append(vm.percent)
        self.swap_history.append(sm.percent)

        self.mem_value_label.configure(text=f"{vm.percent:.1f}%")
        self.mem_detail_label.configure(
            text=f"{bytes_to_gib(vm.used):.1f} / {bytes_to_gib(vm.total):.1f} GiB"
        )
        self.swap_value_label.configure(text=f"{sm.percent:.1f}%")
        self.swap_detail_label.configure(
            text=f"{bytes_to_gib(sm.used):.1f} / {bytes_to_gib(sm.total):.1f} GiB"
        )

        self.graph.update_data(self.mem_history, self.swap_history)

        self.root.after(UPDATE_INTERVAL_MS, self.update_stats)


def main():
    root = tk.Tk()
    MemoryMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
