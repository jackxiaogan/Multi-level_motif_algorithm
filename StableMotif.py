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


import re
##import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import copy
import functions
##import Booleanops
import itertools
import Reduction
import time
##import Simulation
import MultiQM

def lookup_node(vnode,nodescan):
    # return a node in the representation [nodeindex, nodestate]
    node0 = vnode.split('$')[0].strip()
    state0 = vnode.split('$')[1].strip()
    for nodeindex in range(0,len(nodescan[0])):
        if node0== nodescan[0][nodeindex]:
            newnode=[nodeindex]
            break
    for stateindex in range(0,len(nodescan[1][nodeindex])):
        if state0== nodescan[1][nodeindex][stateindex]:
            newnode.append(stateindex)
            return newnode

def findstablemotif(functionlist,mode=0): # find Stable motifs from network 'functionlist'
    # mode=0: simplified cycles finding; mode=1: original nx cycles finding

    ExpandedG=nx.DiGraph()

    # reduce the network by plugging in inputvalues. Stops when there are no inputnodes. the reduced network is 'reducedlist'
    reducedlist = functionlist
    inputnodes = Reduction.findinput(reducedlist)
    while inputnodes!=[[],[]]:  # reduce the network by plugging in inputvalues. Stops when there are no inputnodes. the reduced network is 'reducedlist'
        reducedlist = Reduction.reduction(reducedlist,inputnodes[0],inputnodes[1])
        # TBD: keep track of the reduced nodes
        inputnodes = Reduction.findinput(reducedlist)
##        print inputnodes
##    for item in reducedlist:
##        print item
##        print inputnodes
    # TBD: if all nodes get reduced
##    print '-------------------------'
##    print
    nodescan = functions.nodescan(reducedlist,mode=0)
##    print 'nodescan:',nodescan

    # creating the expanded network
    for words in reducedlist:   # Inherited from old notation: 'words' means node & function. i.e each line in the network .txt file.
        #skip if the node has already been identified as oscillating
        x = words.split("=",1)[1].strip()
##        print
##        print words
        if x !='@':
            vnode = (words.split("*",1)[0]).strip()
            nodestate = [lookup_node(vnode,nodescan)]
            if vnode not in ExpandedG.nodes():
                ExpandedG.add_node(vnode,info=nodestate,c=0)
##            print 'nodes in the expanded network:'
##            for node in ExpandedG.nodes():
##                print node,ExpandedG.node[node]
            function = MultiQM.qm(words,nodescan[0],nodescan[1])
            # it seems the transformation will solve the issue that 'A and B' and 'B and A' are not be considered to be the same, by unifying 'A and B' and 'B and A'

            if function.isdigit():
                # update reducedlist, and return '-1' as a sign of repeatition
                reducedlist[reducedlist.index(words)]= vnode + '* =' + str(function)
##                reducedlist[reducedlist.index(words)]=node + '* =' + str(function)
##                print 'modified:',reducedlist,functionlist
                return [-1,reducedlist]
            else:
            #find each implicant
                implicantscount= function.count('OR')+1
                implicants = function.split("OR")
                implicants = [ item.strip() for item in implicants]    # strip each item in the list implicants

                for j in range (0,implicantscount):
                    if (implicants[j].find("(")!=(-1)):  # remove parenthesis
                        implicants[j] = re.search('\((.*?)\)',implicants[j]).group(1)
                    inputscount = implicants[j].count('AND')+1
                    inputs = implicants[j].split("AND")
                    implicant = []
                    for item in inputs:
                        # creating expanded network
                        inputinfo = lookup_node(item.strip(),nodescan)
                        implicant.append(inputinfo)
                        #if the node does not already exist, add the node
                        if item.strip() not in ExpandedG.nodes():
                            ExpandedG.add_node(item.strip(), info=[inputinfo],c=0)
##                        print 'implicants: ',implicants[j],implicant
                    implicant = sorted(implicant)
                    if implicants[j] not in ExpandedG.nodes():
                        ExpandedG.add_node(implicants[j], info=implicant,c=0)

                    if inputscount>=2: # adds edges when the implicant is a composite node
                        ExpandedG.node[implicants[j]]['c']=1
                        for item in inputs:
                            ExpandedG.add_edge(item.strip(),implicants[j])
                for item in implicants:
                    ExpandedG.add_edge(item.strip(),vnode)
