import os
import json


def load_library(library_name):
    if not os.path.exists(library_name):
        print("File not found, starting with an empty list...")
        return []
    try:
        with open(library_name, "r") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                return data
            else:
                print("Invalid JSON format! Library must be a list.")
                return 1
    except (json.JSONDecodeError, ValueError) as e:
        print("Error reading JSON:", e)
        return 2


def c_save_library(library_name, data):
    with open(library_name, "w") as fh:
        json.dump(data, fh, indent=4)


def c_newfile(filename):
    #Create a new empty JSON file.
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)  # Write an empty JSON list
        print(f"New file created: {filename}")
    except Exception as e:
        print(f"Error creating file: {e}")


def c_openfile(library_name):
    #Open a JSON file and return the loaded data.
    if not os.path.exists(library_name):
        print("Error: File not found.")
        return None

    try:
        with open(library_name, "r", encoding="utf-8") as f:
            content = f.read().strip()  # Read and strip any empty spaces
            return json.loads(content) if content else []  # Handle empty files gracefully
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
