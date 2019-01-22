from mood import Mood
import mt_tkinter as tk

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
        self.mood_index = tk.IntVar(master = frame, value = 0)
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
        
        self.main_ui.center_window(self.root, 280, 0)
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