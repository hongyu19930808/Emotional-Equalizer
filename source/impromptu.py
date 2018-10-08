from midi_operation import MIDI, Note
from chord_progression import Composer
from instrument import Instrument
from generator import Generator
from random import random

class Impromptu:
    
    def __init__(self, unit, offset = 0):
        self.tempo_multiplier = 1.0
        self.harmony_length = unit
        self.offset = offset
        Instrument.init()
    
    def compose(self, mood, index):
        self.tonality = {'key': 0, 'mode': 'Major'}
        melody_param = self.generate_melody_parameter(mood)
        melody_track = Generator.generate_track([], melody_param['tempo'] * self.tempo_multiplier)
        
        harmony_param = self.generate_harmony_parameter(mood)
        # Generator.adjust_mode_for_harmony(adjustable, self.tonality, melody_param, harmony_param)
        # self.adjusted_progressions = Composer.adjust_progression(self.progression_notations, self.annotated_important_notes, harmony_param)
        harmony_annotated_notes = self.generate_harmony(harmony_param, index)
        harmony_track = Generator.generate_track(harmony_annotated_notes, harmony_param['tempo'] * self.tempo_multiplier)
        harmony_track_split = MIDI.separate_track(harmony_track, num_track = 2)
        pattern = MIDI.new_pattern()
        pattern.append(melody_track)
        for track in harmony_track_split:
            pattern.append(track)
            
        
        # set tonality
        if melody_param['mode'][0] > 0:
            tonality = {'mode': 'Major', 'key': self.tonality['key']}
        elif melody_param['mode'][0] < 0:
            tonality = {'mode': 'Minor', 'key': self.tonality['key']}
        else:
            tonality = {'mode': self.tonality['mode'], 'key': self.tonality['key']}
            
        (instruments, seed_change) = Instrument.get_instruments(mood, Generator.seed)
        Generator.seed_change_tmp = seed_change
        tonality_name_major = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        tonality_name_minor = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
        if tonality['mode'] == 'Major':
            print tonality_name_major[tonality['key']], 'Major'
        else:
            print tonality_name_minor[tonality['key']], 'Minor'
        return (pattern, tonality, instruments)
    
    def generate_melody_parameter(self, mood):
        param_basic = {
            'tempo': Generator.gen_tempo_parameter(mood),
            'pitch': Generator.gen_pitch_parameter(mood, 'melody'),
            'dynamic': Generator.gen_dynamic_parameter(mood),
            'mode': Generator.gen_mode_parameter(self.tonality, mood),
        }
        param_effect = Generator.gen_effect_parameter(mood, 'melody')
        return dict(param_basic.items() + param_effect.items())    
    
    def generate_harmony_parameter(self, mood):
        param_basic = {
            'tempo': Generator.gen_tempo_parameter(mood),
            'pitch': Generator.gen_pitch_parameter(mood, 'harmony'),
            'dynamic': Generator.gen_dynamic_parameter(mood),
            'mode': Generator.gen_mode_parameter(self.tonality, mood),
        }
        param_bass = Generator.gen_bass_parameter(mood)
        param_effect = Generator.gen_effect_parameter(mood, 'harmony')
        return dict(param_basic.items() + param_bass.items() + param_effect.items())
    
    def generate_harmony(self, param, index):
        notations = [1, 4, 5, 1]
        notation = notations[index % 4]
        self.annotated_important_notes = [
            {'notation': 1, 
             'note': Note(pitch = 60, start = 0, duration = 2, dynamic = 80, channel = 0)}] * 2
        self.adjusted_progressions = [notation, 1]
        (annotated_notes, tonality) = Generator.add_bass(
            self.annotated_important_notes, self.tonality,
            self.adjusted_progressions, self.harmony_length, param)
        (annotated_notes, tonality) = Generator.add_effects(annotated_notes, tonality, param)
        return annotated_notes
    