from random import shuffle

class Mood:
    
    mood_strs = ['Angry', 'Scary', 'Comic', 'Happy', 'Sad', 'Mysterious', 'Romantic', 'Calm']
    Angry = 'Angry'
    Scary = 'Scary'
    Comic = 'Comic'
    Happy = 'Happy'
    Sad = 'Sad'
    Mysterious = 'Mysterious'
    Romantic = 'Romantic'
    Calm = 'Calm'

    @staticmethod
    def get_default_mood():
        result = {}
        for mood in Mood.mood_strs:
            result[mood] = 50
        return result
    
    @staticmethod
    def get_mood_correlation(mood_1, mood_2):
        mood_dict = {}
        for i in range(len(Mood.mood_strs)):
            mood_dict[Mood.mood_strs[i]] = i
        index_1 = mood_dict[mood_1]
        index_2 = mood_dict[mood_2]
        return Mood.get_mood_index_correlation(index_1, index_2)
        
    @staticmethod
    def get_mood_index_correlation(index_1, index_2):
        # lack 'comic' data, temporarily use 'happy' instead
        # temporarily set correlation('happy', 'comic') = 0.8
        correlation_matrix = [
            [1, 0.86, -0.68, -0.68, 0.2, 0.08, -0.85, -0.81],
            [0.86, 1, -0.85, -0.85, 0.54, 0.44, -0.77, -0.58],
            [-0.68, -0.85, 1, 0.8, -0.64, -0.64, 0.74, 0.46],
            [-0.68, -0.85, 0.8, 1, -0.64, -0.64, 0.74, 0.46],
            [0.2, 0.54, -0.64, -0.64, 1, 0.72, -0.20, 0.11],
            [0.08, 0.44, -0.64, -0.64, 0.72, 1, -0.23, 0.01],
            [-0.85, -0.77, 0.74, 0.74, -0.2, -0.23, 1, 0.84],
            [-0.81, -0.58, 0.46, 0.46, 0.11, 0.01, 0.84, 1]
        ] 
        return correlation_matrix[index_1][index_2]
    
    # adjust the mood value in order to satisfy the correlation
    @staticmethod
    def adjust_value(mood_data, maintained_mood_index):
        adjusted_data = [value for value in mood_data]
        
        for current_index in range(len(mood_data)):
            if current_index == maintained_mood_index:
                continue
            correlation = Mood.get_mood_index_correlation(current_index, maintained_mood_index)
            (min_value, max_value) = Mood.cal_range(correlation, mood_data[maintained_mood_index])
            adjusted_data[current_index] = max(min_value, adjusted_data[current_index])
            adjusted_data[current_index] = min(max_value, adjusted_data[current_index])
        
        for i in range(10):
            loop_outer = range(len(mood_data))
            loop_outer.remove(maintained_mood_index)
            shuffle(loop_outer)
            loop_inner = range(len(mood_data))
            loop_inner.remove(maintained_mood_index)
            shuffle(loop_inner)
            for index_1 in loop_outer:
                for index_2 in loop_inner:
                    correlation = Mood.get_mood_index_correlation(index_1, index_2)
                    (min_value, max_value) = Mood.cal_range(correlation, adjusted_data[index_1])
                    adjusted_data[index_2] = max(min_value, adjusted_data[index_2])
                    adjusted_data[index_2] = min(max_value, adjusted_data[index_2])
            if Mood.check(adjusted_data) == True:
                break
        return adjusted_data
    
    @staticmethod
    def check(adjust_data):
        for i in range(len(adjust_data)):
            for j in range(len(adjust_data)):
                if j <= i:
                    continue
                correlation = Mood.get_mood_index_correlation(i, j)
                if correlation > 0:
                    if abs(adjust_data[i] - adjust_data[j]) > 100 * (1 - correlation):
                        return False
                if correlation < 0:
                    if abs(adjust_data[i] - (100 - adjust_data[j])) > 100 * (1 + correlation):
                        return False
        return True
    
    @staticmethod
    def cal_range(correlation, ref):
        if correlation > 0:
            min_value = int(round(max(0, ref - 100 + correlation * 100)))
            max_value = int(round(min(100, ref + 100 - correlation * 100)))
        else:
            min_value = int(round(max(0, (-1) * ref - correlation * 100)))
            max_value = int(round(min(100, (-1) * ref + 200 + correlation * 100)))
        return (min_value, max_value)
    