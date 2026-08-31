import json


with open("data/en_conceptnet.json", "r", encoding="utf-8") as json_file:
    graph = json.load(json_file)


rel=set()

for key,relations in graph.items():
    for relation,related_term in relations.items():
        rel.add(relation)


with open("data/relations.txt", "w", encoding="utf-8") as f:
    for r in sorted(rel):
        f.write(r + "\n")
