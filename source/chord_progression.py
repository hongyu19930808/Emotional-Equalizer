from random import shuffle
from numpy import mean

class Analyzer:
    
    # find the first note of each bar
    # unit: the number of beats per chord
    @staticmethod
    def find_important_notes(melody_notes, unit):
        sorted_notes = sorted(melody_notes)
        important_notes = []
        current_beat = 0
        for note in sorted_notes:
            if note.start >= current_beat:
                important_notes.append(note)
                while note.start >= current_beat:
                    current_beat += unit
        while important_notes[-1].is_rest() == True:
            important_notes.pop()
        return important_notes
    
    @staticmethod
    def get_trans_matrix():
        prob = [5, 1, 1, 2, 1, 3, 1, 3, 1, 2, 1, 1]
        # probability for key modulation
        matrix = []
        for i in range(12):
            matrix.append([])
            for j in range(12):
                matrix[i].append(prob[(j-i)%12])
        result = {}
        for i in range(12):
            result[i] = {}
            for j in range(12):
                result[i][j] = matrix[i][j]
        return result
    
    @staticmethod
    def get_emit_matrix():
        prob = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        # probability for key -> melody
        matrix = []
        for i in range(12):
            matrix.append([])
            for j in range(12):
                matrix[i].append(prob[(j-i)%12])
        result = {}
        for i in range(12):
            result[i] = {}
            for j in range(12):
                result[i][j] = matrix[i][j]
        return result    
    
    @staticmethod
    def find_tonality(melody_notes, important_notes, unit):
        if len(melody_notes) == 0:
            raise 'no notes, error'
        
        # get first (important) note
        if len(important_notes) != 0:
            notes = important_notes
        else:
            notes = melody_notes
        for i in range(len(notes)):
            note = notes[i]
            if note.is_rest() == False:
                first_note = note
                break
        
        trans_matrix = Analyzer.get_trans_matrix()
        emit_matrix = Analyzer.get_emit_matrix()          
        start_array = {i:1 for i in range(12)}
        for offset in [0, 4, 7, 9]:
            start_array[(first_note.pitch - offset) % 12] = 2
        states = range(12)  
        observations = []
        for note in melody_notes:
            if note.is_rest() == False:
                index = int(note.start / unit)
                while len(observations) <= index:
                    observations.append([])
                observations[index].append((note.pitch % 12, note.duration))     
        for note in important_notes:
            if note.is_rest() == False:
                index = int(note.start / unit)
                while len(observations) <= index:
                    observations.append([])
                observations[index].append((note.pitch % 12, note.duration))
        result = Analyzer.viterbi(observations, states, start_array, trans_matrix, emit_matrix)
        
        tonalities = []
        start = 0
        end = 1
        change_points = [0]
        while True:
            if end < len(result) and result[start] == result[end]:
                end = end + 1
            else:
                notes_within_key = []
                for note in important_notes:
                    if note.is_rest() == False and note.start >= start * unit and note.start < end * unit:
                        notes_within_key.append(note)                
                if len(notes_within_key) == 0:
                    mode = 'Major'
                    offset = 0
                else:
                    count_major = 0
                    count_minor = 0
                    for note in notes_within_key:
                        if (note.pitch - result[start]) % 12 in [0, 7]:
                            count_major += note.duration
                        if (note.pitch - result[start]) % 12 in [9, 4]:
                            count_minor += note.duration
                    if count_major > count_minor:
                        mode = 'Major'
                        offset = 0
                    else:
                        mode = 'Minor'
                        offset = 9
                for i in range(start, end):
                    tonalities.append({'key': (result[start] + offset) % 12, 'mode': mode})
                if end >= len(result):
                    break
                change_points.append(end)
                start = end
                end = end + 1
        return (tonalities, change_points)
    
    @staticmethod
    def cal_emit_prob(emit_p, st, obs):
        if len(obs) == 0:
            return float(max(emit_p[st]))
        score = 0
        all_duration = 0
        for (pitch, duration) in obs:
            score += emit_p[st][pitch] * duration
            all_duration += duration
        return float(score) / float(duration)
    
    # modified from the website: https://en.wikipedia.org/wiki/Viterbi_algorithm
    @staticmethod
    def viterbi(obs, states, start_p, trans_p, emit_p, last_state = None):
        shuffled_states = [element for element in states]
        V = [{}]
        for st in states:
            V[0][st] = {"prob": start_p[st] * Analyzer.cal_emit_prob(emit_p, st, obs[0]), "prev": None}
        # Run Viterbi when t > 0
        for t in range(1, len(obs)):
            V.append({})
            for st in states:
                max_tr_prob = max(V[t-1][prev_st]["prob"] * trans_p[prev_st][st] for prev_st in states)
                shuffle(shuffled_states)
                for prev_st in shuffled_states:
                    if V[t-1][prev_st]["prob"] * trans_p[prev_st][st] == max_tr_prob:
                        max_prob = max_tr_prob * Analyzer.cal_emit_prob(emit_p, st, obs[t])
                        # the last chord should be tonic chord
                        if last_state != None:
                            if t == len(obs) - 1 and st != last_state:
                                max_prob = 0
                        V[t][st] = {"prob": max_prob, "prev": prev_st}
                        break
            if mean([V[t][st]["prob"] for st in states]) > pow(2, 32):
                for st in states:
                    V[t][st]["prob"] = V[t][st]["prob"] / pow(2, 32)
            if mean([V[t][st]["prob"] for st in states]) < pow(2, -32):
                for st in states:
                    V[t][st]["prob"] = V[t][st]["prob"] * pow(2, 32)
        opt = []
        # The highest probability
        max_prob = max(value["prob"] for value in V[-1].values())
        previous = None
        # Get most probable state and its backtrack
        for st, data in V[-1].items():
            if data["prob"] == max_prob:
                opt.append(st)
                previous = st
                break
        # Follow the backtrack till the first observation
        for t in range(len(V) - 2, -1, -1):
            opt.insert(0, V[t + 1][previous]["prev"])
            previous = V[t + 1][previous]["prev"]
        return opt
    
    @staticmethod
    def annotate_notes(notes, tonality):
        # 0: rest
        # 1, 2, 3, ...: tonic, supertonic, mediant, ...
        # 1.5, 2.5, ...: chromatic note
        profile = []
        if tonality['mode'] == 'Major':
            profile = [1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7]
        else:
            profile = [1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 7.5]
        result = []
        for note in notes:
            if note.is_rest() == False:
                normalized_pitch = (note.pitch - tonality['key']) % 12
                result.append({'notation': profile[normalized_pitch],
                               'note': note})
            else:
                result.append({'notation': 0,
                               'note': note})            
        return result
    
    @staticmethod
    def annotate_all_notes(notes, tonalities, unit):
        result = []
        for note in notes:
            # 0: rest
            # 1, 2, 3, ...: tonic, supertonic, mediant, ...
            # 1.5, 2.5, ...: chromatic note            
            index = int(note.start / unit)
            tonality = tonalities[index]
            profile = []
            if tonality['mode'] == 'Major':
                profile = [1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7]
            else:
                profile = [1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 7.5]            

            if note.is_rest() == False:
                normalized_pitch = (note.pitch - tonality['key']) % 12
                result.append({'notation': profile[normalized_pitch],
                               'note': note})
            else:
                result.append({'notation': 0,
                               'note': note})            
        return result

