import json
import pandas as pd
from neo4j import GraphDatabase

# APERTURA CANALE DI COMUNICAZIONE TRA PYTHON E NE04J DESKTOP
# protocollo bolt inventato da Neo4j per far viaggiare i dati dei grafi. Piu performante dell'HTTP
uri = "bolt://localhost:7687" 
driver = GraphDatabase.driver(uri, auth=("neo4j", "YOUR_PASSWORD"))

def import_conceptnet(tx, term, relations):
    query = """
    // MERGE cerca nel database l'entità chiamata "term" se non c'è la crea e le attacca
    // l'etichetta CommonSense
    MERGE (src:Entity {name: $term})
    SET src:CommonSense
    WITH src
    // il primo UNWIND in pratica srotola la lista, una relazione per volta, in rel data per esempio al primo giro vi è la prima relazione coi termini correlati
    UNWIND $rels as rel_data
    // questo unwind srotola i related term, quindi uno per volta
    UNWIND rel_data.targets as target_name
    MERGE (dst:Entity {name: target_name})
    SET dst:CommonSense
    WITH src, dst, rel_data
    // Creazione della relazione di ConceptNet
    // USA LIBRERIA apoc di Neo4j. 
    // PRIMO PARAMETRO: nodo di partenza
    // SECONDO PARAMETRO: nome relazione
    // TERZO E QUARTO PARAMETRI: vuoti, indicano che la relazione viene creata basandosi esclusivamente
    // sui nodi e sul tipo di arco senza salvare attributi aggiuntivi
    // QUINTO PARAMETRO: nodo destinazione
    // YIELD rel : tornami la relazione creata
    // RETURN count(*) per dire a Python che tutto è andato bene
    CALL apoc.merge.relationship(src, rel_data.type, {}, {}, dst) YIELD rel
    RETURN count(*)
    """
    # Neo4j non riesce a leggere i dizionari nidificati
    # quello che arriva in questa funzione è un qualcosa del tipo:
    #   {   IsA: ["...","...","..."],
     #      UsedFor: ["...","...","..."],
     #      .....
    #   }
    # Trasformiamo il dizionario delle relazioni in una lista per UNWIND
    # adesso Neo4j sa che in ogni lista ci saranno le chiavi type (relazione) e targets (related_term)
    # in rels_list si avrà una lista contenente tanti mini dizionari (chiave type e targets, primo value string, secondo value lista di string) 
    # del tipo:
    # [
    #   {
    #       "type": "IsA".
    #       "targets": ["cushion","portable_object"]
    #   },
    #   {
    #       "type":"UsedFor",
    #       "targets":["sleeping","resting"]
    #   }
    # ]
    rels_list = [{"type": k, "targets": v} for k, v in relations.items()]
    tx.run(query, term=term, rels=rels_list)




with open("data/en_conceptnet.json", "r", encoding="utf-8") as f:
    graph = json.load(f)

df_input=pd.read_csv('output/forensic_extractions.csv',sep=';')

with driver.session() as session: #canale logico dentro il driver per eseguire operazioni di lettura/scrittura, con with si chiude automaticamente
    print("Connessione riuscita!\n")
    # Trasforma tutto in stringa (nella colonna object) con astype
    # str da i permessi per accedere a ["object"] per sbloccare i comandi di testo su tutto il contenuto
    # .strip() caccia gli spazzi all'inizio alla fine
    # unique per evitare i doppioni
    csv_entities = df_input["Object"].astype(str).str.strip().unique()
    for entity in csv_entities:
        if entity in graph:
            print(f"Provo a inserire la conoscenza del termine {entity}...\n")
            session.execute_write(import_conceptnet,entity,graph[entity])
            print(f"OK! Inserita conoscenza del termine {entity}!\n")
        else:
            print(f"Entità {entity} non presente nel grafo di ConceptNet!\n")
    print("Chiudo la connessione!\n")
driver.close()