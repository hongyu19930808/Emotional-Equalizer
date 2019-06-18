import os
import csv
from collections import OrderedDict
from numpy import mean, std, sqrt
from scipy.stats import t, norm
from sys import float_info
from matplotlib import pyplot as plt

def get_confidence_interval_bern(X):
    n = len(X)
    p = mean(X)
    alpha = 1.0 - 0.95
    z = norm.ppf(1-alpha/2.0)
    wneg = max(0, (2*n*p + z*z - (z*sqrt(z*z - 1/float(n) + 4*n*p*(1-p) + (4*p-2)) + 1.0)) / float(2*(n+z*z)))
    wpos = min(1, (2*n*p + z*z + (z*sqrt(z*z - 1/float(n) + 4*n*p*(1-p) - (4*p-2)) + 1.0)) / float(2*(n+z*z)))
    # if p = 0 then w- = 0
    if p < float_info.epsilon:
        wneg = 0
    # if p = 1 then w+ = 1
    if p > 1 - float_info.epsilon:
        wpos = 1
    neg_error = p - wneg
    pos_error = wpos - p
    return (p, pos_error, neg_error, wpos, wneg)

def get_confidence_interval_cont(X):
    n = len(X)
    X_mean = mean(X)
    X_std = std(X, ddof = 1)
    # 95% Confidence Interval
    dof = n - 1
    alpha = 1.0 - 0.95
    conf_interval = t.ppf(1-alpha/2.0, dof) * X_std * sqrt(1.0/n)
    return (X_mean, conf_interval, conf_interval, X_mean + conf_interval, X_mean - conf_interval)

def count(X):
    results = [0,0,0,0,0]
    for element in X:
        results[element - 1] += 1
    for i in xrange(len(results)):
        results[i] /= float(len(X))
    return results

