from PIL import Image

def binary_to_message(binary_data):
    # Split binary string into 8-bit chunks and convert back to characters
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ''.join([chr(int(byte, 2)) for byte in all_bytes])
    return decoded_message

def retrieve_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    binary_data = ''
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)  # Extract LSB of Red
            binary_data += str(g & 1)  # Extract LSB of Green
            binary_data += str(b & 1)  # Extract LSB of Blue
    
    # Stop at the end signal (1111111111111110)
    end_signal = '1111111111111110'
    message_bits = binary_data.split(end_signal)[0]
    
    # Convert binary string to readable message
    decoded_message = binary_to_message(message_bits)
    
    return decoded_message

# Example usage:
if __name__ == "__main__":
    image_path = input("Enter the path of the image: ")
    hidden_message = retrieve_message(image_path)
    print("Hidden Message:", hidden_message)
