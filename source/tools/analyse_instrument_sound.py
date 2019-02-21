import wave
import struct
import scipy
import numpy
import pylab

middle_C_freq = 440 * pow(0.5, 0.75)

for instrument in range(4):
    wavefile = wave.open('./sounds/instrument_' + str(instrument).zfill(3) + '.wav', 'r')
    nchannels = wavefile.getnchannels()
    sample_width = wavefile.getsampwidth()
    framerate = wavefile.getframerate()
    numframes = wavefile.getnframes()
    samples = numpy.zeros(numframes)
    for i in range(numframes):
        value = wavefile.readframes(1)
        left = value[0:2]
        right = value[2:4]
        num = struct.unpack('h', left)[0]
        samples[i] = num
    samples /= pow(2.0, 15)
    samples *= numpy.hamming(numframes)
    fft_result = scipy.fft(samples)
    """
    for i in range(20):
        freq = int(round((i+1) * middle_C_freq))
        print freq, abs(result[freq])
    """
    pylab.plot(abs(fft_result[:5000]))
    pylab.show()
