import json
import spacy
import random
import csv



with open("../data/en_conceptnet.json", "r", encoding="utf-8") as json_file:
    graph = json.load(json_file)

blacklist = ['person', 'human', 'group', 'emotion', 'concept', 'music', 'abstract_entity', 'action', 'communication', 'software', 'website', 'media', 'location', 'natural_feature', 'event', 'process', 'disease', 'animal', 'plant', 'time', 'category', 'market', 'industry', 'business', 'type', 'company', 'system', 'theory']
whitelist = ['artifact', 'object', 'tool', 'device', 'weapon', 'container', 'furniture', 'substance', 'material', 'clothing', 'vehicle', 'document', 'equipment']


entities=set()


for entity, relations in graph.items():
    if "IsA" not in relations:
        continue
    blacklisted = False
    if "MadeOf" in relations:
        for term in relations["IsA"]:
            tokens = term.split("_")
            for word in blacklist:
                if word in tokens or word == term:
                    blacklisted = True
                    break
            if blacklisted:
                break
        if not blacklisted:
            entities.add(entity)
    else:
        whitelisted = False
        for term in relations["IsA"]:
            tokens = term.split("_")
            for word in whitelist:
                if word in tokens or word == term:
                    whitelisted = True
                    break
            for word in blacklist:
                if word in tokens or word == term:
                    blacklisted = True
                    break
            if blacklisted:
                break
        if not blacklisted and whitelisted:
            entities.add(entity)
        


forensic_categories = {
    "weapon_offense": ["weapon", "gun", "knife", "firearm", "blade", "explosive", "rifle", "lethal", "assault", "murder"],
    "biological_traces": ["blood", "dna", "saliva", "corpse", "body", "tissue", "fingerprint", "biological", "wound"],
    "digital_evidence": ["computer", "smartphone", "laptop", "data", "password", "hacker", "cyber", "encrypted", "digital", "router"],
    "concealment_destruction": ["bleach", "fire", "burn", "trash", "hide", "bury", "destroy", "acid", "wipe", "shovel"],
    "access_intrusion": ["key", "lock", "door", "window", "crowbar", "security", "trespass", "lockpick", "break-in"],
    "substances_poisons": ["drug", "poison", "chemical", "toxic", "powder", "pill", "narcotic", "cocaine", "overdose"],
    "container_transport": ["bag", "suitcase", "trunk", "vehicle", "car", "van", "box", "cargo", "backpack"],
    "money_transactions": ["money", "cash", "bank", "credit", "transaction", "wallet", "bribe", "fraud", "debt"],
    "everyday_improvised": ["household", "domestic", "tool", "cable", "rope", "tape", "pillow", "towel", "bed", "everyday"]
}



nlp = spacy.load("en_core_web_lg", disable=["tok2vec","attribute_ruler","tagger", "parser", "ner", "lemmatizer"])


vectors=[]

for key, terms in forensic_categories.items():
    for t in terms:
        t_doc=nlp(t)
        if t_doc.has_vector:
            vectors.append(t_doc)


final_entities=set()

for word in entities:
    if len(word.split("_"))>=3:
        continue
    clean_word=word.replace("_"," ")
    clean_word_doc=nlp(clean_word)
    if clean_word_doc.has_vector:
        for v in vectors:
            if clean_word_doc.similarity(v)>0.65:
                final_entities.add(word)
                break



final_entities_list = list(final_entities)


scheduled_relations = "AtLocation, CapableOf, Causes, HasA, HasProperty, IsA, LocatedNear, MadeOf, PartOf, UsedFor"

with open("../data/study_cases.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file, delimiter=";")
    writer.writerow(["entity", "relations"])
    for word in final_entities_list:
        writer.writerow([word, scheduled_relations])
