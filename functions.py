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
##import matplotlib.pyplot as plt
import copy
import collections
##import time


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

    if mode==1:
        for i in range(0,len(nodelist)):
##            print i
##            print 'node=',nodelist[i]
##            print nodehigheststate[i]
##            print nodestatenumber[i]
            if int(nodehigheststate[i]) != (nodestatenumber[i]-1):
                print 'warning: node {} has number of states that does not match: max state {}, total states {}'.format(nodelist[i],nodehigheststate[i],nodestatenumber[i]-1)
##            print '------'

    return [nodelist, nodestates, nodestatenumber, nodehigheststate, newfunctionlist]


# test example:
##y =['N0$0* =(N1$0 AND N4$0) OR (N1$1 AND N4$0)', 'N0$1* =(N1$0 AND N4$1) OR (N1$1 AND N4$1) OR (N1$2 AND N4$0) OR (N1$2 AND N4$1)', 'N1$0* =(N3$0 AND N2$1) OR (N3$1 AND N2$0) OR (N3$2 AND N2$1)', 'N1$1* =(N3$0 AND N2$2) OR (N3$2 AND N2$0) OR (N3$2 AND N2$2)', 'N1$2* =(N3$0 AND N2$0) OR (N3$1 AND N2$1) OR (N3$1 AND N2$2)', 'N2$0* =(N1$0 AND N4$0) OR (N1$0 AND N4$1) OR (N1$2 AND N4$1)', 'N2$1* =(N1$2 AND N4$0)', 'N2$2* =(N1$1 AND N4$0) OR (N1$1 AND N4$1)', 'N3$0* =(N4$1 AND N2$1)', 'N3$1* =(N4$0 AND N2$0) OR (N4$0 AND N2$1) OR (N4$0 AND N2$2) OR (N4$1 AND N2$0)', 'N3$2* =(N4$1 AND N2$2)', 'N4$0* =(N2$0 AND N1$0) OR (N2$0 AND N1$1) OR (N2$1 AND N1$2) OR (N2$2 AND N1$0) OR (N2$2 AND N1$1)', 'N4$1* =(N2$0 AND N1$2) OR (N2$1 AND N1$0) OR (N2$1 AND N1$1) OR (N2$2 AND N1$2)']
##
##x = nodescan(y,mode=1)
##print x


def findinputs(list1,inc_normal=1,mode=1):
    # 'inc_normal' is an argument to control whether normal nodes are considered. Setting it=0 will return only inputs from composite nodes.
    # mode=1: normal mode; mode=0: return a list of composite nodes and a list of corresponding inputs
    composite_nodes=[]
    corresponding_inputs=[]
    nodes=[]
    for item in list1:
        if item.count('AND')>=1:
            composite_nodes.append(item)
            inputs = item.split("AND")
            inputs = [item.strip() for item in inputs]
            for item2 in inputs:
                if mode==1:
                    if item2 not in nodes:
                        nodes.append(item2)
                elif mode==0:
                    corresponding_inputs.append(inputs)
        else:
            if inc_normal:
                nodes.append(item)
    if mode==0:
        return [composite_nodes, corresponding_inputs]
    else:
        return list(set(nodes))




def findinputsstr(string,mode=1): # returns a list of input nodes for an implicant string (node names connected with 'AND').
    inputs=[]
    inputscount = string.count('AND')+1
    if inputscount>=2:
        inputs = string.split("AND")
        inputs = [ item.strip() for item in inputs]
    else:
        inputs.append(string)
    if mode==1:
        return list(set(inputs))
    if mode==0:
        return inputscount

# example
##print findinputsstr ('C$1 AND A$1 AND B$1')

def unrepeatednode(list):
    # From a list of nodes (may include composite nodes), return a list of virtual nodes that does not have other virtual nodes corresponding to the same original node
    Flag=0
    nodelist=[]
##    print nodelist
    repeated=[]
    for item in list:
    # select only virtual nodes; filters out compsite nodes
        if (item.count('AND')==0) and (item.count('$')==1):
            nodelist.append(item)
        elif (item.count('AND')==0) and (item.count('$')==0):
            print 'Error in nodelist'
            return
##    print nodelist
    for i in range (0,len(nodelist)):
        if nodelist[i] not in repeated:
##            print
##            print nodelist[i]
            node1 = nodelist[i].split('$')[0]
            state1 = nodelist[i].split('$')[1]
            Flag1=0
            for j in range (i+1,len(nodelist)):
##                print nodelist[j]
                if nodelist[j] not in repeated:
                    # see if same original node
                    node2 = nodelist[j].split('$')[0]
                    state2 = nodelist[j].split('$')[1]
                    if (node1==node2) and (state1!=state2):
                        repeated.append(nodelist[j])
                        Flag1=1
##                else:
##                    print 'Error: nodelist[j] in repeated',nodelist[j],repeated
            if Flag1==1:
                repeated.append(nodelist[i])
##    print repeated
    return [x for x in nodelist if x not in repeated]

# test examples
##y = ['B$1', 'B$0']
##x = unrepeatednode(y)
##print x

def containrep(list): # check if a list of input nodes contain at least two that refers to the same original node
    Flag=0
    nodes=[]
    states=[]
