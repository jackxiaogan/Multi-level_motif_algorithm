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


##import re
##import numpy as np
import networkx as nx
##import matplotlib.pyplot as plt
import copy
import functions
##import Booleanops
##import StableMotif
##import itertools
import random
import time


def evalfunc(function, fullnodelist, cstate, fullstatelist):
    # copied from MultiQM.py
    # read a function, and return with its node and finds the nodes' states from a complete node level array
    # Note: only accept captalized operators e.g. 'AND'.
    nodelist = []
    statelist = []
    if '=' in function:
        function1 = function.split("=",1)[1].strip()
    else:
        function1 = function
##    print function1
    implicants = function1.split("OR")
##    print implicants
    for implicant in implicants:
        implicant1 = (implicant.strip()).translate(None,'()')
        vnodes = implicant1.split("AND")
        for vnode in vnodes:
            node = vnode.split("$",1)[0].strip()
##            state = vnode.split("$",1)[1].strip()
            if node not in nodelist:
                nodelist.append(node)

    # evaluating the function
    str1 = function1
    for i in range(0,len(fullnodelist)):
    # replace occurences of state nodes with '1's and '0's
    # enumerate a state for this node: correspondent state node =>1, othere nodes =>0
        ON = str(fullnodelist[i]) + '$' + str(cstate[i])
##        print 'ON=',ON
        str1 = str1.replace(ON,'1')
        for state in fullstatelist[i]:
            if str(state) != str(cstate[i]):
                OFF = str(fullnodelist[i]) + '$' + str(state)
##                print 'OFF=',OFF
                str1 = str1.replace(OFF,'0')
    str1 = str1.replace('OR','|')
    str1 = str1.replace('AND','&')
    str1 = str1.replace('NOT','~')
##    print str1
    return eval(str1)


# test example

##y = Reduction.to_list('toy_example1.txt')
##y = 'A$0* = B$0 OR (C$1 AND B$1)'
##fullnodelist = ['A','B','C']
##cstate = [1,1,1]
##fullstatelist = [[0,1],[0,1],[0,1]]
##x = evalfunc(y,fullnodelist, cstate,fullstatelist)
##x = evalfunc('A$0* = B$0 OR (C$1 AND B$1)', ['A', 'B', 'C'], ['1', '0', '0'], [['0', '1', '2'], ['0', '1', '2'], ['0', '1']])
##print x



def nodescan(functionlist,mode=0,subzero=0):
    # find how many original node there is, and how many states each has;
    # (Obsolete) subzero=1: substitute any 'N$0' state nodes with the negation of other node, e.g 'not N$1 and not N$2'
    # TBD: mode=1: show warning of node function errors/issues

    # TBD: replacesib=1: replace undetermined nodes whose sibling nodes are identified. Will not run if replacesib=0.

    # return a list of nodes,a list of states and a list of # states for the corresponding node

    nodelist=[]
    nodestates=[]
    nodestatenumber=[]
    nodehigheststate=[] #record the highest state given in the node name
    newfunctionlist=[]
    Flags=[]
    for words in functionlist:
        vnode = words.split("*",1)[0].strip()
        node = vnode.split("$",1)[0].strip()
        state = vnode.split("$",1)[1].strip()
        function = words.split("=",1)[1].strip()

        if node not in nodelist:
            nodelist.append(node)
            nodestates.append([state])
            nodestatenumber.append(1)
            nodehigheststate.append(state)
            Flags.append(0)
        else:
            # corresponding nodestatenumber +1
            x = nodelist.index(node)
            nodestates[x].append(state)
            nodestatenumber[x] += 1
            if nodehigheststate[x] < state:
                nodehigheststate[x] = state
##                print 'node=',node
##                print 'nodehigheststate=',nodehigheststate
##        if replacesib==1 and not function.isdigit():
##        # check if all sibling nodes has their states identified
##            Flag2=0
##            for words2 in functionlist:
##                vnode2 = words2.split("*",1)[0].strip()
##                node2 = vnode2.split("$",1)[0].strip()
##                state2 = vnode2.split("$",1)[1].strip()
##                function2 = words2.split("=",1)[1].strip()
##                if node ==node2 and state != state2:
##                    # only continues if Flag2<=1
##                    if function2==1:
##                        Flag2 +=1
##                        if Flag2 >=2:
##                            break
##                    elif not function2.isdigit():
##                        Flag2 = 'x'
##                        break
##            if Flag2 ==0 :
##            # reconstruct the function
##                result= vnode + '* = ' + function
##            elif Flag2==1 :
##                result= vnode + '* = ' + 1
##            newfunctionlist.append(result)


##    print nodelist
    if mode==1:
        for i in range(0,len(nodelist)):
##            print i
##            print 'node=',nodelist[i]
##            print nodehigheststate[i]
##            print nodestatenumber[i]
            if int(nodehigheststate[i]) != (nodestatenumber[i]-1):
                print 'warning: node {} has number of states that does not match: max state {}, total states {}'.format(nodelist[i],nodehigheststate[i],nodestatenumber[i]-1)
##            print '------'
    # substituting zero states (not needed anymore)
    if subzero ==1:
        removable = ['(',')',' ']
        for words in functionlist:
            # put a space before each '(', if there hasn't been a space
            str2 = ''
            if len(words)>=1:
                for i in range(0,len(words)):
                    if str2 != '':
                        if (words[i]=='(') and (str2[i-1] != ' '):
                            str2 += ' '
                    str2 += words[i]
                words = str2

            vnode = words.split("*",1)[0].strip()
            node = vnode.split("$",1)[0].strip()
            state = vnode.split("$",1)[1].strip()
            function = words.split("=",1)[1].strip()
    ##        print 'state=',state
            if state != 0: # always true
    ##            print function
                # find zero states in the function
                result= vnode + '* = '
                for item in function.split():
    ##                print item
                    result1=''
                    end=''
                    if len(item)>=2:
                        while item[0] in removable:  # remove symbols in 'removable' category
                            result += item[0]
                            item = item[1:len(item)]
                        while item[len(item)-1] in removable:
                            end += item[len(item)-1]
                            item = item[0:len(item)-1]
                        # substitute zero after found
                        if '$' in item:
    ##                        print item
                            nodex = item.split("$",1)[0]
                            statex = item.split("$",1)[1]
                            if not statex.isdigit():
                                print 'ERROR! state is not digit'
                            elif statex =='0':
                                index1 = nodelist.index(nodex)
                                result1 += '('
                                for j in range (0,nodestatenumber[index1]):
                                    if nodestates[index1][j]!='0':
                                        result1 += 'not '
                                        result1 += nodelist[index1]
                                        result1 += '$'
                                        result1 += nodestates[index1][j]
                                        result1 += ' AND '

                                result1 = result1[:len(result1)-5]
                                result1 += ')'
                            else:
                                result1 = item

                            result += result1

                            result += end
                            if result[len(result)-1] != ' ':
                                result += ' '
                        else:
                            result += item
                            if result[len(result)-1] != ' ':
                                result += ' '
                    else:
                        result += item
                        if result[len(result)-1] != ' ':
                            result += ' '
    ##                print 'result=',result
                newfunctionlist.append(result.strip())

    return [nodelist, nodestates, nodestatenumber, nodehigheststate, newfunctionlist]