def main():
    moods = ['angry', 'scary', 'comic', 'happy', 'sad', 'mysterious', 'romantic', 'calm']
    excerpts = {'avengers': 'film',
                'chopin': 'romanticism', 
                'faded': 'pop', 
                'jazz': 'jazz',
                'mario': 'game',
                'mozart': 'classicism'
                }
    files = os.listdir('./evaluation/')
    
    mood_distributions = OrderedDict()
    for mood_pred in moods:
        mood_distributions[mood_pred] = OrderedDict()
        for mood_actual in moods:
            mood_distributions[mood_pred][mood_actual] = []
            
    details_quality = OrderedDict()
    for mood in moods:
        details_quality[mood] = OrderedDict()
        for excerpt in excerpts.keys():
            details_quality[mood][excerpt] = []
    
    excerpt_quality = OrderedDict()
    for excerpt in excerpts.keys():
        excerpt_quality[excerpt] = []
        
    mood_quality = OrderedDict()
    for mood in moods:
        mood_quality[mood] = []
    
    overall_quality = []
    
    for file_name in files:
        if file_name.endswith('.csv'):
            # read file
            fin = open('./evaluation/' + file_name, 'r')
            reader = csv.reader(fin)
            results = []
            for item in reader:
                if reader.line_num == 1:
                    continue
                results.append(item)
            fin.close()
        
            for row in results:
                excerpt_mood = row[0].split('.')[0]
                excerpt = excerpt_mood.split('-')[0]
                mood_actual = excerpt_mood.split('-')[1]
                for i in xrange(8):
                    mood_distributions[moods[i]][mood_actual].append(int(row[i+1]))
                details_quality[mood_actual][excerpt].append(int(row[9]) + 1)
                excerpt_quality[excerpt].append(int(row[9]) + 1)
                mood_quality[mood_actual].append(int(row[9]) + 1)
                overall_quality.append(int(row[9]) + 1)    
    
    # draw figure
    figure = plt.figure(figsize = (10, 5))
    plt.title('Quality Distribution')
    plt.ylabel('Ratio')
    x_value = ['1', '2', '3', '4', '5']
    y_value = count(overall_quality)
    plt.bar(x_value, y_value, figure = figure)
    plt.show()
    
    for mood in moods:
        figure = plt.figure(figsize = (10, 5))
        plt.title('Quality Distribution - ' + mood.capitalize())
        plt.ylabel('Ratio')
        x_value = ['1', '2', '3', '4', '5']
        y_value = count(mood_quality[mood])
        plt.bar(x_value, y_value, figure = figure)
        plt.show()
        
    for excerpt in excerpts.keys():
        figure = plt.figure(figsize = (10, 5))
        plt.title('Quality Distribution - ' + excerpt.capitalize())
        plt.ylabel('Count')
        x_value = ['1', '2', '3', '4', '5']
        y_value = count(excerpt_quality[excerpt])
        plt.bar(x_value, y_value, figure = figure)
        plt.show()    
    
    # process data
    for mood_pred in moods:
        for mood_actual in moods:
            mood_distributions[mood_pred][mood_actual] = \
                get_confidence_interval_bern(mood_distributions[mood_pred][mood_actual])
            
    for mood in moods:
        for excerpt in excerpts.keys():
            details_quality[mood][excerpt] = \
                get_confidence_interval_cont(mood_distributions[mood_pred][mood_actual])
            
    for excerpt in excerpts.keys():
        excerpt_quality[excerpt] = \
            get_confidence_interval_cont(excerpt_quality[excerpt])
        
    for mood in moods:
        mood_quality[mood] = \
            get_confidence_interval_cont(mood_quality[mood])
    
    overall_quality = get_confidence_interval_cont(overall_quality)
    
    
    # draw figure
    for mood_actual in moods:
        figure = plt.figure(figsize = (10, 5))
        plt.title('Actual Mood: '+ mood_actual.capitalize())
        plt.xlabel('Guessed Mood')
        plt.ylabel('Probability')
        x_value = moods
        y_value = [mood_distributions[mood_pred][mood_actual][0] for mood_pred in moods]
        lower_errs = [mood_distributions[mood_pred][mood_actual][2] for mood_pred in moods]
        upper_errs = [mood_distributions[mood_pred][mood_actual][1] for mood_pred in moods]
        yerr = [lower_errs, upper_errs]
        plt.bar(x_value, y_value, yerr = yerr, figure = figure)
        plt.show()
    
    figure = plt.figure(figsize = (10, 8))
    plt.title('Confusion Matrix')
    plt.xlabel('Actual Mood')
    plt.ylabel('Guessed Mood')
    x_label = [mood.capitalize() for mood in moods]
    y_label = [mood.capitalize() for mood in moods]
    data = []
    index = 0
    for mood_pred in moods:
        data.append([])
        for mood_actual in moods:
            data[index].append(mood_distributions[mood_pred][mood_actual][0])
        index += 1
    ax = figure.add_subplot(111)
    ax.set_yticks(range(len(y_label)))
    ax.set_yticklabels(y_label)
    ax.set_xticks(range(len(x_label)))
    ax.set_xticklabels(x_label)
    im = ax.imshow(data, cmap=plt.cm.gray_r)
    plt.colorbar(im)
    plt.show()
    
    figure = plt.figure(figsize = (10, 5))
    plt.title('Quality Evaluation')
    plt.ylabel('Average Score')
    x_value = [mood.capitalize() for mood in moods] + ['Overall']
    y_value = [mood_quality[mood][0] for mood in moods] + [overall_quality[0]]
    yerr = [mood_quality[mood][1] for mood in moods] + [overall_quality[1]]
    plt.ylim(1, 5)
    plt.bar(x_value, y_value, yerr = yerr, figure = figure)
    plt.show()
    
    figure = plt.figure(figsize = (10, 5))
    plt.title('Quality Evaluation')
    plt.ylabel('Average Score')
    x_value = [excerpt.capitalize() for excerpt in excerpts.keys()] + ['Overall']
    y_value = [excerpt_quality[excerpt][0] for excerpt in excerpts.keys()] + [overall_quality[0]]
    yerr = [excerpt_quality[excerpt][1] for excerpt in excerpts.keys()] + [overall_quality[1]]
    plt.ylim(1, 5)
    plt.bar(x_value, y_value, yerr = yerr, figure = figure)
    plt.show()  
    

if __name__ == '__main__':
    main()
