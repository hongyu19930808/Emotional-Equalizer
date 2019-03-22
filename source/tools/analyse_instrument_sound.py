import wave
import struct
import numpy
import pylab
import sys
import scipy.signal

class Instrument(object):
    
    def __init__(self, path = None):
        self._samples = []
        self._frame_rate = 44100
        self._attack_time = None
        self._volume_dB = None
        self._decay_dB = None
        self._abs_fft_results = None
        self._frequency_interval = None
        self._centroid = None
        self._spectrum_std = None
        self._spectrum_percentile = None
        self._name = ''
        if path != None:
            self._read_samples(path)
            self._gen_loudness_info()
            self._cal_decay_dB()
            self._fft(0, self._attack_time)
            self._calculate_centroid()
            self._calculate_spectrum_std()
            self._calculate_spectrum_percentile()
            
    def _gen_loudness_info(self):
        frame_length = 1024
        c = numpy.exp(-1.0/frame_length)
        (ear_b, ear_a) = Instrument.get_ear_filter()
        ear_filtered_square = scipy.signal.lfilter(ear_b, ear_a, self._samples) ** 2
        vms = scipy.signal.lfilter([1-c], [1, -c], ear_filtered_square)
        # calculate attack time
        local_maximum = []
        for i in xrange(1, len(vms) - 1):
            if vms[i] >= vms[i-1] and vms[i] >= vms[i+1]:
                local_maximum.append(i)
        max_vms = max(vms)
        for i in xrange(len(local_maximum)):
            if vms[local_maximum[i]] <= 0.25 * max_vms:
                continue
            attack_flag = True
            for j in xrange(i+1, len(local_maximum)):
                if local_maximum[j] - local_maximum[i] > 0.1 * self._frame_rate:
                    break
                if vms[local_maximum[i]] < vms[local_maximum[j]]:
                    attack_flag = False
                    break
            if attack_flag == True:
                self._attack_time = local_maximum[i] / float(self._frame_rate)
                break
        # calculate volume
        self._volume_dB = 10.0 * numpy.log10(vms + sys.float_info.epsilon)
            
    def _cal_decay_dB(self):
        index = len(self._volume_dB) - 1
        results = [(index + 1) / float(self._frame_rate)] * 61
        current_decay = 60
        max_volume = max(self._volume_dB)
        while index >= 0 and current_decay > sys.float_info.epsilon:
            if max_volume - self._volume_dB[index] > current_decay:
                results[current_decay] = index / float(self._frame_rate)
                index -= 1
            else:
                current_decay -= 1
                results[current_decay] = results[current_decay+1]
        results[0] = self._volume_dB.argmax() / float(self._frame_rate)
        self._decay_dB = results
        
    @staticmethod
    def get_ear_filter():
        sampling_rate = 44100
        cut_off_1 = 80
        cut_off_2 = 500
        cut_off_3 = 5000
        
        analog_b_1 = [1, 0]
        analog_a_1 = [1, float(cut_off_1) / sampling_rate * 2 * numpy.pi]
        analog_a_2 = [1, float(cut_off_2) / sampling_rate * 2 * numpy.pi]
        analog_a_3 = [1, float(cut_off_3) / sampling_rate * 2 * numpy.pi]
        analog_b = numpy.poly1d(analog_b_1) ** 3
        analog_a = (numpy.poly1d(analog_a_1) ** 2) * numpy.poly1d(analog_a_2) * numpy.poly1d(analog_a_3)       
        (ear_b, ear_a) = scipy.signal.bilinear(analog_b, analog_a)
        return (ear_b, ear_a)    
            
    def cumulative_percentage(self, lower_frequency = 0, upper_frequency = 22050):
        if self._abs_fft_results is None or self._frequency_interval is None:
            self._fft()
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        lower_index = max(0, int(numpy.ceil(lower_frequency / frequency_interval)))
        upper_index = min(len(abs_fft) - 1, int(numpy.floor(upper_frequency / frequency_interval)))
        return round(100.0 * sum(abs_fft[lower_index:upper_index+1]) / sum(abs_fft), 2)
    
    @property
    def spectral_flatness(self):
        if self._abs_fft_results is None or self._frequency_interval is None:
            self._fft()
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        numerator = numpy.exp(numpy.mean(2 * numpy.log(abs_fft)))
        dominator = numpy.mean(abs_fft ** 2)
        return numpy.log10(numerator / dominator) * 10
        
    def plot_spectrum(self, save = True, show = True):
        if self._abs_fft_results is None or self._frequency_interval is None:
            self._fft()
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        fundamental_frequency = 220 * pow(2, 0.25)
        x_value = numpy.array(range(len(abs_fft))) * frequency_interval / fundamental_frequency
        y_value = abs_fft
        thershold = 0
        index = len(abs_fft) - 1
        while True:
            if y_value[index] >= thershold:
                break
            index -= 1
        plot = pylab.subplot(111)
        plot.plot(x_value[:index+1], y_value[:index+1])
        if save == True:
            pylab.savefig('./spectrum/instrument_' + str(self._name).zfill(3) + '.png', dpi = 300)        
        if show == True:
            pylab.show()
        pylab.clf()
            
    def _calculate_spectrum_percentile(self):
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        sum_abs_fft = sum(abs_fft)
        sum_percentile = [sum_abs_fft * i / 100 for i in xrange(100)]
        percentile = 1
        sum_abs_fft = 0
        self._spectrum_percentile = [0]
        for i in xrange(len(abs_fft)):
            sum_abs_fft += abs_fft[i]
            while percentile < 100 and sum_abs_fft >= sum_percentile[percentile]:
                self._spectrum_percentile.append(i * frequency_interval)
                percentile += 1
            if percentile == 100:
                break
    
    def _calculate_centroid(self):
        numerator = 0
        dominator = 0
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        for i in xrange(len(abs_fft)):
            numerator += (abs_fft[i] * i * frequency_interval)
            dominator += abs_fft[i]
        self._centroid = numerator / dominator
        return self._centroid
    
    def _calculate_spectrum_std(self):
        if self._centroid is None:
            self._calculate_centroid()
        numerator = 0
        dominator = 0
        abs_fft = self._abs_fft_results
        frequency_interval = self._frequency_interval
        # Var(X) = E(X*X) - E(X)*E(X)
        for i in xrange(len(abs_fft)):
            numerator += (abs_fft[i] * ((i * frequency_interval) ** 2))
            dominator += abs_fft[i]
        self._spectrum_std = numpy.sqrt(numerator / dominator - self._centroid ** 2)
        return self._spectrum_std
    
    def _fft(self, start_time = None, end_time = None):
        if len(self.samples) == 0:
            raise(Exception("No Instrument's Data"));
        samples = self._samples
        start_index = 0 if start_time is None else max(0, int(start_time * self._frame_rate))
        end_index = len(samples) if end_time is None else max(0, int(end_time * self._frame_rate))
        samples = samples[start_index:end_index]
        samples *= numpy.hamming(end_index - start_index)
        self._abs_fft_results = abs(numpy.fft.rfft(samples)) / len(samples)
        self._frequency_interval = float(self._frame_rate) / len(samples)
    
    def _read_samples(self, path):
        wavefile = wave.open(path, 'r')
        num_frames = wavefile.getnframes()
        frame_rate = wavefile.getframerate()
        samples = numpy.zeros(num_frames)
        all_value_str = wavefile.readframes(num_frames)
        for i in xrange(num_frames):
            left = all_value_str[i*4:i*4+2]
            value = struct.unpack('h', left)[0]
            samples[i] = value
        wavefile.close()
        samples = samples / pow(2.0, 15)
        self._samples = samples
        self._frame_rate = frame_rate
        return samples
    
    @staticmethod
    def info():
        elements = ['Ins ID', 'Centroid (Log)', 'Spectrum Std (Log)', 'Flatness (dB)', 
                    '50% Percentile (Log)', '85% Percentile (Log)', '50-200', '200-500',
                    '500-2000', '2000-5000', '5000-20000', 'Attack Time', 
                    '5dB Decay', '10dB Decay', '15dB Decay', '20dB Decay', '30dB Decay', '40dB Decay']
        final_str = ''
        for element in elements[:-1]:
            final_str += str(element)
            final_str += ','
        final_str += str(elements[-1])
        return final_str        
        
    def __str__(self):
        elements = []
        elements.append(self._name)
        elements.append(round(numpy.log(self._centroid), 2))
        elements.append(round(numpy.log(self._spectrum_std), 2))
        elements.append(round(self.spectral_flatness, 2))
        elements.append(round(numpy.log(self._spectrum_percentile[50]), 2))
        elements.append(round(numpy.log(self._spectrum_percentile[85]), 2))
        elements.append(self.cumulative_percentage(50, 200))
        elements.append(self.cumulative_percentage(200, 500))
        elements.append(self.cumulative_percentage(500, 2000))
        elements.append(self.cumulative_percentage(2000, 5000))
        elements.append(self.cumulative_percentage(5000, 20000))
        elements.append(round(self._attack_time, 4))
        elements.append(round(self._decay_dB[5], 4))
        elements.append(round(self._decay_dB[10], 4))
        elements.append(round(self._decay_dB[15], 4))
        elements.append(round(self._decay_dB[20], 4))
        elements.append(round(self._decay_dB[30], 4))
        elements.append(round(self._decay_dB[40], 4))
        final_str = ''
        for element in elements[:-1]:
            final_str += str(element)
            final_str += ','
        final_str += str(elements[-1])
        return final_str
    
    def cmp_by_centroid(self, other):
        if self._centroid < other.centroid:
            return -1
        elif self._centroid == other.centroid:
            return 0
        else:
            return 1
        
    def cmp_by_median(self, other):
        if self._spectrum_percentile[50] < other._spectrum_percentile[50]:
            return -1
        elif self._spectrum_percentile[50] == other._spectrum_percentile[50]:
            return 0
        else:
            return 1
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = str(value)
        
    @property
    def centroid(self):
        return self._centroid
    
    @property
    def samples(self):
        return self._samples
    
    @property
    def frame_rate(self):
        return self._frame_rate
    
    @property
    def spectrum_percentile(self):
        return self._spectrum_percentile

if __name__ == '__main__':
    #fout = open('instruments_info_spectrum.csv', 'w')
    #fout.write(Instrument.info() + '\n')
    num_instruments = 128
    for ins_id in xrange(num_instruments):
        instrument = Instrument('./sounds/instrument_' + str(ins_id).zfill(3) + '.wav')
        instrument.name = str(ins_id)
        #fout.write(str(instrument))
        #if ins_id < num_instruments - 1:
            #fout.write('\r\n')
        #instrument.plot_spectrum(save = True, show = False)
    #fout.close()