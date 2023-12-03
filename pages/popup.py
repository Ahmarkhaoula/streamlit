import streamlit as st
import folium
from streamlit_folium import folium_static
from urllib.error import URLError
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def create_visitors_chart(visitors):
    # Créer un graphique en fonction de la colonne 'Visitors today (J)'
    plt.figure(figsize=(3.5, 3.5))
    plt.plot(['Today', 'J-1', 'J-2', 'J-3', 'J-4', 'J-5', 'J-6'], visitors, marker='o', color='blue', linestyle='-', linewidth=1)
    plt.title('Visitors Trend')
    plt.xlabel('Day')
    plt.ylabel('Number of Visitors')

    # Convertir le graphique en image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encoder l'image en base64
    img_base64 = base64.b64encode(img.read()).decode('utf-8')
    
    return '<img src="data:image/png;base64,{}">'.format(img_base64)

def main():
    # Titre de l'application
    st.title("Cartography of Hotels in Morocco")

    # Création d'une carte de base centrée sur une position spécifique
    carte = folium.Map(location=[34.526765086141069, -3.846474658933936], zoom_start=6)

    chart_placeholder = st.empty()

    try:
        # Charger le fichier Parquet avec pandas et fastparquet
        df = pd.read_parquet(r"D:\iav\3ci\S5\web_mapping\projet_streanlit\donnee\Hotels.parquet", engine='fastparquet')

        # Convertir les objets bytes en objets GeoPandas
        gdf = gpd.GeoDataFrame(df, geometry=df['geometry'].apply(loads))

        # Ajouter les points du GeoDataFrame à la carte folium
        for index, row in gdf.iterrows():
            try:
                # Extraire les coordonnées à partir de la colonne 'geometry'
                latitude, longitude = row['geometry'].y, row['geometry'].x

                # Créer un popup avec un graphique basé sur 'Visitors today (J)'
                popup_content = create_visitors_chart([
                    row['Visitors today (J)'],
                    row['Visitors yesterday (J-1)'],
                    row['Visitors J-2'],
                    row['Visitors J-3'],
                    row['Visitors J-4'],
                    row['Visitors J-5'],
                    row['Visitors J-6']
                ])

                marker = folium.CircleMarker(
                    location=[latitude, longitude],
                    radius=5,  # Adjust the size of the circle as needed
                    color='blue',  # Set the color of the circle
                    fill=True,
                    fill_color='blue',  # Set the fill color of the circle
                    fill_opacity=0.7,  # Set the fill opacity
                    popup=folium.Popup(popup_content, max_width=1000),
                ).add_to(carte)

                # Add interactivity to the tooltip
                marker.add_child(folium.Tooltip(f"Click for details: {row['Hotel name']}"))

            except Exception as e:
                st.warning(f"Erreur lors de l'extraction des coordonnées pour l'hôtel {row['Hotel name']} : {e}")

        # Afficher la carte mise à jour dans Streamlit
        folium_static(carte)

    except URLError as e:
        # Gestion des erreurs liées aux URL
        st.error(f"Erreur d'URL : {e}")

    except Exception as e:
        # Gestion générique des erreurs
        st.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()