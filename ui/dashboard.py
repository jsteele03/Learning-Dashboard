import tkinter as tk
from tkinter import ttk

from data.macro_data import get_macro_snapshot

class MacroDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("US Macro Dashboard")
        self.geometry("900x600")
        self.configure(bg="#f5f5f5")

        # Store references to value labels
        self.value_labels = {}

        self.create_layout()
        self.populate_macro_column()
        self.refresh_macro_data()

    def create_layout(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Left: Macro column
        self.macro_frame = ttk.Frame(self.main_frame, width=300)
        self.macro_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.macro_frame.pack_propagate(False)

        # Right: Placeholder
        self.other_frame = ttk.Frame(self.main_frame)
        self.other_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(
            self.other_frame,
            text="Your Other Data Goes Here",
            font=("Helvetica", 14)
        ).pack(anchor="center", pady=20)

    def populate_macro_column(self):
        title = ttk.Label(
            self.macro_frame,
            text="US Macro Indicators",
            font=("Helvetica", 14, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))

        for name in get_macro_snapshot().keys():
            self.add_indicator_row(name)

    def add_indicator_row(self, name):
        frame = ttk.Frame(self.macro_frame)
        frame.pack(fill="x", pady=4)

        label = ttk.Label(frame, text=name)
        label.pack(side="left")

        value_label = ttk.Label(frame, text="—", font=("Helvetica", 10, "bold"))
        value_label.pack(side="right")

        self.value_labels[name] = value_label

    def refresh_macro_data(self):
        data = get_macro_snapshot()

        for name, value in data.items():
            label = self.value_labels.get(name)
            if label:
                if value is None:
                    label.config(text="—")
                else:
                    label.config(text=f"{value:.2f}")

if __name__ == "__main__":
    app = MacroDashboard()
    app.mainloop()
