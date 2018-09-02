from controller import Controller
from mood import Mood
from tkFileDialog import askopenfilename
from numpy import mean
import mt_tkinter as tk

class InfoUI:

    @staticmethod
    def is_num(string):
        try:
            value = float(string)
            return True
        except:
            return False

    def __init__(self, main_form):
        self.pop_up_box(main_form)

    def input_number(self):
        if self.is_num(self.unit_entry.get().strip()) and self.is_num(self.offset_entry.get().strip()):
            if float(self.unit_entry.get().strip()) > 0 and float(self.offset_entry.get().strip()) > 0 :
                self.root.withdraw()
                self.root.quit()
        return
    
    def get_unit(self):
        return float(self.unit_entry.get().strip())
    
    def get_offset(self):
        beats_first_bar = float(self.offset_entry.get().strip())
        unit = float(self.unit_entry.get().strip())
        offset = unit - beats_first_bar
        while offset < 0:
            offset += unit
        return offset
    
    def pop_up_box(self, main_form):
        self.root = tk.Toplevel(master = main_form)
        self.root.title('')
        self.root.protocol('WM_DELETE_WINDOW', self.input_number)
        
        frame = tk.Frame(master = self.root)
        frame.grid(padx = 8, pady = 4)       
        
        tk.Label(master = frame, 
                 text = 'How many beats per chord?' + '\n' + 'Please input a positive number.'
                 ).grid(row = 0, column = 0)
        self.unit_entry = tk.Entry(master = frame, width = 21,
                                   textvariable = tk.StringVar(frame, value='2'))
        self.unit_entry.grid(row = 1, column = 0)
        
        tk.Label(master = frame,
                 text = 'How many beats in the first bar?' + '\n' + 'Please input a positive number.'
                 ).grid(row = 2, column = 0)
        self.offset_entry = tk.Entry(master = frame, width = 21, 
                                     textvariable = tk.StringVar(frame, value='2'))
        self.offset_entry.grid(row = 3, column = 0)
        button = tk.Button(master = frame, text = 'OK', width = 19, 
                           command = self.input_number)
        button.grid(row = 4, column = 0)
        
        MainUI.center_window(self.root)
        self.root.resizable(False, False)
        self.unit_entry.focus()
        self.root.mainloop()
        return
    