##    print list
    for index in range (len(list)):
        if list[index].count('AND')>=1:
            print "Error in containrep"
            return True
        else:
            node = list[index].split('$')[0]
            state = list[index].split('$')[1]
            if len(nodes)==0:
                nodes.append(node)
                states.append(state)
            else:
                for index2 in range (len(nodes)):
                    if node == nodes[index2]:
                        if state != states[index2]:
                            Flag=1
                            return True
                        # if same node and state, do nothing
                    else:
                        nodes.append(node)
                        states.append(state)

    if Flag==0:
        return False
    else:
        return "Flag=1"


def removedup(list1):    # keep only the smallest item(subset) in a list
    list2 = copy.copy(sorted(list1))
    discardlist =[]
    for i in range(0,len(list2)):
        item1=list2[i]
##        print 'item1:',item1
        for j in range(i+1,len(list2)):
            item2=list2[j]
##            print 'item2:',item2
            if item2 not in discardlist:
                item1s = set(item1)
                item2s = set(item2)
                if item1 == item2:
                    list1.remove(item2)
                    discardlist.append(item2)
##                    print 'remove item2 due to same:', item2

                else:
                    if item1s.issubset(item2s):
                        if item2 in list1:
                            list1.remove(item2)
                            discardlist.append(item2)
##                            print 'remove item2:', item2
                    elif item2s.issubset(item1s):
                        if item1 in list1:
                            list1.remove(item1)
                            discardlist.append(item1)
##                            print 'remove item1:', item1
##        print
##        print 'cyclelist:',list1

# test example:
##y = [['N6$0', 'N9$1'], ['N8$0', 'N6$0', 'N0$2', 'N1$1', 'N7$0', 'N8$0 AND N0$2', 'N3$1', 'N9$1', 'N5$1 AND N1$1', 'N1$1 AND N3$1', 'N5$1']]
##y = [[1,2,3],[1,3,4],[1,2,3,4],[1,2]]
##
##y = [['N0$1 AND N2$0', 'N1$2', 'N1$2 AND N0$1', 'N3$0', 'N0$1 AND N3$0', 'N4$0', 'N4$0 AND N3$0', 'N0$1', 'N2$0'], ['N4$1', 'N0$0'], ['N0$1 AND N3$0', 'N4$0 AND N3$0', 'N0$1 AND N2$0', 'N0$1', 'N4$0', 'N2$0', 'N1$2 AND N0$1', 'N1$2', 'N3$0']]
##
##removedup(y)
##
##print y



def removerep(cycles,mode=1):    # Mode1: keep only the cycles without repeated nodes in a list; Mode0: keep only cycles with all inputs of composite nodes present
    cycles1 = []
    for cycle in cycles:
        if mode==1:
            if not containrep(findinputs(cycle)):
                cycles1.append(cycle)
        elif mode==0:
            inputs = findinputs(cycle,0)
            Flag=0
            for item in inputs:
                if item not in cycle:
                    break
            else:
                cycles1.append(cycle)

    return cycles1
# test
##cycles = [['N0$1 AND N3$0', 'N2$0', 'N1$2 AND N2$0', 'N3$0'], ['N0$1 AND N3$0', 'N2$0', 'N1$0 AND N2$0', 'N3$0'], ['N0$0 AND N3$0', 'N2$1', 'N1$1 AND N2$1', 'N3$0'], ['N1$1 AND N2$0', 'N3$1', 'N0$0 AND N3$1', 'N2$0'], ['N1$0', 'N0$0'], ['N1$2 AND N2$1', 'N3$1', 'N3$1 AND N0$1', 'N1$2'], ['N1$2 AND N2$1', 'N3$1', 'N0$1 AND N3$1', 'N2$1'], ['N0$1', 'N3$0 AND N0$1', 'N1$1'], ['N3$1', 'N0$1 AND N3$1', 'N2$1', 'N1$0 AND N2$1'], ['N1$1 AND N2$1', 'N3$0', 'N3$0 AND N0$1', 'N1$1']]


def removenode(cycles,node):    # remove all cycles that contain cnode
    cycles1 = []
    for cycle in cycles:
        if node not in cycle:
            cycles1.append(cycle)
    return cycles1

def findcycle(cycles,node,input1=0,input2=0,mode=1):
    # return the cycles with a given node from a list of cycles. if input1 and input2 are given, it will return with cycles with input1 but without input2
    # mode=1 to find w/ input1 & w/o input2; mode=0 to find w/ both input1 and input2
    cycles1=[]
    for cycle in cycles:
        if node in cycle:
            if input1==0 and input2==0:
                cycles1.append(cycle)
            else:
                if input1 in findinputsstr(node):
                    if input1 in cycle:
                        cycles1.append(cycle)
                    else:
                        if mode==1:
                            if input1 in cycle and input2 not in cycle:
                                cycles1.append(cycle)
                        elif mode==0:
                            if input1 in cycle and input2 in cycle:
                                cycles1.append(cycle)

    return cycles1

def findcnode(cycles,Graph): # returns a list of cnodes in a list of cycles
    cnodes=[]
    for cycle in cycles:
        for node1 in cycle:
            if Graph.node[node1]['c']==1 and node1 not in cnodes:
                cnodes.append(node1)
    return cnodes

def getinput(list1):
    # return all inputs from a list of nodes
    nodelist=[]
    for node in list1:
        if node.count('AND')>=1:
            for node1 in node.split('AND'):
                if node1.strip() not in nodelist:
                    nodelist.append(node1.strip())
        elif node not in nodelist:
            nodelist.append(node)
    return nodelist

