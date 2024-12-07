import csv
import os
import json
import random
import string
from PIL import Image
from tkinter import filedialog, messagebox, Toplevel, Checkbutton, BooleanVar, Label, Button
import tkinter as tk
from cryptography.fernet import Fernet

# Generate and save encryption key
key = Fernet.generate_key()
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)
cipher = Fernet(key)

# Generate random passwords for students
def generate_passwords(num_students, length=8):
    return [''.join(random.choices(string.ascii_letters + string.digits, k=length)) for _ in range(num_students)]

# Convert message to binary
def message_to_binary(message):
    if isinstance(message, (dict, list)):
        message = json.dumps(message)
    encrypted_message = cipher.encrypt(message.encode()).decode('utf-8')
    return ''.join(format(ord(char), '08b') for char in encrypted_message)

# Convert CSV and passwords to binary
# def csv_to_binary(csv_file_path):
#     binary_data = ""
#     passwords = []
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         rows = list(reader)
#         passwords = generate_passwords(len(rows))  # Generate passwords equal to the number of students
#         for i, row in enumerate(rows):
#             row['password'] = passwords[i]  # Add password to each row
#             row_json = json.dumps(row)
#             encrypted_data = cipher.encrypt(row_json.encode()).decode('utf-8')
#             binary_data += ''.join(format(ord(char), '08b') for char in encrypted_data) + '00001010'  # Binary newline
#     return binary_data, passwords



def csv_to_binary(csv_file_path):
    global fieldnames  # Use the global variable

    # Define the output file path
    output_csv_file_path = './source/newcsv.csv'
    output_directory = os.path.dirname(output_csv_file_path)

    # Ensure the 'source' directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    binary_data = ""
    passwords = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        preview_rows = list(csv.reader(csvfile))  # Read all rows for preview

        # Skip rows before the selected header row
        header_row_index = None
        for i, row in enumerate(preview_rows):
            if row == fieldnames:  # Match with the selected header row
                header_row_index = i
                break

        if header_row_index is None:
            raise ValueError("Header row not found in the CSV file.")

        # Use rows starting from the header row
        valid_rows = preview_rows[header_row_index + 1:]  # Rows after the header
        valid_rows = [','.join(row) for row in valid_rows]  # Keep as comma-separated

        reader = csv.DictReader(valid_rows, fieldnames=fieldnames)

        # Add 'password' to fieldnames
        fieldnames.append('password')

        rows = list(reader)
        passwords = generate_passwords(len(rows))  # Generate passwords for each row

        # Update rows with passwords
        for i, row in enumerate(rows):
            row['password'] = passwords[i]

        # Save updated rows to a new CSV file
        with open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # Generate binary data from the updated rows
        for row in rows:
            row_json = json.dumps(row)
            encrypted_data = cipher.encrypt(row_json.encode()).decode('utf-8')
            binary_data += ''.join(format(ord(char), '08b') for char in encrypted_data) + '00001010'  # Binary newline

    return binary_data, passwords

# Embed binary message in the image
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

    # Hide CSV and passwords in the image
def hide_csv(image_path, csv_file_path, output_image):
    binary_data, passwords = csv_to_binary(csv_file_path)
    # print(binary_data)
    hide_message(image_path, binary_data, output_image)
    # Save passwords to a file for teacher reference
    with open("passwords.json", "w") as pw_file:
        json.dump(passwords, pw_file)
    messagebox.showinfo("Success", "Data hidden in image.")

