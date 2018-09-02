from pyaudio import PyAudio, paInt16
from time import sleep

class Player:
    def __init__(self, controller):
        self.audio = PyAudio()
        self.stream = self.audio.open(format = paInt16, channels = 2, rate = 44100, output = True)
        self.controller = controller
        
    def __del__(self):
        self.stream.stop_stream()  
        self.stream.close()   
        self.audio.terminate()        
    
    def play(self, samples):
        chunk = 1024
        start = 0
        while True:
            if self.controller.get_status() == 'pause':
                sleep(0.01)
                continue
            elif self.controller.get_status() == 'stop':
                break
            else:
                end = min(len(samples), start + chunk)
                self.stream.write(samples[start:end])
                if end == len(samples):
                    break
                start = start + chunk
            
    
        
        
    