import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (CSS ULTRA-PRINT)
# ==============================================================================
st.set_page_config(
    page_title="Audit Zonage Fiscal",
    page_icon="🦁",
    layout="wide"
)

st.markdown("""
    <style>
    /* --- AFFICHAGE ÉCRAN STANDARD --- */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .main-title { font-size: 2.5em; color: #2c3e50; text-align: center; margin-bottom: 10px; }
    .sub-title { font-size: 1.2em; color: #7f8c8d; text-align: center; margin-bottom: 30px; }

    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Arial', sans-serif; /* Police standard qui passe bien partout */
        font-size: 0.85em;
        margin-top: 15px;
        background-color: white;
        border: 1px solid #ddd;
    }
    th {
        background-color: #2c3e50;
        color: white;
        padding: 10px;
        text-align: center;
        text-transform: uppercase;
        border: 1px solid #34495e;
        width: 18%;
    }
    td:first-child {
        background-color: #f1f2f6;
        font-weight: 800;
        color: #2c3e50;
        text-align: left;
        padding-left: 10px;
        border-right: 2px solid #ccc;
        width: 15%;
    }
    td {
        padding: 8px;
        border: 1px solid #ddd;
        vertical-align: top;
        text-align: left;
        color: #333;
        line-height: 1.3;
    }
    
    /* LIGNE ZONE / CLASSEMENT */
    .zone-row td {
        background-color: #dcedc8 !important; /* Vert clair */
        font-weight: 900;
        color: #1b5e20 !important;
        text-align: center;
        font-size: 1.1em;
        border-bottom: 2px solid #33691e;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    /* BOUTONS LIENS */
    .btn-legifrance {
        display: inline-block;
        background-color: #fce4ec;
        color: #c2185b;
        padding: 4px 8px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #f8bbd0;
        font-size: 0.8em;
        white-space: nowrap;
    }

    /* INSTRUCTIONS D'IMPRESSION (Visibles seulement à l'écran) */
    .print-instruction {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 0.9em;
    }

    /* ==========================================================================
       STYLE D'IMPRESSION (LE COEUR DU SYSTÈME)
       ========================================================================== */
    @media print {
        /* 1. FORCE LE PAYSAGE (Chrome/Edge) */
        @page {
            size: A4 landscape;
            margin: 5mm; /* Marges très fines */
        }

        /* 2. CACHER TOUT LE RESTE */
        body * {
            visibility: hidden;
            height: 0;
            overflow: hidden;
        }

        /* 3. AFFICHER SEULEMENT LA ZONE D'IMPRESSION */
        #printable-area, #printable-area * {
            visibility: visible;
            height: auto;
            overflow: visible;
        }

        /* 4. REPOSITIONNER LE CONTENU EN HAUT À GAUCHE */
        #printable-area {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            margin: 0;
            padding: 0;
        }

        /* 5. AJUSTEMENT DU TABLEAU POUR TENIR SUR UNE PAGE */
        table {
            width: 100% !important;
            font-size: 9pt !important; /* Réduire police */
            border: 2px solid #333;
        }
        
        th {
            background-color: #2c3e50 !important;
            color: white !important;
            -webkit-print-color-adjust: exact; 
        }
        
        /* Transformer les boutons en liens texte simples */
        .btn-legifrance {
            border: none;
            background: none !important;
            color: black !important;
            text-decoration: underline;
            padding: 0;
        }
        
        /* Cacher le bouton d'impression lui-même */
        .no-print {
            display: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT INTELLIGENT DES DONNÉES
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
            elif "ber" in c and not has_col("BER"): rename_map[col] = "BER"

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
# 3. MATRICE DE DONNÉES (2030 UPDATED)
# ==============================================================================
DATA_MATRIX = {
    "ZFU": {
        "Nom": "ZFU-TE",
        "References_legales": "CGI art. 44 octies A",
        "Periode": "Créations jusqu'au <b>31/12/2030</b><br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "100 % 5 ans, puis 60 % (6e), 40 % (7e), 20 % (8e).",
        "Impots_locaux": "Exonération possible sur délibération.",
        "Social": "Exonération spécifique (L.131-4-2)", 
        "Nature_activite": "Indus, Com, Art, BNC.<br><i>Exclusions : location logements, crédit-bail.</i>",
        "Regime_fiscal": "Tout régime (micro ou réel)",
        "Taille": "< 50 salariés, CA ≤ 10 M€. Capital < 25 % par grandes ent.",
        "Implantation": "Activité matérielle effective en ZFU. Non sédentaire sous conditions.",
        "Condition_sociale": "50% salariés résidant ZFU/QPV (dès le 2e salarié)",
        "Exclusions_abus": "Transfert simple exclu.",
        "Plafonds_UE": "50 k€/an + 5k€/emploi.",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/LEGIARTI000026939165/"
    },
    "AFR": {
        "Nom": "ZAFR (Zones AFR)",
        "References_legales": "CGI art. 44 sexies",
        "Periode": "Créations jusqu'au 31/12/2027",
        "Duree_exo": "100 % 2 ans, puis 75 %, 50 %, 25 %.",
        "Impots_locaux": "Exonération possible sur délibération.",
        "Social": "Non",
        "Nature_activite": "Indus, Com, Art, BNC (si Sté IS).",
        "Regime_fiscal": "Régime réel obligatoire",
        "Taille": "PME. Capital < 50 % par autres sociétés.",
        "Implantation": "Siège + moyens en zone.",
        "Condition_sociale": "3 salariés minimum si activité BNC",
        "Exclusions_abus": "Extension d'activité existante.",
        "Plafonds_UE": "De minimis (300 k€).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046003627/"
    },
    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (Classique)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "01/07/2024 – 31/12/2029",
        "Duree_exo": "100 % 5 ans, puis 75 %, 50 %, 25 %.",
        "Impots_locaux": "Exonération possible sur délibération.",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Indus, Com, Art, Lib.<br><i>Excl: Banque, Immo.</i>",
        "Regime_fiscal": "Régime réel obligatoire",
        "Taille": "< 11 salariés.",
        "Implantation": "Siège + moyens exclusifs en zone.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Reprise familiale.",
        "Plafonds_UE": "De minimis (300 k€).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000049746820/"
    },
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (Renforcée)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "01/01/2025 – 31/12/2029",
        "Duree_exo": "100 % 5 ans, puis 75 %, 50 %, 25 %.",
        "Impots_locaux": "Exonération possible sur délibération.",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Indus, Com, Art, Lib.",
        "Regime_fiscal": "Réel ou Micro",
        "Taille": "Création : PME. Reprise : < 11 sal.",
        "Implantation": "Non exclusif.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Reprise familiale.",
        "Plafonds_UE": "De minimis (300 k€).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000051871914/"
    },
    "QPV": {
        "Nom": "QPPV",
        "References_legales": "Décret n° 2023-1314",
        "Periode": "Créations jusqu'au <b>31/12/2030</b><br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "N/C",
        "Impots_locaux": "Exo TFPB 5 ans sauf délibération.",
        "Social": "Non",
        "Nature_activite": "N/C",
        "Regime_fiscal": "N/C",
        "Taille": "N/C",
        "Implantation": "N/C",
        "Condition_sociale": "N/C",
        "Exclusions_abus": "N/C",
        "Plafonds_UE": "N/C",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000048707389/"
    }
}

# ==============================================================================
# 4. GÉNÉRATEUR HTML DU TABLEAU
# ==============================================================================
def get_zone_display(regime_key, row_data):
    raw_val = ""
    if regime_key == "ZFU": raw_val = str(row_data.get('NB_ZFU', '')).strip()
    elif regime_key == "QPV": raw_val = str(row_data.get('NB_QPV', '')).strip()
    elif regime_key == "AFR": raw_val = str(row_data.get('AFR', '')).strip()
    elif "ZFRR" in regime_key: raw_val = str(row_data.get('FRR', '')).strip()

    if raw_val.lower() in ['nan', '0', '', 'non']: return "-"
    if raw_val.lower() == "oui": return "Intégralement"
    elif "partiel" in raw_val.lower(): return "Partiellement"
    elif "maintenue" in raw_val.lower(): return "ZRR maintenue"
    else: return raw_val

def render_html_table(regimes, row_data, date_op):
    rows_config = [
        ("Références légales", "References_legales"),
        ("Période d'application", "Periode"),
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

    html = "<div id='printable-area'>"
    html += f"<div class='main-title'>Audit Zonage Fiscal</div>"
    html += f"<div class='sub-title'>Commune : <b>{row_data['COMMUNE']}</b> (Code: {row_data['CODE']}) | Date opération : {date_op.strftime('%d/%m/%Y')}</div>"
    
    html += "<table>"
    html += "<thead><tr><th>Critères</th>"
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead><tbody>"
    
    html += "<tr class='zone-row'><td>ZONE / CLASSEMENT</td>"
    for r in regimes:
        html += f"<td>{get_zone_display(r, row_data)}</td>"
    html += "</tr>"
    
    date_formatted = date_op.strftime("%Y-%m-%d")
    html += "<tr><td>VÉRIFICATION SOURCE</td>"
    for r in regimes:
        base_url = DATA_MATRIX[r].get("Legifrance_Base")
        if base_url:
            full_link = f"{base_url}{date_formatted}"
            html += f'<td><a href="{full_link}" target="_blank" class="btn-legifrance">Voir le texte à date 🔗</a></td>'
        else:
            html += "<td>-</td>"
    html += "</tr>"

    for label, key in rows_config:
        html += f"<tr><td>{label}</td>"
        for r in regimes:
            val = DATA_MATRIX[r].get(key, "-")
            if val == "nan" or pd.isna(val): val = ""
            html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html

# ==============================================================================
# 5. MOTEUR D'ANALYSE
# ==============================================================================
df = load_data()

# PARTIE VISIBLE UNIQUEMENT À L'ÉCRAN
st.title("Audit Zonage Fiscal")
st.markdown("**Outil d'aide à la décision - Hauts-de-France**")
st.write("---")

if df is not None:
    # Conteneur non imprimable pour les inputs
    with st.container():
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Rechercher...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), format="DD/MM/YYYY")
        st.markdown('</div>', unsafe_allow_html=True)

    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        
        detected = []
        
        # 1. ZFRR
        frr_val = str(row.get('FRR', '')).strip().upper()
        DATE_ZFRR_PLUS = date(2025, 1, 1)
        DATE_ZFRR_CLASSIC = date(2024, 7, 1)
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_ZFRR_PLUS and ("+" in frr_val or "FRR+" in frr_val):
                detected.append("ZFRR_PLUS")
            elif date_crea >= DATE_ZFRR_CLASSIC:
                detected.append("ZFRR_CLASSIC")
            else:
                detected.append("ZFRR_CLASSIC")

        # 2. ZFU (Detection valeur brute)
        nb_zfu = str(row.get('NB_ZFU', '0')).strip()
        is_zfu = False
        if nb_zfu not in ['0', 'nan', 'NON', '', 'Non']: is_zfu = True
        # Prorogation 2030
        if is_zfu and date_crea <= date(2030, 12, 31):
            detected.append("ZFU")

        # 3. AFR
        afr_val = str(row.get('AFR', '')).strip().capitalize()
        if afr_val in ['Integralement', 'Partiellement', 'Oui', 'Intégralement']:
             if date_crea <= date(2027, 12, 31):
                detected.append("AFR")
        
        # 4. QPV
        nb_qpv = str(row.get('NB_QPV', '0')).strip()
        is_qpv = False
        if nb_qpv not in ['0', 'nan', 'NON', '', 'Non']: is_qpv = True
        # Prorogation 2030
        if is_qpv and date_crea <= date(2030, 12, 31):
            detected.append("QPV")

        # AFFICHAGE
        if detected:
            detected = list(dict.fromkeys(detected))
            
            # Instruction pour l'utilisateur
            st.markdown("""
            <div class='print-instruction no-print'>
                🖨️ <b>Pour imprimer :</b> Faites <b>Ctrl+P</b> (ou Cmd+P).<br>
                Dans la fenêtre d'impression, assurez-vous de cocher <b>"Graphiques d'arrière-plan"</b> 
                et choisissez <b>"Paysage"</b>. L'interface inutile disparaîtra automatiquement.
            </div>
            """, unsafe_allow_html=True)

            st.success(f"✅ {len(detected)} dispositif(s) identifié(s)")
            
            # Injection du HTML
            st.markdown(render_html_table(detected, row, date_crea), unsafe_allow_html=True)
            
            if "ZFU" in detected or "QPV" in detected:
                st.warning("⚠️ **Vigilance (ZFU / QPV)** : Éligibilité conditionnée à l'adresse exacte.")
        else:
            st.warning("Aucun dispositif zoné majeur détecté.")

else:
    st.error("Erreur chargement Google Sheet.")
