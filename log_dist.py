# -*- coding: utf-8 -*-
"""
Created on Fri May 27 09:24:27 2022

@author: User
"""

import numpy as np

def log_distribution(x, p):
    return -p**x/x*(1/(np.log(1-p)))


def logistic(x):
    return 1/(1 + np.exp(-x))

def log_random_index(num_array, risk_aversion):
    num_array.sort()
    indices = list(range(1,len(num_array)))  
    weight = 0.8 + (logistic(1/risk_aversion-1)-0.5)/2.5
    log_dist = log_distribution(np.array(indices), weight)
    p = log_dist +((1-log_dist.sum())/len(indices))
    return np.random.choice(np.array(indices)-1, p = p)

def main():
    from matplotlib import pyplot as plt
    d = list()
    a = np.random.random(10)
    for _ in range(1000):
        d.append(log_random_index(a, risk_aversion = 4))
        
    plt.hist(d, bins = range(1,10,1))    
    
if __name__ == "__main__":
    main()