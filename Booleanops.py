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
import numpy as np
import networkx as nx
##import matplotlib.pyplot as plt
import copy
import functions
##import ast
import itertools
import qm2
##from qm import QuineMcCluskey

import mpmath
from sympy import *



##f = open('toy_example1.txt', 'r')
##
### read through all functions. Then create a list of nodes, and a list of their states.
### Create Boolean symbols for each state of each node.
##
##words = f.readline()
##nodes = []
##states =[]
##function = []
##while (words.find("=")!=(-1)):
##    node = words.split("*",1)[0].strip()
##    function.append(words.split("=",1)[1].strip())
##    node1 = node.split("$",1)[0].strip()
##    if node1 not in nodes:
##        nodes.append(node1)
##    states.append(node)
##    words = f.readline()
##
##f.close()
##
##nodestates = [0]*len(nodes)
##for index in range (len(nodes)):
##    nodestates[index]=[]
##
##for nodeindex in range (len(nodes)):
##    for state in states:
##        node2 = state.split("$",1)[0].strip()
##        if node2 == nodes[nodeindex]:
##            if state not in nodestates[nodeindex]:
##                nodestates[nodeindex].append(state)
##
####print nodes
####print states
####print nodestates
##
##A=[0]*(len(states))
##for i in range (len(states)):
##    A[i] = symbols(states[i])


def replace(str,A=0,index=0): # replace Boolean operators with "&,|,~", and nodes with symbols

    result=''
    OR = ['or','|']
    AND = ['and','&']
    NOT = ['not','~']
    if (str in AND) or (str.lower() in AND):
        result='&'
    elif (str in OR) or (str.lower() in OR):
        result='|'
    elif (str in NOT) or (str.lower() in NOT):
        result='~'
    else:
        if A==0:
            result=str
        else:
            A[index] = symbols(str)
            result += 'A[{}]'.format(index)
            index += 1
    return result



def to_sympy(str1,mode=1,outputnode=0): # converts a string (Boolean function) to a specific format
    # assume functions already has"And" "or" "not" rules expressed in "&,|,~"
    # need to convert each input as a symbol

    # put a space before each '(', if there hasn't been a space, and if the character before '(' is not another '('
    str2 = ''
    if len(str1)>=1:
        for i in range(0,len(str1)):
            if str2 != '':
                if (str1[i]=='(') and (str2[i-1] != ' ') and (str1[i-1] != '('):
##                    print str1[i],str1[i-1]
                    str2 += ' '
            str2 += str1[i]
    else:
        str2 = str1
##    print str2
    s = str2.split()

    removable = ['(',')',' ','~']
    result=''
    OR = ['or','|']
    AND = ['and','&']
    NOT = ['not','~']
    index = 0
    A=[0]*len(s)
##    print
##    print s
    for item in s:
##        print item
        result1=''
        end=''
        while item[0] in removable:
            result += item[0]
            item = item[1:len(item)]
            if item =='':
                break
        if item !='':
            while item[len(item)-1] in removable:
                end += item[len(item)-1]
                item = item[0:len(item)-1]

            if (item in AND) or (item.lower() in AND):
                result1='&'
            elif (item in OR) or (item.lower() in OR):
                result1='|'
            elif (item in NOT) or (item.lower() in NOT):
                result1='~'
            else:
                A[index] = symbols(item)
                result1 = 'A[{}]'.format(index)
                index += 1

            result += result1

            result += end
            result += ' '
##    print result
    if outputnode==0:
        if mode==0:
            return result.strip()
        elif mode==1:
            return eval(result)
    else:
        if mode==0:
            return [result.strip(),filter(lambda a: a != 0, A)]
        elif mode==1:
            return [eval(result.strip()),filter(lambda a: a != 0, A)]


def convert(str1,mode=0,outputnode=0): # converts a string (Boolean function) to the format usable by sympy
    # assume functions already has"And" "or" "not" rules expressed in "&,|,~"
    # need to convert each input as a symbol
    # mode=1: 'and, not, or'; mode=0: '&, ~, |'
    # outputnode=0: return only the functions; outputnode=1: return a list of: 1st:functions; 2nd:nodes

    # put a space before each '(', if there hasn't been a space
    str2 = ''
    if len(str1)>=1:
        for i in range(0,len(str1)):
            if str2 != '':
                if (str1[i]=='(') and (str2[i-1] != ' '):
                    str2 += ' '
            str2 += str1[i]
    else:
        str2 = str1
##    print str2
    s = str2.split()
##    print s
    removable = ['(',')',' ']
    result=''
    OR = ['or','|']
    AND = ['and','&']
    NOT = ['not','~']
    index1 = 0
    A=[0]*len(s)
    for item in s:
##        print item
        result1=''
        end=''
        if len(item)>=2:
            while item[0] in removable:  # remove symbols in 'removable' category
                result += item[0]
                item = item[1:len(item)]
            while item[len(item)-1] in removable:
                end += item[len(item)-1]
                item = item[0:len(item)-1]

            if (item[0] == '~') and (item != '~'):  # treat '~' and 'not' differently because '~' can be followed by a node without a space in between
                if mode == 1:
                    result += 'not '
                else:
                    result += '~'
                item = item[1:len(item)]

            if (item in AND) or (item.lower() in AND):
                if mode == 1:
                    result1='and'
                else:
                    result1='&'
            elif (item in OR) or (item.lower() in OR):
                if mode == 1:
                    result1='or'
                else:
                    result1='|'
            elif (item in NOT) or (item.lower() in NOT):
                if mode == 1:
                    result1='not'
                else:
                    result1='~'
            else:
                # if item is already in the A list, call the corresponding A[index]
    ##            print item
    ##            print type(item)
                if symbols(item) in A:
                    result1 = 'A[{}]'.format(A.index(symbols(item)))
                else:
                    A[index1] = symbols(item)
                    result1 = 'A[{}]'.format(index1)
                    index1 += 1
    ##        print A
    ##        print type(A[1])
            result += result1

            result += end
            result += ' '
        else:
            result += item
        if result[len(result)-1]!=' ':
            result += ' '
    if outputnode==0:
        return result.strip()
    else:
        return [result.strip(),filter(lambda a: a != 0, A)]