class Composer:

    @staticmethod
    def gen_chord_progression(annotated_notes, change_points, unit, parameter = None):
        observation_positions = []
        observations = []
        note_index = 0
        change_point_index = 0
        change_point_remarks = []
        for note in annotated_notes:
            notation = note['notation']
            if notation in [1,2,3,4,5,6,7]:
                observation_positions.append(note_index)
                observations.append(notation)
                if change_point_index < len(change_points) and note['note'].start > change_points[change_point_index] * unit:
                    change_point_remarks.append(1)
                    change_point_index += 1
                else:
                    change_point_remarks.append(0)
            note_index = note_index + 1
        progression_notations = [0 for i in range(len(annotated_notes))]
        if len(observations) == 0:
            return progression_notations
        # viterbi
        states = [1,2,3,4,5,6,7]
        trans_matrix = Composer.get_trans_matrix()
        emit_matrix = Composer.get_emit_matrix()
        start_array = Composer.get_start_array()
        result = Composer.viterbi(observations, states, start_array, trans_matrix, emit_matrix, change_point_remarks, last_state = 1)
        # find chord position
        for i in range(len(result)):
            note_index = observation_positions[i]
            progression_notations[note_index] = result[i]
        return progression_notations
    
    # adjust the chord progression according to the mode
    @staticmethod
    def adjust_progression(progression_notations, annotated_important_notes, param):
        adjusted_progressions = [progression for progression in progression_notations]
        mode = param['mode'][0]    
        # Major case
        if mode >= 0 and mode < 1.0 / 2.0:
            original = [1, 4, 5, 7]
            adjusted = [6, 2, 3, 3]
        if mode >= 1.0 / 2.0 and mode < 3.0 / 4.0:
            original = [6, 4, 5, 7]
            adjusted = [1, 2, 3, 3]
        if mode >= 3.0 / 4.0 and mode < 1:
            original = [6, 4, 3, 7]
            adjusted = [1, 2, 5, 5]
        if mode >= 1:
            original = [6, 2, 3, 7]
            adjusted = [1, 4, 5, 5]
        # Minor case
        if mode < 0 and mode >= -1.0 / 2.0:
            original = [1, 4, 5, 2]
            adjusted = [3, 6, 7, 7]
        if mode < -1.0 / 2.0 and mode >= -3.0 / 4.0:
            original = [3, 4, 5, 2]
            adjusted = [1, 6, 7, 7]
        if mode < -3.0 / 4.0 and mode >= -1:
            original = [3, 4, 7, 2]
            adjusted = [1, 6, 5, 5]
        if mode < -1:
            original = [3, 6, 7, 2]
            adjusted = [1, 4, 5, 5]
        
        # Adjust
        emit_matrix = Composer.get_emit_matrix()
        for i in range(len(annotated_important_notes)):
            melody_notation = annotated_important_notes[i]['notation']
            progression_notation = progression_notations[i]
            if progression_notation in original:
                adjusted_notation = adjusted[original.index(progression_notation)]
                if emit_matrix[adjusted_notation][melody_notation] > 0:
                    adjusted_progressions[i] = adjusted_notation
        return adjusted_progressions
    
    @staticmethod
    def get_trans_matrix(parameter = None):
        matrix = [
            # probability for chord transition I->I, I->II, I->III, ...
            [2, 2, 2, 2, 2, 2, 0], 
            # probability for chord transition II->I, II->II, II->III, ...
            [1, 1, 2, 1, 2, 1, 0],
            [2, 0, 1, 0, 1, 2, 0],
            [1, 1, 2, 1, 2, 1, 0],
            [2, 0, 1, 0, 1, 2, 0],
            [2, 2, 2, 2, 2, 2, 0], 
            [2, 0, 1, 0, 1, 2, 0]
        ]
        result = {}
        for i in range(7):
            result[i+1] = {}
            for j in range(7):
                result[i+1][j+1] = matrix[i][j]
        return result
    
    @staticmethod
    def get_emit_matrix(parameter = None):
        # probability for chord -> melody
        matrix = [
            [2, 0, 2, 0, 1, 0, 0],
            [0, 1, 0, 2, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 2],
            [1, 0, 0, 1, 0, 2, 0],
            [0, 2, 0, 1, 1, 0, 1],
            [2, 0, 1, 0, 0, 2, 0],
            [0, 1, 0, 1, 0, 0, 1]
        ]
        result = {}
        for i in range(7):
            result[i+1] = {}
            for j in range(7):
                result[i+1][j+1] = matrix[i][j]
        return result
    
    @staticmethod
    def get_start_array():
        return {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    
    # modified from the website: https://en.wikipedia.org/wiki/Viterbi_algorithm
    @staticmethod
    def viterbi(obs, states, start_p, trans_p, emit_p, change_point_remarks, last_state = None):
        shuffled_states = [element for element in states]
        V = [{}]
        for st in states:
            V[0][st] = {"prob": start_p[st] * emit_p[st][obs[0]], "prev": None}
        # Run Viterbi when t > 0
        for t in range(1, len(obs)):
            V.append({})
            for st in states:
                if change_point_remarks[t] == 0:
                    max_tr_prob = max(V[t-1][prev_st]["prob"] * trans_p[prev_st][st] for prev_st in states)
                else:
                    max_tr_prob = max(V[t-1][prev_st]["prob"] * 1 for prev_st in states)
                shuffle(shuffled_states)
                for prev_st in shuffled_states:
                    if change_point_remarks[t] == 0:
                        trans_p_prev_curr = trans_p[prev_st][st] 
                    else:
                        trans_p_prev_curr = 1
                    if V[t-1][prev_st]["prob"] * trans_p_prev_curr == max_tr_prob:
                        max_prob = max_tr_prob * emit_p[st][obs[t]]
                        # the last chord should be tonic chord
                        if last_state != None:
                            if t == len(obs) - 1 and st != last_state:
                                max_prob = 0
                        V[t][st] = {"prob": max_prob, "prev": prev_st}
                        break
            if mean([V[t][st]["prob"] for st in states]) > pow(2, 32):
                for st in states:
                    V[t][st]["prob"] = V[t][st]["prob"] / pow(2, 32)
            if mean([V[t][st]["prob"] for st in states]) < pow(2, -32):
                for st in states:
                    V[t][st]["prob"] = V[t][st]["prob"] * pow(2, 32)            
        opt = []
        # The highest probability
        max_prob = max(value["prob"] for value in V[-1].values())
        previous = None
        # Get most probable state and its backtrack
        for st, data in V[-1].items():
            if data["prob"] == max_prob:
                opt.append(st)
                previous = st
                break
        # Follow the backtrack till the first observation
        for t in range(len(V) - 2, -1, -1):
            opt.insert(0, V[t + 1][previous]["prev"])
            previous = V[t + 1][previous]["prev"]
        return opt