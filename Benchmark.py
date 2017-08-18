#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Xiao Gan
#
# Created:     13/06/2016
# Copyright:   (c) Xiao Gan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import cProfile
import re
##import numpy as np
##import copy
##import collections
##import functions
import random
##import Reduction
import Booleanops
##import itertools
import MultiQM
import Generating
import time
import Simulation
##import xlwt
import StableMotif


def MultiQM_test(N,k=3,m=4,modex =2,kcutoff=7,samplesize=1,tcut=0.1): # Obsolete
# test simplification of rules of a generated network
    t1 = time.time()
     # switch simulation type: 1=Bool, 2=Multi-level
    t=[]
    totaltime=0
    if modex ==1:
        size = samplesize*2
    if modex ==2:
        size = samplesize
    ##print size
    t1 = time.time()


##    wb = xlwt.Workbook()
##    ws = wb.add_sheet('QM test')

    result1=[] # for recording time into excel
    result2=[]

    for i in range (0,size):
        if i >=samplesize:
            modex=2
        t3=1
        t2=0
    ##    while (t3-t2)>tcut:
        t2 = time.time()
        y=[]
        z=[]
        z1=[]
        x = Generating.generatecomplete(N,k,m,mode=1,kcutoff=kcutoff,m_mode=1)
        for item in x[0]:
            for line in item:
                z1.append(line)
                function = line.split("=",1)[1].strip()
                z.append(function)
    ##        for item in z1:
    ##            print item
        t3 = time.time()
        if  (t3-t2)>tcut:
            print '"""  network passed  """'
            result1.append('network passed')
            result2.append('')
    ##        ws.write(i+1,1,'network passed')
    ##        else:
    ##            print '""""  network generated  """"'
        else:
            print '""""  proceed to tranformation  """"',("--- %s seconds ---" % (t3 - t2))
            result1.append('t3 - t2')
    ##        ws.write(i+1,1, t3 - t2)

            # perform transformation using both QM
            if modex ==1:
            # Bool QM:
                w = Simulation.nodescan(z1,subzero=1)
                for item in w[4]:
            ##        print item
                ##    print type(item)
        ##                print 'raw function:', z[w[4].index(item)]
            ##        print 'sub_zero:', item
                    function1 = Booleanops.transform(item.split("=",1)[1].strip())
            ##        print 'function1 =',function1
            ##        print 'Sub_not =',Simulation.sub_not(function1,w[0],w[1])
                    function2 = Booleanops.transform(Simulation.sub_not(function1,w[0],w[1]))
        ##                print 'function2 =',function2
                    # check if the function has contradictory terms, e.g. 'A1 & A2'
                    function3 = Simulation.exclusioncheck(function2)
        ##                print 'function3 is:',function3

            if modex ==2:
            # perform transformation using both QM
                # multi QM:
                v = Simulation.nodescan(z1,mode=1)
        ##        print 'v=',v
                for func1 in z1:
        ##                print 'raw function=',func1
                    newfunction = MultiQM.qm(func1,v[0],v[1])
        ##                print 'new function=', newfunction
            t4 = (time.time() - t3)
            print '""""  transformation complete  """"',("--- %s seconds ---" % (t4))
            result2.append(t4)
    ##        ws.write(i+1,2,t4)
            totaltime+=t4

    ##    if i == samplesize-1:
    ##        time1 = (time.time() - t1)/samplesize
    ##        t1 =time1
    ##        print 'avg time1=',time1
    ##
    ##    if i == 2*samplesize-1:
    ##        time2 = (time.time() - t1)/samplesize
    ##        print 'avg time2=',time2

    ##print("--- avg time: %s seconds ---" % (totaltime/samplesize))

    ##print("--- avg time: %s seconds ---" % (totaltime/samplesize))
##    for i in range (0,len(result1)):
##        ws.write(i+1,1,result1[i])
##        ws.write(i+1,2,result2[i])
##    wb.save('example.xls')
    print 'Done'
    return


# test example:

def benchmark ():
    ##def randomSM_test(N,k=3,m=4,modex =2,samplesize=1,tcut=0.05):
    N=20
    k=2
    m=3
    modex =2
    kcutoff=5
    samplesize=50
    tcut=0.05

    t1 = time.time()
    t=[]
    totaltime1=0
    totaltime2=0

##    wb = xlwt.Workbook()
##    ws = wb.add_sheet('SMtest')

    result1=[] # for recording time into excel
    result_SM=[]
    result_sim=[]
    Errorlist=[]
    for i in range (0,samplesize):
        print 'sample #',i
        t3=1
        t2=0
    ##    while (t3-t2)>tcut:
        t2 = time.time()
        y=[]
        z=[]
        z1=[]
        x = Generating.generatecomplete(N,k,m,mode=0,kcutoff=kcutoff,m_mode=1)
    ##    print x
        for item in x[0]:
            for line in item:
                z1.append(line)
                function = line.split("=",1)[1].strip()
                z.append(function)
    ##    for item in z1:
    ##        print item
        print z1
        t3 = time.time()
##        if  (t3-t2)>tcut:
##            print '"""  network passed  """'
##            result1.append('network passed')
##            result2.append('')
##        else:
        print '""""  network generated  """"',("--- %s seconds ---" % (t3 - t2))
        result1.append('t3 - t2')
        x = StableMotif.stablemotifsequence(z1)

        t4 = (time.time() - t3)
        print '""""  SM analysis complete  """"',("--- %s seconds ---" % (t4))
        result_SM.append(t4)
        totaltime1+=t4

##        u = Simulation.simulate_attractor(z1,samplesize=100,Tsteps=30,Ttrans=500,Tsearch=1000,istates=[])
##        w = Simulation.show_atr(u)
##        w = []

##        t5 = (time.time() - t4 - t3)
##        print '""""  simulation complete  """"',("--- %s seconds ---" % (t5))
##
##        v = Simulation.compare(w,x,Errorlist,i)
##        print '""""  total time  """"',("--- %s seconds ---" % (t5+t4))
##        result_sim.append(t5)
##        totaltime2+=t5

        print 'avg SM time:',totaltime1/(i+1)
        print 'avg simulation time:',totaltime2/(i+1)
        print
        print 'Errors:', Errorlist

##    for i in range (0,len(result1)):
##        ws.write(i+1,1,result_SM[i])
##        ws.write(i+1,2,result_sim[i])
##    wb.save('example.xls')
    print 'Done'
    print 'avg SM time:',totaltime1/samplesize
    print 'avg simulation time:',totaltime2/samplesize
    ##    return z1
    return
##randomSM_test(N=10,k=3,m=4,modex =2,samplesize=1,tcut=0.05)

benchmark()

test=0
if test==1:
    cProfile.run("benchmark()")
elif test==2:
    benchmark()