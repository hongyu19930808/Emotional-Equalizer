import mt_tkinter as tk

class InfoUI:

    @staticmethod
    def is_num(string):
        try:
            value = float(string)
            return True
        except:
            return False

    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.pop_up_box(main_ui.root)

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
        
        self.main_ui.center_window(self.root)
        self.root.resizable(False, False)
        self.unit_entry.focus()
        self.root.mainloop()
        return