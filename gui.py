# This program is made by: 
# leonard.grill@stud.th-deg.de
# hryhorii.kuznetsov@stud.th-deg.de 
# shamil.liman@stud.th-deg.de


import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
import controller
import random
import threading
from tkinter import ttk
import string


global root, title_entry, author_entry, year_entry, book_list, sort_order,library, library_name, book_count_label

library_name = "lib_default.json"  # Default library name


def load_library(library_name):
    if controller.load_library(library_name) == 1:
        messagebox.showerror("Error", "Invalid JSON format! Please fix the file manually.")
    elif controller.load_library(library_name) == 2:
        messagebox.showerror("Error", "Corrupted JSON file! Please fix it manually.")
    return controller.load_library(library_name)


def open_add_book_window(title=None):
    #Opens a new window to add a book with Title, Author, and Year input fields.
    add_window = tk.Toplevel()
    add_window.title("Add New Book")
    add_window.geometry("300x250")
    add_window.resizable(False, False)

    # Labels and Entry Fields
    tk.Label(add_window, text="Title:").pack(pady=5)
    title_entry = tk.Entry(add_window, width=30)
    title_entry.pack()

    tk.Label(add_window, text="Author:").pack(pady=5)
    author_entry = tk.Entry(add_window, width=30)
    author_entry.pack()

    tk.Label(add_window, text="Year:").pack(pady=5)
    year_entry = tk.Entry(add_window, width=30)
    year_entry.pack()

    if title != None: # If a title is provided, pre-fill the title entry field. (only comes from image search)
        title_entry.insert(0, title)


    # Function to save the book
    def save_book():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        year = year_entry.get().strip()

        if not title or not author or not year:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        if not year.isdigit():
            messagebox.showerror("Error", "Year must be a number!")
            return
        
        messagebox.showinfo("Success", "Book added!")

        # Add book to library
        new_book = {"title": title, "author": author, "year": int(year), "status": "Available"}
        library.append(new_book)
        controller.c_save_library(library_name, library)  # Save to JSON
        refresh_list()  # Refresh main list
        add_window.destroy()  # Close the window

    # Save and Cancel Buttons
    tk.Button(add_window, text="Save", command=save_book, width=10).pack(pady=10)
    tk.Button(add_window, text="Cancel", command=add_window.destroy, width=10).pack()



def delete_book():
    global library

    selected_item = book_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a book to delete!")
        return

    title = book_list.item(selected_item, "values")[0]
    library = [book for book in library if book["title"] != title]
    controller.c_save_library(library_name, library)

    refresh_list()

    emptyfields()

    messagebox.showinfo("Success", title, "deleted!")

def open_delete_confirmation():
    """Opens a confirmation window before deleting a selected book."""
    global library

    selected_item = book_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a book to delete!")
        return

    title = book_list.item(selected_item, "values")[0]

    # Create Confirmation Window
    confirm_window = tk.Toplevel()
    confirm_window.title("Confirm Deletion")
    confirm_window.geometry("300x150")
    confirm_window.resizable(False, False)

    tk.Label(confirm_window, text=f"Are you sure you want to delete:\n'{title}'?", fg="red").pack(pady=10)

    # Function to delete the book
    def confirm_delete():
        global library
        library = [book for book in library if book["title"] != title]
        controller.c_save_library(library_name, library)
        refresh_list()
        emptyfields()
        messagebox.showinfo("Success", f"'{title}' has been deleted!")
        confirm_window.destroy() 
        update_book_count()

    # Buttons
    tk.Button(confirm_window, text="Delete", command=confirm_delete, bg="red", fg="white", width=10).pack(pady=5)
    tk.Button(confirm_window, text="Cancel", command=confirm_window.destroy, width=10).pack()
    



def refresh_list():
    book_list.delete(*book_list.get_children())  # Clear current list

    # Get selected statuses from checkboxes
    selected_statuses = {status for status, var in status_vars.items() if var.get()}

    # Filter and display books based on selected statuses
    for book in library:
        if book["status"] in selected_statuses:
            book_list.insert("", tk.END, values=(book["title"], book["author"], book["year"], book["status"]))


