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
        self.fig = Figure(figsize = (4, 2))
        self.pop_up_box(main_ui.root)
        
    def add_filter(self, name, text, from_, to, column_index = 0, show_switch = True):
        frame = self.frame
        self.scales[name] = tk.Scale(master = frame, length = 150, resolution = 1, 
                                     from_ = from_, to = to, orient = tk.VERTICAL)
        self.scales[name].bind('<ButtonRelease>', self.value_determined)
        self.scales[name].set(from_)
        self.scales[name].grid(row = 1, column = column_index)
        self.labels[name] = tk.Label(master = frame, text = text, height = 2)
        self.labels[name].grid(row = 2, column = column_index)
        if show_switch == True:
            self.switch_vars[name] = tk.BooleanVar(master = frame, value = False)
            self.switches[name] = tk.Checkbutton(master = frame, variable = self.switch_vars[name],
                                                 command = self.value_determined)
            self.switches[name].grid(row = 3, column = column_index)
            
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
            analog_b *= [1]
            analog_a *= [1 / (2 * np.pi * self.scales['LPB'].get() / sampling_rate), 1]
        if self.switch_vars['LPS'].get() == True:
            l0 = 1.0
            lpi = float(np.power(2.0, self.scales['LPS'].get()))
            analog_b *= [np.sqrt(l0*lpi), l0] # Numerator
            analog_a *= [np.sqrt(l0/lpi), 1] # Denominator            
        if self.switch_vars['HPB'].get() == True:
            analog_b *= [1, 0]
            analog_a *= [1, 2 * np.pi * self.scales['HPB'].get() / sampling_rate]
        if self.switch_vars['HPS'].get() == True:
            lpi = 1.0
            l0 = float(np.power(2.0, self.scales['HPS'].get()))
            analog_b *= [np.sqrt(l0*lpi), l0] # Numerator
            analog_a *= [np.sqrt(l0/lpi), 1] # Denominator
        (digital_b, digital_a) = signal.bilinear(analog_b.coeffs, analog_a.coeffs)
        self.main_ui.controller.digital_filter = {'b': digital_b, 'a': digital_a}
        self.plot(digital_b, digital_a, sampling_rate)
        
    def plot(self, digital_b, digital_a, sampling_rate):
        start_freq = np.pi / pow(2, 12)
        worN = [start_freq * pow(2, i / 20.0) for i in xrange(240)]
        (w, h) = signal.freqz(digital_b, digital_a, worN)
    
        self.fig.clear()
        plt = self.fig.add_subplot(111)
        plt.set_xscale('log')
        plt.plot(w / (2 * np.pi) * sampling_rate, 20 * np.log10(abs(h)), color = 'blue')
        plt.set_title("Frequency Response" )
        plt.set_ylabel('Amplitude [dB]')
        plt.set_xlabel('Frequency [Hz]')
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
                               text = 'Equalizer')
        title_label.grid(row = 0, column = 0, columnspan = 4)         
        
        self.scales = {}
        self.switch_vars = {}
        self.labels = {}
        self.switches = {}
        
        # low pass butterworth
        self.add_filter('LPB', 'Low Pass\nButterworth', 400, 20, column_index = 0)
        # low pass shelving
        self.add_filter('LPS', 'Low Pass\nShelving', -1, -20, column_index = 1)
        # high pass butterworth
        self.add_filter('HPB', 'High Pass\nButterworth', 1000, 20000, column_index = 2)
        # high pass shelving
        self.add_filter('HPS', 'High Pass\nShelving', -1, -20, column_index = 3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row = 4, column = 0, columnspan = 4, ipadx = 120, ipady = 120)        
        
        self.root.resizable(False, False)
        self.root.focus()
        self.main_ui.center_window(self.root)
        self.value_determined()
        
    def back_to_main_ui(self):
        self.root.withdraw()
        self.root.quit()