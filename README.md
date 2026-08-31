## 🇮🇹 ITALIANO

Questo repository contiene il codice sorgente e i dataset relativi al progetto di tesi "Arricchimento del Knowledge Graph ConceptNet per il dominio forense tramite LLM". Il sistema utilizza il modello LLaMA 3.3 70b - versatile (interrogato tramite Groq API) per generare e dedurre nuova terminologia forense, espandendo le relazioni di senso comune preesistenti di ConceptNet in un contesto investigativo e criminologico.

### Prerequisiti
* Python 3.10 o superiore.
* Chiave API valida fornita da Groq (necessaria per eseguire lo script principale di estrazione).
* Neo4j Desktop (per l'integrazione e la visualizzazione del grafo).

### Come avviare lo script principale "script.py" (Setup iniziale)
**1. Creare un ambiente virtuale:**
`python3 -m venv venv`

**2. Entrare nell'ambiente virtuale (1° metodo: LINUX/MACOS, 2° metodo: WINDOWS):**
`source venv/bin/activate`
*(oppure)*
`.\venv\Scripts\activate`

**3. Installare le dipendenze:**
`pip install -r requirements.txt`

**4. Avviare lo script:**
`python3 script.py`

**Per le esecuzioni successive, basterà ripetere i passaggi 2 e 4. Per uscire dall'ambiente digitare `deactivate`.**

---

### Gestione del grafo di ConceptNet
Se si desidera rigenerare il grafo in sola lingua inglese o il vocabolario locale con le relative relazioni standardizzate *(passaggi non necessari in quanto già scaricati nella cartella /data)*:

**1. Installare il file assertions:**
Scaricare il file `conceptnet-assertions-5.7.0.csv.gz` nella cartella `/data` da [questo link](https://github.com/commonsense/conceptnet5/wiki/Downloads).

**2. Filtrare il grafo (solo lingua inglese):**
`python3 en_filter.py`
*Attenzione: lo script processa milioni di righe, l'operazione può richiedere tempo. Al termine, il grafo in lingua inglese sarà presente nella cartella /data.*

**3. Costruire il vocabolario in lingua inglese del grafo di ConceptNet:**
`python3 vocabulary_builder.py`

**4. Estrarre le relazioni standardizzate:**
`python3 relations_filter.py`
*Dopo l'esecuzione, il vocabolario inglese e l'insieme delle relazioni standardizzate saranno entrambi presenti nella cartella /data.*

---

### Filtraggio delle entità forensi dal grafo inglese
Se si desidera filtrare dal grafo inglese le entità soggette a studio, affiancandole alle 10 relazioni scelte *(passaggio non necessario in quanto già presenti in /data)*:
`python3 entity_extracter.py`
*Terminata l'esecuzione, le entità pronte per l'interrogazione dell'LLM con le relative relazioni saranno presenti in /data/study_cases.csv.*

---

### Integrazione della conoscenza di senso comune in Neo4j
Se si desidera integrare la conoscenza di senso comune delle entità analizzate dal modello (per poter visualizzare l'effettivo arricchimento forense):
`python3 neo4j_script.py`

<br><br>

## 🇬🇧 ENGLISH

This repository contains the source code and datasets for the thesis project "Enrichment of the ConceptNet Knowledge Graph for the Forensic Domain via LLMs". The system uses the LLaMA 3.3 70b - versatile model (queried via the Groq API) to generate and deduce new forensic terminology, expanding ConceptNet's pre-existing commonsense relations within an investigative and criminological context.

### Prerequisites
* Python 3.10 or higher.
* A valid Groq API Key (required to run the main extraction script).
* Neo4j Desktop (for graph integration and visualization).

### How to run the main script "script.py" (Initial Setup)
**1. Create a virtual environment:**
`python3 -m venv venv`

**2. Activate the virtual environment (1st method: LINUX/MACOS, 2nd method: WINDOWS):**
`source venv/bin/activate`
*(or)*
`.\venv\Scripts\activate`

**3. Install dependencies:**
`pip install -r requirements.txt`

**4. Run the script:**
`python3 script.py`

**For subsequent runs, simply repeat steps 2 and 4. To exit the environment, type `deactivate`.**

---

### ConceptNet Graph Management
If you wish to regenerate the English-only graph or the local vocabulary with its standardized relations *(these steps are not necessary as the files are already downloaded in the /data folder)*:

**1. Install the assertions file:**
Download the `conceptnet-assertions-5.7.0.csv.gz` file into the `/data` folder from [this link](https://github.com/commonsense/conceptnet5/wiki/Downloads).

**2. Filter the graph (English only):**
`python3 en_filter.py`
*Warning: the script processes millions of rows, this operation may take time. Once completed, the English graph will be available in the /data folder.*

**3. Build the ConceptNet English vocabulary:**
`python3 vocabulary_builder.py`

**4. Extract standardized relations:**
`python3 relations_filter.py`
*After execution, the English vocabulary and the set of standardized relations will both be present in the /data folder.*

---

### Filtering forensic entities from the English graph
If you want to filter the studied entities from the English graph, pairing them with the 10 selected relations *(not necessary as they are already present in /data)*:
`python3 entity_extracter.py`
*Upon completion, the entities ready for LLM querying along with their respective relations will be located in /data/study_cases.csv.*

---

### Integration of commonsense knowledge in Neo4j
If you wish to integrate the commonsense knowledge of the entities analyzed by the model (to visualize the actual forensic enrichment):
`python3 neo4j_script.py`
