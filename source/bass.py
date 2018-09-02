from midi_operation import Note
from chord_progression import Analyzer
from mode_map import Mode

class Bass:
    
    @staticmethod
    def gen_single_note_bass(annotated_important_notes, tonality, progression_notations, \
                             harmony_length, dynamic = 48, octave = 3):
        unit = 1.0
        num_notes = harmony_length
        while num_notes > 4:
            num_notes /= 2
            unit *= 2
        while num_notes < 2:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)    
        
        configures = {
            'harmony_length': harmony_length,
            'dynamic': dynamic,
            'octave': octave,
            'chord_map': {
                1: [1, 1, 1, 1],
                2: [2, 2, 2, 2],
                3: [3, 3, 3, 3],
                4: [4, 4, 4, 4],
                5: [-2, -2, -2, -2],
                6: [-1, -1, -1, -1],
                7: [0, 0, 0, 0]            
                },
            'num_notes': num_notes,
            'note_start': [float(i) / harmony_length * unit for i in range(num_notes)],
            'note_duration': [1.0 / harmony_length * unit] * num_notes,
            'note_dynamic_shift': [12, 0, 0, 0],
            'note_channel': [1, 2, 2, 2]
        }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def gen_single_chord_bass(annotated_important_notes, tonality, progression_notations, \
                              harmony_length, dynamic = 48, octave = 3):
        unit = 1.0
        num_notes = harmony_length
        while num_notes > 4:
            num_notes /= 2
            unit *= 2
        while num_notes < 2:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)
        
        configures = {
            'harmony_length': harmony_length,
            'dynamic': dynamic,
            'octave': octave,
            'chord_map': {
                1: [1, 3, 5],
                2: [-1, 2, 4],
                3: [-2, 0, 3],
                4: [1, 4, 6],
                5: [0, 2, 5],
                6: [-1, 1, 3],
                7: [0, 2, 4]                  
                },           
            'num_notes': 3,
            'note_start': [0, 0.5 / num_notes, 1.0 / num_notes],
            'note_duration': [1, 1 - 0.5 / num_notes, 1 - 1.0 / num_notes],
            'note_dynamic_shift': [12, 0, 0],
            'note_channel': [1, 2, 2]
        }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def gen_alberti_bass(annotated_important_notes, tonality, progression_notations, \
                         harmony_length, dynamic = 48, octave = 3, ratio = 0.25):
        unit = 0.5
        num_notes = harmony_length * 2
        while num_notes > 8:
            num_notes /= 2
            unit *= 2
        while num_notes < 4:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)
        
        configures = {
            'harmony_length': harmony_length,
            'dynamic': dynamic,
            'octave': octave,
            'chord_map': {
                1: [1, 5, 3, 5] * 2,
                2: [-1, 4, 2, 4] * 2,
                3: [-2, 3, 0, 3] * 2,
                4: [1, 6, 4, 6] * 2,
                5: [0, 5, 2, 5] * 2,
                6: [-1, 3, 1, 3] * 2,
                7: [0, 4, 2, 4] * 2            
                },
            'num_notes': num_notes,
            'note_start': [float(i) / harmony_length * unit for i in range(num_notes)],
            'note_duration': [ratio / harmony_length * unit for i in range(num_notes)],
            'note_dynamic_shift': [12, 0, 6, 0] * 2,
            'note_channel': [1, 2, 1, 2] * 2
        }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def gen_staccato_bass(annotated_important_notes, tonality, progression_notations, \
                              harmony_length, dynamic = 48, octave = 3, ratio = 0.25):
        unit = 0.5
        num_notes = harmony_length * 2
        while num_notes > 4:
            num_notes /= 2
            unit *= 2
        while num_notes < 2:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)
        
        configures = {
            'harmony_length': harmony_length,
            'dynamic': dynamic,
            'octave': octave,
            'chord_map': {
                1: [1, 3, 5, 3, 5, 3, 5],
                2: [-1, 2, 4, 2, 4, 2, 4],
                3: [-2, 0, 3, 0, 3, 0, 3],
                4: [1, 4, 6, 4, 6, 4, 6],
                5: [0, 2, 5, 2, 5, 2, 5],
                6: [-1, 1, 3, 1, 3, 1, 3],
                7: [0, 2, 4, 2, 4, 2, 4]            
                },
            'num_notes': num_notes * 2 - 1,
            'note_start': [0] + [float((i + 2) / 2) / harmony_length * unit for i in range(num_notes * 2 - 2)], 
            'note_duration': [1.0 / harmony_length * unit] + [ratio / harmony_length * unit for i in range(num_notes * 2 - 2)],
            'note_dynamic_shift': [12, 0, 0, 0, 0, 0, 0],
            'note_channel': [1, 2, 2, 2, 2, 2, 2]
        }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def gen_arpeggio_bass(annotated_important_notes, tonality, progression_notations, \
                              harmony_length, dynamic = 48, octave = 3):
        unit = 0.5
        num_notes = harmony_length * 2
        while num_notes > 6:
            num_notes /= 2
            unit *= 2
        while num_notes < 3:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)
        
        # non-overlapping version: 'note_duration': [1.0 / harmony_length * unit] * num_notes,
        configures = {
            'harmony_length': harmony_length,
            'dynamic': dynamic,
            'octave': octave,
            'chord_map': {
                1: [1, 3, 5, 8, 5, 3],
                2: [-1, 2, 4, 6, 4, 2],
                3: [-2, 0, 3, 5, 3, 0],
                4: [1, 4, 6, 8, 6, 4],
                5: [0, 2, 5, 7, 5, 2],
                6: [-1, 1, 3, 6, 3, 1],
                7: [0, 2, 4, 7, 4, 2]            
                },
            'num_notes': num_notes,
            'note_start': [float(i) / harmony_length * unit for i in range(num_notes)],
            'note_duration': [1 - float(i) / harmony_length * unit for i in range(num_notes)],
            'note_dynamic_shift': [12, 0, 0, 0, 0, 0],
            'note_channel': [1, 2, 2, 2, 2, 2]
        }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)
    
    @staticmethod
    def gen_wide_range_bass(annotated_important_notes, tonality, progression_notations, \
                              harmony_length, dynamic = 48, octave = 3):
        unit = 0.5
        num_notes = harmony_length * 2
        while num_notes > 8:
            num_notes /= 2
            unit *= 2
        while num_notes < 4:
            num_notes *= 2
            unit /= 2
        num_notes = int(num_notes)    
        
        if num_notes >= 6:
            # non-overlapping version: 'note_duration': [1.0 / harmony_length * unit] * 4 + [1.0 - 4.0 / harmony_length * unit],
            configures = {
                'harmony_length': harmony_length,
                'dynamic': dynamic,
                'octave': octave,
                'chord_map': {
                    1: [1-7, 5-7, 1, 3, 5],
                    2: [2-7, 6-7, 2, 4, 6],
                    3: [3-7, 7-7, 3, 5, 7],
                    4: [4-7, 8-7, 4, 6, 8],
                    5: [-2-7, 2-7, -2, 0, 2],
                    6: [-1-7, 3-7, -1, 1, 3],
                    7: [0-7, 4-7, 0, 2, 4]            
                    },
                'num_notes': 5,
                'note_start': [float(i) / harmony_length * unit for i in range(5)],
                'note_duration': [1 - float(i) / harmony_length * unit for i in range(5)],
                'note_dynamic_shift': [12, 0, 0, 0, 0],
                'note_channel': [1, 2, 2, 2, 2]
            }
        else:
            # non-overlapping version: 'note_duration': [1.0 / harmony_length * unit] * 2 + [1 - 2.0 / harmony_length * unit] * 2,
            configures = {
                'harmony_length': harmony_length,
                'dynamic': dynamic,
                'octave': octave,
                'chord_map': {
                    1: [1-7, 5-7, 1, 3],
                    2: [2-7, 6-7, 2, 4],
                    3: [3-7, 7-7, 3, 5],
                    4: [4-7, 8-7, 4, 6],
                    5: [-2-7, 2-7, -2, 0],
                    6: [-1-7, 3-7, -1, 1],
                    7: [0-7, 4-7, 0, 2]            
                    },
                'num_notes': 4,
                'note_start': [0, 1.0 / harmony_length * unit, 2.0 / harmony_length * unit, 2.0 / harmony_length * unit],
                'note_duration': [1, 1 - 1.0 / harmony_length * unit, 1 - 2.0 / harmony_length * unit, 1 - 2.0 / harmony_length * unit],
                'note_dynamic_shift': [12, 0, 0, 0],
                'note_channel': [1, 2, 2, 2]
            }
    
        notes = Bass.gen_bass(annotated_important_notes, tonality, progression_notations, configures)
        tonality = {'key': tonality['key'], 'mode': tonality['mode']}
        return (Analyzer.annotate_notes(notes, tonality), tonality)

    @staticmethod
    def gen_bass(annotated_important_notes, tonality, progression_notations, configures):
        key = tonality['key']
        mode = tonality['mode']
        mode_map = Mode.get_mode_map(mode)    
        notes = []
        for i in range(len(progression_notations) - 1):
            start_time = int(annotated_important_notes[i]['note'].start / configures['harmony_length']) * configures['harmony_length']
            if progression_notations[i] == 0:
                notes.append(Note(pitch = 0, start = start_time, duration = configures['harmony_length'], dynamic = 0, channel = 1))
                notes.append(Note(pitch = 0, start = start_time, duration = configures['harmony_length'], dynamic = 0, channel = 2))
            else:
                # calculate pitch
                pitches = []
                notations = configures['chord_map'][progression_notations[i]]
                for j in range(configures['num_notes']):
                    pitches.append(Bass.cal_pitch(notations[j], mode_map, key, configures['octave']))
                # add note
                for j in range(configures['num_notes']):
                    notes.append(Note(pitch = pitches[j], 
                                      start = start_time + configures['note_start'][j] * configures['harmony_length'], 
                                      duration = configures['harmony_length'] * configures['note_duration'][j], 
                                      dynamic = configures['dynamic'] + configures['note_dynamic_shift'][j],
                                      channel = configures['note_channel'][j]
                                      ))
        
        start_time = (annotated_important_notes[-1]['note'].start / configures['harmony_length']) * configures['harmony_length']
        notes = notes + Bass.add_final_chord(configures['octave'], tonality, start_time, configures['harmony_length'], configures['dynamic']) 
        return notes

    @staticmethod
    def cal_pitch(notation, mode_map, key, octave):
        pitch_shift = 0
        while notation >= 8:
            notation -= 7
            pitch_shift += 12
        while notation < 1:
            notation += 7
            pitch_shift -= 12
        pitch = mode_map[notation] + pitch_shift + key + 12 * (octave + 1)  
        return pitch
    
    @staticmethod
    def add_final_chord(octave, tonality, start_time, harmony_length, dynamic):
        key = tonality['key']
        mode = tonality['mode']
        mode_map = Mode.get_mode_map(mode)
        pitches = [Bass.cal_pitch(notation, mode_map, key, octave) for notation in [1-7,5-7,3,8]]
        channels = [1, 1, 2, 2]
        
        notes = []
        for i in range(len(pitches)):
            pitch = pitches[i]
            channel = channels[i]
            notes.append(Note(pitch = pitch,
                              start = start_time, 
                              duration = harmony_length, 
                              dynamic = dynamic,
                              channel = channel))
        return notes
