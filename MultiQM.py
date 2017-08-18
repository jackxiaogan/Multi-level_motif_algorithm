#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Xiao Gan
#
# Created:     30/10/2016
# Copyright:   (c) Xiao Gan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

##import time
import itertools
##import functions
##import Booleanops
##import Simulation
##import Reduction


def merge(list1, levels):
    # one-step merge: input is a list of all input combination (that yield a particular value in the function). Note the bracketed part of interpretation is not mathematically neccesary
    # levels is a list of levels correspondent to each node in the list
    # !! queston: do I need to consider the 'zeroes' list? For now I am trying the version without considering them
    group=[]
    leftovers=list(list1)
    newlist=[]
    # group the list according to how many 'zeroes' there are.
    for i in range (0,(len(list1[0])+1)):
        group.append([])
    for item in list1:
        group[len(list1[0])-item.count('0')].append(item)
##    print group


    # compare inter-group-wise: if difference =1: access the total state number of the difference node: check if the others are in the group
    for i in range(0, (len(group)-1)):
        for x1 in group[i]:
##            print 'x1=',x1
            for x2 in group[i+1]:
##                print 'x2=',x2
                Flag1=0 # mark number of differences
                # if difference =1: check the rest
                for j in range (0,len(x1)):
                    if x1[j]!=x2[j]:
                        dif=j   # record the different node
                        Flag1+=1
                    if Flag1>=2:
                        break
                if Flag1==1:
                    # access the correspondent list, then check the rest
                    for level in levels[dif]:
                        if level!=0:
##                            print levels[dif]
                            # create a combi, and check if it is in group[i+1]
                            target = ''
                            for k in range(0,len(x1)):
                                if k==dif:
                                    target += str(level)
                                else:
                                    target += x1[k]
##                            print 'target=',target
                            if target !=x1 and target not in group[i+1]:
                                break
                    else:
                        # merge. create a new list of newly-formed minterms.
##                        print 'start merging'
                        target = ''
                        for k in range(0,len(x1)):
                            if k==dif:
                                target += 'X'
                            else:
                                target += x1[k]
##                            print 'merging target=',target
                        if target not in newlist:
                            newlist.append(target)
                        # mark the merged nodes (remove them from the leftovers list)
                        if x1 in leftovers:
                            leftovers.remove(x1)
                        if x2 in leftovers:
                            leftovers.remove(x2)

    return [leftovers,newlist]

# test example:
##t1= time.time()
##a = ['002','011','012','020','022','100','102','110','120','122']
##a = [('0','0','2'),('0','1','1'),('0','1','2'),('0','2','0'),('0','2','2'),('1','0','0'),('1','0','2'),('1','1','0'),('1','2','0'),('1','2','2')]

##x= merge(a,[[0,1],[0,1,2],[0,1,2]])
##x = merge(['00', '01', '11'],[['0', '1', '2'], ['0', '1']])
##print x
##print("--- %s seconds ---" % (time.time() - t1))


def readfunc(function, fullnodelist, fullnodestates):
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
                statelist.append(fullnodestates[fullnodelist.index(node)])

    return [nodelist,statelist]


# test example:
##t1 = time.time()
##y = Reduction.to_list('toy_example1.txt')
##print y
##x = Simulation.nodescan(y,mode=1)
##print x
##z = readfunc(y[4],x[0],x[1])
##print y[4]

##a=['N0', 'N1', 'N2', 'N3', 'N4']
##b=[['0', '1', '2'], ['0', '1', '2'], ['0', '1', '2'], ['0', '1', '2'], ['0', '1', '2']]
##str1 = 'N0$0* =(N2$0 AND N1$1 AND N4$0) OR (N2$1 AND N1$0 AND N4$0) OR (N2$1 AND N1$1 AND N4$0) OR (N2$1 AND N1$1 AND N4$2) OR (N2$1 AND N1$2 AND N4$0) OR (N2$2 AND N1$0 AND N4$2) OR (N2$2 AND N1$1 AND N4$1) OR (N2$2 AND N1$2 AND N4$0) OR (N2$2 AND N1$2 AND N4$1)'
##z = readfunc(str1,a,b)
##print 'z=',z

##print("--- %s seconds ---" % (time.time() - t1))

