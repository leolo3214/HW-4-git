# view.py
# Handles the graphical user interface (GUI) using Tkinter.

import tkinter as tk
from tkinter import messagebox  # For popups
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from io import BytesIO
import easyocr

class LibView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.controller = None  # Will be set by set_controller
        self.image_canvas = None  # Canvas for displaying images
        self.photo_image = None  # To store the PhotoImage reference
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

        # Initialize the delete_button before using it
        self.delete_button = tk.Button(control_frame, text="Delete Selected")
        self.delete_button.grid(row=0, column=4, padx=5, pady=5)

        self.upload_image_button = tk.Button(control_frame, text="Upload Image")
        self.upload_image_button.grid(row=0, column=5, padx=5, pady=5)

        self.count_label = tk.Label(control_frame, text="Books: 0")
        self.count_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Add a button to perform OCR on the rectangle
        self.ocr_rectangle_button = tk.Button(control_frame, text="OCR Rectangle", command=self.perform_ocr_on_rectangle)
        self.ocr_rectangle_button.grid(row=0, column=7, padx=5, pady=5)

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

        # Add a canvas for displaying images
        self.image_canvas = tk.Canvas(self.master, width=500, height=500, bg="white")
        self.image_canvas.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        # Update the Upload Image button to call the new method
        self.upload_image_button.config(command=self.upload_image)

        # Enable rectangle drawing on the canvas
        self.enable_rectangle_drawing()

    def upload_image(self):
        # Open a file dialog to select an image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return  # User canceled the dialog

        # Open the image using Pillow
        try:
            image = Image.open(file_path)
            image = image.resize((500, 500), Image.Resampling.LANCZOS)  # Resize to fit the canvas
            self.photo_image = ImageTk.PhotoImage(image)
            self.uploaded_image = image  # Store the original image for OCR

            # Display the image on the canvas
            self.image_canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        except Exception as e:
            self.show_error("Error", f"Failed to load image: {e}")

    def enable_rectangle_drawing(self):
        # Bind mouse events to the canvas for rectangle drawing
        self.image_canvas.bind("<ButtonPress-1>", self.start_rectangle)
        self.image_canvas.bind("<B1-Motion>", self.update_rectangle)
        self.image_canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

        self.rect_start_x = None
        self.rect_start_y = None
        self.current_rectangle = None

    def start_rectangle(self, event):
        # Record the starting point of the rectangle
        self.rect_start_x = event.x
        self.rect_start_y = event.y
        self.current_rectangle = self.image_canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y, event.x, event.y, outline="red", width=2
        )

    def update_rectangle(self, event):
        # Update the rectangle as the user drags the mouse
        if self.current_rectangle:
            self.image_canvas.coords(
                self.current_rectangle, self.rect_start_x, self.rect_start_y, event.x, event.y
            )

    def finish_rectangle(self, event):
        # Finalize the rectangle and store its coordinates
        if self.current_rectangle:
            coords = self.image_canvas.coords(self.current_rectangle)
            print(f"Rectangle drawn with coordinates: {coords}")
            # Optionally, pass these coordinates to the controller for further processing
            # self.controller.process_rectangle(coords)

    def perform_ocr_on_rectangle(self):
        if self.photo_image is None:
            self.show_error("Error", "No image uploaded to perform OCR.")
            return

        try:
            # Debug: Log the rectangle coordinates
            print(f"[DEBUG] Rectangle coordinates: {self.image_canvas.coords(self.current_rectangle)}")

            # Get the coordinates of the rectangle
            if not self.current_rectangle:
                self.show_error("Error", "No rectangle drawn on the canvas.")
                return

            coords = self.image_canvas.coords(self.current_rectangle)
            x1, y1, x2, y2 = map(int, coords)

            # Map rectangle coordinates to the uploaded image's dimensions
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            image_width, image_height = self.photo_image.width(), self.photo_image.height()

            # Scale the rectangle coordinates to match the image dimensions
            scaled_x1 = int(x1 * (image_width / canvas_width))
            scaled_y1 = int(y1 * (image_height / canvas_height))
            scaled_x2 = int(x2 * (image_width / canvas_width))
            scaled_y2 = int(y2 * (image_height / canvas_height))

            # Crop the uploaded image using the scaled coordinates
            cropped_image = self.uploaded_image.crop((scaled_x1, scaled_y1, scaled_x2, scaled_y2))

            # Convert the cropped image to a NumPy array
            import numpy as np
            cropped_image_np = np.array(cropped_image)

            # Perform OCR using EasyOCR
            reader = easyocr.Reader(['en'])
            results = reader.readtext(cropped_image_np)

            # Display the OCR results
            ocr_text = "\n".join([f"{text} (Confidence: {confidence:.2f})" for _, text, confidence in results])
            self.show_info("OCR Results", ocr_text)
        except Exception as e:
            self.show_error("Error", f"Failed to perform OCR: {e}")

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

