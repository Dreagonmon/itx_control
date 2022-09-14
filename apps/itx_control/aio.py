from uselect import poll, POLLIN, POLLHUP, POLLERR
import uasyncio

class AsyncReader():
    def __init__(self, stream_in, buffer_size=4096):
        self.__stream_in = stream_in
        self.__p = poll()
        self.__p.register(self.__stream_in, POLLIN)
        self.__buffer = bytearray(buffer_size)
        self.__buffer_p = 0
        self.__eof = False
    
    @property
    def is_eof(self): return self.__eof

    def try_read1(self, buffer = bytearray(1)) -> bytes | None:
        try:
            for evt in self.__p.ipoll(0):
                ev = evt[1]
                if ev & POLLIN:
                    num = evt[0].readinto(buffer)
                    size = len(buffer)
                    offset = self.__buffer_p
                    self.__buffer_p = self.__buffer_p + size
                    self.__buffer[offset: self.__buffer_p] = buffer
                    return bytes(buffer)
                elif ev & POLLHUP:
                    self.__eof = True
                elif ev & POLLERR:
                    raise OSError
        except OSError as e:
            pass
        return None

    def readline_gen(self, strip_nl = False):
        buffer = bytearray(1)
        while True:
            data = self.try_read1(buffer)
            if data == b"\n":
                back = 0
                if strip_nl:
                    back += 1
                    if self.__buffer_p >= 2 and self.__buffer[self.__buffer_p-2: self.__buffer_p-1] == b"\r":
                        back += 1
                line_of_data = bytes(memoryview(self.__buffer)[:self.__buffer_p - back])
                self.__buffer_p = 0
                yield line_of_data
                return
            yield None
    
    async def readline(self, strip_nl = False):
        _gen = self.readline_gen(strip_nl)
        data = next(_gen)
        while data == None:
            await uasyncio.sleep(0.0)
            data = next(_gen)
        return data