def to_truthtable(function, fullnodelist, fullnodestates):
    # return a list of all input combination that yield a particular value in the function.
    # 'fullnodelist' and 'fullnodestates' are all nodes in the network with their correspondent levels

    resultlist =[]
    nodelist =[]
    levellist =[]
    # scan nodes of the function
##    function1 = Booleanops.convert(function,mode=1,outputnode=1)
##    print function,'/', fullnodelist,'/', fullnodestates
    x = readfunc(function, fullnodelist, fullnodestates)
##    print fullnodelist,fullnodestates
##    print 'x=',x
    for i in range (0,len(x[0])):
        # exaustively simulate then evaluate the result of all input combinations.
        # access the full states of this node
        nodelist.append(x[0][i])
##        print 'index=', fullnodelist.index(x[0][i])
        levellist.append(fullnodestates[fullnodelist.index(x[0][i])])
##    print list1
    list1 = list(itertools.product(*levellist))
##    print list1
    # all combination/products of states
##    print
    if '=' in function:
        function1 = function.split("=",1)[1].strip()
    else:
        function1 = function

    # evaluate each combination, put the combis that yield '1' in result list. Put the nodes the combination represents and its levels in nodelist and levellist
    for combi in list1:
        str1 = function1
##        print 'combi=',combi
##        print len(combi)
        for i in range(0,len(combi)):
        # replace occurences of state nodes with '1's and '0's
        # enumerate a state for this node: correspondent state node =>1, othere nodes =>0
##            print nodelist[i],levellist[i]
            ON = str(nodelist[i]) + '$' + str(combi[i])
##            print 'ON=',ON
            str1 = str1.replace(ON,'1')
            for state in levellist[i]:
                if str(state) != str(combi[i]):
                    OFF = str(nodelist[i]) + '$' + str(state)
##                    print 'OFF=',OFF
                    str1 = str1.replace(OFF,'0')
        str1 = str1.replace('OR','|')
        str1 = str1.replace('AND','&')
        str1 = str1.replace('NOT','~')
##        print str1
        if eval(str1):
            str2=''
            for item in combi:
                str2 += str(item)
            resultlist.append(str2)
    # If evaluation result= true, add the combi into result list

    return [resultlist,nodelist,levellist]

# test example:
##y = Reduction.to_list('toy_example1.txt')
##print 'y=',y
##x = Simulation.nodescan(y,mode=1)
##print 'x=',x
##

##z = to_truthtable(y[0],x[0],x[1])

##fullnodelist = ['PMV', 'Cac', 'CaATPase', 'Kout', 'Kc', 'Kv', 'KEV', 'SO']
##fullnodestates = [['0', '2', '1'], ['1', '0'], ['1', '0'], ['1', '0'], ['0'], ['0'], ['0'], ['1']]
##function = '(Cac$0 AND KEV$0 AND PMV$0 AND PMV$1) OR (Cac$0 AND KEV$0 AND PMV$0 AND PMV$2) OR (Cac$1 AND KEV$0 AND PMV$0 AND PMV$1) OR (Cac$1 AND KEV$0 AND PMV$0 AND PMV$2)'
##
##z = to_truthtable(function, fullnodelist, fullnodestates)
##print 'z=',z



def translateqm(qmset,inputs,mode=0):
    # translate the result of multiqm to readable function (e.g. '21X0' to 'N1$2 and N2$1 and N4$0')
    lst = list(qmset)
    result=''
##    inputs.reverse()
    # return 'zero' and 'one'
    if lst==[]:
        return '0'
    if len(lst)==1 and not (any(char.isdigit() for char in lst[0])):
        return '1'
    for i in range (0,len(lst)):
        result += '('
        for j in range (0,len(lst[i])):
            if lst[i][j].isdigit():
                result += str(inputs[j]) + '$' + lst[i][j]
                if mode ==0:
                    result += ' AND '
                else:
                    result += ' & '
##            elif lst[i][j]=='0':
##                if mode ==0:
##                    result += 'NOT '
##                else:
##                    result += '~ '
##                result += str(inputs[j])
##                if mode ==0:
##                    result += ' AND '
##                else:
##                    result += ' & '

        if mode==0:
            result = result[0:len(result)-5]
        else:
            result = result[0:len(result)-3]
        result = result.strip()

        result += ')'
        if mode ==0:
            result += ' OR '
        else:
            result += ' | '

    if mode ==0:
        result = result[0:len(result)-4]
    else:
        result = result[0:len(result)-3]
    return result.strip()


