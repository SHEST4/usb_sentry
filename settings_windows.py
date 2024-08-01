import tkinter as tk
from tkinter import ttk

class SettingsWindow:
    def __init__(self, root, ports, update_callback, default_port=None, default_baudrate=None):
        self.root = tk.Toplevel(root)
        self.root.geometry("250x150")
        self.root.resizable(width=False, height=False)
        self.root.title("COM Port Settings")

        self.ports = [port.name for port in ports]

        self.com_port_label = tk.Label(self.root, text="COM Port")
        self.com_port_label.place(x=10, y=10)
        self.combobox = ttk.Combobox(self.root, values=self.ports)
        self.combobox.place(x=100, y=10)
        if default_port:
            self.combobox.set(default_port) 

        self.baudrate_label = tk.Label(self.root, text="Baudrate")
        self.baudrate_label.place(x=10, y=45)
        self.baudrate_entry = ttk.Entry(self.root)
        self.baudrate_entry.place(x=100, y=45)
        if default_baudrate:
            self.baudrate_entry.insert(0, default_baudrate)  

        self.ok_button = tk.Button(self.root, text="OK", command=self.update_values)
        self.ok_button.place(x=110, y=100)

        self.update_callback = update_callback

    def update_values(self):
        select_port = self.combobox.get()
        baudrate = self.baudrate_entry.get()
        self.update_callback(select_port, baudrate)
        self.root.destroy()