def filter_books(status_vars):
    #Filter books based on selected checkboxes.
    refresh_list(status_vars)



def sort_library(column):
    global library, sort_order

    reverse = sort_order[column]  # Get current order
    sort_order[column] = not reverse  # Toggle order for next click

    if column == "Year":
        library.sort(key=lambda book: book[column.lower()], reverse=reverse)  # Numeric sorting
    else:
        library.sort(key=lambda book: book[column.lower()].lower(), reverse=reverse)  # Text sorting

    refresh_list()
    controller.c_save_library(library_name, library)  # Save sorted data


def search_book(title=None):  # search books with queries
    global library, book_list  # Declare book_list as global
    print(title)
    
    library = load_library(library_name)

    if not title:
        query = title_entry.get().strip() or author_entry.get().strip() or year_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a title, author, or year to search!")
            return

        results = [
            book for book in library
            if (query.lower() in book["title"].lower()
            or query.lower() in book["author"].lower()
            or query.isdigit() and int(query) == book["year"])
            and book["status"] in status_vars and status_vars[book["status"]].get()
        ]
    
    else:
        image_window.destroy()
        results = [
            book for book in library
            if (title.lower() in book["title"].lower())
        ]

    if not results:
        if not title:
            messagebox.showinfo("No Results", "No books found matching your search.")
            return
        else:
            #messagebox.showinfo("No Results", "No books found matching your search." + "\nDo you want to create a book with this title?:\n" + title)
            newocr = tk.Toplevel()
            newocr.title("not found")
            newocr.geometry("300x150")
            newocr.resizable(False, False)

            tk.Label(newocr, text="No books found matching your search.", fg="red").pack(pady=10)
            tk.Label(newocr, text="Do you want to create a book with this title?:\n" + title, fg="black").pack(pady=10)

            tk.Button(newocr, text="Yes", command=lambda: (open_add_book_window(title), newocr.destroy())).pack(side=tk.LEFT, padx=20)
            tk.Button(newocr, text="No", command=newocr.destroy).pack(side=tk.RIGHT, padx=20)
            return

    book_list.delete(*book_list.get_children())
    for book in results:
        book_list.insert("", tk.END, values=(book["title"], book["author"], book["year"], book["status"]))


def show_all_books():
    book_list.delete(*book_list.get_children())
    for book in library:
        book_list.insert("", tk.END, values = (book["title"], book["author"], book["year"], book["status"]))
    

def emptyfields():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)

def openfile():
    global library_name, library  # Ensure changes reflect globally

    filename = filedialog.askopenfilename(
        title="Select a JSON file",
        filetypes=[("JSON Files", "*.json")]
    )

    if filename:  # Ensure a file is selected
        library_name = filename  # Update the global file name
        library = controller.load_library(library_name)  # Load new library##################################

        if library is None:
            messagebox.showerror("Error", "Failed to load the selected file.")
            return

        refresh_list()
        messagebox.showinfo("Success", f"Loaded library from {library_name}")


def NewFile():
    global library_name, library  

    filename = filedialog.asksaveasfilename(
        title="Create New JSON Library",
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")]
    )

    if filename:  # If user didn't cancel
        controller.c_newfile(filename)  # Call controller method to create the file
        library_name = filename  # Update global filename
        library = []  # Reset the library list
        refresh_list()  # Refresh GUI
        messagebox.showinfo("Success", f"New library created: {library_name}")


def create_menu():
    menu = tk.Menu(root)
    root.config(menu=menu)
    filemenu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New", command=NewFile)
    filemenu.add_command(label="Open...", command=openfile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)


# Define variables for checkboxes
def create_status_checkboxes():
    global status_vars 
    status_vars = {
    "available": tk.BooleanVar(value=True),
    "lent out": tk.BooleanVar(value=True),
    "deleted": tk.BooleanVar(value=True),
    "missing": tk.BooleanVar(value=True)
    }
    # Creates checkboxes for filtering book statuses.
    status_frame = tk.Frame(root)
    status_frame.pack(pady=5)

    tk.Label(status_frame, text="Filter by Status:").pack(side="left")

    for status, var in status_vars.items():
        tk.Checkbutton(status_frame, text=status, variable=var, command=refresh_list).pack(side="left")



