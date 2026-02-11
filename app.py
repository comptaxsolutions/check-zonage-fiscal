import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (Tableau Expert)
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
        margin-top: 10px;
        background-color: white;
    }
    
    /* En-têtes de colonnes (Zones) */
    th {
        background-color: #2c3e50;
        color: white;
        padding: 15px;
        text-align: center;
        text-transform: uppercase;
        font-size: 1.1em;
        border: 1px solid #34495e;
        width: 25%; /* Largeur fixe pour l'équilibre */
    }
    
    /* Première colonne (Critères) */
    td:first-child {
        background-color: #f1f3f5;
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
        vertical-align: middle;
        text-align: center;
        color: #333;
        line-height: 1.4;
    }
    
    /* Séparateurs de sections */
    .section-header {
        background-color: #e9ecef;
        text-align: left;
        padding-left: 15px;
        font-weight: 800;
        color: #c0392b; /* Rouge brique pour séparer */
        text-transform: uppercase;
        font-size: 0.9em;
        letter-spacing: 1px;
        border-top: 2px solid #ced4da;
    }
    
    /* Classes utilitaires pour le texte */
    .txt-green { color: #27ae60; font-weight: bold; }
    .txt-red { color: #c0392b; font-weight: bold; }
    .txt-orange { color: #d35400; font-weight: bold; }
    .txt-small { font-size: 0.85em; color: #666; display: block; margin-top: 4px; }
    .legal-ref { font-style: italic; color: #7f8c8d; font-size: 0.8em; }
    
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
# 3. MATRICE DE DONNÉES EXHAUSTIVE (Source : PDF Walter France)
# ==============================================================================

DATA_MATRIX = {
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (Renforcée)",
        # --- JURIDIQUE ---
        "Base_Legale": "CGI art. [cite_start]44 quindecies A [cite: 205]",
        [cite_start]"Validite": "Création/Reprise jusqu'au 31/12/2029 [cite: 205]",
        # --- EFFETS FISCAUX ---
        [cite_start]"IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>75% (6e), 50% (7e), 25% (8e) [cite: 205]",
        "IS_IR_Plafond": "200 000 € / 3 ex. (De Minimis)[cite_start]<br><span class='txt-small'>Plafond fiscal global</span> [cite: 205]",
        [cite_start]"Impots_Locaux": "Sur délibération (CFE / TFPB) [cite: 205]",
        # --- EFFETS SOCIAUX ---
        [cite_start]"Social": "<span class='txt-green'>OUI (Patronales)</span><br><span class='txt-small'>Jusqu'à 1.5 ou 2.4 SMIC</span> [cite: 205]",
        # --- CONDITIONS ENTREPRISE ---
        [cite_start]"Regime_Imposition": "<span class='txt-green'>TOUT RÉGIME</span><br>Réel OU Micro-entreprise [cite: 212]",
        [cite_start]"Effectif": "< 11 salariés [cite: 212]",
        [cite_start]"Capital": "Détenu < 50% par d'autres sociétés [cite: 212]",
        # --- CONDITIONS ACTIVITÉ ---
        [cite_start]"Activite": "Indus, Com, Art, Libérale<br><span class='txt-small'>Excl: Banque, Immo, Gestion</span> [cite: 212]",
        [cite_start]"Localisation": "Siège social + Moyens d'exploitation<br><span class='txt-small'>Exclusivement en zone</span> [cite: 212]",
        [cite_start]"Transfert": "<span class='txt-green'>ÉLIGIBLE</span><br><span class='txt-small'>Même sans transfert de clientèle (CE 2025)</span> [cite: 216]"
    },
    
    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (Classique)",
        # --- JURIDIQUE ---
        "Base_Legale": "CGI art. [cite_start]44 quindecies A [cite: 205]",
        [cite_start]"Validite": "Création/Reprise jusqu'au 31/12/2029 [cite: 205]",
        # --- EFFETS FISCAUX ---
        [cite_start]"IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>75% (6e), 50% (7e), 25% (8e) [cite: 205]",
        "IS_IR_Plafond": "200 000 € / 3 ex. (De Minimis) [cite_start][cite: 205]",
        [cite_start]"Impots_Locaux": "Sur délibération (CFE / TFPB) [cite: 205]",
        # --- EFFETS SOCIAUX ---
        [cite_start]"Social": "<span class='txt-green'>OUI (Patronales)</span><br><span class='txt-small'>Sous conditions L.131-4-2</span> [cite: 205]",
        # --- CONDITIONS ENTREPRISE ---
        [cite_start]"Regime_Imposition": "<span class='txt-red'>RÉEL OBLIGATOIRE</span><br>Micro-entreprise EXCLUE [cite: 212]",
        [cite_start]"Effectif": "< 11 salariés [cite: 212]",
        [cite_start]"Capital": "Détenu < 50% par d'autres sociétés [cite: 212]",
        # --- CONDITIONS ACTIVITÉ ---
        [cite_start]"Activite": "Indus, Com, Art, Libérale<br><span class='txt-small'>Excl: Banque, Immo, Gestion</span> [cite: 212]",
        [cite_start]"Localisation": "Siège social + Moyens d'exploitation<br><span class='txt-small'>Exclusivement en zone</span> [cite: 212]",
        [cite_start]"Transfert": "<span class='txt-green'>ÉLIGIBLE</span><br><span class='txt-small'>Jurisprudence CE 2-6-2025</span> [cite: 216]"
    },
    
    "ZFU": {
        "Nom": "ZFU - TE (Territoire Entrepreneur)",
        # --- JURIDIQUE ---
        "Base_Legale": "CGI art. [cite_start]44 octies A [cite: 205]",
        [cite_start]"Validite": "Créations jusqu'au <span class='txt-red'>31/12/2025</span> [cite: 205]",
        # --- EFFETS FISCAUX ---
        [cite_start]"IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>60% (6e), 40% (7e), 20% (8e) [cite: 205]",
        [cite_start]"IS_IR_Plafond": "50 000 € / an<br><span class='txt-small'>+ 5k€/salarié résidant</span> [cite: 205]",
        [cite_start]"Impots_Locaux": "Sur délibération [cite: 205]",
        # --- EFFETS SOCIAUX ---
        [cite_start]"Social": "Non Applicable (Zonage distinct)<br><span class='txt-small'>Voir exonérations spécifiques ZFU</span> [cite: 205]",
        # --- CONDITIONS ENTREPRISE ---
        [cite_start]"Regime_Imposition": "<span class='txt-green'>TOUT RÉGIME</span><br>Réel OU Micro [cite: 212]",
        [cite_start]"Effectif": "< 50 salariés [cite: 212]",
        [cite_start]"Capital": "< 25% détenu par entreprise > 250 sal. [cite: 212]",
        # --- CONDITIONS ACTIVITÉ ---
        [cite_start]"Activite": "Indus, Com, Art, BNC<br><span class='txt-small'>Excl: Location Immeuble (Hab/Com)</span> [cite: 212]",
        [cite_start]"Localisation": "<span class='txt-orange'>STRICTE</span><br>Activité matérielle DANS le périmètre [cite: 212]",
        [cite_start]"Transfert": "<span class='txt-red'>EXCLU</span><br>Sauf création d'activité nouvelle [cite: 212]"
    },

    "AFR": {
        "Nom": "AFR (Aide Finalité Régionale)",
        # --- JURIDIQUE ---
        "Base_Legale": "CGI art. [cite_start]44 sexies [cite: 205]",
        [cite_start]"Validite": "Créations jusqu'au 31/12/2027 [cite: 205]",
        # --- EFFETS FISCAUX ---
        [cite_start]"IS_IR_Taux": "<span class='txt-green'>100% (24 mois)</span><br>75% (3e), 50% (4e), 25% (5e) [cite: 205]",
        [cite_start]"IS_IR_Plafond": "Règle De Minimis<br><span class='txt-small'>300 k€ sur 3 exercices</span> [cite: 205]",
        [cite_start]"Impots_Locaux": "Sur délibération [cite: 205]",
        # --- EFFETS SOCIAUX ---
        [cite_start]"Social": "Non Applicable [cite: 205]",
        # --- CONDITIONS ENTREPRISE ---
        [cite_start]"Regime_Imposition": "<span class='txt-red'>RÉEL OBLIGATOIRE</span> [cite: 212]",
        [cite_start]"Effectif": "PME < 250 salariés [cite: 212]",
        [cite_start]"Capital": "< 25% détenu par entreprise > 250 sal. [cite: 212]",
        # --- CONDITIONS ACTIVITÉ ---
        [cite_start]"Activite": "Indus, Com, Art<br><span class='txt-small'>BNC éligible uniquement en Société IS</span> [cite: 212]",
        [cite_start]"Localisation": "Siège social + Activité [cite: 212]",
        [cite_start]"Transfert": "Éligible sous conditions (Extension) [cite: 212]"
    },

    "BER": {
        "Nom": "BER (Bassin Emploi)",
        "Base_Legale": "CGI art. 44 sexies A",
        "Validite": "Créations jusqu'au 31/12/2026",
        "IS_IR_Taux": "<span class='txt-green'>100% (5 ans)</span><br>Puis dégressif",
        "IS_IR_Plafond": "Règle De Minimis (300 k€)",
        "Impots_Locaux": "Exonération CFE/CVAE/TFPB (5 ans)",
        "Social": "<span class='txt-green'>EXONÉRATION TOTALE</span><br>Patronales + Salariales (partiel)",
        "Regime_Imposition": "Réel Obligatoire",
        "Effectif": "PME < 250 salariés",
        "Capital": "Indépendant",
        "Activite": "Indus, Com, Art (Hors Transport/Agri)",
        "Localisation": "Implantation en zone BER",
        "Transfert": "Non (Création pure ou reprise)"
    }
}

# ==============================================================================
# 4. GÉNÉRATION DU TABLEAU HTML
# ==============================================================================
def render_html_table(regimes):
    """Génère le code HTML du tableau comparatif"""
    
    # Configuration des lignes à afficher (Ordre logique Expert)
    rows_config = [
        ("⚖️ JURIDIQUE", "header"),
        ("Base Légale", "Base_Legale"),
        ("Validité (Date limite)", "Validite"),
        
        ("💰 EFFETS FISCAUX & SOCIAUX", "header"),
        ("Exonération IS/IR (Durée)", "IS_IR_Taux"),
        ("Plafond Avantage Fiscal", "IS_IR_Plafond"),
        ("Exonération Sociale (URSSAF)", "Social"),
        ("Impôts Locaux (CFE/TFPB)", "Impots_Locaux"),
        
        ("🏢 CONDITIONS ENTREPRISE", "header"),
        ("Régime d'Imposition", "Regime_Imposition"),
        ("Effectif Max", "Effectif"),
        ("Détention Capital", "Capital"),
        
        ("🏭 CONDITIONS ACTIVITÉ", "header"),
        ("Activités Éligibles", "Activite"),
        ("Localisation Requise", "Localisation"),
        ("Transfert / Reprise", "Transfert")
    ]

    html = "<table>"
    
    # 1. HEADER (Zones)
    html += "<thead><tr><th>CRITÈRES</th>"
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead>"
    
    # 2. BODY
    html += "<tbody>"
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
# 5. MAIN
# ==============================================================================
df = load_data()

st.title("Audit Zonage Fiscal")
st.markdown("**Outil d'aide à la décision - Basé sur la documentation technique 2025**")
st.write("---")

if df is not None:
    # INPUTS
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Rechercher...")
        with c2:
            date_crea = st.date_input("📅 Date opération", date.today(), format="DD/MM/YYYY")

    # LOGIC
    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        st.subheader(f"Résultats pour : {row['COMMUNE']}")
        
        # DÉTECTION DES RÉGIMES
        detected = []
        
        # 1. ZFRR
        DATE_FRR = date(2024, 7, 1)
        frr_val = str(row['FRR']).strip().upper()
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_FRR:
                if "FRR+" in frr_val or "+" in frr_val:
                    detected.append("ZFRR_PLUS")
                else:
                    detected.append("ZFRR_CLASSIC")
            else:
                detected.append("ZFRR_CLASSIC") # Fallback ancien ZRR

        # 2. ZFU
        DATE_FIN_ZFU = date(2025, 12, 31)
        if str(row['NB_ZFU']) not in ['0', 'nan', 'Non', ''] and date_crea <= DATE_FIN_ZFU:
            detected.append("ZFU")

        # 3. AFR
        if str(row['AFR']) in ['Intégralement', 'Partiellement', 'Oui']:
            detected.append("AFR")

        # 4. BER
        if 'BER' in row and str(row['BER']) == 'Oui':
            detected.append("BER")

        # RENDER
        if detected:
            st.success(f"✅ {len(detected)} Dispositif(s) disponible(s)")
            table_html = render_html_table(detected)
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Légende
            st.markdown("""
            <div style='margin-top:15px; font-size:0.8em; color:#666;'>
            Sources : CGI, BOFiP, Documentation Walter France. <br>
            *Les exonérations sociales ZFU relèvent d'un dispositif spécifique non traité ici en détail (L.131-4-2 CSS).
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("Aucun zonage fiscal incitatif majeur (ZRR, ZFU, AFR, BER) pour cette commune.")

else:
    st.error("Erreur chargement données.")
