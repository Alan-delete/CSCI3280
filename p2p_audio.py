import os
import sys
from pydub import AudioSegment  # pip install pydub
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

class AudioSplitter:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.file_manager = FileManager()

    def send_audio_parts(self, audio_parts, receiver_host, receiver_port):
        # Send the audio parts to the receiver
        for idx, part in enumerate(audio_parts):
            part_bytes = BytesIO()
            part.export(part_bytes, format="wav")
            part_data = part_bytes.getvalue()
            self.file_manager.files[hashlib.md5(part_data).hexdigest()] = {
                "data": part_data,
                "path": f"part_{idx}.wav",
            }

        for file_hash, file_data in self.file_manager.files.items():
            file_downloader = FileDownloader(
                receiver_host, receiver_port, file_hash, "", self.file_manager
            )
            file_downloader.start()
            file_downloader.join()

    def receive_audio_parts(self, sender_host, sender_port):
        # Receive audio parts from the sender
        file_server = fileServer(self, sender_port)
        file_server.start()

        input("[Press Enter to stop the file server]")

        file_server.stop()
        file_server.join()

        audio_parts = []
        for file_hash, file_data in self.file_manager.files.items():
            part_data = file_data["data"]
            part = AudioSegment.from_file(BytesIO(part_data), format="wav")
            audio_parts.append(part)

        return audio_parts

    def split_audio(self, audio_path, num_parts, num_senders):
        # Split the given audio
        audio = AudioSegment.from_file(audio_path)
        duration_ms = len(audio)
        part_duration_ms = duration_ms // (num_parts * num_senders)
        audio_parts = []
        for i in range(num_parts * num_senders):
            start_ms = i * part_duration_ms
            end_ms = (i + 1) * part_duration_ms if i < num_parts * num_senders - 1 else duration_ms
            audio_parts.append(audio[start_ms:end_ms])
        return audio_parts

    def interleave_audios(self, parts_list):
        # Interleave the list of audio parts
        return [part for sublist in zip(*parts_list) for part in sublist]

    def merge_audios(self, parts, output_path):
        # Merge the audio parts into a single audio and save it
        result = AudioSegment.empty()
        for part in parts:
            result += part
        result.export(output_path, format="wav")

    def p2p_audios(self):
        # Get the number of senders
        num_senders = int(input("Input the number of senders (1, 2, or 3): ")) 
        if num_senders not in [1, 2, 3]:
            print("Invalid input. Please enter '1', '2', or '3'.")
            return

        # Get the role of the user
        user_role = input(f"Input your role (receiver, {'/'.join([f'sender{i + 1}' for i in range(num_senders)])}): ")

        if user_role == "receiver":
            received_parts = []
            for i in range(num_senders):
                sender_host = input(f"Input sender{i + 1} IP: ")
                parts = self.receive_audio_parts(sender_host, PORT)
                received_parts.append(parts)
            interleaved_parts = self.interleave_audios(received_parts)
            self.merge_audios(interleaved_parts, "output.wav")
            print("Audio received and saved as 'output.wav'.")

        elif user_role.startswith("sender"):
            sender_num = int(user_role[-1])
            if sender_num > num_senders:
                print(f"Invalid input. Please enter a sender number between 1 and {num_senders}.")
                return

            audio_path = input("Input the path of your audio: ")
            audio_parts = self.split_audio(audio_path, 2, num_senders)
            parts_to_send = audio_parts[sender_num - 1::num_senders]
            receiver_host = input("Input receiver IP: ")
            self.send_audio_parts(parts_to_send, receiver_host, PORT)
            print(f"Audio parts sent by {user_role}.")

        else:
            print(f"Invalid input. Please enter 'receiver' or one of the sender roles ({'/'.join([f'sender{i + 1}' for i in range(num_senders)])}).")

    def local_test(self, audio_paths, num_senders):
        if len(audio_paths) != num_senders:
            print(f"Number of audio paths ({len(audio_paths)}) does not match the number of senders ({num_senders}).")
            return

        # Split the audios into parts
        sender_audio_parts = [self.split_audio(audio_path, 2, num_senders) for audio_path in audio_paths]

        # Simulate sending the parts to a virtual receiver
        received_parts = [[] for _ in range(num_senders)]
        for i in range(num_senders):
            parts_to_send = sender_audio_parts[i][i::num_senders]
            received_parts[i] = parts_to_send

        # Interleave and merge the received parts
        interleaved_parts = self.interleave_audios(received_parts)
        self.merge_audios(interleaved_parts, "local_test_output.wav")
        print("Audio received and saved as 'local_test_output.wav'.")

    def run_audio_splitter(self):
        test_mode = input("Do you want to run a local test? (yes/no): ")
        if test_mode.lower() == "yes":
            num_senders = int(input("Input the number of senders (2 or 3): "))
            audio_paths = [input(f"Input the path of audio for sender {i + 1}: ") for i in range(num_senders)]
            self.local_test(audio_paths, num_senders)
        else:
            self.p2p_audios()

if __name__ == "__main__":
    HOST = socket.gethostname()
    PORT = 1600

    audio_splitter = AudioSplitter(HOST, PORT)
    audio_splitter.run_audio_splitter()