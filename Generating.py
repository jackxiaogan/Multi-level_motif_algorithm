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


##import numpy as np
import numpy
import networkx as nx
##import matplotlib.pyplot as plt
##import functions
##import Booleanops
import itertools
##import Reduction
import random
import time
##import Simulation


##qm = QuineMcCluskey()
##ones = [0,3]
##dontcares = []
##rst = qm.simplify(ones,dontcares)
##print rst
##print list(a)[0]


# generating a network
def generatenetwork(N,k,mode=0,kcutoff=0,m_mode=0, m_dist=3):
    # generate a network of N nodes with k edges
    # mode=0: constant k; mode=1: in-degrees following a power law distribution with exponent k
    # m_mode:
    # output: a list of 3 items:
    #       I0. a list of nodenames (string).
    #       I1: a sub-list of inputs for eachnode. Each item in this sub-list is a node name (string)
    #       I2: graph G of the network, in networkx format
    nodes = []
    nodeinputs = [] # ith item is the inputnodes towards node i
    G=nx.DiGraph()
    nodestates =[]
##    print nodestates
    if mode ==0:
        for i in range(0,N):
            nodename = 'N' + str(i)
            nodes.append(nodename)
        G.add_nodes_from(nodes)

        # generate edges: k inputs for each node
        for i in range(0,N):
            nodeinput = []
            # randomly select k different nodes from all nodes except node i
            A = range(0,N)
            del A[i]
            B = random.sample(A,k)
            for j in B:
                nodeinput.append(nodes[j])
                G.add_edge(nodes[j],nodes[i])
            nodeinputs.append(nodeinput)

    if mode==1:
        z1=nx.utils.create_degree_sequence(N,nx.utils.powerlaw_sequence,exponent=k)
        if kcutoff>0:
            for index in range (0,len(z1)):
                if z1[index]>kcutoff:
                    z1[index]=kcutoff
        # outdegree dist, s.t. the sum of degrees are the same as z1
        z2=[]
##        print z1, sum(z1)
        while sum(z1)!=sum (z2):
##            print sum(z2)
            z2=nx.utils.create_degree_sequence(N,nx.utils.powerlaw_sequence,exponent=k)
            if kcutoff>0:
                for index in range (0,len(z2)):
                    if z2[index]>kcutoff:
                        z2[index]=kcutoff

##        print z2

        G1=nx.directed_configuration_model(z1,z2,create_using=nx.DiGraph())
        def mapping(x):
            return 'N'+str(x)
        G=nx.relabel_nodes(G1,mapping)
        nodes= list(G.nodes())
        for node in nodes:
            nodeinputs.append(G.predecessors(node))
    if m_mode==1:
        # TBD: generate distribution
        for node in nodes:
##            max1 = 2
            max1 = numpy.random.choice(numpy.arange(2, 4), p=[0.5, 0.5])
##            max1 = numpy.random.choice(numpy.arange(2, 5), p=[0.34, 0.33,0.33])
##            max1 = numpy.random.choice(numpy.arange(2, 6), p=[0.6, 0.25,0.1,0.05])
##            max1 = numpy.random.choice(numpy.arange(2, 7), p=[0.55, 0.25, 0.1, 0.05, 0.05])
##            max1 = numpy.random.choice(numpy.arange(2, 8), p=[0.5, 0.25, 0.125, 0.0625, 0.03125, 0.03125])
            states=[]
            for i in range(0, max1):
                states.append(i)
            nodestates.append(states)

        # check all nodes to make sure # nodestates < total input minterms. If not, cutoff higher states in target node
        Flag=1
        while Flag == 1:
            Flag=0
            for node in nodes:
                inputcombi = 1
                for input in nodeinputs[nodes.index(node)]:
##                    print input
                    inputcombi *= len (nodestates[nodes.index(input)])
                if len (nodestates[nodes.index(node)]) > inputcombi:
