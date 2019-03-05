from midi_operation import MIDI
from fluidsynth import Synth, raw_audio_string
from midi import Track, NoteOnEvent, NoteOffEvent
from numpy import append, array, ndarray, poly1d, exp, log10, sqrt, mean, pi
from generator import Generator
from thread import start_new_thread
from time import sleep
from scipy.signal import lfilter, bilinear

class Synthesizer:
    
    def __init__(self):
        self.status = False
        start_new_thread(self.init_background, ())
        (Synthesizer.ear_b, Synthesizer.ear_a) = Synthesizer.get_ear_filter()
        
    def init_background(self):
        self.synths = []
        self.sfids = []
        self.last_instruments = []
        for i in range(4):
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
        self.last_instruments = []

    def convert_pattern_to_samples(self, pattern, instruments, unit, digital_filter,
                                   left_channel_tail = None, right_channel_tail = None, 
                                   dynamic_offset = 0):        
        while self.status == False:
            sleep(0.01)
        
        resolution = pattern.resolution
        tempo = pattern[0][0].get_bpm()
        sampling_rate = 44100.0
        array_length = int(unit * 60.0 / tempo * sampling_rate)
        
        if len(instruments) >= 4:
            if len(self.last_instruments) >= 4:
                instrument_ids = [ins['ID'] for ins in [instruments[0], self.last_instruments[0], instruments[1], self.last_instruments[1]]]
                # gradually change
                if len(set(instrument_ids)) >= 4:
                    instruments[1] = instruments[0]
                    instruments[0] = self.last_instruments[1]
            self.last_instruments = [instruments[0], instruments[1], instruments[2], instruments[3]]
            print 'Melody: ' + instruments[0]['Name'] + ', ' + instruments[1]['Name']
            print 'Harmony: ' + instruments[2]['Name'] + ', ' + instruments[3]['Name']
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
                    self.synths[i].noteon(event.channel, event.pitch, event.velocity)
                if type(event) is NoteOffEvent:
                    self.synths[i].noteoff(event.channel, event.pitch)
            if len(sample) < array_length * 2:
                sample = append(sample, self.synths[i].get_samples(array_length - len(sample) / 2))
            samples.append(sample)
                
        # combine different instruments
        samples[0] *= 1.0 / pow(2, 0.5)
        samples[1] *= 1.0 / pow(2, 0.5)
        combined_samples = samples[0]
        for i in range(1, len(samples)):
            combined_samples += samples[i]
        
        # filter
        num_samples_mono = len(combined_samples) / 2
        num_samples_tail = int(sampling_rate * 0.1)
        reshaped_samples = combined_samples.reshape(num_samples_mono, 2)
        left_channel = list(reshaped_samples[:, 0]) + [0] * num_samples_tail
        right_channel = list(reshaped_samples[:, 1]) + [0] * num_samples_tail
        left_channel = lfilter(digital_filter['b'], digital_filter['a'], left_channel)
        right_channel = lfilter(digital_filter['b'], digital_filter['a'], right_channel)
        
        # calculate the perceptual volume
        frame_length = 1024
        c = exp(-1.0/frame_length)
        (ear_b, ear_a) = (Synthesizer.ear_b, Synthesizer.ear_a)
        ear_filtered_left_square = lfilter(ear_b, ear_a, left_channel) ** 2
        ear_filtered_right_square = lfilter(ear_b, ear_a, right_channel) ** 2
        vms_left = lfilter([1-c], [1, -c], ear_filtered_left_square[:num_samples_mono])
        vms_right = lfilter([1-c], [1, -c], ear_filtered_right_square[:num_samples_mono])
        
        # average the top 20% and calculate the normalization factor
        iterator = xrange(frame_length - 1, num_samples_mono, frame_length)
        vdB = [10.0 * log10(max(vms_left[i], vms_right[i])) for i in iterator]         
        vdB.sort(reverse = True)
        
        original_volume = mean(vdB[0:len(vdB)/5])
        desired_volume = (60 + dynamic_offset * 0.2) if dynamic_offset > -50 else 0
        ratio = sqrt(pow(10, (desired_volume - original_volume) / 10.0))
        max_ratio = (pow(2.0, 15) - 1) / max(max(abs(left_channel)), max(abs(right_channel)))
        ratio = min(ratio, max_ratio)
        
        # normalize the left channel and the right channel
        left_channel *= ratio
        right_channel *= ratio
        
        # add the previous filter results in order to make the transition smooth
        if left_channel_tail is not None and right_channel_tail is not None:
            left_channel[:num_samples_tail] += left_channel_tail
            right_channel[:num_samples_tail] += right_channel_tail
            
        combined_samples = ndarray([num_samples_mono, 2])
        combined_samples[:, 0] = left_channel[:num_samples_mono]
        combined_samples[:, 1] = right_channel[:num_samples_mono]
        combined_samples = combined_samples.flatten()
        
        # keep the filter tail
        left_channel_tail = array(left_channel[-num_samples_tail:])
        right_channel_tail = array(right_channel[-num_samples_tail:])
        return raw_audio_string(combined_samples), left_channel_tail, right_channel_tail
    
    @staticmethod
    def get_ear_filter():
        sampling_rate = 44100
        cut_off_1 = 80
        cut_off_2 = 500
        cut_off_3 = 5000
        
        analog_b_1 = [1, 0]
        analog_a_1 = [1, float(cut_off_1) / sampling_rate * 2 * pi]
        analog_a_2 = [1, float(cut_off_2) / sampling_rate * 2 * pi]
        analog_a_3 = [1, float(cut_off_3) / sampling_rate * 2 * pi]
        analog_b = poly1d(analog_b_1) ** 3
        analog_a = (poly1d(analog_a_1) ** 2) * poly1d(analog_a_2) * poly1d(analog_a_3)       
        (ear_b, ear_a) = bilinear(analog_b, analog_a)
        return (ear_b, ear_a)