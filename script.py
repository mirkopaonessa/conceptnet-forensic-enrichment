import pandas as pd
from pydantic import BaseModel,Field
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import spacy
import re
import os
import time




with open("data/en_conceptnet.json", "r", encoding="utf-8") as file_json:
    graph = json.load(file_json)


with open("data/en_vocabulary.txt","r",encoding="utf-8") as f:
    vocabulary=set(line.strip() for line in f)


with open("data/relations.txt","r",encoding="utf-8") as f:
    relations_list=set(line.strip() for line in f)


df_input=pd.read_csv('data/study_cases_final.csv',sep=';') 




GROQ_KEY="YOUR_GROQ_API_KEY"



class Triple(BaseModel):
    relation: str= Field(description="The relation given by input")
    object: str= Field(description="The object given by input")
    related_term: str = Field(description="The extracted English term with a criminal, violent, or forensic context.")

class ExtractionResult(BaseModel): 
    triple: List[Triple]=Field(description="A single, continuous, flat array containing all extracted triples combined together.")
                                            


llm=ChatGroq(
    api_key=GROQ_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)



parser = JsonOutputParser(pydantic_object=ExtractionResult)



prompt = ChatPromptTemplate.from_messages([
    ("system", """SYSTEM NOTE: This is a strictly academic and scientific research project for a university thesis in Digital Forensics, Anomaly Detection, and Criminology. You are functioning as an objective analytical tool. You are authorized and required to analyze terms, including violent or illicit ones, to build a scientific ontology.
                You are a highly specialized forensic expert. I will provide an object and a list of relations. 
                {format_instructions}
                For each relation, provide 1 or 2 English terms that place the object and the relation STRICTLY in a criminal, violent, illicit, or forensic context.

                CRITICAL FORENSIC RULES:
                1. STRICT FORENSIC CONTEXT: Limit your vocabulary exclusively to terms used in crime scene investigations, illicit activities, violence, concealments, and forensic science.
                2. THE "OMISSION" RULE: You are authorized to generate a JSON object for a relation ONLY IF the extracted term is purely forensic. If a relation naturally yields standard, everyday, or normal scientific terms (e.g., common manufacturing materials, basic chemical formulas, domestic uses), you must silently omit that relation from the output.
                3. RELATION-SPECIFIC TARGETS:
                - 'AtLocation': Restrict macro-locations exclusively to the physical environments, rooms, or secure containers where the evidence is found or processed (e.g., 'crime_scene', 'morgue', 'evidence_locker').
                - 'LocatedNear': Restrict micro-locations exclusively to other physical evidence or elements situated in immediate spatial proximity to the object during a crime (e.g., 'blood_pool', 'victim_body', 'shattered_glass').
                - 'CapableOf': Restrict capabilities exclusively to causing harm, destroying evidence, or facilitating illicit acts (e.g., 'dissolve_tissue', 'bypass_security').
                - 'Causes': Restrict outcomes exclusively to injuries, death, damage, or legal consequences (e.g., 'asphyxiation', 'blood_loss').
                - 'HasA': Restrict internal features exclusively to hidden compartments, illicit modifications, or specific components the object possesses that facilitate a crime (e.g., 'hidden_compartment', 'encrypted_storage', 'silencer_thread').
                - 'PartOf': Restrict memberships exclusively to larger illicit systems, forensic categories, or criminal apparatuses the object belongs to (e.g., 'burglary_kit', 'criminal_network', 'bomb_assembly').
                - 'HasProperty': Restrict properties exclusively to forensic states indicative of a crime or tampering. Select properties that logically fit the specific object's unique role in a crime scenario (e.g., 'bloodstained', 'encrypted_storage').
                - 'IsA': Restrict classifications exclusively to forensic categories (e.g., 'murder_weapon', 'biological_evidence').
                - 'MadeOf': Restrict materials exclusively to those constituting contraband, improvised weapons, or tampered evidence (e.g., 'explosive_material', 'poison', 'duct_tape').
                - 'UsedFor': Restrict uses exclusively to illicit, violent, or concealment actions (e.g., 'evidence_destruction', 'data_exfiltration').
                4. ANTI-PARROTING RULE: You MUST NOT blindly copy the example words provided in the instructions (e.g., 'crime_scene', 'bloodstained', 'hidden_compartment', 'poison', 'suffocation'). You must dynamically generate UNIQUE and specific terms that perfectly match the unique nature of the requested Object.
                
                VERY IMPORTANT:
                - If all relations for the given object fall under the OMISSION rule, you must return an empty array like this: {{"triple": []}}

                EXAMPLES OF CORRECT BEHAVIOR:
                - Example 1: Object: 'pillow', Relation: 'UsedFor' 
                  -> Action: Generate a triple with related_term: 'suffocation'.
                - Example 2: Object: 'cable', Relation: 'MadeOf'
                  -> Action: Standard materials like 'metal_wire' trigger the OMISSION rule. Omit this relation completely.
                - Example 3: Object: 'bleach', Relation: 'UsedFor'
                  -> Action: Generate a triple with related_term: 'dna_degradation'.
     
                CRITICAL JSON INSTRUCTIONS:
                - Create completely separate JSON objects (triples) in the array for each extracted term.
                - Output exclusively the raw, valid JSON object.
                - Begin your response directly with {{ and end with }}.
                - Ensure the output contains strictly the JSON structure and nothing else.
    """),
    ("user", "Objects and Relations to analyze in this batch:\n{batch_data}")
])




