from mood import Mood
from os import listdir

class Instrument:
    
    descriptions = None
    
    @staticmethod
    def output_remark_mood():
        print 'Not High', '\t', 'Not Low', '\t',
        for mood in Mood.mood_strs:
            print mood, '\t',
        print ''
        for instrument in Instrument.descriptions:
            if instrument.has_key('Remark') and (instrument['Remark'] == 'NH'):
                print '1', '\t',
            else:
                print '0', '\t',
            if instrument.has_key('Remark') and (instrument['Remark'] == 'NL'):
                print '1', '\t',
            else:
                print '0', '\t',            
            for mood in Mood.mood_strs:
                print instrument[mood], '\t',
            print ''

    @staticmethod
    def output_name_remark():
        for instrument in Instrument.descriptions:
            if instrument.has_key('Remark'):
                print instrument['Name'] + '\t' + instrument['Remark']
            else:
                print instrument['Name']
    
    @staticmethod        
    def init():
        # read listening test results
        instrument_moods = {i: {} for i in xrange(128)}
        instrument_count = {i: 0 for i in xrange(128)}
        files = listdir('./tools/moods/')
        for file_name in files:
            if file_name.endswith('.csv'):
                fin = open('./tools/moods/' + file_name, 'r')
                fin.readline()
                while True:
                    line = fin.readline().strip('\r\n')
                    if line == '':
                        break
                    elements = line.split(',')
                    ins_num = int(elements[0][4:])
                    instrument_count[ins_num] += 1
                    for i in xrange(len(Mood.mood_strs)):
                        mood = Mood.mood_strs[i]
                        if instrument_moods[ins_num].has_key(mood):
                            instrument_moods[ins_num][mood] += int(elements[i+1])
                        else:
                            instrument_moods[ins_num][mood] = int(elements[i+1])
                fin.close()
        
        # read meta info
        instrument_name = []
        instrument_remark = []
        fin = open('./tools/instruments_meta_info.csv', 'r')
        while True:
            line = fin.readline().strip('\r\n')
            if line == '':
                break
            elements = line.split(',')
            instrument_name.append(elements[1])
            instrument_remark.append(elements[2])
        fin.close()
        
        # average the subjects' responses
        Instrument.descriptions = []
        for i in xrange(128):
            info = {}
            for mood in Mood.mood_strs:
                if instrument_count[i] != 0:
                    info[mood] = float(instrument_moods[i][mood]) / float(instrument_count[i])
                else:
                    info[mood] = 0.0
            info['ID'] = i
            info['Name'] = instrument_name[i]
            if instrument_remark[i] != '':
                info['Remark'] = instrument_remark[i]
            Instrument.descriptions.append(info)
    
    @staticmethod
    def get_instruments(mood, seed):
        len_pick = 12
        threshold = 49.9
        scores = [{'index': i, 'score': 0} for i in range(len(Instrument.descriptions))]
        for i in xrange(len(Instrument.descriptions)):
            for mood_str in mood.keys():
                score = Instrument.descriptions[i][mood_str] - 1
                scores[i]['score'] += (score * (mood[mood_str] - threshold))
        scores.sort(cmp = Instrument.cmp_instruments_score, reverse = True)
        
        picked = []
        for i in xrange(len_pick):
            score = scores[i]
            index = score['index']
            picked.append(Instrument.descriptions[index])
        
        index_offset = 0
        result = []
        
        # melody instrument 1
        index = (seed + index_offset) % len_pick
        while index_offset < len_pick and picked[index].has_key('Remark') and picked[index]['Remark'] == 'NH':
            index_offset += 1
            index = (seed + index_offset) % len_pick
        result.append(picked[index])
        index_offset += 1
        
        # harmony instrument 1
        index = (seed + index_offset) % len_pick
        while index_offset < len_pick and picked[index].has_key('Remark') and picked[index]['Remark'] == 'NL':
            index_offset += 1
            index = (seed + index_offset) % len_pick
        result.append(picked[index])
        index_offset += 1
        
        # harmony instrument 2
        index = (seed + index_offset) % len_pick
        while index_offset < len_pick and picked[index].has_key('Remark') and picked[index]['Remark'] == 'NL':
            index_offset += 1
            index = (seed + index_offset) % len_pick
        result.append(picked[index])
        index_offset += 1
        
        return (result, index_offset - 3)
    
    @staticmethod            
    def cmp_instruments_score(score_1, score_2):
        if score_1['score'] > score_2['score']:
            return 1
        if score_1['score'] == score_2['score']:
            return 0
        if score_1['score'] < score_2['score']:
            return -1
        
    @staticmethod
    def init_old_version():
        Instrument.descriptions = [
            {'Name': 'Acoustic Grand Piano', 'Type': 'Piano', 'ID': 0, 
             'Is': [Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic]},
            {'Name': 'Bright Acoustic Piano', 'Type': 'Piano', 'ID': 1, 
             'Is': [], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic]}, 
            {'Name': 'Electric Grand Piano', 'Type': 'Piano', 'ID': 2, 
             'Is': [Mood.Comic, Mood.Scary, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic]}, 
            {'Name': 'Honky-tonk Piano', 'Type': 'Piano', 'ID': 3, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Electric Piano 1', 'Type': 'Piano', 'ID': 4, 
             'Is': [Mood.Scary, Mood.Comic, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Romantic]}, 
            {'Name': 'Electric Piano 2', 'Type': 'Piano', 'ID': 5, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Harpsichord', 'Type': 'Piano', 'ID': 6, 
             'Is': [], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Clavinet', 'Type': 'Piano', 'ID': 7, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Celesta', 'Type': 'Chromatic Percussion', 'ID': 8, 
             'Is': [Mood.Comic, Mood.Happy, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Glockenspiel', 'Type': 'Chromatic Percussion', 'ID': 9, 'Remark': 'NL',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Music Box', 'Type': 'Chromatic Percussion', 'ID': 10, 'Remark': 'NL',
             'Is': [Mood.Happy, Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Angry]}, 
            {'Name': 'Vibraphone', 'Type': 'Chromatic Percussion', 'ID': 11, 'Remark': 'NL',
             'Is': [Mood.Scary, Mood.Mysterious], 
             'Is Not': [Mood.Angry]}, 
            {'Name': 'Marimba', 'Type': 'Chromatic Percussion', 'ID': 12, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Calm]}, 
            {'Name': 'Xylophone', 'Type': 'Chromatic Percussion', 'ID': 13, 'Remark': 'NL',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Tubular Bells', 'Type': 'Chromatic Percussion', 'ID': 14, 'Remark': 'NL',
             'Is': [], 
             'Is Not': [Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Dulcimer', 'Type': 'Chromatic Percussion', 'ID': 15, 'Remark': 'NH',
             'Is': [Mood.Angry, Mood.Scary], 
             'Is Not': [Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Drawbar Organ', 'Type': 'Organ', 'ID': 16, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Happy, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Percussive Organ', 'Type': 'Organ', 'ID': 17, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Rock Organ', 'Type': 'Organ', 'ID': 18, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Church Organ', 'Type': 'Organ', 'ID': 19, 
             'Is': [Mood.Scary, Mood.Angry], 
             'Is Not': [Mood.Comic, Mood.Sad, Mood.Happy, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Reed Organ', 'Type': 'Organ', 'ID': 20, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Accordion', 'Type': 'Organ', 'ID': 21, 'Remark': 'NL',
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Harmonica', 'Type': 'Organ', 'ID': 22, 'Remark': 'NL',
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Tango Accordion', 'Type': 'Organ', 'ID': 23, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Happy, Mood.Calm]}, 
            {'Name': 'Acoustic Guitar (nylon)', 'Type': 'Guitar', 'ID': 24, 
             'Is': [Mood.Comic, Mood.Happy, Mood.Mysterious, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Scary]}, 
            {'Name': 'Acoustic Guitar (steel)', 'Type': 'Guitar', 'ID': 25, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary]}, 
            {'Name': 'Electric Guitar (jazz)', 'Type': 'Guitar', 'ID': 26, 
             'Is': [Mood.Comic, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry]}, 
            {'Name': 'Electric Guitar (clean)', 'Type': 'Guitar', 'ID': 27, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Electric Guitar (muted)', 'Type': 'Guitar', 'ID': 28, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic]}, 
            {'Name': 'Overdriven Guitar', 'Type': 'Guitar', 'ID': 29, 
             'Is': [Mood.Angry, Mood.Scary], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Distortion Guitar', 'Type': 'Guitar', 'ID': 30, 
             'Is': [Mood.Angry, Mood.Scary], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Guitar Harmonics', 'Type': 'Guitar', 'ID': 31, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Acoustic Bass', 'Type': 'Bass', 'ID': 32, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Romantic]}, 
            {'Name': 'Electric Bass (finger)', 'Type': 'Bass', 'ID': 33, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Romantic]}, 
            {'Name': 'Electric Bass (pick)', 'Type': 'Bass', 'ID': 34, 'Remark': 'NH',
             'Is': [Mood.Comic, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Romantic]}, 
            {'Name': 'Fretless Bass', 'Type': 'Bass', 'ID': 35, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Slap Bass 1', 'Type': 'Bass', 'ID': 36, 'Remark': 'NH',
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Slap Bass 2', 'Type': 'Bass', 'ID': 37, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Happy, Mood.Romantic]}, 
            {'Name': 'Synth Bass 1', 'Type': 'Bass', 'ID': 38, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Synth Bass 2', 'Type': 'Bass', 'ID': 39, 'Remark': 'NH',
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Violin', 'Type': 'Strings', 'ID': 40, 'Remark': 'NL',
             'Is': [Mood.Scary, Mood.Sad, Mood.Romantic], 
             'Is Not': [Mood.Happy, Mood.Mysterious, Mood.Calm]},
            {'Name': 'Viola', 'Type': 'Strings', 'ID': 41, 'Remark': 'NH',
             'Is': [Mood.Scary, Mood.Sad, Mood.Romantic], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Mysterious]}, 
            {'Name': 'Cello', 'Type': 'Strings', 'ID': 42, 'Remark': 'NH',
             'Is': [Mood.Scary, Mood.Sad, Mood.Romantic], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Mysterious]}, 
            {'Name': 'Contrabass', 'Type': 'Strings', 'ID': 43, 'Remark': 'NH',
             'Is': [Mood.Scary, Mood.Sad, Mood.Romantic], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Mysterious]}, 
            {'Name': 'Tremolo Strings', 'Type': 'Strings', 'ID': 44, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Pizzicato Strings', 'Type': 'Strings', 'ID': 45, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Orchestral Harp', 'Type': 'Strings', 'ID': 46, 
             'Is': [Mood.Happy, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Romantic]}, 
            {'Name': 'Timpani', 'Type': 'Percussive', 'ID': 47, 'Remark': 'NH',
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]},
            {'Name': 'String Ensemble 1', 'Type': 'Strings', 'ID': 48, 
             'Is': [Mood.Sad, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry]},
            {'Name': 'String Ensemble 2', 'Type': 'Strings', 'ID': 49, 
             'Is': [Mood.Sad, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Scary]},
            {'Name': 'Synth Strings 1', 'Type': 'Strings', 'ID': 50, 
             'Is': [Mood.Scary, Mood.Sad], 
             'Is Not': [Mood.Comic, Mood.Happy]},
            {'Name': 'Synth Strings 2', 'Type': 'Strings', 'ID': 51, 
             'Is': [Mood.Scary, Mood.Mysterious, Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy]}, 
            {'Name': 'Choir Aahs', 'Type': 'Voice', 'ID': 52, 
             'Is': [Mood.Scary, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Voice Oohs', 'Type': 'Voice', 'ID': 53, 
             'Is': [Mood.Scary, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry]}, 
            {'Name': 'Synth Choir', 'Type': 'Voice', 'ID': 54, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad]}, 
            {'Name': 'Orchestra Hit', 'Type': 'Percussive', 'ID': 55, 
             'Is': [Mood.Angry, Mood.Happy], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Trumpet', 'Type': 'Brass', 'ID': 56, 'Remark': 'NL',
             'Is': [Mood.Angry, Mood.Scary], 
             'Is Not': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Trombone', 'Type': 'Brass', 'ID': 57, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Calm]}, 
            {'Name': 'Tuba', 'Type': 'Brass', 'ID': 58, 
             'Is': [Mood.Scary, Mood.Comic, Mood.Sad], 
             'Is Not': [Mood.Mysterious, Mood.Romantic]}, 
            {'Name': 'Muted Trumpet', 'Type': 'Brass', 'ID': 59, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'French Horn', 'Type': 'Brass', 'ID': 60,
             'Is': [Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Comic]},
            {'Name': 'Brass Section', 'Type': 'Brass', 'ID': 61, 
             'Is': [Mood.Scary, Mood.Happy, Mood.Sad], 
             'Is Not': [Mood.Angry]}, 
            {'Name': 'Synth Brass 1', 'Type': 'Brass', 'ID': 62, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Synth Brass 2', 'Type': 'Brass', 'ID': 63, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Soprano Sax', 'Type': 'Reed', 'ID': 64, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Alto Sax', 'Type': 'Reed', 'ID': 65, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Tenor sax', 'Type': 'Reed', 'ID': 66, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Happy, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Baritone Sax', 'Type': 'Reed', 'ID': 67, 
             'Is': [Mood.Angry, Mood.Comic], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Oboe', 'Type': 'Reed', 'ID': 68, 
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'English Horn', 'Type': 'Reed', 'ID': 69, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Mysterious, Mood.Romantic]}, 
            {'Name': 'Bassoon', 'Type': 'Reed', 'ID': 70, 
             'Is': [Mood.Scary, Mood.Happy, Mood.Sad, Mood.Calm], 
             'Is Not': [Mood.Angry]},
            {'Name': 'Clarinet', 'Type': 'Reed', 'ID': 71, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Happy, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Piccolo', 'Type': 'Pipe', 'ID': 72, 'Remark': 'NL',
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Flute', 'Type': 'Pipe', 'ID': 73, 'Remark': 'NL',
             'Is': [Mood.Comic, Mood.Happy, Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Romantic]}, 
            {'Name': 'Recorder', 'Type': 'Pipe', 'ID': 74, 
             'Is': [Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Romantic]}, 
            {'Name': 'Pan Flute', 'Type': 'Pipe', 'ID': 75, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Blown bottle', 'Type': 'Pipe', 'ID': 76, 
             'Is': [Mood.Comic, Mood.Happy, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad]}, 
            {'Name': 'Shakuhachi', 'Type': 'Pipe', 'ID': 77, 'Remark': 'NL',
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Calm]}, 
            {'Name': 'Whistle', 'Type': 'Pipe', 'ID': 78, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Ocarina', 'Type': 'Pipe', 'ID': 79, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Lead 1 (square)', 'Type': 'Synth Lead', 'ID': 80, 
             'Is': [Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Lead 2 (sawtooth)', 'Type': 'Synth Lead', 'ID': 81, 
             'Is': [Mood.Angry, Mood.Scary, Mood.Comic], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Lead 3 (calliope)', 'Type': 'Synth Lead', 'ID': 82, 
             'Is': [Mood.Scary], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Lead 4 (chiff)', 'Type': 'Synth Lead', 'ID': 83, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Lead 5 (charang)', 'Type': 'Synth Lead', 'ID': 84, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Lead 6 (voice)', 'Type': 'Synth Lead', 'ID': 85, 
             'Is': [Mood.Scary, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious]}, 
            {'Name': 'Lead 7 (fifths)', 'Type': 'Synth Lead', 'ID': 86, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Lead 8 (bass + lead)', 'Type': 'Synth Lead', 'ID': 87, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Pad 1 (new age)', 'Type': 'Synth Pad', 'ID': 88, 
             'Is': [Mood.Scary, Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Sad]}, 
            {'Name': 'Pad 2 (warm)', 'Type': 'Synth Pad', 'ID': 89, 
             'Is': [Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic]},
            {'Name': 'Pad 3 (polysynth)', 'Type': 'Synth Pad', 'ID': 90, 
             'Is': [], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Pad 4 (choir)', 'Type': 'Synth Pad', 'ID': 91, 
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy]}, 
            {'Name': 'Pad 5 (bowed)', 'Type': 'Synth Pad', 'ID': 92,
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Pad 6 (metallic)', 'Type': 'Synth Pad', 'ID': 93, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Pad 7 (halo)', 'Type': 'Synth Pad', 'ID': 94, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Pad 8 (sweep)', 'Type': 'Synth Pad', 'ID': 95, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'FX 1 (rain)', 'Type': 'Synth Effects', 'ID': 96, 
             'Is': [Mood.Mysterious, Mood.Calm], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Sad]}, 
            {'Name': 'FX 2 (soundtrack)', 'Type': 'Synth Effects', 'ID': 97, 
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'FX 3 (crystal)', 'Type': 'Synth Effects', 'ID': 98, 
             'Is': [], 
             'Is Not': [Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'FX 4 (atmosphere)', 'Type': 'Synth Effects', 'ID': 99, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'FX 5 (brightness)', 'Type': 'Synth Effects', 'ID': 100, 
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Calm]},
            {'Name': 'FX 6 (goblins)', 'Type': 'Synth Effects', 'ID': 101, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Comic, Mood.Happy, Mood.Romantic, Mood.Sad, Mood.Calm]}, 
            {'Name': 'FX 7 (echoes)', 'Type': 'Synth Effects', 'ID': 102, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Calm]}, 
            {'Name': 'FX 8 (sci-fi)', 'Type': 'Synth Effects', 'ID': 103, 
             'Is': [Mood.Mysterious], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Sitar', 'Type': 'Ethnic', 'ID': 104, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Banjo', 'Type': 'Ethnic', 'ID': 105, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Shamisen', 'Type': 'Ethnic', 'ID': 106, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Koto', 'Type': 'Ethnic', 'ID': 107, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Kalimba', 'Type': 'Ethnic', 'ID': 108, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Bagpipes', 'Type': 'Ethnic', 'ID': 109, 
             'Is': [Mood.Angry, Mood.Comic], 
             'Is Not': [Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Fiddle', 'Type': 'Ethnic', 'ID': 110, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Shannai', 'Type': 'Ethnic', 'ID': 111, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Tinkle Bell', 'Type': 'Percussive', 'ID': 112, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Agogo', 'Type': 'Percussive', 'ID': 113, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Steel Drums', 'Type': 'Percussive', 'ID': 114, 
             'Is': [Mood.Comic, Mood.Happy], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Woodblock', 'Type': 'Percussive', 'ID': 115, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Taiko Drum', 'Type': 'Percussive', 'ID': 116, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Melodic Tom', 'Type': 'Percussive', 'ID': 117, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Synth Drum', 'Type': 'Percussive', 'ID': 118, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Reverse Cymbal', 'Type': 'Percussive', 'ID': 119, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Guitar Fret Noise', 'Type': 'Sound effects', 'ID': 120, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]},
            {'Name': 'Breath Noise', 'Type': 'Sound effects', 'ID': 121, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Seashore', 'Type': 'Sound effects', 'ID': 122, 
             'Is': [Mood.Angry], 
             'Is Not': [Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Bird Tweet', 'Type': 'Sound effects', 'ID': 123, 
             'Is': [Mood.Comic], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Telephone Ring', 'Type': 'Sound effects', 'ID': 124, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Helicopter', 'Type': 'Sound effects', 'ID': 125, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Applause', 'Type': 'Sound effects', 'ID': 126, 
             'Is': [], 
             'Is Not': [Mood.Angry, Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}, 
            {'Name': 'Gunshot', 'Type': 'Sound effects', 'ID': 127, 
             'Is': [Mood.Angry], 
             'Is Not': [Mood.Scary, Mood.Comic, Mood.Happy, Mood.Sad, Mood.Mysterious, Mood.Romantic, Mood.Calm]}
        ]
        
if __name__ == '__main__':
    Instrument.init()
    Instrument.output_remark_mood()