# test example:
##y = Reduction.to_list('toy_example1.txt')
##print y
##x = nodescan(y,mode=1)
##print x


def sub_not(function,nodelist, nodestates):
    # Obsolete
    # substitute 'not A1' type of rules with 'A0 or A2 or...' s.t. there is no 'not' rule in the result
    # input is a function string, output is a string
    # current version: does not consider situations with 'not('
    result=''
    i=0
    while i < len(function):
        if function[i:i+4].lower() == 'not ':
            j= i+4
##            print type(len(function)-1)
            vnode = function[j:len(function)-1].split(" ",1)[0]
            while vnode[len(vnode)-1]==')':
                vnode = vnode[0:len(vnode)-1]
##            print vnode
            if '$' not in vnode:
                print 'Error! No sign in vnode'
            else:
                node = vnode.split("$",1)[0].strip()
##                print node
                state = vnode.split("$",1)[1].strip()
##                print state
                index = nodelist.index(node)
                result += '('
                for k in range (0,len(nodestates[index])):
                    if nodestates[index][k] != state:
                        result += node + '$' + nodestates[index][k]
                        result += ' or '

                result = result[0:len(result)-4].strip() + ')'
            i = j + len(vnode)
        else:
            result += function[i]
            i += 1

    return result

# ###############   test   #############
##str1 = '(N9$2 AND N5$1) OR (NOT N9$1 AND N5$2 AND N5$1) OR (NOT N9$1 AND NOT N9$2 AND N5$2)'
##nodelist = ['N9','N5']
##str1 = '(N2$2 AND N4$1) OR (NOT N2$2 AND NOT N4$1 AND NOT N4$2) OR (N2$1)'
##nodelist = ['N2','N4']
##

def exclusioncheck(function):
    # Obsolete
    # check if the function has contradictory terms, e.g. 'A1 & A2'. Remove this type of implicants from the function string.
    # return a string of outcome function
    newfunction=''
    implicants = function.split("OR")
##    print implicants
    for implicant in implicants:
##        print 'implicant:',implicant
        if 'AND' in implicant:
            x = implicant.translate(None,'()')
            x1 = functions.findinputsstr(x)
##            print x1
            if not functions.containrep(x1):
                newfunction+= implicant.strip() + ' OR '
        else:
            newfunction+= implicant.strip() + ' OR '
##        print newfunction
    newfunction = newfunction[0:len(newfunction)-4].strip()
    if 'OR' not in newfunction:
        newfunction = newfunction.translate(None,'()')
    return newfunction


# test example
##str1='((not N4$1 AND not N4$2) AND (not N3$1 AND not N3$2))'
##nodelist = ['N3','N4']
##nodestates = [['0','1','2'],['0','1','2']]
##x = sub_not(str1,nodelist, nodestates)
##print x
##y = Booleanops.transform(x)
##print y
##z = exclusioncheck(y)
##print z



def sample(functionlist):
    # Obsolete
    # TBD: simulate partial state space of a functionlist, from N initial states, in T timesteps.

    x = nodescan(functionlist)
    # x: [nodelist, nodestates, nodestatenumber, nodehigheststate]
    print x
    nodelist =[]
    statelist =[]
    # generating initial states by randomly assign a value to each original node
##    for j in range (0,N):
    for i in range (0,len(x[0])):
        y = random.choice(x[1][i])
        nodelist.append(str(x[0][i])+ '$' + str(y))
        statelist.append(1)
    return Reduction.inputsub(functionlist,[nodelist, statelist])

# test example
##
##y = Reduction.to_list('toy_example1.txt')
##print y
##x = sample(y)
##print x



def simulate (functionlist,timestep,outputmode=0,istates=[]):
    # simulate the trajectory of a model
    # inputs:
    # output mode 0: print ss or trajectory in format: [t (int,timestep; t=-1 means no ss was found), ss state/trajectory (a list)]
    # output mode 1: print in words a steady state or trajectory is found
    # TBD: istate is a designated initial state (as a list). Its default is an empty list, in which case a random initial state will be generated.

    x = nodescan(functionlist)
    nodes = x[0]
    fullstatelist =x[1]

    if istates ==[]:
        # generate an initial state
        initial_state = []
        for i in range (0,len(x[0])):
            y = random.choice(x[1][i])
            initial_state.append(y)
    else:
        initial_state = random.choice(istates)

    trajectory =[initial_state]
##    print trajectory
    reducedlist = functionlist
    # (Optional TBD) reduction / QM transformation of functions

    cstate = copy.copy(initial_state)

    for t in range(0, timestep):
    # Simulation of: effective trajectory:
    # 1. randomly select a original node index (i,e, a set of functions corresponding to the same node), then simulate
   	# 2. if result is same, remove this index (i.e. this set of functions), then go to 1
	# 3. if all results are same (no function left), reached a steady state attractors
##        print cstate
        list1 = reducedlist
        indexrange1 = range(len(nodes))
        Flag1 = 0
##        trajectory.append(cstate)
        states = []
        for i in indexrange1:
            states.append(nodes[i]+'$'+cstate[i])
##        print states

        while (Flag1==0 and indexrange1 !=[]):
            index1 = random.choice(indexrange1)
##            print 'index1=',index1
##            newstate = '@'

            # evaluate new state, by first accessing the correspondent functions
            for words in reducedlist:
                vnode = words.split("*",1)[0].strip()
                node = vnode.split("$",1)[0].strip()
                state1 = vnode.split("$",1)[1].strip()
                function1 = words.split("=",1)[1].strip()
                if node == nodes[index1]:
