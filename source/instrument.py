from mood import Mood
from os import listdir
from numpy import mean, dot, linalg

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
        mood_avg = {mood: [] for mood in Mood.mood_strs}
        for i in xrange(128):
            info = {}
            for mood in Mood.mood_strs:
                if instrument_count[i] != 0:
                    info[mood] = float(instrument_moods[i][mood]) / float(instrument_count[i])
                else:
                    info[mood] = 0.0
                mood_avg[mood].append(info[mood])
            info['ID'] = i
            info['Name'] = instrument_name[i]
            if instrument_remark[i] != '':
                info['Remark'] = instrument_remark[i]
            Instrument.descriptions.append(info)
        for mood in Mood.mood_strs:
            mood_avg[mood] = mean(mood_avg[mood])
        for i in xrange(128):
            for mood in Mood.mood_strs:
                Instrument.descriptions[i][mood] -= mood_avg[mood]
    
    @staticmethod
    def get_instruments(mood, seed):
        
        threshold = 50
        scores = [{'index': i, 'score': 0} for i in range(len(Instrument.descriptions))]
        for i in xrange(len(Instrument.descriptions)):
            instrument_mood = []
            ui_mood = []
            for mood_str in Mood.mood_strs:
                instrument_mood.append(Instrument.descriptions[i][mood_str])
                ui_mood.append(mood[mood_str] - threshold)
            if linalg.norm(ui_mood) != 0.0:
                scores[i]['score'] = dot(instrument_mood, ui_mood) / float(linalg.norm(ui_mood))
            else:
                scores[i]['score'] = 0
        scores.sort(cmp = Instrument.cmp_instruments_score, reverse = True)
        
        picked = []
        len_pick = 20
        for i in xrange(len_pick):
            score = scores[i]
            index = score['index']
            picked.append(Instrument.descriptions[index])
        
        index_offset = 0
        result = []
        
        # melody instrument 1
        index = (seed + index_offset) % len_pick
        while index_offset < len_pick and \
              ( (picked[index].has_key('Remark') and picked[index]['Remark'] == 'NH') or \
              picked[index]['ID'] >= 112):
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
        
if __name__ == '__main__':
    Instrument.init()
    Instrument.output_remark_mood()