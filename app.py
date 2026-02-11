import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Vérification zonage fiscal",
    page_icon="🦁",
    layout="centered"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Style des Checklists */
    .checklist-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #2c3e50;
        font-size: 0.95em;
        margin-top: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .checklist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
    }
    .checklist-title {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.1em;
    }
    .badge-scope {
        background-color: #e2e6ea;
        color: #495057;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
        text-transform: uppercase;
    }
    .benefits-box {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-weight: 500;
        border: 1px solid #c3e6cb;
    }
    ul { margin-bottom: 0; padding-left: 20px; }
    li { margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    # 👇👇👇 TON ID GOOGLE SHEET ICI 👇👇👇
    sheet_id = "1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I" 
    
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url, dtype=str)
        # Création de la colonne recherche
        if 'CP' in df.columns:
            df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
        else:
            df['Label_Recherche'] = df['COMMUNE'] + " (Insee: " + df['CODE'] + ")"
        return df
    except Exception as e:
        return None

# ==============================================================================
# 3. FONCTIONS D'AFFICHAGE (Conditions & Avantages)
# ==============================================================================

def afficher_details_regime(type_regime):
    """Affiche les détails (Avantages, Scope, Conditions) selon le régime"""
    
    # --- ZFRR PLUS (RENFORCÉE) ---
    # Source : PDF Page 16 (Micro autorisé)
    if type_regime == "ZFRR_PLUS":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #27ae60;">
            <div class="checklist-header">
                <span class="checklist-title">📋 ZFRR+ (Renforcée)</span>
                <span class="badge-scope">Création • Reprise • Extension</span>
            </div>
            <div class="benefits-box">
                💰 <b>Avantages :</b> Exonération IS/IR (100% 5 ans + dégressif) + Exonération charges patronales.
            </div>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:green; font-weight:bold;">TOUT RÉGIME (Réel OU Micro)</span>.</li>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale ou libérale.</li>
                <li><b>Effectif :</b> Moins de 11 salariés.</li>
                <li><b>Exclusions :</b> Activités bancaires, financières, immobilières.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- ZFRR CLASSIQUE ---
    # Source : PDF Page 16 (Réel obligatoire)
    elif type_regime == "ZFRR_CLASSIC":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #2ecc71;">
            <div class="checklist-header">
                <span class="checklist-title">📋 ZFRR (Classique)</span>
                <span class="badge-scope">Création • Reprise</span>
            </div>
            <div class="benefits-box">
                💰 <b>Avantages :</b> Exonération IS/IR (100% 5 ans + dégressif) + Exonération charges patronales.
            </div>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span> (Pas de Micro).</li>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale ou libérale.</li>
                <li><b>Effectif :</b> Moins de 11 salariés.</li>
                <li><b>Capital :</b> Détenu à moins de 50% par d'autres sociétés.</li>
                <li><b>Note :</b> Le transfert d'activité est éligible (Jurisprudence 2025).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- ZFU ---
    # Source : PDF Page 16 (Création uniquement, 50k plafond)
    elif type_regime == "ZFU":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #e67e22;">
            <div class="checklist-header">
                <span class="checklist-title">📋 ZFU-TE (Territoire Entrepreneur)</span>
                <span class="badge-scope">Création uniquement</span>
            </div>
            <div class="benefits-box">
                💰 <b>Avantages :</b> Exonération IS/IR (100% 5 ans) jusqu'à 50 000 € de bénéfice + 5k€/salarié.
            </div>
            <ul>
                <li><b>Date limite :</b> Créations jusqu'au <b>31/12/2025</b>.</li>
                <li><b>Régime Fiscal :</b> <span style="color:green; font-weight:bold;">TOUT RÉGIME</span> (Micro accepté).</li>
                <li><b>Clause d'embauche :</b> Dès le 2ème salarié, 50% résidents ZFU/QPV.</li>
                <li><b>Localisation :</b> Activité matérielle et effective DANS le périmètre (bureau/atelier).</li>
                <li><b>Effectif :</b> Moins de 50 salariés.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    # --- AFR ---
    elif type_regime == "AFR":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #2980b9;">
            <div class="checklist-header">
                <span class="checklist-title">📋 ZAFR (Aide Finalité Régionale)</span>
                <span class="badge-scope">Création</span>
            </div>
            <div class="benefits-box">
                💰 <b>Avantages :</b> Exonération 100% (24 mois) puis dégressif.
            </div>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span>.</li>
                <li><b>Forme :</b> Sociétés soumises à l'IS (pour les activités libérales).</li>
                <li><b>Plafond :</b> Règles "de minimis" (300 k€ sur 3 ans).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- BER ---
    elif type_regime == "BER":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #8e44ad;">
            <div class="checklist-header">
                <span class="checklist-title">📋 BER (Bassin d'Emploi)</span>
                <span class="badge-scope">Création • Reprise</span>
            </div>
            <div class="benefits-box">
                💰 <b>Avantages :</b> Exonération Totale Impôts + Charges Sociales Patronales.
            </div>
            <ul>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale.</li>
                <li><b>PME :</b> Effectif < 250 salariés, CA < 50 M€.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 4. INTERFACE PRINCIPALE
# ==============================================================================

df = load_data()

st.title("Fiscal-Check HDF")
st.caption("Comparateur de régimes - Mise à jour Documentaire Sept 2025")
st.write("---")

if df is not None:
    # --- ZONE DE SAISIE (Simplifiée) ---
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Tapez Amiens...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), format="DD/MM/YYYY")
        
        # SUPPRESSION DU BOUTON CREATION/REPRISE ICI
        # L'info est désormais donnée dans chaque bloc "Champ d'application"

    # --- LOGIQUE DE DÉTECTION ET AFFICHAGE ---
    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        st.subheader(f"Analyse pour : {row['COMMUNE']}")

        # 1. ANALYSE FRANCE RURALITÉS (ZFRR+ vs ZFRR)
        DATE_FRR = date(2024, 7, 1)
        valeur_frr = str(row['FRR']).strip().upper() # On met en majuscule pour éviter les erreurs
        
        # On vérifie si c'est une zone FRR
        if valeur_frr in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            
            # Si on est après la date de réforme
            if date_crea >= DATE_FRR:
                # DISTINCTION ZFRR+ / ZFRR CLASSIQUE
                if "FRR+" in valeur_frr:
                    st.success("✅ **ÉLIGIBLE ZFRR+ (Renforcée)**")
                    afficher_details_regime("ZFRR_PLUS")
                else:
                    st.success("✅ **ÉLIGIBLE ZFRR (Classique)**")
                    afficher_details_regime("ZFRR_CLASSIC")
            else:
                # Avant Juillet 2024 = Ancien ZRR
                st.success("✅ **ÉLIGIBLE ZRR (Ancien Régime)**")
                afficher_details_regime("ZFRR_CLASSIC") # Conditions similaires au ZFRR classique

        # 2. ANALYSE ZFU
        DATE_FIN_ZFU = date(2025, 12, 31)
        if str(row['NB_ZFU']) not in ['0', 'nan', 'Non', '']:
            if date_crea <= DATE_FIN_ZFU:
                st.warning("⚠️ **COMMUNE ZFU-TE** (Sous réserve adresse)")
                afficher_details_regime("ZFU")
            else:
                st.error(f"❌ Zone ZFU : Dispositif expiré (Date limite : {DATE_FIN_ZFU.strftime('%d/%m/%Y')})")

        # 3. ANALYSE AFR
        if str(row['AFR']) in ['Intégralement', 'Partiellement', 'Oui']:
            st.info("ℹ️ **ZONE AFR**")
            afficher_details_regime("AFR")

        # 4. ANALYSE BER
        if 'BER' in row and str(row['BER']) == 'Oui':
            st.success("✅ **ÉLIGIBLE BER**")
            afficher_details_regime("BER")

        # 5. CAS NÉGATIF
        if valeur_frr not in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI'] and str(row['NB_ZFU']) in ['0', 'nan', 'Non', ''] and str(row['AFR']) not in ['Intégralement', 'Partiellement', 'Oui'] and str(row.get('BER', 'Non')) != 'Oui':
             st.info("Aucun dispositif ZRR/FRR/ZFU/AFR/BER détecté pour cette commune.")

else:
    st.error("Erreur chargement Google Sheet.")
