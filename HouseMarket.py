import csv
import os
import sys
import multiprocessing
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer

# --- CODICI COLORE ANSI ---
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

class FinestraMappaKML(QMainWindow):
    """Finestra GUI PyQt5 locale per la visualizzazione avanzata del file KML, ricerca indirizzi ed esportazione PDF."""
    def __init__(self, percorso_kml, nome_comune):
        super().__init__()
        self.nome_comune = nome_comune
        self.setWindowTitle(f"Visualizzatore OMI - {nome_comune}")
        self.setGeometry(100, 100, 1100, 800)

        with open(percorso_kml, 'r', encoding='utf-8', errors='ignore') as f:
            kml_content = f.read().replace('\n', ' ').replace("'", "\\'")

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mappa OMI</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            
            <!-- Leaflet CSS & JS -->
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script src="https://unpkg.com/@tmcw/togeojson@5.8.1/dist/togeojson.umd.js"></script>

            <style>
                html, body, #map {{ height: 100%; margin: 0; padding: 0; font-family: sans-serif; }}
                #search-box {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 1000;
                    background: white;
                    padding: 8px;
                    border-radius: 6px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                    display: flex;
                    gap: 5px;
                }}
                #search-input {{
                    width: 220px;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    outline: none;
                }}
                #search-btn {{
                    padding: 5px 10px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                #search-btn:hover {{ background: #0056b3; }}
                .leaflet-popup-content-wrapper {{ border-radius: 4px; padding: 5px; }}
            </style>
        </head>
        <body>
            <div id="search-box">
                <input type="text" id="search-input" placeholder="Cerca via o indirizzo..." onkeydown="if(event.key==='Enter') cercaStrada()" />
                <button id="search-btn" onclick="cercaStrada()">Cerca</button>
            </div>

            <div id="map"></div>

            <script>
                var map = L.map('map').setView([41.9028, 12.4964], 6);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }}).addTo(map);

                var searchMarker = null;

                function cercaStrada() {{
                    var query = document.getElementById('search-input').value;
                    if (!query) return;

                    var url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query + ' {nome_comune}');
                    
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {{
                            if (data && data.length > 0) {{
                                var lat = parseFloat(data[0].lat);
                                var lon = parseFloat(data[0].lon);
                                
                                if (searchMarker) map.removeLayer(searchMarker);

                                searchMarker = L.marker([lat, lon]).addTo(map)
                                    .bindPopup('<b>' + data[0].display_name + '</b>')
                                    .openPopup();

                                map.setView([lat, lon], 16);
                            }} else {{
                                alert('Indirizzo o strada non trovata.');
                            }}
                        }})
                        .catch(err => alert('Errore durante la ricerca. Verifica la connessione internet.'));
                }}

                try {{
                    var parser = new DOMParser();
                    var kmlDoc = parser.parseFromString('{kml_content}', 'text/xml');
                    var geojson = toGeoJSON.kml(kmlDoc);

                    var layer = L.geoJson(geojson, {{
                        style: function(feature) {{
                            var fill = feature.properties.fill || '#3388ff';
                            var opacity = feature.properties['fill-opacity'] || 0.6;
                            var stroke = feature.properties.stroke || '#000000';
                            return {{
                                fillColor: fill,
                                fillOpacity: opacity,
                                color: stroke,
                                weight: 1.5
                            }};
                        }},
                        onEachFeature: function(feature, layer) {{
                            if (feature.properties) {{
                                var title = feature.properties.name || 'Zona OMI';
                                var desc = feature.properties.description || '';
                                var popupContent = '<b>' + title + '</b><br>' + desc;
                                layer.bindPopup(popupContent);
                            }}
                        }}
                    }}).addTo(map);

                    if (layer.getBounds().isValid()) {{
                        map.fitBounds(layer.getBounds());
                    }}
                }} catch(e) {{
                    console.error("Errore KML:", e);
                }}
            </script>
        </body>
        </html>
        """
        
        self.browser = QWebEngineView()
        self.browser.setHtml(html_code)
        self.setCentralWidget(self.browser)

    def esporta_pdf(self, percorso_salvataggio=None):
        """Esporta la mappa visualizzata in formato PDF."""
        if not percorso_salvataggio:
            percorso_salvataggio = f"Mappa_{self.nome_comune.replace(' ', '_')}.pdf"
        self.browser.page().printToPdf(percorso_salvataggio)

def _avvia_processo_gui(file_trovato, nome_comune, salva_pdf=False):
    """Funzione target eseguita in un processo parallelo per non bloccare la CLI."""
    app = QApplication(sys.argv)
    finestra = FinestraMappaKML(file_trovato, nome_comune)
    finestra.show()
    
    if salva_pdf:
        nome_pdf = f"Mappa_OMI_{nome_comune.replace(' ', '_')}.pdf"
        QTimer.singleShot(2500, lambda: finestra.esporta_pdf(nome_pdf))

    app.exec_()

def apri_gui_kml(codice_comune, info_comune, salva_pdf=False):
    """Apre MappeCatasto nel browser predefinito e la mappa KML in una finestra PyQt5 locale."""
    try:
        webbrowser.open_new_tab("https://mappecatasto.it/c1.htm")
    except Exception as e:
        print(f"{RED}[!] Errore nell'apertura del browser: {e}{RESET}")

    file_trovato = None
    possibili_nomi = [
        f"{codice_comune}.kml",
        f"{info_comune.get('amm', '')}.kml",
        f"{info_comune.get('cat', '')}.kml",
        f"{info_comune.get('istat', '')}.kml"
    ]

    for nome in possibili_nomi:
        if nome and os.path.exists(nome):
            file_trovato = nome
            break

    if file_trovato:
        print(f"\n{GREEN}[+] Aperto MappeCatasto.{RESET}")
        print(f"{GREEN}[+] Avvio mappa KML:{RESET} {BOLD}{file_trovato}{RESET}")
        
        p = multiprocessing.Process(target=_avvia_processo_gui, args=(file_trovato, info_comune['nome'], salva_pdf))
        p.daemon = True
        p.start()
    else:
        print(f"\n{YELLOW}[!] Nessun file KML trovato per questo comune (es. {codice_comune}.kml). Aperto solo MappeCatasto.it.{RESET}")

def pulisci_schermo():
    os.system('cls' if os.name == 'nt' else 'clear')

def pulisci_numero(valore_str):
    if not valore_str:
        return None
    valore_clean = valore_str.replace('.', '').replace(',', '.').strip()
    try:
        return float(valore_clean)
    except ValueError:
        return None

def carica_dati_zone(file_zone):
    comuni = {}
    with open(file_zone, mode='r', encoding='utf-8-sig') as f:
        next(f)
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            row_clean = {k.strip(): v.strip() for k, v in row.items() if k}
            
            istat = row_clean.get('Comune_ISTAT', '')
            cat = row_clean.get('Comune_cat', '')
            amm = row_clean.get('Comune_amm', '')
            nome_comune = row_clean.get('Comune_descrizione', '')
            zona = row_clean.get('Zona', '')
            zona_descr = row_clean.get('Zona_Descr', '')
            fascia = row_clean.get('Fascia', '')

            if not istat and not cat and not amm:
                continue

            for key in [istat, cat, amm]:
                if key:
                    if key not in comuni:
                        comuni[key] = {
                            'nome': nome_comune,
                            'istat': istat,
                            'cat': cat,
                            'amm': amm,
                            'zone': {}
                        }
                    comuni[key]['zone'][zona] = {
                        'descr': zona_descr,
                        'fascia': fascia
                    }
    return comuni

def salva_su_txt(nome_comune, codice_comune, etichetta_zona, righe_dati, medie):
    nome_file = f"Quotazioni_{nome_comune.replace(' ', '_')}_{etichetta_zona}.txt"
    
    with open(nome_file, mode='w', encoding='utf-8') as f:
        zona_testo = "TUTTE LE ZONE" if etichetta_zona == "TUTTE" else etichetta_zona
        f.write("┌──────┬────────────────────────────────────────┬──────────────┬───────────────────┬───────────────────┬───────────────────┬───────────────────┐\n")
        f.write(f"│ VALORI DI MERCATO IMMOBILIARI  │  Comune: {nome_comune} ({codice_comune})  │  Zona: {zona_testo:<52}│\n")
        f.write("├──────┼────────────────────────────────────────┼──────────────┼───────────────────┼───────────────────┼───────────────────┼───────────────────┤\n")
        f.write(f"│ {'Zona':<4} │ {'Tipologia':<38} │ {'Stato':<12} │ {'Compr. Min (€/m²)':<17} │ {'Compr. Max (€/m²)':<17} │ {'Loc. Min (€/m²/m)':<17} │ {'Loc. Max (€/m²/m)':<17} │\n")
        f.write("├──────┼────────────────────────────────────────┼──────────────┼───────────────────┼───────────────────┼───────────────────┼───────────────────┤\n")
        
        for r in righe_dati:
            f.write(f"│ {r['zona']:<4} │ {r['tipologia']:<38} │ {r['stato']:<12} │ {r['compr_min']:<17} │ {r['compr_max']:<17} │ {r['loc_min']:<17} │ {r['loc_max']:<17} │\n")
            
        f.write("└──────┴────────────────────────────────────────┴──────────────┴───────────────────┴───────────────────┴───────────────────┴───────────────────┘\n")
        
        if medie:
            f.write("\n=====================================================================================================================\n")
            f.write(f" PREZZI MEDI AL M²\n")
            f.write("=====================================================================================================================\n")
            f.write(f" • Compravendita Media : {medie['compr_media']:.2f} €/m²  (Min Media: {medie['compr_min_med']:.2f} € | Max Media: {medie['compr_max_med']:.2f} €)\n")
            f.write(f" • Locazione Media    : {medie['loc_media']:.2f} €/m²/mese (Min Media: {medie['loc_min_med']:.2f} € | Max Media: {medie['loc_max_med']:.2f} €)\n")
            f.write("=====================================================================================================================\n")

    print(f"{GREEN}[✓] Dettagli salvati con successo nel file: {BOLD}{nome_file}{RESET}\n")

def mostra_dettagli_valori(file_valori, info_comune, codice_comune, zona_scelta):
    mostra_tutto = (zona_scelta == "T")
    etichetta_header = "TUTTE LE ZONE" if mostra_tutto else zona_scelta

    print(f"\n{CYAN}┌──────┬────────────────────────────────────────┬──────────────┬───────────────────┬───────────────────┬───────────────────┬───────────────────┐{RESET}")
    print(f"{CYAN}│{RESET} {BOLD}VALORI DI MERCATO IMMOBILIARI{RESET}  │  Comune: {YELLOW}{info_comune['nome']} ({codice_comune}){RESET}  │  Zona: {YELLOW}{etichetta_header:<52}{RESET} {CYAN}│{RESET}")
    print(f"{CYAN}├──────┼────────────────────────────────────────┼──────────────┼───────────────────┼───────────────────┼───────────────────┼───────────────────┤{RESET}")
    
    header = f"{CYAN}│{RESET} {BOLD}{'Zona':<4}{RESET} {CYAN}│{RESET} {BOLD}{'Tipologia':<38}{RESET} {CYAN}│{RESET} {BOLD}{'Stato':<12}{RESET} {CYAN}│{RESET} {BOLD}{'Compr. Min (€/m²)':<17}{RESET} {CYAN}│{RESET} {BOLD}{'Compr. Max (€/m²)':<17}{RESET} {CYAN}│{RESET} {BOLD}{'Loc. Min (€/m²/m)':<17}{RESET} {CYAN}│{RESET} {BOLD}{'Loc. Max (€/m²/m)':<17}{RESET} {CYAN}│{RESET}"
    print(header)
    print(f"{CYAN}├──────┼────────────────────────────────────────┼──────────────┼───────────────────┼───────────────────┼───────────────────┼───────────────────┤{RESET}")

    trovato = False
    righe_da_salvare = []
    i = 0

    c_min_list, c_max_list = [], []
    l_min_list, l_max_list = [], []

    with open(file_valori, mode='r', encoding='utf-8-sig') as f:
        next(f)
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            row_clean = {k.strip(): v.strip() for k, v in row.items() if k}

            riga_istat = row_clean.get('Comune_ISTAT', '')
            riga_cat = row_clean.get('Comune_cat', '')
            riga_amm = row_clean.get('Comune_amm', '')
            riga_zona = row_clean.get('Zona', '')

            match_zona = mostra_tutto or (riga_zona.upper() == zona_scelta.upper())

            if (codice_comune in [riga_istat, riga_cat, riga_amm]) and match_zona:
                trovato = True
                
                tipologia = ""
                for k, v in row_clean.items():
                    if k.lower().startswith("descr_tip"):
                        tipologia = v
                        break
                if not tipologia:
                    tipologia = "N/D"

                stato = row_clean.get('Stato', '')
                compr_min = row_clean.get('Compr_min', '')
                compr_max = row_clean.get('Compr_max', '')
                loc_min = row_clean.get('Loc_min', '')
                loc_max = row_clean.get('Loc_max', '')

                c_min_val = pulisci_numero(compr_min)
                c_max_val = pulisci_numero(compr_max)
                l_min_val = pulisci_numero(loc_min)
                l_max_val = pulisci_numero(loc_max)

                if c_min_val is not None: c_min_list.append(c_min_val)
                if c_max_val is not None: c_max_list.append(c_max_val)
                if l_min_val is not None: l_min_list.append(l_min_val)
                if l_max_val is not None: l_max_list.append(l_max_val)

                righe_da_salvare.append({
                    'zona': riga_zona,
                    'tipologia': tipologia,
                    'stato': stato,
                    'compr_min': compr_min,
                    'compr_max': compr_max,
                    'loc_min': loc_min,
                    'loc_max': loc_max
                })

                colore_testo = GREEN if i % 2 == 0 else WHITE
                i += 1

                print(f"{CYAN}│{RESET} {YELLOW}{riga_zona:<4}{RESET} {CYAN}│{RESET} {colore_testo}{tipologia:<38}{RESET} {CYAN}│{RESET} {stato:<12} {CYAN}│{RESET} {compr_min:<17} {CYAN}│{RESET} {compr_max:<17} {CYAN}│{RESET} {loc_min:<17} {CYAN}│{RESET} {loc_max:<17} {CYAN}│{RESET}")

    medie_dict = None

    if not trovato:
        print(f"{CYAN}│{RESET} {RED}{'Nessun valore trovato per la ricerca effettuata.':<138}{RESET}{CYAN}│{RESET}")
        print(f"{CYAN}└──────┴────────────────────────────────────────┴──────────────┴───────────────────┴───────────────────┴───────────────────┴───────────────────┘{RESET}\n")
    else:
        print(f"{CYAN}└──────┴────────────────────────────────────────┴──────────────┴───────────────────┴───────────────────┴───────────────────┴───────────────────┘{RESET}")
        
        c_min_med = sum(c_min_list) / len(c_min_list) if c_min_list else 0
        c_max_med = sum(c_max_list) / len(c_max_list) if c_max_list else 0
        compr_media_globale = (c_min_med + c_max_med) / 2

        l_min_med = sum(l_min_list) / len(l_min_list) if l_min_list else 0
        l_max_med = sum(l_max_list) / len(l_max_list) if l_max_list else 0
        loc_media_globale = (l_min_med + l_max_med) / 2

        medie_dict = {
            'compr_min_med': c_min_med,
            'compr_max_med': c_max_med,
            'compr_media': compr_media_globale,
            'loc_min_med': l_min_med,
            'loc_max_med': l_max_med,
            'loc_media': loc_media_globale
        }

        print(f"\n{MAGENTA}┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}")
        print(f"{MAGENTA}│{RESET} {BOLD}RIEPILOGO PREZZI MEDI AL M²{RESET}                                                                                     {MAGENTA}│{RESET}")
        print(f"{MAGENTA}├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤{RESET}")
        print(f"{MAGENTA}│{RESET} • {BOLD}Compravendita Media{RESET} : {YELLOW}{compr_media_globale:.2f} €/m²{RESET}   (Media Min: {c_min_med:.2f} €/m² | Media Max: {c_max_med:.2f} €/m²){' ':<22}{MAGENTA}│{RESET}")
        print(f"{MAGENTA}│{RESET} • {BOLD}Locazione Media{RESET}    : {YELLOW}{loc_media_globale:.2f} €/m²/m{RESET} (Media Min: {l_min_med:.2f} €/m²/m | Media Max: {l_max_med:.2f} €/m²/m){' ':<18}{MAGENTA}│{RESET}")
        print(f"{MAGENTA}└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}\n")

        salva = input(f"{BOLD}Vuoi salvare questi dati su file .txt? (s/n): {RESET}").strip().lower()
        if salva == 's':
            etichetta_salvataggio = "TUTTE" if mostra_tutto else zona_scelta
            salva_su_txt(info_comune['nome'], codice_comune, etichetta_salvataggio, righe_da_salvare, medie_dict)

def main():
    FILE_ZONE = "Zone.csv"
    FILE_VALORI = "Valori.csv"

    os.system('')

    while True:
        pulisci_schermo()
        print(f"{CYAN}══════════════════════════════════════════════════════════════════════════════{RESET}")
        print(fr"""{BOLD}{CYAN}
                                              _        _    _____ _        _       
  /\  /\___  _   _ ___  ___  /\/\   __ _ _ __| | _____| |_  \_   \ |_ __ _| |_   _ 
 / /_/ / _ \| | | / __|/ _ \/    \ / _` | '__| |/ / _ \ __|  / /\/ __/ _` | | | | |
