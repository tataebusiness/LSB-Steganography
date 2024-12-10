import csv
from PIL import Image
from cryptography.fernet import Fernet
from Crypto.Hash import MD2
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

# Load the encryption key
def load_key():
    with open("encryption_key.key", "rb") as key_file:
        return key_file.read()

key = load_key()
cipher = Fernet(key)

# Load display configuration from JSON
def load_display_config():
    with open("display_config.json", "r") as config_file:
        config = json.load(config_file)
    return config.get("fields_to_display", [])

# Load student ID column configuration from JSON
def load_student_id_field():
    with open("studentid_config.json", "r") as config_file:
        config = json.load(config_file)
    return config.get("student_id", "ID")  # Default to "ID" if not specified

# Fields to display (loaded from config)
fields_to_display = load_display_config()
student_id_field = load_student_id_field()  # Selected field for student ID

def binary_to_message(binary_data):
    decrypted_data = cipher.decrypt(binary_data).decode('utf-8')
    return decrypted_data

# Function to retrieve binary message from image
def retrieve_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    binary_data = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
    end_signal = '1111111111111110'
    message_bits = binary_data.split(end_signal)[0]
    return ''.join(chr(int(message_bits[i:i+8], 2)) for i in range(0, len(message_bits), 8))

def binary_to_text(binary_data):
    # Split the binary string into chunks of 8 bits (1 byte per character)
    text = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))

    return text

# Decrypt the binary message into a list of JSON objects (rows)
def binary_to_csv(binary_data):
    encrypted_rows = binary_data.split('\n')
    csv_data = []
    for encrypted_row in encrypted_rows:
        if(encrypted_row != ''):
            try:
                decrypted_data = cipher.decrypt(encrypted_row.strip().encode()).decode('utf-8')
                row = json.loads(decrypted_data)
                print(row)
                csv_data.append(row)
            except Exception as e:
                print(f"Failed to decrypt row: {encrypted_row}, Error: {e}")

    return csv_data

# GUI functions for loading image, ID, and password
def select_image():
    global image_path
    image_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    image_label.config(text=os.path.basename(image_path) if image_path else "No Image Selected")

def enter_student_id():
    student_id = id_entry.get()
    if not image_path or not student_id:
        messagebox.showerror("Error", "Please select an image and enter a valid student ID.")
        return
    # Prompt for password after valid ID entry
    prompt_password(student_id)

# Function to check password and retrieve student data
def prompt_password(student_id):
    def check_password():
        input_password = password_entry.get()
        binary_data = retrieve_message(image_path)
        csv_data = binary_to_csv(binary_data)
        
        for row in csv_data:
            if (row.get(student_id_field) == student_id) & (row.get('password') == input_password):  # Match student ID column dynamically
                display_data = "\n".join([f"{key}: {value}" for key, value in row.items() if key in fields_to_display])
                messagebox.showinfo("Success", display_data)
                return
        messagebox.showerror("Error", "Incorrect password or student data not found.")

    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_label = tk.Label(password_window, text="Enter Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack(pady=5)
    password_button = tk.Button(password_window, text="Submit", command=check_password)
    password_button.pack(pady=10)

# Initialize Tkinter window
root = tk.Tk()
root.title("Student Decryption")

image_path = None

# Labels and buttons
image_button = tk.Button(root, text="Select Image", command=select_image)
image_button.pack(pady=10)

image_label = tk.Label(root, text="No Image Selected")
image_label.pack(pady=5)

id_label = tk.Label(root, text="Enter Student ID:")
id_label.pack(pady=5)

id_entry = tk.Entry(root)
id_entry.pack(pady=5)

id_button = tk.Button(root, text="Submit ID", command=enter_student_id)
id_button.pack(pady=10)

root.mainloop()