from flask import Flask, jsonify, request
from flask_api import FlaskAPI, status, exceptions
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import json, numpy, operator
from collections import OrderedDict

api = FlaskAPI(__name__) 
api.config['JSON_SORT_KEYS'] = False

"""local function section"""

"""
Purporse: compare current part anotation with category of annotation
Input: other part's in the object that you are annotating (key for it is "partOf")
Output: returns sorted list 
"""
def sortPartWithCategory(part, category, pos):
	scoreList = []
	j = 0
	info = []
	category_synset = returnSynsetWithPOS(category, pos)
	part_synset = returnSynsetWithPOS(part, pos)
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
		info[j].update({"key": part_synset[index].name()})
		info[j].update({"gloss": part_synset[index].definition()})
		info[j].update({"synsetID": part_synset[index].offset()})
		info[j].update({"score": average})
		j = j + 1
	newlist = sorted(info, key=lambda k: k['score'], reverse=True) 
	return newlist

"""
Purporse: compare current part anotation with category of annotation
Input: other part's in the object that you are annotating (key for it is "partof")
Output: returns sorted list 
"""
def sortLabel(part, otherParts, pos):
	counter = 2 #this is for keeping track of how many scores are being averaged 
	scoreList = []
	output = []
	info = {}
	for otherPart in otherParts:
		part_synset = returnSynsetWithPOS(part, pos)
		otherPartSynsets = returnSynsetWithPOS(otherPart, pos)
		for index in range(0,len(part_synset)):
			for indexWord in range(0,len(otherPartSynsets)):
				score = part_synset[index].wup_similarity(otherPartSynsets[indexWord])
				if score is not None:
					scoreList.append(score)
			sum = 0
			for num in scoreList:
				sum = sum + num
			average = sum / (len(scoreList))
			scoreList.clear()
			try:
				new_val = (average + ((counter - 1) * info[part_synset[index]]["score"]))/ counter
				info[part_synset[index]].update({"gloss": part_synset[index].definition(), "score": new_val})
				counter = counter + 1
			except Exception:
				info[part_synset[index]] = {"gloss": part_synset[index].definition(), "score": average} 
	j = 0
	for keyVal in info.keys():
		output.append({})
		output[j].update({"key": keyVal.name()})
		output[j].update({"gloss": keyVal.definition()})
		output[j].update({"synsetID": keyVal.offset()})
		output[j].update({"score": info[keyVal]["score"]})
		j = j + 1
	newlist = sorted(output, key=lambda k: k['score'], reverse=True) 
	return newlist

"""
Purpose: function for getting info about a word
Input: the common name of a part
Output: returns information of the part as a dictionary inside 1 list
"""
def returnWordInfo(word, pos):
	syn = returnSynsetWithPOS(word, pos)
	info = []
	bracket = {}
	for j in range(0,len(syn)):
		info.append({})
		info[j].update({"key": syn[j].name()})
		info[j].update({"gloss": syn[j].definition()})
		info[j].update({"synsetID": syn[j].offset()})
	return info

"""Return list of definitions for a word"""
def returnDef(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	definitionList = []
	for i in syn:
		definitionList.append(i.definition())
	return definitionList

"""Return list of synset keys for a word"""
def returnKey(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	keyList = []
	for i in syn:
		keyList.append(i.name())
	return keyList

"""Return list of POS for every synset of a word"""
def returnPOS(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	posList = []
	for i in syn:
		posList.append(i.pos())
	return posList

"""Return list of synset IDs for a word"""
def returnID(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	idList = []
	for i in syn:
		idList.append(i.offset())
	return idList

"""Return list of synsets based on correct POS """
def returnSynsetWithPOS(word, pos):
	pos = pos.upper()
	if pos == "NOUN":
		try:
			syn = wordnet.synsets(word, pos = wn.NOUN)
		except Exception:
			syn = wordnet.synsets(word)	
	elif pos == "ADJECTIVE":
		try:
			syn = wordnet.synsets(word, pos = wn.ADJECTIVE)
		except Exception:
			syn = wordnet.synsets(word)	
	elif pos == "VERB":
		try:
			syn = wordnet.synsets(word, pos = wn.VERB)
		except Exception:
			syn = wordnet.synsets(word)	
	elif pos == "ADVERB":
		try:
			syn = wordnet.synsets(word, pos = wn.ADVERB)
		except Exception:
			syn = wordnet.synsets(word)	
	else:
		syn = wordnet.synsets(word)
	return syn

"""main screen"""
@api.route("/", methods=['GET', 'POST'])
def test():
	return jsonify ({'message' : 'It works'})

"""Adress for testing helper functions"""
@api.route('/wordlink/currentTest', methods=['GET', 'POST'])
def testThings ():
	data = request.get_json()
	word = 	data["label"]
	return jsonify(returnID(word))

""" 
Purpose: address for getting info about a word
Input: the common name of a part (make sure item is a list) (dictionary key is "label")
Output: returns information of the part as a dictionary inside 1 list
"""
@api.route('/wordlink/getInfo', methods=['GET', 'POST'])
def returnInfo():
	data = request.get_json()
	word = data["label"]
	pos = data["pos"]
	output = returnWordInfo(word, pos)
	return jsonify(output)

""" 
Purpose: address for identifying correct synset for a part annotation linkage based on similarity scores
Input: current part and list of other parts in an object (keys are "otherparts" and "label")
Output: returns list of dictionaries
"""
@api.route('/wordlink/sortByOtherParts', methods=['GET', 'POST'])
def sortPart():
	data = request.get_json()
	otherParts = data["otherParts"]
	part = 	data["label"]
	pos = data["pos"]
	return jsonify(sortLabel(part, otherParts, pos))

""" 
Purpose: address for identifying correct synset for a part annotation linkage based on similarity scores
Input: current part and list of other parts in an object (keys are "partof" and "label")
Output: returns list of dictionaries 
"""
@api.route('/wordlink/sortByCategory', methods=['GET', 'POST'])
def sort():
	data = request.get_json()
	category = data["partOf"]
	part = 	data["label"]
	pos = data["pos"]
	return jsonify(sortPartWithCategory(part, category, pos))

if __name__ == "__main__":
	api.run(debug=True, port = 8080)