##                    print words
                    # find the new state of this node
##                    print 'eval:',words,nodes, cstate,fullstatelist
                    new = evalfunc(words,nodes, cstate,fullstatelist)
##                    print node,state1,new,type(new)
                    if new == '1' or new == True or new == 1:
                        newstate = state1
                        states[index1] = nodes[index1]+'$'+cstate[index1]
##            if newstate == '@': print 'Error:', nodes[index1]
##            print newstate,cstate[index1]
            if newstate != cstate[index1]:
                Flag1=1
                cstate[index1] = newstate
            else:
                # remove this index
                indexrange1.remove(index1)
        if indexrange1 == []:
        # reached a steady state
            if outputmode ==0:
                return [t,cstate]
            if outputmode ==1:
                return 'steady state in {} steps:{}; trajectory: {}'.format(t,cstate,trajectory)
        else:
            trajectory.append(copy.copy(cstate))
##            print trajectory

    if outputmode ==0:
        return [-1,trajectory]
    if outputmode ==1:
        return 'trajectory:',trajectory

# test example
test = 0
if test ==1:
    y= ['N0$0* =(N7$2 AND N6$1)', 'N0$1* =(N7$0 AND N6$0) OR (N7$0 AND N6$1) OR (N7$1 AND N6$0) OR (N7$1 AND N6$1) OR (N7$1 AND N6$2) OR (N7$2 AND N6$0) OR (N7$2 AND N6$2)', 'N0$2* =(N7$0 AND N6$2)', 'N1$0* =(N3$0 AND N9$0) OR (N3$0 AND N9$2) OR (N3$2 AND N9$0) OR (N3$2 AND N9$2)', 'N1$1* =(N3$1 AND N9$0) OR (N3$1 AND N9$2)', 'N1$2* =(N3$0 AND N9$1) OR (N3$1 AND N9$1) OR (N3$2 AND N9$1)', 'N2$0* =(N6$0 AND N7$0) OR (N6$0 AND N7$1) OR (N6$0 AND N7$2) OR (N6$1 AND N7$1) OR (N6$1 AND N7$2) OR (N6$2 AND N7$0) OR (N6$2 AND N7$1)', 'N2$1* =(N6$1 AND N7$0) OR (N6$2 AND N7$2)', 'N3$0* =(N1$2 AND N7$2)', 'N3$1* =(N1$0 AND N7$0) OR (N1$0 AND N7$1) OR (N1$0 AND N7$2) OR (N1$1 AND N7$1) OR (N1$1 AND N7$2) OR (N1$2 AND N7$1)', 'N3$2* =(N1$1 AND N7$0) OR (N1$2 AND N7$0)', 'N4$0* =(N9$0 AND N5$0) OR (N9$1 AND N5$0) OR (N9$1 AND N5$1)', 'N4$1* =(N9$0 AND N5$1) OR (N9$2 AND N5$0) OR (N9$2 AND N5$1)', 'N5$0* =(N4$0 AND N7$0) OR (N4$0 AND N7$1) OR (N4$0 AND N7$2) OR (N4$1 AND N7$0) OR (N4$1 AND N7$2)', 'N5$1* =(N4$1 AND N7$1)', 'N6$0* =(N0$0 AND N4$1) OR (N0$1 AND N4$0) OR (N0$2 AND N4$1)', 'N6$1* =(N0$0 AND N4$0) OR (N0$2 AND N4$0)', 'N6$2* =(N0$1 AND N4$1)', 'N7$0* =(N4$0 AND N0$0)', 'N7$1* =(N4$0 AND N0$1) OR (N4$0 AND N0$2) OR (N4$1 AND N0$0) OR (N4$1 AND N0$2)', 'N7$2* =(N4$1 AND N0$1)', 'N8$0* =(N4$1 AND N2$0)', 'N8$1* =(N4$0 AND N2$0) OR (N4$1 AND N2$1)', 'N8$2* =(N4$0 AND N2$1)', 'N9$0* =(N4$1 AND N5$1)', 'N9$1* =(N4$0 AND N5$1) OR (N4$1 AND N5$0)', 'N9$2* =(N4$0 AND N5$0)']

    start_time = time.time()
    z = simulate (y,timestep=500,outputmode=1,istates=[])
    print z
##    w = show_atr(z)
##    print w

    print("--- %s seconds ---" % (time.time() - start_time))



def createSTG(traj,STG=0):
    # for cases where no SS where found, construct/add-up a state-transition-graph(STG) based on the trajectory, then find terminal SCCs in this STG
    # traj is a trajectory, i.e. a list of states, where each state is a list of nodestates
    # STG: modify to unify all trajectories from different samples; STG=0: single trajectories
    if STG==0:
        STG=nx.DiGraph()
    for i in range(0,len(traj)-1):      # create STG from trajectory
        if not STG.has_edge(str(traj[i]),str(traj[i+1])):
            STG.add_edge(str(traj[i]),str(traj[i+1])) # turn lists into strings to create nodenames in the Digraph
    return STG

def terminalSCC(STG):
    # Obsolete
    # finds the terminal SCCs from a STG.
    SCCs = list(nx.strongly_connected_components(STG))
    attractors = []
    for item1 in SCCs:
    # finding the terminal SCC
        if nx.is_attracting_component(item1):
            attractors.append(item1)
##        for item2 in SCCs:
##            if item2 != item1:
##                if nx.has_path(STG,list(item1)[0],list(item2)[0]): # SCC1 has path to SCC2, SCC1 is not a teminal SCC
##                    break
##        else:
##            if item1 not in attractors:
##                attractors.append(item1)
##    print 'terminal SCCs: ',attractors
    return attractors