# test example:

##qmset= ['0X2', 'X02', 'X20', '1X0', 'X22']
##inputs = ['A','B','C']
##x = translateqm(qmset, inputs)
##print x

def qm(function, fullnodelist, fullnodestates):
    # main qm function
##    print function, fullnodelist, fullnodestates
    x = to_truthtable(function, fullnodelist, fullnodestates)
##    print 'x=',x
    if x[0] == []:
        return '0'
    else:
        y = merge(x[0], x[2])
        # iteratively merge until can be done no more
##        print 'y1=',y
        qmset=y[0]
        while y[1] != []:
##            print 'qmset',qmset
            y = merge(y[1], x[2])
##            print 'y=',y
            qmset += y[0]
##        print y
##        print qmset
##        return
        return translateqm(qmset,x[1],mode=0)




# test example

##fullnodelist = ['x0','x1','x2','x3']
##fullnodestates = [['0','1']]*len(fullnodelist)
##function = '(x3$0 AND x2$0 AND x0$0) OR (x3$0 AND x2$1 AND x1$0 AND x0$1) OR (x3$0 AND x2$1 AND x1$1 AND x0$1) OR (x3$0 AND x2$1 AND x1$1 AND x0$0) OR (x3$1 AND x2$0 AND x1$0 AND x0$0) OR (x3$1 AND x2$0 AND x1$0 AND x0$1) OR (x3$1 AND x2$0 AND x1$1 AND x0$0) OR (x3$1 AND x2$0 AND x1$1 AND x0$1) OR (x3$1 AND x2$1 AND x1$0 AND x0$0) OR (x3$1 AND x2$1 AND x1$1 AND x0$0) '
##function = 'x1$1 AND x2$1 OR x3$1 AND x2$0'

##fullnodelist = ['PMV', 'Cac', 'CaATPase', 'Kout', 'Kc', 'Kv', 'KEV', 'SO']
##fullnodestates = [['0', '2', '1'], ['1', '0'], ['1', '0'], ['1', '0'], ['0'], ['0'], ['0'], ['1']]
##function = '(Cac$0 AND KEV$0 AND PMV$0 AND PMV$1) OR (Cac$0 AND KEV$0 AND PMV$0 AND PMV$2) OR (Cac$1 AND KEV$0 AND PMV$0 AND PMV$1) OR (Cac$1 AND KEV$0 AND PMV$0 AND PMV$2)'
##
##words & function: <N4$1* =N2$0 OR N2$1>, <)> ['N2', 'N3', 'N4'] [['0', '1'], ['0', '1'], ['1']]
##z = qm(function, fullnodelist, fullnodestates)
##z = qm('N4$1* =N2$0 OR N2$1', ['N2', 'N3', 'N4'],[['0', '1'], ['0', '1'], ['1']])
##z= qm ('N0$0* =(N3$0 AND N1$0) OR (N3$0 AND N1$2) OR (N3$1 AND N1$0) OR (N3$1 AND N1$2)', ['N0', 'N1', 'N2', 'N3', 'N4'], [['0', '1'], ['0', '1', '2'], ['0', '1'], ['0', '1'], ['0', '1', '2']])
##print z



