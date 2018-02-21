from flask import Flask, jsonify, request
from flask_api import FlaskAPI, status, exceptions
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import json, numpy, operator
from collections import OrderedDict

api = FlaskAPI(__name__) 

"""local function Section"""

"""
Purporse: Compare Current Part Anotation With Category of Annotation
Input: Other Part's in the Object that You Are Annotating (key for it is "partOf")
Output: Returns sorted list 
"""
def sortPartWithCategory(part, category):
	scoreList = []
	synset_with_score = {}
	j = 0
	info = []
	bracket = {}
	category_synset = wn.synsets(category)
	part_synset = wn.synsets(part)
	for index in range(0,len(part_synset)):
		for indexWord in range(0,len(category_synset)):
			score = part_synset[index].wup_similarity(category_synset[indexWord])
			if score is not None:
				scoreList.append(score)
		sum = 0
		for element in scoreList:
			sum = sum + element
		average = sum / len(scoreList)
		scoreList.clear()
		info.append({})
		info[j].update({"Key": part_synset[index].name()})
		info[j].update({"SynsetGloss": part_synset[index].definition()})
		info[j].update({"SynsetID": part_synset[index].offset()})
		info[j].update({"Score": average})
		j = j + 1
	newlist = sorted(info, key=lambda k: k['Score'], reverse=True) 
	return newlist

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
	word = 	data["label"]
	return jsonify(returnID(word))

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
Input: Current Part and List of Other Parts in an Object (keys are "partOf" and "label")
Output: Returns Sorted Dictionary 
"""
@api.route('/wordlink/sortByCategory', methods=['GET', 'POST'])
def sort():
	data = request.get_json()
	category = data["partOf"]
	part = 	data["label"]
	return jsonify(sortPartWithCategory(part, category))

if __name__ == "__main__":
	api.run(debug=True, port = 8080)