# test
##traj1 = [['0', '0', '0', '1', '0'], ['0', '0', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1'], ['0', '0', '0', '1', '1'], ['0', '0', '0', '0', '1'], ['0', '0', '1', '0', '1'], ['0', '0', '1', '1', '1']]
##traj1 = [['1', '0', '2', '2', '0', '0'], ['0', '0', '2', '2', '0', '0'], ['0', '0', '2', '2', '0', '1'], ['0', '2', '2', '2', '0', '1'], ['0', '2', '2', '2', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '0', '2', '2', '1'], ['1', '2', '0', '2', '1', '1'], ['1', '2', '0', '2', '1', '0'], ['1', '2', '0', '2', '2', '0'], ['2', '2', '0', '2', '2', '0'], ['2', '2', '1', '2', '2', '0'], ['1', '2', '1', '2', '2', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '1'], ['0', '0', '2', '2', '2', '1'], ['0', '0', '2', '2', '1', '1'], ['0', '0', '0', '2', '1', '1'], ['0', '0', '0', '1', '1', '1'], ['1', '0', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['2', '2', '0', '1', '1', '0'], ['2', '2', '0', '1', '1', '1'], ['2', '2', '2', '1', '1', '1'], ['2', '2', '2', '0', '1', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '0', '0', '2', '1'], ['0', '1', '0', '0', '2', '1'], ['0', '1', '0', '0', '2', '0'], ['0', '1', '0', '1', '2', '0'], ['0', '1', '0', '1', '0', '0'], ['0', '1', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['0', '1', '2', '2', '2', '0'], ['0', '1', '2', '1', '2', '0'], ['0', '2', '2', '1', '2', '0'], ['0', '2', '2', '1', '0', '0'], ['0', '2', '1', '1', '0', '0'], ['1', '2', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '2', '2', '0', '0'], ['1', '0', '2', '2', '0', '0'], ['0', '0', '2', '2', '0', '0'], ['0', '0', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '0'], ['0', '2', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '1'], ['2', '2', '1', '1', '0', '1'], ['2', '2', '2', '1', '0', '1'], ['0', '2', '2', '1', '0', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['1', '2', '0', '0', '1', '0'], ['1', '2', '0', '0', '2', '0'], ['1', '2', '0', '2', '2', '0'], ['2', '2', '0', '2', '2', '0'], ['2', '2', '0', '0', '2', '0'], ['2', '2', '1', '0', '2', '0'], ['2', '2', '1', '0', '2', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '0', '0', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '0', '0', '1', '1'], ['1', '1', '2', '0', '1', '1'], ['1', '1', '2', '0', '1', '0'], ['0', '1', '2', '0', '1', '0'], ['0', '1', '1', '0', '1', '0'], ['0', '2', '1', '0', '1', '0'], ['0', '2', '1', '1', '1', '0'], ['0', '2', '1', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['0', '1', '1', '1', '1', '0'], ['0', '2', '1', '1', '1', '0'], ['0', '2', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '1'], ['2', '2', '1', '1', '0', '1'], ['2', '2', '2', '1', '0', '1'], ['0', '2', '2', '1', '0', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['0', '1', '1', '1', '1', '0'], ['1', '1', '1', '1', '1', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '1'], ['1', '0', '2', '2', '1', '1'], ['1', '0', '2', '0', '1', '1'], ['1', '0', '2', '0', '2', '1'], ['0', '0', '2', '0', '2', '1'], ['0', '0', '2', '1', '2', '1'], ['0', '0', '0', '1', '2', '1'], ['0', '0', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['1', '2', '2', '1', '1', '0'], ['1', '2', '2', '0', '1', '0'], ['1', '2', '2', '0', '2', '0'], ['1', '2', '2', '2', '2', '0'], ['0', '2', '2', '2', '2', '0'], ['0', '2', '2', '1', '2', '0'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '1', '0'], ['1', '2', '0', '0', '2', '0'], ['1', '2', '0', '2', '2', '0'], ['1', '2', '2', '2', '2', '0'], ['0', '2', '2', '2', '2', '0'], ['0', '2', '1', '2', '2', '0'], ['1', '2', '1', '2', '2', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '1'], ['0', '0', '2', '2', '2', '1'], ['0', '0', '0', '2', '2', '1'], ['0', '0', '0', '2', '1', '1'], ['0', '0', '0', '1', '1', '1'], ['1', '0', '0', '1', '1', '1'], ['1', '0', '0', '0', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '1', '0'], ['2', '2', '0', '0', '1', '0'], ['2', '2', '0', '0', '2', '0'], ['2', '2', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '0'], ['1', '2', '2', '0', '2', '0'], ['1', '0', '2', '0', '2', '0'], ['0', '0', '2', '0', '2', '0'], ['0', '0', '2', '0', '2', '1'], ['0', '0', '2', '1', '2', '1'], ['0', '0', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['0', '1', '0', '1', '0', '0'], ['0', '1', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '1'], ['0', '2', '0', '1', '0', '1'], ['1', '2', '0', '1', '0', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['1', '2', '0', '0', '1', '0'], ['1', '2', '2', '0', '1', '0'], ['0', '2', '2', '0', '1', '0'], ['0', '2', '1', '0', '1', '0'], ['1', '2', '1', '0', '1', '0'], ['1', '1', '1', '0', '1', '0'], ['1', '1', '1', '0', '2', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['0', '1', '2', '2', '2', '0'], ['0', '2', '2', '2', '2', '0'], ['0', '2', '2', '1', '2', '0'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '2', '1', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '0'], ['1', '1', '0', '0', '1', '0'], ['2', '1', '0', '0', '1', '0'], ['2', '1', '0', '0', '1', '1'], ['1', '1', '0', '0', '1', '1'], ['1', '1', '2', '0', '1', '1'], ['0', '1', '2', '0', '1', '1'], ['0', '1', '2', '1', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '0', '0', '1', '1'], ['1', '1', '0', '0', '1', '0'], ['1', '1', '0', '0', '2', '0'], ['2', '1', '0', '0', '2', '0'], ['2', '1', '0', '0', '2', '1'], ['2', '2', '0', '0', '2', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['1', '2', '0', '1', '2', '1'], ['1', '2', '2', '1', '2', '1'], ['1', '0', '2', '1', '2', '1'], ['1', '0', '2', '1', '1', '1'], ['0', '0', '2', '1', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '2', '1', '1', '1'], ['0', '1', '2', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '0', '0'], ['2', '1', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '2', '1', '0', '0'], ['1', '1', '2', '2', '0', '0'], ['0', '1', '2', '2', '0', '0'], ['0', '1', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '1'], ['0', '2', '0', '1', '0', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '1', '0'], ['1', '2', '2', '0', '1', '0'], ['1', '2', '2', '0', '2', '0'], ['1', '0', '2', '0', '2', '0'], ['1', '0', '2', '0', '2', '1'], ['1', '0', '2', '2', '2', '1'], ['0', '0', '2', '2', '2', '1'], ['0', '0', '0', '2', '2', '1'], ['0', '0', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '0'], ['0', '1', '1', '1', '2', '0'], ['0', '2', '1', '1', '2', '0'], ['1', '2', '1', '1', '2', '0'], ['1', '1', '1', '1', '2', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '1'], ['1', '0', '2', '2', '1', '1'], ['0', '0', '2', '2', '1', '1'], ['0', '2', '2', '2', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['0', '1', '0', '1', '0', '0'], ['0', '1', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '0'], ['1', '2', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '2', '2', '0', '0'], ['1', '1', '2', '2', '2', '0'], ['0', '1', '2', '2', '2', '0'], ['0', '1', '2', '1', '2', '0'], ['0', '1', '2', '1', '0', '0'], ['0', '1', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '1', '2', '2', '0'], ['1', '1', '2', '2', '2', '0'], ['0', '1', '2', '2', '2', '0'], ['0', '1', '1', '2', '2', '0'], ['0', '1', '1', '1', '2', '0'], ['0', '2', '1', '1', '2', '0'], ['0', '2', '1', '1', '0', '0'], ['0', '2', '1', '1', '0', '1'], ['2', '2', '1', '1', '0', '1'], ['2', '2', '1', '1', '1', '1'], ['2', '2', '1', '0', '1', '1'], ['2', '2', '2', '0', '1', '1'], ['0', '2', '2', '0', '1', '1'], ['0', '2', '0', '0', '1', '1'], ['0', '2', '0', '0', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '1', '0'], ['2', '1', '1', '1', '1', '0'], ['2', '1', '1', '1', '1', '1'], ['2', '1', '1', '0', '1', '1'], ['2', '2', '1', '0', '1', '1'], ['2', '2', '2', '0', '1', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '2', '1', '1', '1'], ['0', '1', '2', '1', '1', '1'], ['0', '1', '2', '1', '1', '0'], ['0', '1', '1', '1', '1', '0'], ['1', '1', '1', '1', '1', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '2', '1', '0', '0'], ['1', '0', '2', '1', '0', '0'], ['0', '0', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '1'], ['0', '2', '0', '1', '0', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['2', '2', '0', '1', '1', '0'], ['2', '2', '1', '1', '1', '0'], ['2', '2', '1', '0', '1', '0'], ['2', '2', '1', '0', '1', '1'], ['2', '2', '2', '0', '1', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['1', '1', '0', '1', '2', '1'], ['1', '2', '0', '1', '2', '1'], ['1', '2', '2', '1', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['1', '1', '0', '1', '2', '1'], ['1', '1', '2', '1', '2', '1'], ['1', '1', '2', '2', '2', '1'], ['0', '1', '2', '2', '2', '1'], ['0', '1', '0', '2', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '2', '1', '1', '1'], ['1', '2', '2', '0', '1', '1'], ['1', '0', '2', '0', '1', '1'], ['0', '0', '2', '0', '1', '1'], ['0', '0', '2', '1', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['0', '1', '0', '1', '0', '0'], ['0', '1', '1', '1', '0', '0'], ['1', '1', '1', '1', '0', '0'], ['1', '1', '1', '2', '0', '0'], ['1', '1', '2', '2', '0', '0'], ['1', '1', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '0'], ['1', '0', '2', '2', '2', '1'], ['1', '0', '2', '2', '1', '1'], ['1', '0', '2', '0', '1', '1'], ['0', '0', '2', '0', '1', '1'], ['0', '2', '2', '0', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '0', '2', '2', '1'], ['1', '2', '2', '2', '2', '1'], ['1', '2', '2', '2', '1', '1'], ['1', '2', '2', '2', '1', '0'], ['0', '2', '2', '2', '1', '0'], ['0', '2', '2', '2', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '2', '1', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '0'], ['1', '1', '0', '0', '1', '0'], ['2', '1', '0', '0', '1', '0'], ['2', '1', '0', '0', '2', '0'], ['2', '2', '0', '0', '2', '0'], ['2', '2', '1', '0', '2', '0'], ['2', '2', '1', '0', '2', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '0', '0', '2', '1'], ['0', '1', '0', '0', '2', '1'], ['1', '1', '0', '0', '2', '1'], ['1', '1', '2', '0', '2', '1'], ['0', '1', '2', '0', '2', '1'], ['0', '1', '0', '0', '2', '1'], ['1', '1', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '0', '0', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '1'], ['0', '1', '0', '1', '2', '0'], ['2', '1', '0', '1', '2', '0'], ['2', '2', '0', '1', '2', '0'], ['2', '2', '1', '1', '2', '0'], ['2', '2', '1', '1', '2', '1'], ['2', '2', '1', '0', '2', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['1', '2', '0', '1', '2', '1'], ['1', '2', '0', '2', '2', '1'], ['1', '2', '2', '2', '2', '1'], ['0', '2', '2', '2', '2', '1'], ['0', '2', '2', '2', '1', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '0'], ['2', '1', '0', '1', '1', '0'], ['2', '2', '0', '1', '1', '0'], ['2', '2', '0', '1', '0', '0'], ['2', '2', '0', '1', '0', '1'], ['2', '2', '0', '1', '1', '1'], ['2', '2', '0', '0', '1', '1'], ['2', '2', '0', '0', '2', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '2', '1', '1', '1'], ['0', '2', '0', '1', '1', '1'], ['0', '1', '0', '1', '1', '1'], ['1', '1', '0', '1', '1', '1'], ['1', '1', '2', '1', '1', '1'], ['1', '1', '2', '1', '1', '0'], ['1', '1', '2', '1', '0', '0'], ['0', '1', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '0'], ['0', '2', '2', '1', '0', '1'], ['0', '2', '0', '1', '0', '1'], ['0', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '1'], ['1', '2', '0', '1', '1', '0'], ['1', '2', '0', '1', '0', '0'], ['2', '2', '0', '1', '0', '0'], ['2', '2', '1', '1', '0', '0'], ['2', '2', '1', '1', '0', '1'], ['2', '2', '1', '1', '1', '1'], ['2', '2', '1', '0', '1', '1'], ['2', '2', '2', '0', '1', '1'], ['2', '2', '2', '0', '2', '1'], ['0', '2', '2', '0', '2', '1'], ['0', '2', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '0'], ['1', '2', '2', '0', '2', '0'], ['0', '2', '2', '0', '2', '0'], ['0', '2', '2', '1', '2', '0'], ['0', '2', '2', '1', '2', '1'], ['0', '2', '0', '1', '2', '1'], ['1', '2', '0', '1', '2', '1'], ['1', '2', '0', '2', '2', '1'], ['1', '2', '0', '2', '1', '1'], ['1', '2', '0', '0', '1', '1'], ['1', '2', '0', '0', '2', '1'], ['1', '2', '0', '0', '2', '0'], ['1', '2', '0', '2', '2', '0'], ['2', '2', '0', '2', '2', '0'], ['2', '2', '0', '2', '2', '1']]
##x = createSTG(traj1)
##print x