def checkreplist(list1, Graph,nodescan):
    # seems not working
    # check if two lists of virtual nodes has repeated between lists
##    print list1
    for node1 in list1:
        for expandednode1 in Graph.node[node1]['info']:
            # expanded node format [node#, state#]
            for state in nodescan[1][expandednode1[0]]:
##                print 'node and expandednode: ', node1, expandednode1, nodescan[1][expandednode1[0]], Graph.node[node1]['info'], state#, expandednode1[1] #, type(int(state)), type(expandednode1[1])
                if int(state) != expandednode1[1]:
                    for node2 in list1:
                        if [expandednode1[0],state] in Graph.node[node2]['info']:
##                            print Graph.node[node2]['info']
                            return True
    return False

def checkreplist1(list1,list2, Graph):
    # OLd version
    # check if two lists of virtual nodes has repeated between lists
    for node1 in list1:
        for node2 in list2:
            for expandednode1 in Graph.node[node1]['info']:
                for expandednode2 in Graph.node[node2]['info']:
                    if expandednode1[0] ==expandednode2[0] and expandednode1[1] != expandednode2[1]:
                        return True
    return False

def checkreplist2(list1,list2):
    # OLd version
    # check if two lists of virtual nodes has repeated between lists
##    print list1,list2
    for expandednode1 in list1:
        for expandednode2 in list2:
            for node1 in expandednode1:
                for node2 in expandednode2:
##                    print 'node1, node2:', node1,node2
                    if node1[0] == node2[0] and node1[1] != node2[1]:
                        return True
    return False

def union(cycles1, cycles2, Graph, nodescan, mode=1):
    # seems not working
    # merge a list of cycles with another list of cycles, without merging those in the same list. Mode=1: Resulting cycles with repeated nodes are discarded.
##    i=0
    cycles3=[]
    for cycle1 in cycles1:
        for cycle2 in cycles2:
##            if not checkreplist1(cycle1,cycle2,Graph):
                # if no repeated node, merge the cycles
            newcycle = list(set(cycle1+cycle2))
            if (newcycle not in cycles3) and not checkreplist(newcycle,Graph,nodescan):
                cycles3.append(newcycle)
    return cycles3

def union1(cycles1, cycles2, Graph, mode=1):
    # old version
    # merge a list of cycles with another list of cycles, without merging those in the same list. Mode=1: Resulting cycles with repeated nodes are discarded.
##    i=0
    cycles3=[]
    for cycle1 in cycles1:
        for cycle2 in cycles2:
            if not checkreplist1(cycle1,cycle2,Graph):
                # if no repeated node, merge the cycles
                newcycle = list(set(cycle1+cycle2))
                cycles3.append(newcycle)
    return cycles3

def convert_to_list(cycles, Graph):
    # convert a cycle of strings as nodes in a Graph to a list of numbers
    newcycle=[]
    for cycle in cycles:
        newnode=[]
        for node1 in cycle:
            newnode.append(Graph.node[node1]['info'])
        newcycle.append(newnode)
    return newcycle

def union2(cycles1, cycles2, Graph):
    # modified old version without using the graph
    # merge a list of cycles with another list of cycles, without merging those in the same list. Mode=1: Resulting cycles with repeated nodes are discarded.
##    i=0
    cycles3=[]
    list1 = convert_to_list(cycles1, Graph)
    list2 = convert_to_list(cycles2, Graph)
##    print 'lists',list1,list2
    for index1 in range(0, len(list1)):
        for index2 in range(0, len(list2)):
            if not checkreplist2(list1[index1], list2[index2]):
                # if no repeated node, merge the cycles
                newcycle = list(set(cycles1[index1]+cycles2[index2]))
                cycles3.append(newcycle)
    return cycles3

def plus(cycles1,cycles2):
    # returns all the elements in cycle1 or cycles2
    cycles3=cycles1
    for cycle2 in cycles2:
        if cycle2 not in cycles3:
            cycles3.append(cycle2)
    return cycles3

def exclude(cycles1,cycles2):
    # returns the elements in cycle1 that are not elements of cycles2
    cycles3=[]
    for cycle1 in cycles1:
        if cycle1 not in cycles2:
            cycles3.append(cycle1)
    return cycles3

def intersection(cycles1,cycles2):
    # returns the elements in both cycle1 and cycles2
    cycles3=[]
    for cycle1 in cycles1:
        if cycle1 in cycles2:
            cycles3.append(cycle1)
    return cycles3

def checkcnode(cycle,Graph):
    # return True if all cnodes' inputs are also present in the cycle
    for node1 in cycle:
        if Graph.node[node1]['c']==1:
##            print 'node1:',node1,Graph.node[node1]['info']
            for nodestate1 in Graph.node[node1]['info']:
##                print 'nodestate1:',nodestate1
                for node2 in cycle:
##                    print 'node2:',node2,Graph.node[node2]
                    if Graph.node[node2]['c']==0 and Graph.node[node2]['info'][0]==nodestate1:    #  Match. Proceed to the next input of the cnode.
##                        print 'match'
                        break
##                    print 'continue to next input'
                else:   # If no match after searching through all nodes, return False.
##                    print 'no match'
                    return False
    return True

def filtercnode(cycles,Graph):
    # keep only cycles with all inputs of its cnodes present
    newcycles=[]
    for cycle in cycles:
