"""
Usage:

play music:
see __main__
basically: first buffer q with data; then with stream: keep adding data into q
reading speed of data should be blocksize * channels * samplesize each time

stop music:
ps.stopmusic()

Note:
>>first prototype, really simple...<<
Problem need to be solved: do not know if stop music works fine, still
Did not implement the part where playback finishes

Chinese Simplified Version:
还是不知道stop能不能用
然后这个实现方法非常简单粗暴……总之需要我们不断地通过无论什么stream往q里面塞东西
（其实就是把原本playwav里的这部分移到了外面……）
强行关掉会报错。我想正确的关掉方式应该是stream结束之后call stopmusic吧
"""
import queue
import sys
import threading
import sounddevice as sd
import soundfile as sf

#just for testing purpose:
import ffmpeg

class PlayStream:
    def __init__(self,sample_rate,channels,block_size = 2048,buffer_size = 20):
        #self._data = data
        self._sample_rate = sample_rate
        self._channels = channels
        self._block_size = block_size
        self._buffer_size = buffer_size
        self._q = queue.Queue(maxsize = buffer_size)
    #will remove these if not needed
    @property
    def q(self):
        return self._q
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

    def initstream(self):
        #play from a "buffer" - data
        #just keep going, while streaming audio into the "buffer"
        #data is a file descriptor
        #clear the queue first
        #need to create a stream each time
        self.stream = sd.RawOutputStream(samplerate = self.sample_rate,blocksize = self.block_size,channels = self.channels,callback = self.callback,dtype='float32')
#        while not self._q.empty():
#            try:
#                self._q.get_nowait()
#            except Empty:
#                continue
#            self._q.task_done()
#        for i in range(self.buffer_size):
#            data = self.data.read(self.block_size)
#            if not len(data):
#                break
#            self._q.put_nowait(data)
#        with self.stream:
#            timeout = self.block_size * self.buffer_size / self.sample_rate
#            while len(data):
#                data = self.data.read(self.block_size)
#                self._q.put(data,timeout = timeout)
            
    def stopmusic(self):
        self.stream.stop()


#main function... for testing
if __name__ == "__main__":
    url = "http://icecast.spc.org:8000/longplayer"
    info = ffmpeg.probe(url)
    streams = info.get('streams',[])
    stream = streams[0]
    channels = stream['channels']
    samplerate = float(stream['sample_rate'])
    #q = queue.Queue(maxsize = 20)
    ps = PlayStream(sample_rate = samplerate,channels = channels)
    ps.initstream()
    process = ffmpeg.input(
        url
    ).output(
        'pipe:',
        format='f32le',
        acodec='pcm_f32le',
        ac=channels,
        ar=samplerate,
        loglevel='quiet',
    ).run_async(pipe_stdout=True)
    read_size = ps.block_size * channels * ps.stream.samplesize
    for i in range(20):
        ps.q.put_nowait(process.stdout.read(read_size))
    with ps.stream as s:
        timeout = ps.block_size * ps.buffer_size / samplerate
        while True:
            ps.q.put(process.stdout.read(read_size), timeout=timeout)
