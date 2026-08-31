import json
import pandas as pd
from neo4j import GraphDatabase


uri = "bolt://localhost:7687" 
driver = GraphDatabase.driver(uri, auth=("neo4j", "YOUR_PASSWORD"))

def import_conceptnet(tx, term, relations):
    query = """
    MERGE (src:Entity {name: $term})
    SET src:CommonSense
    WITH src
    UNWIND $rels as rel_data
    UNWIND rel_data.targets as target_name
    MERGE (dst:Entity {name: target_name})
    SET dst:CommonSense
    WITH src, dst, rel_data
    CALL apoc.merge.relationship(src, rel_data.type, {}, {}, dst) YIELD rel
    RETURN count(*)
    """
    rels_list = [{"type": k, "targets": v} for k, v in relations.items()]
    tx.run(query, term=term, rels=rels_list)




with open("data/en_conceptnet.json", "r", encoding="utf-8") as f:
    graph = json.load(f)

df_input=pd.read_csv('output/forensic_extractions.csv',sep=';')

with driver.session() as session: 
    csv_entities = df_input["Object"].astype(str).str.strip().unique()
    for entity in csv_entities:
        if entity in graph:
            session.execute_write(import_conceptnet,entity,graph[entity])
        
driver.close()