##        print 'cycle:',cycle
        if checkcnode(cycle,Graph):
            newcycles.append(cycle)
##            print 'newcycles:', newcycles
    return newcycles

def findcycle1(cycles, cnode, input1, Graph):
    # return the cycles with a given cnode and also with input1 from a list of cycles.
    newcycles=[]
    for cycle in cycles:
##        print 'cycle:',cycle,cnode
        if cnode in cycle:
##            print 'input',input1, Graph.node[cnode]['info']
            for node in cycle:
                if Graph.node[node]['c']==0 and input1 in Graph.node[node]['info']: # and input1 in Graph.node[cnode]['info']:
                    newcycles.append(cycle)
                    break
    return newcycles

def findcycle2(cycles, cnode, Graph):
    # return the cycles with a given cnode from a list of cycles.
    newcycles=[]
    for cycle in cycles:
##        print 'cycle:',cycle,cnode
        if cnode in cycle:
##            print 'input',input1, Graph.node[cnode]['info']
            for node in cycle:
                if Graph.node[node]['c']==0 :
                    newcycles.append(cycle)
                    break
    return newcycles

def filtercycle(cycles, Graph):
    # TBD add a checker that filters out cycles with composite nodes such that it cannot be part of a stable motif
    tempcycles = []
    newcycles = []
    for cycle in cycles:
        # 1. For each cycle with a composite node it checks if the complimentary node of each of its inputs is in the cycle. If that is the case,
        #    then that composite node cannot form part of a stable SCC and it is removed
        # 2. For each cycle with more than a composite node it checks if the inputs necessary for one of the composites is the opposite of the ones
        #    necessary for another one in that cycle. If that is the case then this cycle can never be part of a stable SCC and it is removed
        inputs = getinput(cycle)
        if not containrep(inputs):
            tempcycles.append(cycle)

    # 3. checks if joining all the cycles containing a composite node has all the inputs of said composite node. If this is not the case,
    #    then this composite node can never be part of a stable SCC and so we remove those cycles
    cnodes=findcnode(tempcycles,Graph)
    for cnode in cnodes:
        cnodecycles = findcycle2(tempcycles, cnode, Graph)
        total_nodes=[]
        for cycle1 in cnodecycles:
            for node in cycle1:
                if node not in total_nodes:
                    total_nodes.append(node)
        if not checkcnode(getinput(total_nodes),Graph):
            for item in cnodecycles:
                tempcycles.remove(item)

    return tempcycles

def candidate(cycles,Graph,nodescan):  # return a list of SM candidates from a list of cycles
    cycles_a = copy.copy(cycles)
    a = copy.copy(cycles)
##    a = filtercycle(cycles,Graph)
##    if cycles_a != a:
##        print cycles_a
##        print a
##    print cycles_a
##    print a
    SMcandidates = filtercnode(a,Graph)
##    print 'SMcandidates:',SMcandidates

    cnodes=findcnode(cycles,Graph)
##    print 'cnodes:', cnodes
    inputs = ['']*len(cnodes)

    for cindex in range (len(cnodes)):# merge cycles that share the same composite node
        inputs[cindex] = Graph.node[cnodes[cindex]]['info']
##        print 'cnode and inputs:',cnodes[cindex], inputs[cindex]
        candidates = findcycle1(a,cnodes[cindex],input1=inputs[cindex][0],Graph=Graph) #
##        print 'candidates:',candidates,cnodes[cindex],inputs[cindex][0]
        # return the cycles with a given cnode and given input of the cnode from a list of cycles.

##        inputs[cindex] = findinputsstr(cnodes[cindex]) #
##        candidates = findcycle(a,cnodes[cindex],input1=inputs[cindex][0])

        for inputindex in range (1,len(inputs[cindex])):
##            print 'input:',inputs[cindex][inputindex]
            ab= candidates
            c = findcycle1(cycles_a,cnodes[cindex],input1=inputs[cindex][inputindex],Graph=Graph)
##            c = findcycle(cycles_a,cnodes[cindex],input1=inputs[cindex][inputindex])
##            print inputs[cindex][inputindex],'ab:',ab,'c:',c

##            cycles1 = ab.difference(c)
##            cycles2 = c.difference(ab)
            cycles1 = exclude(ab,c)
            cycles2 = exclude(c,ab)

##            newcycles = union(cycles1,cycles2,Graph,nodescan)# found the 'union' of the above cycles
            newcycles = union2(cycles1,cycles2,Graph)# found the 'union' of the above cycles
##            cycles3 = ab.intersection(c)
            cycles3 = intersection(ab,c)
##            print 'cycle1:{}, cycle2:{},newcycles:{},cycles3:{}'.format(cycles1,cycles2,newcycles,cycles3)

            # add cycles3, the cycles with both inputs A and B present
##            candidates = list(set(tuple(cycles3))+set(tuple(newcycles)))
            candidates = plus(cycles3,newcycles)

        for candidate in candidates:  # add the unions to the candidate pool
            if candidate not in SMcandidates:
                SMcandidates.append(candidate)
                cycles_a.append(candidate)

        # remove cycles with cnodes[cindex] that are not SM candidates (does not include all inputs for this cnode), add SM candidates
        a = removenode(a,cnodes[cindex])
        a = plus(a,SMcandidates)
##        a = list(set(tuple(a))+set(tuple(SMcandidates)))
##        print 'a=',a

    SMcandidates = removerep(SMcandidates,mode=0)
