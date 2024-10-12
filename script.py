# Reference: https://github.com/RobinDavid/LSB-Steganography/blob/master/README.md
import LSBSteg
import cv2
import os
import shutil

source_file_path = "./source/sourceimage.png"
hide_file_path = "./data/my_new_image.png"
recover_file_path = "./data/recovered.png"
if not os.path.isfile(source_file_path):
    print(f"File not found: {source_file_path}")
else:
    print(f"Found: {source_file_path}")
    # result = cv2.imread(file_path)
    #encoding
    steg = LSBSteg.LSBSteg(cv2.imread(source_file_path))
    img_encoded = steg.encode_text("my message")
    cv2.imwrite(hide_file_path, img_encoded)

    #decoding
    im = cv2.imread(hide_file_path)
    steg = LSBSteg.LSBSteg(im)
    print("Text value:",steg.decode_text())

    #encoding
    # secret_image_path = "./source/secret_image.jpg"
    # steg = LSBSteg.LSBSteg(cv2.imread(source_file_path))
    # result = cv2.imread(secret_image_path)
    # new_im = steg.encode_image(result)
    # cv2.imwrite(hide_file_path, new_im)

    #decoding
    # steg = LSBSteg.LSBSteg(hide_file_path)
    # orig_im = steg.decode_image()
    # cv2.imwrite(recover_file_path, orig_im)