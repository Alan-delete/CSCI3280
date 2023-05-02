import os
import sys
from PIL import Image  # pip install pillow
from io import BytesIO
import socket
import struct
import hashlib
import pickle

# ------These classes are from pythonp2p------
from pythonp2p.file_transfer import FileManager
from pythonp2p.file_transfer import fileClientThread
from pythonp2p.file_transfer import fileServer
from pythonp2p.file_transfer import FileDownloader
# ------These classes are from pythonp2p------

class ImageSplitter:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.file_manager = FileManager()

    def send_image_parts(self, image_parts, receiver_host, receiver_port):
        # Send the image parts to the receiver
        for idx, part in enumerate(image_parts):
            part_bytes = BytesIO()
            part.save(part_bytes, format="PNG")
            part_data = part_bytes.getvalue()
            self.file_manager.files[hashlib.md5(part_data).hexdigest()] = {
                "data": part_data,
                "path": f"part_{idx}.png",
            }

        for file_hash, file_data in self.file_manager.files.items():
            file_downloader = FileDownloader(
                receiver_host, receiver_port, file_hash, "", self.file_manager
            )
            file_downloader.start()
            file_downloader.join()

    def receive_image_parts(self, sender_host, sender_port):
        # Receive image parts from the sender
        file_server = fileServer(self, sender_port)
        file_server.start()

        input("[Press Enter to stop the file server]")

        file_server.stop()
        file_server.join()

        image_parts = []
        for file_hash, file_data in self.file_manager.files.items():
            part_data = file_data["data"]
            part = Image.open(BytesIO(part_data))
            image_parts.append(part)

        return image_parts

    def split_image(self, image_path, num_parts, num_senders):
        # Split the given image
        image = Image.open(image_path)
        width, height = image.size
        part_width = width // (num_parts * num_senders)
        image_parts = []
        for i in range(num_parts * num_senders):
            start_x = i * part_width
            end_x = (i + 1) * part_width if i < num_parts * num_senders - 1 else width
            image_parts.append(image.crop((start_x, 0, end_x, height)))
        return image_parts
        
    def interleave_images(self, parts_list):
        # Interleave the list of image parts
        return [part for sublist in zip(*parts_list) for part in sublist]
        
    def merge_images(self, parts, output_path):
        # Merge the image parts into a single image and save it
        total_width = sum([part.size[0] for part in parts])
        height = parts[0].size[1]
        result = Image.new('RGB', (total_width, height))
        current_x = 0
        for part in parts:
            result.paste(part, (current_x, 0))
            current_x += part.size[0]
        result.save(output_path)
        
    def p2p_images(self):
        # Get the number of senders
        num_senders = int(input("Input the number of senders (2 or 3): "))
        if num_senders not in [2, 3]:
            print("Invalid input. Please enter '2' or '3'.")
            return

        # Get the role of the user
        user_role = input(f"Input your role (receiver, {'/'.join([f'sender{i + 1}' for i in range(num_senders)])}): ")

        if user_role == "receiver":
            received_parts = []
            for i in range(num_senders):
                sender_host = input(f"Input sender{i + 1} IP: ")
                parts = self.receive_image_parts(sender_host, PORT)
                received_parts.append(parts)
            interleaved_parts = self.interleave_images(received_parts)
            self.merge_images(interleaved_parts, "output.png")
            print("Image received and saved as 'output.png'.")

        elif user_role.startswith("sender"):
            sender_num = int(user_role[-1])
            if sender_num > num_senders:
                print(f"Invalid input. Please enter a sender number between 1 and {num_senders}.")
                return

            image_path = input("Input the path of your image: ")
            image_parts = self.split_image(image_path, 2, num_senders)
            parts_to_send = image_parts[sender_num - 1::num_senders]
            receiver_host = input("Input receiver IP: ")
            self.send_image_parts(parts_to_send, receiver_host, PORT)
            print(f"Image parts sent by {user_role}.")

        else:
            print(f"Invalid input. Please enter 'receiver' or one of the sender roles ({'/'.join([f'sender{i + 1}' for i in range(num_senders)])}).")

        
    def local_test(self, image_paths, num_senders):
        if len(image_paths) != num_senders:
            print(f"Number of image paths ({len(image_paths)}) does not match the number of senders ({num_senders}).")
            return

        # Split the images into parts
        sender_image_parts = [self.split_image(image_path, 2, num_senders) for image_path in image_paths]

        # Simulate sending the parts to a virtual receiver
        received_parts = [[] for _ in range(num_senders)]
        for i in range(num_senders):
            parts_to_send = sender_image_parts[i][i::num_senders]
            received_parts[i] = parts_to_send

        # Interleave and merge the received parts
        interleaved_parts = self.interleave_images(received_parts)
        self.merge_images(interleaved_parts, "local_test_output.png")
        print("Image received and saved as 'local_test_output.png'.")

    def run_image_splitter(self):
        test_mode = input("Do you want to run a local test? (yes/no): ")
        if test_mode.lower() == "yes":
            num_senders = int(input("Input the number of senders (2 or 3): "))
            image_paths = [input(f"Input the path of image for sender {i + 1}: ") for i in range(num_senders)]
            self.local_test(image_paths, num_senders)
        else:
            self.p2p_images()

if __name__ == "__main__":
    HOST = socket.gethostname()
    PORT = 1600

    image_splitter = ImageSplitter(HOST, PORT)
    image_splitter.run_image_splitter()
