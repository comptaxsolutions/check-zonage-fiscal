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
                <span class="badge-scope">Cré
