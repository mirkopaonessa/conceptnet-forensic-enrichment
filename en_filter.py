import gzip
import json


GZ_PATH = "data/conceptnet-assertions-5.7.0.csv.gz"
OUTPUT_PATH = "data/en_conceptnet.json"


english_graph = {} 

with gzip.open(GZ_PATH, 'rt', encoding='utf-8') as file_in:   
    for line in file_in:
        parts = line.split('\t') 
        
        if len(parts) >= 4:
            relation_node = parts[1] 
            start_node = parts[2]     
            end_node = parts[3]       
            
            if start_node.startswith('/c/en/') and end_node.startswith('/c/en/'): 
                try: 
                    relation = relation_node.split('/')[2].strip() 
                    start_word = start_node.split('/')[3].lower().strip() 
                    end_word = end_node.split('/')[3].lower().strip()
                    
                    if start_word not in english_graph: 
                        english_graph[start_word] = {} 
                        
                    if relation not in english_graph[start_word]: 
                        english_graph[start_word][relation] = set() 
                        
                    
                    english_graph[start_word][relation].add(end_word) 
        
                except IndexError: 
                    pass


final_graph = {}
for word, relation in english_graph.items():
    final_graph[word] = {}
    for rel, words_list in relation.items():
        final_graph[word][rel] = list(words_list)

with open(OUTPUT_PATH, 'w', encoding='utf-8') as file_out:
    json.dump(final_graph, file_out) 