def simulate_attractor(functionlist,samplesize,Tsteps,Ttrans,Tsearch,istates=[]):
    # simulation method to find attractors.
    # samplesize: # of initial states; Tsteps: # of steps of 1st simulation; Ttrans & Tsearch: quoted from Jorge's paper:'To avoid false positives, we check the validity of every attractor obtained with this method by starting from one of the states in the putative attractor, updating it Ttransient eective time steps, then creating a partial state transition graph with Tsearch eective time steps, and nally searching for attractors in the resulting state transition graph.'
    # 'istates' is an optional input that designates a specific initial state set to start the simulation with. leaing it empty means generating random initial states.
    # return all found attractors
    attractors = []
##    STG=0
    STG=nx.DiGraph()
    osc_count=0
    i=0
    for i in range(0,samplesize):
        x = simulate(functionlist,Tsteps,outputmode=0,istates=istates)
        if x[0]==-1:
            # further analyze the trajectory to find possible oscillation
##            print 'trajectory:{}'.format(x[1])
            STG = createSTG(x[1],STG=STG)
##            print 'STG:',STG.nodes()
            attractor =[]
##            for item in att_temp:
##                attractor.append(eval(item))
##            attractor=sorted(attractor)
##            print 'attractor1:',attractor
            x = simulate(functionlist,Ttrans,outputmode=0,istates=attractor)
            if x[0]== -1:       # confirmed oscillation
            # check if trajectory is within the previous found attractor
