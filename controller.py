import os
import json
from PIL import Image, ImageTk
import pyocr
import pyocr.builders
import tkinter as tk
#import gui


class ImageDrawer:
    def __init__(self, root, image_path, search_callback=None, confirm_callback=None):
        self.recognized_text = None  # Initialize recognized_text to None
        self.root = root
        self.image_path = image_path
        self.search_callback = search_callback
        self.confirm_callback = confirm_callback
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()

        # Load the image
        self.image = Image.open(image_path)
        self.image_tk = ImageTk.PhotoImage(self.image)
        
        # Display the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

        # Variables to track mouse position and rectangle drawing
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rect_id = None
        self.label = tk.Label(root, text="Dimensions: Width x Height", font=("Helvetica", 12))
        self.label.pack(pady=10)
        self.text_label = tk.Label(root, text="Recognized Text: ", font=("Helvetica", 12))
        self.text_label.pack(pady=10)

        # Set up OCR tool (pyocr)
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise Exception("No OCR tool found")
        self.tool = tools[0]  # Using the first available OCR tool (usually Tesseract)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # When a new rectangle starts, delete the previous one
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        # Store the initial position when the mouse button is pressed
        self.start_x = event.x
        self.start_y = event.y

        # Create a new placeholder rectangle (empty)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)
        self.rect_id = self.rect  # Store the ID of the current rectangle

    def on_mouse_drag(self, event):
        # Update the rectangle's dimensions as the mouse moves
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        
        # Calculate width and height of the rectangle
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        
        # Update label with the current width and height
        self.label.config(text=f"Dimensions: {width} x {height}")

    def on_button_release(self, event):
        # Finalize the rectangle position after the mouse button is released
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        # Final width and height
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        
        # Update label with the final dimensions
        self.label.config(text=f"Dimensions: {width} x {height}")

        # Perform OCR on the selected area
        self.recognize_text_in_rectangle(self.start_x, self.start_y, event.x, event.y)

    def recognize_text_in_rectangle(self, x1, y1, x2, y2):
        global recognized_text

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Crop the image based on the selected area
        cropped_image = self.image.crop((x1, y1, x2, y2))

        # Convert the cropped image to text using pyocr
        recognized_text = self.tool.image_to_string(cropped_image, lang='eng', builder=pyocr.builders.TextBuilder()).strip()
        self.recognized_text = recognized_text  # Store the recognized text

        # Display the recognized text in the label
        self.text_label.config(text=f"Recognized Text: {recognized_text.strip()}")

        if self.confirm_callback:
            self.confirm_callback(recognized_text, self.save_text)

    def save_text(self, recognized_text, confirm_window):
        self.recognized_text = recognized_text  # Store the recognized text
        confirm_window.destroy()  # Close the confirmation window
        
        if self.search_callback:
            self.search_callback(recognized_text)

    
    def return_recognized_text(self):
        return self.recognized_text



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
