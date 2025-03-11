import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import subprocess
from tkinterdnd2 import DND_FILES, TkinterDnD

class LogAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WoW Raid Log Analyzer")
        self.root.geometry("800x400")
        
        self.selected_file = None
        self.csv_output_dir = None
        
        # Use the directory of the executable if running as an executable
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Left Side - Log Filtering
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.select_button = tk.Button(left_frame, text="Select Log File", command=self.select_file)
        self.select_button.pack(pady=5)
        
        self.drop_area = tk.Label(left_frame, text="Drag and Drop Log File Here", relief="solid", width=50, height=5)
        self.drop_area.pack(pady=5)
        
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.drop_log_file)
        
        self.file_label = tk.Label(left_frame, text="No file selected", wraplength=400)
        self.file_label.pack()
        
        self.process_button = tk.Button(left_frame, text="Run Log Filter", command=self.run_log_filter_thread, state=tk.DISABLED)
        self.process_button.pack(pady=5)
        
        self.csv_process_button = tk.Button(left_frame, text="Run CSV Processing", command=self.run_csv_processing_thread, state=tk.DISABLED)
        self.csv_process_button.pack(pady=5)
        
        self.status_label = tk.Label(left_frame, text="")
        self.status_label.pack(pady=5)
        
        self.csv_output_entry = tk.Entry(left_frame, width=50)
        self.csv_output_entry.pack(pady=5)
        
        self.open_folder_button = tk.Button(left_frame, text="Open CSV Folder", command=self.open_csv_folder, state=tk.DISABLED)
        self.open_folder_button.pack(pady=5)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self._set_log_file(file_path)
    
    def drop_log_file(self, event):
        file_path = event.data.strip('{}"\'')
        if os.path.isfile(file_path) and file_path.lower().endswith('.txt'):
            self._set_log_file(file_path)
        else:
            messagebox.showwarning("Invalid File", "Please drop a .txt log file.")
    
    def _set_log_file(self, file_path):
        self.selected_file = file_path
        self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
        self.process_button.config(state=tk.NORMAL)
    
    def run_log_filter_thread(self):
        threading.Thread(target=self.process_log, daemon=True).start()
    
    def run_csv_processing_thread(self):
        threading.Thread(target=self.process_csv, daemon=True).start()
    
    def process_log(self):
        if self.selected_file:
            self.status_label.config(text="Running Log Filter... Please wait.")
            script_path = os.path.join(os.path.dirname(__file__), "log_filter one.py")
            os.system(f"python \"{script_path}\" \"{self.selected_file}\"")
            self.csv_process_button.config(state=tk.NORMAL)
            self.status_label.config(text="Log Filter Complete!")
        else:
            messagebox.showwarning("No File", "Please select a file first.")
    
    def process_csv(self):
        self.status_label.config(text="Processing CSV... Please wait.")
        script_path = os.path.join(os.path.dirname(__file__), "CSVtoCSV.py")
        os.system(f"python \"{script_path}\"")
        
        self.csv_output_dir = os.path.dirname(script_path)
        self.csv_output_entry.delete(0, tk.END)
        self.csv_output_entry.insert(0, self.csv_output_dir)
        self.open_folder_button.config(state=tk.NORMAL)
        
        self.status_label.config(text="CSV Processing Complete!")
    
    def open_csv_folder(self):
        if self.csv_output_dir:
            subprocess.Popen(f'explorer "{self.csv_output_dir}"', shell=True)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()