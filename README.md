# HouseMarket 🏠

Un tool indirizzato agli italiani appassionati di immobili per la visualizzazione e l'analisi delle zone e delle quotazioni OMI.

---

## 📋 Istruzioni d'utilizzo

1. **Clonare il repository**
```bash
git clone https://github.com/LemonPower21/HouseMarket.git
cd HouseMarket

```


2. **Scaricare i dati dall'Agenzia delle Entrate**
* Accedi al portale OMI dell'Agenzia delle Entrate dopo aver effettuato l'accesso con **CieID** o **SPID**.
* Scarica le **Forniture OMI con perimetri di zona** relative alla zona di tuo interesse.


3. **Organizzare i file nella cartella**
Estrai tutto il contenuto scaricato all'interno della stessa cartella di progetto dove si trova `HouseMarket.py`. La cartella dovrà contenere:
```text
HouseMarket/
├── HouseMarket.py
├── Zone.csv          # File Zone estratto e rinominato in (Zone.csv)
├── Valori.csv        # File Valori estratto e rinominato in (Valori.csv)
└── *.kml             # I file KML dei perimetri di zona

```


4. **Installare le dipendenze**
Apri il terminale e installa le librerie richieste:
```bash
pip install PyQt5 PyQtWebEngine

```


5. **Avviare l'applicazione**
Posizionati nella cartella in cui sono presenti tutti i file ed esegui lo script:
```bash
python HouseMarket.py

```



---

## 🔒 Privacy e Note Legali

> **Nota:** Non posso includere i file CSV dell'Agenzia delle Entrate direttamente in questo repository per evitare violazioni della normativa sul **GDPR** e rispettare i termini d'uso dei dati istituzionali. Ciascun utente deve scaricare autonomamente i file dal portale ufficiale.

---

## 📬 Contatti e Supporto

Per dubbi, domande, suggerimenti o segnalazioni:

* **Email:** [giotta.francescovitosp@gmail.com](mailto:giotta.francescovitosp@gmail.com)

---
