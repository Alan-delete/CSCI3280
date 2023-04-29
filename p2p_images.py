# 暂时设置为一台receiver，三台sender，分别发送图片的14部分、25部分、36部分。

import os
import sys
from PIL import Image  # pip install pillow
import socket
import struct

# test
HOST = socket.gethostname()
PORT = 1600

def send_image_parts(image_parts, receiver_host, receiver_port):
    # Send the image parts to the receiver
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((receiver_host, receiver_port))
        for part in image_parts:
            sock.sendall(struct.pack('>I', len(part)))
            sock.sendall(part)
        sock.sendall(struct.pack('>I', 0))

def receive_image_parts(sender_host, sender_port):
    # Receive image parts from the sender
    image_parts = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((sender_host, sender_port))
        sock.listen(1)
        conn, _ = sock.accept()
        with conn:
            while True:
                length = struct.unpack('>I', conn.recv(4))[0]
                if length == 0:
                    break
                part = conn.recv(length)
                image_parts.append(part)
    return image_parts

def split_image(image_path, num_parts):
    # Split the given image
    image = Image.open(image_path)
    width, height = image.size
    part_width = width // num_parts
    image_parts = []
    for i in range(num_parts):
        start_x = i * part_width
        end_x = (i + 1) * part_width if i < num_parts - 1 else width
        image_parts.append(image.crop((start_x, 0, end_x, height)))
    return image_parts

def interleave_images(parts_list):
    # Interleave the list of image parts
    return [part for sublist in zip(*parts_list) for part in sublist]

def merge_images(parts, output_path):
    # Merge the image parts into a single image and save it
    total_width = sum([part.size[0] for part in parts])
    height = parts[0].size[1]
    result = Image.new('RGB', (total_width, height))
    current_x = 0
    for part in parts:
        result.paste(part, (current_x, 0))
        current_x += part.size[0]
    result.save(output_path)

def p2p_images():
    # Get the role of the user
    user_role = input("Input your role (receiver, sender1, sender2, sender3): ")

    if user_role == "receiver":
        received_parts = []
        for i in range(3):
            sender_host = input(f"Input sender{i + 1} IP: ")
            parts = receive_image_parts(sender_host, PORT)
            received_parts.append(parts)
        interleaved_parts = interleave_images(received_parts)
        merge_images(interleaved_parts, "output.png")
        print("Image received and saved as 'output.png'.")

    elif user_role in ["sender1", "sender2", "sender3"]:
        image_path = input("Input the path of your image: ")
        image_parts = split_image(image_path, 6)
        parts_to_send = image_parts[int(user_role[-1]) - 1::3]
        receiver_host = input("Input receiver IP: ")
        send_image_parts(parts_to_send, receiver_host, PORT)
        print(f"Image parts sent by {user_role}.")

    else:
        print("Invalid input. Please enter 'receiver', 'sender1', 'sender2', or 'sender3'.")

if __name__ == "__main__":
    p2p_images()
