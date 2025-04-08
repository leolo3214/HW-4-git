# main.py

import tkinter as tk

from model import LibModel
from view import LibView
from controller import LibController

JSON_STORAGE_FILE = "books.json"

def main():
    root = tk.Tk()
    root.title("Library Manager (MVC Pattern)")
    root.minsize(800, 600)

    model = LibModel(JSON_STORAGE_FILE)
    view = LibView(root)
    controller = LibController(model, view)

    root.mainloop()

if __name__ == "__main__":
    main()