# test
##
##a = 'Not(D$1)'
##x = convert (a)
##print x



def enum_ones(str1,length):  # enumerate the full truth table, in the form of a list of "ones" of a Boolean function; length is the # inputs
    lst = list(itertools.product([0, 1], repeat=length))
##    print str1
    ones = []
    zeros = []
    for i in range (0,len(lst)):
        A = lst[i]
##        print A
        sum=0
##        print 'eval(str1)=',eval(str1)
        if eval(str1):
            for j in range (0,len(A)):
                sum += A[j]*(2**(len(A)-1-j))
            ones.append(sum)
        else:

            for j in range (0,len(A)):
                sum += A[j]*(2**(len(A)-1-j))
            zeros.append(sum)
    return [ones,zeros]

# test example:




def reconsturct(qmset,inputs,mode=0):  # convert the result from qm back to readable function. mode=1: use '&,|, ~' notations
    lst = list(qmset)
    result=''
##    inputs.reverse()
    for i in range (0,len(lst)):
        result += '('
        for j in range (0,len(lst[i])):
            if lst[i][j]=='1':
                result += str(inputs[j])
                if mode ==0:
                    result += ' AND '
                else:
                    result += ' & '

            elif lst[i][j]=='0':
                if mode ==0:
                    result += 'NOT '
                else:
                    result += '~ '
                result += str(inputs[j])
                if mode ==0:
                    result += ' AND '
                else:
                    result += ' & '

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

def reconsturct_sympy(sympy_function):  # convert the result from sympy in dnf back to readable function.
    str1 = str(sympy_function)
    result=''
    if str1[0:3] == 'Or(':
        str1 = str1[3:len(str1)-1]
    elif str1[0] == '(':
        str1 = str1[1:len(str1)-1]

##    print str1
    parts =  str1.split(",")
    for i in range(0,len(parts)):
        parts[i] = parts[i].strip()
##    print parts

    Flag=1
    for i in range(0,len(parts)):
##        print parts[i]
        # count '(' and ')'
        count=0
        for j in range (0,len(parts[i])):
            if parts[i][j] == '(':
                count-=1
            if parts[i][j] == ')':
                count+=1
        Flag += count
##        print Flag
        if count ==-1: result += '('
        if Flag ==0:
            if parts[i][0:4]== 'And(':
                result += parts[i][4:len(parts[i])]

            else:
                result += parts[i]
            result += ' AND '
        elif Flag ==1:
            result += parts[i][0:len(parts[i])]

            result += ' OR '
        else:
            print 'Error!'
##        print 'result=',result

    result = result[0:len(result)-4].strip()

    return result


def transform(str1): # ultimate function to transform a given function into the required all-prime-implicants form
##    print str1
    x = convert(str1,mode=1,outputnode=1) # x[0] is the string of function, with variables represented by A[i]; x[1] is the list A[i] with each item being the node A[i] represents
##    print x
    ones=enum_ones(x[0],len(x[1]))
##    print ones
##    qm = QuineMcCluskey()
##    if ones == [0]:     # to overcome the error in the qm algorithm
##        a = set(['0'])
##    else:
    a = qm2.qm(ones[0],ones[1],mode=1)
##        b=list(a)
##        for item in b: # check if '0', i.e. 'Not' rule is present in the converted rule
##            if '0' in list(item):
##                print '------------------   zero found!   ------------------------'
##                print 'a=',a
    return reconsturct(a,x[1],mode=0)


# #################   test   ########
##str1= 'Or(z, Not(x), And(y, not(w)))'
##str1= 'Or(And(y, not(w)),z, Not(x), And(y, not(w)))'
##
##
##x = reconsturct_sympy(str1)
##
##print 'result=',x

##str1 = '((not N4$1 AND not N4$2) AND (not N8$1 AND not N8$2))'
##b= transform(str1)
##print b



##str1= 'B$0 | (~C$1 ANd B$1)'
##str1 = '(B AND C) OR (A AND ~C)'
##print transform(str1)

##x = convert(str1,mode=1,outputnode=1) # x[0] is the string of function, with variables represented by A[i]; x[1] is the list A[i] with each item being the node A[i] represents
##
##print x
##print enum_ones(x[0],len(x[1]))
##str1= 'B & A | C ANd ~A'

##a = to_dnf(to_sympy(str1))
##a = convert(str1,mode=1,outputnode=1)

##str1 = '(A1 and B1 or C1 and B0) and ((B1 or B0) and (not B1 or not B0))'
##str1 = '(A1 and C1 and B0) or (A1 and C1 and not B0)'
##str1 = '(A1 and (not B1 and not B2)) or (C1 and B1) or (C1 and B2)'
##print transform(str1)



# start from a dnf produced by sympy: create the list of '1's needed by QM



# read through all functions. Then create a list of nodes, and a list of their states. Create Boolean symbols for each state of each node.
