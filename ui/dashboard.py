import tkinter as tk
from tkinter import ttk
import threading
import sv_ttk

from data.macro_data import (
    real_gdp_growth,
    nominal_gdp_growth,
    unemployment_rate,
    prime_age_employment_ratio,
    payroll_employment_change,
    core_pce_yoy,
    wage_growth_yoy,
    yield_curve_3m_10y,
    credit_spread_high_yield,
    financial_conditions_index,
)

class MacroDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        # Enable dark mode
        sv_ttk.set_theme("dark")

        self.title("US Macro Dashboard")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        # Store row IDs for updating values
        self.row_ids = {}

        self.create_layout()
        self.populate_table()
        self.load_macro_data_async()

    def create_layout(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Table frame
        self.table_frame = ttk.Frame(self.main_frame, width=400)
        self.table_frame.pack(side="left", fill="both", expand=True)
        self.table_frame.pack_propagate(False)

        # Treeview for macro indicators
        self.tree = ttk.Treeview(
            self.table_frame,
            columns=("Indicator", "Value"),
            show="headings",
            height=15
        )
        self.tree.heading("Indicator", text="Indicator")
        self.tree.heading("Value", text="Value")
        self.tree.column("Indicator", width=250, anchor="w")
        self.tree.column("Value", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Right: Placeholder
        self.other_frame = ttk.Frame(self.main_frame)
        self.other_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(
            self.other_frame,
            text="Your Other Data Goes Here",
            font=("Helvetica", 14)
        ).pack(anchor="center", pady=20)

    def populate_table(self):
        # Define indicators as (label, function) pairs
        self.indicators = [
            ("Real GDP Growth (%)", real_gdp_growth),
            ("Nominal GDP Growth (%)", nominal_gdp_growth),
            ("Unemployment Rate (%)", unemployment_rate),
            ("Prime-Age E/P Ratio (%)", prime_age_employment_ratio),
            ("Payroll Change (k)", payroll_employment_change),
            ("Core PCE YoY (%)", core_pce_yoy),
            ("Wage Growth YoY (%)", wage_growth_yoy),
            ("Yield Curve 3m–10y", yield_curve_3m_10y),
            ("High-Yield Spread", credit_spread_high_yield),
            ("Financial Conditions Index", financial_conditions_index),
        ]

        # Insert each indicator as a row with placeholder value
        for name, _ in self.indicators:
            row_id = self.tree.insert("", "end", values=(name, "..."))
            self.row_ids[name] = row_id

    def load_macro_data_async(self):
        """Fetch macro data per indicator in a background thread."""
        threading.Thread(target=self._load_macro_data, daemon=True).start()

    def _load_macro_data(self):
        for name, func in self.indicators:
            try:
                value = func()
                display = f"{value:.2f}" if value is not None else "Error"
            except Exception:
                display = "Error"

            # Update Treeview row on the main thread
            self.after(0, lambda n=name, d=display: self.tree.item(self.row_ids[n], values=(n, d)))


if __name__ == "__main__":
    app = MacroDashboard()
    app.mainloop()