class ScheduleUI:
    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.pop_up_box(main_ui.root, main_ui.song_length)
        
    def pop_up_box(self, main_form, song_length):
        self.root = tk.Toplevel(master = main_form)
        self.root.protocol('WM_DELETE_WINDOW', self.back_to_main_ui)
        self.root.title('')
        
        # set pad
        frame = tk.Frame(master = self.root)
        frame.grid(padx = 8, pady = 8)
        
        # canvas
        self.canvas_offset = 3
        self.canvas_width = 552
        self.canvas_height = 492
        self.canvas = tk.Canvas(master = frame, height = self.canvas_height, width = self.canvas_width)
        self.canvas.grid(row = 0, column = 0, columnspan = len(Mood.mood_strs))
        self.canvas.bind('<B1-Motion>', self.canvas_clicked)        
        
        self.canvas_resolution = 101
        if self.main_ui.canvas_data != None:
            self.canvas_data = self.main_ui.canvas_data
        else:
            self.canvas_data = []
            for i in xrange(self.canvas_resolution):
                self.canvas_data.append([])
            for i in xrange(self.canvas_resolution):
                for j in xrange(self.canvas_resolution):
                    self.canvas_data[i].append(0)
            self.main_ui.canvas_data = self.canvas_data
        
        # progress scale
        self.progress_scale = tk.Scale(master = frame, length = self.canvas_width, resolution = 1, showvalue = True,
                                       orient = tk.HORIZONTAL, repeatinterval = 1, state = tk.DISABLED)
        self.progress_scale['from'] = 0
        if song_length != -1:
            self.progress_scale['to'] = song_length
            self.progress_scale['state'] = tk.NORMAL
        self.progress_scale.grid(row = 1, column = 0, columnspan = len(Mood.mood_strs))
        self.progress_scale.bind('<ButtonPress>', self.progress_scale_pressed)
        self.progress_scale.bind('<ButtonRelease>', self.progress_scale_released)         
        
        # radio buttons
        tk.Label(master = frame, font = ('Arial', 1)).grid(row = 2, column = 0, columnspan = len(Mood.mood_strs))
        label = tk.Label(master = frame, font = ('Arial', 15),
                         text = 'Please select the mood, and then you can draw the curve to describe its intensity')
        label.grid(row = 3, column = 0, columnspan = len(Mood.mood_strs))
        
        index = 0
        self.mood_color = ['yellow', 'magenta', 'orange', 'red', 'cyan', 'grey', 'pink', 'green']
        self.mood_index = tk.IntVar(master = frame, value = -1)
        for mood in Mood.mood_strs:
            button = tk.Radiobutton(master = frame, text = mood, background = self.mood_color[index],
                                    variable = self.mood_index, value = index)
            button.grid(row = 4, column = index)
            index += 1
        
        # clear curve buttons
        tk.Label(master = frame, font = ('Arial', 1)).grid(row = 5, column = 0, columnspan = 8)
        clear_frame = tk.Frame(master = frame)
        clear_frame.grid(row = 6, column = 0, columnspan = len(Mood.mood_strs))
        label = tk.Label(master = clear_frame, font = ('Arial', 15), text = 'Clear the curves of')
        label.grid(row = 0, column = 0)
        clear_selected_mood = tk.Button(master = clear_frame, text = 'Selected', command = self.clear_selected_clicked)
        clear_selected_mood.grid(row = 0, column = 1)
        tk.Label(master = clear_frame, font = ('Arial', 15), text = '/').grid(row = 0, column = 2)
        clear_all_moods = tk.Button(master = clear_frame, text = 'All', command = self.clear_all_clicked)
        clear_all_moods.grid(row = 0, column = 3)
        tk.Label(master = clear_frame, font = ('Arial', 15), text = 'moods from').grid(row = 0, column = 4)
        self.start_time_entry = tk.Entry(master = clear_frame, width = 3, justify = tk.CENTER, textvariable = tk.StringVar(clear_frame, value='0'))
        self.start_time_entry.grid(row = 0, column = 5)
        tk.Label(master = clear_frame, font = ('Arial', 15), text = '% to').grid(row = 0, column = 6)
        self.end_time_entry = tk.Entry(master = clear_frame, width = 3, justify = tk.CENTER, textvariable = tk.StringVar(clear_frame, value='100'))
        self.end_time_entry.grid(row = 0, column = 7)
        tk.Label(master = clear_frame, font = ('Arial', 15), text = '% of the song').grid(row = 0, column = 8)
        
        # redraw all curves
        self.clear(pow(2, 8) - 1)
        
        MainUI.center_window(self.root, 280, 0)
        self.root.resizable(False, False)
        self.root.focus()
        
    def canvas_init(self, canvas, canvas_width, canvas_height, canvas_offset):
        canvas.create_line(canvas_offset, canvas_offset, canvas_width + canvas_offset - 1, canvas_offset)
        canvas.create_line(canvas_width + canvas_offset - 1, canvas_offset, canvas_width + canvas_offset - 1, canvas_height + canvas_offset - 1)
        canvas.create_line(canvas_width + canvas_offset - 1, canvas_height + canvas_offset - 1, canvas_offset, canvas_height + canvas_offset - 1)
        canvas.create_line(canvas_offset, canvas_height + canvas_offset - 1, canvas_offset, canvas_offset)
        for i in range(1, 10):
            canvas.create_line(canvas_width * i / 10 + canvas_offset, canvas_offset, 
                               canvas_width * i / 10 + canvas_offset, canvas_height + canvas_offset - 1,
                               dash=(4, 4))
            canvas.create_line(canvas_offset, canvas_height * i / 10 + canvas_offset, 
                               canvas_width + canvas_offset - 1, canvas_height * i / 10 + canvas_offset,
                               dash=(4, 4))        
    
    def canvas_clicked(self, event):
        if self.mood_index.get() != -1:
            if event.x >= self.canvas_offset and event.x <= self.canvas_width + self.canvas_offset - 1:
                if event.y >= self.canvas_offset and event.y <= self.canvas_height + self.canvas_offset - 1:
                    color = self.mood_color[self.mood_index.get()]
                    self.canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, 
                                                 fill = color, outline = color)
                    # bit i saves the state of the mood i (0 <= i <= 7)
                    y = int(round((event.y - self.canvas_offset) * (self.canvas_resolution - 1.0) / self.canvas_height))
                    x = int(round((event.x - self.canvas_offset) * (self.canvas_resolution - 1.0) / self.canvas_width))
                    self.canvas_data[y][x] = self.canvas_data[y][x] | pow(2, self.mood_index.get())
    
    def clear(self, value):
        start = self.start_time_entry.get()
        end = self.end_time_entry.get()
        try:
            start = float(start)
            end = float(end)
            start = min(max(start, 0), 100)
            end = min(max(end, 0), 100)
        except:
            return
              
        # clear data
        start_position = int(round((start * self.canvas_resolution / 100.0)))
        end_position = int(round((end * self.canvas_resolution / 100.0)))
        for i in xrange(self.canvas_resolution):
            for j in xrange(start_position, end_position):
                self.canvas_data[i][j] = self.canvas_data[i][j] & value
        
        # redraw
        self.canvas.delete('all')
        self.canvas_init(self.canvas, self.canvas_width, self.canvas_height, self.canvas_offset)
        for i in xrange(self.canvas_resolution):
            for j in xrange(self.canvas_resolution):
                for k in xrange(len(Mood.mood_strs)):
                    if self.canvas_data[i][j] & pow(2, k) != 0:
                        color = self.mood_color[k]
                        y = i * self.canvas_height / (self.canvas_resolution - 1) + self.canvas_offset
                        x = j * self.canvas_width / (self.canvas_resolution - 1) + self.canvas_offset
                        self.canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill = color, outline = color)                        
    
    def clear_selected_clicked(self):
        index = self.mood_index.get()
        if index != -1:
            value = pow(2, len(Mood.mood_strs)) - 1 - pow(2, index)
            self.clear(value)
    
    def clear_all_clicked(self):
        self.clear(0)
    
    def progress_scale_pressed(self, event):
        if self.progress_scale['state'] != tk.DISABLED:
            self.main_ui.controller.pause()    
    
    def progress_scale_released(self, event):
        if self.progress_scale['state'] != tk.DISABLED:
            self.main_ui.controller.set_pos(self.progress_scale.get())            
    
    def back_to_main_ui(self):
        self.root.withdraw()
        self.root.quit()

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
        
        info_ui = InfoUI(self.root)
        unit = info_ui.get_unit()
        offset = info_ui.get_offset()
        self.play_pause_button['text'] = 'Play'
        self.play_pause_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.NORMAL
        self.change_button['state'] = tk.NORMAL
        self.controller.open(path, unit, offset)
        self.root.update()
        self.root.deiconify()
    
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
    
    def gui(self):
        self.root = tk.Tk()
        self.root.title('')
        self.root.protocol('WM_DELETE_WINDOW', self.quit_program)
        
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
                                      command = self.play_pause_clicked, state = tk.DISABLED)
        self.play_pause_button.grid(row = 10, column = 1)
        self.stop_button = tk.Button(master = frame, text = 'Stop', width = button_width,
                                command = self.stop_clicked, state = tk.DISABLED)
        self.stop_button.grid(row = 10, column = 3)
        self.change_button = tk.Button(master = frame, text = 'Change', width = button_width,
                                  state = tk.DISABLED)
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