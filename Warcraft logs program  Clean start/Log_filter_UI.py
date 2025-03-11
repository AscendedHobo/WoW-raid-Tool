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
        
        # Use absolute path to locate main_UI.py relative to this script's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjust the path to correctly point to main_UI.py (same directory example)
        self.main_ui_path = os.path.join(current_dir, "main_UI.py")
        
        # GUI setup remains the same...
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
        
        # Right Side - Launch Main UI
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.main_ui_label = tk.Label(right_frame, text="Processed CSV ready? Click below:")
        self.main_ui_label.pack(pady=5)
        
        self.load_db_button = tk.Button(right_frame, text="Open Main UI", command=self.launch_main_ui)
        self.load_db_button.pack(pady=5)
    
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
    
    def launch_main_ui(self):
        try:
            # Use the precomputed main_ui_path
            main_ui_path = self.main_ui_path
            
            print(f"Attempting to launch main UI from: {main_ui_path}")
            
            if os.path.exists(main_ui_path):
                # Launch the script in its own directory to resolve relative paths
                subprocess.Popen(
                    [sys.executable, main_ui_path],
                    cwd=os.path.dirname(main_ui_path)  # Set working directory
                )
            else:
                messagebox.showerror("File Not Found", f"Main UI script not found at {main_ui_path}")
                print(f"ERROR: Main UI script does not exist at {main_ui_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch main UI: {str(e)}")
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()