import tkinter as tk
import serial
import serial.tools.list_ports
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
from settings_windows import *

class PortController:
    def __init__(self):
        self.baudrate = 115200
        self.ser = None
        self.ports = serial.tools.list_ports.comports()
        self.select_port = self.ports[0].name
        self.create_gui()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.geometry("1100x500")
        self.root.resizable(width=False, height=False)
        self.root.title("USB Sentry")
        self.root.option_add("*tearOff", False)

        self.create_canvas()
        self.create_output_field()
        self.create_input_field()
        self.find_ports()
        self.create_menu()
        self.create_buttons()

        self.status_port = tk.Label(self.root, text="COM Port select: " + self.select_port)
        self.status_port.place(x=10, y=450)
        self.value_baudrate = tk.Label(self.root, text="Baudrate: " + str(self.baudrate))
        self.value_baudrate.place(x=10, y=425)

        self.create_context_menu()

        self.root.mainloop()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, width=50, height=50)
        self.circle = self.canvas.create_oval(5, 5, 15, 15, outline='black', fill='red')
        self.canvas.place(x=5, y=405)

    def create_input_field(self):
        self.input_field = ScrolledText(self.root, highlightthickness=2, highlightbackground="gray", width=60, height=10)
        self.input_field.place(x=575, y=10)
        self.input_field.bind("<Button-3>", lambda event: self.input_field.focus_set())
    
    def create_output_field(self):
        self.output_field = ScrolledText(self.root, state='disabled', highlightthickness=2, highlightbackground="gray", width=60, height=23, wrap='none')
        self.output_field.place(x=10, y=10)
        self.output_field.bind("<Button-3>", lambda event: self.output_field.focus_set())
        xscrollbar = Scrollbar(self.root, orient=HORIZONTAL, command=self.output_field.xview)
        xscrollbar.place(x=10, y=387, width=490)
        self.output_field.config(xscrollcommand=xscrollbar.set)
    
    def create_buttons(self):
        self.send_button = tk.Button(self.root, text="Send", command=self.send)
        self.send_button.place(x=800, y=180)

    def create_menu(self):
        self.menu = tk.Menu(self.root)

        self.port_menu = tk.Menu(self.menu)
        self.port_menu.add_command(label="Open port", command=self.open_port)
        self.port_menu.add_command(label="Close port", command=self.close_port)
        self.port_menu.add_command(label="Settings", command=self.open_settings)

        self.scan_menu = tk.Menu(self.menu)
        self.scan_menu.add_command(label="Find ports", command=self.find_ports)

        self.window_menu = tk.Menu(self.menu)
        self.window_menu.add_command(label="Clear all windows", command=self.clear_all)
        self.window_menu.add_command(label="Clear output window", command=self.clear_output)
        self.window_menu.add_command(label="Clear input window", command=self.clear_input)

        self.menu.add_cascade(label="Port", menu=self.port_menu)
        self.menu.add_cascade(label="Scan", menu=self.scan_menu)
        self.menu.add_cascade(label="Window", menu=self.window_menu)
        self.menu.add_cascade(label="Help")
        self.root.config(menu=self.menu)

    def create_context_menu(self):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Clear field", command=self.clear_field)

        self.output_field.bind("<Button-3>", lambda e: self.show_context_menu(e, context_menu), lambda event: self.output_field.focus_set())
        self.input_field.bind("<Button-3>", lambda e: self.show_context_menu(e, context_menu), lambda event: self.output_field.focus_set())
    
    def show_context_menu(self, event, menu):
        menu.post(event.x_root, event.y_root)

    def open_settings(self):
        settings_window = SettingsWindow(self.root, self.ports, self.update_port_settings, default_port=self.select_port, default_baudrate=self.baudrate)

    def open_port(self):
        self.ser = serial.Serial(self.select_port, self.baudrate)
        self.root.after(1000, self.update_circle_color)
        if self.ser.is_open:
            self.add_text_in_output_field(f"Port {self.select_port} opened successfully.")
            thread = threading.Thread(target=self.read_from_port)
            thread.start()
        else:
            self.add_text_in_output_field(f"Failed to open port {self.select_port}. Please check your connection.")

    def close_port(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.root.after(1000, self.update_circle_color)
            if not self.ser.is_open:
                self.add_text_in_output_field(f"Port {self.select_port} closed successfully.")
            else:
                self.add_text_in_output_field(f"Failed to close port {self.select_port}.")

    def read_from_port(self):
        self.root.after(1000, self.update_circle_color)
        while self.ser.is_open:
            data = self.ser.readline().decode('utf-8').strip()
            if data:
                self.add_text_in_output_field(data)

    def update_circle_color(self):
        if self.ser and self.ser.is_open:
            self.canvas.itemconfig(self.circle, fill='green')
        else:
            self.canvas.itemconfig(self.circle, fill='red')

    def update_port_settings(self, select_port, baudrate):
        self.select_port = select_port
        self.baudrate = baudrate
        self.status_port.config(text="COM Port select: " + self.select_port)
        self.value_baudrate.config(text="Baudrate: " + str(self.baudrate))

    def add_text_in_output_field(self, text):
        self.output_field.config(state='normal')
        self.output_field.insert(tk.END, text + '\n')
        self.output_field.config(state='disabled')

    def clear_output(self):
        self.output_field.config(state='normal')
        self.output_field.delete(1.0, tk.END)
        self.output_field.config(state='disabled')

    def clear_input(self):
        self.input_field.delete(1.0, tk.END)

    def clear_field(self):
        if self.root.focus_get() == self.input_field:
            self.clear_input()
        if self.root.focus_get() == self.output_field:
            self.clear_output()
    
    def clear_all(self):
        self.clear_input()
        self.clear_output()

    def find_ports(self):
        self.ports = serial.tools.list_ports.comports()
        self.add_text_in_output_field("Found COM ports:")
        for port in self.ports:
            desc = port.description
            self.add_text_in_output_field(port.device + ': ' + desc)

    def send(self):
        if not self.ser:
            self.add_text_in_output_field(">>>ERROR>>>COM port is closed")
            return
        data = self.input_field.get(1.0, "end-1c")
        if not data:
            self.add_text_in_output_field(">>>ERROR>>>Empty input field")
            return
        if self.ser.is_open:
            self.ser.write(data.encode("utf-8"))
            self.add_text_in_output_field(">>>"+self.select_port+" Sent>>>"+data)
        