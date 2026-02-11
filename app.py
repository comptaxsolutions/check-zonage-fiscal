import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Fiscal-Check | Hauts-de-France",
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
    .checklist-title {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.1em;
        margin-bottom: 10px;
        display: block;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
    }
    .expert-note {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9em;
        color: #0c5460;
        margin-top: 10px;
        border: 1px solid #bee5eb;
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
    sheet_id = "TON_ID_GOOGLE_SHEET_ICI" 
    
    url = f"https://docs.google.com/spreadsheets/d/1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I/export?format=csv"
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
# 3. FONCTIONS D'AFFICHAGE DES CONDITIONS (Basées sur le PDF Walter France)
# ==============================================================================

def afficher_checklist(dispositif, type_ope):
    """Affiche les conditions basées sur la documentation expert"""
    
    # --- CONDITIONS FRR / ZRR (Source: Page 16 du PDF) ---
    if dispositif == "FRR":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #27ae60;">
            <span class="checklist-title">📋 Conditions ZFRR (Art. 44 quindecies A)</span>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span> (Sauf si ZFRR+). Le régime Micro est exclu pour la ZFRR classique.</li>
                <li><b>Effectif :</b> Moins de 11 salariés (à la date de clôture ou création).</li>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale ou libérale.</li>
                <li><b>Exclusions :</b> Activités bancaires, financières, immobilières, gestion de patrimoine.</li>
                <li><b>Capital :</b> Détenu à moins de 50% par d'autres sociétés.</li>
                <li><b>Localisation :</b> Siège social + moyens d'exploitation <u>exclusivement</u> dans la zone.</li>
            </ul>
            <div class="expert-note">
                💡 <b>Note Jurisprudence (CE 2-6-2025) :</b><br>
                Le transfert d'une activité préexistante vers une ZRR/ZFRR ouvre droit à l'exonération, même sans renouvellement de clientèle.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- CONDITIONS ZFU (Source: Page 16 du PDF) ---
    elif dispositif == "ZFU":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #e67e22;">
            <span class="checklist-title">📋 Conditions ZFU-TE (Art. 44 octies A)</span>
            <ul>
                <li><b>Date limite :</b> Dispositif valide pour les créations jusqu'au <b>31/12/2025</b>.</li>
                <li><b>Régime Fiscal :</b> <span style="color:green; font-weight:bold;">TOUT RÉGIME</span> (Micro-entreprise acceptée).</li>
                <li><b>Plafond Exonération :</b> 50 000 €/an + 5 000 € par nouveau salarié résidant.</li>
                [cite_start]<li><b>Clause d'embauche :</b> Dès le 2ème salarié, 50% de l'effectif doit résider en ZFU ou QPV[cite: 213].</li>
                <li><b>Effectif :</b> Moins de 50 salariés.</li>
                <li><b>CA / Bilan :</b> Inférieur à 10 M€.</li>
                <li><b>Activité :</b> Exclusion stricte location d'immeubles (habitation ou commercial).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    # --- CONDITIONS AFR (Source: Page 16 du PDF) ---
    elif dispositif == "AFR":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #2980b9;">
            <span class="checklist-title">📋 Conditions ZAFR (Art. 44 sexies)</span>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span>.</li>
                <li><b>Durée :</b> Exonération 100% pendant 24 mois, puis dégressif.</li>
                <li><b>Plafond :</b> Soumis aux règles "de minimis" (300 k€ sur 3 ans).</li>
                <li><b>Forme :</b> Si activité BNC, obligation d'exercice en société soumise à l'IS.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- CONDITIONS BER ---
    elif dispositif == "BER":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #8e44ad;">
            <span class="checklist-title">📋 Conditions BER (Bassin d'Emploi à Redynamiser)</span>
            <ul>
                <li><b>Avantage :</b> Exonération fiscale + Exonération <u>charges sociales patronales</u>.</li>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale.</li>
                <li><b>PME :</b> Effectif < 250 salariés, CA < 50 M€.</li>
                <li><b>Exclusions :</b> Transport, Agriculture, Construction navale.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 4. INTERFACE PRINCIPALE
# ==============================================================================

df = load_data()

st.title("Fiscal-Check HDF")
st.caption("Outil basé sur la documentation technique Walter France / Actis (Sept 2025)")
st.write("---")

if df is not None:
    # --- ZONE DE SAISIE ---
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Tapez Amiens...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), format="DD/MM/YYYY")
        
        type_operation = st.radio("Nature de l'opération", ["Création", "Reprise / Transfert"], horizontal=True)

    # --- LOGIQUE DE DÉTECTION ET AFFICHAGE ---
    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        st.subheader(f"Analyse pour : {row['COMMUNE']}")

        # 1. ANALYSE FRANCE RURALITÉS (FRR / ZRR)
        DATE_FRR = date(2024, 7, 1)
        valeur_frr = str(row['FRR']).strip()
        is_frr_zone = valeur_frr in ['FRR', 'FRR+', 'ZRR maintenue', 'Oui']
        
        if is_frr_zone:
            # Distinction ZFRR vs ZRR selon la date
            label_dispo = "ZFRR (France Ruralités)" if date_crea >= DATE_FRR else "ZRR (Ancien Régime)"
            
            st.success(f"✅ **ÉLIGIBLE {label_dispo}**")
            st.caption(f"Classement base : {valeur_frr} | Application Art. 44 quindecies A")
            afficher_checklist("FRR", type_operation)

        # 2. ANALYSE ZFU
        DATE_FIN_ZFU = date(2025, 12, 31) # Date limite fixée par la loi de finances actuelle
        
        if str(row['NB_ZFU']) not in ['0', 'nan', 'Non', '']:
            if date_crea <= DATE_FIN_ZFU:
                st.warning("⚠️ **COMMUNE ZFU-TE (Territoire Entrepreneur)**")
                st.caption("Attention : Éligibilité conditionnée à l'adresse exacte (Parcelle)")
                afficher_checklist("ZFU", type_operation)
            else:
                st.error(f"❌ Zone ZFU : Dispositif expiré (Date limite : {DATE_FIN_ZFU.strftime('%d/%m/%Y')})")

        # 3. ANALYSE AFR
        if str(row['AFR']) in ['Intégralement', 'Partiellement', 'Oui']:
            st.info("ℹ️ **ZONE AFR (Aide à Finalité Régionale)**")
            afficher_checklist("AFR", type_operation)

        # 4. ANALYSE BER (Si colonne présente)
        if 'BER' in row and str(row['BER']) == 'Oui':
            st.success("✅ **ÉLIGIBLE BER (Bassin d'Emploi)**")
            afficher_checklist("BER", type_operation)

        # 5. CAS NÉGATIF
        if not is_frr_zone and str(row['NB_ZFU']) in ['0', 'nan', 'Non', ''] and str(row['AFR']) not in ['Intégralement', 'Partiellement', 'Oui'] and str(row.get('BER', 'Non')) != 'Oui':
             st.info("Aucun dispositif ZRR/FRR/ZFU/AFR/BER détecté pour cette commune.")

else:

    st.error("Erreur chargement Google Sheet. Vérifiez l'ID.")
