from scipy import signal
from numpy import pi, log10, poly1d
from matplotlib import pyplot

"""
       b[0]*(s)**M + b[1]*(s)**(M-1) + ... + b[M]
H(s) = ------------------------------------------
       a[0]*(s)**N + a[1]*(s)**(N-1) + ... + a[N]    
"""

sampling_rate = 44100
cut_off_1 = 80
cut_off_2 = 500
cut_off_3 = 5000

analog_b_1 = [1, 0]
analog_a_1 = [1, float(cut_off_1) / sampling_rate * 2 * pi]
analog_a_2 = [1, float(cut_off_2) / sampling_rate * 2 * pi]
analog_a_3 = [1, float(cut_off_3) / sampling_rate * 2 * pi]
analog_b = poly1d(analog_b_1) ** 3
analog_a = (poly1d(analog_a_1) ** 2) * poly1d(analog_a_2) * (poly1d(analog_a_3))

start_freq = pi / pow(2.0, 12)
worN = [start_freq * pow(2, i / 10.0) for i in xrange(120)]
(w, h) = signal.freqs(analog_b, analog_a, worN)

# the frequency transformation is not linear and high frequency will be lowered.
(digital_b, digital_a) = signal.bilinear(analog_b, analog_a)
(w, h) = signal.freqz(digital_b, digital_a, worN)

fig = pyplot.figure()
plt = fig.add_subplot(111)
plt.set_title("Frequency Response" )
plt.set_xlabel('Frequency [Hz]')
plt.set_ylabel('Normalized Amplitude [dB]')         
plt.set_xscale('log')
plt.plot(w / (2 * pi) * sampling_rate, 20 * log10(abs(h)), color = 'blue')
plt.grid()
pyplot.show()