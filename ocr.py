import easyocr

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])  # Specify the language(s) you want to recognize

# Perform OCR on the image
results = reader.readtext('image1.png')

# Print the detected text
for bbox, text, confidence in results:
    print(f"Detected text: '{text}' with confidence: {confidence}")