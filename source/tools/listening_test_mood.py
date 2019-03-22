import tkinter as tk
import wave
import numpy
import struct
from pyaudio import PyAudio, paInt16
from thread import start_new_thread
from fluidsynth import raw_audio_string
from random import shuffle
from time import sleep

class Gender:
    Male = 'male'
    Female = 'female'

# settings
email = 'yhongag'
gender = Gender.Male
age = 25

start_session = 2
num_session = 2

# global variables
num_excerpt_per_session = 4
all_excerpts = range(start_session * num_excerpt_per_session, (start_session + num_session) * num_excerpt_per_session)
records = {excerpt: {} for excerpt in all_excerpts}
shuffle(all_excerpts)
finished = False
repeat_flag = False

current_excerpt_index = 0
current_mood_index = 0
mood_strs = ['Angry', 'Scary', 'Comic', 'Happy', 'Sad', 'Mysterious', 'Romantic', 'Calm']
shuffle(mood_strs)

root = tk.Tk()
frame = tk.Frame(master = root)
labels = tk.Frame(master = frame)
question_label_1 = tk.Label(master = labels, font = ('Arial', 20), text = 'Is the mood of the sound')
question_label_2 = tk.Label(master = labels, font = ('Arial', 20), foreground = 'red', text = mood_strs[0])
question_label_3 = tk.Label(master = labels, font = ('Arial', 20), text = '?')

audio = PyAudio()
stream = audio.open(format = paInt16, channels = 1, rate = 44100, output = True)

def play_excerpt():
    global repeat_flag
    current_playing_index = -1
    start = 0
    frame_length = 1024
    samples = []
    while True:
        if current_playing_index == -1:
            current_playing_index = current_excerpt_index
            samples = read_samples()
            if samples is None:
                break
            start = 0
            end = min(start + frame_length, len(samples))
            frame = samples[start:end]
            stream.write(raw_audio_string(frame * pow(2, 15)))
            start += frame_length
            repeat_flag = False
        elif current_playing_index != current_excerpt_index:
            end = min(start + frame_length, len(samples))
            frame = samples[start:end]
            for i in xrange(len(frame)):
                frame[i] *= (1.0 - float(i) / len(frame))
            stream.write(raw_audio_string(frame * pow(2, 15)))
            start = 0
            samples = read_samples()
            if samples is None:
                break            
            current_playing_index = current_excerpt_index
            repeat_flag = False
        else:
            end = min(start + frame_length, len(samples))
            frame = samples[start:end]
            # check whether it is the last frame of the excerpt
            if start + frame_length >= len(samples):
                for i in xrange(len(frame)):
                    frame[i] *= (1.0 - float(i) / len(frame))
                stream.write(raw_audio_string(frame * pow(2, 15)))
                if repeat_flag == True:
                    start = 0
                    repeat_flag = False
                else:
                    start += frame_length
                    sleep(1)
            else:
                stream.write(raw_audio_string(frame * pow(2, 15)))
                start += frame_length

def read_samples():
    if current_excerpt_index >= len(all_excerpts):
        return None
    instrument_index = str(all_excerpts[current_excerpt_index]).zfill(3)
    path = './sounds/instrument_' + instrument_index + '.wav'
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
    samples = samples / pow(2.0, 15)
    return samples

def close_audio():
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
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

def update_index():
    global current_mood_index, current_excerpt_index
    if finished == True:
        return
    current_mood_index += 1
    if current_mood_index >= len(mood_strs):
        current_mood_index = 0
        current_excerpt_index += 1
        shuffle(mood_strs)
    if current_excerpt_index < num_session * num_excerpt_per_session:
        question_label_2['text'] = mood_strs[current_mood_index]
    else:
        question_label_1['text'] = 'You have finished the test.'
        question_label_2['text'] = 'Thank you!'
        question_label_3['text'] = ''

def button_no_clicked():
    if finished == False:
        records[all_excerpts[current_excerpt_index]][mood_strs[current_mood_index]] = 0
        update_index()
    
def button_maybe_clicked():
    if finished == False:
        records[all_excerpts[current_excerpt_index]][mood_strs[current_mood_index]] = 1
        update_index()
    
def button_yes_clicked():
    if finished == False:
        records[all_excerpts[current_excerpt_index]][mood_strs[current_mood_index]] = 2
        update_index()
    
def button_repeat_clicked():
    global repeat_flag
    repeat_flag = True

def key_press_event(event):
    if event.char == '1':
        button_no_clicked()
    if event.char == '2':
        button_maybe_clicked()
    if event.char == '3':
        button_yes_clicked()
    if event.char == '0':
        button_repeat_clicked()

def main():
    
    root.title('Listening Test')
    root.bind(sequence = '<KeyPress>', func = key_press_event)
    frame.grid(padx = 8, pady = 16)
    labels.grid(row = 0, column = 0, columnspan = 3)
    question_label_1.grid(row = 0, column = 0)
    question_label_2.grid(row = 0, column = 1)
    question_label_3.grid(row = 0, column = 2)
    
    tk.Label(master = frame, text = ' ', font = ('Arial', 4)).grid(row = 1, column = 0, columnspan = 3)
    
    button_no = tk.Button(master = frame, text = 'Not at all (Press 1)', font = ('Arial', 16), 
                          command = button_no_clicked)
    button_no.grid(row = 2, column = 0)
    button_no = tk.Button(master = frame, text = 'Somewhat (Press 2)', font = ('Arial', 16), 
                          command = button_maybe_clicked)
    button_no.grid(row = 2, column = 1)
    button_no = tk.Button(master = frame, text = 'Definitely (Press 3)', font = ('Arial', 16), 
                          command = button_yes_clicked)
    button_no.grid(row = 2, column = 2)
    
    tk.Label(master = frame, text = ' ', font = ('Arial', 4)).grid(row = 3, column = 0, columnspan = 3)
    button_repeat = tk.Button(master = frame, text = 'Repeat (Press 0)', font = ('Arial', 16), 
                          command = button_repeat_clicked)
    button_repeat.grid(row = 4, column = 0, columnspan = 3)
    
    start_new_thread(play_excerpt, ())    
    
    # setting
    center_window(root)
    root.resizable(False, False)
    root.focus()
    root.mainloop()
    
    # output
    file_name = email + '-' + gender + '-' + str(age)
    for i in xrange(num_session):
        file_name += '-s'
        file_name += str(start_session + i)
    fout = open(file_name + '.csv', 'w')
    all_excerpts.sort()
    mood_strs = ['Angry', 'Scary', 'Comic', 'Happy', 'Sad', 'Mysterious', 'Romantic', 'Calm']
    for mood in mood_strs:
        fout.write(',')
        fout.write(mood)
    fout.write('\n')
    for excerpt in all_excerpts:
        fout.write('Ins ' + str(excerpt))
        for mood in mood_strs:
            fout.write(',')
            if records[excerpt].has_key(mood):
                fout.write(str(records[excerpt][mood]))
            else:
                fout.write('-1')
        fout.write('\n')
    fout.close()
    

if __name__ == '__main__':
    main()


