# controller.py

import threading
import random
import string
import time
import tkinter.filedialog
import json
class LibController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.update_view()

    def update_view(self, book_list=None):
        books_to_display = book_list if book_list is not None else self.model.books
        self.view.fill_list(books_to_display)

    def add_book_controller(self):
        new_book = self.view.show_add_book_dialog()
        if new_book:
            if new_book["title"]:
                self.model.add_book(new_book)
                self.update_view()
            else:
                self.view.show_error("Add Error", "Title is required.")
        else:
            # User cancelled the dialog.
            pass

    def generate_random_book(self):
        title_words = []
        for _ in range(random.randint(1, 4)):
            word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            title_words.append(word)
        title = ' '.join(title_words).title()

        author_first_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        author_last_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
        author = f"{author_first_name} {author_last_name}"

        year = random.randint(1900, 2024)
        status = random.choice(["available", "borrowed", "maintenance", "lost", "on hold"])

        return {"title": title, "author": author, "year": year, "status": status}

    def generate_books_threaded(self, num_books):
        generated_books = []
        for i in range(num_books):
            if self.cancel_generation_flag:
                break
            # Generate random strings for title and author.
            title = ''.join(random.choices(string.ascii_letters, k=10))
            author = ''.join(random.choices(string.ascii_letters, k=8))
            year = random.randint(1900, 2025)
            status = random.choice(["available", "lent out", "missing", "deleted"])
            book = {"title": title, "author": author, "year": year, "status": status}
            generated_books.append(book)
        # Append generated books to existing library.
        self.model.books.extend(generated_books)
        self.model.save_library()
        self.update_view()
        if self.cancel_generation_flag:
            self.view.show_info("Generation Cancelled", f"Generation cancelled after {len(generated_books)} books.")
        else:
            self.view.show_info("Generation Complete", f"Successfully generated {len(generated_books)} books.")

    def cancel_generation(self):
        self.cancel_generation_flag = True

        
    def start_generate_books_controller(self, num_books):
        self.view.show_info("Generation Started", "Generating books in the background...\nThe list will update when complete.")
        # Reset cancel flag before starting generation.
        self.cancel_generation_flag = False
        thread = threading.Thread(target=self.generate_books_threaded, args=(num_books,), daemon=True)
        thread.start()

    def search_book_controller(self):
        criteria = self.view.show_search_dialog()
        if criteria is not None:
            results = self.model.search_book(criteria)
            self.update_view(book_list=results)
    def delete_book_controller(self):
        selected_view_index = self.view.get_selected_index()
        if selected_view_index is not None:
            try:
                display_string = self.view.book_listbox.get(selected_view_index)
                title_to_delete = display_string.split('|')[0].strip()
                model_index_to_delete = -1
                for i, book in enumerate(self.model.books):
                    if book.get('title', '') == title_to_delete:
                        model_index_to_delete = i
                        break
                if model_index_to_delete != -1:
                    if self.view.ask_yes_no("Confirm Delete", f"Are you sure you want to delete '{title_to_delete}'?"):
                        if self.model.delete_book(model_index_to_delete):
                            self.update_view()
                        else:
                            self.view.show_error("Delete Error", "Model failed to delete the book.")
                else:
                    self.view.show_error("Delete Error", "Could not find the selected book in the main library data. The list might have changed. Please try again.")
            except Exception as e:
                self.view.show_error("Delete Error", f"An error occurred during deletion: {e}")
        else:
            self.view.show_error("Delete Error", "Please select a book from the list to delete.")

    def change_status_controller(self):
        selected_view_index = self.view.get_selected_index()
        if selected_view_index is not None:
            try:
                display_string = self.view.book_listbox.get(selected_view_index)
                title_to_change = display_string.split('|')[0].strip()
                model_index_to_change = -1
                for i, book in enumerate(self.model.books):
                    if book.get('title', '') == title_to_change:
                        model_index_to_change = i
                        break
                if model_index_to_change != -1:
                    new_status = self.view.ask_status(title_to_change)
                    if new_status is not None:
                        self.model.change_status(model_index_to_change, new_status)
                        self.update_view()
                else:
                    self.view.show_error("Change Status Error", "Could not find the selected book in the main library data. The list might have changed. Please try again.")
            except Exception as e:
                self.view.show_error("Change Status Error", f"An error occurred during status change: {e}")
        else:
            self.view.show_error("Change Status Error", "Please select a book from the list to change the status.")
    def sort_library_by_title(self):
        self.model.sort_library_by_title()
        self.update_view()

    def sort_library_by_year(self):
        self.model.sort_library_by_year()
        self.update_view()

    def sort_library_by_author(self):
        self.model.sort_library_by_author()
        self.update_view()

    def sort_library_by_status(self):
        self.model.sort_library_by_status()
        self.update_view()

    def open_library_file(self):
        file_path = tkinter.filedialog.askopenfilename(
            title="Open Library File",
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Update the model's books with the new data.
                self.model.set_books(data)
                # Change the model's storage_file to the new file so that save_library writes here.
                self.model.storage_file = file_path
                # Refresh the main window with the new data.
                self.view.fill_list(data)
            except Exception as e:
                self.view.show_error("Error", f"Failed to load JSON file:\n{str(e)}")

    def new_library_controller(self):
        file_path = tkinter.filedialog.asksaveasfilename(
            title="Create New Library File",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")])
        # Use "lib_default.json" if no file is chosen.
        if not file_path:
            file_path = "lib_default.json"
        # Initialize an empty library
        self.model.set_books([])
        # Update the storage file so that subsequent saves write to the new file.
        self.model.storage_file = file_path
        self.model.save_library()
        self.update_view()
        self.view.show_info("New Library Created", f"New library created: {file_path}")