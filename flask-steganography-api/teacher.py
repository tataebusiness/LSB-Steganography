import csv
from PIL import Image
from tkinter import filedialog, messagebox, Toplevel, Checkbutton, BooleanVar, Label, Button
import tkinter as tk
import os
from cryptography.fernet import Fernet
import json

# Generate and save encryption key
key = Fernet.generate_key()
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)
cipher = Fernet(key)

# Convert CSV file to binary, treating each row as JSON for flexibility
def csv_to_binary(csv_file_path):
    binary_data = ""
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Use DictReader to get rows as dictionaries
        for row in reader:
            row_json = json.dumps(row)  # Convert row to JSON string
            encrypted_data = cipher.encrypt(row_json.encode()).decode('utf-8')
            binary_data += ''.join(format(ord(char), '08b') for char in encrypted_data) + '00001010'  # Binary newline
    return binary_data

# Embedding function to hide binary message in the image
def hide_message(image_path, message, output_image):
    img = Image.open(image_path)
    binary_message = message + '1111111111111110'  # End signal
    pixels = img.load()
    width, height = img.size
    binary_index = 0
    for y in range(height):
        for x in range(width):
            if binary_index < len(binary_message):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_message[binary_index])
                binary_index += 1
                if binary_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                if binary_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                pixels[x, y] = (r, g, b)
    img.save(output_image)

# Hide CSV in image
def hide_csv(image_path, csv_file_path, output_image):
    binary_data = csv_to_binary(csv_file_path)
    hide_message(image_path, binary_data, output_image)

# Function to select which fields to display in student view
def select_fields():
    # Open a new window for field selection
    field_window = Toplevel(root)
    field_window.title("Select Fields to Display")
    
    # Create a list to hold the state of each checkbox
    field_vars = {}
    Label(field_window, text="Select fields to display:").pack(pady=5)

    # Create a checkbox for each field in the CSV file
    for field in fieldnames:
        var = BooleanVar(value=True)  # Default to checked
        Checkbutton(field_window, text=field, variable=var).pack(anchor='w')
        field_vars[field] = var

    # Function to save the selected fields to `display_config.json`
    def save_selected_fields():
        selected_fields = [field for field, var in field_vars.items() if var.get()]
        with open("display_config.json", "w") as config_file:
            json.dump({"fields_to_display": selected_fields}, config_file)
        messagebox.showinfo("Saved", "Field selection saved successfully.")
        field_window.destroy()

    # Save button to confirm selection
    Button(field_window, text="Save", command=save_selected_fields).pack(pady=10)

# Modified function to select CSV and display field selection
def select_csv():
    global csv_path, fieldnames
    csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    
    if csv_path:
        csv_label.config(text=os.path.basename(csv_path))
        
        # Open the CSV and get the field names
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames  # Store the fieldnames for checkboxes
        
        # Open the field selection window immediately
        if fieldnames:
            select_fields()
        else:
            messagebox.showerror("Error", "The CSV file appears to be empty or incorrectly formatted.")
    else:
        csv_label.config(text="No CSV File Selected")

# Function to select the image
def select_image():
    global image_path
    image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    image_label.config(text=os.path.basename(image_path) if image_path else "No Image Selected")

# Function to hide data in image
def hide_data():
    if not image_path or not csv_path:
        messagebox.showerror("Error", "Please select both an image and a CSV file.")
        return
    image_dir, image_file = os.path.split(image_path)
    file_name, file_extension = os.path.splitext(image_file)
    output_image = os.path.join(image_dir, f"{file_name}_hidden{file_extension}")
    
    try:
        hide_csv(image_path, csv_path, output_image)
        messagebox.showinfo("Success", f"Data hidden in {output_image}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to hide data: {str(e)}")

root = tk.Tk()
root.title("Teacher - Encrypt Scores")

image_path = None
csv_path = None
fieldnames = []

# Buttons and labels
image_button = tk.Button(root, text="Select Image", command=select_image)
image_button.pack(pady=10)

image_label = tk.Label(root, text="No Image Selected")
image_label.pack(pady=5)

csv_button = tk.Button(root, text="Select CSV File", command=select_csv)
csv_button.pack(pady=10)

csv_label = tk.Label(root, text="No CSV File Selected")
csv_label.pack(pady=5)

hide_button = tk.Button(root, text="Hide CSV in Image", command=hide_data)
hide_button.pack(pady=10)

root.mainloop()
