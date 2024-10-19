from PIL import Image

def message_to_binary(message):
    # Convert the message to binary format
    return ''.join([format(ord(i), '08b') for i in message])

def binary_to_message(binary_data):
    # Split binary string into 8-bit chunks and convert back to characters
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ''.join([chr(int(byte, 2)) for byte in all_bytes])
    return decoded_message

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

# Example usage:
# Hide message
hide_message('input_image.png', 'Testing 123', 'output_image.png')

# Retrieve message
hidden_message = retrieve_message('output_image.png')
# print("Hidden Message:", hidden_message)
