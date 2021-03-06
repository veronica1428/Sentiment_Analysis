#! /usr/bin/env python

import numpy as np
import nltk;
import pprint;
import csv
import collections
import textwrap

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize

inputLines = []
filePath = 'sentiword.txt'
wordnet = []
falseNeg = []
falsePos = []
truePos = []
trueNeg = []
global reviewDict
reviewDict = {}

#define two lists: one for positive score and other for negative score
posList = []
negList = []

#variable for confidence matrix
global falsePositive
global falseNegative
global trueNegative
global truePositive

#loading senti word net dictionary
def sentiWordNet():
    
    sent_scores = collections.defaultdict(list)
    
    f = open(filePath)
    reader = csv.reader(f, delimiter='\t')
    for line in reader:
        if line[0].startswith("#"):
            continue
        if len(line) == 1:
            continue
            
        POS, ID, PosScore, NegScore, SynsetTerms, Gloss = line
        
        if len(POS) == 0 or len(ID) == 0:
            continue
        # print POS,PosScore,NegScore,SynsetTerms
        for term in SynsetTerms.split(" "):
            # drop #number at the end of every term
            term = term.split("#")[0]
            term = term.replace("-", " ").replace("_", " ")
            key = "%s/%s" % (POS, term.split("#")[0])
            sent_scores[key].append((float(PosScore), float(NegScore)))
        
    for key, value in sent_scores.items():
        sent_scores[key] = np.mean(value, axis=0)
        
    return sent_scores

sentiLib = sentiWordNet()

#to determine whether the word is stopword in english dictionary or not
def is_stopWord(word):
    if word.lower() in nltk.corpus.stopwords.words('english'):
        return True
    return False

#function to calculate mean of a list
def calculateMean(list):
    length = len(list)
    total = 0
    
    for x in list:
        total = total + x
    
    return ((total/length))

#Read sentiwordNet and calculate scores
def sentiment(line):

    tokens = word_tokenize(line)
    tag_tuples = nltk.pos_tag(tokens)
    tag_type = 0

    for (string, tag) in tag_tuples:

        if tag.startswith("JJ"):
            tag_type = "a"
        if tag.startswith("NN"):
            tag_type = "n"
        if tag.startswith("RB"):
            tag_type = "r"
        if tag.startswith("VB"):
            tag_type = "v"

        #remove stop words
        if is_stopWord(string):
            continue

        #remove punctuations
        if not is_punctuation(string):
            token = {'word':string, 'pos':tag_type}
            sentence = "%s/%s"%(tag_type, string)

            if sentence in sentiLib:
                pos, neg = sentiLib[sentence]
                posList.append(pos)
                negList.append(neg)

#check whether parametric value is punctuation or not
def is_punctuation(string):
    for char in string:
        if char.isalpha() or char.isdigit():
            return False
    return True

#Function to read input file
def readFileContent():
    print ('Inside readFileContent Method')
    
    LinePos = 0
    lineNeg = 0
    lineCount = 0
    objScore = 0
    ch = 0
    
    print ('PREDICTED SCORE:')
    print ('LineNum\t\tReview Id\t\tTitle\t\t\tPositive Score\t\tNegative Score\t\tObj Score\t\t\tResult')
    
    with open('randomfile2.txt') as inputfile:
        for line in inputfile:
            if (ch > 0 and ch <= 300):
                lineCount = lineCount + 1
            
                fileDesc = line.split('\t')
            
                inputLines.append(line)
                sentiment(line)

                #calculate total positive score for a line
                LinePos = calculateMean(posList)
                lineNeg = calculateMean(negList)
                objScore = 1 - LinePos - lineNeg
            
                predScore = PosNeg(LinePos, lineNeg)
                #dictProgramReview(fileDesc[0], predScore)
                reviewDict[str(fileDesc[0])] = str(predScore)

                del posList[:]
                del negList[:]
                
                print (str(lineCount) + '\t\t' + str(fileDesc[0]) + '\t\t' + str(fileDesc[1]) + '\t\t' + str(LinePos) + '\t\t' + str(lineNeg) + '\t\t' + str(objScore)  + '\t\t' + str(PosNeg(LinePos, lineNeg)))
                
                ch = ch + 1
            else:
                ch = ch + 1
    
    print ('going inside readManualFile')
    tp, tn, fp, fn = readManualFile()
    print ('True positive: ' , str(tp), '\n', 'True Negative', str(tn))
    print ('False positive: ', str(fp), '\n', 'False Negative', str(fn))

    precision = tp/(tp + fp)
    recall = tp/(tp + fn)
    accuracy = 2/(1/precision + 1/recall)

    print ('precision: ', str(precision))
    print ('recall: ', str(recall))
    print ('accuracy: ', str(accuracy))

#function to calculate more Positive or more negative
def PosNeg(posNum, negNum):
    if posNum >= negNum:
        return 1

    else:
        return 0

#Manually read a file to get the review
def readManualFile():
    
    falsePositive = 0
    falseNegative = 0
    trueNegative = 0
    truePositive = 0
    
    f = open('ManualReview.txt')
    
    for line in range(100):
        id,scoreMan = f.readline().rsplit(None, 1)
        scorePred = reviewDict[str(id)]
        
        #Calculate confidence matrix values
        print ('score pred: ',str(scorePred), 'scoreman: ', str(scoreMan))
        if str(scorePred) == str(0):
            if str(scorePred) == str(scoreMan):
                print ('true negative', str(trueNegative), 'predicted score: ' , str(scorePred), 'Manual score: ' , str(scoreMan))
                trueNegative = trueNegative + 1
                trueNeg.append(id)
            else:
                print ('false negative', str(falseNegative), 'predicted score: ' , str(scorePred), 'Manual score: ' , str(scoreMan))
                falseNegative = falseNegative + 1
                falseNeg.append(id)
        if str(scorePred) == str(1):
            if str(scorePred) == str(scoreMan):
                print ('true positive', str(truePositive), 'predicted score: ' , str(scorePred), 'Manual score: ' , str(scoreMan))
                truePositive = truePositive + 1
                truePos.append(id)
            else:
                print ('false positive', str(falsePositive), 'predicted score: ' , str(scorePred), 'Manual score: ' , str(scoreMan))
                falsePositive = falsePositive + 1
                falsePos.append(str(id))
                falsePos.append(id)

    return truePositive, trueNegative, falsePositive, falseNegative

#function to store predicted values in dictionary
#def dictProgramReview(id, score):
#reviewDict.update({str(id) : str(score)})

#Main function
def main():

    readFileContent()
    print ('***********after readFileContent********')

    print ('**********************************FALSE POSITIVE**********************')
    for fp in falsePos:
        print ('fp: ', fp)
    
    print ('**********************************FALSE NEGATIVE**********************')
    for fn in falseNeg:
        print ('fn: ' , fn)

    print ('**********************************TRUE POSITIVE**********************')
    for tp in truePos:
        print ('tp: ', tp)

    print ('**********************************TRUE NEGATIVE**********************')
    for tn in trueNeg:
        print ('tn: ', tn)

main()