##                    print 'exceeding',node
                    nodestates[nodes.index(node)] = range(0,inputcombi)
                    Flag =1

    return [nodes, nodeinputs, G, nodestates]

# test example: generatenetwork
# takes several seconds to draw a network of N=1000, k=3; generation is done immediately

##t1= time.time()
##for i in range(0,1):
##    x = generatenetwork(50,k=2.5,mode=1,kcutoff=7,m_mode=1, m_dist=3)
####print x
##
##print("--- %s seconds ---" % (time.time() - t1))
##G= x[2]

##pos=nx.spring_layout(G)
##nx.draw(G, with_labels = True)
##plt.show()

def generatefunc(target, inputnodes, m, mlist=[],m_mode=0, m_dist=3):
    # Randomly generate a semi-Boolean function for 'target' (string) node. 'inputnodes' is a list of strings of inputnode names. 'm' is the max nulti-level of each node (a unviersal constant, not node-sepcific).

    # input: target: string; inputnodes: a list of strings; m: # of state for the target node; mlist: a list of all states of all input nodes; m_mode=0: constant m for all nodes; m_mode=1: power law distribution for m, with exponent m_dist
    # Output: string
    if m_mode==0:
        lst = list(itertools.product(range(0, m, 1), repeat=len(inputnodes)))
    elif m_mode==1:
        lst = list(itertools.product(*mlist))
    else:
        print 'Error in generatefunc: m_mode out of range'
    #creating state nodes
    state=[]
    for i in range (0,len(lst)):
        state.append([])
        for j in range (0,len(inputnodes)):
            state[i].append('0')
    phrase = ['']*len(lst)

    for i in range (0,len(lst)):
        for j in range (0,len(inputnodes)):
            state[i][j] = inputnodes[j] + '$' + str(lst[i][j])
            phrase[i] += state[i][j]
            phrase[i] += ' AND '
        phrase[i] = phrase[i][0:(len(phrase[i])-5)].strip()
##    print phrase

    # plug it into target node
    Flag=0
    while Flag == 0: # Flag: check to make sure that the function is appropriate: i.e. each states gets at least one 'phrase';
        function = ['']*m
        Flag = 1
        for i in range(0,len(phrase)):
            # randomly assign the phrase to a value in (0,m)
            function[random.choice(range(0, m, 1))] += '('+ phrase[i] +')' + ' OR '
        for i in range(0,len(function)):
            if function[i] =='':  # if a state gets no 'phrase', re-generate the fucntions for all states
                Flag =0
            else:
                function[i] = function[i][0:(len(function[i])-4)].strip()
##    print function

    # TBD: check if both input are active/meaningful in the function. Q: is this neccesary?

    # node names
    node=[]
    nodefunction = []
    for i in range(0,m):
        nodename = target + '$' + str(i)
        node.append(nodename)
        func = nodename + '* =' + function[i]
        nodefunction.append(func)

    return nodefunction

# test example: single generatefunc
##t1=time.time()
##N=5
##size =1
##m=3
##lstA=[]
##mlist = [[0,1],[0,1,2,3],[0,1,2],[0,1],[0,1]]
##for i in range (0,N):
##    lstA.append('A'+str(i))
##
##print lstA
##
##for j in range(0,size):
##    x = generatefunc('D', lstA, m, mlist, m_mode=1,m_dist=3)
##
##for item in x:
##    print item
##print("--- %s seconds ---" % ((time.time() - t1)/size))



def generatecomplete(N,k,m, mode=0,kcutoff=0,m_mode=0,m_dist=3):
    # generate a complete network, with node functions.
    # mode=0: constant k; mode1: degrees following a power law distribution with exponent k
    # m_mode=0: fixed m (# states) for each node; m_mode=1: m has a distribution 'm_dis'
    # Inputs: N: # of nodes (int); k: node in-degree (int); m: max node level (int, universal)
    # output: a list: L0: node fuctions as a list of strings; L1: network graph file in networkx format

    nodefunctions=[]
    network = generatenetwork(N,k,mode,kcutoff,m_mode=m_mode,m_dist=m_dist)
