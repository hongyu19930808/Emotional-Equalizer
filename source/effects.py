from chord_progression import Analyzer
from midi_operation import Note
from mode_map import Mode
from numpy import mean, median, sin, pi

class Effect:

    # octave: put all the notes within the range from key-Octave to key-(Octave+1)
    @staticmethod
    def to_shepard_tone(annotated_notes, tonality, octave = None):
        key = tonality['key']
        if octave == None:
            pitches = []
            for element in annotated_notes:
                if element['note'].is_rest() == False:
                    pitches.append(element['note'].pitch - key)
            average = mean(pitches)
            octave = int(average) / 12 - 1
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                notes.append(note.copy())
            else:
                # as pitch increases, lower octave one appears and higher octave one disappears
                ratio = {1: sin(0*pi/14)/2, 1.5: sin(1*pi/14)/2,
                         2: sin(2*pi/14)/2, 2.5: sin(3*pi/14)/2,
                         3: sin(4*pi/14)/2, 3.5: sin(5*pi/14)/2,
                         4: sin(6*pi/14)/2, 4.5: sin(7*pi/14)/2,
                         5: 1 - sin(6*pi/14)/2, 5.5: 1 - sin(5*pi/14)/2,
                         6: 1 - sin(4*pi/14)/2, 6.5: 1 - sin(3*pi/14)/2,
                         7: 1 - sin(2*pi/14)/2, 7.5: 1 - sin(1*pi/14)/2
                         }
                pitch = 12 * (octave + 1) + (note.pitch - key) % 12 + key
                notes.append(Note(pitch = pitch - 12, start = note.start, duration = note.duration, 
                                  dynamic = int(note.dynamic * ratio[notation]), channel = note.channel))                        
                notes.append(Note(pitch = pitch, start = note.start, duration = note.duration,
                                  dynamic = note.dynamic, channel = note.channel))
                notes.append(Note(pitch = pitch + 12, start = note.start, duration = note.duration,
                                dynamic = int(note.dynamic * (1.0 - ratio[notation])), channel = note.channel))            
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def to_staccato(annotated_notes, tonality, ratio = 0.25, loudness = 0):
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                notes.append(note.copy())
            else:
                notes.append(Note(pitch = note.pitch, start = note.start, duration = note.duration * ratio, 
                                  dynamic = note.dynamic + loudness, channel = note.channel))
                notes.append(Note(pitch = 0, start = note.start + note.duration * ratio, 
                                  duration = note.duration * (1 - ratio), dynamic = 0, channel = note.channel))
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)              
    
    # num_chromatics can be ..., -2, -1, 0, 1, 2, ...
    # loudness[0] will be added to the volume of the original tone
    # loudness[1] will be added to the volume of the newly created tone
    @staticmethod
    def add_ornament(annotated_notes, tonality, num_chromatics = -1, duration = 1.0 / 8.0, loudness = [0, -48]):
        if type(loudness) is int or type(loudness) is float:
            loudness = [0, loudness]    
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                notes.append(note.copy())
            elif note.duration < 3 * duration:
                notes.append(Note(pitch = note.pitch, start = note.start, duration = note.duration,
                                  dynamic = note.dynamic + loudness[0], channel = note.channel))            
            else:
                notes.append(Note(pitch = note.pitch + num_chromatics, start = note.start, duration = duration,
                                  dynamic = note.dynamic + loudness[1], channel = note.channel))                        
                notes.append(Note(pitch = note.pitch, start = note.start + duration, duration = note.duration - duration,
                                  dynamic = note.dynamic + loudness[0], channel = note.channel))  
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    # num_chromatics can be ..., -2, -1, 0, 1, 2, ...
    # loudness[0] will be added to the volume of the original tone
    # loudness[1] will be added to the volume of the newly created tone
    # add most add 8 notes for tremolo
    # leave some rest for each original note if possible
    @staticmethod
    def add_tremolo(annotated_notes, tonality, num_chromatics = -12, unit = 1.0 / 4.0, loudness = [0, 0]):
        if type(loudness) is int or type(loudness) is float:
            loudness = [0, loudness]
        multiplier = 2.0 if (loudness[0] - loudness[1]) >= 25 else 1.0
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                notes.append(note.copy())
            elif note.duration < 2 * unit:
                notes.append(Note(pitch = note.pitch, start = note.start, duration = note.duration, 
                                  dynamic = note.dynamic + loudness[0], channel = note.channel))         
            else:
                num_notes = min(int(note.duration / unit), 8)
                num_notes = max(2, int(num_notes * 0.75))
                current_beat = note.start
                for i in range(num_notes):
                    if i == num_notes - 1 and multiplier > 1:
                        multiplier = 1
                    if i % 2 == 0:
                        notes.append(Note(pitch = note.pitch, start = current_beat, duration = unit * multiplier, 
                                          dynamic = note.dynamic + loudness[0], channel = note.channel))                                            
                    else:
                        notes.append(Note(pitch = note.pitch + num_chromatics, start = current_beat, duration = unit, 
                                          dynamic = note.dynamic + loudness[1], channel = note.channel))                       
                    current_beat += unit
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)            
    
    # num_chromatics can be ..., -2, -1, 0, 1, 2, ...
    # loudness will be added to the volume of the original track
    @staticmethod
    def transpose(annotated_notes, tonality, num_chromatics = 0, loudness = 0):
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                pitch_adjustment = 0
                loudness_adjustment = 0
            else:
                pitch_adjustment = num_chromatics
                loudness_adjustment = loudness
            notes.append(Note(pitch = note.pitch + pitch_adjustment, start = note.start, duration = note.duration, 
                              dynamic = note.dynamic + loudness_adjustment, channel = note.channel))
        adjusted_tonality = {'key': (tonality['key'] + num_chromatics) % 12, 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, adjusted_tonality), adjusted_tonality)
    
    # degrees can be 1, 1.5, 2, 2.5, ... , 7.5, 8
    # loudness[0] will be added to the volume of the original track
    # loudness[1] will be added to the volume of the newly created track
    @staticmethod
    def add_parallel_n_degrees(annotated_notes, tonality, degrees = 8, loudness = [0, -24]):
        if type(loudness) is int or type(loudness) is float:
            loudness = [0, loudness]
        notes = []
        degrees = degrees - 1
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            
            if note.is_rest() == True:
                notes.append(note.copy())
            else:
                key = tonality['key']
                mode_map = Mode.get_mode_map(tonality['mode'])
                pitch_shift = 0
                adjusted_notation = notation - degrees
                if adjusted_notation < 1:
                    adjusted_notation = adjusted_notation + 7
                    pitch_shift = -12
                adjusted_pitch = (int(note.pitch - key) / 12) * 12 + key + mode_map[adjusted_notation] + pitch_shift
                
                notes.append(Note(pitch = note.pitch, start = note.start, duration = note.duration,
                                  dynamic = note.dynamic + loudness[0], channel = note.channel))            
                notes.append(Note(pitch = adjusted_pitch, start = note.start, duration = note.duration,
                                  dynamic = note.dynamic + loudness[1], channel = note.channel))
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    # for each note, generate at most three notes with different octaves
    @staticmethod
    def add_multi_parallel_8_degrees(annotated_notes, tonality, loudness):
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            if note.is_rest() == True:
                notes.append(note.copy()) 
            else:
                for i in range(5):
                    if loudness[i] >= median(loudness) and loudness[i] > 0:
                        channel = note.channel
                        channel = max(0, min(15, channel))
                        notes.append(Note(pitch = note.pitch - 24 + 12 * i, start = note.start, duration = note.duration,
                                          dynamic = note.dynamic * loudness[i], channel = channel))
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def to_major(annotated_notes, tonality):
        return Effect.adjust_mode(annotated_notes, tonality, Mode.get_mode_map('Major'))        
    
    @staticmethod
    def to_natural_minor(annotated_notes, tonality):
        return Effect.adjust_mode(annotated_notes, tonality, Mode.get_mode_map('Natural Minor'))
    
    @staticmethod
    def to_harmonic_minor(annotated_notes, tonality):
        return Effect.adjust_mode(annotated_notes, tonality, Mode.get_mode_map('Harmonic Minor'))
    
    @staticmethod
    def adjust_mode(annotated_notes, tonality, mode_map):
        notes = []
        for element in annotated_notes:
            notation = element['notation']
            note = element['note']
            key = tonality['key']
            if note.is_rest() == True:
                adjusted_pitch = 0
            else:
                adjusted_pitch = (int(note.pitch - key) / 12) * 12 + key + mode_map[notation]
            notes.append(Note(pitch = adjusted_pitch, start = note.start, duration = note.duration, 
                              dynamic = note.dynamic, channel = note.channel))
        adjusted_tonality = {'key': tonality['key'], 'mode': mode_map['name']}
        return (Analyzer.annotate_notes(notes, adjusted_tonality), adjusted_tonality)    
