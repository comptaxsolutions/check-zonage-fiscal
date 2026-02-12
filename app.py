import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURATION & DESIGN (CSS "OVERLAY" POUR IMPRESSION)
# ==============================================================================
st.set_page_config(
    page_title="Audit Zonage Fiscal",
    page_icon="🦁",
    layout="wide"
)

st.markdown("""
    <style>
    /* --- 1. DESIGN ÉCRAN (Joli et Moderne) --- */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .main-title { font-size: 2em; color: #2c3e50; text-align: center; margin-bottom: 5px; font-weight: bold; }
    .sub-title { font-size: 1.1em; color: #555; text-align: center; margin-bottom: 20px; }

    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 0.9em;
        background-color: white;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    
    th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        text-transform: uppercase;
        border: 1px solid #34495e;
        width: 18%;
    }
    
    td {
        padding: 10px;
        border: 1px solid #ddd;
        vertical-align: top;
        color: #333;
        line-height: 1.4;
    }

    /* Colonne des titres à gauche */
    td:first-child {
        background-color: #f8f9fa;
        font-weight: 700;
        color: #2c3e50;
        width: 15%;
    }
    
    /* Ligne ZONE / CLASSEMENT (Vert) */
    .zone-row td {
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
        font-weight: bold;
        text-align: center;
        font-size: 1.1em;
        border-bottom: 2px solid #2e7d32;
    }

    /* Boutons Liens */
    .btn-legifrance {
        background-color: #fce4ec;
        color: #c2185b;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #f8bbd0;
        font-size: 0.85em;
        white-space: nowrap;
    }

    /* --- 2. DESIGN IMPRESSION (La méthode Radicale) --- */
    @media print {
        /* Cacher TOUT le corps de la page par défaut */
        body * {
            visibility: hidden;
        }

        /* Isoler la zone imprimable et la rendre visible */
        #printable-area, #printable-area * {
            visibility: visible;
        }

        /* Positionner la zone imprimable par-dessus tout le reste */
        #printable-area {
            position: fixed;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 20px;
            background-color: white; /* Fond blanc forcé */
            z-index: 9999; /* Au-dessus de tout */
        }
        
        /* Force Paysage */
        @page {
            size: A4 landscape;
            margin: 1cm;
        }

        /* Ajustements du tableau pour l'impression */
        table {
            width: 100% !important;
            font-size: 9pt !important; /* Réduire un peu la police */
            border: 2px solid #000;
        }
        
        th {
            background-color: #2c3e50 !important;
            color: white !important;
            -webkit-print-color-adjust: exact; /* Force la couleur de fond */
            print-color-adjust: exact;
        }
        
        /* Les liens deviennent du texte noir souligné */
        .btn-legifrance {
            border: none;
            background: none !important;
            color: black !important;
            text-decoration: underline;
            padding: 0;
        }
        
        /* Cacher les éléments "no-print" */
        .no-print {
            display: none !important;
        }
    }
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
        df_raw = pd.read_csv(url, header=None, dtype=str)
        header_row_idx = None
        for i, row in df_raw.iterrows():
            row_str = " ".join(row.fillna("").astype(str).values)
            if "Libellé" in row_str and "Code" in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            df = pd.read_csv(url, dtype=str)
        else:
            df = pd.read_csv(url, header=header_row_idx, dtype=str)

        df.columns = [c.strip() for c in df.columns]
        rename_map = {}
        existing_cols = df.columns.tolist()
        def has_col(target): return target in existing_cols

        for col in existing_cols:
            c = col.lower()
            if ("libellé" in c or "commune" in c) and not has_col("COMMUNE"): rename_map[col] = "COMMUNE"
            elif ("code" in c and "insee" not in c) and not has_col("CODE"): rename_map[col] = "CODE"
            elif "nb_zfu" in c: rename_map[col] = "NB_ZFU"
            elif "zfu" in c and not has_col("NB_ZFU") and "NB_ZFU" not in rename_map.values(): rename_map[col] = "NB_ZFU"
            elif "nb_qpv" in c: rename_map[col] = "NB_QPV"
            elif ("quartier" in c or "qpv" in c or "qppv" in c) and not has_col("NB_QPV") and "NB_QPV" not in rename_map.values(): rename_map[col] = "NB_QPV"
            elif ("frr" in c or "ruralités" in c) and not has_col("FRR"): rename_map[col] = "FRR"
            elif "afr" in c and not has_col("AFR"): rename_map[col] = "AFR"
            elif "ber" in c and not has_col("BER"): rename_map[col] = "BER"

        df = df.rename(columns=rename_map)
        if 'COMMUNE' in df.columns and 'CODE' in df.columns:
            if 'CP' in df.columns:
                df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CP'] + ")"
            else:
                df['Label_Recherche'] = df['COMMUNE'] + " (" + df['CODE'] + ")"
            return df
        else:
            return None
    except Exception as e:
        return None

# ==============================================================================
# 3. MATRICE DE DONNÉES (VALIDÉE 2030)
# ==============================================================================
DATA_MATRIX = {
    "ZFU": {
        "Nom": "ZFU-TE",
        "References_legales": "CGI art. 44 octies A",
        "Periode": "Créations jusqu'au <b>31/12/2030</b><br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "100 % 5 ans, puis 60 % (6e), 40 % (7e), 20 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale (totale puis progressive)",
        "Social": "Exonération spécifique (L.131-4-2)", 
        "Nature_activite": "Industrielles, commerciales, artisanales, BNC.<br><i>Exclusions : crédit-bail mobilier, location logements + certaines activités particulières</i>",
        "Regime_fiscal": "Tout régime (micro ou réel)",
        "Taille": "< 50 salariés, CA ≤ 10 M€. Capital < 25 % par grandes ent.",
        "Implantation": "Implantation matérielle et activité effective (locaux, clientèle, production) en ZFU. Possible non sédentarité sous conditions.",
        "Condition_sociale": "Obligation emploi % salariés résidant en ZFU ou QPV à compter du 2ème salarié",
        "Exclusions_abus": "Non éligible si transfert/restructuration simple, ou changement de forme sans nouveauté.",
        "Plafonds_UE": "Plafond spécifique (50 k€/an + 5k€/emploi).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/LEGIARTI000026939165/"
    },
    
    "AFR": {
        "Nom": "ZAFR (Zones AFR)",
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
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046003627/"
    },

    "ZFRR_CLASSIC": {
        "Nom": "ZFRR (Classique)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "01/07/2024 – 31/12/2029",
        "Duree_exo": "100 % 5 ans, puis 75 % (6e), 50 % (7e), 25 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Industrielles, commerciales, artisanales, libérales.<br><i>Exclusion activités particulières</i>",
        "Regime_fiscal": "Régime réel obligatoire",
        "Taille": "< 11 salariés.<br><i>Pas de condition liée au capital mais demandé dans le modèle de rescrit</i>",
        "Implantation": "Siège + moyens exclusivement en zone. Activité non sédentaire : CA hors zone ≤ 25 %.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Non éligible si activité déjà exonérée dans les 5 ans (ZFU, ZAFR, BER…), ou reprise intra-familiale (sauf 1ère reprise par descendant).",
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000049746820/"
    },
    
    "ZFRR_PLUS": {
        "Nom": "ZFRR+ (Renforcée)",
        "References_legales": "CGI art. 44 quindecies A",
        "Periode": "01/01/2025 – 31/12/2029 + admet extensions d'établissement",
        "Duree_exo": "100 % 5 ans, puis 75 % (6e), 50 % (7e), 25 % (8e).",
        "Impots_locaux": "Possible exonération sur délibération locale",
        "Social": "Oui (cotisations patronales)",
        "Nature_activite": "Industrielles, commerciales, artisanales, libérales.<br><i>Exclusion activités particulières</i>",
        "Regime_fiscal": "réel ou micro",
        "Taille": "Création : PME UE (moins de 250 salariés, CA ≤ 50 M€, bilan ≤ 43 M€). Reprise : < 11 salariés.",
        "Implantation": "Pas d'exclusivité. Sédentaire : prorata de CA en zone. Non sédentaire : règle des 25 % + prorata si locaux en/hors zone.",
        "Condition_sociale": "cf taille entreprise",
        "Exclusions_abus": "Non éligible si activité déjà exonérée dans les 5 ans (ZFU, ZAFR, BER…), ou reprise intra-familiale (sauf 1ère reprise par descendant).",
        "Plafonds_UE": "Soumis aux plafonds 'de minimis' (300 k€ sur 3 ans).",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000051871914/"
    },

    "QPV": {
        "Nom": "QPPV",
        "References_legales": "Décret n° 2023-1314",
        "Periode": "Créations jusqu'au <b>31/12/2030</b><br><i>(en attente promulgation LF2026)</i>",
        "Duree_exo": "N/C",
        "Impots_locaux": "exonération TFPB 5 ans sauf délibération contraire collectivité",
        "Social": "nan",
        "Nature_activite": "N/C",
        "Regime_fiscal": "N/C",
        "Taille": "N/C",
        "Implantation": "N/C",
        "Condition_sociale": "N/C",
        "Exclusions_abus": "N/C",
        "Plafonds_UE": "N/C",
        "Legifrance_Base": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000048707389/"
    }
}

# ==============================================================================
# 4. GÉNÉRATEUR HTML DU TABLEAU
# ==============================================================================
def get_zone_display(regime_key, row_data):
    raw_val = ""
    if regime_key == "ZFU": raw_val = str(row_data.get('NB_ZFU', '')).strip()
    elif regime_key == "QPV": raw_val = str(row_data.get('NB_QPV', '')).strip()
    elif regime_key == "AFR": raw_val = str(row_data.get('AFR', '')).strip()
    elif "ZFRR" in regime_key: raw_val = str(row_data.get('FRR', '')).strip()

    if raw_val.lower() in ['nan', '0', '', 'non']: return "-"
    if raw_val.lower() == "oui": return "Intégralement"
    elif "partiel" in raw_val.lower(): return "Partiellement"
    elif "maintenue" in raw_val.lower(): return "ZRR maintenue"
    else: return raw_val

def render_html_table(regimes, row_data, date_op):
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

    # CONTENEUR SPECIAL POUR L'IMPRESSION (ID=printable-area)
    html = f"""
    <div id='printable-area'>
        <div class='main-title'>Audit Zonage Fiscal</div>
        <div class='sub-title'>
            Commune : <b>{row_data['COMMUNE']}</b> (Code: {row_data['CODE']}) | 
            Date opération : {date_op.strftime('%d/%m/%Y')}
        </div>
        <table>
            <thead><tr><th>Critères</th>
    """
    
    for r in regimes:
        html += f"<th>{DATA_MATRIX[r]['Nom']}</th>"
    html += "</tr></thead><tbody>"
    
    # LIGNE ZONE
    html += "<tr class='zone-row'><td>ZONE / CLASSEMENT</td>"
    for r in regimes:
        html += f"<td>{get_zone_display(r, row_data)}</td>"
    html += "</tr>"
    
    # LIGNE LIENS
    date_formatted = date_op.strftime("%Y-%m-%d")
    html += "<tr><td>VÉRIFICATION SOURCE</td>"
    for r in regimes:
        base_url = DATA_MATRIX[r].get("Legifrance_Base")
        if base_url:
            full_link = f"{base_url}{date_formatted}"
            html += f'<td><a href="{full_link}" target="_blank" class="btn-legifrance">Texte à date 🔗</a></td>'
        else:
            html += "<td>-</td>"
    html += "</tr>"

    # CORPS DU TABLEAU
    for label, key in rows_config:
        html += f"<tr><td>{label}</td>"
        for r in regimes:
            val = DATA_MATRIX[r].get(key, "-")
            if val == "nan" or pd.isna(val): val = ""
            html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html

# ==============================================================================
# 5. MOTEUR D'ANALYSE
# ==============================================================================
df = load_data()

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Audit Zonage Fiscal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Outil d'aide à la décision (Hauts-de-France)</p>", unsafe_allow_html=True)
st.write("---")

if df is not None:
    # Conteneur pour inputs (sera caché à l'impression)
    with st.container():
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            choix_commune = st.selectbox("📍 Commune", df['Label_Recherche'], index=None, placeholder="Rechercher...")
        with c2:
            date_crea = st.date_input("📅 Date de l'opération", date.today(), format="DD/MM/YYYY")
        st.markdown('</div>', unsafe_allow_html=True)

    if choix_commune:
        row = df[df['Label_Recherche'] == choix_commune].iloc[0]
        st.divider()
        
        detected = []
        
        # 1. ZFRR
        frr_val = str(row.get('FRR', '')).strip().upper()
        DATE_ZFRR_PLUS = date(2025, 1, 1)
        DATE_ZFRR_CLASSIC = date(2024, 7, 1)
        if frr_val in ['FRR', 'FRR+', 'ZRR MAINTENUE', 'OUI']:
            if date_crea >= DATE_ZFRR_PLUS and ("+" in frr_val or "FRR+" in frr_val):
                detected.append("ZFRR_PLUS")
            elif date_crea >= DATE_ZFRR_CLASSIC:
                detected.append("ZFRR_CLASSIC")
            else:
                detected.append("ZFRR_CLASSIC")

        # 2. ZFU (2030)
        nb_zfu = str(row.get('NB_ZFU', '0')).strip()
        is_zfu = False
        if nb_zfu not in ['0', 'nan', 'NON', '', 'Non']: is_zfu = True
        if is_zfu and date_crea <= date(2030, 12, 31):
            detected.append("ZFU")

        # 3. AFR
        afr_val = str(row.get('AFR', '')).strip().capitalize()
        if afr_val in ['Integralement', 'Partiellement', 'Oui', 'Intégralement']:
             if date_crea <= date(2027, 12, 31):
                detected.append("AFR")
        
        # 4. QPV (2030)
        nb_qpv = str(row.get('NB_QPV', '0')).strip()
        is_qpv = False
        if nb_qpv not in ['0', 'nan', 'NON', '', 'Non']: is_qpv = True
        if is_qpv and date_crea <= date(2030, 12, 31):
            detected.append("QPV")

        # AFFICHAGE
        if detected:
            detected = list(dict.fromkeys(detected))
            
            st.success(f"✅ {len(detected)} dispositif(s) identifié(s)")
            
            # Injection du HTML
            st.markdown(render_html_table(detected, row, date_crea), unsafe_allow_html=True)
            
            st.markdown("""
            <div class='print-instruction no-print'>
                💡 <b>POUR IMPRIMER (A4 Paysage) :</b><br>
                Appuyez sur <b>Ctrl+P</b>. Assurez-vous de cocher <b>"Graphiques d'arrière-plan"</b> dans les paramètres d'impression.
                La page se nettoiera automatiquement.
            </div>
            """, unsafe_allow_html=True)
            
            if "ZFU" in detected or "QPV" in detected:
                st.warning("⚠️ **Vigilance (ZFU / QPV)** : Éligibilité conditionnée à l'adresse exacte.")
        else:
            st.warning("Aucun dispositif zoné majeur détecté.")

else:
    st.error("Erreur chargement Google Sheet.")
