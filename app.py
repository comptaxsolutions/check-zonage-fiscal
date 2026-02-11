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
    
    /* Style des Fiches Techniques */
    .checklist-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 8px;
        border-left: 6px solid #2c3e50;
        font-size: 0.95em;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .checklist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 2px solid #f1f3f5;
        padding-bottom: 10px;
    }
    .checklist-title {
        font-weight: 800;
        color: #2c3e50;
        font-size: 1.2em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-scope {
        background-color: #2c3e50;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75em;
        font-weight: bold;
        text-transform: uppercase;
    }
    .benefits-section {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-weight: 600;
        border: 1px solid #c8e6c9;
    }
    .warning-section {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 0.9em;
        border: 1px solid #ffeeba;
    }
    h4 {
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 1em;
        color: #555;
        text-decoration: underline;
    }
    ul { margin-bottom: 0; padding-left: 20px; }
    li { margin-bottom: 6px; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    # 👇👇👇 ID GOOGLE SHEET MIS À JOUR 👇👇👇
    sheet_id = "1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I"
    
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url, dtype=str)
        # Création de la colonne recherche intelligente
        if 'CP' in df.columns:
            df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
        else:
            df['Label_Recherche'] = df['COMMUNE'] + " (Insee: " + df['CODE'] + ")"
        return df
    except Exception as e:
        return None

# ==============================================================================
# 3. FONCTIONS D'AFFICHAGE (Fiches Exhaustives)
# ==============================================================================

def afficher_details_regime(type_regime):
    """Affiche les détails COMPLETS selon le régime (Source: Walter France/Actis)"""
    
    # [cite_start]--- ZFRR PLUS (RENFORCÉE) [cite: 205, 212] ---
    if type_regime == "ZFRR_PLUS":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #27ae60;">
            <div class="checklist-header">
                <span class="checklist-title">ZFRR+ (Renforcée)</span>
                <span class="badge-scope">Création • Reprise • Extension</span>
            </div>
            <div class="benefits-section">
                💶 FISCAL : Exonération 100% (5 ans) puis 75%, 50%, 25%.<br>
                👥 SOCIAL : Exonération charges patronales (sous conditions).
            </div>
            
            <h4>1. Conditions liées à l'entreprise</h4>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:green; font-weight:bold;">TOUT RÉGIME AUTORISÉ</span> (Réel OU Micro-entreprise).</li>
                <li><b>Effectif :</b> Moins de 11 salariés (à la création ou reprise).</li>
                <li><b>Capital :</b> Détenu à moins de 50% par d'autres sociétés.</li>
            </ul>

            <h4>2. Conditions d'activité</h4>
            <ul>
                <li><b>Nature :</b> Industrielle, commerciale, artisanale ou libérale.</li>
                <li><b>Localisation :</b> Siège social ET moyens d'exploitation <u>exclusivement</u> dans la zone.</li>
                <li><b>Exclusions :</b> Activités bancaires, financières, immobilières, gestion de patrimoine.</li>
            </ul>
             <div class="warning-section">
                📅 <b>Validité :</b> Opérations réalisées entre le 01/01/2025 et le 31/12/2029.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # [cite_start]--- ZFRR CLASSIQUE [cite: 205, 212] ---
    elif type_regime == "ZFRR_CLASSIC":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #2ecc71;">
            <div class="checklist-header">
                <span class="checklist-title">ZFRR (Classique)</span>
                <span class="badge-scope">Création • Reprise</span>
            </div>
            <div class="benefits-section">
                💶 FISCAL : Exonération 100% (5 ans) puis 75%, 50%, 25%.<br>
                👥 SOCIAL : Exonération charges patronales (sous conditions).
            </div>

            <h4>1. Conditions liées à l'entreprise</h4>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span> (Micro-entreprise EXCLUE).</li>
                <li><b>Effectif :</b> Moins de 11 salariés.</li>
                <li><b>Capital :</b> Détenu à moins de 50% par d'autres sociétés.</li>
            </ul>

            <h4>2. Conditions d'activité</h4>
            <ul>
                <li><b>Nature :</b> Industrielle, commerciale, artisanale ou libérale.</li>
                <li><b>Localisation :</b> Siège social ET moyens d'exploitation <u>exclusivement</u> dans la zone.</li>
                <li><b>Transfert :</b> Éligible même sans renouvellement de clientèle (Jurisprudence CE 2025).</li>
            </ul>
             <div class="warning-section">
                📅 <b>Validité :</b> Opérations réalisées à partir du 01/07/2024.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # [cite_start]--- ZFU (TERRITOIRE ENTREPRENEUR) [cite: 205, 212] ---
    elif type_regime == "ZFU":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #e67e22;">
            <div class="checklist-header">
                <span class="checklist-title">ZFU-TE (Territoire Entrepreneur)</span>
                <span class="badge-scope">Création Uniquement</span>
            </div>
            <div class="benefits-section">
                💶 FISCAL : Exonération 100% (5 ans) puis dégressif (60, 40, 20%).<br>
                🚧 <b>Plafond :</b> 50 000 €/an + 5 000 € par nouveau salarié résidant.
            </div>

            <h4>1. Conditions liées à l'entreprise</h4>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:green; font-weight:bold;">TOUT RÉGIME</span> (Micro accepté).</li>
                <li><b>Taille :</b> Moins de 50 salariés et CA < 10 M€.</li>
                <li><b>Clause d'embauche (Crucial) :</b> Dès le 2ème salarié, 50% de l'effectif doit résider en ZFU ou QPV.</li>
            </ul>

            <h4>2. Conditions d'activité</h4>
            <ul>
                <li><b>Nature :</b> Industrielle, commerciale, artisanale, BNC.</li>
                <li><b>Exclusions :</b> Location d'immeubles (habitation ou commercial), crédit-bail mobilier.</li>
                <li><b>Localisation :</b> Activité matérielle et effective DANS le périmètre (bureau/atelier/stock).</li>
            </ul>
            <div class="warning-section">
                ⚠️ <b>Exclusion :</b> Les transferts, concentrations ou restructurations d'activités préexistantes sont exclus.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # [cite_start]--- ZAFR (AIDE À FINALITÉ RÉGIONALE) - CORRIGÉ [cite: 205, 212] ---
    elif type_regime == "AFR":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #2980b9;">
            <div class="checklist-header">
                <span class="checklist-title">ZAFR (Aide Finalité Régionale)</span>
                <span class="badge-scope">Création (PME) • Reprise (< 11 sal.)</span>
            </div>
            <div class="benefits-section">
                💶 FISCAL : Exonération 100% (24 mois) puis 75%, 50%, 25%.<br>
                🚧 <b>Plafond :</b> Règle "de minimis" (300 000 € sur 3 ans glissants).
            </div>

            <h4>1. Conditions strictes d'éligibilité</h4>
            <ul>
                <li><b>Régime Fiscal :</b> <span style="color:red; font-weight:bold;">RÉEL OBLIGATOIRE</span>.</li>
                <li><b>Forme Juridique (Spécial BNC) :</b> Les activités BNC ne sont éligibles que si exercées en <u>Société soumise à l'IS</u> (et min. 3 salariés).</li>
                <li><b>Taille :</b> PME au sens communautaire (< 250 sal, CA < 50M€).</li>
            </ul>

            <h4>2. Conditions de localisation (Art. 44 sexies)</h4>
            <ul>
                <li><b>Activité Sédentaire :</b> Prorata du CA réalisé dans la zone.</li>
                <li><b>Activité Non Sédentaire :</b> Éligible si < 25% du CA est réalisé hors zone.</li>
                <li><b>Exclusions :</b> Activités financières, assurances, gestion locative.</li>
            </ul>
             <div class="warning-section">
                📅 <b>Validité :</b> Créations jusqu'au 31/12/2027.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- BER ---
    elif type_regime == "BER":
        st.markdown(f"""
        <div class="checklist-box" style="border-left-color: #8e44ad;">
            <div class="checklist-header">
                <span class="checklist-title">BER (Bassin d'Emploi)</span>
                <span class="badge-scope">Création • Reprise</span>
            </div>
            <div class="benefits-section">
                🚀 <b>DOUBLE AVANTAGE :</b> Exonération FISCALE totale + Exonération SOCIALE patronale.
            </div>

            <h4>Conditions principales</h4>
            <ul>
                <li><b>Activité :</b> Industrielle, commerciale, artisanale.</li>
                <li><b>Exclusions :</b> Agriculture, transport, construction navale.</li>
                <li><b>Taille :</b> PME (< 250 salariés, CA < 50 M€).</li>
                <li><b>Régime :</b> Entreprise non en difficulté.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 4. INTERFACE PRINCIPALE
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
        
    # --- LOGIQUE DE DÉTECTION ---
    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        st.subheader(f"Analyse pour : {row['COMMUNE']}")

        # 1. ANALYSE FRANCE RURALITÉS (ZFRR+ vs ZFRR)
        DATE_FRR = date(2024, 7, 1)
        valeur_frr = str(row['FRR']).strip().upper()
        
        if valeur_frr in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_FRR:
                # DISTINCTION ZFRR+ (MICRO OK) / ZFRR CLASSIQUE (REEL ONLY)
                if "FRR+" in valeur_frr or "+" in valeur_frr:
                    st.success("✅ **ÉLIGIBLE ZFRR+ (Renforcée)**")
                    afficher_details_regime("ZFRR_PLUS")
                else:
                    st.success("✅ **ÉLIGIBLE ZFRR (Classique)**")
                    afficher_details_regime("ZFRR_CLASSIC")
            else:
                st.success("✅ **ÉLIGIBLE ZRR (Ancien Régime)**")
                afficher_details_regime("ZFRR_CLASSIC")

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
            st.info("ℹ️ **ZONE ZAFR (Aide Finalité Régionale)**")
            afficher_details_regime("AFR")

        # 4. ANALYSE BER
        if 'BER' in row and str(row['BER']) == 'Oui':
            st.success("✅ **ÉLIGIBLE BER**")
            afficher_details_regime("BER")

        # 5. CAS NÉGATIF
        if valeur_frr not in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI'] and str(row['NB_ZFU']) in ['0', 'nan', 'Non', ''] and str(row['AFR']) not in ['Intégralement', 'Partiellement', 'Oui'] and str(row.get('BER', 'Non')) != 'Oui':
             st.markdown("""
             <div style="padding:15px; background-color:#f8d7da; color:#721c24; border-radius:5px;">
             <b>Aucun dispositif fiscal majeur détecté</b> (ZRR, FRR, ZFU, AFR, BER) pour cette commune.
             </div>
             """, unsafe_allow_html=True)

else:
    st.error("Erreur de connexion au fichier Google Sheet. Vérifiez l'ID.")
