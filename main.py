import csv
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def message_to_binary(message):
    # Convert the message to binary format
    return ''.join([format(ord(i), '08b') for i in message])

def binary_to_message(binary_data):
    # Split binary string into 8-bit chunks and convert back to characters
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ''.join([chr(int(byte, 2)) for byte in all_bytes])
    return decoded_message

def csv_to_binary(csv_file_path):
    binary_data = ""
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            row_data = ','.join(row)
            binary_data += message_to_binary(row_data) + message_to_binary("\n")
    return binary_data

def binary_to_csv(binary_data, output_csv_file):
    message = binary_to_message(binary_data)

    rows = message.split('\n')
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            if row:
                writer.writerow(row.split(','))

def hide_message(image_path, message, output_image):
    # Open the image and convert it to RGB
    img = Image.open(image_path)
    binary_message = message_to_binary(message) + '1111111111111110'  # End signal
    
    # Convert image to an array of pixels
    pixels = img.load()
    width, height = img.size
    binary_index = 0
    
    # Loop over each pixel
    for y in range(height):
        for x in range(width):
            if binary_index < len(binary_message):
                # Get the RGB values of the pixel
                r, g, b = pixels[x, y]
                
                # Modify the least significant bit of each channel
                r = (r & ~1) | int(binary_message[binary_index])
                binary_index += 1
                if binary_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                if binary_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                
                # Set the modified pixel back
                pixels[x, y] = (r, g, b)
    
    # Save the modified image
    img.save(output_image)
    # print(f"Message hidden in {output_image}")

def retrieve_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    binary_data = ''
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
    
    # Split the binary string into bytes and stop at end signal (1111111111111110)
    end_signal = '1111111111111110'
    message_bits = binary_data.split(end_signal)[0]
    
    # Convert binary string to readable message
    decoded_message = binary_to_message(message_bits)
    
    return decoded_message

# Hide csv file in image
def hide_csv(image_path, csv_file_path, output_image):
    binary_data = csv_to_binary(csv_file_path)
    hide_message(image_path, binary_data, output_image)

# Retrieve CSV file from image
def retrieve_csv(image_path, output_csv_file):
    binary_data = retrieve_message(image_path)
    binary_to_csv(binary_data, output_csv_file)


# Example usage:
# Variables
input_image = "./source/source_image.png"
output_image = "./source/output_image.png"
csv_file_path = "./source/score_sheet.csv"
# Feature: Text LSB
# Hide message
# # hide_message('input_image.png', 'Testing 123', 'output_image.png')
# hide_message(input_image, 'Testing 123', output_image)

# # Retrieve message
# hidden_message = retrieve_message(output_image)
# print("Hidden Message:", hidden_message)

# Feature: CSV LSB
# Hide csv
hide_csv(input_image, csv_file_path, output_image)

# Retrieve CSV
retrieve_csv_file = "./data/retrieve_data.csv"
retrieve_csv(output_image, retrieve_csv_file)

# GUI
def select_image():
    global image_path
    image_path = filedialog.askopenfilename(
        title="Select Image", 
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    image_label.config(text=os.path.basename(image_path) if image_path else "No Image Selected")

def select_csv():
    global csv_path
    csv_path = filedialog.askopenfilename(
        title="Select CSV File", 
        filetypes=[("CSV Files", "*.csv")]
    )
    csv_label.config(text=os.path.basename(csv_path) if csv_path else "No CSV File Selected")

def hide_data():
    if not image_path or not csv_path:
        messagebox.showerror("Error", "Please select both an image and a CSV file.")
        return

    # Create output image path automatically (append "_hidden" to original image file name)
    image_dir, image_file = os.path.split(image_path)
    file_name, file_extension = os.path.splitext(image_file)
    output_image = os.path.join(image_dir, f"{file_name}_hidden{file_extension}")

    try:
        hide_csv(image_path, csv_path, output_image)
        messagebox.showinfo("Success", f"Data hidden in {output_image}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to hide data: {str(e)}")

def retrieve_data():
    # Select steganography image to retrieve hidden CSV from
    global image_path
    image_path = filedialog.askopenfilename(
        title="Select Steganography Image", 
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    
    if not image_path:
        messagebox.showerror("Error", "Please select an image to retrieve data from.")
        return

    # Automatically save the retrieved CSV in the same directory as the image
    image_dir, image_file = os.path.split(image_path)
    file_name, _ = os.path.splitext(image_file)
    retrieve_csv_file = os.path.join(image_dir, f"{file_name}_retrieved.csv")

    try:
        retrieve_csv(image_path, retrieve_csv_file)
        messagebox.showinfo("Success", f"CSV file retrieved and saved as {retrieve_csv_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve data: {str(e)}")

# Initialize Tkinter window
root = tk.Tk()
root.title("Steganography GUI")

image_path = None
csv_path = None

# Labels and buttons
image_button = tk.Button(root, text="Select Image", command=select_image)
image_button.pack(pady=10)

image_label = tk.Label(root, text="No Image Selected")
image_label.pack(pady=5)

csv_button = tk.Button(root, text="Select CSV File", command=select_csv)
csv_button.pack(pady=10)

csv_label = tk.Label(root, text="No CSV File Selected")
csv_label.pack(pady=5)

hide_button = tk.Button(root, text="Hide CSV in Image", command=hide_data)
hide_button.pack(pady=20)

retrieve_button = tk.Button(root, text="Retrieve CSV from Image", command=retrieve_data)
retrieve_button.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
