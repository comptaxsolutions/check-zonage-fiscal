import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (CSS SPECIAL IMPRESSION A4)
# ==============================================================================
st.set_page_config(
    page_title="Audit Zonage Fiscal",
    page_icon="🦁",
    layout="wide"
)

st.markdown("""
    <style>
    /* --- STYLE ÉCRAN (Classique) --- */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.9em;
        margin-top: 15px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
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
    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        text-align: left;
        padding-left: 15px;
        border-right: 2px solid #dee2e6;
        width: 15%;
    }
    td {
        padding: 10px;
        border: 1px solid #dee2e6;
        vertical-align: top;
        text-align: left;
        color: #333;
        line-height: 1.4;
    }
    
    /* Ligne ZONE / CLASSEMENT (Fond Vert) */
    .zone-row td {
        background-color: #e8f5e9 !important;
        font-weight: bold;
        color: #1b5e20 !important;
        text-align: center;
        font-size: 1.1em;
        border-bottom: 2px solid #2e7d32;
        -webkit-print-color-adjust: exact; 
        print-color-adjust: exact;
    }

    /* Boutons Liens (Ecran) */
    .btn-legifrance {
        display: inline-block;
        background-color: #fce4ec;
        color: #c2185b;
        padding: 6px 12px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #f8bbd0;
        font-size: 0.9em;
        text-align: center;
        white-space: nowrap;
    }

    /* --- STYLE IMPRESSION (Ctrl+P) --- */
    @media print {
        /* 1. Cacher toute l'interface Streamlit inutile */
        [data-testid="stSidebar"], 
        [data-testid="stHeader"], 
        [data-testid="stToolbar"], 
        footer, 
        .stDeployButton,
        iframe {
            display: none !important;
        }

        /* 2. Cacher les champs de saisie (Selectbox, DateInput, Alertes) */
        .stSelectbox, 
        .stDateInput, 
        .stAlert, 
        .no-print {
            display: none !important;
        }
        
        /* 3. Ajuster la page A4 Paysage */
        @page {
            size: A4 landscape;
            margin: 1cm;
        }
        
        body {
            background-color: white;
            font-size: 10pt; /* Réduire un peu la police pour tout faire tenir */
            -webkit-print-color-adjust: exact; /* Force l'impression des couleurs (vert/gris) */
            print-color-adjust: exact;
        }
        
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        
        /* 4. Tableau Pleine Largeur */
        table {
            width: 100% !important;
            box-shadow: none !important;
            border: 2px solid #333;
        }
        
        th {
            background-color: #2c3e50 !important;
            color: white !important;
            -webkit-print-color-adjust: exact; 
        }

        /* 5. Transformer les liens boutons en texte souligné simple */
        .btn-legifrance {
            background: none !important;
            border: none !important;
            color: black !important;
            text-decoration: underline !important;
            padding: 0 !important;
            font-size: 0.8em;
        }
        
        /* Titre Propre */
        h1 {
            color: #2c3e50 !important;
            font-size: 24pt !important;
            text-align: center;
            margin-bottom: 20px;
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
        # 1. Détection de la ligne d'en-tête
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

        # 2. NETTOYAGE
        df.columns = [c.strip() for c in df.columns]

        # 3. RENOMMAGE SÉCURISÉ
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
        
        # 4. Construction colonne Recherche
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
# 3. MATRICE DE DONNÉES (MIS À JOUR 2030)
# ==============================================================================
DATA_MATRIX = {
    "ZFU": {
        "Nom": "ZFU-TE",
        "References_legales": "CGI art. 44 octies A",
        # MISE À JOUR PROROGATION 2030
        "Periode": "Créations jusqu'au 31/12/2030<br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "100 % 5 ans, puis 60 % (6e année), 40 % (7e), 20 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale (totale puis progressive)",
        "Social": "Exonération spécifique (L.131-4-2)", 
        "Nature_activite": "Industrielles, commerciales, artisanales, BNC.<br><i>Exclusions : crédit-bail mobilier, location logements + certaines activités particulières</i>",
        "Regime_fiscal": "Tout régime (micro ou réel)",
        "Taille": "< 50 salariés, CA ≤ 10 M€ ou bilan ≤ 10 M€. Capital non détenu ≥ 25 % par grandes entreprises",
        "Implantation": "Implantation matérielle et activité effective (locaux, clientèle, production) en ZFU. Possible non sédentarité sous conditions.",
        "Condition_sociale": "Obligation emploi % salariés résidant en ZFU ou QPV à compter du 2ème salarié",
        "Exclusions_abus": "Non éligible si transfert/restructuration simple, ou changement de forme sans nouveauté.",
        "Plafonds_UE": "Plafond spécifique (50 k€/an + 5k€/emploi).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/LEGIARTI000026939165/"
    },
    
    "AFR": {
        "Nom": "ZAFR (zones AFR)",
        "References_legales": "CGI art. 44 sexies",
        "Periode": "Créations jusqu'au 31/12/2027",
        "Duree_exo": "100 % 2 ans, puis 75 % (3e), 50 % (4e), 25 % (5e).",
        "Impots_locaux": "Possible exonération sur délibération locale",
        "Social": "Non",
        "Nature_activite": "Industrielles, commerciales, artisanales, activités BNC exercées en société IS avec ≥ 3 salariés).<br><i>Exclusion activités particulières</i>",
        "Regime_fiscal": "Régime réel obligatoire",
        "Taille": "Pas de seuil général. Condition capital : pas détenu > 50 % par d'autres sociétés.",
        "Implantation": "Siège + moyens en zone. Activité non sédentaire : ≥ 85 % du CA en zone (sinon prorata limité).",
        "Condition_sociale": "3 salariés minimum si activité BNC",
        "Exclusions_abus": "Non éligible si extension d'activité existante (dépendance, franchise, etc.).",
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046003627/"
    },

    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (classique)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "Créations/reprises entre 01/07/2024 – 31/12/2029",
        "Duree_exo": "100 % 5 ans, puis 75 % (6e), 50 % (7e), 25 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Industrielles, commerciales, artisanales, libérales.<br><i>Exclusion activités particulières</i>",
        "Regime_fiscal": "Régime réel obligatoire",
        "Taille": "< 11 salariés.<br><i>Pas de condition liée au capital mais demandé dans le modèle de rescrit</i>",
        "Implantation": "Siège + moyens exclusivement en zone. Activité non sédentaire : CA hors zone ≤ 25 %.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Non éligible si activité déjà exonérée dans les 5 ans (ZFU, ZAFR, BER…), ou reprise intra-familiale (sauf 1ère reprise par descendant).",
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000049746820/"
    },
    
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (renforcée)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "Créations/reprises entre 01/01/2025 – 31/12/2029 + admet extensions d'établissement",
        "Duree_exo": "100 % 5 ans, puis 75 % (6e), 50 % (7e), 25 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Industrielles, commerciales, artisanales, libérales.<br><i>Exclusion activités particulières</i>",
        "Regime_fiscal": "réel ou micro",
        "Taille": "Création : PME UE (moins de 250 salariés, CA ≤ 50 M€, bilan ≤ 43 M€). Reprise : < 11 salariés.",
        "Implantation": "Pas d'exclusivité. Sédentaire : prorata de CA en zone. Non sédentaire : règle des 25 % + prorata si locaux en/hors zone.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Non éligible si activité déjà exonérée dans les 5 ans (ZFU, ZAFR, BER…), ou reprise intra-familiale (sauf 1ère reprise par descendant).",
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000051871914/"
    },

    "QPV": {
        "Nom": "QPPV",
        "References_legales": "Décret n° 2023-1314 du 28 décembre 2023",
        # MISE À JOUR PROROGATION 2030
        "Periode": "Créations jusqu'au 31/12/2030<br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "N/C",
        "Impots_locaux": "exonération TFPB 5 ans sauf délibération contraire collectivité",
        "Social": "nan",
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
# 4. GÉNÉRATEUR HTML DU TABLEAU (DYNAMIQUE)
# ==============================================================================
def get_zone_display(regime_key, row_data):
    """Génère la valeur de la ligne ZONE / CLASSEMENT"""
    raw_val = ""
    if regime_key == "ZFU":
        raw_val = str(row_data.get('NB_ZFU', '')).strip()
    elif regime_key == "QPV":
        raw_val = str(row_data.get('NB_QPV', '')).strip()
    elif regime_key == "AFR":
        raw_val = str(row_data.get('AFR', '')).strip()
    elif "ZFRR" in regime_key:
        raw_val = str(row_data.get('FRR', '')).strip()

    if raw_val.lower() in ['nan', '0', '', 'non']:
        return "-"
    
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

    html = "<table>"
    
    # HEADER
    html += "<thead><tr><th>Critères</th>"
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead><tbody>"
    
    # LIGNE 1 : ZONE (DYNAMIQUE)
    html += "<tr class='zone-row'><td>ZONE / CLASSEMENT</td>"
    for r in regimes:
        html += f"<td>{get_zone_display(r, row_data)}</td>"
    html += "</tr>"
    
    # LIGNE 2 : LIEN LÉGIFRANCE (DYNAMIQUE DATE)
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

    # LIGNES STATIQUES
    for label, key in rows_config:
        html += f"<tr><td>{label}</td>"
        for r in regimes:
            val = DATA_MATRIX[r].get(key, "-")
            if val == "nan" or pd.isna(val): val = ""
            html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table>"
    return html

# ==============================================================================
# 5. MOTEUR D'ANALYSE
# ==============================================================================
df = load_data()

st.title("Audit Zonage Fiscal")
st.markdown("**Tableau de synthèse multi-zonages**")
st.write("---")

if df is not None:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Rechercher...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), format="DD/MM/YYYY")

    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        st.subheader(f"Résultats pour : {row['COMMUNE']}")
        
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

        # 2. ZFU
        nb_zfu = str(row.get('NB_ZFU', '0')).strip()
        is_zfu = False
        if nb_zfu not in ['0', 'nan', 'NON', '', 'Non']:
             is_zfu = True

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
        if nb_qpv not in ['0', 'nan', 'NON', '', 'Non']:
            is_qpv = True
        
        # Prorogation 2030
        if is_qpv and date_crea <= date(2030, 12, 31):
            detected.append("QPV")

        # AFFICHAGE
        if detected:
            detected = list(dict.fromkeys(detected)) # Anti-doublon
            
            # Instruction Impression
            st.info("🖨️ **Pour imprimer cette fiche :** Appuyez sur **Ctrl+P** (Windows) ou **Cmd+P** (Mac). La mise en page s'adaptera automatiquement (format A4 Paysage).")
            
            # Tableau
            st.markdown(render_html_table(detected, row, date_crea), unsafe_allow_html=True)
            
            if "ZFU" in detected or "QPV" in detected:
                st.warning("⚠️ **Attention (ZFU / QPV)** : L'éligibilité dépend de l'adresse exacte. ")
        else:
            st.warning("Aucun dispositif zoné majeur détecté.")

else:
    st.error("Erreur de chargement. Le fichier Google Sheet n'est pas accessible.")
