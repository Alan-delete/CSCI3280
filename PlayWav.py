"""
Usage:

initializing:
filename = filename needed
sample_rate = sample rate decoded from header
channels = number of channels decoded from header
pw (or whatever) = PlayWav(filename = filename,sample_rate = sample_rate,channels = channels)

play music:
start_position = starting position (current position on the progress bar), default 0 (start from beginning)
>> how to calculate start_position <<
> current time * size of data
>-----------------------------(divide by)
> total time * pw.block_size
> should be an integer
pw.playmusic(start_position = start_position)

stop music:
pw.stopmusic()

Note:
I am using sounddevice because only sounddevice can work fine on my computer...
Problem need to be solved: do not know if stop music works fine because I can't test stop music.
When the music is playing it blocks everything else. Maybe this can be solved by calling methods
in this class concurrently with other processes, e.g. UI, but I'm not sure.
<new!>It should now support progress bar (to some extent)

Chinese Simplified Version:
不知道为啥我的电脑上只有sounddevice能用。。。现在这个程序确定能工作的只有playmusic，不知道stopmusic
能不能用，因为我不知道怎么让这个音乐后台播放。。。也许需要做UI部分的大佬来处理一下音乐播放和UI同时
运行的问题。。。
（更新）现在大概可以支持progress bar了（大概（总之看上面↑的usage
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
        #self.test_count = 0
        #self.stream = sd.OutputStream(samplerate = self.sample_rate,blocksize = self.block_size,channels = self.channels,callback = self.callback)
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
        #self.test_count += 1
        assert frames == self.block_size
        assert not status
        data = self._q.get_nowait()
        if len(data) < len(outdata):
            outdata[:len(data)] = data
            outdata[len(data):].fill(0)
            raise sd.CallbackStop
        outdata[:] = data

    def playmusic(self,start_position = 0):
        #play from current "block" -> start_position (default:0)
        #f.seek(start_position * self.block_size)
        #clear the queue first
        #need to create a stream each time
        self.stream = sd.OutputStream(samplerate = self.sample_rate,blocksize = self.block_size,channels = self.channels,callback = self.callback)
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Empty:
                continue
            self._q.task_done()
        with sf.SoundFile(self.filename) as f:
            #initialize buffer with the first chunks of data
            f.seek(start_position * self.block_size)
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
        pw.playmusic(start_position = 500)
        print("finished")
        pw.playmusic()
