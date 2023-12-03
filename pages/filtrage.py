import streamlit as st
import folium
from streamlit_folium import folium_static
import os
import numpy as np
import rasterio as rio
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
from urllib.error import URLError
import tempfile

def load_hotel_data(file_path, min_lat, max_lat, min_lon, max_lon):
    # Load hotel data from Parquet file
    df = pd.read_parquet(file_path, engine='fastparquet')

    # Convert bytes to GeoPandas objects
    df['geometry'] = df['geometry'].apply(lambda x: loads(x))
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    # Filter data based on specified coordinates
    filtered_gdf = gdf.cx[min_lon:max_lon, min_lat:max_lat]

    return filtered_gdf

def add_hotel_markers(carte, gdf):
    # Add hotel markers to the map
    for index, row in gdf.iterrows():
        try:
            latitude, longitude = row['geometry'].y, row['geometry'].x

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                tooltip=f"Hotel: {row['Hotel name']}"
            ).add_to(carte)

        except Exception as e:
            st.warning(f"Error extracting coordinates for hotel {row['Hotel name']}: {e}")

def save_folium_map_as_png(map_obj, output_path):
    temp_html = tempfile.NamedTemporaryFile(delete=False)
    map_obj.save(temp_html.name)

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    driver.get(f'file://{temp_html.name}')

    time.sleep(5)

    driver.save_screenshot(output_path)

    driver.quit()

    temp_html.close()

def convert_png_to_pdf(png_path, pdf_path, min_latitude, max_latitude, min_longitude, max_longitude, selected_column, min_value, max_value):
    image = Image.open(png_path)
    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer, pagesize=image.size)
    pdf.drawInlineImage(png_path, 0, 0, width=image.width, height=image.height)

    # Ajouter les informations de filtrage au PDF
    pdf.drawString(10, 10, f"Latitude minimale: {min_latitude}")
    pdf.drawString(10, 20, f"Latitude maximale: {max_latitude}")
    pdf.drawString(10, 30, f"Longitude minimale: {min_longitude}")
    pdf.drawString(10, 40, f"Longitude maximale: {max_longitude}")
    pdf.drawString(10, 50, f"Colonne sélectionnée: {selected_column}")
    pdf.drawString(10, 60, f"Valeur minimale: {min_value}")
    pdf.drawString(10, 70, f"Valeur maximale: {max_value}")

    pdf.save()

    pdf_buffer.seek(0)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

def main():
    st.title("Filter data")



    # User input for filtering coordinates
    
    min_latitude = st.number_input("Enter Minimum Latitude:", value=21.0, min_value=21.0, max_value=30.0)
    max_latitude = st.number_input("Enter Maximum Latitude:", value=36.0, min_value=-36.0, max_value=36.0)
    min_longitude = st.number_input("Enter Minimum Longitude:", value=-18.0, min_value=-18.0, max_value=18.0)
    max_longitude = st.number_input("Enter Maximum Longitude:", value=-0.0, min_value=-0.0, max_value=0.0)

    # Create a base map centered on a specific position
    carte = folium.Map(location=[33.379103, -6.430229], zoom_start=4)

    try:
        # Load all data to get column names for the attribute selection
        gdf_all = load_hotel_data(r"D:\iav\3ci\S5\web_mapping\projet_streanlit\donnee\Hotels.parquet",
                                  min_latitude, max_latitude, min_longitude, max_longitude)

        # Exclude specific columns from the attribute selection, including "geometry"
        excluded_columns = ["id", "Hotel name", "Rank ", "Date", "geometry"]
        attribute_columns = [col for col in gdf_all.columns if col not in excluded_columns]

        # Get user input for selecting attribute column
        selected_column = st.selectbox("Select Attribute Column:", attribute_columns)

        # Get user input for filtering column values
        min_value = st.number_input(f"Enter Minimum Value for {selected_column}:", value=gdf_all[selected_column].min())
        max_value = st.number_input(f"Enter Maximum Value for {selected_column}:", value=gdf_all[selected_column].max())

        # Load filtered hotel data based on both attribute column values and spatial coordinates
        gdf_filtered = gdf_all[(gdf_all[selected_column] >= min_value) & (gdf_all[selected_column] <= max_value)]

        # Add hotel markers to the map
        add_hotel_markers(carte, gdf_filtered)

        # Display the updated map in Streamlit
        folium_static(carte)

        if st.button("Convert to PDF"):
            screenshot_path = 'output.png'
            pdf_path = 'output.pdf'

            save_folium_map_as_png(carte, screenshot_path)
            convert_png_to_pdf(
                screenshot_path,
                pdf_path,
                min_latitude, max_latitude, min_longitude, max_longitude,
                selected_column, min_value, max_value
            )

            st.success(' PDF done ✅')
        
            # Utiliser st.file_download pour télécharger le fichier PDF
            with open(pdf_path, 'rb') as f:
                st.download_button('Downlaod PDF', f, key='pdf_download_button', help="Download PDF", file_name='output.pdf', mime='application/pdf')

    except URLError as e:
        st.error(f"URL Error: {e}")

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main()