/ __  / (_) | |_| \__ \  __/ /\/\ \ (_| | |  |   <  __/ |_/\/ /_ | || (_| | | |_| |
\/ /_/ \___/ \__,_|___/\___\/    \/\__,_|_|  |_|\_\___|\__\____/  \__\__,_|_|\__, |
                                                                             |___/ 
       @ LemonPower21  (FrancescoVitoGiotta)
        {RESET}""")
        print(f"{CYAN}══════════════════════════════════════════════════════════════════════════════{RESET}")

        try:
            dati_comuni = carica_dati_zone(FILE_ZONE)
        except FileNotFoundError:
            print(f"\n{RED}[ERRORE] Impossibile trovare il file '{FILE_ZONE}'.{RESET}")
            break

        cod_comune = input(f"\n{BOLD}> Inserisci il codice Comune (es. '16072036' o 'H096'): {RESET}").strip().upper()
        
        if cod_comune in dati_comuni:
            info = dati_comuni[cod_comune]
            print(f"\n{GREEN}[+] Comune Trovato:{RESET} {BOLD}{info['nome']}{RESET} (ISTAT: {YELLOW}{info['istat']}{RESET} | Amm/Cat: {YELLOW}{info['amm']}{RESET})")
            
            salva_pdf = input(f"{BOLD}> Vuoi salvare anche la mappa in formato PDF? (s/n): {RESET}").strip().lower() == 's'

            apri_gui_kml(cod_comune, info, salva_pdf=salva_pdf)

            print(f"\n{BOLD}Zone OMI disponibili:{RESET}")
            print(f"{CYAN}┌───────────┬────────┬────────────────────────────────────────────────────────────────────────┐{RESET}")
            print(f"{CYAN}│{RESET} {BOLD}{'Cod. Zona':<9}{RESET} {CYAN}│{RESET} {BOLD}{'Fascia':<6}{RESET} {CYAN}│{RESET} {BOLD}{'Descrizione Zona':<70}{RESET} {CYAN}│{RESET}")
            print(f"{CYAN}├───────────┼────────┼────────────────────────────────────────────────────────────────────────┤{RESET}")
            
            for cod_z, z_info in info['zone'].items():
                print(f"{CYAN}│{RESET} {YELLOW}{cod_z:<9}{RESET} {CYAN}│{RESET} {z_info['fascia']:<6} {CYAN}│{RESET} {z_info['descr']:<70} {CYAN}│{RESET}")
            print(f"{CYAN}└───────────┴────────┴────────────────────────────────────────────────────────────────────────┘{RESET}")
            
            while True:
                zona_scelta = input(f"\n{BOLD}> Inserisci il codice Zona (es. B1, C1) o {YELLOW}'T'{RESET}{BOLD} per vederle TUTTE: {RESET}").strip().upper()
                if zona_scelta == "T" or zona_scelta in info['zone']:
                    try:
                        mostra_dettagli_valori(FILE_VALORI, info, cod_comune, zona_scelta)
                    except FileNotFoundError:
                        print(f"\n{RED}[ERRORE] Impossibile trovare il file dei valori '{FILE_VALORI}'.{RESET}")
                    break
                else:
                    print(f"{RED}[!] Codice Zona non valido. Riprova con una zona presente nell'elenco o premi 'T'.{RESET}")
            
            ancora = input(f"{BOLD}Vuoi effettuare un'altra ricerca? (s/n): {RESET}").strip().lower()
            if ancora != 's':
                print(f"\n{GREEN}Applicazione terminata.{RESET}")
                break
        else:
            print(f"\n{RED}[!] Codice Comune non trovato.{RESET}")
            input(f"\nPremere {BOLD}INVIO{RESET} per riprovare...")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
