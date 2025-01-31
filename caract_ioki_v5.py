import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np  # Import numpy for calculations

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse IOKI", layout="wide")

# Chargement des données
df = pd.read_csv("DATA/006_20250131T105453.csv", sep=",")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Calculer les moyennes pour chaque ligne
df["IOKI 1_AV (A)"] = df["IOKI 1 (A)"].rolling(window=5, min_periods=1).mean()  # Moyenne mobile de IOKI 1
df["IOKI 2_AV (A)"] = df["IOKI 2 (A)"].rolling(window=5, min_periods=1).mean()  # Moyenne mobile de IOKI 2

# Calcul des résidus pour les données brutes
residuals = df["IOKI 2 (A)"] - df["IOKI 1 (A)"]

# Calcul de l'écart type des résidus pour les données brutes
std_residuals = np.std(residuals, ddof=1)  # ddof=1 pour un échantillon



# Sélection de la section à afficher
section = st.radio("Sélectionnez une section :", ["Données", "Visualisation"], index=0)

if section == "Données":
    st.title("📊 Données IOKI")
    st.markdown("Affichage des données chargées.")
    st.dataframe(df.style.format(precision=2))
    st.write("### 📥 Télécharger le dataset")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données",
        data=csv,
        file_name="donnees_ioki.csv",
        mime="text/csv"
    )

elif section == "Visualisation":
    st.title("📊 Visualisation de la dispersion entre IOKI 1 et IOKI 2")
    st.markdown("Cette application permet d'afficher et d'analyser la relation entre les variables **IOKI 1** et **IOKI 2** sous forme de graphiques interactifs.")
    # Affichage du résultat pour les données brutes
    st.write(f"📊 **Écart type des résidus pour les données brutes :** {std_residuals:.4f} A")

    # Calcul des résidus pour les moyennes
    residuals_avg = df["IOKI 2_AV (A)"] - df["IOKI 1_AV (A)"]

    # Calcul de l'écart type des résidus pour les moyennes
    std_residuals_avg = np.std(residuals_avg, ddof=1)

    # Affichage du résultat pour les moyennes
    st.write(f"📊 **Écart type des résidus pour les moyennes :** {std_residuals_avg:.4f} A")

    # Sidebar pour les paramètres
    st.sidebar.header("🔧 Paramètres")
    graph_choice = st.sidebar.radio("Sélectionnez le type de graphique :", ["Scatter Plot", "Scatter + Linéarité", "Évolution Temporelle", "Évolution Temporelle AVG"])  
    point_color = st.sidebar.color_picker("Couleur des points", "#1f77b4")
    point_size = st.sidebar.slider("Taille des points", 5, 50, 15)
    show_grid = st.sidebar.checkbox("Afficher la grille", True)

    # Fonction pour créer un scatter plot simple avec plotly
    def create_scatter_plot():
        fig = px.scatter(
            df, 
            x="IOKI 1 (A)", 
            y="IOKI 2 (A)", 
            title="Dispersion entre IOKI 1 et IOKI 2",
            labels={"IOKI 1 (A)": "IOKI 1 (A)", "IOKI 2 (A)": "IOKI 2 (A)"},
            color_discrete_sequence=[point_color]
        )
        fig.update_traces(marker=dict(size=point_size, line=dict(width=2, color='black')))
        fig.update_layout(showlegend=False, width=1200, height=700)  # Set custom width and height
        if show_grid:
            fig.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
                              yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))
        return fig

    # Fonction pour créer un scatter plot avec la ligne de linéarité idéale
    def create_scatter_with_line():
        fig = px.scatter(
            df, 
            x="IOKI 1 (A)", 
            y="IOKI 2 (A)", 
            title="Dispersion avec une droite de linéarité idéale",
            labels={"IOKI 1 (A)": "IOKI 1 (A)", "IOKI 2 (A)": "IOKI 2 (A)"},
            color_discrete_sequence=[point_color]
        )
        min_val = min(df["IOKI 1 (A)"].min(), df["IOKI 2 (A)"].min())
        max_val = max(df["IOKI 1 (A)"].max(), df["IOKI 2 (A)"].max())
        fig.add_shape(
            type="line", 
            x0=min_val, y0=min_val, x1=max_val, y1=max_val,
            line=dict(color="red", width=2, dash="dash"), 
            name="Linéarité idéale"
        )
        fig.update_traces(marker=dict(size=point_size, line=dict(width=2, color='black')))
        fig.update_layout(showlegend=False, width=1200, height=700)  # Set custom width and height
        if show_grid:
            fig.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
                              yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))
        return fig

    # Fonction pour créer un graphique d'évolution temporelle
    def create_time_series_plot():
        fig = px.line(
            df, 
            x="Timestamp", 
            y=["IOKI 1 (A)", "IOKI 2 (A)"], 
            title="Évolution de IOKI 1 et IOKI 2 en fonction du temps",
            labels={"Timestamp": "Temps", "value": "Courant (A)", "variable": "IOKI"},
            color_discrete_map={
                "IOKI 1 (A)": "blue",  # Set color for IOKI 1
                "IOKI 2 (A)": "red"    # Set color for IOKI 2
            }
        )
        fig.update_layout(width=1200, height=700, xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
                        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))
        return fig

    # Fonction pour créer un graphique d'évolution temporelle avec les moyennes
    def create_time_series_plot_avg():
        fig = px.line(
            df, 
            x="Timestamp", 
            y=["IOKI 1_AV (A)", "IOKI 2_AV (A)"],  # Utilisation des moyennes
            title="Évolution des moyennes de IOKI 1 et IOKI 2 en fonction du temps",
            labels={"Timestamp": "Temps", "value": "Courant (A)", "variable": "IOKI"},
            color_discrete_map={
                "IOKI 1_AV (A)": "blue",  # Couleur pour IOKI 1
                "IOKI 2_AV (A)": "red"    # Couleur pour IOKI 2
            }
        )
        fig.update_layout(width=1200, height=700, xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
                        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))
        return fig

    # Sélection du graphique à afficher
    if graph_choice == "Scatter Plot":
        fig = create_scatter_plot()
    elif graph_choice == "Scatter + Linéarité":
        fig = create_scatter_with_line()
    elif graph_choice == "Évolution Temporelle":
        fig = create_time_series_plot()
    elif graph_choice == "Évolution Temporelle AVG":
        fig = create_time_series_plot_avg()

    # Affichage du graphique dans Streamlit avec interactivité
    st.plotly_chart(fig, use_container_width=True)

    # Fonction pour convertir la figure en image téléchargeable
    def fig_to_bytes(fig):
        return fig.to_image(format="png", width=1500, height=800)

    # Ajout d'un bouton pour télécharger le graphique
    st.download_button(
        label="📥 Télécharger le graphique",
        data=fig_to_bytes(fig),
        file_name="graphique.png",
        mime="image/png"
    )

    # Ajout d'un footer
    st.markdown(""" 
    --- 
    💡 ** Utilisez la barre latérale pour modifier l'affichage du graphique.
    """)
