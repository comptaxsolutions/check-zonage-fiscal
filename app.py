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
        font-size: 0.9em;
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
        font-size: 1em;
        border: 1px solid #34495e;
        width: 25%;
    }
    
    /* Première colonne (Libellés) */
    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        text-align: left;
        padding-left: 15px;
        border-right: 2px solid #dee2e6;
        width: 20%;
    }
    
    /* Cellules de données */
    td {
        padding: 10px;
        border: 1px solid #dee2e6;
        vertical-align: top;
        text-align: center;
        color: #333;
        line-height: 1.5;
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
    
    /* Classes utilitaires */
    .txt-green { color: #27ae60; font-weight: bold; }
    .txt-red { color: #c0392b; font-weight: bold; }
    .txt-orange { color: #d35400; font-weight: bold; }
    .txt-small { font-size: 0.85em; color: #666; display: block; margin-top: 4px; }
    
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
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
# 3. BASE DE CONNAISSANCE JURIDIQUE (2025)
# ==============================================================================

DATA_MATRIX = {
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (Renforcée)",
        "Base_Legale": "<b>CGI art. 44 quindecies A</b><br><span class='txt-small'>Loi Fin. 2024 art. 73 + LF 2025</span>",
        "Validite": "Jusqu'au 31/12/2029",
        "IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>Puis 75%, 50%, 25%",
        "IS_IR_Plafond": "Plafond AFR<br><span class='txt-small'>Selon carte 2022-2027</span>",
        "Social": "<span class='txt-green'>OUI (Renforcé)</span><br><span class='txt-small'>Exonérations patronales spécifiques</span>",
        "Impots_Locaux": "Sur délibération (CFE/TFPB)",
        "Regime_Imposition": "<span class='txt-green'>TOUT RÉGIME</span><br>Réel OU Micro-entreprise",
        "Effectif": "PME (< 11 salariés pour exonération max)",
        "Capital": "Non détenu > 50% par grands groupes",
        "Activite": "Indus, Com, Art, Libérale<br><span class='txt-small'>Excl: Banque, Immo, Gestion</span>",
        "Localisation": "Siège ET Activité en zone ZFRR+",
        "Transfert": "<span class='txt-orange'>Attention</span><br><span class='txt-small'>Création/Reprise privilégiées</span>"
    },
    
    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (Socle)",
        "Base_Legale": "<b>CGI art. 44 quindecies A</b><br><span class='txt-small'>Arrêtés juin 2024</span>",
        "Validite": "Jusqu'au 31/12/2029",
        "IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>Puis 75%, 50%, 25%",
        "IS_IR_Plafond": "Plafond AFR<br><span class='txt-small'>200k€ / 300k€ selon zone</span>",
        "Social": "<span class='txt-green'>OUI</span><br><span class='txt-small'>Exonérations patronales classiques</span>",
        "Impots_Locaux": "Sur délibération (CFE/TFPB)",
        "Regime_Imposition": "<span class='txt-red'>RÉEL OBLIGATOIRE</span><br>Micro exclu",
        "Effectif": "< 11 salariés",
        "Capital": "Non détenu > 50% par grands groupes",
        "Activite": "Indus, Com, Art, Libérale",
        "Localisation": "Siège ET Activité en zone",
        "Transfert": "<span class='txt-green'>Admis</span><br><span class='txt-small'>Sous conditions (Jurisprudence)</span>"
    },
    
    "ZFU": {
        "Nom": "ZFU - TE",
        "Base_Legale": "<b>CGI art. 44 octies A</b><br><span class='txt-small'>Loi 2006-396 prorogée</span>",
        "Validite": "<span class='txt-orange'>31/12/2025</span><br><span class='txt-small'>(Date théorique actuelle)</span>",
        "IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>Puis 60%, 40%, 20%",
        "IS_IR_Plafond": "50 000 € / an<br><span class='txt-small'>+ 5k€ par salarié résidant</span>",
        "Social": "<span class='txt-green'>OUI (Spécifique)</span><br><span class='txt-small'>Exonération bas salaires</span>",
        "Impots_Locaux": "Sur délibération",
        "Regime_Imposition": "<span class='txt-green'>TOUT RÉGIME</span>",
        "Effectif": "< 50 salariés",
        "Capital": "Indépendance (< 25% grands groupes)",
        "Activite": "Indus, Com, Art, BNC<br><span class='txt-small'>Excl: Location Immeuble</span>",
        "Localisation": "<span class='txt-red'>STRICTE</span><br>Activité matérielle DANS le périmètre",
        "Transfert": "<span class='txt-red'>EXCLU</span>"
    },

    "AFR": {
        "Nom": "AFR (Aide Régionale)",
        "Base_Legale": "<b>CGI art. 44 sexies</b><br><span class='txt-small'>Carte 2022-2027</span>",
        "Validite": "Jusqu'au 31/12/2027",
        "IS_IR_Taux": "<span class='txt-green'>100% (24 mois)</span><br>Puis dégressif",
        "IS_IR_Plafond": "De Minimis / AFR<br><span class='txt-small'>Selon taille entreprise</span>",
        "Social": "NON",
        "Impots_Locaux": "Facultative (CFE/TFPB)",
        "Regime_Imposition": "<span class='txt-red'>RÉEL OBLIGATOIRE</span>",
        "Effectif": "PME",
        "Capital": "Critères PME communautaires",
        "Activite": "Indus, Services Productifs",
        "Localisation": "Établissement en zone AFR",
        "Transfert": "Sous condition (Extension)"
    },

    "BER": {
        "Nom": "BER (Bassin Emploi)",
        "Base_Legale": "<b>CGI art. 44 duodecies</b>",
        "Validite": "Jusqu'au 31/12/2026",
        "IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>Puis dégressif",
        "IS_IR_Plafond": "Plafond AFR / De Minimis",
        "Social": "<span class='txt-green'>TOTALE</span><br><span class='txt-small'>Patronales + Salariales (partiel)</span>",
        "Impots_Locaux": "Exonération 5 ans",
        "Regime_Imposition": "<span class='txt-red'>RÉEL OBLIGATOIRE</span>",
        "Effectif": "PME",
        "Capital": "Indépendance PME",
        "Activite": "Indus, Com, Art",
        "Localisation": "Zone BER (Vallée Meuse...)",
        "Transfert": "Non (Création pure)"
    }
}

# ==============================================================================
# 4. GÉNÉRATEUR HTML
# ==============================================================================
def render_html_table(regimes):
    rows_config = [
        ("⚖️ JURIDIQUE", "header"),
        ("Base légale", "Base_Legale"),
        ("Validité", "Validite"),
        ("💰 EFFETS FISCAUX", "header"),
        ("IS/IR (Durée)", "IS_IR_Taux"),
        ("Plafond Avantage", "IS_IR_Plafond"),
        ("Social (URSSAF)", "Social"),
        ("Impôts Locaux", "Impots_Locaux"),
        ("🏢 CONDITIONS", "header"),
        ("Régime Imposition", "Regime_Imposition"),
        ("Effectif Max", "Effectif"),
        ("Activité Éligible", "Activite"),
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
st.markdown("**Outil d'aide à la décision – Régimes zonés (Hauts-de-France)**")
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
        
        # 1. ZFRR / ZFRR+
        # On sécurise l'extraction avec .get() pour éviter les erreurs si colonne vide
        frr_val = str(row.get('FRR', '')).strip().upper()
        DATE_ZFRR_PLUS = date(2025, 1, 1)
        DATE_ZFRR_CLASSIC = date(2024, 7, 1)
        
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            # Logique temporelle stricte
            if date_crea >= DATE_ZFRR_PLUS and ("+" in frr_val or "FRR+" in frr_val):
                detected.append("ZFRR_PLUS")
            elif date_crea >= DATE_ZFRR_CLASSIC:
                detected.append("ZFRR_CLASSIC")
            else:
                # Fallback pour période antérieure (Ancien ZRR assimilé ZFRR Classic pour affichage)
                detected.append("ZFRR_CLASSIC")

        # 2. ZFU
        DATE_FIN_ZFU = date(2025, 12, 31) # On prolonge à 2025 pour la simulation
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
            # On enlève les doublons potentiels
            detected = list(dict.fromkeys(detected))
            st.success(f"✅ {len(detected)} dispositif(s) identifié(s)")
            st.markdown(render_html_table(detected), unsafe_allow_html=True)
            st.caption("Source : Documentation Walter France & Textes officiels 2025.")
        else:
            st.warning("Aucun dispositif zoné majeur (ZFRR, ZFU, AFR, BER) détecté pour cette commune à cette date.")

else:
    st.error("Erreur de connexion au Google Sheet. Vérifiez l'ID.")