##    print 'SMcandidates:', SMcandidates
    # keep only the smallest SCCs
    removedup(SMcandidates)

    return SMcandidates

# test example
##cycles = ['N4$0', 'N1$2 AND N4$0', 'N2$1', 'N2$1 AND N1$2']
##['N4$0', 'N1$2 AND N4$0', 'N2$1', 'N3$1 AND N2$1', 'N1$2', 'N2$1 AND N1$2']
##['N2$1', 'N3$1 AND N2$1', 'N1$2', 'N1$2 AND N4$0']
##
##x = candidate(cycles)
##print x

##x = findcycle(a,'N2$1 AND N3$1',input1=inputs[cindex][0])
##print x

def siblingnode(nodex, nodelist, nodestates):
##    print vnode, nodelist,nodestates
    # returns all sibling nodes of a node from a nodelist
    sibling_nodelist =[]
    if nodex.count('AND')>=1:
        vnodes = nodex.split("AND")
    else:
        vnodes= [nodex]
    for vnode in vnodes:
        node = vnode.split("$",1)[0].strip()
        state = vnode.split("$",1)[1].strip()
        for state1 in nodestates[nodelist.index(node)]:
            if state1 != state:
                vnode1 = node + '$' + state1
                sibling_nodelist.append(vnode1)
##    print sibling_nodelist
    return sibling_nodelist

#test:

##y = [['N0', 'N1', 'N2', 'N3', 'N4', 'N5'], [['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1', '2'], ['0', '1']]]
##y = [['N0', 'N1', 'N2'], [['0', '1'], ['0', '1'], ['0', '1']]]
##nodex = 'N0$1 AND N1$1'
##
##x = siblingnode(nodex,y[0],y[1])
##
##print x

def checkrep(nextnode,path,Graph):
    if len(path)>= 2 and Graph!=[]:
##        print 'nextnode:',nextnode, Graph.node[nextnode], 'path',path
        for item1 in Graph.node[nextnode]['info']:
##            print 'item1:',item1
            for item3 in path:
##                print 'item3',item3
                for item2 in Graph.node[item3]['info']:
##                    print 'item2:',item2
                    if item1[0] == item2[0] and item1[1] != item2[1]:
##                        print item1,item2
                        return True
    return False

def simple_cycles_SM(G,lengthlimit=30,timelimit=0, nodelist=[], nodestates=[],Graph=[]):
    # copied from nx.simple_cycles(G). finds cycles that does not have repeated nodes.
    # TBD: setting upper bound of cycles

    def _unblock(thisnode,blocked,B):
        stack=set([thisnode])
        while stack:
            node=stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

##    start_time = time.time()
    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    subG = type(G)(G.edges_iter()) # save the actual graph so we can mutate it here
                              # We only take the edges because we do not want to
                              # copy edge and node attributes here.
    sccs = list(nx.strongly_connected_components(subG))
    while sccs:
        scc=sccs.pop()
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path=[startnode]
        blocked = set() # vertex: blocked from search?
        closed = set() # nodes involved in a cycle
        blocked.add(startnode)
        B=collections.defaultdict(set) # graph portions that yield no elementary circuit
        stack=[ (startnode,list(subG[startnode])) ]  # subG gives component nbrs
##        print startnode,stack
        while stack:
            thisnode,nbrs = stack[-1]
##            print 'thisnode:',thisnode,nbrs
            # filter out nodes in nbrs that are repeated
            if nbrs:
                nextnode = nbrs.pop()
##                if startnode == 'N0$1':
##                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
##                print 'nextnode:{},blocked:{}'.format(nextnode,blocked),len(blocked)
##                print 'path:',path,'nextnode:',nextnode
##                print 'stack:', stack
#                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
#                    f=raw_input("pause")
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
##                    print "Found a cycle",path,closed
                elif nextnode not in blocked:
                    path.append(nextnode)
##                    print 'path:',path,findinputs(path)
                    if len(path)>=lengthlimit or checkrep(nextnode,path[:-1:],Graph):
                        closed.update(path)
                        path.remove(nextnode)
                    else:
                        stack.append( (nextnode,list(subG[nextnode])) )
                        closed.discard(nextnode)
                        blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode,blocked,B)
                else:
                    for nbr in subG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1]==thisnode
                path.pop()
        # done processing this node
        subG.remove_node(startnode)
        H=subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(list(nx.strongly_connected_components(H)))

# test example
##G = nx.DiGraph([('A$0', 'A$1'),('B$0', 'A$1'), ('A$1', 'B$1'), ('B$1', 'A$0'), ('B$1', 'A$1'), ('A$1', 'A$1'), ('B$1', 'B$0')])

##G = nx.DiGraph([('N4$0','N3$1'), ('N3$1','N3$1 AND N2$1'), ('N3$1 AND N2$1','N1$2'), ('N1$2','N1$2 AND N4$0'), ('N1$2 AND N4$0','N2$1'), ('N2$1', 'N2$1 AND N1$2'),('N2$1 AND N1$2','N4$0')])
##    print ExpandedG.nodes()
##    # drawing the graph
##    pos=nx.spring_layout(ExpandedG)
##    nx.draw(ExpandedG, with_labels = True)
##    plt.show()print list(simple_cycles_SM(G))
##print list(simple_cycles_SM(G))


