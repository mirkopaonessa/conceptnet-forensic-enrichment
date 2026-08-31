### Come avviare lo script principale "script.py" (Setup iniziale)
Requisiti: Python 3.10 o superiore  
**1. Creare un ambiente virtuale:**
```
python3 -m venv venv
```
**2. Entrare nell'ambiente virtuale (1° metodo: LINUX/MACOS, 2° metodo: WINDOWS):**
```
source venv/bin/activate
```
```
.\venv\Scripts\activate
```
**3. Installare le dipendenze:**
```
pip install -r requirements.txt
```
**4. Avviare lo script**
```
python3 script.py
```

**Per le esecuzioni successive, basterà ripetere i passaggi 2 e 4. Per uscire dall'ambiente digitare deactivate**




**Gestione del grafo di ConceptNet**  
Se si desidera rigenerare il grafo in sola lingua inglese o il vocabolario locale (non necessari in quanto già scaricati nella cartella /data):

**1. Installare nella cartella /data il file assertions (conceptnet-assertions-5.7.0.csv.gz) presente a questo link:** 
```
https://github.com/commonsense/conceptnet5/wiki/Downloads
```
**2. Filtrare il grafo (solo lingua inglese):**
```
python3 en_filter.py
```
Attenzione: lo script processa milioni di righe, l'operazione può richiedere tempo.

**Costruire il vocabolario in lingua inglese del grafo di ConceptNet:**
```
python3 vocabulary_builder.py
```
