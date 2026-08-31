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




################ SEZIONE APERTURA DATI IN INPUT #######################

#apertura json contenente il grafo di ConceptNet, Python riesce a convertire il JSON in un dizionario di dizionari di liste
with open("data/en_conceptnet.json", "r", encoding="utf-8") as file_json:
    graph = json.load(file_json)


with open("data/en_vocabulary.txt","r",encoding="utf-8") as f:
    vocabulary=set(line.strip() for line in f)


with open("data/relations.txt","r",encoding="utf-8") as f:
    relations_list=set(line.strip() for line in f)


df_input=pd.read_csv('data/study_cases_final.csv',sep=';') #pandas è programmato colonne separate da , nel nostro csv le colonne sono separate da ;

#########################################################################





####################### SEZIONE INIZIALIZZAZIONE GROQ + PYDANTIC + LANGCHAIN ####################

#API KEY di Groq
GROQ_KEY="YOUR_GROQ_API_KEY"


#creo il formato in cui l'LLM mi dovrà rispondere
#descrizioni sono importanti poichè l'LLM le ispeziona logicamente per capire esattamente cosa deve inserire in ogni variabile
class Triple(BaseModel):
    relation: str= Field(description="The relation given by input")
    object: str= Field(description="The object given by input")
    related_term: str = Field(description="The extracted English term with a criminal, violent, or forensic context.")

class ExtractionResult(BaseModel): #risultato è array di oggetti triple
    triple: List[Triple]=Field(description="A single, continuous, flat array containing all extracted triples combined together.")
                                            #necessario per evitare errore 400 (dati malformati), senza questa descrizione e senza le critical instructions
                                            #avrebbe potuto generare una lista per ogni relazione (noi vogliamo triple contigue)

#inizializzo groq
llm=ChatGroq(
    api_key=GROQ_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)



#contiene il metodo get format instructions, che genera una sorta di testo in inglese che spiega al llm come formattare l'output
# usato per prima cosa (dopo aver eliminato eventuale rumore del LLM) 
# controllare se l'output del modello è un JSON, seconda cosa convertirlo in un dizionario python, 
# terza cosa passa a pydantic questo dizionario, il quale controlla se combacia con le classi Pydantic.
parser = JsonOutputParser(pydantic_object=ExtractionResult)



#prompt in stile LangChain
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



# serve piu che altro per modelli reasoning come qwen che "pensano ad alta voce"
# senza questo metodo modelli come qwen restituiscono anche il blocco del ragionamento, invalidando l'output
def output_reasoning_cleaning(ai_message):
    # ai_message non contiene solo il testo ma anche altri dati come metadati, token utilizzati etc...
    # il metodo content prende solo il testo
    text = ai_message.content
    print(f"OUTPUT DI QWEN: {text}\n")
    # re.sub -> sostituisci
    # <think>.*?</think> -> tutto ciò che c'è tra i tag think
    # '' con il niente
    # re.DOTALL per evitare di far terminare la regex quando incontra uno \n , prendendo tutto il blocco effettivo
    cleaned_text = re.sub(r'<think>.*?(?:</think>|$)', '', text, flags=re.DOTALL)
    # rimuove i backtick del markdown che fanno crashare il parser
    cleaned_text = re.sub(r'```(?:json)?', '', cleaned_text)
    # rimuove eventuali spazi vuoti o ritorni a capo extra
    return cleaned_text.strip()


# se uso gpt
def clean_gpt_output(ai_message):
    text=ai_message.content
    # Trova dove inizia e dove finisce realmente il JSON
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1:
        cleaned_json = text[start:end+1]
        return cleaned_json
    
    return text.strip()


#pipeline di inferenza
#prompt riempie i buchi nel suddetto, quindi inserisce le entità, le relazioni e le format instructions
#llm si collega al llm fa generare la risposta
#parser controlla che l'output combacia con lo schema Pydantic e converte il JSON in un dizionario Python
chain= prompt | llm | parser


#######################################################################################




################ SEZIONE SPACY ##################

#noi abbiamo bisogno solo del vettore, disattiviamo queste cose perchè calcolano qualcosa che non ci serve, aumentiamo l'efficienza
nlp = spacy.load("en_core_web_lg", disable=["tok2vec","attribute_ruler","tagger", "parser", "ner", "lemmatizer"])


def already_known(related_term):
    # PAROLA COMPOSTA
    if "_" in related_term:
        splitted_word=related_term.split("_")
        for i in range(len(splitted_word)):
            # verifico se qualche parola del vocabolario è contenuta nel termine generato
            if splitted_word[i] in vocabulary:
                # STEP 3:
                # verifico la similarità tra termine del LLM e sotto termine del LLM contenuto nel vocabolario
                if entity_linking(related_term,splitted_word[i]):
                    return splitted_word[i]
    # PAROLA SINGOLA
    else:
        for word in vocabulary:
            if "_" in word:
                splitted_word=word.split("_")
                # verifico se il termine generato è una sottoparola di una parola composta presente nel vocabolario
                if related_term in splitted_word:
                    # STEP 3:
                    # verifico similarità tra termine del LLM e parola composta del vocabolario con all'interno il termine del LLM
                    if entity_linking(related_term,word):
                        return word
    return related_term


