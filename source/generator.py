from midi_operation import MIDI
from chord_progression import Analyzer, Composer
from effects import Effect
from bass import Bass
from mood import Mood
from instrument import Instrument
from numpy import sqrt, mean, sign
from random import random

class Song:
    def __init__(self, track_melody, unit, offset = 0, resolution = None):
        if resolution == None:
            melody_notes = MIDI.list_notes(track_melody)
        else:
            melody_notes = MIDI.list_notes(track_melody, resolution)
        self.tempo_multiplier = 1.0
        self.adjust_melody_notes(melody_notes, offset)
        self.harmony_length = unit
        important_notes = Analyzer.find_important_notes(melody_notes, unit)
        if offset != 0:
            important_notes.pop(0)
        self.num_chord = int(important_notes[-1].start / unit) + 1
        (self.tonalities, change_points) = Analyzer.find_tonality(melody_notes, important_notes, unit)
        self.annotated_melody = Analyzer.annotate_all_notes(melody_notes, self.tonalities, unit)
        self.annotated_important_notes = Analyzer.annotate_all_notes(important_notes, self.tonalities, unit)
        self.progression_notations = Composer.gen_chord_progression(self.annotated_important_notes, change_points, unit)
        Instrument.init()
    
    # some adjustment of the melody
    # in case the original pitch, tempo, dynamic is not suitable for normal mood
    @staticmethod
    def adjust_melody_notes(melody_notes, offset):
        dynamics = []
        pitches = []
        durations = []
        for note in melody_notes:
            note.start += offset
            note.dynamic = min(max(note.dynamic, 72), 108)
            if note.is_rest() == False:
                dynamics.append(note.dynamic)
                pitches.append(note.pitch)
                durations.append(note.duration)
        
        mean_dynamic = mean(dynamics)
        mean_pitch = int(round(mean(pitches)))
        pitch_shift = 0
        while mean_pitch > 75:
            pitch_shift -= 7
            mean_pitch -= 7
        while mean_pitch < 63:
            pitch_shift += 7
            mean_pitch += 7
        for note in melody_notes:
            if note.is_rest() == False:
                note.dynamic = max(0, min(120, note.dynamic + 90 - mean_dynamic))
                note.pitch = note.pitch + pitch_shift
    
    def compose(self, mood, index):
        if index < self.num_chord:
            self.tonality = self.tonalities[index]
        else:
            self.tonality = self.tonalities[-1]
        melody_param = self.generate_melody_parameter(mood)
        harmony_param = self.generate_harmony_parameter(mood)
        if index >= self.num_chord:
            pattern = MIDI.new_pattern()
            pattern.append(Generator.generate_track([], melody_param['tempo'] * self.tempo_multiplier))
            pattern.append(Generator.generate_track([], harmony_param['tempo'] * self.tempo_multiplier))
            pattern.append(Generator.generate_track([], harmony_param['tempo'] * self.tempo_multiplier))
        else:
            (melody_annotated_notes, adjustable) = self.generate_melody(melody_param, index)
            Generator.adjust_mode_for_harmony(adjustable, self.tonality, melody_param, harmony_param)
            self.adjusted_progressions = Composer.adjust_progression(self.progression_notations, self.annotated_important_notes, harmony_param)
            harmony_annotated_notes = self.generate_harmony(harmony_param, index)
            melody_track = Generator.generate_track(melody_annotated_notes, melody_param['tempo'] * self.tempo_multiplier)
            harmony_track = Generator.generate_track(harmony_annotated_notes, melody_param['tempo'] * self.tempo_multiplier)
            
            melody_track_split = MIDI.separate_track(melody_track, num_track = 1)
            harmony_track_split = MIDI.separate_track(harmony_track, num_track = 2)
            pattern = MIDI.new_pattern()
            for track in melody_track_split:
                pattern.append(track)
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
    
    def generate_melody(self, param, index):
        tonality = self.tonality
        annotated_notes = self.select_notes(self.annotated_melody, index)
        important_notes = self.select_notes(self.annotated_important_notes, index)
        # calculate whether we can use the borrowed chord in harmony
        adjustable = (len(important_notes) > 0 and important_notes[0]['notation'] in [1,2,4,5])
        (annotated_notes, tonality) = Generator.add_effects(annotated_notes, tonality, param)
        return (annotated_notes, adjustable)
    
    def generate_harmony(self, param, index):       
        (annotated_notes, tonality) = Generator.add_bass(
            self.annotated_important_notes, self.tonality,
            self.adjusted_progressions, self.harmony_length, param)
        annotated_notes = self.select_notes(annotated_notes, index)
        (annotated_notes, tonality) = Generator.add_effects(annotated_notes, tonality, param)
        return annotated_notes
    
    # select the notes from a particular bar
    def select_notes(self, annotated_notes, index):
        start = index * self.harmony_length
        end = (index + 1) * self.harmony_length
        annotated_notes_cut = []
        for element in annotated_notes:
            if element['note'].start >= start and element['note'].start < end:
                note = element['note'].copy()
                note.start = note.start - start
                annotated_notes_cut.append({
                    'notation': element['notation'],
                    'note': note
                })
        return annotated_notes_cut
    
