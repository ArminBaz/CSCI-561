import pickle
import gzip
import numpy as np

def load_data():
    f = gzip.open('mnist.pkl.gz', 'rb')
    training_data, validation_data, test_data = pickle.load(f, encoding="latin1")
    f.close()
    return (training_data, validation_data, test_data)
def load_data_wrapper():
    tr_d, va_d, te_d = load_data()
    training_inputs = [np.reshape(x, (784, 1)) for x in tr_d[0]]
    training_results = [vectorized_result(y) for y in tr_d[1]]
    training_data = zip(training_inputs, training_results)
    validation_inputs = [np.reshape(x, (784, 1)) for x in va_d[0]]
    validation_data = zip(validation_inputs, va_d[1])
    test_inputs = [np.reshape(x, (784, 1)) for x in te_d[0]]
    test_data = zip(test_inputs, te_d[1])
    return (training_data, validation_data, test_data)

def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

training_data, validation_data, test_data=load_data()
training_img=np.int32(training_data[0]*256)
training_label=np.int32(training_data[1])
validation_img = np.int32(validation_data[0]*256)
validation_label=np.int32(validation_data[1])
test_img=np.int32(test_data[0]*256)
test_label=np.int32(test_data[1])

tr_img = np.concatenate((training_img,validation_img))
tr_label = np.concatenate((training_label,validation_label))

tr_label=np.reshape(tr_label,(60000,1))
test_label=np.reshape(test_label,(10000,1))

np.savetxt('train_label.csv',tr_label,delimiter=',', fmt='%d')
np.savetxt('test_label.csv',test_label,delimiter=',', fmt='%d')
np.savetxt('train_image.csv',tr_img,delimiter=',', fmt='%d')
np.savetxt('test_image.csv',test_img,delimiter=',', fmt='%d')