## print list(nx.simple_cycles(G))
##['N4$0', 'N3$1', 'N3$1 AND N2$1', 'N1$2', 'N1$2 AND N4$0', 'N2$1', 'N2$1 AND N1$2']
##pos=nx.spring_layout(G)
##nx.draw(G, with_labels = True)
##plt.show()

def simple_cycles(G):
    def _unblock(thisnode,blocked,B):
        stack=set([thisnode])
        while stack:
            node=stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    subG = type(G)(G.edges_iter()) # save the actual graph so we can mutate it here
                              # We only take the edges because we do not want to
                              # copy edge and node attributes here.
    sccs = list(nx.strongly_connected_components(subG))
    while sccs:
        scc=sccs.pop()
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path=[startnode]
        blocked = set() # vertex: blocked from search?
        closed = set() # nodes involved in a cycle
        blocked.add(startnode)
        B=collections.defaultdict(set) # graph portions that yield no elementary circuit
        stack=[ (startnode,list(subG[startnode])) ]  # subG gives component nbrs
        while stack:
            thisnode,nbrs = stack[-1]
            if nbrs:
                nextnode = nbrs.pop()
##                if startnode == 'N0$1':
##                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
#                    f=raw_input("pause")
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
##                    if startnode == 'N0$1':
##                        print "Found a cycle",path,closed
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append( (nextnode,list(subG[nextnode])) )
                    closed.discard(nextnode)
                    blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode,blocked,B)
                else:
                    for nbr in subG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1]==thisnode
                path.pop()
        # done processing this node
        subG.remove_node(startnode)
        H=subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(list(nx.strongly_connected_components(H)))


def findoscillation(ExpandedG, stablemotifs):  # return a list of oscillation candidates from the expanded graph

# conditions:
# (1) the SCC must contain at least 2 virtual nodes of every normal/orginal node
# (2) if the SCC contains a composite node, all its input nodes must also be part of the SCC
# (3)* (not sure if true for multi-level) the oscillating component must not contain stable motifs without composite nodes
    oscillations =[]
    SCCs=[]
    newSCCs=[]
    for item in list(nx.strongly_connected_components(ExpandedG)):
        # filter out single nodes
        if len(item)>1:
            newSCCs.append(list(item))
##            print newSCCs
##    SCCs=temp
    # filter out non-source SCC
    for item1 in newSCCs:
        Flag0=0
        for item2 in newSCCs:
            if item2 != item1:
                if nx.has_path(ExpandedG,list(item2)[0],list(item1)[0]):
                    Flag0=1
        if Flag0 ==0:
            SCCs.append(list(item1))
##    print SCCs

    while SCCs != []:
##        print
##        print 'SCCs:',SCCs
        obj = SCCs.pop(0) # pop up an SCC (list of nodes)
##        print 'obj=',obj
        ExpandedG1 = nx.DiGraph(ExpandedG.subgraph(obj))
##        print 'nodes:', nx.nodes(ExpandedG1), type(ExpandedG1)
##        print 'edges:', nx.edges(ExpandedG1)
        compositenodelist =findinputs(obj,inc_normal=0,mode=0)
        temp=[]
        for item in compositenodelist[1]:
            if item not in temp:
                temp.append(item)
        compositenodelist[1] = temp

##        print 'compositenodelist:',compositenodelist
        # find all composite nodes in obj that do not have all their input nodes in this SCC; remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC
##        print
        Flag1=0
        # check if the SCC satisfies (2): If so, proceed to 3; if not, remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC to stack
        for i in range(0,len(compositenodelist[0])):
            for input in compositenodelist[1][i]:
##                print 'input:',input,i,compositenodelist[1]
                if input not in obj:
                    # remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC
##                    print 'removing composite node: ', compositenodelist[0][i]
                    ExpandedG1.remove_node(compositenodelist[0][i])
##                    print 'nodes:', nx.nodes(ExpandedG1)
##                    print 'edges:', nx.edges(ExpandedG1)
                    newSCCs=[]
                    for item in list(nx.strongly_connected_components(ExpandedG1)):
                        # filter out single nodes
                        if len(item)>1:
                            newSCCs.append(list(item))
##                            print newSCCs
                    SCCs += newSCCs
##                    print list(nx.strongly_connected_components(ExpandedG1))
##                    print 'added SCCs',newSCCs
##                    print 'SCCs:', SCCs
                    Flag1=1
                    break
            if Flag1==1:
                break

        if Flag1==0:
        #3. check if the SCC contains at least 2 virtual nodes of every normal/orginal node: if so, proceed to 4; if not, remove the corresponding virtual nodes, then add sub-SCCs within this SCC
            unrepeated = unrepeatednode(obj)
##            print unrepeated
            if unrepeated != []:
##                print 'removing unrepeated nodes: ', unrepeated
                for item in unrepeated:
                    ExpandedG1.remove_node(item)
                Flag1=1
                newSCCs=[]
                for item in list(nx.strongly_connected_components(ExpandedG1)):
                    # filter out single nodes
                    if len(item)>1:
                        newSCCs.append(list(item))
                SCCs += newSCCs

        # 4 & 5. check if the SCC contains a stable motif without a composite node, if so, remove the stable motif, then go to 1; if not, the SCC is an oscillating candidate
        # suspected: incorrect in Multi-level?
        if Flag1==0:
            simpleSM=[]
            for sm in stablemotifs:
