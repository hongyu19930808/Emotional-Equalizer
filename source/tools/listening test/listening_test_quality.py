import tkinter as tk

check_button_vars = []
radio_button_var = []

def center_window(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.update_idletasks()
    root.withdraw()
    root.geometry('%sx%s+%s+%s' % (
        root.winfo_width(), root.winfo_height(),
        (screen_width - root.winfo_width()) / 2, 
        (screen_height - root.winfo_height()) /2
    ))
    root.deiconify()  
    
def next_excerpt():
    global check_button_vars
    for var in check_button_vars:
        print var.get(),
    print ''
    
def repeat_excerpt():
    print 'repeat'
    
def main():
    global check_button_vars, radio_button_var
    
    root = tk.Tk()
    root.title('Listening Test')
    frame = tk.Frame(master = root)
    frame.grid(padx = 20, pady = 10)
    question_label_1 = tk.Label(master = frame, text = 'What is the mood the music?', font = ('Arial', 20))
    question_label_1.grid(row = 0, column = 0, columnspan = 4)
    question_label_2 = tk.Label(master = frame, text = '(You can choose multiple moods)', font = ('Arial', 16))
    question_label_2.grid(row = 1, column = 0, columnspan = 4)
    
    check_buttons = []
    mood_strs = ['Angry', 'Scary', 'Comic', 'Happy', 'Sad', 'Mysterious', 'Romantic', 'Calm']
    for i in xrange(len(mood_strs)):
        mood = mood_strs[i]
        check_button_var = tk.IntVar(master = frame, value = 0)
        check_button = tk.Checkbutton(master = frame, text = mood, variable = check_button_var)
        check_button.grid(row = 2 + int(i / 4), column = i % 4)
        check_buttons.append(check_button)
        check_button_vars.append(check_button_var)
        
    tk.Label(master = frame, text = '', font = ('Arial', 4)).grid(row = 4, column = 0, columnspan = 4)
    question_label_3 = tk.Label(master = frame, text = 'Does it sound musical?', font = ('Arial', 20))
    question_label_3.grid(row = 5, column = 0, columnspan = 4)
    musical_frame = tk.Frame(master = frame)
    musical_frame.grid(row = 6, column = 0, columnspan = 4)
    radio_buttons = []
    radio_button_text = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']
    radio_button_var.append(tk.IntVar(master = musical_frame, value = -1))
    for i in xrange(5):
        radio_button = tk.Radiobutton(master = musical_frame, text = radio_button_text[i], 
                                      variable = radio_button_var[0], value = i)
        radio_button.grid(row = 0, column = i)
    
    repeat_button = tk.Button(master = frame, text = 'Repeat (Press R)', command = repeat_excerpt)
    repeat_button.grid(row = 7, column = 0, columnspan = 2)
    next_button = tk.Button(master = frame, text = 'Next (Press Space)', command = next_excerpt)
    next_button.grid(row = 7, column = 2, columnspan = 2)
    
    # setting
    center_window(root)
    root.resizable(False, False)
    root.focus()
    root.mainloop()

if __name__ == '__main__':
    main()
