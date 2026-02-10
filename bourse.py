import streamlit as st
import pandas as pd
import io
import requests

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Investissement",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Tableau de Bord : Aide à la Décision Boursière")
st.markdown("Ce tableau de bord analyse les indicateurs macroéconomiques en temps réel pour orienter la stratégie d'investissement.")
st.markdown("---")

# ==============================================================================
# 1. CONNEXION ET CHARGEMENT (CACHE POUR LA RAPIDITÉ)
# ==============================================================================
@st.cache_data(ttl=60) # Actualise les données toutes les 60 secondes
def charger_donnees():
    SHEET_ID = '149LRG1G-b6fckX7i8dj-4aRsJaTmOHOQojVj0zdlMOg'
    SHEET_GID = '1883446598'
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
    
    try:
        s = requests.get(url).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')))
        
        # Nettoyage
        df.columns = df.columns.str.strip()
        # Gestion des virgules françaises
        df['Valeur'] = df['Valeur'].astype(str).str.replace(',', '.').apply(pd.to_numeric, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return pd.DataFrame()

# Chargement
df = charger_donnees()

if not df.empty:
    # ==============================================================================
    # 2. AFFICHAGE DES INDICATEURS (KPIs)
    # ==============================================================================
    st.subheader("📊 Indicateurs Clés")
    
    # Création de 4 colonnes pour l'affichage
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    score = 0
    details = []

    for index, row in df.iterrows():
        nom = str(row['Indicateur'])
        valeur = row['Valeur']
        
        if pd.isna(valeur): continue

        point = 0
        delta_color = "off"
        
        # --- LOGIQUE MÉTIER ---
        if 'PIB' in nom:
            if valeur >= 3.0: 
                point = 1
                kpi1.metric(label="Croissance (PIB)", value=f"{valeur}%", delta="Solide", delta_color="normal")
            else: 
                point = -1
                kpi1.metric(label="Croissance (PIB)", value=f"{valeur}%", delta="Faible", delta_color="inverse")
            
        elif 'Inflation' in nom:
            if -1 <= valeur <= 3: 
                point = 1
                kpi2.metric(label="Inflation", value=f"{valeur}%", delta="Maîtrisée", delta_color="normal") # Inverse car baisse = bon
            else: 
                point = -1
                kpi2.metric(label="Inflation", value=f"{valeur}%", delta="Risque", delta_color="inverse")
            
        elif 'Intérêt' in nom or 'Directeur' in nom:
            if valeur <= 3.0: 
                point = 1
                kpi3.metric(label="Taux Directeur", value=f"{valeur}%", delta="Favorable", delta_color="inverse")
            else: 
                point = 0
                kpi3.metric(label="Taux Directeur", value=f"{valeur}%", delta="Restrictif", delta_color="off")

        elif 'Chômage' in nom:
            if valeur > 12: 
                point = -1
                kpi4.metric(label="Chômage", value=f"{valeur}%", delta="Élevé", delta_color="inverse")
            else: 
                point = 0
                kpi4.metric(label="Chômage", value=f"{valeur}%", delta="Stable", delta_color="normal")

        score += point

    st.markdown("---")

    # ==============================================================================
    # 3. DÉCISION ALGORITHMIQUE
    # ==============================================================================
    
    col_gauche, col_droite = st.columns([2, 1])

    with col_gauche:
        st.subheader("🔎 Analyse Détaillée")
        st.dataframe(df, use_container_width=True)

    with col_droite:
        st.subheader("🎯 Recommandation IA")
        
        if score >= 2:
            st.success("## ACHETER (BULLISH)")
            st.write("Le contexte macroéconomique est très favorable aux actions.")
        elif score < 0:
            st.error("## VENDRE (BEARISH)")
            st.write("Les risques (Inflation/Chômage) pèsent sur la rentabilité.")
        else:
            st.warning("## CONSERVER (NEUTRE)")
            st.write("Marché incertain. Privilégier le 'Stock Picking'.")
        
        st.metric(label="Score Algorithmique", value=f"{score} / 4")

else:
    st.warning("En attente des données...")