def entity_linking(term,known_word):
    clean_llm_term=term.replace("_"," ")
    clean_known_word=known_word.replace("_"," ")

    llm_doc=nlp.make_doc(clean_llm_term) # llm_doc è un oggetto Doc : conterrà parola grezza + token (più token se parola composta poichè viene spezzettata)
                                        # doc è collegato al nlp.vocab, che sa esattamente dove prendere il vettore della parola
    known_word_doc=nlp.make_doc(clean_known_word)

    has_llm_valid_vector=any(token.has_vector for token in llm_doc)
    has_known_valid_vector=any(token.has_vector for token in known_word_doc)

    if has_llm_valid_vector and has_known_valid_vector:
        # il metodo similarity in caso di parola composta riesce a calcolare la media vettoriale delle parole che formano il termine composto
        # in caso di singola parola torna solo il vettore del singolo termine
        similarity_score=llm_doc.similarity(known_word_doc)
        if similarity_score > 0.90:
            print(f"Sostituisco il termine {term} con il termine {known_word}, similarità al {similarity_score}\n")
            return True
        else:
            print(f"[-] NON sostituisco '{term}' con '{known_word}' (Similarità troppo bassa: {similarity_score})\n")
            return False

    print(f"NON sostituisco il termine {term} con il termine {known_word}\n")
    return False


#####################################################################



################### SEZIONE ESTRAZIONE ANOMALIE ######################
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
    
    print(f"\n=======================================================")
    print(f"Elaborazione Batch {i//BATCH_SIZE + 1} di {(total_rows + BATCH_SIZE - 1)//BATCH_SIZE}")
    print(f"Entità in elaborazione...")

    #entity=str(df_input['entity'].iloc[i]).strip() #prendo prima entità, poi seconda ecc....
    #relations=str(df_input['relations'].iloc[i]).strip() # " "

    extensions_found=[]
    
    try:
        result=chain.invoke({
            "batch_data": batch_data_str,
            "format_instructions": parser.get_format_instructions()
        })
        #LangChain riceve una stringa JSON dal server di Groq del tipo:
        #triple:[
        #   {
        #       "relation":"UsedFor",
        #       "object":"knife",
        #       "related_term":"stabbing"
        #   },
        #   {
        #       "relation":"UsedFor",
        #       "object":"knife",
        #       "related_term":"slashing"
        #   }
        #]
        #il risultato sarà un oggetto ExtractionResult, al cui interno vi è la lista di triple
        for triple in result['triple']:
            relation=triple['relation'].strip()
            object=triple['object'].strip().lower().replace(" ","_")
            related_term=triple['related_term'].strip().lower().replace(" ","_")
            if object in graph:
                if relation in graph[object]:
                    if related_term not in graph[object][relation]:
                        # STEP 1: controllo se il termine generato è nel vocabolario. In caso negativo STEP 2
                        if related_term in vocabulary:
                            print(f"Termine {related_term} da associare all'entità {object} tramite relazione {relation} già presente nel grafo di ConceptNet, la aggiungo normalmente!\n")
                            extensions_found.append([relation,object,related_term])
                        else:
                            # STEP 2: due casi
                            # PAROLA SINGOLA: verifico se è contenuta in una parola composta del vocabolario
                            # PAROLA COMPOSTA: verifico se una parola del vocabolario è contenuta nella parola composta generata
                            final_term=already_known(related_term)
                            extensions_found.append([relation,object,final_term])
                    else:
                        print(f"Termine {related_term} già presente nella lista di termini correlati all'entità {object} tramite la relazione {relation}\n")
                else:
                    if relation in relations_list: # se la relazione è presente nelle 36 standardizzate, la usiamo
                        print(f"Relazione {relation} non presente nella lista delle relazioni correlate al termine {object}, la creiamo!\n")
                        if related_term in vocabulary:
                            if [relation,object,related_term] not in extensions_found:
                                print(f"Termine {related_term} da associare all'entità {object} tramite relazione {relation} già presente nel grafo di ConceptNet, la aggiungo normalmente!\n")
                                extensions_found.append([relation,object,related_term])
                        else:
                            final_term=already_known(related_term)
                            if [relation,object,final_term] not in extensions_found:
                                extensions_found.append([relation,object,final_term])

        if len(extensions_found)>0:
            df_output=pd.DataFrame(extensions_found)
            df_output.to_csv(output_path,mode='a',header=False, index=False, sep=';', encoding='utf-8')   
            print(f"Salvate {len(extensions_found)} triple nel file CSV.\n")
        else:
            print("Nessuna tripla estratta in questo batch (Omission Rule applicata).\n")

    except Exception as e:
        print(f"Errore: {e}\n")

    if i+BATCH_SIZE<total_rows:
        time.sleep(15)

#if len(anomalies_found)>0:
    #df_output = pd.DataFrame(anomalies_found, columns=["Relation", "Object", "Related Term"])
    #output_path = 'output/extracted_anomalies.csv'
    #df_output.to_csv(output_path, index=False, sep=';', encoding='utf-8')


###########################  END  ################################

