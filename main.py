# main.py

import tkinter as tk
import time

from model import LibModel
from view import LibView
from controller import LibController

JSON_STORAGE_FILE = "books.json"

def main():
    start_time = time.time()

    root = tk.Tk()
    root.title("Library Manager (MVC Pattern)")
    root.minsize(800, 600)

    print(f"[DEBUG] Tkinter root initialized in {time.time() - start_time:.2f} seconds")
    
    model_start = time.time()
    model = LibModel(JSON_STORAGE_FILE)
    print(f"[DEBUG] Model initialized in {time.time() - model_start:.2f} seconds")

    view_start = time.time()
    view = LibView(root)
    print(f"[DEBUG] View initialized in {time.time() - view_start:.2f} seconds")

    controller_start = time.time()
    controller = LibController(model, view)
    print(f"[DEBUG] Controller initialized in {time.time() - controller_start:.2f} seconds")

    print(f"[DEBUG] Total initialization time: {time.time() - start_time:.2f} seconds")

    root.mainloop()

if __name__ == "__main__":
    main()




