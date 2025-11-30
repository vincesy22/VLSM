import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
from network import get_ip_info

class IPInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VLS-EM | Public IP and Geolocation Finder")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        self.root.config(bg="#e0f2f7")

        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TLabel", font=("Segoe UI", 10), background="#e0f2f7", foreground="#333333")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#e0f2f7", foreground="#004d66")
        style.configure("Subheader.TLabel", font=("Segoe UI", 9, "italic"), background="#e0f2f7", foreground="#004d66")
        style.configure("Field.TLabel", font=("Segoe UI", 10, "bold"), background="#e0f2f7", foreground="#007bff")
        style.configure("Value.TLabel", font=("Segoe UI", 10), background="#e0f2f7", foreground="#555555", wraplength=300)
        style.configure("TButton", font=("Segoe UI", 11, "bold"), background="#28a745", foreground="white", relief="flat")
        style.map("TButton",
                  background=[('active', '#218838'), ('pressed', '#1e7e34')],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        style.configure("TFrame", background="#e0f2f7")
        style.configure("Status.TLabel", font=("Segoe UI", 8, "italic"), background="#e0f2f7", foreground="#6c757d")

        main_frame = ttk.Frame(self.root, padding="25", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="🌎 VLS-EM Public IP Finder", style="Header.TLabel", anchor="center")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        group_label = ttk.Label(main_frame, text="Get your current IPV4/IPV6 address in an instant!", style="Subheader.TLabel", anchor="center")
        group_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        self.info_vars = {}
        self.map_file = None
        fields = [
            "IPv4 Address", "Version", "City", "Region", "Country",
            "Latitude", "Longitude", "Timezone", "ISP", "ASN"
        ]

        for i, field in enumerate(fields):
            label = ttk.Label(main_frame, text=f"{field}:", style="Field.TLabel")
            label.grid(row=i + 3, column=0, sticky="w", padx=5, pady=4)
            self.info_vars[field] = tk.StringVar(value="N/A")
            value_label = ttk.Label(main_frame, textvariable=self.info_vars[field], style="Value.TLabel")
            value_label.grid(row=i + 3, column=1, sticky="w", padx=5, pady=4)

        ttk.Separator(main_frame, orient='horizontal').grid(row=len(fields) + 3, column=0, columnspan=2, sticky="ew", pady=(15, 15))

        fetch_button = ttk.Button(main_frame, text="🚀 Get My IP Info", command=self.start_fetch_thread, style="TButton")
        fetch_button.grid(row=len(fields) + 4, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.map_button = ttk.Button(main_frame, text="🗺️ View Map", command=self.open_map, style="TButton")
        self.map_button.grid(row=len(fields) + 5, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        self.map_button.grid_remove()  # Hide initially

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="indeterminate")
        self.progress_bar.grid(row=len(fields) + 6, column=0, columnspan=2, pady=(5, 5), sticky="ew")
        self.progress_bar.grid_remove()

        self.status_var = tk.StringVar(value="Ready. Click the button to fetch data.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.grid(row=len(fields) + 7, column=0, columnspan=2, pady=(5, 0), sticky="ew")

        powered_by_label = ttk.Label(main_frame, text="Data provided by ipapi.co", font=("Segoe UI", 7, "italic"), background="#e0f2f7", foreground="#999999")
        powered_by_label.grid(row=len(fields) + 8, column=0, columnspan=2, pady=(10, 0), sticky="se")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

    def update_ui_with_data(self, data):
        self.info_vars["IPv4 Address"].set(data.get('ip', 'N/A'))
        self.info_vars["Version"].set(data.get('version', 'N/A'))
        self.info_vars["City"].set(data.get('city', 'N/A'))
        self.info_vars["Region"].set(data.get('region', 'N/A'))
        country_name = data.get('country_name', 'N/A')
        country_code = data.get('country_code', 'N/A')
        self.info_vars["Country"].set(f"{country_name} ({country_code})")
        self.info_vars["Latitude"].set(data.get('latitude', 'N/A'))
        self.info_vars["Longitude"].set(data.get('longitude', 'N/A'))
        self.info_vars["Timezone"].set(data.get('timezone', 'N/A'))
        self.info_vars["ISP"].set(data.get('org', 'N/A'))
        self.info_vars["ASN"].set(data.get('asn', 'N/A'))
        self.map_file = data.get('map_file')
        if self.map_file:
            self.map_button.grid()
        else:
            self.map_button.grid_remove()
        self.status_var.set("Data updated successfully.")

    def fetch_and_display_info(self):
        self.progress_bar.grid()
        self.progress_bar.start()
        self.status_var.set("Fetching data from API...")

        data = get_ip_info()

        self.progress_bar.stop()
        self.progress_bar.grid_remove()

        if data and "error" in data:
            messagebox.showerror("Connection Error", data["error"])
            self.status_var.set("Error! Could not fetch data.")
        elif data:
            self.update_ui_with_data(data)
        else:
            messagebox.showerror("Error", "Failed to retrieve data. No response from network.")
            self.status_var.set("Error! No data received.")

    def start_fetch_thread(self):
        thread = threading.Thread(target=self.fetch_and_display_info, daemon=True)
        thread.start()

    def open_map(self):
        if self.map_file:
            webbrowser.open(self.map_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPInfoApp(root)
    root.mainloop()

