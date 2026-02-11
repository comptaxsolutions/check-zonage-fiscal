import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (Tableau Pro)
# ==============================================================================
st.set_page_config(
    page_title="Vérification zonage fiscal",
    page_icon="🦁",
    layout="wide" # Format large pour le tableau
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Style du Tableau de Synthèse */
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Arial', sans-serif;
        font-size: 0.9em;
        margin-top: 20px;
    }
    th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid #ddd;
    }
    td {
        padding: 12px;
        border: 1px solid #ddd;
        vertical-align: top;
        color: #333;
    }
    /* Colonne des titres (la première) */
    td:first-child {
        background-color: #f8f9fa;
        font-weight: bold;
        width: 20%;
        color: #2c3e50;
    }
    /* Lignes de séparation */
    .section-header {
        background-color: #e9ecef;
        text-align: center;
        font-weight: bold;
        color: #495057;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 1px;
    }
    /* Mise en valeur des mots clés */
    .highlight-green { color: #27ae60; font-weight: bold; }
    .highlight-red { color: #c0392b; font-weight: bold; }
    .highlight-orange { color: #d35400; font-weight: bold; }
    
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I" # ID Mis à jour
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
# 3. BASE DE CONNAISSANCE (Données des Régimes)
# ==============================================================================
# C'est ici qu'on définit le contenu des cellules du tableau

DATA_REGIMES = {
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (Renforcée)",
        "IS_IR": "✅ EXONÉRATION 100%<br><small>5 ans, puis 75%, 50%, 25%</small>",
        "Social": "✅ EXONÉRATION PATRONALE<br><small>Jusqu'à 1.5 ou 2.4 SMIC (selon barème)</small>",
        "Plafond": "200 000 € (sur 3 ex.)<br><small>Règle De Minimis</small>",
        "Regime": "<span class='highlight-green'>TOUT RÉGIME</span><br><small>Réel OU Micro-entreprise</small>",
        "Effectif": "< 11 salariés<br><small>À la création/reprise</small>",
        "Activite": "Indus, Com, Artisanale, Libérale",
        "Exclusion": "Bancaire, Immo, Gestion",
        "Specificite": "Siège ET Activité 100% en zone"
    },
    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (Classique)",
        "IS_IR": "✅ EXONÉRATION 100%<br><small>5 ans, puis 75%, 50%, 25%</small>",
        "Social": "✅ EXONÉRATION PATRONALE<br><small>Sous conditions (Art L.131-4-2)</small>",
        "Plafond": "200 000 € (sur 3 ex.)",
        "Regime": "<span class='highlight-red'>RÉEL OBLIGATOIRE</span><br><small>Micro-entreprise EXCLUE</small>",
        "Effectif": "< 11 salariés",
        "Activite": "Indus, Com, Artisanale, Libérale",
        "Exclusion": "Bancaire, Immo, Gestion",
        "Specificite": "Transfert d'activité éligible<br><small>(Jurisprudence CE 2025)</small>"
    },
    "ZFU": {
        "Nom": "ZFU - Territoire Entrepreneur",
        "IS_IR": "✅ EXONÉRATION 100%<br><small>5 ans, puis 60%, 40%, 20%</small>",
        "Social": "⚠️ SPÉCIFIQUE<br><small>Exonération possible bas salaires</small>",
        "Plafond": "50 000 € / an<br><small>+ 5 000 € par salarié résidant</small>",
        "Regime": "<span class='highlight-green'>TOUT RÉGIME</span>",
        "Effectif": "< 50 salariés",
        "Activite": "Indus, Com, Artisanale, BNC",
        "Exclusion": "Location Immeubles (Hab/Com)",
        "Specificite": "<span class='highlight-orange'>CLAUSE D'EMBAUCHE</span><br><small>50% salariés résidents zone (dès le 2e)</small>"
    },
    "AFR": {
        "Nom": "ZAFR (Aide Régionale)",
        "IS_IR": "✅ EXONÉRATION 100%<br><small>24 mois, puis dégressif</small>",
        "Social": "❌ AUCUNE",
        "Plafond": "300 000 € (De Minimis)",
        "Regime": "<span class='highlight-red'>RÉEL OBLIGATOIRE</span>",
        "Effectif": "PME < 250 salariés",
        "Activite": "Indus, Com, Service Entreprise",
        "Exclusion": "Activités financières",
        "Specificite": "BNC éligible uniquement en Société IS"
    },
    "BER": {
        "Nom": "BER (Bassin Emploi)",
        "IS_IR": "✅ EXONÉRATION TOTALE",
        "Social": "✅ EXONÉRATION TOTALE<br><small>Charges patronales + fiscales</small>",
        "Plafond": "Règlementation UE",
        "Regime": "<span class='highlight-green'>TOUT RÉGIME</span>",
        "Effectif": "PME < 250 salariés",
        "Activite": "Indus, Com, Artisanale",
        "Exclusion": "Transport, Agri, Construction",
        "Specificite": "Entreprise non en difficulté"
    }
}

# ==============================================================================
# 4. GÉNÉRATION DU TABLEAU COMPARATIF
# ==============================================================================
def generer_tableau_html(regimes_detectes):
    """Crée le tableau HTML propre à partir des régimes trouvés"""
    
    if not regimes_detectes:
        return "<div style='padding:15px; background:#f8d7da; color:#721c24; border-radius:5px;'>Aucun dispositif détecté.</div>"

    # Ordre des lignes du tableau
    lignes_config = [
        ("--- EFFETS & AVANTAGES ---", "header"),
        ("Fiscal (IS/IR)", "IS_IR"),
        ("Social (URSSAF)", "Social"),
        ("Plafond / Durée", "Plafond"),
        ("--- CONDITIONS D'ÉLIGIBILITÉ ---", "header"),
        ("Régime Fiscal", "Regime"),
        ("Effectif Max", "Effectif"),
        ("Activité Éligible", "Activite"),
        ("Exclusions", "Exclusion"),
        ("Point de Vigilance", "Specificite")
    ]

    # Construction du HTML
    html = "<table>"
    
    # 1. En-tête (Noms des Zones)
    html += "<thead><tr><th>CRITÈRES</th>"
    for r in regimes_detectes:
        data = DATA_REGIMES[r]
        html += f"<th>{data['Nom']}</th>"
    html += "</tr></thead>"
    
    # 2. Corps du tableau
    html += "<tbody>"
    for label, key in lignes_config:
        if key == "header":
            # Ligne de séparation
            colspan = len(regimes_detectes) + 1
            html += f"<tr><td colspan='{colspan}' class='section-header'>{label}</td></tr>"
        else:
            # Ligne de données
            html += f"<tr><td>{label}</td>"
            for r in regimes_detectes:
                valeur = DATA_REGIMES[r].get(key, "-")
                html += f"<td>{valeur}</td>"
            html += "</tr>"
    html += "</tbody></table>"
    
    return html

# ==============================================================================
# 5. INTERFACE PRINCIPALE
# ==============================================================================

df = load_data()

st.title("Vérification zonage fiscal")
st.write("---")

if df is not None:
    # --- ZONE DE SAISIE ---
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox(
                "📍 Sélectionner la commune", 
                df['Label_Recherche'], 
                index=None, 
                placeholder="Tapez le nom ou le code..."
            )
        with c2:
            date_crea = st.date_input("📅 Date de création / reprise", date.today(), format="DD/MM/YYYY")

    # --- ANALYSE ---
    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        regimes_trouves = []

        # 1. DÉTECTION FRR / ZRR
        DATE_FRR = date(2024, 7, 1)
        val_frr = str(row['FRR']).strip().upper()
        
        if val_frr in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_FRR:
                if "FRR+" in val_frr or "+" in val_frr:
                    regimes_trouves.append("ZFRR_PLUS")
                else:
                    regimes_trouves.append("ZFRR_CLASSIC")
            else:
                # Ancien ZRR (Conditions proches du ZFRR Classique pour l'affichage)
                regimes_trouves.append("ZFRR_CLASSIC")

        # 2. DÉTECTION ZFU
        DATE_FIN_ZFU = date(2025, 12, 31)
        if str(row['NB_ZFU']) not in ['0', 'nan', 'Non', ''] and date_crea <= DATE_FIN_ZFU:
            regimes_trouves.append("ZFU")

        # 3. DÉTECTION AFR
        if str(row['AFR']) in ['Intégralement', 'Partiellement', 'Oui']:
            regimes_trouves.append("AFR")

        # 4. DÉTECTION BER
        if 'BER' in row and str(row['BER']) == 'Oui':
            regimes_trouves.append("BER")

        # --- AFFICHAGE DES RÉSULTATS ---
        st.divider()
        st.subheader(f"Analyse pour : {row['COMMUNE']}")
        
        if regimes_trouves:
            st.success(f"✅ {len(regimes_trouves)} Dispositif(s) identifié(s)")
            # Génération et affichage du tableau HTML
            html_table = generer_tableau_html(regimes_trouves)
            st.markdown(html_table, unsafe_allow_html=True)
            
            st.caption("Note : Ce tableau est une synthèse d'aide à la décision. Vérifiez toujours les textes officiels (BOFiP).")
        else:
             st.info("Aucun dispositif fiscal majeur détecté (ZRR, FRR, ZFU, AFR, BER) pour cette commune.")

else:
    st.error("Erreur de connexion au fichier Google Sheet. Vérifiez l'ID.")
