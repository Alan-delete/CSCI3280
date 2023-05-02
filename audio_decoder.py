import struct
import subprocess
import numpy as np
#import simpleaudio as sa
from PlayWav import PlayWav

class AudioDecoder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pw = None

    def read_wav_header(file):
        header_info = [
            ('chunk_id', 4, '4s'),
            ('chunk_size', 4, 'I'),
            ('format', 4, '4s'),
            ('subchunk1_id', 4, '4s'),
            ('subchunk1_size', 4, 'I'),
            ('audio_format', 2, 'H'),
            ('num_channels', 2, 'H'),
            ('sample_rate', 4, 'I'),
            ('byte_rate', 4, 'I'),
            ('block_align', 2, 'H'),
            ('bits_per_sample', 2, 'H'),
        ]

        header_data = {}
        for name, size, fmt in header_info:
            data = file.read(size)
            value = struct.unpack(fmt, data)[0]
            header_data[name] = value

        if header_data['subchunk1_size'] > 16:
            file.read(header_data['subchunk1_size'] - 16)

        header_data['subchunk2_id'] = file.read(4)
        header_data['subchunk2_size'] = struct.unpack('I', file.read(4))[0]

        return header_data

    def decode_mp3(file_path):
        command = ['ffmpeg', '-i', file_path, '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', '-']
        ffmpeg = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, _ = ffmpeg.communicate()
        return stdout

    def decode(self):
        if self.file_path.endswith(".wav"):
            with open(self.file_path, "rb") as file:
                header = AudioDecoder.read_wav_header(file)
                # Extract audio data
                #audio_data = file.read()

                # Convert audio data to a NumPy array
                sample_width = header['bits_per_sample'] // 8
                #dtype = np.int16 if sample_width == 2 else np.int8
                #audio_array = np.frombuffer(audio_data, dtype=dtype)

                num_channels = header['num_channels']
                sample_rate = header['sample_rate']

            return num_channels, sample_width, sample_rate

        elif self.file_path.endswith(".mp3"):
            #audio_data = AudioDecoder.decode_mp3(self.file_path)
            #dtype = np.int16
            sample_width = 2
            num_channels = 2
            sample_rate = 44100
            #audio_array = np.frombuffer(audio_data, dtype=dtype)

            return num_channels, sample_width, sample_rate

        else:
            print("Unsupported file format.")
            return None, None, None


#    def play_audio(self, audio_array, num_channels, sample_width, sample_rate):
#        if audio_array is not None:
#            play_obj = sa.play_buffer(audio_array, num_channels, sample_width, sample_rate)
#            play_obj.wait_done()
    def decode_and_init(self):
        channels,sample_width,sample_rate = self.decode()
        #print("debug: channels = "+str(channels))
        self.pw = PlayWav(filename = self.file_path,sample_rate = sample_rate,channels = channels)

    def play_music(self, start_position = 0):
        self.pw.playmusic(start_position = start_position)

    def stop_music(self):
        self.pw.stopmusic()
