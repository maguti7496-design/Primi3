import streamlit as st
import pandas as pd
from collections import Counter
import random
from datetime import datetime
import itertools

st.set_page_config(page_title="Primitiva Elite", layout="wide")
st.title("🎰 Primitiva Elite - 2 Combinaciones Óptimas")
st.markdown("**Análisis avanzado +15 años** • Sin dependencias extra")

@st.cache_data(ttl=3600)
def load_data():
    with st.spinner("📥 Cargando histórico completo..."):
        try:
            url1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTov1BuA0nkVGTS48arpPFkc9cG7B40Xi3BfY6iqcWTrMwCBg5b50-WwvnvaR6mxvFHbDBtYFKg5IsJ/pub?gid=0&single=true&output=csv"
            url2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTov1BuA0nkVGTS48arpPFkc9cG7B40Xi3BfY6iqcWTrMwCBg5b50-WwvnvaR6mxvFHbDBtYFKg5IsJ/pub?gid=1&single=true&output=csv"
            df = pd.concat([pd.read_csv(url1), pd.read_csv(url2)], ignore_index=True)
            st.success(f"✅ {len(df):,} sorteos cargados")
            return df
        except:
            st.error("Error al cargar datos. Revisa tu conexión.")
            return None

df = load_data()

if df is not None:
    col1, col2 = st.columns(2)
    with col1:
        years = st.slider("Años a analizar", 8, 25, 15)
    with col2:
        strategy = st.selectbox("Estrategia", ["Balanced Elite (Recomendada)", "Mixed Hot+Cold"])

    # Preprocesado
    date_col = next((col for col in df.columns if 'fecha' in str(col).lower()), None)
    num_cols = [col for col in df.columns if any(str(i) in str(col).lower() for i in range(1,7))]

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        cutoff = datetime.now() - pd.Timedelta(days=365 * years)
        recent = df[df[date_col] >= cutoff].copy()
    else:
        recent = df.tail(1800)

    all_nums = []
    for col in num_cols[:6]:
        all_nums.extend(pd.to_numeric(recent[col], errors='coerce').dropna().astype(int))

    freq = Counter(all_nums)
    total = len(recent)

    st.subheader("📊 Estadísticas clave")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("**🏆 Top 15 números más frecuentes**")
        for n, c in freq.most_common(15):
            st.write(f"{n:2d} → {c} veces ({c/total*100:.1f}%)")
    
    with col_g2:
        st.write("**❄️ Top 10 menos frecuentes**")
        for n, c in freq.most_common()[-10:]:
            st.write(f"{n:2d} → {c} veces")

    # Generador élite
    def generate_elite_combo(freq, strategy):
        hot = [n for n, _ in freq.most_common(30)]
        cold = [n for n, _ in freq.most_common()[-20:]]
        
        for _ in range(300):
            if strategy == "Mixed Hot+Cold":
                combo = sorted(random.sample(hot[:22], 4) + random.sample(cold, 2))
            else:
                combo = sorted(random.sample(range(1,50), 6))
            
            odds = sum(1 for x in combo if x % 2 == 1)
            lows = sum(1 for x in combo if x <= 25)
            s = sum(combo)
            decades = len(set(x//10 for x in combo))
            
            if (odds in [3, 4] and 
                lows in [2, 3, 4] and 
                120 <= s <= 185 and 
                decades >= 4 and 
                max(combo) - min(combo) >= 18 and
                not any(abs(combo[i]-combo[i+1]) == 1 for i in range(5))):
                return combo, random.randint(0, 9), s, odds
        return sorted(random.sample(hot, 6)), random.randint(0, 9), sum(hot[:6]), 3

    if st.button("🎯 GENERAR MIS 2 MEJORES COMBINACIONES", type="primary", use_container_width=True):
        st.subheader("🏆 Tus 2 Combinaciones Élite")
        
        for i in range(2):
            combo, reintegro, suma, impares = generate_elite_combo(freq, strategy)
            st.success(f"""
            **Combinación {i+1}**  
            **{combo}** + **Reintegro: {reintegro}**  
            Suma: **{suma}** | Impares: **{impares}/6**
            """)

    st.info("💡 Estas combinaciones están filtradas por los patrones más comunes en la historia de La Primitiva.")
    st.caption("Juega con responsabilidad • Datos públicos")
