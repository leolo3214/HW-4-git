import json
import os

class LibModel:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.books = []
        self.load_library()

    def load_library(self):
        if not hasattr(self, '_library_loaded') or not self._library_loaded:
            if os.path.exists(self.json_file_path):
                try:
                    with open(self.json_file_path, "r", encoding='utf-8') as file:
                        content = file.read()
                        if content.strip():
                            self.books = json.loads(content)
                            if not isinstance(self.books, list):
                                print(f"Warning: JSON content in {self.json_file_path} is not a list. Initializing empty library.")
                                self.books = []
                        else:
                            self.books = []
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON from {self.json_file_path}. Starting with empty library.")
                    self.books = []
                except Exception as e:
                    print(f"An error occurred while loading {self.json_file_path}: {e}")
                    self.books = []
            else:
                print(f"Info: {self.json_file_path} not found. Starting with empty library.")
                self.books = []
            self._library_loaded = True

    def set_books(self, books):
        self.books = books

    def search_book(self, criteria):
        results = []
        for book in self.books:
            # Check title criteria if provided.
            if criteria.get("title"):
                if criteria["title"].lower() not in book.get("title", "").lower():
                    continue
            # Check author criteria.
            if criteria.get("author"):
                if criteria["author"].lower() not in book.get("author", "").lower():
                    continue
            # Check year criteria.
            if criteria.get("year"):
                if str(book.get("year", "")) != criteria["year"]:
                    continue
            # Check statuses if any selected.
            selected_statuses = criteria.get("statuses", [])
            if selected_statuses and book.get("status", "") not in selected_statuses:
                continue
            results.append(book)
        return results
    
    def save_library(self):
        try:
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(self.books, f, indent=4)
        except Exception as e:
            print(f"Error saving library: {e}")

    def add_book(self, book_data):
        if isinstance(book_data, dict):
            self.books.append(book_data)
            self.save_library()
        else:
            print("Error: Attempted to add invalid book data format (must be a dictionary).")

    def delete_book(self, index):
        if 0 <= index < len(self.books):
            try:
                del self.books[index]
                self.save_library()
                return True
            except Exception as e:
                print(f"Error deleting book at index {index}: {e}")
                return False
        else:
            print(f"Error: Invalid index {index} for deletion.")
            return False

    def search_book(self, criteria):
        results = []
        # Clean up search criteria.
        title_crit = criteria.get("title", "").strip().lower()
        author_crit = criteria.get("author", "").strip().lower()
        year_crit = criteria.get("year", "").strip()
        statuses_crit = [s.strip().lower() for s in criteria.get("statuses", []) if s.strip()]
        
        for book in self.books:
            # Extract and clean book fields.
            btitle = str(book.get("title", "")).strip().lower()
            bauthor = str(book.get("author", "")).strip().lower()
            byear = str(book.get("year", "")).strip()
            bstatus = str(book.get("status", "")).strip().lower()
            
            # Debug prints - uncomment to trace matching
            # print(f"Book: title='{btitle}', author='{bauthor}', year='{byear}', status='{bstatus}'")
            # print(f"Criteria: title='{title_crit}', author='{author_crit}', year='{year_crit}', statuses={statuses_crit}")
            
            # Check Title: substring match.
            if title_crit and title_crit not in btitle:
                continue

            # Check Author: substring match.
            if author_crit and author_crit not in bauthor:
                continue

            # Check Year:
            if year_crit:
                if year_crit.isdigit() and byear.isdigit():
                    if int(byear) != int(year_crit):
                        continue
                else:
                    if year_crit not in byear:
                        continue

            # Check Status (if provided in criteria).
            if statuses_crit and bstatus not in statuses_crit:
                continue

            results.append(book)
        return results

    def sort_library_by_title(self):
        try:
            self.books.sort(key=lambda book: book.get('title', '').lower() if isinstance(book, dict) else '')
            self.save_library()
        except Exception as e:
            print(f"Error sorting by title: {e}")

    def sort_library_by_year(self):
        try:
            self.books.sort(key=lambda book: book.get('year', float('inf'))
                            if isinstance(book, dict) and isinstance(book.get('year'), (int, float))
                            else float('inf'))
            self.save_library()
        except Exception as e:
            print(f"Error sorting by year: {e}")

    def sort_library_by_author(self):
        try:
            self.books.sort(key=lambda book: book.get('author', '').lower() if isinstance(book, dict) else '')
            self.save_library()
        except Exception as e:
            print(f"Error sorting by author: {e}")

    def sort_library_by_status(self):
        try:
            self.books.sort(key=lambda book: book.get('status', '').lower() if isinstance(book, dict) else '')
            self.save_library()
        except Exception as e:
            print(f"Error sorting by status: {e}")

    def change_category(self, index, new_category):
        if 0 <= index < len(self.books):
            try:
                self.books[index]['status'] = new_category
                self.save_library()
                return True
            except Exception as e:
                print(f"Error changing category for book at index {index}: {e}")
                return False
        else:
            print(f"Error: Invalid index {index} for category change.")
            return False
        
    def change_status(self, index, new_status):
        if 0 <= index < len(self.books):
            try:
                self.books[index]['status'] = new_status
                self.save_library()
                return True
            except Exception as e:
                print(f"Error changing status for book at index {index}: {e}")
                return False
        else:
            print(f"Error: Invalid index {index} for status change.")
            return False
