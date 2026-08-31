import gzip
import json

#da modellare in base a come abbiamo salvato noi il file di ConceptNet
GZ_PATH = "data/conceptnet-assertions-5.7.0.csv.gz"
OUTPUT_PATH = "data/en_conceptnet.json"

#print("Inizio filtraggio\n")

# grafo["pillow"]["UsedFor"] = set("sleep", "rest")
english_graph = {} # dizionario principale
row_counter = 0
saved_counter = 0

with gzip.open(GZ_PATH, 'rt', encoding='utf-8') as file_in: #read text, apre il file compresso decomprimendolo mano mano
    #ogni linea è del tipo /a/[/r/UsedFor/,/c/en/pillow/,/c/en/sleep/]    /r/UsedFor    /c/en/pillow    /c/en/sleep    {"dataset": "/d/conceptnet/4/en", "license": "cc:by/4.0", "sources": [...], "weight": 2.0}
    for line in file_in:
        #row_counter += 1
        
        #if row_counter % 1000000 == 0:
         #   print(f"Lette {row_counter} milioni di righe. Salvati {saved_counter} archi.")
            
        parts = line.split('\t') #separa da tab poichè conceptnet usa tab per separare gli elementi
        
        # 0->URI, 1->Relazione, 2->StartNode, 3->EndNode, 4->JSON
        if len(parts) >= 4:
            relation_node = parts[1] # Es. /r/UsedFor
            start_node = parts[2]     # Es. /c/en/pillow
            end_node = parts[3]       # Es. /c/en/sleep
            
            if start_node.startswith('/c/en/') and end_node.startswith('/c/en/'): #mi prendo tutto ciò che è inglese
                try: # essendo creato tramite crowdsourcing potrebbero esserci righe buggate es. senza parola
                    # Estraiamo i dati puliti
                    relation = relation_node.split('/')[2].strip() # Da "/r/UsedFor" a "UsedFor"
                    start_word = start_node.split('/')[3].lower().strip() #in minuscolo e caccio spazi iniziali e finali
                    end_word = end_node.split('/')[3].lower().strip()
                    
                    # Costruiamo il dizionario nidificato per la parola di partenza
                    if start_word not in english_graph: #se la start_word non è nel grafo creo la sua "istanza"
                        english_graph[start_word] = {} #dizionari per la parola "start_word" del tipo pillow-> UsedFor:(),IsA:()
                        
                    if relation not in english_graph[start_word]: #se la relazione interessata non è nel set di relazioni della parola a sinistra
                        english_graph[start_word][relation] = set() #creo l'insieme di quella relazione del tipo pillow: {usedFor:{},....}
                        # pillow->UsedFor->()
                    # Salviamo la parola a destra per la giusta relazione
                    english_graph[start_word][relation].add(end_word) #inserisco in usedFor per esempio sleep (seguendo l'esempio di sopra)
                    # pillow->UsedFor->(suffocate,...)
                    #saved_counter += 1
                    
                except IndexError: # evito righe buggate es. /c/en/""
                    pass

#print(f"Filtraggio completato. Salvati {saved_counter} archi validi.")

# converto i set in list per compatibilità con il json
final_graph = {}
for word, relation in english_graph.items():
    final_graph[word] = {}
    for rel, words_list in relation.items():
        final_graph[word][rel] = list(words_list)

with open(OUTPUT_PATH, 'w', encoding='utf-8') as file_out:
    json.dump(final_graph, file_out) #creo il mio mini ConceptNet (versione inglese)

#print("English Knowledge Graph di ConceptNet creato.")