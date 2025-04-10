import tkinter as tk
from PIL import Image, ImageTk
import pyocr
import pyocr.builders

class ImageDrawer:
    def __init__(self, root, image_path):
        self.root = root
        self.image_path = image_path
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()

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
        # Crop the image based on the selected area
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        cropped_image = self.image.crop((x1, y1, x2, y2))

        # Convert the cropped image to text using pyocr
        recognized_text = self.tool.image_to_string(cropped_image, lang='eng', builder=pyocr.builders.TextBuilder())

        print("Recognized Text: {recognized_text.strip()}")

        # Display the recognized text in the label
        self.text_label.config(text=f"Recognized Text: {recognized_text.strip()}")

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Draw Rectangle on Image with OCR (pyocr)")

    # Provide the path to your image
    image_path = "image1.png"  # Replace with your image path
    app = ImageDrawer(root, image_path)

    # Start the Tkinter event loop
    root.mainloop()