def open_status_window(event, book_list):
    # Opens a new window to change the status of the selected book.
    selected_item = book_list.selection()
    if not selected_item:
        return

    # Get book details
    book_values = book_list.item(selected_item, "values")
    title = book_values[0]

    # Find book in the library
    book = next((b for b in library if b["title"] == title), None)
    if not book:
        messagebox.showerror("Error", "Book not found!")
        return

    # Create new window
    status_window = tk.Toplevel()
    status_window.title(f"Change Status - {title}")
    status_window.geometry("300x150")
    status_window.resizable(False, False)

    # Status options
    statuses = ["available", "lent out", "missing", "deleted"]

    # Label
    tk.Label(status_window, text=f"Change status for: {title}", font=("Arial", 12)).pack(pady=10)

    # Dropdown for selecting status
    status_var = tk.StringVar(value=book["status"])
    status_dropdown = ttk.Combobox(status_window, textvariable=status_var, values=statuses, state="readonly")
    status_dropdown.pack(pady=5)

    # Function to update status
    def save_new_status():
        book["status"] = status_var.get()
        controller.c_save_library(library_name, library)  # Save changes
        refresh_list()  # Refresh the list in the main window
        status_window.destroy()

    # Save Button
    tk.Button(status_window, text="Save", command=save_new_status, width=15).pack(pady=10)



stop_generating = False  # Global flag to stop book generation

def open_random_books_window():
    #Opens a new window to specify the number of random books to generate.
    global stop_generating

    # Create the new window
    random_window = tk.Toplevel(root)
    random_window.title("Generate Random Books")
    random_window.geometry("300x200")
    random_window.resizable(False, False)

    # Label & Input for Book Count
    tk.Label(random_window, text="Number of Books:").pack(pady=5)
    book_count_entry = tk.Entry(random_window)
    book_count_entry.pack(pady=5)

    # Progress Bar
    progress = ttk.Progressbar(random_window, length=250, mode="determinate")
    progress.pack(pady=10)

    # Start Generation Button
    def start_generation():
        global stop_generating
        stop_generating = False  # Reset stop flag

        try:
            num_books = int(book_count_entry.get())
            if num_books <= 0:
                messagebox.showerror("Error", "Enter a valid number!")
                return
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number!")
            return

        # Disable the entry field after a valid number is entered
        book_count_entry.config(state="disabled")

        threading.Thread(target=generate_books, args=(num_books, progress, random_window), daemon=True).start()

    # Stop Button
    def stop_generation():
        global stop_generating
        stop_generating = True  # Set stop flag

    tk.Button(random_window, text="Start", command=start_generation, bg="green", fg="white").pack(pady=5)
    tk.Button(random_window, text="Stop", command=stop_generation, bg="red", fg="white").pack(pady=5)

def generate_books(num_books, progress, window):
    # Generates random books and updates the library with a progress bar.
    global library, stop_generating

    progress["maximum"] = num_books
    progress["value"] = 0

    for i in range(num_books):
        if stop_generating:
            break  # Stop if user presses "Stop"
        
        alength = random.randint(5, 15)  # Random length for author
        tlength = random.randint(5, 15)  # Random length for title
        letters   = string.ascii_lowercase

        title = ''.join(random.choice(letters) for i in range(tlength))
        author = ''.join(random.choice(letters) for i in range(alength))
        year = random.randint(1900, 2025)

        library.append({"title": title, "author": author, "year": year, "status": "available"})
        controller.c_save_library(library_name, library)  # Save to file

        progress["value"] = i + 1  # Update progress bar
        update_book_count()

    messagebox.showinfo("Completed", "Random book generation finished!")
    window.destroy()  # Close the window when done

def update_book_count():
    # Updates the label displaying the number of books in the library.
    book_count_label.config(text=f"Total Books: {len(library)}")


