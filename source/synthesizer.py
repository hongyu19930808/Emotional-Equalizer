from midi_operation import MIDI
from fluidsynth import Synth, raw_audio_string
from midi import Track, NoteOnEvent, NoteOffEvent
from numpy import append, array, mean, sqrt, maximum, minimum
from generator import Generator
from thread import start_new_thread
from time import sleep
from scipy.signal import lfilter, lfilter_zi

class Synthesizer:
    def __init__(self):
        self.status = False
        start_new_thread(self.init_background, ())
        
    def init_background(self):
        self.synths = []
        self.sfids = []
        for i in range(3):
            synth = Synth()
            self.synths.append(synth)
            self.sfids.append(synth.sfload("/Users/hongyu/SoundFonts/timbres of heaven.sf2"))
        self.status = True
        
    def __del__(self):
        while self.status == False:
            sleep(0.01)        
        for synth in self.synths:
            synth.sfunload(1)
            synth.delete()
            
    def reset(self):
        while self.status == False:
            sleep(0.01)
        for synth in self.synths:
            synth.system_reset()

    def convert_pattern_to_samples(self, pattern, instruments, unit, digital_filter):
        while self.status == False:
            sleep(0.01)
        resolution = pattern.resolution
        tempo = pattern[0][0].get_bpm()
        array_length = int(unit * 60.0 / tempo * 44100)
        
        if len(instruments) >= 3:
            print 'Melody: ' + instruments[0]['Name']
            print 'Harmony: ' + instruments[1]['Name'] + ', ' + instruments[2]['Name']
            print ''
        
        for i in range(min(len(instruments), len(self.synths))):
            self.synths[i].program_select(i, self.sfids[i], 0, instruments[i]['ID'])

        # generate samples
        samples = []
        for i in range(min(len(pattern), len(self.synths))):
            sample = []
            track = pattern[i]
            for event in track:
                if event.tick != 0:
                    length = int(event.tick / float(resolution) * 60.0 / tempo * 44100)
                    sample = append(sample, self.synths[i].get_samples(length))
                if type(event) is NoteOnEvent:
                    self.synths[i].noteon(event.channel, event.data[0], event.data[1])
                if type(event) is NoteOffEvent:
                    self.synths[i].noteoff(event.channel, event.data[0])
            if len(sample) < array_length * 2:
                sample = append(sample, self.synths[i].get_samples(array_length - len(sample) / 2))
            samples.append(sample)
                
        combined_samples = samples[0]
        for i in range(1, len(samples)):
            combined_samples += samples[i]
        if len(digital_filter['a']) >= 2:
            max_original = max(abs(combined_samples))
            zi = lfilter_zi(digital_filter['b'], digital_filter['a'])
            (combined_samples, _) = lfilter(digital_filter['b'], digital_filter['a'], 
                                       combined_samples, zi = zi * combined_samples[0])
            max_filtered = max(abs(combined_samples))
            combined_samples = combined_samples * (max_original / max_filtered)
        return raw_audio_string(combined_samples)