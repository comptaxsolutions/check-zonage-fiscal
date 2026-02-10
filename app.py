import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (Le Look "Cabinet d'Avocats")
# ==============================================================================
st.set_page_config(
    page_title="Fiscal-Check | Hauts-de-France",
    page_icon="⚖️",
    layout="centered"
)

# CSS Custom pour cacher les éléments Streamlit et styliser l'app
st.markdown("""
    <style>
    /* Cacher le menu hamburger et le footer Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Styliser les titres */
    h1 {
        font-family: 'Helvetica', sans-serif;
        color: #2c3e50;
        text-align: center;
        border-bottom: 2px solid #e74c3c;
        padding-bottom: 15px;
        margin-bottom: 30px;
    }
    
    /* Styliser les métriques (les gros chiffres) */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        color: #2980b9;
    }
    
    /* Styliser les cadres de résultats */
    .result-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid;
        background-color: #f8f9fa;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES (Connexion Google Sheet)
# ==============================================================================
@st.cache_data(ttl=600)  # Mise en cache 10 min pour la rapidité
def load_data():
    # 👇👇👇 REMPLACE L'ID CI-DESSOUS PAR LE TIEN 👇👇👇
    sheet_id = "TON_ID_GOOGLE_SHEET_ICI" 
    
    url = f"https://docs.google.com/spreadsheets/d/1XwJM0unxho3qPpxRohA_w8Ou9-gP8bHqguPQeD0aI2I/export?format=csv"
    
    try:
        # On force tout en texte (dtype=str) pour éviter que les codes postaux perdent le zéro (ex: 02100 -> 2100)
        df = pd.read_csv(url, dtype=str)
        
        # NETTOYAGE & SÉCURITÉ
        # On s'assure que les colonnes existent, sinon on les crée vides pour ne pas planter
        required_cols = ['CODE', 'COMMUNE', 'FRR', 'NB_ZFU', 'AFR']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"⚠️ Colonne manquante dans le Google Sheet : {col}")
                return None

        # CRÉATION DE LA COLONNE DE RECHERCHE INTELLIGENTE
        # Si la colonne 'CP' existe, on l'utilise, sinon on utilise le Code Insee ('CODE')
        if 'CP' in df.columns:
            df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
        else:
            df['Label_Recherche'] = df['COMMUNE'] + " (Insee: " + df['CODE'] + ")"
            
        return df
        
    except Exception as e:
        st.error(f"Erreur technique lors du chargement : {e}")
        return None

# ==============================================================================
# 3. MOTEUR D'ANALYSE FISCALE (Le Cerveau)
# ==============================================================================
def analyser_eligibilite(row, date_creation):
    resultats = []
    
    # --- DATES PIVOTS ---
    DATE_BASCULE_FRR = date(2024, 7, 1)
    DATE_FIN_ZFU = date(2024, 12, 31) # Date théorique fin ZFU

    # --- A. ZONE RURALE (FRR / ZRR) ---
    valeur_frr = str(row['FRR']).strip()
    is_frr_listed = valeur_frr in ['FRR', 'FRR+', 'ZRR maintenue', 'Oui']
    
    if date_creation >= DATE_BASCULE_FRR:
        # Nouveau Régime FRR
        if is_frr_listed:
            resultats.append({
                "titre": "Zone France Ruralités (FRR)",
                "statut": "✅ ÉLIGIBLE",
                "color": "#27ae60", # Vert
                "desc": f"Classement commune : {valeur_frr}. Exonération IS/IR totale (5 ans) puis dégressive."
            })
    else:
        # Ancien Régime ZRR
        if is_frr_listed: # On présume que FRR auj = ZRR hier pour le MVP
            resultats.append({
                "titre": "Zone ZRR (Ancien Régime)",
                "statut": "✅ ÉLIGIBLE",
                "color": "#27ae60",
                "desc": "Création avant le 01/07/2024. Régime ZRR maintenu (Art 44 quindecies)."
            })

    # --- B. ZONE URBAINE (ZFU) ---
    nb_zfu = str(row['NB_ZFU'])
    if nb_zfu not in ['0', 'nan', 'Non', '']:
        if date_creation <= DATE_FIN_ZFU:
            resultats.append({
                "titre": "Zone Franche Urbaine (ZFU-TE)",
                "statut": "⚠️ VÉRIFICATION REQUISE",
                "color": "#f39c12", # Orange
                "desc": "La commune contient une ZFU. L'éligibilité dépend de l'adresse exacte (à la parcelle)."
            })
        else:
            resultats.append({
                "titre": "Zone Franche Urbaine (ZFU-TE)",
                "statut": "❌ DISPOSITIF EXPIRÉ",
                "color": "#c0392b", # Rouge
                "desc": f"Dispositif théoriquement clos au {DATE_FIN_ZFU.strftime('%d/%m/%Y')}."
            })

    # --- C. AIDE RÉGIONALE (AFR) ---
    valeur_afr = str(row['AFR'])
    if valeur_afr in ['Intégralement', 'Partiellement', 'Oui']:
        resultats.append({
            "titre": "Zone AFR",
            "statut": "✅ ÉLIGIBLE",
            "color": "#2980b9", # Bleu
            "desc": "Éligible aux aides à l'investissement et exonérations locales (CFE/CVAE)."
        })

    # --- D. BASSIN EMPLOI (BER) - Si la colonne existe ---
    if 'BER' in row and str(row['BER']) == 'Oui':
        resultats.append({
            "titre": "Zone BER",
            "statut": "✅ ÉLIGIBLE (Exonérations Renforcées)",
            "color": "#8e44ad", # Violet
            "desc": "Bassin d'Emploi à Redynamiser. Exonérations fiscales ET sociales massives."
        })

    return resultats

# ==============================================================================
# 4. INTERFACE UTILISATEUR (Le Frontend)
# ==============================================================================

# Chargement
df = load_data()

# Titre Principal
st.title("Fiscal-Check HDF")
st.markdown("<div style='text-align: center; color: grey; margin-top: -20px;'>Outil d'aide à la décision - Zonages Fiscaux</div>", unsafe_allow_html=True)
st.write("---")

if df is not None:
    # --- FORMULAIRE DE SAISIE ---
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélecteur Intelligent avec Recherche
            choix_commune = st.selectbox(
                "📍 Rechercher une commune (Nom ou Code)",
                df['Label_Recherche'],
                index=None,
                placeholder="Tapez Amiens, 80000..."
            )
            
        with col2:
            date_crea = st.date_input("📅 Date de création / reprise", date.today())

        # Bouton d'action large
        btn_calcul = st.button("Lancer l'Audit d'Éligibilité", type="primary", use_container_width=True)

    # --- AFFICHAGE RÉSULTATS ---
    if btn_calcul:
        if choix_commune is None:
            st.warning("Veuillez sélectionner une commune.")
        else:
            # On récupère la ligne de données correspondante
            # On cherche la ligne où 'Label_Recherche' correspond exactement au choix
            row_data = df[df['Label_Recherche'] == choix_commune].iloc[0]
            
            # Calcul
            analyses = analyser_eligibilite(row_data, date_crea)
            
            st.divider()
            st.subheader(f"Résultats pour {row_data['COMMUNE']}")
            
            # Métriques de synthèse
            m1, m2, m3 = st.columns(3)
            m1.metric("Département", row_data['CODE'][:2]) # Les 2 premiers chiffres du code Insee
            m2.metric("Dispositifs détectés", len(analyses))
            m3.metric("Date retenue", date_crea.strftime("%d/%m/%Y"))
            
            st.write("") # Espace

            if not analyses:
                st.info("ℹ️ Aucun zonage fiscal incitatif majeur identifié pour cette commune à cette date.")
            else:
                for a in analyses:
                    # Affichage HTML des cartes de résultat
                    st.markdown(f"""
                    <div class="result-card" style="border-left-color: {a['color']};">
                        <h4 style="color: {a['color']}; margin:0;">{a['statut']}</h4>
                        <strong style="font-size: 1.1em; color: #333;">{a['titre']}</strong>
                        <p style="margin-top: 5px; color: #555; font-size: 0.95em;">{a['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Petit disclaimer légal automatique
                st.caption("⚠️ Cet outil est fourni à titre indicatif. Il ne remplace pas une consultation formelle des textes (BOFiP).")

else:
    st.info("Veuillez configurer l'ID du Google Sheet dans le code pour démarrer.")