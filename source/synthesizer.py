from midi_operation import MIDI
from fluidsynth import Synth, raw_audio_string
from midi import Track, NoteOnEvent, NoteOffEvent
from numpy import append, array, ndarray, poly1d, exp, log10, sqrt, mean, pi, minimum, maximum, cos
from generator import Generator
from thread import start_new_thread
from time import sleep
from scipy.signal import lfilter, bilinear

class Synthesizer:
    
    def __init__(self):
        self.status = False
        self.last_instruments = []
        self.trans = 0
        self.last_ratio = 1.0
        self.left_channel_tail = None
        self.right_right_tail = None
        self.digital_filter = {'b': [1], 'a': [1]}
        self.overdriven_coeff = 1.0
        self.reverb_delay_time = 0
        self.reverb_amount = 0       
        start_new_thread(self.init_background, ())
        (Synthesizer.ear_b, Synthesizer.ear_a) = Synthesizer.get_ear_filter()
        
    def init_background(self):
        self.synths = []
        self.sfids = []
        for i in range(6):
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
        self.trans = 0
        self.last_ratio = 1.0
        self.left_channel_tail = None
        self.right_right_tail = None
        self.digital_filter = {'b': [1], 'a': [1]}
        self.overdriven_coeff = 1.0

    def convert_pattern_to_samples(self, pattern, instruments, unit, dynamic_offset = 0):   

        while self.status == False:
            sleep(0.01)
        
        resolution = pattern.resolution
        tempo = pattern[0][0].get_bpm()
        sampling_rate = 44100.0
        array_length = int(unit * 60.0 / tempo * sampling_rate)
        digital_filter = self.digital_filter
        
        if len(instruments) < 3:
            print 'error in loading instruments'
            
        num_bars_trans = 4
        if len(self.last_instruments) != 0 and \
           ((self.last_instruments[0]['ID'] != instruments[0]['ID']) or \
           (self.last_instruments[1]['ID'] != instruments[1]['ID']) or \
           (self.last_instruments[2]['ID'] != instruments[2]['ID'])):
            instruments.append(self.last_instruments[0])
            instruments.append(self.last_instruments[1])
            instruments.append(self.last_instruments[2])
            pattern.append(MIDI.copy_track(pattern[0], channel_offset = 3))
            pattern.append(MIDI.copy_track(pattern[1], channel_offset = 3))
            pattern.append(MIDI.copy_track(pattern[2], channel_offset = 3))
        
            # whether in transition state or not, 0 is not a transition state
            if self.trans == 0:
                self.trans = num_bars_trans
        
        if self.trans > 0:
            self.trans -= 1
        if self.trans <= 0:
            if len(self.last_instruments) == 0:
                self.last_instruments.append(instruments[0])
                self.last_instruments.append(instruments[1])
                self.last_instruments.append(instruments[2])
            else:
                self.last_instruments[0] = instruments[0]
                self.last_instruments[1] = instruments[1]
                self.last_instruments[2] = instruments[2]
        
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
                    self.synths[i].noteon(event.channel, event.pitch, event.velocity)
                if type(event) is NoteOffEvent:
                    self.synths[i].noteoff(event.channel, event.pitch)
            if len(sample) < array_length * 2:
                sample = append(sample, self.synths[i].get_samples(array_length - len(sample) / 2))
            samples.append(sample)
                
        
        # combine different instruments
        len_trans = float(array_length * 2)
        len_smooth_trans = 16.0
        smooth_dec = [(cos(i * pi / len_smooth_trans) + 1) / 2.0 for i in xrange(int(len_smooth_trans))]
        smooth_inc = [(-cos(i * pi / len_smooth_trans) + 1) / 2.0 for i in xrange(int(len_smooth_trans))]
        if len(instruments) == 6:
            coeff_fade_in = array(xrange(int(len_trans)))
            coeff_fade_in = coeff_fade_in / (len_trans * num_bars_trans) + (num_bars_trans - 1 - self.trans) / 4.0
            coeff_fade_out = array(xrange(int(len_trans), 0, -1))
            coeff_fade_out = coeff_fade_out / (len_trans * num_bars_trans) + self.trans / 4.0
            # avoid the signal suddenly change
            if self.trans == num_bars_trans - 1:
                coeff_fade_out[:len(smooth_inc)] = smooth_inc
                coeff_fade_in[:len(smooth_dec)] = smooth_dec
            
            samples[0] *= coeff_fade_in
            samples[1] *= coeff_fade_in
            samples[2] *= coeff_fade_in            
            samples[3] *= coeff_fade_out
            samples[4] *= coeff_fade_out
            samples[5] *= coeff_fade_out
            combined_samples = samples[0] + samples[1] + samples[2] + samples[3] + samples[4] + samples[5]
        else:
            combined_samples = samples[0] + samples[1] + samples[2]
        
        
        if self.trans <= 0:
            self.synths[3].system_reset()
            self.synths[4].system_reset()
            self.synths[5].system_reset()        
        
        # filter
        num_samples_mono = len(combined_samples) / 2
        num_samples_tail = int(sampling_rate * 0.5)
        reshaped_samples = combined_samples.reshape(num_samples_mono, 2)
        left_channel = array(list(reshaped_samples[:, 0]) + [0] * num_samples_tail)
        right_channel = array(list(reshaped_samples[:, 1]) + [0] * num_samples_tail)
        
        if self.overdriven_coeff < 1:
            max_amp = max(max(abs(left_channel)), max(abs(right_channel)))
            left_channel = minimum(left_channel, max_amp * self.overdriven_coeff)
            right_channel = minimum(right_channel, max_amp * self.overdriven_coeff)
        left_channel = lfilter(digital_filter['b'], digital_filter['a'], left_channel)
        right_channel = lfilter(digital_filter['b'], digital_filter['a'], right_channel)
        
        num_samples = array_length + num_samples_tail
        reverb_delay_samples = int(self.reverb_delay_time * sampling_rate)
        current_reverb_coeff = self.reverb_amount
        for i in xrange(5):
            if reverb_delay_samples >= num_samples:
                break
            left_channel[reverb_delay_samples:] += \
                (left_channel[:num_samples - reverb_delay_samples] * current_reverb_coeff)
            right_channel[reverb_delay_samples:] += \
                (right_channel[:num_samples - reverb_delay_samples] * current_reverb_coeff)
            reverb_delay_samples *= 2
            current_reverb_coeff *= current_reverb_coeff
        
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
        trans_ratio = [ratio * smooth_inc[i] + self.last_ratio * smooth_dec[i] for i in xrange(int(len_smooth_trans))]
        left_channel[:int(len_smooth_trans)] *= trans_ratio
        right_channel[:int(len_smooth_trans)] *= trans_ratio
        left_channel[:int(len_smooth_trans)] = maximum(minimum(left_channel[:int(len_smooth_trans)], pow(2.0, 15) - 1), -pow(2.0, 15) + 1)
        left_channel[:int(len_smooth_trans)] = maximum(minimum(left_channel[:int(len_smooth_trans)], pow(2.0, 15) - 1), -pow(2.0, 15) + 1)
        left_channel[int(len_smooth_trans):] *= ratio
        right_channel[int(len_smooth_trans):] *= ratio
        
        self.last_ratio = ratio
        
        # add the previous filter results in order to make the transition smooth
        if self.left_channel_tail is not None and self.right_channel_tail is not None:
            left_channel[:num_samples_tail] += self.left_channel_tail
            right_channel[:num_samples_tail] += self.right_channel_tail
            
        combined_samples = ndarray([num_samples_mono, 2])
        combined_samples[:, 0] = left_channel[:num_samples_mono]
        combined_samples[:, 1] = right_channel[:num_samples_mono]
        combined_samples = combined_samples.flatten()
        
        # keep the filter tail
        self.left_channel_tail = array(left_channel[-num_samples_tail:])
        self.right_channel_tail = array(right_channel[-num_samples_tail:])
        
        return raw_audio_string(combined_samples)
    
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