##    for node in ExpandedG.nodes():
##        print node, ExpandedG.node[node]

    # drawing the graph
##    pos=nx.spring_layout(ExpandedG)
##    nx.draw(ExpandedG, with_labels = True)
##    plt.show()

    # analyze cycles
    v=nodescan
    if mode==0:
        cycles = list(functions.simple_cycles_SM(ExpandedG,lengthlimit=30,timelimit=0, nodelist=[0], nodestates=v[1],Graph=ExpandedG))
    elif mode==1:
        cycles = list(functions.simple_cycles(ExpandedG))
    elif mode==2:
        cycles = list(functions.simple_cycles_SM(ExpandedG,lengthlimit=30,timelimit=0, nodelist=v[0], nodestates=v[1]))
        lengths = [len(i) for i in cycles]
        return [len(ExpandedG.nodes()),len(cycles), (sum(lengths)) / max(len(lengths), 1)]
    elif mode==3:
        return [len(ExpandedG.nodes()),len(list(functions.simple_cycles_SM(ExpandedG,lengthlimit=30,timelimit=0, nodelist=v[0], nodestates=v[1]))),len(list(functions.simple_cycles(ExpandedG)))]

##    print "Cycles in the expanded network:",len(cycles)
##    for item in cycles:
##        print item

    SMcandidates = functions.candidate(cycles,ExpandedG,v)
##    print 'Stable Motifs:',SMcandidates
    # finding oscilations
    SCCs = (nx.strongly_connected_components(ExpandedG))
    # find the largest SCCs in the current network/sub-network
##    print  'SCCs:',list(SCCs)
##    print type(SCCs)
##    for c in SCCs:
##        print sorted(c)
##    print
##    print 'finding oscillations: '
    oscillations= functions.findoscillation(ExpandedG,SMcandidates)
##    print 'oscillations:',oscillations

##    print "SM candidates in the expanded network:"
##    for item in SMcandidates:
##        print item
##
##    # to apply reduction, needs first to get all stablized value from a stable motif
##    for item in SMcandidates:
##        inputnodes = functions.findstablenodes(item)  # find nodes and their states in a stable motif
##        Flag1=1
    if SMcandidates == []:
        return ['None',oscillations]  # return a string 'None', if no SM is found
    else:
        return [SMcandidates,oscillations]

# test example
test=0
if test ==1:
##    y = Reduction.to_list('toy_example3.txt')
    y = Reduction.to_list('Senescence_Onset_G1_S.txt')
