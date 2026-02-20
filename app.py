import streamlit as st
import pandas as pd
import datetime
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Vérification zonage fiscal",
    page_icon=":round_pushpin:",
    layout="wide"
)

st.markdown("""
    <style>
    /* --- 1. DESIGN ÉCRAN --- */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .main-title { font-size: 2em; color: #2c3e50; text-align: center; margin-bottom: 20px; font-weight: bold; }

    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 0.9em;
        background-color: white;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    
    th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        text-transform: uppercase;
        border: 1px solid #34495e;
        width: 18%;
    }
    
    td {
        padding: 10px;
        border: 1px solid #ddd;
        vertical-align: top;
        color: #333;
        line-height: 1.4;
    }

    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        width: 1%;            
        white-space: nowrap;  
        padding-right: 20px;
    }
    
    .zone-row td {
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
        font-weight: bold;
        text-align: center;
        font-size: 1.1em;
        border-bottom: 2px solid #2e7d32;
    }

    .btn-legifrance {
        background-color: #fce4ec;
        color: #c2185b;
        padding: 4px 8px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #f8bbd0;
        font-size: 0.8em;
        white-space: nowrap;
        display: inline-block;
        margin-bottom: 4px; 
    }
    
    .btn-cgi {
        background-color: #f3e5f5;
        color: #7b1fa2;
        padding: 4px 8px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #e1bee7;
        font-size: 0.8em;
        white-space: nowrap;
        display: inline-block;
    }
    
    .btn-doc {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #bbdefb;
        font-size: 0.85em;
        white-space: nowrap;
        display: inline-block;
    }

    /* --- 2. DESIGN IMPRESSION (Overlay Method) --- */
    @media print {
        body * { visibility: hidden; }
        #printable-area, #printable-area * { visibility: visible; }
        
        #printable-area {
            position: fixed;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 20px;
            background-color: white;
            z-index: 9999;
        }
        
        @page { size: A4 landscape; margin: 1cm; }

        table {
            width: 100% !important;
            font-size: 9pt !important;
            border: 2px solid #000;
        }
        
        th {
            background-color: #2c3e50 !important;
            color: white !important;
            -webkit-print-color-adjust: exact; 
            print-color-adjust: exact;
        }
        
        .btn-legifrance, .btn-doc, .btn-cgi {
            border: none;
            background: none !important;
            color: black !important;
            text-decoration: underline;
            padding: 0;
            margin-right: 10px;
        }
        
        .no-print { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DE LA BASE DES COMMUNES
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df_raw = pd.read_csv(url, header=None, dtype=str)
        header_row_idx = None
        for i, row in df_raw.iterrows():
            row_str = " ".join(row.fillna("").astype(str).values)
            if "Libellé" in row_str and "Code" in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            df = pd.read_csv(url, dtype=str)
        else:
            df = pd.read_csv(url, header=header_row_idx, dtype=str)

        df.columns = [c.strip() for c in df.columns]
        rename_map = {}
        existing_cols = df.columns.tolist()
        def has_col(target): return target in existing_cols

        for col in existing_cols:
            c = col.lower()
            if ("libellé" in c or "commune" in c) and not has_col("COMMUNE"): rename_map[col] = "COMMUNE"
            elif ("code" in c and "insee" not in c) and not has_col("CODE"): rename_map[col] = "CODE"
            elif "nb_zfu" in c: rename_map[col] = "NB_ZFU"
            elif "zfu" in c and not has_col("NB_ZFU") and "NB_ZFU" not in rename_map.values(): rename_map[col] = "NB_ZFU"
            elif "nb_qpv" in c: rename_map[col] = "NB_QPV"
            elif ("quartier" in c or "qpv" in c or "qppv" in c) and not has_col("NB_QPV") and "NB_QPV" not in rename_map.values(): rename_map[col] = "NB_QPV"
            elif ("frr" in c or "ruralités" in c) and not has_col("FRR"): rename_map[col] = "FRR"
            elif "afr" in c and not has_col("AFR"): rename_map[col] = "AFR"

        df = df.rename(columns=rename_map)
        if 'COMMUNE' in df.columns and 'CODE' in df.columns:
            if 'CP' in df.columns:
                df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
            else:
                df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CODE'] + ")"
            return df
        else:
            return None
    except Exception as e:
        return None

# ==============================================================================
# 3. CHARGEMENT DE LA MATRICE (BASE EXTERNE EXCLUSIVE)
# ==============================================================================
@st.cache_data(ttl=600)
def load_matrix():
    SHEET_ID_MATRICE = "1pD6AJViuY1PRWYLJh3K9Xlpc_ngsVqeK1ljRJgmvKX0" 
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_MATRICE}/export?format=csv"
        df = pd.read_csv(url, dtype=str)
        
        if "ID_CRITERE" not in df.columns:
            return None
            
        df = df.set_index("ID_CRITERE")
        df = df.fillna("") 
        return df.to_dict()
    except Exception as e:
        return None 

# ==============================================================================
# 4. MOTEUR DE VÉRIFICATION DYNAMIQUE DES DATES
# ==============================================================================
def is_eligible_by_date(regime_key, date_op, matrix):
    """Vérifie si la date de l'opération est dans les clous du dispositif"""
    if regime_key not in matrix:
        return False
        
    start_str = str(matrix[regime_key].get("Date_debut", "")).strip()
    end_str = str(matrix[regime_key].get("Date_fin", "")).strip()
    
    # Par défaut, si rien n'est renseigné, c'est toujours bon
    start_d = date.min
    end_d = date.max
    
    def parse_d(d_str):
        if not d_str or d_str.lower() in ['nan', 'null', '']: return None
        try:
            # Tente le format YYYY-MM-DD
            if "-" in d_str: return date.fromisoformat(d_str)
            # Tente le format DD/MM/YYYY
            elif "/" in d_str: return datetime.datetime.strptime(d_str, "%d/%m/%Y").date()
        except: pass
        return None
        
    parsed_start = parse_d(start_str)
    if parsed_start: start_d = parsed_start
    
    parsed_end = parse_d(end_str)
    if parsed_end: end_d = parsed_end
    
    return start_d <= date_op <= end_d

# ==============================================================================
# 5. GÉNÉRATEUR HTML DU TABLEAU
# ==============================================================================
def get_zone_display(regime_key, row_data):
    # Logique de récupération de la valeur brute
    raw_val = ""
    # Gestion du QPV_2026 qui lit les mêmes colonnes géographiques
    if regime_key == "ZFU" or regime_key == "QPV_2026": 
        raw_val = str(row_data.get('NB_ZFU', '')).strip()
        # Si la commune est QPV, elle est aussi éligible au nouveau QPV_2026
        if raw_val.lower() in ['0', 'nan', 'non', '', '-']:
            raw_val = str(row_data.get('NB_QPV', '')).strip()
            
    elif regime_key == "QPV": raw_val = str(row_data.get('NB_QPV', '')).strip()
    elif regime_key == "AFR": raw_val = str(row_data.get('AFR', '')).strip()
    elif "ZFRR" in regime_key: raw_val = str(row_data.get('FRR', '')).strip()

    if raw_val.lower() in ['nan', '0', '', 'non', '-']: return "-"
    if raw_val.lower() == "oui": return "Intégralement"
    elif "partiel" in raw_val.lower(): return "Partiellement"
    elif "maintenue" in raw_val.lower(): return "ZRR maintenue"
    else: return raw_val

def render_html_table(regimes, row_data, date_op, data_matrix):
    rows_config = [
        ("Références légales", "References_legales"),
        ("Période d'application", "Periode"), # On affiche "Periode" pour l'humain
        ("Durée exonération IR/IS", "Duree_exo"),
        ("Impôts locaux (CFE / TFPB)", "Impots_locaux"),
        ("Exonérations sociales", "Social"),
        ("Nature d'activité éligible", "Nature_activite"),
        ("Régime fiscal", "Regime_fiscal"),
        ("Taille de l'entreprise", "Taille"),
        ("Implantation exigée", "Implantation"),
        ("Condition sociale", "Condition_sociale"),
        ("Exclusions anti-abus", "Exclusions_abus"),
        ("Règles UE / plafonds d'aides", "Plafonds_UE")
    ]

    commune_info = f"Commune : <b>{row_data['COMMUNE']}</b> (Code: {row_data['CODE']})"
    if row_data['COMMUNE'] == "MODE RÉFÉRENCE":
        commune_info = "<b>MODE RÉFÉRENCE (Tous dispositifs)</b>"

    html = f"""
    <div id='printable-area'>
        <div class='main-title'>Vérification zonage fiscal</div>
        <div class='sub-title'>
            {commune_info} | 
            Date opération : {date_op.strftime('%d/%m/%Y')}
        </div>
        <table>
            <thead><tr><th>Critères</th>
    """
    
    for r in regimes:
        html += f"<th>{data_matrix[r].get('Nom', '')}</th>"
    html += "</tr></thead><tbody>"
    
    # 1. ZONE
    html += "<tr class='zone-row'><td>ZONE / CLASSEMENT</td>"
    for r in regimes:
        html += f"<td>{get_zone_display(r, row_data)}</td>"
    html += "</tr>"
    
    # 2. DOCUMENTATION
    html += "<tr><td>DOCUMENTATION</td>"
    for r in regimes:
        doc_url = data_matrix[r].get("Doc_Link", "")
        if str(doc_url).strip() and str(doc_url) != "nan":
            html += f'<td><a href="{doc_url}" target="_blank" class="btn-doc">Fiche Pratique 📘</a></td>'
        else:
            html += "<td>-</td>"
    html += "</tr>"
    
    # 3. VERIFICATION SOURCE (DOUBLE BOUTON)
    date_formatted = date_op.strftime("%Y-%m-%d")
    html += "<tr><td>VÉRIFICATION SOURCE</td>"
    for r in regimes:
        cell_content = ""
        
        base_url = data_matrix[r].get("Legifrance_Base", "")
        if str(base_url).strip() and str(base_url) != "nan":
            full_link = f"{base_url}{date_formatted}"
            cell_content += f'<a href="{full_link}" target="_blank" class="btn-legifrance">Liste communes</a><br>'
        
        article_url = data_matrix[r].get("Legifrance_Article", "")
        ref_text = data_matrix[r].get("References_legales", "Article Loi")
        clean_ref = str(ref_text).split("<br>")[0] if ref_text else "Article Loi"
        
        if str(article_url).strip() and str(article_url) != "nan":
            full_article_link = f"{article_url}{date_formatted}"
            cell_content += f'<a href="{full_article_link}" target="_blank" class="btn-cgi">{clean_ref}</a>'
            
        if not cell_content: cell_content = "-"
        html += f"<td>{cell_content}</td>"
    html += "</tr>"

    # 4. RESTE DU TABLEAU
    for label, key in rows_config:
        html += f"<tr><td>{label}</td>"
        for r in regimes:
            val = data_matrix[r].get(key, "-")
            if pd.isna(val) or val == "nan": val = ""
            html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html

# ==============================================================================
# 6. MOTEUR D'ANALYSE
# ==============================================================================
if 'show_all_mode' not in st.session_state:
    st.session_state.show_all_mode = False

def toggle_mode():
    st.session_state.show_all_mode = not st.session_state.show_all_mode

df = load_data()
DATA_MATRIX = load_matrix()

st.markdown("<h1 class='main-title'>Vérification zonage fiscal</h1>", unsafe_allow_html=True)

# GESTION D'ERREUR MATRICE EXTERNE
if DATA_MATRIX is None or not DATA_MATRIX:
    st.error("⚠️ Attention : Les données sources de législation sont en cours de révision. L'application est momentanément indisponible.")
    st.stop() 

if df is not None:
    with st.container():
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        st.warning("⚠️ Attention : La base de données est en cours de constitution. Toutes les communes ne sont pas encore référencées.")
        
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Sélectionner une commune", df['Label_Recherche'], index=None, placeholder="Rechercher...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), 
                                      min_value=date(2025, 1, 1), 
                                      format="DD/MM/YYYY")
        
        btn_label = "📖 Masquer le comparatif complet" if st.session_state.show_all_mode else "📖 Afficher tous les dispositifs (Mode Référence)"
        st.button(btn_label, on_click=toggle_mode, type="secondary")
        st.markdown('</div>', unsafe_allow_html=True)

    row_to_display = None
    regimes_to_display = []

    if st.session_state.show_all_mode:
        # Affiche tout ce qui est éligible À CETTE DATE
        for r_key in DATA_MATRIX.keys():
            if is_eligible_by_date(r_key, date_crea, DATA_MATRIX):
                regimes_to_display.append(r_key)
        row_to_display = {'COMMUNE': 'MODE RÉFÉRENCE', 'CODE': '-', 'NB_ZFU': '-', 'NB_QPV': '-', 'AFR': '-', 'FRR': '-'}
    
    elif choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        row_to_display = row
        
        # 1. ZFRR
        frr_val = str(row.get('FRR', '')).strip().upper()
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if ("+" in frr_val or "FRR+" in frr_val) and is_eligible_by_date("ZFRR_PLUS", date_crea, DATA_MATRIX):
                regimes_to_display.append("ZFRR_PLUS")
            elif is_eligible_by_date("ZFRR_CLASSIC", date_crea, DATA_MATRIX):
                regimes_to_display.append("ZFRR_CLASSIC")

        # 2. ZFU (Ancien)
        nb_zfu = str(row.get('NB_ZFU', '0')).strip()
        is_zfu = False
        if nb_zfu not in ['0', 'nan', 'NON', '', 'Non', '-']: is_zfu = True
        if is_zfu and is_eligible_by_date("ZFU", date_crea, DATA_MATRIX):
            regimes_to_display.append("ZFU")

        # 3. AFR
        afr_val = str(row.get('AFR', '')).strip().capitalize()
        if afr_val in ['Integralement', 'Partiellement', 'Oui', 'Intégralement']:
             if is_eligible_by_date("AFR", date_crea, DATA_MATRIX):
                regimes_to_display.append("AFR")
        
        # 4. QPV (Ancien)
        nb_qpv = str(row.get('NB_QPV', '0')).strip()
        is_qpv = False
        if nb_qpv not in ['0', 'nan', 'NON', '', 'Non', '-']: is_qpv = True
        if is_qpv and is_eligible_by_date("QPV", date_crea, DATA_MATRIX):
            regimes_to_display.append("QPV")
            
        # 5. QPV_2026 (Nouveau régime unifié - S'active si la ville est ZFU ou QPV)
        if (is_zfu or is_qpv) and is_eligible_by_date("QPV_2026", date_crea, DATA_MATRIX):
            regimes_to_display.append("QPV_2026")

    if row_to_display is not None:
        st.divider()
        if regimes_to_display:
            regimes_to_display = list(dict.fromkeys(regimes_to_display))
            
            if not st.session_state.show_all_mode:
                st.success(f"✅ {len(regimes_to_display)} dispositif(s) identifié(s) à la date du {date_crea.strftime('%d/%m/%Y')}")
            
            st.markdown(render_html_table(regimes_to_display, row_to_display, date_crea, DATA_MATRIX), unsafe_allow_html=True)
            
            st.markdown("""
            <div class='no-print' style='text-align:center; margin-top:20px; color:#666;'>
                <small>Pour imprimer, faites <b>Ctrl+P</b>. Cochez "Graphiques d'arrière-plan" pour voir les couleurs.</small>
            </div>
            """, unsafe_allow_html=True)

            if ("ZFU" in regimes_to_display or "QPV" in regimes_to_display or "QPV_2026" in regimes_to_display) and not st.session_state.show_all_mode:
                st.warning("⚠️ **Vigilance (ZFU / QPV)** : Éligibilité conditionnée à l'adresse exacte.")
        else:
            st.warning(f"Aucun dispositif zoné majeur détecté pour cette commune à la date du {date_crea.strftime('%d/%m/%Y')}.")

else:
    st.error("Erreur de chargement de la base des communes.")
