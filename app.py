import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Audit Zonage Fiscal",
    page_icon="🦁",
    layout="wide"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* STYLE DU TABLEAU EXPERT */
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.85em;
        margin-top: 15px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* En-têtes de colonnes (Zones) */
    th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        text-transform: uppercase;
        font-size: 1em;
        border: 1px solid #34495e;
        width: 20%;
    }
    
    /* Première colonne (Libellés) */
    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        text-align: left;
        padding-left: 15px;
        border-right: 2px solid #dee2e6;
        width: 15%;
    }
    
    /* Cellules de données */
    td {
        padding: 10px;
        border: 1px solid #dee2e6;
        vertical-align: top;
        text-align: center;
        color: #333;
        line-height: 1.4;
    }
    
    /* Séparateurs */
    .section-header {
        background-color: #e9ecef;
        text-align: left;
        padding-left: 15px;
        font-weight: 800;
        color: #c0392b;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 1px;
        border-top: 2px solid #ced4da;
    }
    
    /* Mises en forme spécifiques */
    .txt-green { color: #27ae60; font-weight: bold; }
    .txt-red { color: #c0392b; font-weight: bold; }
    .txt-orange { color: #d35400; font-weight: bold; }
    
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

DATA_MATRIX = {
    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (SOCLE)",
        "Ref_Legale": "CGI art. 44 quindecies A",
        "Date_Limite": "31/12/2029",
        "Impot_Benefice": "Exonération",
        "Taux": "100% (5 ans), 75% (6e), 50% (7e), 25% (8e)",
        "Plafond": "200 000 € (sur 3 ex) - De minimis",
        "Impots_Locaux": "Exonération CFE / CVAE (sur délibération)",
        "Charges_Sociales": "Exonération patronale (L.131-4-2)",
        "Regime": "<span class='txt-red'>Réel (Simplifié ou Normal) - MICRO EXCLU</span>",
        "Effectif": "< 11 salariés",
        "Activite": "Ind, Com, Art, Libérale",
        "Exclusions": "Banque, Assurance, Gestion, Immo",
        "Capital": "< 50% par d'autres sociétés",
        "Localisation": "Siège social + Activité + Moyens",
        "Transfert": "Éligible (Jurisprudence CE 2025)"
    },
    
    "ZFRR_PLUS": {
        "Nom": "ZFRR + (RENFORCE)",
        "Ref_Legale": "CGI art. 44 quindecies A",
        "Date_Limite": "31/12/2029",
        "Impot_Benefice": "Exonération",
        "Taux": "100% (5 ans), 75% (6e), 50% (7e), 25% (8e)",
        "Plafond": "200 000 € (sur 3 ex) - De minimis",
        "Impots_Locaux": "Exonération CFE / CVAE (sur délibération)",
        "Charges_Sociales": "<span class='txt-green'>Exonération majorée (jusqu'à 2.4 SMIC)</span>",
        "Regime": "<span class='txt-green'>Tout régime (Micro autorisé)</span>",
        "Effectif": "< 11 salariés",
        "Activite": "Ind, Com, Art, Libérale",
        "Exclusions": "Banque, Assurance, Gestion, Immo",
        "Capital": "< 50% par d'autres sociétés",
        "Localisation": "Siège social + Activité + Moyens",
        "Transfert": "Éligible (Jurisprudence CE 2025)"
    },
    
    "ZFU": {
        "Nom": "ZFU - TE",
        "Ref_Legale": "CGI art. 44 octies A",
        "Date_Limite": "31/12/2025",
        "Impot_Benefice": "Exonération",
        "Taux": "100% (5 ans), 60%, 40%, 20%",
        "Plafond": "50k€ + 5k€/salarié",
        "Impots_Locaux": "Exonération CFE / CVAE (sur délibération)",
        "Charges_Sociales": "Exonération spécifique ZFU",
        "Regime": "<span class='txt-green'>Tout régime</span>",
        "Effectif": "< 50 salariés",
        "Activite": "Ind, Com, Art, BNC",
        "Exclusions": "Location Immeuble",
        "Capital": "< 25% par sociétés > 250 sal.",
        "Localisation": "<span class='txt-orange'>Activité matérielle DANS le périmètre</span>",
        "Transfert": "<span class='txt-red'>Non éligible (Sauf création)</span>"
    },

    "AFR": {
        "Nom": "AFR",
        "Ref_Legale": "CGI art. 44 sexies",
        "Date_Limite": "31/12/2027",
        "Impot_Benefice": "Exonération",
        "Taux": "100% (24 mois), puis dégressif",
        "Plafond": "De Minimis / Carte AFR",
        "Impots_Locaux": "Facultative (CFE)",
        "Charges_Sociales": "NON",
        "Regime": "<span class='txt-red'>Réel Obligatoire</span>",
        "Effectif": "PME (< 250 salariés)",
        "Activite": "Ind, Com, Art (BNC si Sté IS)",
        "Exclusions": "Activités financières",
        "Capital": "< 25% par grandes entreprises",
        "Localisation": "Etablissement en zone",
        "Transfert": "Sous conditions (Extension)"
    },

    "BER": {
        "Nom": "BER",
        "Ref_Legale": "CGI art. 44 sexies A",
        "Date_Limite": "31/12/2026",
        "Impot_Benefice": "Exonération",
        "Taux": "100% (5 ans)",
        "Plafond": "De Minimis",
        "Impots_Locaux": "Exonération Totale",
        "Charges_Sociales": "<span class='txt-green'>Totale (Patronale + Salariale)</span>",
        "Regime": "Réel",
        "Effectif": "PME (< 250 salariés)",
        "Activite": "Ind, Com, Art",
        "Exclusions": "Transport, Agri, Construction",
        "Capital": "Indépendant",
        "Localisation": "Zone BER",
        "Transfert": "Non"
    }
}

# ==============================================================================
# 4. GÉNÉRATEUR HTML DU TABLEAU
# ==============================================================================
def render_html_table(regimes):
    # Configuration des lignes exactement selon votre Excel
    rows_config = [
        ("JURIDIQUE", "header"),
        ("Référence légale", "Ref_Legale"),
        ("Date limite", "Date_Limite"),
        
        ("EFFETS FISCAUX", "header"),
        ("Impôt sur les bénéfices", "Impot_Benefice"),
        ("Taux / Durée", "Taux"),
        ("Plafond", "Plafond"),
        ("Impôts locaux", "Impots_Locaux"),
        ("Charges sociales", "Charges_Sociales"),
        
        ("CONDITIONS", "header"),
        ("Régime d'imposition", "Regime"),
        ("Effectif", "Effectif"),
        ("Activité", "Activite"),
        ("Exclusions", "Exclusions"),
        ("Capital", "Capital"),
        ("Localisation", "Localisation"),
        ("Transfert", "Transfert")
    ]

    html = "<table>"
    html += "<thead><tr><th>CRITÈRES</th>"
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead><tbody>"
    
    for label, key in rows_config:
        if key == "header":
            colspan = len(regimes) + 1
            html += f"<tr><td colspan='{colspan}' class='section-header'>{label}</td></tr>"
        else:
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
st.markdown("**Tableau comparatif officiel - Basé sur les textes 2025**")
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
            # Logique temporelle pour distinguer Socle vs Renforcé
            if date_crea >= DATE_ZFRR_PLUS and ("+" in frr_val or "FRR+" in frr_val):
                detected.append("ZFRR_PLUS")
            elif date_crea >= DATE_ZFRR_CLASSIC:
                detected.append("ZFRR_CLASSIC")
            else:
                detected.append("ZFRR_CLASSIC")

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

        # 4. BER
        ber_val = str(row.get('BER', '')).strip().capitalize()
        if ber_val == 'Oui':
            if date_crea <= date(2026, 12, 31):
                detected.append("BER")

        # AFFICHAGE
        if detected:
            detected = list(dict.fromkeys(detected)) # Anti-doublon
            st.success(f"✅ {len(detected)} dispositif(s) identifié(s)")
            st.markdown(render_html_table(detected), unsafe_allow_html=True)
        else:
            st.warning("Aucun dispositif zoné majeur (ZFRR, ZFU, AFR, BER) détecté pour cette commune.")

else:
    st.error("Erreur de connexion au Google Sheet. Vérifiez l'ID.")