##    y=['N0$0* =(N1$0 AND N2$1) OR (N1$1 AND N2$1)', 'N0$1* =(N1$0 AND N2$0) OR (N1$1 AND N2$0)', 'N1$0* =(N5$0 AND N3$0) OR (N5$1 AND N3$0)', 'N1$1* =(N5$0 AND N3$1) OR (N5$1 AND N3$1)', 'N2$0* =(N3$0 AND N7$0) OR (N3$0 AND N7$1)', 'N2$1* =(N3$1 AND N7$0) OR (N3$1 AND N7$1)', 'N3$0* =(N5$0 AND N0$0) OR (N5$0 AND N0$1) OR (N5$1 AND N0$1)', 'N3$1* =(N5$1 AND N0$0)', 'N4$0* =(N6$0 AND N7$0) OR (N6$1 AND N7$0)', 'N4$1* =(N6$0 AND N7$1) OR (N6$1 AND N7$1)', 'N5$0* =(N4$0 AND N2$1) OR (N4$1 AND N2$0) OR (N4$1 AND N2$1)', 'N5$1* =(N4$0 AND N2$0)', 'N6$0* =(N7$1 AND N0$0)', 'N6$1* =(N7$0 AND N0$0) OR (N7$0 AND N0$1) OR (N7$1 AND N0$1)', 'N7$0* =(N1$0 AND N4$1) OR (N1$1 AND N4$1)', 'N7$1* =(N1$0 AND N4$0) OR (N1$1 AND N4$0)']
##    y = ['N0$0* =(N4$0 AND N1$0) OR (N4$1 AND N1$1)', 'N0$1* =(N4$0 AND N1$1)', 'N0$2* =(N4$0 AND N1$2) OR (N4$1 AND N1$0) OR (N4$1 AND N1$2)', 'N1$0* =(N0$0 AND N2$0) OR (N0$1 AND N2$0) OR (N0$2 AND N2$0)', 'N1$1* =(N0$0 AND N2$1)', 'N1$2* =(N0$1 AND N2$1) OR (N0$2 AND N2$1)', 'N2$0* =(N6$0 AND N5$0) OR (N6$0 AND N5$2) OR (N6$1 AND N5$0) OR (N6$1 AND N5$1) OR (N6$1 AND N5$2)', 'N2$1* =(N6$0 AND N5$1)', 'N3$0* =(N7$0 AND N2$0) OR (N7$0 AND N2$1) OR (N7$2 AND N2$1)', 'N3$1* =(N7$1 AND N2$1) OR (N7$2 AND N2$0)', 'N3$2* =(N7$1 AND N2$0)', 'N4$0* =(N7$0 AND N2$1) OR (N7$1 AND N2$0) OR (N7$1 AND N2$1)', 'N4$1* =(N7$0 AND N2$0) OR (N7$2 AND N2$0) OR (N7$2 AND N2$1)', 'N5$0* =(N1$0 AND N0$1) OR (N1$2 AND N0$1)', 'N5$1* =(N1$0 AND N0$0) OR (N1$0 AND N0$2) OR (N1$1 AND N0$0) OR (N1$1 AND N0$1) OR (N1$1 AND N0$2)', 'N5$2* =(N1$2 AND N0$0) OR (N1$2 AND N0$2)', 'N6$0* =(N0$0 AND N2$0) OR (N0$0 AND N2$1) OR (N0$2 AND N2$0)', 'N6$1* =(N0$1 AND N2$0) OR (N0$1 AND N2$1) OR (N0$2 AND N2$1)', 'N7$0* =(N3$0 AND N6$0) OR (N3$0 AND N6$1)', 'N7$1* =(N3$1 AND N6$1) OR (N3$2 AND N6$1)', 'N7$2* =(N3$1 AND N6$0) OR (N3$2 AND N6$0)']

    start_time = time.time()
    x = findstablemotif(y,0)

    if x[0]!= -1:
        print "SMs in the expanded network:"
        print x[0]
        print "Oscillation candidates in the expanded network:"
        print x[1]

    ##stablenodes = functions.findstablenodes(x[1])
    ##z = Reduction.inputsub(y,stablenodes)
    ##print z
    ##
    ##w = findstablemotif(z)
    ##print w
    print("--- %s seconds ---" % (time.time() - start_time))
##
##    start_time = time.time()
##
##    x = findstablemotif(y,1)
##
##    print "SM candidates in the expanded network:"
##    print x[0]
##    print "Oscillation candidates in the expanded network:"
##    print x[1]
##    print("--- %s seconds ---" % (time.time() - start_time))


def showattractor(functionlist, SMsequence):
    # returns a (class of) attractor as a list of functions, determined by a sequence of Stable motifs.
    # TBD display oscillations
    # TBD display oscillation downstreams: keep only possible states
    reducedlist = functionlist
    for sm in SMsequence:
##        print sm
        stablenodes = functions.findstablenodes(sm)
        reducedlist = Reduction.inputsub(reducedlist,stablenodes)

        inputnodes = Reduction.findinput(reducedlist)
        Flag=0
        while Flag == 0 :
            reducedlist = Reduction.reduction(reducedlist,inputnodes[0],inputnodes[1],mode=1)
            inputnodes1 = Reduction.findinput(reducedlist)
            if inputnodes == inputnodes1:
                Flag =1
            else:
                inputnodes = inputnodes1

##    print reducedlist
    # show the attractor in a more proper form
    nodelist =[]
    statelist =[]
    oscnodelist =[]
    oscstatelist =[]
    for words in reducedlist:
##        print words       # monitoring the attractor
        vnode = words.split("*",1)[0].strip()
        node = vnode.split("$",1)[0].strip()
        state = vnode.split("$",1)[1].strip()
##        print node
##        print state
        function = words.split("=",1)[1].strip()   #removes spaces and '/n'  at the end of each line
##        print function
        if function == 'True':
##            print function
            function = '1'
        elif function == 'False':
            function = '0'

        elif function == '1':
            if node not in nodelist:
                nodelist.append(node)
                statelist.append(state)