##    print network
    for i in range(0, len(network[0])):
        if m_mode==1:
            # m1 = # states of target; mlist = # states of inputs
            m1 = len (network[3][i])
            mlist=[]
            for input in network[1][i]:
                mlist.append(network[3][network[0].index(input)])
        else:
            m1=m
            mlist=[]
        nodefunc = generatefunc(network[0][i], network[1][i], m1, mlist, m_mode, m_dist)
##        print nodefunc
        nodefunctions.append(nodefunc)

    return [nodefunctions,network[2]]

# test example for generatecomplete(N,k,m)
##t1=time.time()
##size=10
##N=50
##for i in range(0,size):
##    x = generatecomplete(N,k=3,m=4,mode=1,kcutoff=7,m_mode=1)
####    print 'network generated'
##
##
##print("--- %s seconds ---" % ((time.time() - t1)/size))
##G=x[1]
##pos=nx.spring_layout(G)
##nx.draw(G, with_labels = True)
##plt.show()


# #############   test   ##########

# test simplification of rules of a generated network
##t1 = time.time()
##t=[]
##k=2
##N=10
##m=3
##for n in range (N,N+1):
##    y=[]
##    z=[]
##    z1=[]
##    x = generatecomplete(n,k,m)
##    for item in x[0]:
##        for line in item:
##            z1.append(line)
##            function = line.split("=",1)[1].strip()
##            z.append(function)
##    for item in z1:
##        print item
##
##    # perform transformation using both QM
##    # Bool QM:
##
##
##
####    ##z = ['(N3$2 AND N1$1)']
####    ##print("--- %s seconds ---" % (time.time() - start_time))
##    w = Simulation.nodescan(z1,subzero=1)
##    for item in w[4]:
####        print item
##    ##    print type(item)
##        print 'raw function:', z[w[4].index(item)]
####        print 'sub_zero:', item
##        function1 = Booleanops.transform(item.split("=",1)[1].strip())
####        print 'function1 =',function1
####        print 'Sub_not =',Simulation.sub_not(function1,w[0],w[1])
##        function2 = Booleanops.transform(Simulation.sub_not(function1,w[0],w[1]))
####        print 'function2 =',function2
##        # check if the function has contradictory terms, e.g. 'A1 & A2'
##        function3 = Simulation.exclusioncheck(function2)
##        print 'function3 is:',function3
##    print("--- %s seconds ---" % (time.time() - t1))
##        y1 = item.split("=",1)[0] + '= ' + function3
##        y.append(y1)
##
####        print 'simplifyies to: '
####        print y
##    ##    print
####    for item in y:
####        print item
####    print
##
####    print'y2=', y2
##

##    t.append(time.time() - t1)
##    t1 = time.time()

##for i in range(0,len(w[4])):
##    print 'original function=', z[i]
##    print w[4][i]
##    print y[i]

##Flag=0
##for i in range(0,len(z)):
##    print z[i]
##    print y[i]
##    x1 = Booleanops.convert(z[i],mode=1,outputnode=1) # x[0] is the string of function, with variables represented by A[i]; x[1] is the list A[i] with each item being the node A[i] represents
####    print x
##    ones1=Booleanops.enum_ones(x1[0],len(x1[1]))
##    x2 = Booleanops.convert(y[i],mode=1,outputnode=1)
##    ones2=Booleanops.enum_ones(x2[0],len(x2[1]))
##    if ones1==ones2:
##        print 'same'
##    else:
##        print 'simplified'
##        print 'x1=',x1
##        print 'ones1 =',ones1
##        print
##        print 'x2=',x2
##        print 'ones2 =', ones2
##        Flag=1
##
##if Flag==1:
##    print '-------- simplified found! --------'