from flask import Flask, jsonify, request
from flask_api import FlaskAPI, status, exceptions
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import json, numpy, operator
from collections import OrderedDict

api = FlaskAPI(__name__) 

"""local function Section"""

"""
Purporse: Compare Current Part Anotation With Other Parts
Input: Other Part's in the Object that You Are Annotating (key for it is "otherParts")
Output: Returns sorted list 
"""
def returnSortedScores(word, data ):
	scores = []
	synset_with_score = {}
	other_parts = data
	for other in other_parts:
		word_synset = wn.synsets(word)
		current_synset = wn.synsets(other)
		for index in range(0, len(current_synset)):
			for indexWord in range (0, len(word_synset)):
				val = current_synset[index].wup_similarity(word_synset[indexWord])
				if val is not None:
					scores.append(val)
					synset_with_score[word_synset[indexWord].name()] = val
	sorted_scores = sorted(scores, key=float)
	sortedList = sorted(synset_with_score.items(), key=operator.itemgetter(1), reverse=True)
	return sortedList
"""
Purpose: Function For Getting Info About a Word
Input: The Common Name of a Part
Output: Returns Information of the part as a dictionary inside 1 list
"""
def returnWordInfo(word):
	syn = wordnet.synsets(word)
	info = []
	bracket = {}
	for j in range(0,len(syn)):
		info.append({})
		info[j].update({"Key": syn[j].name()})
		info[j].update({"SynsetGloss": syn[j].definition()})
		info[j].update({"SynsetID": syn[j].offset()})
	return info
"""Return List of Definitions for a Word"""
def returnDef(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	definitionList = []
	for i in syn:
		definitionList.append(i.definition())
	return definitionList

"""Return List of Synset Keys for a Word"""
def returnKey(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	keyList = []
	for i in syn:
		keyList.append(i.name())
	return keyList

"""Return List of POS for Every Synset of a Word"""
def returnPOS(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	posList = []
	for i in syn:
		posList.append(i.pos())
	return posList

"""Return List of Synset IDs for a Word"""
def returnID(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	idList = []
	for i in syn:
		idList.append(i.offset())
	return idList

"""main screen"""
@api.route("/", methods=['GET', 'POST'])
def test():
	return jsonify ({'message' : 'It works'})

"""Adress For Testing Helper Functions"""
@api.route('/wordlink/currentTest', methods=['GET', 'POST'])
def testThings ():
	data = request.get_json()
	otherPartList = {"otherPart": data["otherPart"]}
	word = 	data["currentPart"]
	synset_with_score = returnSortedScores(word, otherPartList)
	return jsonify(synset_with_score)

""" 
Purpose: Adress For Getting Info About a Word
Input: The Common Name of a Part (make sure item is a list) (dictionary key is "label")
Output: Returns Information of the part as a dictionary inside 1 list
"""
@api.route('/wordlink/getInfo', methods=['GET', 'POST'])
def returnInfo():
	data = request.get_json()
	word = data["label"]
	output = returnWordInfo(word)
	return jsonify(output)

""" 
Purpose: Adress For Identifying Correct Synset for a Part Annotation Linkage Based on Similarity Scores
Input: Current Part and List of Other Parts in an Object (keys are "otherPart" and "label")
Output: Returns Sorted Dictionary 
"""
@api.route('/wordlink/compare_and_sort', methods=['GET', 'POST'])
def sort():
	data = request.get_json()
	otherPartList = data["otherPart"]
	word = 	data["label"]
	sorted_synsets = returnSortedScores(word, otherPartList)
	return jsonify(sorted_synsets)

if __name__ == "__main__":
	api.run(debug=True, port = 8080)