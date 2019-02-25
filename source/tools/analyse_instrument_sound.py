import wave
import struct
import numpy
import pylab

class Instrument(object):
    
    def __init__(self, path = None):
        self._samples = []
        self._frame_rate = 44100
        self._fft_results = None
        self._frequency_interval = None
        self._centroid = None
        self._spectrum_percentile = None
        self._name = ''
        if path != None:
            self._read_samples(path)
            self._fft()
            self._calculate_centroid()
            self._calculate_spectrum_percentile()
            
    def _calculate_spectrum_percentile(self):
        fft_results = self._fft_results
        frequency_interval = self._frequency_interval
        abs_fft = abs(fft_results)
        sum_abs_fft = sum(abs_fft)
        sum_percentile = [sum_abs_fft * i / 100 for i in xrange(100)]
        percentile = 1
        sum_abs_fft = 0
        self._spectrum_percentile = [0]
        for i in xrange(len(abs_fft)):
            sum_abs_fft += abs_fft[i]
            while percentile < 100 and sum_abs_fft >= sum_percentile[percentile]:
                self._spectrum_percentile.append(i)
                percentile += 1
            if percentile == 100:
                break
    
    def _calculate_centroid(self):
        numerator = 0
        dominator = 0
        fft_results = self._fft_results
        frequency_interval = self._frequency_interval
        for i in xrange(len(fft_results)):
            numerator += (abs(fft_results[i]) * i * frequency_interval)
            dominator += abs(fft_results[i])
        self._centroid = numerator / dominator
        return self._centroid
    
    def _fft(self, skip_onset_time = 0):
        samples = self._samples * numpy.hamming(len(self._samples))
        num_frame_skipped = int(skip_onset_time * self._frame_rate)
        samples = samples[num_frame_skipped:]
        self._fft_results = numpy.fft.rfft(samples)
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
    
    def plot_spectrum(self, skip_onset_time = 0):
        samples = self._samples * numpy.hamming(len(self._samples))
        num_frame_skipped = int(skip_onset_time * self._frame_rate)
        samples = samples[num_frame_skipped:]
        fft_results = numpy.fft.rfft(samples)
        frequency_interval = float(self._frame_rate) / len(samples)
        
        x_value = numpy.array(range(len(fft_results))) * frequency_interval
        y_value = abs(fft_results)
        thershold = max(y_value) / 100.0
        index = len(fft_results) - 1
        while True:
            if y_value[index] >= thershold:
                break
            index -= 1
        plot = pylab.subplot(111)
        plot.plot(x_value[:index+1], y_value[:index+1])
        pylab.show()
        
    def __str__(self):
        name_str = 'Name: ' + self._name + '\n';
        centroid_str = 'Spectrum Centroid: ' + str(round(self._centroid, 2)) + 'Hz' + '\n'
        median_str = 'Spectrum Median: ' + str(self._spectrum_percentile[50]) + 'Hz' + '\n'
        return name_str + centroid_str + median_str
    
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
    instruments = []
    for ins_id in xrange(128):
        instrument = Instrument('./sounds/instrument_' + str(ins_id).zfill(3) + '.wav')
        instrument.name = 'Instrument ' + str(ins_id)
        instruments.append(instrument)
    instruments.sort(cmp = Instrument.cmp_by_median)
    for ins in instruments:
        print ins