##                print 'trajectory:{}'.format(x[1])
                STG = createSTG(x[1],STG=STG)
##                print 'STGnodes: ',STG.nodes()
                att_temp = nx.attracting_components(STG)
##                print 'attractor_temp: ',att_temp
                # check: if att_temp is a single node, cancel this sample.  may need to set i -=1 to make sure samplesize.
                for att_temp1 in att_temp:
                    if len(att_temp1) <=1:
                        continue
                    else:
                        attractor =[]
                        for item in att_temp1:
                            attractor.append(eval(item))
                        attractor=sorted(attractor)
                        osc_count+=1
            else:
                attractor=x[1]      # steady state attractor
##            print attractor
        else:       # steady state attractor
            attractor=x[1]


        # filter out same attractors
        # TBD: filter out same oscillation
        if attractor not in attractors:
            attractors.append(attractor)
##            print 'steady state in {} steps:{}'.format(x[0],x[1])
##    if Flag ==0:
##        print 'All simulations yielded steady states.'
##    else:
##        print '{} our of {} runs yielded oscillations'.format(Flag,repeat)
    return [attractors,nodescan(functionlist)[0],osc_count]


def show_atr(result):
# convert the attractor found by simulation into a similar form of the result of SM
    attractorlist = []
    if result[0] != []:
        for attractor in result[0]:
            if attractor!= []:
                attractor1 = []
                if type(attractor[0]) == type('1'):  # if attractor is a steady state:
                    for node in result[1]:
                        func = node + '=' + str(attractor[result[1].index(node)])
                        if func not in attractor1:
                            attractor1.append(func)
                else:   # if attractor is an oscillation:
                    for osc_state in attractor:
                        for node in result[1]:
                            func = node + '=' + str(osc_state[result[1].index(node)])
                            if func not in attractor1:
                                attractor1.append(func)
                if sorted(attractor1) not in attractorlist:
                    attractorlist.append(sorted(attractor1))
    return attractorlist

def stablenodes(attractorlist):
# finding all stablized nodes in an attractor list (a list of sets). return a list of stavble nodes sets
# attractors with no stable nodes are discarded
    stableset=[]
##    print attractorlist
    for elem in attractorlist:
##        print elem
        stablenodes = []
        for item1 in elem:
            for item2 in elem:
##                print item1.split('='),'   ',item2.split('=')
                if (item1.split('=')[0] == item2.split('=')[0]) and (item1.split('=')[1] != item2.split('=')[1]):
##                    print 'break'
                    break
            else:
##                print 'appending',item1
                stablenodes.append(item1)
                continue
        if stablenodes != []:
            stableset.append(set(stablenodes))

    return stableset

# test example:
##y = [set(['D=0', 'D=1', 'B=0', 'B=1', 'A=1', 'A=0', 'C=1', 'C=0'])]
##y = [set(['N4=1', 'N4=0', 'N4=2', 'N2=2', 'N2=1', 'N2=0', 'N0=1', 'N0=0', 'N0=2', 'N1=0', 'N1=1', 'N1=2', 'N3=2', 'N5=1', 'N3=0', 'N3=1', 'N5=0']), set(['N4=2', 'N2=1', 'N0=1', 'N1=0', 'N5=1', 'N3=0']), set(['N4=2', 'N2=2', 'N0=0', 'N1=1', 'N3=2', 'N5=1']), set(['N4=2', 'N2=0', 'N0=1', 'N1=1', 'N3=2', 'N5=1'])]
##
##x = stablenodes(y)
##print x

def printatr(atr_SM,SMsequence):
# print an SM sequence
    print 'SM sequence:'
    for a in SMsequence:
        # print, but replace $ with =
        str1=''
        for sm in a:
            str1+='('
            for index in range(0, len(sm)):
                b = sm[index].replace('$','=')
                if 'AND' not in b:
                    str1+=b
                    if index < len(sm)-1:
                        str1+=','
            str1+=')'
        print str1
    return

