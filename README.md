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
