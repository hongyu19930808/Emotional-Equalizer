import wave
import struct
import numpy
import pylab
import librosa

class Instrument(object):
    
    def __init__(self, path = None):
        self._samples = []
        self._frame_rate = 44100
        self._abs_fft_results = None
        self._frequency_interval = None
        self._centroid = None
        self._spectrum_std = None
        self._spectrum_percentile = None
        self._name = ''
        if path != None:
            self._read_samples(path)
            self._fft()
            self._calculate_centroid()
            self._calculate_spectrum_std()
            self._calculate_spectrum_percentile()
            
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
        self._samples = samples / pow(2.0, 15)
        self._frame_rate = frame_rate
        return (self._samples, self._frame_rate)
        
    def __str__(self):
        # name_str = 'Name: ' + self._name + '\n';
        # centroid_str = 'Spectrum Centroid: ' + str(round(self._centroid, 2)) + 'Hz' + '\n'
        # median_str = 'Spectrum Median: ' + str(self._spectrum_percentile[50]) + 'Hz' + '\n'
        elements = []
        elements.append(self._name)
        elements.append(round(self._centroid, 2))
        elements.append(round(self._spectrum_std, 2))
        elements.append(round(self.spectral_flatness, 2))
        elements.append(round(self._spectrum_percentile[50], 2))
        elements.append(round(self._spectrum_percentile[85], 2))
        elements.append(self.cumulative_percentage(50, 200))
        elements.append(self.cumulative_percentage(200, 500))
        elements.append(self.cumulative_percentage(500, 2000))
        elements.append(self.cumulative_percentage(2000, 5000))
        elements.append(self.cumulative_percentage(5000, 20000))
        final_str = ''
        for element in elements:
            final_str += str(element)
            final_str += '\t'
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
    for ins_id in xrange(128):
        instrument = Instrument('./sounds/instrument_' + str(ins_id).zfill(3) + '.wav')
        instrument.name = str(ins_id)
        print instrument