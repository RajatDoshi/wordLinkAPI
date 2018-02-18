from flask import Flask, jsonify, request
from flask_api import FlaskAPI, status, exceptions
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import json, numpy, operator
from collections import OrderedDict

api = FlaskAPI(__name__) 

#local function Section

# Purporse: Compare Current Part Anotation With Other Parts
# Input: Other Part's Synsets in the Object that You Are Annotating (key is "otherParts")
# Output: Returns sorted 
def returnSortedScores(word, recieve):
	scores = []
	other_parts = {"otherParts": []}
	synset_with_score = {}
	for i in recieve["otherPart"]:
		other_parts["otherParts"].append(i)
	for other in other_parts["otherParts"]:
		word_synset = wn.synsets(word)
		current_synset = wn.synsets(other)
		for index in range(0, len(current_synset)):
			for indexWord in range (0, len(word_synset)):
				val = current_synset[index].wup_similarity(word_synset[indexWord])
				if val is not None:
					scores.append(val)
					synset_with_score[word_synset[indexWord].name()] = val
	sort_val = sorted(scores, key=float)
	sor = sorted(synset_with_score.items(), key=operator.itemgetter(1), reverse=True)
	return sor


#This is the function for comparing a part with the other parts 
#this returns a list of all the synset keys and their similarity scores
def returnPartComparison(word, recieve):
	scores = []
	other_parts = {"otherParts": []}
	synset_with_score = {}
	for i in recieve["otherPart"]:
		other_parts["otherParts"].append(i)
	for other in other_parts["otherParts"]:
		word_synset = wn.synsets(word)
		current_synset = wn.synsets(other)
		for index in range(0, len(current_synset)):
			for indexWord in range (0, len(word_synset)):
				val = current_synset[index].wup_similarity(word_synset[indexWord])
				if val is not None:
					scores.append(val)		
					synset_with_score[word_synset[indexWord].name()] = val				
	return synset_with_score

#This funtion returns name, definition, POS, and synset key of a word in a list
def returnWordInfo(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	name = [
	{"synsetKey": []},
	{"synsetDefinition": []},
	{"synsetPOS": []},
	{"synsetCommonName": []}
	]
	for i in syn:
		for j in i.lemmas():
			name[0]["synsetKey"].append(i.name())
			name[1]["synsetDefinition"].append(i.definition())
			name[2]["synsetPOS"].append(i.pos())
			name[3]["synsetCommonName"].append(j.name())
	return name

#funtion to return a list of definitions for every synset of a particular word
def returnDef(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	definitionList = []
	for i in syn:
		definitionList.append(i.definition())
	return definitionList

#function to return a list of a word's synset IDs
def returnID(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	idList = []
	for i in syn:
		idList.append(i.offset())
	return idList

#function that returns a list of part of speechs for each synset of a word
def returnPOS(word):
	syn = wordnet.synsets(word)
	length = len(syn)
	posList = []
	for i in syn:
		posList.append(i.pos())
	return posList

#main screen
@api.route("/", methods=['GET', 'POST'])
def test():
	return jsonify ({'message' : 'It works'})

#test different functions at this address
@api.route('/wordlink/currentTest', methods=['GET', 'POST'])
def testThings ():
	recieve = request.get_json()
	otherPartList = {"otherPart": recieve["otherPart"]}
	word = 	recieve["currentPart"]
	synset_with_score = returnSortedScores(word, otherPartList)
	return jsonify(synset_with_score)

#adress to get information about a synset 
@api.route('/wordlink/getInfo', methods=['GET', 'POST'])
def returnInfo():
	recieve = request.get_json()
	info = []
	for i in range (0, len(recieve["part"])):
		word = recieve["part"][i]
		info.append(returnWordInfo(word))
	return jsonify(info)

@api.route('/wordlink/compare', methods=['GET', 'POST'])
def compare():
	recieve = request.get_json()
	otherPartList = {"otherPart": recieve["otherPart"]}
	word = 	recieve["currentPart"]
	synset_with_score = returnPartComparison(word, otherPartList)
	return jsonify(synset_with_score)

@api.route('/wordlink/compare_and_sort', methods=['GET', 'POST'])
def sort():
	recieve = request.get_json()
	otherPartList = {"otherPart": recieve["otherPart"]}
	word = 	recieve["currentPart"]
	sorted_synsets = returnSortedScores(word, otherPartList)
	return jsonify(sorted_synsets)

if __name__ == "__main__":
	api.run(debug=True, port = 8080)