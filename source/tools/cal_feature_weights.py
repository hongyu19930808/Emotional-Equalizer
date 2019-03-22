import torch
import numpy
import pylab

fin = open('instruments_info_all.csv', 'r')
metas = fin.readline().strip().split(',')
metas = [meta.strip() for meta in metas]
all_instruments = []

x = numpy.zeros([128, 18]) # 17 features + 1 constant
r = numpy.zeros([128, 8]) # 8 moods
x_label = metas[1:18] # 17 features
r_label = metas[20:28] # 8 moods
row_index = 0

while True:
    line = fin.readline().strip()
    if line == None or len(line) == 0:
        break
    elements = line.split(',')
    elements = [float(element) for element in elements]
    x[row_index, :-1] = elements[1:18]
    r[row_index, :] = elements[20:28]
    row_index += 1

fin.close()

"""
# linear regression
x[:, -1] = 1
x = numpy.matrix(x)
r = numpy.matrix(r)
w = numpy.linalg.inv(numpy.transpose(x) * x) * numpy.transpose(x) * r

for i in xrange(18):
    for j in xrange(8):
        print round(float(w[i, j]), 3), '\t',
    print ''
"""

# correlation
for i in xrange(17):
    x_value = x[:, i]
    for j in xrange(8):
        y_value = r[:, j]
        print x_label[i], r_label[j]
        pylab.scatter(x_value, y_value)
        pylab.show()
        pass