from controller import Controller
from mood import Mood
from tkFileDialog import askopenfilename
from numpy import mean
from ui_schedule import ScheduleUI
from ui_info import InfoUI
import mt_tkinter as tk

class EqualizerUI:
    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.pop_up_box(main_ui.root)
        
    def pop_up_box(self, main_form):
        self.root = tk.Toplevel(master = main_form)

class MainUI:
    
    @staticmethod
    def center_window(root, offset_x = 0, offset_y = 0):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.update_idletasks()
        root.withdraw()
        root.geometry('%sx%s+%s+%s' % (root.winfo_width(), root.winfo_height(),
                                       (screen_width - root.winfo_width()) / 2 + offset_x, 
                                       (screen_height - root.winfo_height()) /2 + offset_y) )
        root.deiconify()      
    
    def __init__(self):
        self.root = None
        self.progress_scale = None
        self.play_pause_button = None
        self.mood_labels = []
        self.mood_scales = []
        self.key_state = {}
        self.controller = Controller(self)
        self.schedule_ui = None
        self.canvas_data = None
        self.song_length = -1
        self.state = 'normal'
        self.gui()
        
    def value_changed(self, event):
        maintained_index = event
        mood_data = []
        for i in range(len(self.mood_scales)):
            mood_data.append(100 - self.mood_scales[i].get())
        
        for i in range(len(self.mood_scales)):
            self.mood_scales[i].set(100 - mood_data[i])
            self.mood_labels[i]['text'] = Mood.mood_strs[i] + ': ' + str(100 - self.mood_scales[i].get())
        
    def value_determined(self, event):
        maintained_index = self.mood_scales.index(event.widget) 
        mood_data = []
        for i in range(len(self.mood_scales)):
            mood_data.append(100 - self.mood_scales[i].get())
        
        mood = {}
        for i in range(len(self.mood_scales)):
            mood[Mood.mood_strs[i]] = mood_data[i]
        self.controller.mood_change(mood)
        
    def get_mood_from_schedule(self, index, num_chord):
        result = {}
        for mood in Mood.mood_strs:
            result[mood] = None
        if index >= num_chord or self.schedule_ui == None:
            return result
        
        mood_values = {}
        for mood in Mood.mood_strs:
            mood_values[mood] = []
            
        start_position = int(float(index) / float(num_chord) * self.schedule_ui.canvas_resolution)
        end_position = int(float(index + 1) / float(num_chord) * self.schedule_ui.canvas_resolution)
        for i in xrange(self.schedule_ui.canvas_resolution):
            for j in xrange(start_position, end_position):
                for k in xrange(len(Mood.mood_strs)):
                    if self.schedule_ui.canvas_data[i][j] & pow(2, k) != 0:
                        mood = Mood.mood_strs[k]
                        mood_values[mood].append(self.schedule_ui.canvas_resolution - 1 - i)
        
        for mood in Mood.mood_strs:
            if len(mood_values[mood]) != 0:
                result[mood] = mean(mood_values[mood]) * 100.0 / (self.schedule_ui.canvas_resolution - 1)
                result[mood] = max(0, min(int(round(result[mood])), 100))
        return result
        
    def set_mood_scales(self, mood_data):
        for i in range(len(Mood.mood_strs)):
            mood = Mood.mood_strs[i]
            if mood_data[mood] != None:
                self.mood_scales[i].set(100 - mood_data[mood])
                self.mood_labels[i]['text'] = Mood.mood_strs[i] + ': ' + str(mood_data[mood])
        
    def tempo_changed(self, event):
        value = self.tempo_scale.get()
        value = pow(2, value / 50.0 - 1)
        self.controller.tempo_change(value)
        
    def progress_scale_pressed(self, event):
        if self.get_state(self.progress_scale) == True:
            self.controller.pause()    
    
    def progress_scale_released(self, event):
        if self.get_state(self.progress_scale) == True:
            self.controller.set_pos(self.progress_scale.get())
    
    def open_clicked(self):
        self.root.withdraw()
        path = askopenfilename(filetypes = [('MIDI File', '.mid'), 
                                                 ('MIDI File', '.midi')], 
                               initialdir = '../midi/')
        if path == None or path == '':
            self.root.update()
            self.root.deiconify()        
            return
        
        info_ui = InfoUI(self)
        unit = info_ui.get_unit()
        offset = info_ui.get_offset()
        result = self.controller.open(path, unit, offset)
        if result == True:
            self.play_pause_button['text'] = 'Play'
            self.play_pause_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.NORMAL
            self.change_button['state'] = tk.NORMAL
        self.root.update()
        self.root.deiconify()
    
    def get_unit_offset(self):
        self.root.withdraw()
        info_ui = InfoUI(self, self.root)
        unit = info_ui.get_unit()
        offset = info_ui.get_offset()
        self.root.update()
        self.root.deiconify()        
        return (unit, offset)
    
    def set_state(self, widget, state):
        if state == False:
            widget['state'] = tk.DISABLED
        else:
            widget['state'] = tk.NORMAL
            
    def get_state(self, widget):
        if widget['state'] == tk.DISABLED:
            return False
        else:
            return True
    
    def init_progress_scale(self, length):
        self.progress_scale['from'] = 0
        self.progress_scale['to'] = length
        self.set_state(self.progress_scale, True)
        if self.schedule_ui != None:
            self.schedule_ui.progress_scale['from'] = 0
            self.schedule_ui.progress_scale['to'] = length
            self.set_state(self.schedule_ui.progress_scale, True)
    
    def update_progress_scale(self, index):
        self.progress_scale.set(index)
        if self.schedule_ui != None:
            self.schedule_ui.progress_scale.set(index)
    
    def play_pause_clicked(self):
        if self.play_pause_button['text'] == 'Play':
            self.play_pause_button['text'] = 'Pause'
            self.controller.play()
        else:
            self.play_pause_button['text'] = 'Play'
            self.controller.pause()
    
    def stop_clicked(self):
        self.play_pause_button['text'] = 'Play'
        self.controller.stop()
    
    def change_clicked(self, event):
        mood = {}
        for i in range(len(self.mood_scales)):
            mood[Mood.mood_strs[i]] = 100 - self.mood_scales[i].get()
        self.controller.mood_change(mood, increase_seed = 3)
        
    def control_change_clicked(self, event):
        mood = {}
        for i in range(len(self.mood_scales)):
            mood[Mood.mood_strs[i]] = 100 - self.mood_scales[i].get()
        self.controller.mood_change(mood, increase_seed = 1) 
        
    def reset(self):
        mood = {}
        for i in range(len(self.mood_scales)):
            self.mood_scales[i].set(50)
            mood[Mood.mood_strs[i]] = 50
        self.controller.mood_change(mood)
        
    def schedule(self):
        MainUI.center_window(self.root, -280, 0)
        self.schedule_ui = ScheduleUI(self)
        self.schedule_button['state'] = tk.DISABLED
        self.schedule_ui.root.mainloop()
        # when schedule user interface quit
        if self.state == 'normal':
            MainUI.center_window(self.root)
            self.root.focus()
            self.schedule_ui = None
            self.schedule_button['state'] = tk.NORMAL
        else:
            self.root.quit()
    
    @staticmethod
    def get_keysym(keycode):
        keysym_map_mac = {131074: 'Shift_L', 131076: 'Shift_R', 
                          262145: 'Control', 524320: 'Option_L', 
                          1048584: 'Command_L', 1048592: 'Command_R',
                          524352: 'Option_R'}
        if keysym_map_mac.has_key(keycode):
            return keysym_map_mac[keycode]
        else:
            return str(keycode)
    
    def key_press_event(self, event):
        if event.keysym == '??':
            event.keysym = MainUI.get_keysym(event.keycode)        
        self.key_state[event.keysym] = 1
        
    def key_release_event(self, event):
        if event.keysym == '??':
            event.keysym = MainUI.get_keysym(event.keycode)        
        self.key_state[event.keysym] = 0
    
    def gui(self):
        self.root = tk.Tk()
        self.root.title('')
        self.root.protocol('WM_DELETE_WINDOW', self.quit_program)
        # self.root.bind(sequence = '<KeyPress>', func = self.key_press_event)
        # self.root.bind(sequence = '<KeyRelease>', func = self.key_release_event)
        
        # set pad
        frame = tk.Frame(master = self.root)
        frame.grid(padx = 8, pady = 16)
        
        # set title
        title_label = tk.Label(master = frame, font = ('Arial', 20),
                               text = 'Emotional Equalizer')
        title_label.grid(row = 0, column = 0, columnspan = 5) 
        tk.Label(master = frame, font = ('Arial', 8)).grid(row = 1, column = 0, columnspan = 5)    
        # mood scales and labels
        mood_positions = [(2, 0), (2, 1), (2, 3), (2, 4), (5, 0), (5, 1), (5, 3), (5, 4)]
        for i in range(len(Mood.mood_strs)):
            self.mood_scales.append(tk.Scale(master = frame, length = 150, resolution = 1,
                                       from_ = 0, to = 100, orient = tk.VERTICAL,
                                       showvalue = False, repeatinterval = 1))
            self.mood_scales[i].bind('<ButtonRelease>', self.value_determined)
            self.mood_scales[i].set(50)
            self.mood_scales[i].grid(row = mood_positions[i][0], column = mood_positions[i][1])
            self.mood_labels.append(tk.Label(master = frame, font = ('Arial', 15), height = 2, width = 15,
                                       text = Mood.mood_strs[i] + ': ' + str(100 - self.mood_scales[i].get())))
            self.mood_labels[i].grid(row = mood_positions[i][0] + 1, column = mood_positions[i][1])

        self.mood_scales[0]['command'] = lambda x: self.value_changed(event = 0)
        self.mood_scales[1]['command'] = lambda x: self.value_changed(event = 1)
        self.mood_scales[2]['command'] = lambda x: self.value_changed(event = 2)
        self.mood_scales[3]['command'] = lambda x: self.value_changed(event = 3)
        self.mood_scales[4]['command'] = lambda x: self.value_changed(event = 4)
        self.mood_scales[5]['command'] = lambda x: self.value_changed(event = 5)
        self.mood_scales[6]['command'] = lambda x: self.value_changed(event = 6)
        self.mood_scales[7]['command'] = lambda x: self.value_changed(event = 7)
            
        horizontal_line = tk.Label(master = frame, font = ('Arial', 8), anchor = tk.N, 
                                   height = 2, text = '  *  ' * 20 + '  ' + '  *  ' * 20)
        horizontal_line.grid(row = 4, column = 0, columnspan = 5)
        vertical_line = tk.Label(master = frame, font = ('Arial', 8), 
                                 text = '*\n' * 20 + '\n\n' + '*\n'* 20)
        vertical_line.grid(row = 2, column = 2, rowspan = 5)    
        
        # progress scale
        tk.Label(master = frame, font = ('Arial', 8)).grid(row = 7, column = 0, columnspan = 5) 
        self.progress_scale = tk.Scale(master = frame, length = 465, resolution = 1, showvalue = True,
                                  orient = tk.HORIZONTAL, repeatinterval = 1, state = tk.DISABLED)
        self.progress_scale.grid(row = 8, column = 0, columnspan = 5)
        self.progress_scale.bind('<ButtonPress>', self.progress_scale_pressed)
        self.progress_scale.bind('<ButtonRelease>', self.progress_scale_released)
        tk.Label(master = frame, font = ('Arial', 4)).grid(row = 9, column = 0, columnspan = 5)    
        
        # buttons
        button_width = 6
        self.open_button = tk.Button(master = frame, text = 'Open', width = button_width,
                                command = self.open_clicked)
        self.open_button.grid(row = 10, column = 0)
        self.play_pause_button = tk.Button(master = frame, text = 'Play', width = button_width,
                                      command = self.play_pause_clicked, state = tk.NORMAL)
        self.play_pause_button.grid(row = 10, column = 1)
        self.stop_button = tk.Button(master = frame, text = 'Stop', width = button_width,
                                command = self.stop_clicked, state = tk.NORMAL)
        self.stop_button.grid(row = 10, column = 3)
        self.change_button = tk.Button(master = frame, text = 'Change', width = button_width,
                                  state = tk.NORMAL)
        self.change_button.bind('<Button-1>', self.change_clicked)
        self.change_button.bind('<Control-Button-1>', self.control_change_clicked)
        self.change_button.grid(row = 10, column = 4)
        
        tk.Label(master = frame, font = ('Arial', 1)).grid(row = 11, column = 0, columnspan = 5)
        
        self.reset_button = tk.Button(master = frame, text = 'Reset', width = button_width, command = self.reset)
        self.reset_button.grid(row = 12, column = 0)
        self.schedule_button = tk.Button(master = frame, text = 'Schedule', width = button_width, command = self.schedule)
        self.schedule_button.grid(row = 12, column = 1)
        
        
        speed_frame = tk.Frame(master = frame)
        speed_frame.grid(row = 12, column = 3, columnspan = 2)
        self.tempo_label = tk.Label(master = speed_frame, font = ('Arial', 15), text = 'Speed ')
        self.tempo_label.grid(row = 0, column = 0, columnspan = 1)
        self.tempo_scale = tk.Scale(master = speed_frame, length = 150, resolution = 1, showvalue = False,
                                  orient = tk.HORIZONTAL, repeatinterval = 1, from_ = 0, to = 100)
        self.tempo_scale.set(50)
        self.tempo_scale.grid(row = 0, column = 1, columnspan = 2)
        self.tempo_scale.bind('<ButtonRelease>', self.tempo_changed)
        
        # setting
        MainUI.center_window(self.root)
        self.root.resizable(False, False)
        self.root.focus()
        self.root.mainloop()
    
    def quit_program(self):
        self.state = 'exited'
        if self.schedule_ui != None:
            # After executing these codes, it will continue to executing the function 'schedule'
            self.schedule_ui.root.withdraw()
            self.schedule_ui.root.quit()
        else:
            self.root.quit()
    
if __name__ == '__main__':
    MainUI()