##                print nodelist
##                print statelist
            else:
                if state != statelist[nodelist.index(node)]:
                    print 'Error1!',',',node, ',',state,',',statelist[nodelist.index(node)]
                    return
        elif function == '0':
            if (node in nodelist) and (state == statelist[nodelist.index(node)]):
                    print 'Error2!'
                    return
        elif function == '@':
        #displaying oscillations
##            print 'oscillation',node
##            print oscnodelist
##            for item in oscnodelist:
##                print type(item)
            if node not in oscnodelist:
                nodelist.append(node)
                statelist.append(str(state))
##                print node,state,oscnodelist
            else:
##                print 'found osc'
##                print node,oscnodelist
##                print oscnodelist.index(node)
##                print node,state,oscnodelist,oscstatelist
                statelist[nodelist.index(node)] += 'or' + str(state)
##            print 'oscnodes:',oscnodelist
##            print
        elif not function.isdigit():
        # refine the reducedlist, by determining more nodes.
        # check if all sibling nodes has their states identified. If so, Flag2=0
        # e.g. 'N2$0* =N7$0', 'N2$1* =0' => 'N2$0* =1', 'N2$1* =0'

            Flag2=0
            for words2 in reducedlist:
                vnode2 = words2.split("*",1)[0].strip()
                node2 = vnode2.split("$",1)[0].strip()
                state2 = vnode2.split("$",1)[1].strip()
                function2 = words2.split("=",1)[1].strip()
                if node ==node2 and state != state2:
                    if function2==0:
                        Flag2 +=0
                    elif function2==1:
                        Flag2 +=1

            if Flag2 ==0 :
                nodelist.append(node)
                statelist.append(str(state))

        else:
            print 'Error in function:',node,function
            return

    attractor = []
##    print nodelist,statelist
    for sm in SMsequence:
        for vnode in sm:
            node = vnode.split("$",1)[0].strip()
            state = vnode.split("$",1)[1].strip()
            if node not in nodelist:
                nodelist.append(node)
                statelist.append(state)
##            elif state != statelist[nodelist.index(node)]:
##                print 'Error in attractor states: contradiction. node {}, state {}'.format(node,state)

    for i in range (0, len(nodelist)):
        result = str(nodelist[i]) +'='+ str(statelist[i])
        attractor.append(result)
##        print result
    # TBD: showing downstream of attractor
    return attractor

# test example:
##y = Reduction.to_list('toy_example5.txt')
##y = ['A$0* = B$0 OR (C$1 AND B$1)', 'A$1* = B$1 AND C$0', 'A$2* = B$2', 'B$0* = C$0 OR A$0', 'B$1* = C$1 AND A$1', 'B$2* = C$1 AND A$2', 'C$0* = A$0', 'C$1* = A$1 OR A$2']
##x = showattractor(y, [['B$1', 'A$1'], ['C$1', 'D$1']])
##x= showattractor(['N2$0* = @', 'N2$1* = @', 'N3$0* = @', 'N3$1* = @', 'N4$1* =1'], [['N0$0', 'N1$0'], ['N2$0', 'N2$1', 'N3$0', 'N3$1']])
##x = showattractor(['N0$0* =@', 'N0$1* =@', 'N1$0* =@', 'N1$1* =@', 'N2$0* =@', 'N2$1* =@', 'N3$0* =@', 'N3$1* =@', 'N4$0* =@', 'N4$1* =@', 'N4$2* =@', 'N7$1* =1', 'N8$0* =@', 'N8$1* =@', 'N9$0* =@', 'N9$1* =@'], [['N8$0 AND N9$0', 'N4$2', 'N1$0', 'N8$0', 'N9$0', 'N8$1 AND N9$0', 'N4$0', 'N1$1', 'N1$1 AND N0$1', 'N8$1', 'N1$1 AND N8$1', 'N9$1', 'N8$1 AND N9$1', 'N3$1', 'N0$1', 'N6$0 AND N0$1', 'N2$1', 'N9$0 AND N2$0', 'N3$0', 'N0$0', 'N2$0', 'N8$0 AND N9$1', 'N4$1', 'N4$1 AND N5$1']])
##print x



# find stablemotif iteratively

def stablemotifsequence(functionlist):
    # input: a list of functions (strings)
    # Output: a list of all stable motif sequences, plus the corresponding attractor
    sequence = []
    attractors =[]
    stack=[]
    usedSMseq=[]
    # '1st order' SM
##    print '1'
    x = (findstablemotif(functionlist))