##                print sm
                Flag2=0
                # filter sm s.t. only sms w/o composite node
                for item in sm:
##                    print item
                    if item.count('AND')==1:
                        Flag2=1
                        break
                if Flag2==0:
                    simpleSM.append(sm)
##            print simpleSM

            for sm in simpleSM:
##                print sm,obj
                if set(sm) & set(obj) == set(sm):
                # if the SCC contains a stable motif without a composite node, remove the stable motif
                    Flag1=1
                    for item in sm:
                        if item in ExpandedG1:
                            ExpandedG1.remove_node(item)
                    newSCCs=[]
                    for item in list(nx.strongly_connected_components(ExpandedG1)):
                        # filter out single nodes
                        if len(item)>1:
                            newSCCs.append(list(item))
                    SCCs += newSCCs

        if Flag1==0:
            oscillations.append(obj)
##        print
    return oscillations

# test examples:
##y = ['A$0* = B$0 OR (C$1 AND B$1)', 'A$1* = B$1 AND C$0', 'A$2* = B$2', 'B$0* = C$0 OR A$0', 'B$1* = C$1 AND A$1', 'B$2* = C$1 AND A$2', 'C$0* = A$0', 'C$1* = A$1 OR A$2']

##z = list(nx.strongly_connected_components(ExpandedG))
##x = findoscillation(y)

##print x


def findstablenodes(SM,mode=1): # from a single SM candidate or oscillating motif, find all nodes in it, with corresponding values.
    # Returns a list of two lists: 1. stablenodes; 2. values
    # if input is 'None' or '[]', i.e. no Stable Motif, return 'None'
    # if input is an oscillation , the value for oscillating nodes will be '@'
    if SM== 'None':
        return 'None'
##    print len(SM)
    nodes=[]
    states=[]
    stablenodes=[]
    values=[]
    Error=0
##    count1=0
##    count2=0
    for i in range (0,len(SM)):
##        print
##        print 'i={}, count={}'.format(i,count1+count2)
        x = findinputsstr(SM[i])
##        print 'x=',x
        # finding all nodes and values from a set of input nodes
        for j in range (0,len(x)):
##            print 'x[{}]= {}'.format(j,x[j])
            node1 = x[j].split("$")[0].strip()
            state1 = x[j].split("$")[1].strip()
            if node1 not in nodes:
                nodes.append(node1)
                states.append(state1)
                a = node1
                a += '$'
                a += state1
                stablenodes.append(a)
                values.append(1)
##                count1 += 1

            else:       # if the same node but different state, then enter as oscillation
                for k in range (0, len(nodes)):
                    if node1 == nodes[k]:
                        if state1 != states[k]:
                            # oscillation
                            a = node1
                            a += '$'
                            a += state1
                            if a not in stablenodes:
##                                count2 += 1
                                nodes.append(node1) # not sure if right here
                                states.append(state1)
##                                print node1,state1,states[k]
                                stablenodes.append(a)
                                values.append('@')
                                y= nodes[k] + '$' + str(states[k])
                                values[stablenodes.index(y)]='@'
##        print stablenodes,values

    if mode==0:
        return [nodes,states,Error]
    else:
##        print 'stablenodes:',stablenodes,values
        return [stablenodes,values]

#TBD: The result will include all virtual nodes of the same original node. e.g if the stable motif contains A$1, then A$0, A$2, etc.will all gets 0



# test

