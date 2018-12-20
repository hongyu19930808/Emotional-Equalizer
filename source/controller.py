from synthesizer import Synthesizer
from player import Player
from midi_operation import MIDI
from generator import Song, Generator
from mood import Mood
from threading import Lock
from thread import start_new_thread
from time import sleep, time
from impromptu import Impromptu
from random import randint

class Controller:
    def __init__(self, gui):
        self.gui = gui
        self.song = None
        self.inpromptu = None
        
        # used by several threads
        self.composition_mutex = Lock()
        self.current_mood = Mood.get_default_mood()
        self.current_playing_index = -1
        self.next_samples = 'not ready'
        self.need_compose = True
        
        self.status_mutex = Lock()
        self.status = 'play'
        
        self.compose_thread_mutex = Lock()
        self.play_thread_mutex = Lock()
        self.synth = Synthesizer()
        self.tempo_multiplier = 1.0
        start_new_thread(self.key_detection, ())
    
    def key_detection(self):
        key_state = {}
        while True:
            for key in self.gui.key_state.keys():
                value = self.gui.key_state[key]
                if value == 1 and (key_state.has_key(key) == False or key_state[key] == 0):
                    # note on event
                    key_state[key] = 1
                    notation = self.key_to_notation(key)
                    events = self.notation_to_events(notation, 'on')
                    if self.inpromptu != None:
                        self.composition_mutex.acquire()
                        self.inpromptu.melody_notation = notation
                        self.next_samples = 'not ready'
                        self.need_compose = True
                        self.composition_mutex.release()
                if value == 0 and (key_state.has_key(key) == True and key_state[key] == 1):
                    # note off event
                    key_state[key] = 0
                    notation = self.key_to_notation(key)
                    events = self.notation_to_events(notation, 'off')
            sleep(0.01)
            
    def key_to_notation(self, key):
        if key == 'space':
            return 1
        elif key == 'u':
            return 2
        elif key == 'i':
            return 3
        elif key == 'o':
            return 4
        elif key == 'p':
            return 5
        elif key == 'bracketleft':
            return 6
        elif key == 'bracketright':
            return 7
        else:
            return 0
    
    def notation_to_events(self, notation, note_type):
        return None
        
    # in case some notes cross the bar    
    def revise_pattern(self, pattern, index):
        unit = self.song.harmony_length
        resolution = pattern.resolution
        self.removed_event[index] = []
        for track_index in range(len(pattern)):
            track = pattern[track_index]
            track.make_ticks_abs()
            # remove the event which should not located in bar[index]
            event_list = []
            for event in track:
                if event.tick >= unit * resolution:
                    event_list.append(event)
                    self.removed_event[index].append((event, track_index))
            for event in event_list:
                track.remove(event)
            # add the event which should located in the bar[index]
            for key in self.removed_event.keys():
                for (event, event_track_index) in self.removed_event[key]:
                    if event_track_index == track_index and \
                       event.tick >= (index - key) * unit * resolution and \
                       event.tick < (index + 1 - key) * unit * resolution:
                        new_event = MIDI.copy_event(event)
                        new_event.tick = event.tick - (index - key) * unit * resolution
                        track.append(new_event)
            track.sort()
            track.make_ticks_rel()
        return pattern
    
    def compose(self):
        self.compose_thread_mutex.acquire()
        self.synth.reset()
        num_chord = self.song.num_chord
        unit = self.song.harmony_length
        self.patterns = {}
        self.tonalities = {}
        self.instruments = {}
        self.removed_event = {}
        while True:
            if self.get_status() == 'stop':
                break
            self.composition_mutex.acquire()
            local_need_compose = self.need_compose
            next_index = self.current_playing_index + 1
            # get mood from schedule
            mood_from_schedule = self.gui.get_mood_from_schedule(next_index, num_chord)
            for mood in Mood.mood_strs:
                if mood_from_schedule[mood] != None:
                    self.current_mood[mood] = mood_from_schedule[mood]
            local_mood = self.current_mood
            self.composition_mutex.release()
            
            # set mood scales
            self.gui.set_mood_scales(mood_from_schedule)
            
            if next_index >= num_chord + 2:
                self.composition_mutex.acquire()
                self.next_samples = None
                self.composition_mutex.release()
                break
            
            if local_need_compose == True:
                (pattern, tonality, instruments) = self.song.compose(local_mood, next_index)
                pattern = self.revise_pattern(pattern, next_index)
                self.patterns[next_index] = pattern
                self.tonalities[next_index] = tonality
                self.instruments[next_index] = instruments
                samples = self.synth.convert_pattern_to_samples(pattern, instruments, unit)          
                
                self.composition_mutex.acquire()
                self.next_samples = samples
                self.need_compose = False
                self.composition_mutex.release()
            else:
                sleep(0.01)
        
        MIDI.write_patterns('demo.mid', self.patterns, unit, self.tonalities, self.instruments)
        self.compose_thread_mutex.release()
    
    def play_samples(self):
        self.play_thread_mutex.acquire()
        player = Player(self)
        
        while True:
            if self.get_status() == 'stop':
                break
            elif self.get_status() == 'pause':
                sleep(0.01)
                continue    
            else:
                self.composition_mutex.acquire()
                local_playing_index = None
                need_wait = False
                # finish playing
                if self.next_samples == None:
                    local_playing_index = self.current_playing_index
                    self.composition_mutex.release()
                    self.gui.update_progress_scale(local_playing_index + 1)
                    break
                # the samples are not ready
                elif self.next_samples == 'not ready':
                    self.need_compose = True
                    need_wait = True
                # ready to play
                else:
                    samples = self.next_samples
                    self.current_playing_index += 1
                    local_playing_index = self.current_playing_index
                    self.next_samples = 'not ready'
                    self.need_compose = True
                self.composition_mutex.release()
                if local_playing_index != None:
                    self.gui.update_progress_scale(local_playing_index)
            if need_wait == True:
                sleep(0.01)
            else:
                player.play(samples)
        
        self.play_thread_mutex.release()
        
    def impromptu_compose(self, unit, offset):
        self.compose_thread_mutex.acquire()
        self.synth.reset()
        self.patterns = {}
        self.tonalities = {}
        self.instruments = {}
        self.inpromptu = Impromptu(unit, offset)
        while True:
            if self.get_status() == 'stop':
                break
            self.composition_mutex.acquire()
            local_need_compose = self.need_compose
            next_index = self.current_playing_index + 1
            local_mood = self.current_mood
            self.composition_mutex.release()
            
            if local_need_compose == True:
                (pattern, tonality, instruments) = self.inpromptu.compose(local_mood)
                self.patterns[next_index] = pattern
                self.tonalities[next_index] = tonality
                self.instruments[next_index] = instruments
                samples = self.synth.convert_pattern_to_samples(pattern, instruments, unit)          
                
                self.composition_mutex.acquire()
                self.next_samples = samples
                self.need_compose = False
                self.composition_mutex.release()
            else:
                sleep(0.01)
        
        MIDI.write_patterns('demo.mid', self.patterns, unit, self.tonalities, self.instruments)
        self.compose_thread_mutex.release()
    
    def impromptu_play(self):
        self.play_thread_mutex.acquire()
        player = Player(self)
        
        while True:
            if self.get_status() == 'stop':
                break
            elif self.get_status() == 'pause':
                sleep(0.01)
                continue    
            else:
                self.composition_mutex.acquire()
                local_playing_index = None
                need_wait = False
                # finish playing
                if self.next_samples == None:
                    local_playing_index = self.current_playing_index
                    self.composition_mutex.release()
                    break
                # the samples are not ready
                elif self.next_samples == 'not ready':
                    self.need_compose = True
                    need_wait = True
                # ready to play
                else:
                    samples = self.next_samples
                    self.current_playing_index += 1
                    local_playing_index = self.current_playing_index
                    self.next_samples = 'not ready'
                    self.need_compose = True
                self.composition_mutex.release()
            if need_wait == True:
                sleep(0.01)
            else:
                player.play(samples)
                sleep(0.1)
        
        self.play_thread_mutex.release()
            
    def mood_change(self, mood, increase_seed = 0):
        self.composition_mutex.acquire()
        if increase_seed > 0:
            Generator.seed += increase_seed
            Generator.seed += Generator.seed_change_tmp
            Generator.seed_change_tmp = 0
            if Generator.seed >= 65536:
                Generator.seed -= 65536
        self.current_mood = mood
        self.next_samples = 'not ready'
        self.need_compose = True
        self.composition_mutex.release()
        
    def tempo_change(self, value):
        if self.song != None:
            self.song.tempo_multiplier = value
        if self.inpromptu != None:
            self.inpromptu.tempo_multiplier = value
        self.tempo_multiplier = value
    
    def open(self, path, unit, offset):
        self.stop()
        (melody, resolution) = MIDI.read_melody(path)
        if len(melody) == 0:
            return False
        self.song = Song(track_melody = melody, unit = unit, offset = offset, resolution = resolution)
        self.song.tempo_multiplier = self.tempo_multiplier
        self.gui.init_progress_scale(self.song.num_chord)
        self.gui.song_length = self.song.num_chord
        return True
        
    def play(self):
        self.set_status('play')
        compose_thread_locked = self.compose_thread_mutex.locked()
        play_thread_locked = self.play_thread_mutex.locked()          
        if self.song != None:
            if compose_thread_locked == False:               
                start_new_thread(self.compose, ())
            if play_thread_locked == False:
                start_new_thread(self.play_samples, ())
        else:
            if compose_thread_locked == False:
                (unit, offset) = self.gui.get_unit_offset()
                start_new_thread(self.impromptu_compose, (unit, offset))
            if play_thread_locked == False:
                start_new_thread(self.impromptu_play, ())
    
    def stop(self):        
        self.composition_mutex.acquire()
        self.current_playing_index = -1
        self.need_compose = True
        self.next_samples = 'not ready'
        self.set_status('stop')
        self.removed_event = {}
        self.composition_mutex.release()
        if self.song != None:
            self.gui.update_progress_scale(0)
    
    def pause(self):
        self.set_status('pause')
        
    def set_pos(self, value):
        self.set_status('pause')
        self.composition_mutex.acquire()
        self.current_playing_index = value - 1
        self.next_samples = 'not ready'
        self.need_compose = True
        self.composition_mutex.release()
        self.gui.play_pause_button['text'] = 'Pause'
        self.set_status('play')
        
        compose_thread_locked = self.compose_thread_mutex.locked()
        play_thread_locked = self.play_thread_mutex.locked()
        if compose_thread_locked == False:
            start_new_thread(self.compose, ())
        if play_thread_locked == False:
            start_new_thread(self.play_samples, ())
        
    def get_status(self):
        self.status_mutex.acquire()
        status = self.status
        self.status_mutex.release()
        return status
    
    def set_status(self, status):
        self.status_mutex.acquire()
        self.status = status
        self.status_mutex.release()