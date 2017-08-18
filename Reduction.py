#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Xiao Gan
#
# Created:     05/09/2016
# Copyright:   (c) Xiao Gan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re
##import numpy as np
import networkx as nx
##import matplotlib.pyplot as plt
import copy
##import functions
##import ast
import Booleanops
import itertools
from sympy import *

def findinput(list1): # find all input nodes in a .txt file. Return a list two lists: 1st list of nodes in strings,  2nd list of corresponding values.

    inputlist=[]
    valuelist=[]
    for words in list1:
##        print words
        node = words.split("*",1)[0].strip()
        function = words.split("=",1)[1].strip()   #removes spaces and '/n'  at the end of each line

        if function.isdigit():
            inputlist.append(node)
            valuelist.append(function)

    return [inputlist,valuelist]


def evaluation(str1,inputs,values):# evaluate/simplify a single boolean function by plugging in values for inputs
    # Returns a sympy function
##    print str1

    x = Booleanops.to_sympy(str1,mode=1,outputnode=1)
    y = {}
    for j in range (0,len(x[1])):
##        print 'node={}'.format(str(x[1][j]))
        # if node is an input, plug in the corresponding value
        for i in range (0,len(inputs)):
            if str(x[1][j]) == inputs[i]:
                y[x[1][j]]=values[i]
##                print y
##        print
    x[0] = x[0].subs(y)
    x[0] = to_dnf(x[0])
    return x[0]



def reduction(list1, inputs=[], values=[],mode=0):  # reduce a set of functions by plugging input values
    # mode=0: discard const. functions; mode=1: keep const. functions
##    # find inputs and their values as two lists combined in a list
##    f = open(file1, 'r')
    reducedlist =[]
##    f1 = open('reduced.txt', 'w')
##    f1.write('#Reduced Functions\n')
    for words in list1:
        node = words.split("*",1)[0].strip()
        function = words.split("=",1)[1].strip()   #removes spaces and '/n'  at the end of each line

        if not function.isdigit():
            x = evaluation(function,inputs,values)

##            print x
            y = Booleanops.reconsturct_sympy(x)           # convert x to normal Boolean form

            if y == 'True':
    ##            print function
                y = '1'
            if y == 'False':
                y = '0'
            item = ''
            item += node
            item += '* ='
            item += str(y)
            reducedlist.append(item)
        elif mode==1:
            reducedlist.append(words)
##            f1.write(node)
##            f1.write('* =')
##            f1.write(str(y))
##            f1.write('\n')
##        else:
##            f1.write(node)
##            f1.write(' Reduced\n')
    # plug in values for each input
##        words = f.readline()

    return reducedlist

def to_list(file1): # convert a functions file into a list of strings/functions
    list1=[]
    f = open(file1, 'r')

    words = f.readline()
    while (words[0]==('#')) or (words==''):
        words = f.readline()
    while (words.find("=")!=(-1)):
        list1.append(words.strip())
        words = f.readline()
    return list1

def inputsub(functionlist, inputs): # replace certain functions in the functionlist with given inputs
    # inputs: 'functionlist' is a list of functions (strings); 'inputs' is a list of two lists: 1st list of nodes, 2nd list of their corresponding values
##    # 'oscillations' is an optional list of lists, that marks lists of nodes that belong to an oscillation and cannot be reduced
    # for each given input, not only its value is set to 1, but also all its other virtual nodes are set to 0. E.g. if A$1 = 1 is given, A$0 will be set to 0
    # for each oscillating node, set all its other virtual nodes to 0. E.g. if A$2 and A$3 are given, A$0 and A$1 will be set to 0

    list1=[]
    for function in functionlist:
##        print function,inputs
        node = function.split("*",1)[0].strip()
        if function.split("=",1)[1].strip() != '@':
            for i in range(0,len(inputs[0])):
##                print node, inputs[0][i]
                if node == inputs[0][i]:
                    function = node + '* = ' + str(inputs[1][i])
##                    print 'sub',str(inputs[1][i]),function
                    break
                # if the node is a virtual node corresponding to the same original node, set it to 0
                else:
##                    print (node.split("$",1)[0], inputs[0][i].split("$",1)[0])
                    if (node.split("$",1)[0] == inputs[0][i].split("$",1)[0]): # not sure if correct 0216/2017
##                    if (node.split("$",1)[0] == inputs[0][i].split("$",1)[0]) and (inputs[1][i]!='@'):
                        function = node + '* = ' + '0'
##            print function
        list1.append(function)

    return list1

# test example
##obj = [['N0$0* = 1', 'N0$1* = 0', 'N1$0* =(N2$1 AND N0$1)', 'N1$1* =(N2$0 AND N0$0) OR (N2$0 AND N0$1) OR (N2$1 AND N0$0)', 'N2$0* = 1', 'N2$1* = 0', 'N4$0* =(N0$0 AND N5$0) OR (N0$1 AND N5$2)', 'N4$1* =(N0$0 AND N5$2)', 'N4$2* =(N0$0 AND N5$1) OR (N0$1 AND N5$0) OR (N0$1 AND N5$1)', 'N5$0* =(N1$0 AND N4$2) OR (N1$1 AND N4$2)', 'N5$1* =(N1$0 AND N4$1) OR (N1$1 AND N4$0)', 'N5$2* =(N1$0 AND N4$0) OR (N1$1 AND N4$1)'], [['N0$0', 'N2$0'], ['N4$0', 'N4$2', 'N5$0', 'N5$1']]]
##stablenodes = [['N4$0', 'N4$2', 'N5$0', 'N5$1'], ['@', '@', '@', '@']]
##
##print inputsub(obj[0],stablenodes)


##print to_list('toy_example1.txt')
##str1= 'B$0 | (~C$1 ANd B$1)'

##x = evaluation(str1,['B$0','B$1'],[0,1])
##reduction('toy_example1.txt')


##print x
##print x[0].subs(x[1][0],0)


##f = open('toy_example.txt', 'r')
##words = f.readline()
##while (words.find("=")!=(-1)):
##    node = words.split("*",1)[0].strip()
##    function = words.split("=",1)[1].strip()   #removes spaces and '/n'  at the end of each line
##    print function
##
##    if not function.isdigit():
##        x = Booleanops.convert(function,mode=1,outputnode=1)
##
##        # evaluate x[0] according to given inputs and values
##
##
##
### plug in values for each input
##    words = f.readline()