class Generator:

    # when 'change' button clicked, the seed will increases
    seed = 0
    # sometimes the seed will increase more than one since the pitch range of an instrument
    seed_change_tmp = 0
    
    @staticmethod
    def gen_pitch_parameter(mood, track_type):
        pitch = [0, 0, 1, 0, 0]
        abs_offset = {key: max(0, mood[key] / 25.0 - 2) for key in mood.keys()}
        if track_type == 'melody':
            rules = {
                0: {'+': [Mood.Angry], '-': [Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Mysterious]},
                1: {'+': [Mood.Angry, Mood.Sad], '-': [Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Mysterious]},
                2: {'+': [Mood.Calm], '-': [Mood.Scary, Mood.Mysterious]},
                3: {'+': [Mood.Comic, Mood.Happy, Mood.Mysterious, Mood.Calm], '-': []},
                4: {'+': [Mood.Scary, Mood.Mysterious], '-': []}
            }
        else:
            rules = {
                0: {'+': [Mood.Angry, Mood.Scary], '-': [Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Mysterious, Mood.Calm]},
                1: {'+': [Mood.Angry], '-': [Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Mysterious]},
                2: {'+': [Mood.Calm], '-': [Mood.Scary, Mood.Mysterious]},
                3: {'+': [Mood.Comic, Mood.Happy, Mood.Mysterious, Mood.Calm], '-': []},
                4: {'+': [], '-': []},
            }
            
        for i in range(5):
            final_pos_offset = 0
            final_neg_offset = 0
            for mood in rules[i]['+']:
                final_pos_offset = max(final_pos_offset, abs_offset[mood])
            for mood in rules[i]['-']:
                final_neg_offset = max(final_neg_offset, abs_offset[mood])
            pitch[i] += final_pos_offset
            pitch[i] -= final_neg_offset
        
        # normalize
        sum_of_square = 0
        for i in range(len(pitch)):
            pitch[i] = max(0, pitch[i])
            sum_of_square += pitch[i] * pitch[i]
        if sum_of_square == 0:
            return [0, 0, 1, 0, 0]
        for i in range(len(pitch)):
            pitch[i] /= sqrt(sum_of_square)
        return pitch
    
    @staticmethod
    def gen_tempo_parameter(mood):
        tempo_offset = ( \
            max(mood[Mood.Angry], mood[Mood.Comic], mood[Mood.Happy]) - \
            max(mood[Mood.Sad], mood[Mood.Mysterious], mood[Mood.Calm], mood[Mood.Romantic])
            ) / 2.0
        tempo = 100 + tempo_offset
        return min(150, max(50, tempo))
    
    @staticmethod
    def gen_dynamic_parameter(mood):
        dynamic_offset = ( \
            max(mood[Mood.Angry], mood[Mood.Scary], mood[Mood.Comic]) - \
            max(mood[Mood.Sad], mood[Mood.Mysterious], mood[Mood.Calm], mood[Mood.Romantic]) \
            ) / 4.0
        return max(-25, min(25, dynamic_offset))
    
    @staticmethod
    def gen_mode_parameter(tonality, mood):
        if tonality['mode'] == 'Major':
            mode = 0.5
        else:
            mode = -0.5
        mode += ( \
            max(mood[Mood.Comic], mood[Mood.Happy], mood[Mood.Calm]) - \
            max(mood[Mood.Angry], mood[Mood.Scary], mood[Mood.Sad], mood[Mood.Mysterious]) \
        ) / 50.0
        
        if max(mood[Mood.Angry], mood[Mood.Scary]) > max(mood[Mood.Sad], mood[Mood.Mysterious]):
            remarks = 'harmonic'
        else:
            remarks = 'natural'
        return [mode, remarks]

    @staticmethod
    def adjust_mode_for_harmony(adjustable, tonality, melody_param, harmony_param):
        if adjustable == False:
            return
        if melody_param['mode'][0] == 0 and tonality['mode'] == 'Major':
            harmony_param['mode'][0] = -1.0
            return
        if melody_param['mode'][0] == 0 and tonality['mode'] != 'Major':
            harmony_param['mode'][0] = 1.0
            return
        if abs(melody_param['mode'][0]) <= random() / 4.0:
            harmony_param['mode'][0] = (-1.0) * sign(melody_param['mode'][0])
            return
        return

    @staticmethod
    def gen_bass_parameter(mood):
        param = {}
        value_max = 0
        value_min = 100
        for key in mood:
            value_max = max(value_max, mood[key])
            value_min = min(value_min, mood[key])
        
        bass_map = {
            'Normal': [
                ('arpeggio_bass', True),
                ('wide_range_bass', True),
                ('single_chord_bass', True),             
                ('single_note_bass', True),
                ('alberti_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('staccato_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001))
                ],
            Mood.Angry: [
                ('single_note_bass', True),
                ('alberti_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('staccato_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001))                
                ],
            Mood.Scary: [
                ('single_note_bass', True),
                ('alberti_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('staccato_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001))                    
                ],
            Mood.Comic: [
                ('alberti_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('staccato_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('single_note_bass', True)
                ],
            Mood.Happy: [
                ('staccato_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('alberti_bass', min(1, (150 - value_max) * (150 - value_max) * 0.0001)),
                ('single_note_bass', True)
                ],
            Mood.Sad: [
                ('single_chord_bass', True),
                ('arpeggio_bass', True),
                ('wide_range_bass', True)
                ],
            Mood.Mysterious: [
                ('arpeggio_bass', True),
                ('single_chord_bass', True),
                ('wide_range_bass', True)
                ],
            Mood.Romantic: [
                ('arpeggio_bass', True),
                ('wide_range_bass', True),
                ('single_chord_bass', True),
                ],
            Mood.Calm: [
                ('wide_range_bass', True),
                ('arpeggio_bass', True),
                ('single_chord_bass', True)             
            ]
        }
        
        for mood_str in Mood.mood_strs:
            if mood[mood_str] == value_max:
                dominated_mood = mood_str
                break
        if value_max - value_min <= 10:
            dominated_mood = 'Normal'
        num_available = len(bass_map[dominated_mood])
        bass_type = bass_map[dominated_mood][Generator.seed % num_available][0]
        bass_param = bass_map[dominated_mood][Generator.seed % num_available][1]
        param[bass_type] = bass_param
        return param

    @staticmethod
    def gen_effect_parameter(mood, track_type):
        param = {}
        if (mood[Mood.Angry] > 50 or mood[Mood.Scary] > 50) and track_type == 'harmony':
            value = max(mood[Mood.Angry], mood[Mood.Scary])
            unit_param = [1.0, 2.0, 4.0, 6.0, 8.0]
            unit = 1.0 / unit_param[(value - 50 - 1) / 10]
            loudness = (value - 100) * (value - 100) / -50.0
            param['tremolo'] = (-1, unit, loudness)
        if (mood[Mood.Angry] > 50 or mood[Mood.Scary] > 50) and track_type == 'melody':
            value = max(mood[Mood.Angry], mood[Mood.Scary])
            loudness = (value - 100) * (value - 100) / -25.0
            param['parallel'] = (4.5, loudness)
        if mood[Mood.Comic] > 50 and track_type == 'melody':
            param['staccato'] = min(1, (150 - mood[Mood.Comic]) * (150 - mood[Mood.Comic]) * 0.0001)
            param['ornament'] = (mood[Mood.Comic] > 75)
        return param
    
    @staticmethod
    def add_bass(annotated_important_notes, tonality, progression_notations, harmony_length, param):
        if param.has_key('staccato_bass'):
            (annotated_notes, tonality) = Bass.gen_staccato_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length, ratio = param['staccato_bass'])        
        elif param.has_key('alberti_bass'):
            (annotated_notes, tonality) = Bass.gen_alberti_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length, ratio = param['alberti_bass'])
        elif param.has_key('arpeggio_bass'):
            (annotated_notes, tonality) = Bass.gen_arpeggio_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length)         
        elif param.has_key('single_chord_bass'):
            (annotated_notes, tonality) = Bass.gen_single_chord_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length)              
        elif param.has_key('single_note_bass'):
            (annotated_notes, tonality) = Bass.gen_single_note_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length)      
        else:
            (annotated_notes, tonality) = Bass.gen_wide_range_bass(
                annotated_important_notes, tonality, 
                progression_notations, harmony_length)
        return (annotated_notes, tonality)
    
    @staticmethod
    def add_effects(annotated_notes, tonality, param):
        if param.has_key('mode'):
            if param['mode'][0] > 0:
                (annotated_notes, tonality) = Effect.to_major(annotated_notes, tonality)
            if param['mode'][0] < 0 and param['mode'][1] == 'harmonic':
                (annotated_notes, tonality) = Effect.to_harmonic_minor(annotated_notes, tonality)
            if param['mode'][0] < 0 and param['mode'][1] == 'natural':
                (annotated_notes, tonality) = Effect.to_natural_minor(annotated_notes, tonality)    
        if param.has_key('dynamic'):
            (annotated_notes, tonality) = Effect.transpose(
                annotated_notes, tonality, loudness = param['dynamic'])
        if param.has_key('parallel'):
            (annotated_notes, tonality) = Effect.add_parallel_n_degrees(
                annotated_notes, tonality, degrees = param['parallel'][0], loudness = param['parallel'][1])
        if param.has_key('tremolo'):
            (annotated_notes, tonality) = Effect.add_tremolo(
                annotated_notes, tonality, num_chromatics = param['tremolo'][0], unit = param['tremolo'][1], loudness = param['tremolo'][2])
        if param.has_key('staccato'):
            (annotated_notes, tonality) = Effect.to_staccato(
                annotated_notes, tonality, ratio = param['staccato'])
        if param.has_key('ornament') and param['ornament'] == True:
            (annotated_notes, tonality) = Effect.add_ornament(
                annotated_notes, tonality)
        if param.has_key('shepard'):
            (annotated_notes, tonality) = Effect.to_shepard_tone(
                annotated_notes, tonality, octave = 4)
        if param.has_key('pitch'):
            (annotated_notes, tonality) = Effect.add_multi_parallel_8_degrees(
                annotated_notes, tonality, param['pitch'])
        return (annotated_notes, tonality)
    
    @staticmethod    
    def generate_track(annotated_notes, tempo = 100):
        notes = [note['note'] for note in annotated_notes]
        notes.sort()    
        track = MIDI.new_track(tempo)
        track.make_ticks_abs()
        for note in notes:
            MIDI.add_note_abs(track, note.pitch, note.start, 
                              note.start + note.duration, 
                              note.dynamic, note.channel)
        track.sort()
        track.make_ticks_rel()
        return track
    