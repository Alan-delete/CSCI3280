"""
Usage:

initializing:
filename = filename needed
sample_rate = sample rate decoded from header
channels = number of channels decoded from header
pw (or whatever) = PlayWav(filename = filename,sample_rate = sample_rate,channels = channels)

play music:
pw.playmusic()

stop music:
pw.stopmusic()

please create a new PlayWav object even when replaying the same file

Note:
I am using sounddevice because only sounddevice can work fine on my computer...
Problem need to be solved: do not know if stop music works fine because I can't test stop music.
When the music is playing it blocks everything else. Maybe this can be solved by calling methods
in this class concurrently with other processes, e.g. UI, but I'm not sure. Also, after stopping
the music has to restart from the begining. It would need some modification if we want to imple-
ment progress bar.

Chinese Simplified Version:
不知道为啥我的电脑上只有sounddevice能用。。。现在这个程序确定能工作的只有playmusic，不知道stopmusic
能不能用，因为我不知道怎么让这个音乐后台播放。。。也许需要做UI部分的大佬来处理一下音乐播放和UI同时
运行的问题。。。而且这个play/stop停止之后只能重新开始。。。总之先写一个应付一下phase 1 ddl，以后可
以再改
"""
import queue
import sys
import threading
import sounddevice as sd
import soundfile as sf

class PlayWav:
    def __init__(self,filename,sample_rate,channels,block_size = 2048,buffer_size = 20):
        self._filename = filename
        self._sample_rate = sample_rate
        self._channels = channels
        self._block_size = block_size
        self._buffer_size = buffer_size
        self._q = queue.Queue(maxsize = buffer_size)
        #self._event = threading.Event()
        self.stream = sd.OutputStream(samplerate = self.sample_rate,blocksize = self.block_size,channels = self.channels,callback = self.callback)
    #will remove these if not needed
    @property
    def filename(self):
        return self._filename
    @property
    def sample_rate(self):
        return self._sample_rate
    @property
    def channels(self):
        return self._channels
    @property
    def block_size(self):
        return self._block_size
    @property
    def buffer_size(self):
        return self._buffer_size

    def callback(self,outdata,frames,time,status):
        assert frames == self.block_size
        assert not status
        data = self._q.get_nowait()
        if len(data) < len(outdata):
            outdata[:len(data)] = data
            outdata[len(data):].fill(0)
            raise sd.CallbackStop
        outdata[:] = data

    def playmusic(self):
        with sf.SoundFile(self.filename) as f:
            #initialize buffer with the first chunks of data
            for i in range(self.buffer_size):
                data = f.read(self.block_size)
                if not len(data):
                    break
                self._q.put_nowait(data)
            #stream = sd.OutputStream(samplerate = self.sample_rate,blocksize = self.block_size,channels = self.channels,callback = self.callback,finished_callback = self._event.set)
            with self.stream:
                timeout = self.block_size * self.buffer_size / self.sample_rate
                while len(data):
                    data = f.read(self.block_size)
                    self._q.put(data,timeout = timeout)
                #self._event.wait()
    def stopmusic(self):
        self.stream.stop()


#main function... for testing
if __name__ == "__main__":
    filename = "file_example.wav"
    with sf.SoundFile(filename) as fi:
        sample_rate = fi.samplerate
        channels = fi.channels
        pw = PlayWav(filename = filename,sample_rate = sample_rate,channels = channels)
        pw.playmusic()
        print("playback ended")
