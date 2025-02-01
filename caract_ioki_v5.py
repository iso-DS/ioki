import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np  # Import numpy for calculations
from io import StringIO
import os

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse IOKI", layout="wide")


#Check fichier : ATTENTION A LA CASE de l' extension Maj ou Miniscule
#st.write("📂 Liste des fichiers dans `DATA/` :")
#st.write(os.listdir("DATA/"))

file = "DATA/006_20250131T105453.CSV"
if not os.path.exists(file):
    st.error(f"❌ Le fichier `{file}` n'existe pas. Vérifiez son emplacement !")
else:
    st.success(f"✅ Chemin Fichier `{file}` trouvé ! En cours...")
    df = pd.read_csv(file)

# Function to load data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Allow user to upload a file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
file = r'./DATA/006_20250131T105453.CSV'  # Ensure correct file path

# Load dataset
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = load_data(file)

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Compute moving averages
df["IOKI 1_AV (A)"] = df["IOKI 1 (A)"].rolling(window=5, min_periods=1).mean()
df["IOKI 2_AV (A)"] = df["IOKI 2 (A)"].rolling(window=5, min_periods=1).mean()

# Compute residuals
residuals = df["IOKI 2 (A)"] - df["IOKI 1 (A)"]
std_residuals = np.std(residuals, ddof=1)

# Section selection
section = st.radio("Sélectionnez une section :", ["Données", "Visualisation"], index=0)

if section == "Données":
    st.title("📊 Données IOKI")
    st.dataframe(df.style.format(precision=2))

    # Download dataset
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données",
        data=csv,
        file_name="donnees_ioki.csv",
        mime="text/csv"
    )

elif section == "Visualisation":
    st.title("📊 Visualisation de la dispersion entre IOKI 1 et IOKI 2")
    st.write(f"📊 **Écart type des résidus pour les données brutes :** {std_residuals:.4f} A")

    # Compute moving average residuals
    residuals_avg = df["IOKI 2_AV (A)"] - df["IOKI 1_AV (A)"]
    std_residuals_avg = np.std(residuals_avg, ddof=1)
    st.write(f"📊 **Écart type des résidus pour les moyennes :** {std_residuals_avg:.4f} A")

    # Sidebar settings
    st.sidebar.header("🔧 Paramètres")
    graph_choice = st.sidebar.radio("Sélectionnez le type de graphique :", 
                                    ["Scatter Plot", "Scatter + Linéarité", 
                                     "Évolution Temporelle", "Évolution Temporelle AVG"])
    point_color = st.sidebar.color_picker("Couleur des points", "#1f77b4")
    point_size = st.sidebar.slider("Taille des points", 5, 50, 15)
    show_grid = st.sidebar.checkbox("Afficher la grille", True)

    # Graph functions
    def create_scatter_plot():
        fig = px.scatter(df, x="IOKI 1 (A)", y="IOKI 2 (A)", title="Dispersion entre IOKI 1 et IOKI 2",
                         color_discrete_sequence=[point_color])
        fig.update_traces(marker=dict(size=point_size, line=dict(width=2, color='black')))
        fig.update_layout(showlegend=False, width=1200, height=700)
        if show_grid:
            fig.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
                              yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))
        return fig

    def create_scatter_with_line():
        fig = create_scatter_plot()
        min_val = min(df["IOKI 1 (A)"].min(), df["IOKI 2 (A)"].min())
        max_val = max(df["IOKI 1 (A)"].max(), df["IOKI 2 (A)"].max())
        fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val,
                      line=dict(color="red", width=2, dash="dash"))
        return fig

    def create_time_series_plot():
        fig = px.line(df, x="Timestamp", y=["IOKI 1 (A)", "IOKI 2 (A)"], 
                      title="Évolution de IOKI 1 et IOKI 2 en fonction du temps")
        return fig

    def create_time_series_plot_avg():
        fig = px.line(df, x="Timestamp", y=["IOKI 1_AV (A)", "IOKI 2_AV (A)"],
                      title="Évolution des moyennes de IOKI 1 et IOKI 2")
        return fig

    # Select graph
    if graph_choice == "Scatter Plot":
        fig = create_scatter_plot()
    elif graph_choice == "Scatter + Linéarité":
        fig = create_scatter_with_line()
    elif graph_choice == "Évolution Temporelle":
        fig = create_time_series_plot()
    elif graph_choice == "Évolution Temporelle AVG":
        fig = create_time_series_plot_avg()

    # Display graph
    st.plotly_chart(fig, use_container_width=True)

    # Download button for the graph
    from plotly.io import write_image
    def fig_to_bytes(fig):
        return fig.to_image(format="png", width=1500, height=800, engine="kaleido")

    st.download_button(
        label="📥 Télécharger le graphique",
        data=fig_to_bytes(fig),
        file_name="graphique.png",
        mime="image/png"
    )
