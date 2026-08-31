import json


with open("data/en_conceptnet.json", "r", encoding="utf-8") as json_file:
    graph = json.load(json_file)

vocabulary=set()


for key,relations in graph.items():
    vocabulary.add(key)
    for relation,related_terms in relations.items():
        for term in related_terms:
            vocabulary.add(term)


with open("data/en_vocabulary.txt", "w", encoding="utf-8") as f:
    for word in sorted(vocabulary):
        f.write(word + "\n")

        