##    print x
    # (To be checked) if everyone stablizes: ####################
    if x==['None', []]:
        sm=[]
        for words in functionlist:
##            print words
            vnode = words.split("*",1)[0].strip()
            function = words.split("=",1)[1].strip()
##            print function
            if function =='1':
                sm.append(vnode)
##            print sm
        attractor = showattractor(functionlist,[sm])
        return [[[sm],attractor]]

    while x[0] == -1:
        reducedlist = x[1]
        x =findstablemotif(reducedlist)
##    print x
##    print
    if x[0] != 'None':
        for item in x[0]:
            item.sort()
        for sm in x[0]:
            stack.append([functionlist,[sm]])
            # each 'object' in the stack is a list with 1st item being the current network, 2nd item being the list of SMs found in the previous reduction process and the current level SMs

    if x[1] !=[]:
##        print x[1]
        for item in x[1]:
##            print item
            list(item).sort()
        for osc in x[1]:
            stack.append([functionlist,[osc]])

    while stack != []:
        obj = stack.pop(0)
##        print '-----'
##        print 'object =',obj
        # analyze the first [network,[sm]] pair in stack
        stablenodes = functions.findstablenodes(obj[1][len(obj[1])-1]) # access the last stable motif/oscillation in the sm sequence record
##        print 'stablenodes =', stablenodes
        # Note: The result will include all virtual nodes of the same original node (written in the function 'inputsub'). e.g if the stable motif contains A$1, then A$0, A$2, etc.will all gets 0
        reducedlist = Reduction.inputsub(obj[0],stablenodes)
##        print 'reducedlist=',reducedlist
        result =findstablemotif(reducedlist)
        while result[0] == -1:
            reducedlist = result[1]
            result =findstablemotif(reducedlist)
##            print result,reducedlist
        x1 = result[0] # stable motif list
        x2 = result[1] # oscillation list
##        print 'stablemotifs=',x1,x2
##        print
        if x1 != 'None':
            for item in x1:
                item.sort()
            for sm1 in x1:
                SMsequence = copy.copy(obj[1])
##                print obj
                SMsequence.append(sm1)
##                SMsequence.sort()  # ***** seems wrong ****
##                print 'SMsequence=',SMsequence[len(SMsequence)-1]
                # TBD: #####  uncertain!!  #######     filter repeated SM sequence
##                Flag=0
##                for i in range(0,len(attractors)):
##                    y1 = copy.copy(attractors[i][0])
##                    y1.sort()
##                    y2 = copy.copy(SMsequence)
##                    y2.sort()
####                    print 'y1=',y1,'y2=',y2
##                    if y1 == y2:
####                        print 'same sequence identified'
##                        Flag=1
##                        break
####                        print '{} added'.format(SMsequence)
##                if Flag==0:
                if SMsequence not in usedSMseq:
##                    print 'SMsequence',SMsequence
                    stack.append([reducedlist,SMsequence])
                    usedSMseq.append(SMsequence)
##                print

        if x2!=[]:  # TBD (Not sure if correct)
        # !!!!! TBD: mark the downstream of oscillation

        # subs in oscillation
            for item in x2:
                item.sort()
            for osc in x2:
                SMsequence = copy.copy(obj[1])
                SMsequence.append(osc)
##                print [reducedlist,SMsequence]
                if SMsequence not in usedSMseq:
                    stack.append([reducedlist,SMsequence])
##                    print 'SMsequence',SMsequence
                    usedSMseq.append(SMsequence)


        elif x1 == 'None':
            # reached the end of SMsequence identification
##            print 'found attractor SM sequence',obj[1]
##            print reducedlist

            # finding exact state of the attractor
            if obj[1] not in sequence:
                sequence.append(obj[1])
##                print 'reducedlist=',(reducedlist, obj[1])
##                print

                attractor = showattractor(functionlist, obj[1])
                # obj[1] is the SM sequence needed to reach the attractor. obj[1] is a list of expanded nodes (strings)
                # return SMsequence-attractor pairs.

                # #####   Uncertain!  ####  filter same SMsequence
                Flag=0
                for i in range(0,len(attractors)):
                    y1 = copy.copy(attractors[i][0])
                    y1.sort()
                    y2 = copy.copy(obj[1])
                    y2.sort()
##                    print 'y1=',y1,'y2=',y2
                    if y1 == y2:
