from scipy import signal
import numpy as np
import mt_tkinter as tk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class EqualizerUI:
    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.fig = Figure(figsize = (10, 2))
        self.pop_up_box(main_ui.root)
    
    def add_filter(self, name, text, from_, to, column_index = 0, column_span = 1, show_switch = True):
        frame = self.frame
        self.scales[name] = tk.Scale(master = frame, length = 150, resolution = 1, 
                                     from_ = from_, to = to, orient = tk.VERTICAL)
        self.scales[name].bind('<ButtonRelease>', self.value_determined)
        self.scales[name].set(from_)
        self.scales[name].grid(row = 1, column = column_index)
        self.labels[name] = tk.Label(master = frame, text = text, width = 8, height = 2)
        self.labels[name].grid(row = 2, column = column_index)
        if show_switch == True:
            self.switch_vars[name] = tk.BooleanVar(master = frame, value = False)
            self.switches[name] = tk.Checkbutton(master = frame, variable = self.switch_vars[name],
                                                 command = self.value_determined)
            self.switches[name].grid(row = 3, column = column_index, columnspan = column_span)
            
    """
           b[0]*(s)**M + b[1]*(s)**(M-1) + ... + b[M]
    H(s) = ------------------------------------------
           a[0]*(s)**N + a[1]*(s)**(N-1) + ... + a[N]    
    """    
    def value_determined(self, event = None):
        sampling_rate = 44100.0
        analog_b = np.poly1d([1])
        analog_a = np.poly1d([1])
        if self.switch_vars['LPB'].get() == True:
            analog_b *= [1] # Numerator
            analog_a *= [1 / self.convert_radian_z_to_s(2 * np.pi * self.scales['LPB'].get() / sampling_rate), 1] # Denominator
        if self.switch_vars['LPS'].get() == True:
            l0 = 1.0
            lpi = float(np.power(10.0, self.scales['LPS'].get() / -20.0))
            analog_b *= [np.sqrt(l0*lpi), l0] # Numerator
            analog_a *= [np.sqrt(l0/lpi), 1] # Denominator
        if self.switch_vars['LPT'].get() == True:
            pole = (20.0 / sampling_rate) * 2.0 * np.pi
            zero = (20.0 / sampling_rate) * 2.0 * np.pi * pow(np.sqrt(10.0), self.scales['LPT'].get() / 20.0)
            for i in range(6):
                analog_b *= [1, self.convert_radian_z_to_s(zero)]
                analog_a *= [1, self.convert_radian_z_to_s(pole)]
                pole *= np.sqrt(10.0)
                zero *= np.sqrt(10.0)
        if self.switch_vars['HPB'].get() == True:
            analog_b *= [1, 0] # Numerator
            analog_a *= [1, self.convert_radian_z_to_s(2 * np.pi * self.scales['HPB'].get() / sampling_rate)] # Denominator
        if self.switch_vars['HPS'].get() == True:
            lpi = 1.0
            l0 = float(np.power(10.0, self.scales['HPS'].get() / -20.0))
            analog_b *= [np.sqrt(l0*lpi), l0] # Numerator
            analog_a *= [np.sqrt(l0/lpi), 1] # Denominator
        if self.switch_vars['HPT'].get() == True:
            pole = (20.0 / sampling_rate) * 2.0 * np.pi
            zero = (20.0 / sampling_rate) * 2.0 * np.pi / pow(np.sqrt(10.0), self.scales['HPT'].get() / 20.0)
            for i in range(6):
                analog_b *= [1, self.convert_radian_z_to_s(zero)]
                analog_a *= [1, self.convert_radian_z_to_s(pole)]
                pole *= np.sqrt(10.0)
                zero *= np.sqrt(10.0)
        (digital_b, digital_a) = signal.bilinear(analog_b.coeffs, analog_a.coeffs)
        
        digital_b = np.poly1d(digital_b)
        digital_a = np.poly1d(digital_a)     
        for i in xrange(4):
            if self.switch_vars['PK' + str(i + 1)].get() == True:
                center_frequency = self.scales['PK' + str(i + 1)].get()
                band_width = self.scales['PK' + str(i + 1) + '-Width'].get()
                normalized_frequency = center_frequency / float(sampling_rate) * 2
                Q = center_frequency / float(band_width)
                (pk_digital_b, pk_digital_a) = signal.iirpeak(normalized_frequency, Q)
                digital_b *= pk_digital_b
                digital_a *= pk_digital_a
        
        digital_b = digital_b.coeffs
        digital_a = digital_a.coeffs
        self.plot(digital_b, digital_a, sampling_rate)
        self.main_ui.controller.digital_filter = {'b': digital_b, 'a': digital_a}
        
    def convert_radian_s_to_z(self, w_analog, T = 1.0):
        w_digital = 2 / T * np.arctan(w_analog * T / 2.0)
        return w_digital
    
    def convert_radian_z_to_s(self, w_digital, T = 1.0):
        w_analog = 2 / T * np.tan(w_digital * T / 2.0)
        return w_analog
        
    def plot(self, digital_b, digital_a, sampling_rate):
        start_freq = np.pi / pow(2, 12)
        worN = [start_freq * pow(2, i / 10.0) for i in xrange(120)]
        (w, h) = signal.freqz(digital_b, digital_a, worN)
    
        self.fig.clear()
        plt = self.fig.add_subplot(111)
        plt.set_title("Frequency Response" )
        plt.set_xlabel('Frequency [Hz]')
        plt.set_ylabel('Normalized Amplitude [dB]')         
        plt.set_xscale('log')
        h *= (1.0 / max(abs(h)))
        plt.plot(w / (2 * np.pi) * sampling_rate, 20 * np.log10(abs(h)), color = 'blue')
        plt.grid()
        self.canvas.draw()
        
    def pop_up_box(self, main_form):
        self.root = tk.Toplevel(master = main_form)
        self.root.protocol('WM_DELETE_WINDOW', self.back_to_main_ui)
        self.root.title('')
        # set pad
        self.frame = tk.Frame(master = self.root)
        self.frame.grid(padx = 8, pady = 8)
        
        title_label = tk.Label(master = self.frame, font = ('Arial', 20),
                               text = 'Equalizer', height = 2)
        title_label.grid(row = 0, column = 0, columnspan = 14)         
        
        self.scales = {}
        self.switch_vars = {}
        self.labels = {}
        self.switches = {}
        
        # low pass butterworth
        self.add_filter('LPB', 'Low Pass\nButterworth', 400, 20, column_index = 0)
        # low pass shelving
        self.add_filter('LPS', 'Low Pass\nShelving', 1, 100, column_index = 1)
        # low pass spectral tilt
        self.add_filter('LPT', 'Low Pass\nSepc Tilt', 1, 20, column_index = 2)        
        # high pass butterworth
        self.add_filter('HPB', 'High Pass\nButterworth', 1000, 20000, column_index = 3)
        # high pass shelving
        self.add_filter('HPS', 'High Pass\nShelving', 1, 100, column_index = 4)
        # high pass spectral tilt
        self.add_filter('HPT', 'High Pass\nSpec Tilt', 1, 20, column_index = 5)
        # peak filter 1
        self.add_filter('PK1', 'Peak 1\nCenter', 20, 100, column_index = 6, column_span = 2)
        self.add_filter('PK1-Width', 'Peak 1\nBand Width', 1, 400, column_index = 7, show_switch = False)
        # peak filter 2
        self.add_filter('PK2', 'Peak 2\nCenter', 100, 500, column_index = 8, column_span = 2)
        self.add_filter('PK2-Width', 'Peak 2\nBand Width', 5, 2000, column_index = 9, show_switch = False)
        # peak filter 3
        self.add_filter('PK3', 'Peak 3\nCenter', 500, 2000, column_index = 10, column_span = 2)
        self.add_filter('PK3-Width', 'Peak 3\nBand Width', 20, 8000, column_index = 11, show_switch = False)
        # peak filter 4
        self.add_filter('PK4', 'Peak 4\nCenter', 2000, 20000, column_index = 12, column_span = 2)
        self.add_filter('PK4-Width', 'Peak 4\nBand Width', 100, 20000, column_index = 13, show_switch = False)        
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 4, column = 0, columnspan = 14, ipady = 40)        
        
        self.root.resizable(False, False)
        self.root.focus()
        self.main_ui.center_window(self.root)
        self.value_determined()
        
    def back_to_main_ui(self):
        self.root.withdraw()
        self.root.quit()