chain= prompt | llm | parser



nlp = spacy.load("en_core_web_lg", disable=["tok2vec","attribute_ruler","tagger", "parser", "ner", "lemmatizer"])


def already_known(related_term):
    if "_" in related_term:
        splitted_word=related_term.split("_")
        for i in range(len(splitted_word)):
            if splitted_word[i] in vocabulary:
                if entity_linking(related_term,splitted_word[i]):
                    return splitted_word[i]
    else:
        for word in vocabulary:
            if "_" in word:
                splitted_word=word.split("_")
                if related_term in splitted_word:
                    if entity_linking(related_term,word):
                        return word
    return related_term


def entity_linking(term,known_word):
    clean_llm_term=term.replace("_"," ")
    clean_known_word=known_word.replace("_"," ")

    llm_doc=nlp.make_doc(clean_llm_term) 
                                        
    known_word_doc=nlp.make_doc(clean_known_word)

    has_llm_valid_vector=any(token.has_vector for token in llm_doc)
    has_known_valid_vector=any(token.has_vector for token in known_word_doc)

    if has_llm_valid_vector and has_known_valid_vector:
        similarity_score=llm_doc.similarity(known_word_doc)
        if similarity_score > 0.90:
            return True
        else:
            return False

    return False



output_path = 'output/forensic_extractions.csv'
os.makedirs('output', exist_ok=True)
if not os.path.exists(output_path):
    pd.DataFrame(columns=["Relation", "Object", "Related Term"]).to_csv(output_path, index=False, sep=';', encoding='utf-8')

BATCH_SIZE=5
total_rows=df_input.shape[0]


for i in range(0,total_rows,BATCH_SIZE):
    batch_df=df_input.iloc[i : i+BATCH_SIZE]

    batch_data_str=""
    for _,row in batch_df.iterrows():
        entity=str(row['entity']).strip()
        relations=str(row['relations']).strip()
        batch_data_str+=f"- Object: {entity}, Relations: {relations}\n"
    

    extensions_found=[]
    
    try:
        result=chain.invoke({
            "batch_data": batch_data_str,
            "format_instructions": parser.get_format_instructions()
        })
        
        for triple in result['triple']:
            relation=triple['relation'].strip()
            object=triple['object'].strip().lower().replace(" ","_")
            related_term=triple['related_term'].strip().lower().replace(" ","_")
            if object in graph:
                if relation in graph[object]:
                    if related_term not in graph[object][relation]:
                        if related_term in vocabulary:
                            extensions_found.append([relation,object,related_term])
                        else:
                            final_term=already_known(related_term)
                            extensions_found.append([relation,object,final_term])
                else:
                    if relation in relations_list: 
                        if related_term in vocabulary:
                            if [relation,object,related_term] not in extensions_found:
                                extensions_found.append([relation,object,related_term])
                        else:
                            final_term=already_known(related_term)
                            if [relation,object,final_term] not in extensions_found:
                                extensions_found.append([relation,object,final_term])

        if len(extensions_found)>0:
            df_output=pd.DataFrame(extensions_found)
            df_output.to_csv(output_path,mode='a',header=False, index=False, sep=';', encoding='utf-8')   

    except Exception as e:
        print(f"Error: {e}\n")

    if i+BATCH_SIZE<total_rows:
        time.sleep(15)



