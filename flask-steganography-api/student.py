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

# Decrypt the binary message into a list of JSON objects (rows)
def binary_to_csv(binary_data):
    encrypted_rows = binary_data.split('\n')
    csv_data = []
    for encrypted_row in encrypted_rows:
        if encrypted_row.strip():
            decrypted_data = cipher.decrypt(encrypted_row.encode()).decode('utf-8')
            row = json.loads(decrypted_data)
            csv_data.append(row)
    return csv_data

# Hash the password using MD2 (same as in `testencryption.py`)
def hash_password(password):
    hash_obj = MD2.new()
    hash_obj.update(password.encode())
    hashed = hash_obj.hexdigest()
    print(f"Input Password: {password}, Hashed Password: {hashed}")  # Debug print
    return hashed

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
        # hashed_input_password = hash_password(input_password)  # Hash the input password
        binary_data = retrieve_message(image_path)
        field_data = binary_data.split("lsb_password")
        csv_binary_data = field_data[0]
        password_data = field_data[1]
        csv_data = binary_to_csv(csv_binary_data)
        password = binary_to_message(password_data)
        print(password)
        
        for row in csv_data:
            if row.get(student_id_field) == student_id:  # Match student ID column dynamically
                if password == input_password:  # Match hashed password, change to input_password
                    # Display only fields listed in `fields_to_display`
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