def open_image_window():
    global image_window
    imagename = filedialog.askopenfilename(
        title="PNG file",
        filetypes=[("PNG Files", "*.png")]
    )
    if imagename: # Ensure an image is selected
        image_window = tk.Toplevel(root)
        image_window.title("search book by image and text recognition")
        image_window.geometry("400x400")
        image_window.resizable(True, True)
        tk.Label(image_window, text="search book by image + OCR", font=("Arial", 12)).pack(pady=10)    
 
        image = controller.ImageDrawer(image_window, imagename, search_callback=search_book, confirm_callback=confirm_search_window)

        if image is None:
            messagebox.showerror("Error", "Failed to load the selected file.")
            return
       

def confirm_search_window(recognized_text, on_confirm):
    confirm_window = tk.Toplevel(root)
    confirm_window.title("Confirm Text")
    confirm_window.geometry("400x150")
    confirm_window.resizable(False, False)

    tk.Label(
        confirm_window,
        text="Do you want to search for a book with this name in your library?",
        fg="red",
        font=("Arial", 12)
    ).pack(pady=(10, 0))

    tk.Label(
        confirm_window,
        text=f"'{recognized_text}'",
        fg="red",
        font=("Arial", 16, "bold")
    ).pack(pady=(0, 10))


    tk.Button(confirm_window, text="Yes", command=lambda: (on_confirm(recognized_text, confirm_window))).pack(side=tk.LEFT, padx=20)
    tk.Button(confirm_window, text="No, select new text", command=confirm_window.destroy).pack(side=tk.RIGHT, padx=20)



def create_gui():
    global root, title_entry, author_entry, year_entry, book_list, sort_order,library, library_name, book_count_label, book_list
    root = tk.Tk()
    root.title("Library Manager")
    root.geometry("850x600")
    root.resizable(False, False)

    create_menu()

    library = load_library(library_name)
    if library is None:
        return
    
    book_count_label = tk.Label(root, text=f"Total Books: {len(library)}", font=("Arial", 12, "bold"))
    book_count_label.pack(pady=5)

    sort_order = {"Title": True, "Author": True, "Year": True, "Status": True}  # Track sort direction

    frame = tk.Frame(root)
    frame.pack(pady=10)

    # Entry fields for adding/searching books
    tk.Label(frame, text="Title:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    title_entry = tk.Entry(frame, width=30)
    title_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame, text="Author:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    author_entry = tk.Entry(frame, width=30)
    author_entry.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame, text="Year:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    year_entry = tk.Entry(frame, width=30)
    year_entry.grid(row=2, column=1, padx=5, pady=2)

    tk.Button(frame, text="Add Book", command=open_add_book_window, width=20).grid(row=3, column=0, pady=5)
    tk.Button(frame, text="Search Book", command=search_book, width=20).grid(row=3, column=1, pady=5)
    tk.Button(frame, text="Show all Books", command=show_all_books, width=20).grid(row=3, column=2, pady=5)
    tk.Button(frame, text="Delete Book", command=open_delete_confirmation, width=20,  bg="red", fg="white").grid(row=4, column=0, pady=5)
    tk.Button(frame, text="Add Random Books", command=open_random_books_window, width=20, bg="blue", fg="white").grid(row=4, column=1, pady=5)
    tk.Button(frame, text="Upload Image", command=open_image_window, width=20, bg="green", fg="white").grid(row=4, column=2, pady=5)

    # Frame for book list and scrollbar
    book_frame = tk.Frame(root)
    book_frame.pack(pady=10, fill="both", expand=True)

    # Create Treeview (book list)
    book_list = ttk.Treeview(book_frame, columns=("Title", "Author", "Year", "Status"), show="headings", height=10)
    book_list.grid(row=0, column=0, sticky="nsew")
    book_list.bind("<Double-1>", lambda event: open_status_window(event, book_list))

    # Scrollbar
    scrollbar = ttk.Scrollbar(book_frame, orient="vertical", command=book_list.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    book_list.configure(yscrollcommand=scrollbar.set)

    book_frame.columnconfigure(0, weight=1)
    book_frame.rowconfigure(0, weight=1)

    # Create checkboxes for filtering by status
    create_status_checkboxes()

    # Set column headings and bind clicks for sorting
    for col in ("Title", "Author", "Year", "Status"):
        book_list.heading(col, text=col, command=lambda c=col: sort_library(c))  # Bind header click

    refresh_list()
    root.mainloop()




if __name__ == "__main__":
    create_gui()
