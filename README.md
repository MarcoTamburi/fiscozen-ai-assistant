# Fiscozen AI Assistant

Assistente AI per supporto fiscale personalizzato sviluppato come soluzione per il test Data Scientist AI di Fiscozen.

L'obiettivo del progetto non è costruire un semplice chatbot FAQ, ma un assistente contestuale in grado di:

* rispondere a domande fiscali e operative
* personalizzare le risposte in base ai dati del cliente
* rispettare il Tone of Voice di Fiscozen
* coinvolgere un consulente umano quando necessario

## Funzionalità principali

### Knowledge Retrieval

L'assistente recupera le informazioni fiscali più rilevanti prima di generare una risposta.

Implementazione attuale:

* suddivisione dei documenti in chunk
* vettorizzazione tramite TF-IDF
* ricerca tramite similarità coseno
* recupero dei documenti più rilevanti

Questo approccio riduce le allucinazioni del modello e migliora la coerenza delle risposte.

### Personalizzazione cliente

Ogni conversazione viene arricchita con informazioni specifiche del cliente:

* regime fiscale
* cassa previdenziale
* commercialista assegnato
* fatturato corrente
* soglia residua del regime forfettario

La stessa domanda può produrre risposte diverse a seconda del profilo cliente selezionato.

### Sistema di Escalation

Alcune richieste non dovrebbero essere gestite automaticamente.

L'assistente effettua l'escalation verso il consulente nei casi che riguardano:

* cambio di regime fiscale
* apertura o chiusura della Partita IVA
* sanzioni fiscali
* accertamenti
* contenziosi in corso

L'obiettivo è simulare un flusso di supporto reale, mantenendo il controllo umano nei casi più delicati.

## Architettura

```text
Cliente
   │
   ▼
Streamlit UI
   │
   ▼
Chat Engine
   │
   ├── Customer Data
   ├── Knowledge Base
   └── Escalation Rules
   │
   ▼
LLM (Llama 3.3 70B)
   │
   ▼
Risposta
```

## Struttura del progetto

```text
.
├── app.py
├── chat.py
├── customer.py
├── knowledge.py
├── prompts.py
├── requirements.txt
├── Dockerfile
└── data
    ├── customer_data.xlsx
    ├── tax_knowledge_1.txt
    ├── tax_knowledge_2.txt
    └── tone_of_voice.txt
```

## Tecnologie utilizzate

* Python
* Streamlit
* Groq API
* Llama 3.3 70B
* Scikit-Learn
* Pandas
* NumPy
* OpenPyXL
* Python-Docx

## Esecuzione locale

### 1. Creare un ambiente virtuale

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Installare le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configurare la chiave API

```bash
export GROQ_API_KEY=your_api_key
```

### 4. Avviare l'applicazione

```bash
streamlit run app.py
```

L'applicazione sarà disponibile all'indirizzo:

```text
http://localhost:8501
```

## Esecuzione con Docker

Costruzione dell'immagine:

```bash
docker build -t fiscozen-ai .
```

Avvio del container:

```bash
docker run -p 8501:8501 \
-e GROQ_API_KEY=your_api_key \
fiscozen-ai
```

## Possibili evoluzioni

La soluzione è stata progettata per essere semplice, riproducibile e facilmente estendibile.

Miglioramenti futuri:

* retrieval basato su embeddings
* vector database (Qdrant, Chroma, Pinecone)
* persistenza della memoria conversazionale
* integrazione diretta con API Fiscozen
* tool calling
* automazione della creazione e modifica delle fatture
* monitoraggio e logging delle conversazioni

## Principio progettuale

> L'intelligenza artificiale accelera il supporto. Il valore nasce dal contesto del cliente e dall'intervento umano nei momenti che contano.

Questo progetto nasce dall'idea che un buon assistente AI non debba limitarsi a generare testo, ma debba utilizzare il contesto corretto, personalizzare la risposta e riconoscere quando è necessario il supporto di un esperto umano.
