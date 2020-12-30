#!/usr/bin/env python
# coding: utf-8

from numpy import *
from scipy import *
from scipy.signal import decimate
import scipy.io.wavfile
import warnings
import sys
import os

warnings.filterwarnings("ignore")

def check(file, expected):
    if file[4] == str(expected):
        return 1
    return 0

def predict(file):

    rate, signal = scipy.io.wavfile.read(file)
    if len(shape(signal))==2:
        signal = [x[0] for x in signal]
    elif len(shape(signal))==1:
        signal = signal
    else:
        raise Exception("Niewłaściwy format danych")

    times = min(len(signal)/rate, 3) #ile razy funkcja hps jest wykonywana
    part_lenght=int(rate)
    parts = [signal[i*part_lenght:(i+1)*part_lenght] for i in range(int(times))]
    
    spectrum_list = []
    for signal in parts:
        window = hamming(len(signal)) #funkcja okna 
        signal = multiply(signal,window)
        spectrum_list.append(abs(fft(signal)))
    
    m=0
    k=0
    resultParts = []
    for spectrum in spectrum_list:
        hps = copy(spectrum)
        for i in range(2, 5): 
            dec = decimate(spectrum, i) 
            hps[:len(dec)] *= dec
        time = int(len(signal) / rate) #w sekundach
        freq_result = argmax(hps[60:])
        result = (60 + freq_result) / time

        if result < 172.5 and result > 60:
            m+=1
        elif result > 172.5:
            k+=1
            
    #print("K:",k,"M:",m)
    if k>m:
        return "K"
    else:
        return "M"

def check_all():
    files = os.listdir('train')

    M_true = 0
    K_true = 0
    M_false = 0
    K_false = 0
    suma = 0
    for file in files:
        predicted = predict('train/'+file)
        print(file, predicted, check(file,predicted))
        suma += check(file,predicted)
        if (check(file,predicted) and predicted == "M"):
            M_true+=1
        elif (check(file,predicted) and predicted == "K"):
            K_true+=1
        elif (check(file,predicted) == 0 and predicted == "K"):
            K_false +=1
        elif check(file,predicted) == 0 and predicted == "M":
            M_false+=1
    print(suma/len(files))
    print("KOBIETY POPRAWNIE: ", K_true)
    print("KOBIETY NIEPOPRAWNIE: ",K_false)
    print("MĘŻCZYŹNI POPRAWNIE: ", M_true)
    print("MĘŻCZYŹNI NIEPOPRAWNIE: ",M_false)


if __name__ == '__main__':
    if len(sys.argv)==2:
        print(predict(sys.argv[1]))
    elif len(sys.argv)==1:
        check_all()
    else:
        raise Exception("Niepoprawna ilość argumentów")