# more tests
##t1 = time.time()
##import Reduction
##import Simulation
##y = Reduction.to_list('toy_example1.txt')
##print 'y=',y
##y=['N0$0* =(N2$0 AND N1$1 AND N4$0) OR (N2$1 AND N1$0 AND N4$0) OR (N2$1 AND N1$1 AND N4$0) OR (N2$1 AND N1$1 AND N4$2) OR (N2$1 AND N1$2 AND N4$0) OR (N2$2 AND N1$0 AND N4$2) OR (N2$2 AND N1$1 AND N4$1) OR (N2$2 AND N1$2 AND N4$0) OR (N2$2 AND N1$2 AND N4$1)',
## 'N0$1* =(N2$0 AND N1$0 AND N4$0) OR (N2$0 AND N1$0 AND N4$1) OR (N2$0 AND N1$0 AND N4$2) OR (N2$0 AND N1$1 AND N4$1) OR (N2$0 AND N1$1 AND N4$2) OR (N2$0 AND N1$2 AND N4$0) OR (N2$0 AND N1$2 AND N4$1) OR (N2$0 AND N1$2 AND N4$2) OR (N2$1 AND N1$0 AND N4$2) OR (N2$1 AND N1$1 AND N4$1)',
## 'N0$2* =(N2$1 AND N1$0 AND N4$1) OR (N2$1 AND N1$2 AND N4$1) OR (N2$1 AND N1$2 AND N4$2) OR (N2$2 AND N1$0 AND N4$0) OR (N2$2 AND N1$0 AND N4$1) OR (N2$2 AND N1$1 AND N4$0) OR (N2$2 AND N1$1 AND N4$2) OR (N2$2 AND N1$2 AND N4$2)',
## 'N1$0* =(N0$0 AND N3$0 AND N4$1) OR (N0$0 AND N3$1 AND N4$0) OR (N0$0 AND N3$2 AND N4$1) OR (N0$1 AND N3$0 AND N4$0) OR (N0$1 AND N3$1 AND N4$0) OR (N0$1 AND N3$2 AND N4$2) OR (N0$2 AND N3$0 AND N4$0) OR (N0$2 AND N3$1 AND N4$2)',
## 'N1$1* =(N0$0 AND N3$0 AND N4$0) OR (N0$0 AND N3$0 AND N4$2) OR (N0$0 AND N3$1 AND N4$1) OR (N0$0 AND N3$2 AND N4$0) OR (N0$1 AND N3$0 AND N4$2) OR (N0$1 AND N3$1 AND N4$2) OR (N0$1 AND N3$2 AND N4$1) OR (N0$2 AND N3$2 AND N4$1)',
## 'N1$2* =(N0$0 AND N3$1 AND N4$2) OR (N0$0 AND N3$2 AND N4$2) OR (N0$1 AND N3$0 AND N4$1) OR (N0$1 AND N3$1 AND N4$1) OR (N0$1 AND N3$2 AND N4$0) OR (N0$2 AND N3$0 AND N4$1) OR (N0$2 AND N3$0 AND N4$2) OR (N0$2 AND N3$1 AND N4$0) OR (N0$2 AND N3$1 AND N4$1) OR (N0$2 AND N3$2 AND N4$0) OR (N0$2 AND N3$2 AND N4$2)',
## 'N2$0* =(N4$0 AND N3$0 AND N1$0) OR (N4$0 AND N3$0 AND N1$1) OR (N4$0 AND N3$0 AND N1$2) OR (N4$0 AND N3$2 AND N1$1) OR (N4$1 AND N3$0 AND N1$0) OR (N4$1 AND N3$1 AND N1$2) OR (N4$1 AND N3$2 AND N1$1) OR (N4$1 AND N3$2 AND N1$2) OR (N4$2 AND N3$1 AND N1$2)',
## 'N2$1* =(N4$0 AND N3$1 AND N1$2) OR (N4$0 AND N3$2 AND N1$0) OR (N4$1 AND N3$1 AND N1$1) OR (N4$1 AND N3$2 AND N1$0) OR (N4$2 AND N3$0 AND N1$2) OR (N4$2 AND N3$1 AND N1$1) OR (N4$2 AND N3$2 AND N1$0) OR (N4$2 AND N3$2 AND N1$1)',
## 'N2$2* =(N4$0 AND N3$1 AND N1$0) OR (N4$0 AND N3$1 AND N1$1) OR (N4$0 AND N3$2 AND N1$2) OR (N4$1 AND N3$0 AND N1$1) OR (N4$1 AND N3$0 AND N1$2) OR (N4$1 AND N3$1 AND N1$0) OR (N4$2 AND N3$0 AND N1$0) OR (N4$2 AND N3$0 AND N1$1) OR (N4$2 AND N3$1 AND N1$0) OR (N4$2 AND N3$2 AND N1$2)',
## 'N3$0* =(N1$0 AND N0$0 AND N4$1) OR (N1$0 AND N0$1 AND N4$0) OR (N1$1 AND N0$1 AND N4$0) OR (N1$1 AND N0$1 AND N4$2) OR (N1$2 AND N0$1 AND N4$1) OR (N1$2 AND N0$1 AND N4$2) OR (N1$2 AND N0$2 AND N4$0)',
## 'N3$1* =(N1$0 AND N0$1 AND N4$2) OR (N1$0 AND N0$2 AND N4$2) OR (N1$1 AND N0$0 AND N4$1) OR (N1$1 AND N0$2 AND N4$0) OR (N1$1 AND N0$2 AND N4$2) OR (N1$2 AND N0$0 AND N4$0) OR (N1$2 AND N0$0 AND N4$2) OR (N1$2 AND N0$2 AND N4$1) OR (N1$2 AND N0$2 AND N4$2)',
## 'N3$2* =(N1$0 AND N0$0 AND N4$0) OR (N1$0 AND N0$0 AND N4$2) OR (N1$0 AND N0$1 AND N4$1) OR (N1$0 AND N0$2 AND N4$0) OR (N1$0 AND N0$2 AND N4$1) OR (N1$1 AND N0$0 AND N4$0) OR (N1$1 AND N0$0 AND N4$2) OR (N1$1 AND N0$1 AND N4$1) OR (N1$1 AND N0$2 AND N4$1) OR (N1$2 AND N0$0 AND N4$1) OR (N1$2 AND N0$1 AND N4$0)',
## 'N4$0* =(N1$0 AND N2$0 AND N0$1) OR (N1$0 AND N2$1 AND N0$1) OR (N1$1 AND N2$0 AND N0$0) OR (N1$1 AND N2$0 AND N0$1) OR (N1$1 AND N2$1 AND N0$1) OR (N1$2 AND N2$0 AND N0$1)',
## 'N4$1* =(N1$0 AND N2$0 AND N0$2) OR (N1$0 AND N2$1 AND N0$0) OR (N1$0 AND N2$2 AND N0$1) OR (N1$0 AND N2$2 AND N0$2) OR (N1$1 AND N2$1 AND N0$0) OR (N1$1 AND N2$1 AND N0$2) OR (N1$1 AND N2$2 AND N0$1) OR (N1$1 AND N2$2 AND N0$2) OR (N1$2 AND N2$0 AND N0$0) OR (N1$2 AND N2$0 AND N0$2) OR (N1$2 AND N2$2 AND N0$0) OR (N1$2 AND N2$2 AND N0$1) OR (N1$2 AND N2$2 AND N0$2)',
## 'N4$2* =(N1$0 AND N2$0 AND N0$0) OR (N1$0 AND N2$1 AND N0$2) OR (N1$0 AND N2$2 AND N0$0) OR (N1$1 AND N2$0 AND N0$2) OR (N1$1 AND N2$2 AND N0$0) OR (N1$2 AND N2$1 AND N0$0) OR (N1$2 AND N2$1 AND N0$1) OR (N1$2 AND N2$1 AND N0$2)']