##obj = [['N0$0* =N0$0', 'N0$1* =N0$1', 'N1$0* = 0', 'N1$1* = 1'], [['N0$1'], ['N1$1']]]
##obj = [['N0$0* =(N8$0 AND N2$1) OR (N8$0 AND N2$2)', 'N0$1* =(N8$0 AND N2$0) OR (N8$1 AND N2$0) OR (N8$1 AND N2$1) OR (N8$1 AND N2$2) OR (N8$2 AND N2$1) OR (N8$2 AND N2$2)', 'N0$2* =(N8$2 AND N2$0)', 'N1$0* =(N6$1 AND N9$1)', 'N1$1* =(N6$0 AND N9$0) OR (N6$1 AND N9$0) OR (N6$2 AND N9$2)', 'N1$2* =(N6$0 AND N9$1) OR (N6$0 AND N9$2) OR (N6$1 AND N9$2) OR (N6$2 AND N9$0) OR (N6$2 AND N9$1)', 'N2$0* =(N8$0 AND N3$0) OR (N8$0 AND N3$2) OR (N8$1 AND N3$0) OR (N8$1 AND N3$1) OR (N8$2 AND N3$2)', 'N2$1* =(N8$0 AND N3$1) OR (N8$1 AND N3$2)', 'N2$2* =(N8$2 AND N3$0) OR (N8$2 AND N3$1)', 'N3$0* =(N6$0 AND N0$0)', 'N3$1* =(N6$1 AND N0$0) OR (N6$1 AND N0$1) OR (N6$2 AND N0$1) OR (N6$2 AND N0$2)', 'N3$2* =(N6$0 AND N0$1) OR (N6$0 AND N0$2) OR (N6$1 AND N0$2) OR (N6$2 AND N0$0)', 'N4$0* =(N5$1 AND N7$0) OR (N5$1 AND N7$2) OR (N5$2 AND N7$2)', 'N4$1* =(N5$0 AND N7$0) OR (N5$0 AND N7$1) OR (N5$0 AND N7$2) OR (N5$1 AND N7$1) OR (N5$2 AND N7$0) OR (N5$2 AND N7$1)', 'N5$0* =(N2$1 AND N3$2)', 'N5$1* =(N2$0 AND N3$1) OR (N2$1 AND N3$0) OR (N2$1 AND N3$1) OR (N2$2 AND N3$2)', 'N5$2* =(N2$0 AND N3$0) OR (N2$0 AND N3$2) OR (N2$2 AND N3$0) OR (N2$2 AND N3$1)', 'N6$0* =(N3$0 AND N5$1) OR (N3$1 AND N5$0) OR (N3$2 AND N5$0) OR (N3$2 AND N5$1)', 'N6$1* =(N3$0 AND N5$0) OR (N3$1 AND N5$2)', 'N6$2* =(N3$0 AND N5$2) OR (N3$1 AND N5$1) OR (N3$2 AND N5$2)', 'N7$0* =(N3$0 AND N1$2) OR (N3$2 AND N1$0) OR (N3$2 AND N1$1)', 'N7$1* =(N3$0 AND N1$1)', 'N7$2* =(N3$0 AND N1$0) OR (N3$1 AND N1$0) OR (N3$1 AND N1$1) OR (N3$1 AND N1$2) OR (N3$2 AND N1$2)', 'N8$0* =(N4$0 AND N1$0) OR (N4$0 AND N1$1) OR (N4$1 AND N1$0) OR (N4$1 AND N1$2)', 'N8$1* =(N4$1 AND N1$1)', 'N8$2* =(N4$0 AND N1$2)', 'N9$0* =(N3$0 AND N4$0) OR (N3$1 AND N4$1) OR (N3$2 AND N4$0) OR (N3$2 AND N4$1)', 'N9$1* =(N3$0 AND N4$1)', 'N9$2* =(N3$1 AND N4$0)'], [['N5$1 AND N7$2', 'N4$0', 'N3$0 AND N4$0', 'N9$0', 'N6$1 AND N9$0', 'N1$1', 'N4$0 AND N1$1', 'N3$2 AND N1$1', 'N7$0', 'N5$2 AND N7$0', 'N4$1', 'N4$1 AND N1$1', 'N8$1', 'N3$0 AND N4$1', 'N9$1', 'N6$1 AND N9$1', 'N1$0', 'N8$0', 'N8$0 AND N2$2', 'N0$0', 'N6$1 AND N0$0', 'N3$1', 'N8$1 AND N3$1', 'N3$1 AND N4$1', 'N3$1 AND N4$0', 'N9$2', 'N8$0 AND N3$1', 'N2$0 AND N3$1', 'N5$1', 'N3$1 AND N5$1', 'N3$2 AND N5$1', 'N6$0', 'N6$0 AND N9$0', 'N6$0 AND N9$1', 'N6$0 AND N9$2', 'N6$0 AND N0$0', 'N3$0', 'N3$0 AND N1$1', 'N7$1', 'N8$1 AND N3$0', 'N3$0 AND N5$1', 'N8$0 AND N3$0', 'N6$0 AND N0$2', 'N3$2', 'N8$1 AND N3$2', 'N2$1', 'N2$1 AND N3$1', 'N2$1 AND N3$0', 'N8$0 AND N2$1', 'N2$1 AND N3$2', 'N5$0', 'N3$2 AND N5$0', 'N3$1 AND N5$0', 'N3$0 AND N5$0', 'N8$0 AND N3$2', 'N2$0', 'N2$0 AND N3$0', 'N2$0 AND N3$2', 'N5$2', 'N3$1 AND N5$2', 'N6$1', 'N6$1 AND N9$2', 'N3$0 AND N5$2', 'N3$2 AND N5$2', 'N6$2', 'N6$2 AND N9$2', 'N6$2 AND N0$0', 'N6$2 AND N9$0', 'N6$2 AND N9$1', 'N1$2', 'N4$0 AND N1$2', 'N8$2', 'N8$2 AND N3$2', 'N8$2 AND N3$0', 'N8$2 AND N3$1', 'N2$2', 'N2$2 AND N3$1', 'N2$2 AND N3$0', 'N2$2 AND N3$2', 'N8$2 AND N2$2', 'N8$2 AND N2$1', 'N3$0 AND N1$2', 'N4$1 AND N1$2', 'N8$0 AND N2$0', 'N0$1', 'N6$0 AND N0$1', 'N6$2 AND N0$1', 'N6$1 AND N0$1', 'N8$2 AND N2$0', 'N0$2', 'N6$2 AND N0$2', 'N6$1 AND N0$2', 'N3$2 AND N1$2', 'N3$0 AND N1$0', 'N7$2', 'N5$2 AND N7$2', 'N3$2 AND N1$0', 'N5$1 AND N7$0']]]

##print obj[1][len(obj[1])-1]
##stablenodes = findstablenodes(obj[1][len(obj[1])-1])

##x = ['B$2 AND C$2','B$0', 'C$1','B$1','B$0 AND B$1','B$2']
##
##stablenodes = findstablenodes(x)
##print stablenodes


##SMcandidates = candidate(cycles)
##
##
##print "SM candidates in the expanded network:"
##for item in SMcandidates:
##    print item

##SMcandidates = candidate(cycles)


##print "SM candidates in the expanded network:"
##for item in SMcandidates:
##    print item