def select_idfield():
    # Open a new window for field selection
    field_window = Toplevel(root)
    field_window.title("Select Field for Student ID")
    
    # Create a frame with a scrollbar
    canvas = tk.Canvas(field_window)
    scroll_y = tk.Scrollbar(field_window, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    # Configure the canvas and scrollbar
    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Variable to store the selected field
    selected_field = tk.StringVar(value=None)  # Default to no selection

    Label(frame, text="Select a field for student ID:").pack(pady=5)

    # Create a radiobutton for each field in the CSV file
    for field in fieldnames:
        tk.Radiobutton(
            frame, 
            text=field, 
            variable=selected_field, 
            value=field
        ).pack(anchor='w')

    # Function to save the selected field to studentid_config.json
    def save_selected_studentid():
        if selected_field.get():  # Check if a field was selected
            with open("studentid_config.json", "w") as config_file:
                json.dump({"student_id": selected_field.get()}, config_file)
            messagebox.showinfo("Saved", "Field selection saved successfully.")
            field_window.destroy()
            select_fields()  # Proceed to the next step
        else:
            messagebox.showerror("Error", "Please select a field for the student ID.")

    # Add a save button at the bottom
    Button(frame, text="Save", command=save_selected_studentid).pack(pady=10)

def select_fields():
    # Open a new window for field selection
    field_window = Toplevel(root)
    field_window.title("Select Fields to Display")
    
    # Create a frame with a scrollbar
    canvas = tk.Canvas(field_window)
    scroll_y = tk.Scrollbar(field_window, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    # Configure the canvas and scrollbar
    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Create a list to hold the state of each checkbox
    field_vars = {}
    Label(frame, text="Select fields to display:").pack(pady=5)

    # Handle duplicates by creating unique keys for each checkbox
    unique_fieldnames = []
    for i, field in enumerate(fieldnames):
        unique_fieldnames.append(f"{field}_{i}" if fieldnames.count(field) > 1 else field)

    # Create a checkbox for each unique field name
    for i, field in enumerate(unique_fieldnames):
        var = BooleanVar(value=False)  # Default to unchecked
        checkbox = Checkbutton(frame, text=fieldnames[i], variable=var)
        checkbox.pack(anchor='w')
        field_vars[field] = var

    # Function to save the selected fields to display_config.json
    def save_selected_fields():
        selected_fields = [field for field, var in field_vars.items() if var.get()]
        with open("display_config.json", "w") as config_file:
            json.dump({"fields_to_display": selected_fields}, config_file)
        messagebox.showinfo("Saved", "Field selection saved successfully.")
        field_window.destroy()

    # Function to check/select all fields
    def select_all_fields():
        for var in field_vars.values():
            var.set(True)  # Check all checkboxes
        field_window.update()  # Force window to update and display changes immediately

    # Add a button to select all fields
    Button(frame, text="Display All", command=select_all_fields).pack(pady=5)

    # Add a save button at the bottom
    Button(frame, text="Save", command=save_selected_fields).pack(pady=10)

def select_csv():
    global csv_path, fieldnames
    csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if csv_path:
        csv_label.config(text=os.path.basename(csv_path))
        select_header_row(csv_path)
    else:
        csv_label.config(text="No CSV File Selected")

def select_header_row(csv_file_path):
    header_window = Toplevel(root)
    header_window.title("Select Header Row")
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        preview_rows = list(csv.reader(csvfile))
    if not preview_rows:
        messagebox.showerror("Error", "CSV is empty or unreadable.")
        header_window.destroy()
        return
    Label(header_window, text="Select the header row:").pack(pady=5)
    listbox = tk.Listbox(header_window, selectmode='single', height=min(len(preview_rows), 10))
    for i, row in enumerate(preview_rows):
        listbox.insert(tk.END, f"Row {i + 1}: {', '.join(row)}")
    listbox.pack(pady=5)
    def confirm_header():
        try:
            selected_index = listbox.curselection()[0]
            global fieldnames
            fieldnames = preview_rows[selected_index]
            messagebox.showinfo("Success", f"Row {selected_index + 1} selected as header.")
            header_window.destroy()
            select_idfield()
        except IndexError:
            messagebox.showerror("Error", "Select a row before confirming.")
    Button(header_window, text="Confirm", command=confirm_header).pack(pady=10)

def select_image():
    global image_path
    image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    image_label.config(text=os.path.basename(image_path) if image_path else "No Image Selected")

def hide_data():
    if not image_path or not csv_path:
        messagebox.showerror("Error", "Select both an image and a CSV file.")
        return
    image_dir, image_file = os.path.split(image_path)
    file_name, file_extension = os.path.splitext(image_file)
    output_image = os.path.join(image_dir, f"{file_name}_hidden{file_extension}")
    try:
        hide_csv(image_path, csv_path, output_image)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to hide data: {str(e)}")

root = tk.Tk()
root.title("Teacher - Encrypt Scores")
image_path = csv_path = None
fieldnames = []
# Buttons and labels
tk.Button(root, text="Select Image", command=select_image).pack(pady=10)
image_label = tk.Label(root, text="No Image Selected")
image_label.pack(pady=5)
tk.Button(root, text="Select CSV File", command=select_csv).pack(pady=10)
csv_label = tk.Label(root, text="No CSV File Selected")
csv_label.pack(pady=5)
tk.Button(root, text="Hide CSV in Image", command=hide_data).pack(pady=10)
root.mainloop()

# 