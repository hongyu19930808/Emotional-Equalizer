from scipy import signal
from numpy import pi, log10, poly1d
from matplotlib import pyplot

"""
       b[0]*(s)**M + b[1]*(s)**(M-1) + ... + b[M]
H(s) = ------------------------------------------
       a[0]*(s)**N + a[1]*(s)**(N-1) + ... + a[N]    
"""
cut_off = 1000
sampling_rate = 44100

analog_b = [1]
analog_a = [1 / (float(cut_off) / sampling_rate * 2 * pi), 1]
start_freq = pi / pow(2.0, 12)
worN = [start_freq * pow(2, i / 10.0) for i in xrange(120)]
(w, h) = signal.freqs(analog_b, analog_a, worN)

# the frequency transformation is not linear and high frequency will be lowered.
(digital_b, digital_a) = signal.bilinear(analog_b, analog_a)
(w, h) = signal.freqz(digital_b, digital_a, worN)

(ear_b_high, ear_a_high) = signal.butter(1, 0.02, btype = 'high')
(ear_b_low, ear_a_low) = signal.butter(1, 0.6, btype = 'low')
ear_b = poly1d(ear_b_high) * poly1d(ear_b_low)
ear_a = poly1d(ear_a_high) * poly1d(ear_a_low)
(w, h) = signal.freqz(ear_b, ear_a, worN)

fig = pyplot.figure()
plt = fig.add_subplot(111)
plt.set_title("Frequency Response" )
plt.set_xlabel('Frequency [Hz]')
plt.set_ylabel('Normalized Amplitude [dB]')         
plt.set_xscale('log')
plt.plot(w / (2 * pi) * sampling_rate, 20 * log10(abs(h)), color = 'blue')
plt.grid()
pyplot.show()