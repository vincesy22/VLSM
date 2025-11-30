import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import json
import csv
import os
from network import get_ip_info, get_local_ips

try:
    import folium  # optional
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False


class IPInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VLS-EM | Public & Local IP + Geolocation")
        self.root.geometry("600x640")
        self.root.resizable(False, False)
        self.root.config(bg="#e0f2f7")

        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TLabel", font=("Segoe UI", 10), background="#e0f2f7", foreground="#333333")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#e0f2f7", foreground="#004d66")
        style.configure("Subheader.TLabel", font=("Segoe UI", 9, "italic"), background="#e0f2f7", foreground="#004d66")
        style.configure("Field.TLabel", font=("Segoe UI", 10, "bold"), background="#e0f2f7", foreground="#007bff")
        style.configure("Value.TLabel", font=("Segoe UI", 10), background="#e0f2f7", foreground="#555555", wraplength=350)
        style.configure("TButton", font=("Segoe UI", 11, "bold"), background="#28a745", foreground="white", relief="flat")
        style.map("TButton",
                  background=[('active', '#218838'), ('pressed', '#1e7e34')],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        style.configure("TFrame", background="#e0f2f7")
        style.configure("Status.TLabel", font=("Segoe UI", 8, "italic"), background="#e0f2f7", foreground="#6c757d")

        main_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="🌎 VLS-EM IP & Geolocation", style="Header.TLabel", anchor="center")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="ew")

        group_label = ttk.Label(main_frame, text="Shows local IPv4/IPv6 and public IP + geolocation.", style="Subheader.TLabel", anchor="center")
        group_label.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="ew")

        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        self.info_vars = {}
        fields = [
            ("Local IPv4", "local_ipv4"),
            ("Local IPv6", "local_ipv6"),
            ("Public IP", "public_ip"),
            ("IP Version", "version"),
            ("City", "city"),
            ("Region", "region"),
            ("Country", "country"),
            ("Latitude", "latitude"),
            ("Longitude", "longitude"),
            ("Timezone", "timezone"),
            ("ISP / Org", "org"),
            ("ASN", "asn"),
        ]

        for i, (label_text, key) in enumerate(fields):
            label = ttk.Label(main_frame, text=f"{label_text}:", style="Field.TLabel")
            label.grid(row=i + 3, column=0, sticky="w", padx=5, pady=4)
            self.info_vars[key] = tk.StringVar(value="N/A")
            value_label = ttk.Label(main_frame, textvariable=self.info_vars[key], style="Value.TLabel")
            value_label.grid(row=i + 3, column=1, columnspan=2, sticky="w", padx=5, pady=4)

        ttk.Separator(main_frame, orient='horizontal').grid(row=len(fields) + 3, column=0, columnspan=3, sticky="ew", pady=(15, 10))

        fetch_button = ttk.Button(main_frame, text="🚀 Get My IP Info", command=self.start_fetch_thread, style="TButton")
        fetch_button.grid(row=len(fields) + 4, column=0, sticky="ew", padx=3, pady=(0, 8))

        export_csv_button = ttk.Button(main_frame, text="⬇️ Export CSV", command=self.export_csv, style="TButton")
        export_csv_button.grid(row=len(fields) + 4, column=1, sticky="ew", padx=3, pady=(0, 8))

        export_json_button = ttk.Button(main_frame, text="⬇️ Export JSON", command=self.export_json, style="TButton")
        export_json_button.grid(row=len(fields) + 4, column=2, sticky="ew", padx=3, pady=(0, 8))

        map_button = ttk.Button(main_frame, text="🗺️ Show Map", command=self.show_map, style="TButton")
        map_button.grid(row=len(fields) + 5, column=0, columnspan=3, sticky="ew", padx=3, pady=(4, 8))

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="indeterminate")
        self.progress_bar.grid(row=len(fields) + 6, column=0, columnspan=3, pady=(5, 5), sticky="ew")
        self.progress_bar.grid_remove()

        self.status_var = tk.StringVar(value="Ready. Click the button to fetch data.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.grid(row=len(fields) + 7, column=0, columnspan=3, pady=(5, 0), sticky="ew")

        powered_by_label = ttk.Label(main_frame, text="Public data by ipapi.co • Map via folium or Google Maps", font=("Segoe UI", 7, "italic"), background="#e0f2f7", foreground="#999999")
        powered_by_label.grid(row=len(fields) + 8, column=0, columnspan=3, pady=(12, 0), sticky="se")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(2, weight=2)

        # store latest raw data
        self.latest_data = {}

    def update_ui_with_data(self, data: dict):
        # combine fields coming from local + public responses
        self.info_vars["local_ipv4"].set(data.get("local_ipv4", "N/A"))
        self.info_vars["local_ipv6"].set(data.get("local_ipv6", "N/A"))

        self.info_vars["public_ip"].set(data.get("public_ip", data.get("ip", "N/A")))
        self.info_vars["version"].set(data.get("version", "N/A"))
        self.info_vars["city"].set(data.get("city", "N/A"))
        self.info_vars["region"].set(data.get("region", "N/A"))
        country_name = data.get("country_name") or data.get("country", "N/A")
        country_code = data.get("country_code", "")
        if country_code:
            self.info_vars["country"].set(f"{country_name} ({country_code})")
        else:
            self.info_vars["country"].set(country_name)
        self.info_vars["latitude"].set(data.get("latitude", data.get("lat", "N/A")))
        self.info_vars["longitude"].set(data.get("longitude", data.get("lon", "N/A")))
        self.info_vars["timezone"].set(data.get("timezone", "N/A"))
        self.info_vars["org"].set(data.get("org", "N/A"))
        self.info_vars["asn"].set(data.get("asn", "N/A"))
        self.status_var.set("Data updated successfully.")
        self.latest_data = data.copy()

    def fetch_and_display_info(self):
        self.progress_bar.grid()
        self.progress_bar.start()
        self.status_var.set("Fetching data from API and local interfaces...")

        # get local IPs quickly
        local = get_local_ips()
        # get remote / public data
        public = get_ip_info()

        merged = {}
        merged.update(local)
        merged.update(public if isinstance(public, dict) else {})

        self.progress_bar.stop()
        self.progress_bar.grid_remove()

        if isinstance(public, dict) and "error" in public:
            messagebox.showerror("Connection Error", public["error"])
            self.status_var.set("Error! Could not fetch public data.")
            # still display local IPs
            self.update_ui_with_data(merged)
        elif merged:
            self.update_ui_with_data(merged)
        else:
            messagebox.showerror("Error", "Failed to retrieve data.")
            self.status_var.set("Error! No data received.")

    def start_fetch_thread(self):
        thread = threading.Thread(target=self.fetch_and_display_info, daemon=True)
        thread.start()

    def _get_current_record(self) -> dict:
        """
        Return a normalized dictionary for export/map
        """
        d = {
            "local_ipv4": self.info_vars.get("local_ipv4").get(),
            "local_ipv6": self.info_vars.get("local_ipv6").get(),
            "public_ip": self.info_vars.get("public_ip").get(),
            "version": self.info_vars.get("version").get(),
            "city": self.info_vars.get("city").get(),
            "region": self.info_vars.get("region").get(),
            "country": self.info_vars.get("country").get(),
            "latitude": self.info_vars.get("latitude").get(),
            "longitude": self.info_vars.get("longitude").get(),
            "timezone": self.info_vars.get("timezone").get(),
            "org": self.info_vars.get("org").get(),
            "asn": self.info_vars.get("asn").get(),
        }
        return d

    def export_json(self):
        record = self._get_current_record()
        if record["public_ip"] in ("N/A", "") and record["local_ipv4"] in ("N/A", ""):
            messagebox.showwarning("No data", "No IP data to export. Fetch data first.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON file", "*.json")], title="Save as JSON"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            messagebox.showinfo("Exported", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export JSON: {e}")

    def export_csv(self):
        record = self._get_current_record()
        if record["public_ip"] in ("N/A", "") and record["local_ipv4"] in ("N/A", ""):
            messagebox.showwarning("No data", "No IP data to export. Fetch data first.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV file", "*.csv")], title="Save as CSV"
        )
        if not file_path:
            return
        try:
            # write a single-row CSV with headers
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(record.keys()))
                writer.writeheader()
                writer.writerow(record)
            messagebox.showinfo("Exported", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def show_map(self):
        lat = self.info_vars.get("latitude").get()
        lon = self.info_vars.get("longitude").get()
        public_ip = self.info_vars.get("public_ip").get()

        if not lat or lat in ("N/A", "") or not lon or lon in ("N/A", ""):
            messagebox.showwarning("No coordinates", "No latitude/longitude available. Fetch data first.")
            return

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except Exception:
            messagebox.showerror("Invalid coordinates", "Latitude/Longitude are not valid numeric values.")
            return

        # Prefer folium if available
        if FOLIUM_AVAILABLE:
            try:
                m = folium.Map(location=[lat_f, lon_f], zoom_start=10)
                tooltip = f"Public IP: {public_ip}"
                folium.Marker([lat_f, lon_f], popup=tooltip, tooltip=tooltip).add_to(m)
                # Save to a temporary file near current working directory
                path = os.path.join(os.getcwd(), "ip_map.html")
                m.save(path)
                webbrowser.open(f"file://{path}")
                self.status_var.set(f"Map opened in browser (saved to {path})")
                return
            except Exception as e:
                # fallback to google maps
                print("Folium error:", e)

        # Fallback: open Google Maps with lat,lon
        gmaps_url = f"https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}"
        webbrowser.open(gmaps_url)
        self.status_var.set("Opened location in Google Maps.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IPInfoApp(root)
    root.mainloop()