def compare(atrlist_sim, atrlist_SM,Errorlist=[],ID=[],mode=0):
    # compare sampled attractors with SM attractors.
    # TBD: consistency check
    # check 1: 'consistency' for every quasi-attractor, there is a simluated partial SS that matches the stablized states of the quasi-attractor
    # check 2: 'equivalence' (Not sure if this is enough for multi-level case)
    #   - (weak ver.) non-stablized node oscillates
    #   - (strong ver.) non-stablized node oscillates within the given range
    # mode: 1: show SM sequence; 0: default, shows only att


    atr_sim = [set(sorted(elem)) for elem in atrlist_sim]
    atr_SM = []
    SMsequence = []
    atr_SM_stablized_nodes = []
    for elem in atrlist_SM:
##        print elem
        SM_stablized_nodes = []
        if set (sorted(elem[1])) not in atr_SM:
            atr_SM.append(set(sorted(elem[1])))
            SMsequence.append(elem[0])
##        if sorted(elem[1]) not in atr_SM:
##            print sorted(elem[1])
##            atr_SM.append(sorted(elem[1]))

            # finds SM-stabled nodes in elem
            if stablenodes([elem[1]]) != []: # all stablized nodes
##                print stablenodes([elem[1]])
                for item in stablenodes([elem[1]])[0]:
##                    print item
                    node1 = item.split('=')[0]
                    for sm in elem[0]:
##                        print sm, functions.containrep(functions.findinputs(sm))
                        if not functions.containrep(functions.findinputs(sm)):
                            for vnode in sm:
                                node2 = vnode.split('$')[0]
##                                print vnode,node2
                                if node1 == node2 and item not in SM_stablized_nodes:
                                    SM_stablized_nodes.append(item)
##                                    print 'adding:',item
                                    break
        atr_SM_stablized_nodes.append(SM_stablized_nodes)

    if atrlist_sim==[]:
        print 'SM result:'
        for a in atr_SM: print list(a),len(a)
        if mode ==1:
            printatr(atr_SM,SMsequence)
##            print 'SM sequence:'
##            for a in SMsequence:
##                # print, but replace $ with =
##                for sm in a:
##                    print '(',
##                    for index in range(0, len(sm)):
##                        b = sm[index].replace('$','=')
##                        if 'AND' not in b:
##                            print b,
##                            if index < len(sm)-1:
##                                print ',',
##                    print ')',
##                print

    else:
        print 'simluated:'
        for a in atr_sim: print a
        print 'SM result:'
        for a in atr_SM: print a,len(a)
        if mode ==1:
            printatr(atr_SM,SMsequence)
##            print 'SM sequence:'
##            for a in SMsequence: print a
    ##    print 'SM raw result:'
    ##    for item in atrlist_SM:
    ##        print item
    ##    print 'SM stablized nodes:',atr_SM_stablized_nodes

        # compare the two methods

        flag=0
        A = stablenodes(atr_SM)
        B = stablenodes(atr_sim)
    ##    print A,B
        # consistency check
    ##    for stb_nodes1 in atr_SM_stablized_nodes:
        for stb_nodes1 in A:
            if stb_nodes1!=[]:
                print 'stb_nodes1:', stb_nodes1
                for stb_nodes2 in B:
    ##                print 'stb_nodes2:', stb_nodes2
                    if stb_nodes2.issuperset(stb_nodes1):
                        print 'consistent'
                        break
                else:
                    print 'inconsistent', stb_nodes1
                    if ID != []:
                        Errorlist.append(str(ID)+':inconsistency')
                    flag+=1
                    continue
        if flag==0:
            print 'All consistent'
        else:
            print '{} inconsistencies', flag

        # SS completeness check
        for b1 in atr_sim:
            b2 = stablenodes([b1])
            if b2 !=[]:
    ##            print 'SS check:', stablenodes([b1]),len(b2[0]),b1,len(b1)
                if len(stablenodes([b1])[0]) == len (b1):
                    if b1 not in A:
                        print 'Error!'
                        if ID != []:
                            Errorlist.append(str(ID)+':missed SS')

        # equivalence check
            # Q: already contained in the consistency check?
    ##    for i in range(0,len(atr_SM_stablized_nodes)):
    ##        target = atr_SM_stablized_nodes[i]
    ##        if len(target) != len(stablenodes(atr_SM)[i]): # has a partial SM
    ##
    ##            for nodeset in atrlist_sim: # check if there is a SS that contains this SM
    ##                if nodeset.issuperset(set(target)) and len(stablenodes([nodeset])[0]) == len(nodeset): # if the nodeset is a complete SS, skip.
    ##                    break
    ##            else:
    ##                print 'equivalence check:', target, atr_SM[i]
    ##                if a1 not in B:
    ##                    print 'partial SM: Not equivalent!'
    ##                    if ID != []:
    ##                        Errorlist.append(str(ID)+': not equivalent')
    ##                else:
    ##                    print 'partial SM: equivalent'

    return


# test examle:
test=0
atr_SM =[set(['N4=1', 'N2=1', 'N0=1', 'N1=0', 'N5=1', 'N3=0']), set(['N4=1', 'N4=0', 'N4=2', 'N5=2', 'N2=1', 'N2=0', 'N1=0', 'N1=1', 'N1=2', 'N3=2', 'N5=1', 'N3=0', 'N3=1', 'N5=0'])]
atr_sim = [set(['N4=1', 'N2=1', 'N0=1', 'N1=0', 'N5=1', 'N3=0']), set(['N4=1', 'N2=1', 'N0=2', 'N1=1', 'N5=1', 'N3=1'])]


atr_sim =[set(['N4=1', 'N5=2', 'N2=0', 'N0=1', 'N0=2', 'N1=0', 'N1=1', 'N5=1', 'N3=0', 'N3=1'])]
atr_SM = [set(['N4=1', 'N4=0', 'N4=2', 'N5=2', 'N2=2', 'N2=1', 'N2=0', 'N0=1', 'N0=0', 'N0=2', 'N5=0', 'N5=1', 'N3=0', 'N3=1'])]


if test==1:
    flag=0
    for stb_nodes1 in stablenodes(atr_SM):
        print 'stb_nodes1:', stb_nodes1
        for stb_nodes2 in stablenodes(atr_sim):
            if stb_nodes2.issuperset(stb_nodes1):
                print 'consistent'
                break
        else:
            print 'inconsistent', stb_nodes1
            flag+=1
            continue
    if flag==0:
        print 'All consistent'
    else:
        print '{} inconsistencies', flag


