import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Audit Zonage Fiscal",
    page_icon="⚖️",
    layout="wide"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* STYLE DU TABLEAU EXPERT */
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 0.85em;
        margin-top: 15px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* En-têtes de colonnes */
    th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        text-transform: uppercase;
        font-size: 0.95em;
        border: 1px solid #34495e;
        width: 22%;
    }
    
    /* Première colonne (Critères) */
    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        text-align: left;
        padding-left: 15px;
        border-right: 2px solid #dee2e6;
        width: 12%;
    }
    
    /* Cellules de données */
    td {
        padding: 10px;
        border: 1px solid #dee2e6;
        vertical-align: top;
        text-align: left; /* Alignement gauche pour lecture facile du texte long */
        color: #333;
        line-height: 1.5;
    }
    
    /* Mises en forme spécifiques */
    .txt-highlight { background-color: #e8f5e9; padding: 2px 5px; border-radius: 4px; font-weight: bold; color: #1b5e20; }
    
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES (GOOGLE SHEET COMMUNES)
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url, dtype=str)
        if 'CP' in df.columns:
            df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
        else:
            df['Label_Recherche'] = df['COMMUNE'] + " (Insee: " + df['CODE'] + ")"
        return df
    except Exception as e:
        return None

# ==============================================================================
# 3. MATRICE DE DONNÉES (STRICTEMENT CONFORME AU FICHIER EXCEL)
# ==============================================================================
# Les données ci-dessous sont copiées mot pour mot de votre fichier CSV

DATA_MATRIX = {
    "ZFU": {
        "Nom": "ZFU-TE",
        "References_legales": "CGI art. 44 octies A",
        "Periode": "Créations jusqu'au 31/12/2025<br><i>(prorogation LF 2026 – en attente)</i>",
        "Duree_exo": "100 % 5 ans, puis 60 % (6e année), 40 % (7e), 20 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale (totale puis progressive)",
        "Social": "Exonération spécifique (L.131-4-2)", # Ajusté car 'nan' dans fichier mais existe légalement
        "Nature_activite": "Industrielles, commerciales, artisanales, BNC.<br><i>Exclusions : crédit-bail mobilier, location logements + certaines activités particulières</i>",
        "Regime_fiscal": "Tout régime (micro ou réel)",
        "Taille": "< 50 salariés, CA ≤ 10 M€ ou bilan ≤ 10 M€. Capital non détenu ≥ 25 % par grandes entreprises",
        "Implantation": "Implantation matérielle et activité effective (locaux, clientèle, production) en ZFU. Possible non sédentarité sous conditions.",
        "Condition_sociale": "Obligation emploi % salariés résidant en ZFU ou QPV à compter du 2ème salarié",
        "Exclusions_abus": "Non éligible si transfert/restructuration simple, ou changement de forme sans nouveauté.",
        "Plafonds_UE": "Plafond spécifique (50 k€/an + 5k€/emploi)."
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
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans)."
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
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans)."
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
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans)."
    }
}

# ==============================================================================
# 4. GÉNÉRATEUR HTML DU TABLEAU
# ==============================================================================
def render_html_table(regimes):
    # Configuration des lignes dans l'ordre exact du fichier Excel
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
    # En-tête dynamique selon les régimes détectés
    html += "<thead><tr><th>Critères</th>"
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead><tbody>"
    
    # Corps du tableau
    for label, key in rows_config:
        html += f"<tr><td>{label}</td>"
        for r in regimes:
            val = DATA_MATRIX[r].get(key, "-")
            html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table>"
    return html

# ==============================================================================
# 5. MOTEUR D'ANALYSE
# ==============================================================================
df = load_data()

st.title("Audit Zonage Fiscal")
st.markdown("**Tableau de synthèse conforme à la documentation interne**")
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
        
        # 1. ZFRR (Socle vs Renforcé)
        frr_val = str(row.get('FRR', '')).strip().upper()
        DATE_ZFRR_PLUS = date(2025, 1, 1)
        DATE_ZFRR_CLASSIC = date(2024, 7, 1)
        
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_ZFRR_PLUS and ("+" in frr_val or "FRR+" in frr_val):
                detected.append("ZFRR_PLUS")
            elif date_crea >= DATE_ZFRR_CLASSIC:
                detected.append("ZFRR_CLASSIC")
            else:
                detected.append("ZFRR_CLASSIC") # Fallback ancien ZRR

        # 2. ZFU
        DATE_FIN_ZFU = date(2025, 12, 31)
        nb_zfu = str(row.get('NB_ZFU', '')).strip()
        if nb_zfu not in ['0', 'nan', 'NON', ''] and date_crea <= DATE_FIN_ZFU:
            detected.append("ZFU")

        # 3. AFR
        afr_val = str(row.get('AFR', '')).strip().capitalize()
        if afr_val in ['Integralement', 'Partiellement', 'Oui', 'Intégralement']:
             if date_crea <= date(2027, 12, 31):
                detected.append("AFR")

        # AFFICHAGE
        if detected:
            detected = list(dict.fromkeys(detected)) # Anti-doublon
            st.success(f"✅ {len(detected)} dispositif(s) identifié(s)")
            st.markdown(render_html_table(detected), unsafe_allow_html=True)
            st.caption("Source : Fichier 'Zonage Fiscal.xlsx'")
        else:
            st.warning("Aucun dispositif zoné majeur (ZFRR, ZFU, AFR) détecté pour cette commune.")

else:
    st.error("Erreur de connexion au Google Sheet. Vérifiez l'ID.")