##                        print 'same sequence identified'
                        Flag=1
                        break
##                        print '{} added'.format(SMsequence)
                if Flag==0:
                    attractors.append([obj[1],attractor])
##                print 'attractors=',attractors
##        print 'next stack =', stack
##        print '-------------------------'
##        print

    return attractors

# test
test = 0
if test ==1:
##    y = Reduction.to_list('toy_example2.txt')
##    y = Reduction.to_list('SOmodel.txt')
##    y = Reduction.to_list('MCP_budding_yeast_CC.txt')
##    y = Reduction.to_list('primary_sex_determination_1.txt')
##    y = Reduction.to_list('Senescence_Onset_G1_S.txt')
    y = Reduction.to_list('ap_boundary.txt')
##    y = Reduction.to_list('MultiLevel_MamCC.txt')
##    y = ['N0$0* =(N4$0 AND N1$0) OR (N4$1 AND N1$1)', 'N0$1* =(N4$0 AND N1$1)', 'N0$2* =(N4$0 AND N1$2) OR (N4$1 AND N1$0) OR (N4$1 AND N1$2)', 'N1$0* =(N0$0 AND N2$0) OR (N0$1 AND N2$0) OR (N0$2 AND N2$0)', 'N1$1* =(N0$0 AND N2$1)', 'N1$2* =(N0$1 AND N2$1) OR (N0$2 AND N2$1)', 'N2$0* =(N6$0 AND N5$0) OR (N6$0 AND N5$2) OR (N6$1 AND N5$0) OR (N6$1 AND N5$1) OR (N6$1 AND N5$2)', 'N2$1* =(N6$0 AND N5$1)', 'N3$0* =(N7$0 AND N2$0) OR (N7$0 AND N2$1) OR (N7$2 AND N2$1)', 'N3$1* =(N7$1 AND N2$1) OR (N7$2 AND N2$0)', 'N3$2* =(N7$1 AND N2$0)', 'N4$0* =(N7$0 AND N2$1) OR (N7$1 AND N2$0) OR (N7$1 AND N2$1)', 'N4$1* =(N7$0 AND N2$0) OR (N7$2 AND N2$0) OR (N7$2 AND N2$1)', 'N5$0* =(N1$0 AND N0$1) OR (N1$2 AND N0$1)', 'N5$1* =(N1$0 AND N0$0) OR (N1$0 AND N0$2) OR (N1$1 AND N0$0) OR (N1$1 AND N0$1) OR (N1$1 AND N0$2)', 'N5$2* =(N1$2 AND N0$0) OR (N1$2 AND N0$2)', 'N6$0* =(N0$0 AND N2$0) OR (N0$0 AND N2$1) OR (N0$2 AND N2$0)', 'N6$1* =(N0$1 AND N2$0) OR (N0$1 AND N2$1) OR (N0$2 AND N2$1)', 'N7$0* =(N3$0 AND N6$0) OR (N3$0 AND N6$1)', 'N7$1* =(N3$1 AND N6$1) OR (N3$2 AND N6$1)', 'N7$2* =(N3$1 AND N6$0) OR (N3$2 AND N6$0)']

    start_time = time.time()
    ##print y
    ##print
    ##y = ['A$0* = B$0 OR (C$1 AND B$1)', 'A$1* = B$1 AND C$0', 'A$2* = B$2', 'B$0* = C$0 OR A$0', 'B$1* = C$1 AND A$1', 'B$2* = C$1 AND A$2', 'C$0* = A$0', 'C$1* = A$1 OR A$2']

    ##y =['A$0* = C$0', 'A$1* = C$1', 'B$0* = B$1', 'B$1* = B$0', 'C$0* = A$0 OR B$0', 'C$1* = A$1 AND B$1'] # toy example
    ##y =['E$0* = 1','E$1* = 0','A$0* = C$0 AND E$0', 'A$1* = C$1', 'B$0* = B$1', 'B$1* = B$0', 'C$0* = A$0 OR B$0', 'C$1* = A$1 AND B$1'] # toy example

    ##x = findstablemotif(y)
    ##print x

    x = stablemotifsequence(y)
##    print x
    for item in x:
        print item
##        print len(item[1])
##    print x[1]
##    for sm in x[1]:
##        stablenodes = functions.findstablenodes(sm)
##        print stablenodes
    print("--- %s seconds ---" % (time.time() - start_time))