# test example: Simulation

test = 0
repeat = 5
Tsteps = 20
Ttrans = 100
Tsearch = 300
initial_states=[]
mode=1
if test ==1:
##    import Reduction
##    y = Reduction.to_list('toy_example2.txt')
##    y= ['N0$0* =(N7$2 AND N6$1)', 'N0$1* =(N7$0 AND N6$0) OR (N7$0 AND N6$1) OR (N7$1 AND N6$0) OR (N7$1 AND N6$1) OR (N7$1 AND N6$2) OR (N7$2 AND N6$0) OR (N7$2 AND N6$2)', 'N0$2* =(N7$0 AND N6$2)', 'N1$0* =(N3$0 AND N9$0) OR (N3$0 AND N9$2) OR (N3$2 AND N9$0) OR (N3$2 AND N9$2)', 'N1$1* =(N3$1 AND N9$0) OR (N3$1 AND N9$2)', 'N1$2* =(N3$0 AND N9$1) OR (N3$1 AND N9$1) OR (N3$2 AND N9$1)', 'N2$0* =(N6$0 AND N7$0) OR (N6$0 AND N7$1) OR (N6$0 AND N7$2) OR (N6$1 AND N7$1) OR (N6$1 AND N7$2) OR (N6$2 AND N7$0) OR (N6$2 AND N7$1)', 'N2$1* =(N6$1 AND N7$0) OR (N6$2 AND N7$2)', 'N3$0* =(N1$2 AND N7$2)', 'N3$1* =(N1$0 AND N7$0) OR (N1$0 AND N7$1) OR (N1$0 AND N7$2) OR (N1$1 AND N7$1) OR (N1$1 AND N7$2) OR (N1$2 AND N7$1)', 'N3$2* =(N1$1 AND N7$0) OR (N1$2 AND N7$0)', 'N4$0* =(N9$0 AND N5$0) OR (N9$1 AND N5$0) OR (N9$1 AND N5$1)', 'N4$1* =(N9$0 AND N5$1) OR (N9$2 AND N5$0) OR (N9$2 AND N5$1)', 'N5$0* =(N4$0 AND N7$0) OR (N4$0 AND N7$1) OR (N4$0 AND N7$2) OR (N4$1 AND N7$0) OR (N4$1 AND N7$2)', 'N5$1* =(N4$1 AND N7$1)', 'N6$0* =(N0$0 AND N4$1) OR (N0$1 AND N4$0) OR (N0$2 AND N4$1)', 'N6$1* =(N0$0 AND N4$0) OR (N0$2 AND N4$0)', 'N6$2* =(N0$1 AND N4$1)', 'N7$0* =(N4$0 AND N0$0)', 'N7$1* =(N4$0 AND N0$1) OR (N4$0 AND N0$2) OR (N4$1 AND N0$0) OR (N4$1 AND N0$2)', 'N7$2* =(N4$1 AND N0$1)', 'N8$0* =(N4$1 AND N2$0)', 'N8$1* =(N4$0 AND N2$0) OR (N4$1 AND N2$1)', 'N8$2* =(N4$0 AND N2$1)', 'N9$0* =(N4$1 AND N5$1)', 'N9$1* =(N4$0 AND N5$1) OR (N4$1 AND N5$0)', 'N9$2* =(N4$0 AND N5$0)']

    y= ['N0$0* =(N4$0 AND N2$1)', 'N0$1* =(N4$0 AND N2$0) OR (N4$1 AND N2$0) OR (N4$1 AND N2$1)', 'N1$0* =(N12$1 AND N6$0) OR (N12$1 AND N6$1)', 'N1$1* =(N12$0 AND N6$0) OR (N12$0 AND N6$1)', 'N2$0* =(N11$0 AND N6$0) OR (N11$1 AND N6$1)', 'N2$1* =(N11$0 AND N6$1) OR (N11$1 AND N6$0)', 'N3$0* =(N12$0 AND N11$0) OR (N12$1 AND N11$1)', 'N3$1* =(N12$0 AND N11$1) OR (N12$1 AND N11$0)', 'N4$0* =(N14$0 AND N13$0) OR (N14$1 AND N13$0)', 'N4$1* =(N14$0 AND N13$1) OR (N14$1 AND N13$1)', 'N5$0* =(N3$0 AND N14$0) OR (N3$1 AND N14$1)', 'N5$1* =(N3$0 AND N14$1) OR (N3$1 AND N14$0)', 'N6$0* =(N14$1 AND N9$1)', 'N6$1* =(N14$0 AND N9$0) OR (N14$0 AND N9$1) OR (N14$1 AND N9$0)', 'N7$0* =(N3$0 AND N10$1) OR (N3$1 AND N10$1)', 'N7$1* =(N3$0 AND N10$0) OR (N3$1 AND N10$0)', 'N8$0* =(N6$0 AND N9$0) OR (N6$1 AND N9$1)', 'N8$1* =(N6$0 AND N9$1) OR (N6$1 AND N9$0)', 'N9$0* =(N13$0 AND N8$0) OR (N13$1 AND N8$0) OR (N13$1 AND N8$1)', 'N9$1* =(N13$0 AND N8$1)', 'N10$0* =(N13$1 AND N7$1)', 'N10$1* =(N13$0 AND N7$0) OR (N13$0 AND N7$1) OR (N13$1 AND N7$0)', 'N11$0* =(N0$1 AND N6$0) OR (N0$1 AND N6$1)', 'N11$1* =(N0$0 AND N6$0) OR (N0$0 AND N6$1)', 'N12$0* =(N1$0 AND N6$0) OR (N1$0 AND N6$1) OR (N1$1 AND N6$0)', 'N12$1* =(N1$1 AND N6$1)', 'N13$0* =(N10$0 AND N1$0) OR (N10$0 AND N1$1) OR (N10$1 AND N1$0)', 'N13$1* =(N10$1 AND N1$1)', 'N14$0* =(N9$0 AND N13$0) OR (N9$1 AND N13$0)', 'N14$1* =(N9$0 AND N13$1) OR (N9$1 AND N13$1)']


    start_time = time.time()
    z = simulate_attractor(y,repeat,Tsteps,Ttrans,Tsearch,initial_states)
    print 'result:', z
    w = show_atr(z)
    print w

    print("--- %s seconds ---" % (time.time() - start_time))



