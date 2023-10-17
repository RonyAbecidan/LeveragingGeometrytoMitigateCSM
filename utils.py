import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
import yaml
from pathlib import Path

MMD=np.loadtxt('Data/MMD.txt',delimiter=',')


def difference(a,b,name1,name2,distance_name):
    a=a.reshape(-1)
    b=b.reshape(-1)
    m=np.median(a-b)
    s=np.std(a-b)
    print(f'For {distance_name} : \n')
          
    print(f"median {name1} : {np.median(a)}")
    print(f"median {name2} : {np.median(b)}")
    print(f"{name1} - {name2} = {m:.5f} +/- {s:.5f}")
    print('-------')

def is_invariant(distance,distance_name):
    '''
    A little code enabling to plot metrics helping to assess invariance to cover stego balance for a specific distance.
    '''
    difference(distance[:,0:1000],distance[:,1000:2000],'full cover','full stego',distance_name)
    difference(distance[:,0:1000],distance[:,2000:3000],'full cover','mix',distance_name)
    difference(distance[:,1000:2000],distance[:,2000:3000],'full stego','mix',distance_name)


def median_plot(distance,regret,distance_name,slide=0.1,gap=0.01,alpha=0.8,fontsize=10):
    min_d=round(distance.min(),2)
    max_d=round(distance.max(),2)
    N=[len(regret[np.logical_and(distance>i-slide,distance<i+slide)]) for i in np.arange(min_d,max_d,gap)]
    L1=[np.quantile(regret[np.logical_and(distance>i-slide,distance<i+slide)],0.25) for i in np.arange(min_d,max_d,gap)]
    L2=[np.median(regret[np.logical_and(distance>i-slide,distance<i+slide)]) for i in np.arange(min_d,max_d,gap)]
    L3=[np.quantile(regret[np.logical_and(distance>i-slide,distance<i+slide)],0.75) for i in np.arange(min_d,max_d,gap)]
    L4=[np.quantile(regret[np.logical_and(distance>i-slide,distance<i+slide)],0.9) for i in np.arange(min_d,max_d,gap)]

    
    plt.fill_between(np.arange(min_d,max_d,gap), L1,L3, color='grey', alpha=0.5)
    plt.plot(np.arange(min_d,max_d,gap),L4,c='black',linestyle='dotted',label='Q(90\%)',alpha=alpha)
    plt.plot(np.arange(min_d,max_d,gap),L3,c='black',linestyle='--',label='Q3',alpha=alpha)
    plt.plot(np.arange(min_d,max_d,gap),L2,label='median',c='black',alpha=alpha)
    plt.plot(np.arange(min_d,max_d,gap),L1,c='black',linestyle='--',label='Q1',alpha=alpha)
    
    #plt.xticks(list(np.arange(min_d-gap,max_d+gap,10*gap)),fontsize=fontsize)
    #plt.yticks(list(np.arange(int(regret.min()),int(regret.max()),5)),fontsize=fontsize)
    plt.grid()

    plt.xlabel(distance_name,fontsize=fontsize)
    plt.ylabel('Regret',fontsize=fontsize)
    plt.legend(fontsize=fontsize//2+5)
    
    return N,np.arange(min_d,max_d,gap)


def unbias_and_describe(l_min,l_max,distance,threshold,csm_study):


    unbias=distance[:,l_min:l_max].copy()
    unbias[MMD[:,0:1000]<=threshold]=100


    print(f"Min : {np.clip(np.quantile(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)],0),0,50)}")
    print(f"Q1 : {np.quantile(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)],0.25):.1f}")
    print(f"Median : {np.quantile(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)],0.5):.1f}")
    print(f"Q3 : {np.quantile(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)],0.75):.1f}")
    print(f"Max : {np.quantile(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)],1):.0f}")
    print(f"% (R>5%) : {(csm_study.regret_matrix[unbias.argmin(axis=0),np.arange(0,1000)]>5).mean()*100}")