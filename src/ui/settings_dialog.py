import tkinter as tk
from tkinter import ttk, messagebox
from core.preferences import PreferenceManager

class SettingsDialog(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Settings")
        self.pref_mgr = PreferenceManager.get_instance()
        self._build_ui()

    def _build_ui(self):
        # Example: Theme
        tk.Label(self, text="Theme:").grid(row=0, column=0, sticky="w")
        self.theme_var = tk.StringVar(value=self.pref_mgr.get("theme"))
        theme_menu = ttk.Combobox(self, textvariable=self.theme_var, values=["light", "dark"])
        theme_menu.grid(row=0, column=1)

        # Example: Auto Update
        tk.Label(self, text="Auto Update:").grid(row=1, column=0, sticky="w")
        self.auto_update_var = tk.BooleanVar(value=self.pref_mgr.get("auto_update"))
        tk.Checkbutton(self, variable=self.auto_update_var).grid(row=1, column=1)

        # Example: Refresh Interval
        tk.Label(self, text="Refresh Interval (min):").grid(row=2, column=0, sticky="w")
        self.refresh_var = tk.IntVar(value=self.pref_mgr.get("refresh_interval"))
        tk.Spinbox(self, from_=5, to=60, textvariable=self.refresh_var).grid(row=2, column=1)

        # Save/Cancel buttons
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Save", command=self.save).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def save(self):
        # TODO: Validate and save preferences
        try:
            self.pref_mgr.set("theme", self.theme_var.get())
            self.pref_mgr.set("auto_update", self.auto_update_var.get())
            self.pref_mgr.set("refresh_interval", self.refresh_var.get())
            self.pref_mgr.save_preferences()
            self.pref_mgr.notify_observers()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
