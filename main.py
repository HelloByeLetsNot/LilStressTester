import tkinter as tk
from tkinter import ttk
from ttkthemes import themed_tk as tktheme
import threading
import requests
import socket
import subprocess
import whois
import stem.process

class NetworkUtilityApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lil Stresser Tester")

        self.create_widgets()

    def create_widgets(self):
        self.label_url = ttk.Label(self.master, text="Enter website URL:")
        self.label_url.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.url_entry = ttk.Entry(self.master, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

        self.whois_button = ttk.Button(self.master, text="WHOIS Lookup", command=self.perform_whois_lookup)
        self.whois_button.grid(row=0, column=3, padx=10, pady=5)

        self.ping_button = ttk.Button(self.master, text="Ping", command=self.perform_ping)
        self.ping_button.grid(row=0, column=4, padx=10, pady=5)

        self.ip_button = ttk.Button(self.master, text="Get IP Address", command=self.get_ip_address)
        self.ip_button.grid(row=0, column=5, padx=10, pady=5)

        self.scan_button = ttk.Button(self.master, text="Directory Scan", command=self.start_directory_scan)
        self.scan_button.grid(row=0, column=6, padx=10, pady=5)

        self.tor_start_button = ttk.Button(self.master, text="Start Tor", command=self.start_tor)
        self.tor_start_button.grid(row=1, column=0, padx=10, pady=5)

        self.tor_connections_label = ttk.Label(self.master, text="Number of Tor connections:")
        self.tor_connections_label.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.tor_connections_entry = ttk.Entry(self.master)
        self.tor_connections_entry.grid(row=1, column=2, padx=10, pady=5)

        self.tor_stress_test_button = ttk.Button(self.master, text="Start Tor Stress Test", command=self.start_tor_stress_test)
        self.tor_stress_test_button.grid(row=1, column=3, padx=10, pady=5)

        self.output_text = tk.Text(self.master, height=15, width=70)
        self.output_text.grid(row=2, column=0, columnspan=7, padx=10, pady=5)

    def perform_whois_lookup(self):
        website_url = self.url_entry.get()
        try:
            whois_info = whois.whois(website_url)
            self.output_text.insert(tk.END, f"WHOIS Information for {website_url}:\n")
            self.output_text.insert(tk.END, whois_info)
            self.output_text.insert(tk.END, "\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred during WHOIS lookup: {str(e)}\n")

    def perform_ping(self):
        website_url = self.url_entry.get()
        try:
            result = subprocess.run(['ping', '-n', '4', website_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.output_text.insert(tk.END, f"Ping Result for {website_url}:\n")
            self.output_text.insert(tk.END, result.stdout.decode())
            self.output_text.insert(tk.END, result.stderr.decode())
            self.output_text.insert(tk.END, "\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred during Ping: {str(e)}\n")

    def get_ip_address(self):
        website_url = self.url_entry.get()
        try:
            ip_address = socket.gethostbyname(website_url)
            self.output_text.insert(tk.END, f"IP Address for {website_url}: {ip_address}\n")
        except socket.gaierror as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            self.output_text.insert(tk.END, f"Failed to retrieve IP address for {website_url}. Please check the hostname and try again.\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred while retrieving IP address: {str(e)}\n")

    def fetch_wordlist(self):
        try:
            response = requests.get('https://raw.githubusercontent.com/bevacqua/correcthorse/master/wordlist.json')
            if response.status_code == 200:
                return response.json()
            else:
                self.output_text.insert(tk.END, "Error: Unable to fetch wordlist from the URL\n")
                return None
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred while fetching wordlist: {str(e)}\n")
            return None

    def perform_directory_scan(self, wordlist):
        website_url = self.url_entry.get()
        if not website_url.startswith('http://') and not website_url.startswith('https://'):
            website_url = 'http://' + website_url

        self.output_text.insert(tk.END, f"Starting directory scan for {website_url}...\n")
        for directory in wordlist:
            url = f"{website_url}/{directory}"
            self.output_text.insert(tk.END, f"Scanning directory: {directory}\n")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.output_text.insert(tk.END, f"Directory found: {url}\n")
                else:
                    self.output_text.insert(tk.END, f"Directory not found: {url}\n")
            except Exception as e:
                self.output_text.insert(tk.END, f"Error occurred while scanning {url}: {str(e)}\n")

    def start_directory_scan(self):
        wordlist = self.fetch_wordlist()
        if wordlist:
            threading.Thread(target=self.perform_directory_scan, args=(wordlist,), daemon=True).start()

    def start_tor(self):
        try:
            self.tor_process = stem.process.launch_tor()
            self.output_text.insert(tk.END, "Tor started successfully.\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred while starting Tor: {str(e)}\n")

    def start_tor_stress_test(self):
        num_connections = int(self.tor_connections_entry.get())
        if num_connections <= 0:
            self.output_text.insert(tk.END, "Please enter a valid number of connections.\n")
            return

        website_url = self.url_entry.get()
        if not website_url:
            self.output_text.insert(tk.END, "Please enter a website URL for Tor stress test.\n")
            return

        try:
            self.output_text.insert(tk.END, f"Starting Tor stress test with {num_connections} connections...\n")
            for _ in range(num_connections):
                response = requests.get(website_url, proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'})
                self.output_text.insert(tk.END, f"Request status code: {response.status_code}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred during Tor stress test: {str(e)}\n")

def main():
    root = tktheme.ThemedTk()
    root.get_themes()
    root.set_theme("ubuntu")

    app = NetworkUtilityApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
