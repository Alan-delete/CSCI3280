from audio_decoder import AudioDecoder

def main():
    file_path = input("Input the file name of your audio file (WAV or MP3): ")
    decoder = AudioDecoder(file_path)
    #audio_array, num_channels, sample_width, sample_rate = decoder.decode()
    #decoder.play_audio(audio_array, num_channels, sample_width, sample_rate)
    decoder.decode_and_init()
    decoder.play_music()

if __name__ == "__main__":
    main()
