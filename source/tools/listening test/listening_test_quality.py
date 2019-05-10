import mt_tkinter as tk
import os
import wave
import numpy
import struct
from random import shuffle
from pyaudio import PyAudio, paInt16
from thread import start_new_thread
from fluidsynth import raw_audio_string
from tkMessageBox import showinfo
from collections import OrderedDict

class Gender:
    Male = 'male'
    Female = 'female'

email = 'gktam@connect.ust.hk'
gender = Gender.Female
age = 23





check_button_vars = []
radio_button_var = []
all_excerpts = []
mood_records = OrderedDict()
quality_records = OrderedDict()

current_excerpt_index = -1
play_status = False
check_buttons = []
radio_buttons = []

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
    
def play_excerpt(path):
    global play_status, check_buttons, radio_buttons
    
    for check_button in check_buttons:
        check_button['state'] = tk.DISABLED
    for radio_button in radio_buttons:
        radio_button['state'] = tk.DISABLED
    
    samples = read_samples(path)
    start = 0
    frame_length = 16384
    
    audio = PyAudio()
    stream = audio.open(format = paInt16, channels = 1, rate = 44100, output = True)    
    while True:
        end = min(len(samples), start + frame_length)
        frame = samples[start:end]
        stream.write(raw_audio_string(frame))
        start += frame_length
        if start >= len(samples):
            break
        
    play_status = False
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    for check_button in check_buttons:
        check_button['state'] = tk.NORMAL
    for radio_button in radio_buttons:
        radio_button['state'] = tk.NORMAL    
    
def read_samples(path):
    wavefile = wave.open(path, 'r')
    num_frames = wavefile.getnframes()
    frame_rate = wavefile.getframerate()
    samples = numpy.zeros(num_frames)
    all_value_str = wavefile.readframes(num_frames)
    for i in xrange(num_frames):
        left = all_value_str[i*4:i*4+2]
        value = struct.unpack('h', left)[0]
        samples[i] = value
    wavefile.close()
    return samples
    
def play(excerpt_index):
    global all_excerpts, play_status
    play_status = True
    path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Test', 'excerpts', all_excerpts[excerpt_index])
    start_new_thread(play_excerpt, (path, ))
    
def next_excerpt():
    global check_button_vars, radio_button_var, current_excerpt_index, all_excerpts
    global mood_records, quality_records, play_status
    global email, gender, age
    
    if current_excerpt_index >= len(all_excerpts):
        showinfo('', 'You have finished the test. Thank you!')
        return
    
    if current_excerpt_index == -1:
        current_excerpt_index += 1
        play(current_excerpt_index)
        return
    
    quality = radio_button_var[0].get()
    current_mood = []
    for var in check_button_vars:
        current_mood.append(var.get())
    
    if quality == -1 or sum(current_mood) == 0 or play_status == True:
        return
    
    # save the results
    filename = all_excerpts[current_excerpt_index]
    mood_records[filename] = current_mood
    quality_records[filename] = quality
    current_excerpt_index += 1
    
    # reset the var
    for var in check_button_vars:
        var.set(0)
    radio_button_var[0].set(-1)
    
    # play next
    if current_excerpt_index < len(all_excerpts):
        play(current_excerpt_index)
    else:
        mood_strs = ['Angry', 'Scary', 'Comic', 'Happy', 'Sad', 'Mysterious', 'Romantic', 'Calm']
        path = '../evaluation/' + email + '-' + gender + '-' + str(age) + '.csv'
        fout = open(path, 'w')
        for mood in mood_strs:
            fout.write(',' + mood)
        fout.write(',Quality\n')
        for key in mood_records.keys():
            fout.write(key)
            for i in xrange(8):
                fout.write(',' + str(mood_records[key][i]))
            fout.write(',' + str(quality_records[key]) + '\n')
        fout.close()        
        showinfo('', 'You have finished the test. Thank you!')
    
def repeat_excerpt():
    global current_excerpt_index, all_excerpts
    if play_status == False and current_excerpt_index != -1 and current_excerpt_index < len(all_excerpts):
        play(current_excerpt_index)
    else:
        return
    
def key_press_event(event):
    if event.char == ' ':
        next_excerpt()
    if event.char.lower() == 'r':
        repeat_excerpt()
    
def main():
    global check_button_vars, radio_button_var, all_excerpts, mood_records, quality_records
    global check_buttons, radio_buttons
    
    filenames = os.listdir(os.path.join(os.path.expanduser('~'), 'Desktop', 'Test', 'excerpts'))
    for filename in filenames:
        if filename.endswith('.wav'):
            all_excerpts.append(filename)
            mood_records[filename] = None
            quality_records[filename] = None
    shuffle(all_excerpts)
    
    root = tk.Tk()
    root.title('Listening Test')
    root.bind(sequence = '<KeyPress>', func = key_press_event)
    
    frame = tk.Frame(master = root)
    frame.grid(padx = 20, pady = 10)
    question_label_1 = tk.Label(master = frame, text = 'What is the mood the music?', font = ('Arial', 20))
    question_label_1.grid(row = 0, column = 0, columnspan = 4)
    question_label_2 = tk.Label(master = frame, text = '(You can choose multiple moods)', font = ('Arial', 16))
    question_label_2.grid(row = 1, column = 0, columnspan = 4)
    
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
    radio_button_text = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']
    radio_button_var.append(tk.IntVar(master = musical_frame, value = -1))
    for i in xrange(5):
        radio_button = tk.Radiobutton(master = musical_frame, text = radio_button_text[i], 
                                      variable = radio_button_var[0], value = i)
        radio_button.grid(row = 0, column = i)
        radio_buttons.append(radio_button)
    
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
