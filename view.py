# view.py
# Handles the graphical user interface (GUI) using Tkinter.

import tkinter as tk
from tkinter import messagebox # For popups
from tkinter import ttk
class LibView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.controller = None # Will be set by set_controller

        self.create_widgets()

    def ask_status(self, title):
        dialog = tk.Toplevel(self.master)
        dialog.title("Change Status")
        tk.Label(dialog, text=f"Select new status for {title}:").pack(padx=10, pady=10)

        # Define allowed statuses:
        statuses = ["available", "lent out", "missing", "deleted"]
        selected_status = tk.StringVar(value=statuses[0])
        # Use ttk.Combobox for a dropdown:
        status_combo = ttk.Combobox(dialog, textvariable=selected_status, values=statuses, state="readonly")
        status_combo.pack(padx=10, pady=10)
        
        # Variable to capture the result
        result = [None]
        def on_ok():
            result[0] = selected_status.get()
            dialog.destroy()
        
        tk.Button(dialog, text="OK", command=on_ok).pack(padx=10, pady=10)
        
        # Center the dialog over the main window (optional)
        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)
        return result[0]
    

    def show_add_book_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Book")
        
        tk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Author:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        author_entry = tk.Entry(dialog, width=40)
        author_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        year_entry = tk.Entry(dialog, width=40)
        year_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Status:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        statuses = ["available", "lent out", "missing", "deleted"]
        status_var = tk.StringVar(value="available")
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=statuses, state="readonly")
        status_combo.grid(row=3, column=1, padx=5, pady=5)
        
        result = [None]
        def on_ok():
            new_book = {
                "title": title_entry.get().strip(),
                "author": author_entry.get().strip(),
                "year": year_entry.get().strip(),
                "status": status_var.get()
            }
            # Convert year to integer if possible; else set to None.
            try:
                new_book["year"] = int(new_book["year"]) if new_book["year"] else None
            except ValueError:
                new_book["year"] = None
            result[0] = new_book
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)
        return result[0]
    def on_book_double_click(self, event=None):
        self.controller.change_status_controller()
    def create_widgets(self):
        # Configure master to use grid.
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)  # list_frame row

        # Create control frame at the top.
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        control_frame.columnconfigure(1, weight=1)  # Allow entry to expand

        #tk.Label(control_frame, text="Title/Search:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        #self.entry = tk.Entry(control_frame, width=40)
        #self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.add_button = tk.Button(control_frame, text="Add Book")
        self.add_button.grid(row=0, column=2, padx=5, pady=5)

        self.search_button = tk.Button(control_frame, text="Search")
        self.search_button.grid(row=0, column=3, padx=5, pady=5)

        self.delete_button = tk.Button(control_frame, text="Delete Selected")
        self.delete_button.grid(row=0, column=4, padx=5, pady=5)

        self.count_label = tk.Label(control_frame, text="Books: 0")
        self.count_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Create list_frame for the book list.
        list_frame = tk.Frame(self.master)
        list_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Header label for columns.
        headers = tk.Label(list_frame, 
            text=f"{'Title':<45} | {'Author':<25} | {'Year':<6} | {'Status':<12}",
            font=("Courier", 10, "bold"))
        headers.grid(row=0, column=0, sticky="w")

        # Create the listbox within list_frame.
        self.book_listbox = tk.Listbox(list_frame, width=100, height=20, font=("Courier", 10))
        self.book_listbox.grid(row=1, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.book_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.book_listbox.config(yscrollcommand=scrollbar.set)
        self.book_listbox.bind("<Double-Button-1>", self.on_book_double_click)

        # Create extra_frame for generation and file buttons.
        extra_frame = tk.Frame(self.master)
        extra_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.generate_button = tk.Button(extra_frame, text="Generate 1 000 000 Books (Threaded)")
        self.generate_button.pack(side=tk.LEFT, padx=5)
        self.cancel_gen_button = tk.Button(extra_frame, text="Cancel Generation")
        self.cancel_gen_button.pack(side=tk.LEFT, padx=5)
        self.open_library_button = tk.Button(extra_frame, text="Open Library File")
        self.open_library_button.pack(side=tk.LEFT, padx=5)

        # Create sort_frame for sort buttons.
        sort_frame = tk.Frame(self.master)
        sort_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        tk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_title_button = tk.Button(sort_frame, text="Title")
        self.sort_title_button.pack(side=tk.LEFT, padx=5)
        self.sort_year_button = tk.Button(sort_frame, text="Year")
        self.sort_year_button.pack(side=tk.LEFT, padx=5)
        self.sort_author_button = tk.Button(sort_frame, text="Author")
        self.sort_author_button.pack(side=tk.LEFT, padx=5)
        self.sort_status_button = tk.Button(sort_frame, text="Status")
        self.sort_status_button.pack(side=tk.LEFT, padx=5)

    def set_controller(self, controller):
        self.controller = controller
        self.add_button.config(command=self.controller.add_book_controller)
        self.search_button.config(command=self.controller.search_book_controller)
        self.delete_button.config(command=self.controller.delete_book_controller)
        self.sort_title_button.config(command=self.controller.sort_library_by_title)
        self.sort_year_button.config(command=self.controller.sort_library_by_year)
        self.sort_author_button.config(command=self.controller.sort_library_by_author)
        self.sort_status_button.config(command=self.controller.sort_library_by_status)
        self.generate_button.config(command=lambda: self.controller.start_generate_books_controller(1000000))
        self.open_library_button.config(command=self.controller.open_library_file)
        self.cancel_gen_button.config(command=self.controller.cancel_generation)
        self.create_menu()
        #self.change_status_button.config(command=self.controller.change_status_controller)
    def get_entry_text(self):
        return self.entry.get()

    def clear_entry(self):
        self.entry.delete(0, tk.END)

    def format_book_display(self, book):
        title = book.get('title', 'N/A')
        author = book.get('author', 'N/A')
        year_str = str(book.get('year', 'N/A'))
        status = book.get('status', 'N/A')

        return f"{title:<45.45} | {author:<25.25} | {year_str:<6.6} | {status:<12.12}"

    def show_search_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Search Books")
        
        tk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Author:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        author_entry = tk.Entry(dialog, width=40)
        author_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        year_entry = tk.Entry(dialog, width=40)
        year_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Include statuses:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        statuses = ["available", "lent out", "missing", "deleted"]
        status_vars = {}
        status_frame = tk.Frame(dialog)
        status_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        for i, status in enumerate(statuses):
            var = tk.IntVar(value=1)
            tk.Checkbutton(status_frame, text=status, variable=var).grid(row=0, column=i, padx=2)
            status_vars[status] = var

        result = [None]
        def on_ok():
            criteria = {
                "title": title_entry.get().strip(),
                "author": author_entry.get().strip(),
                "year": year_entry.get().strip(),
                "statuses": [s for s, var in status_vars.items() if var.get() == 1]
            }
            result[0] = criteria
            dialog.destroy()
            
        def on_cancel():
            result[0] = None
            dialog.destroy()
            
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Search", command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)
        return result[0]
    
    def fill_list(self, books):
        self.book_listbox.delete(0, tk.END)
        for book in books:
            title = book.get('title', 'N/A')
            author = book.get('author', 'N/A')
            year = book.get('year', 'N/A')
            status = book.get('status', 'N/A')
            display_text = f"{title} | {author} | {year} | {status}"
            self.book_listbox.insert(tk.END, display_text)
        self.count_label.config(text=f"Books: {len(books)}")

    def get_selected_index(self):
        selection = self.book_listbox.curselection()
        return selection[0] if selection else None

    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self.master)

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.master)

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message, parent=self.master)
    
    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.controller.new_library_controller)
        file_menu.add_command(label="Open", command=self.controller.open_library_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.master.config(menu=menu_bar)