##y =['STAT3$1 * = (IL23_e$0 AND IL23$0 AND (( IL27_e$0 AND (( IL21$0 AND (IL10_e$1 OR (IL10_e$0 AND (IL10$1 OR (IL10$0 AND (IL6_e$0 AND IL21_e$1 OR IL6_e$1)))))) OR IL21$1 )) OR IL27_e$1) ) OR ( (IL23_e$0 AND IL23$1 OR IL23_e$1) AND ((STAT3$1 AND ((RORGT$0 AND (( IL27_e$0 AND (( IL21$0 AND (IL10_e$1 OR (IL10_e$0 AND IL10$1 OR (IL10$0 AND ((IL6_e$0 AND IL21_e$1) OR IL6_e$1)))))) OR IL21$1)) OR IL27_e$1)) OR RORGT$1)) OR (STAT3$0 AND ((IL27_e$0 AND ((IL21$0 AND (IL10_e$1 OR(IL10_e$0 AND (IL10$1 OR (IL10$0 AND ((IL6_e$0 AND IL21_e$1) OR IL6_e$1)))))) OR IL21$1)) OR IL27_e$1)) )']
##x = Simulation.nodescan(y,mode=1)
##print 'x=',x
##
##print y[0]
##z = qm(y[0],x[0],x[1])
##print 'z=',z
##print("--- %s seconds ---" % (time.time() - t1))

