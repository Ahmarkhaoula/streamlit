import streamlit as st
import folium
from streamlit_folium import folium_static
from urllib.error import URLError
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
import folium.plugins as plugins
from branca.colormap import linear
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import tempfile
from reportlab.pdfgen import canvas
from io import BytesIO

def get_radius(column_value, selected_column):
    thresholds = {
        'Visitors': [18, 36, 53],
        'Moroccans': [13, 25, 38],
        'Foreigners': [5, 10, 15]
    }

    for category, values in thresholds.items():
        if category in selected_column:
            if column_value < values[0]:
                return 4
            elif values[0] <= column_value < values[1]:
                return 8
            elif values[1] <= column_value < values[2]:
                return 12
            else:
                return 16

    return 4

def get_color(column_value, selected_column, gdf):
    color_mapping = {
        'Visitors': linear.YlGnBu_09,
        'Moroccans': linear.YlGn_09,
        'Foreigners': linear.YlOrRd_09
    }

    for category, colormap in color_mapping.items():
        if category in selected_column:
            normalized_value = (column_value - gdf[selected_column].min()) / (gdf[selected_column].max() - gdf[selected_column].min())
            return colormap(normalized_value)

    return 'lightgray'

def create_map(gdf, selected_column, map_type, category_choice):
    carte = folium.Map(location=[33.379103, -6.430229], zoom_start=8)

    try:
        for index, row in gdf.iterrows():
            try:
                latitude, longitude = row['geometry'].y, row['geometry'].x
                column_value = row[selected_column]
                hotel_name = row['Hotel name']

                radius = get_radius(column_value, selected_column)
                color = get_color(column_value, selected_column, gdf)

                if map_type == 'Graduated symbols':
                    folium.CircleMarker(
                        location=[latitude, longitude],
                        radius=radius,
                        color='blue',
                        fill=True,
                        fill_color='blue',
                        tooltip=f"{hotel_name}: {selected_column}: {column_value}",
                    ).add_to(carte)
                elif map_type == 'Choropleth map':
                    folium.CircleMarker(
                        location=[latitude, longitude],
                        radius=4,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        tooltip=f"{hotel_name}: {selected_column}: {column_value}",
                    ).add_to(carte)

            except Exception as e:
                st.warning(f"Erreur lors de l'extraction des coordonnées pour {selected_column} {column_value}: {e}")

        if map_type == 'Choropleth map':
            if category_choice == 'Visitors':
                # Add a Choropleth legend
                colormap = linear.YlGnBu_09.scale(gdf[selected_column].min(), gdf[selected_column].max())
                colormap.caption = selected_column
                colormap.add_to(carte)
            elif category_choice == 'Moroccans':
                # Add a Choropleth legend
                colormap = linear.YlGn_09.scale(gdf[selected_column].min(), gdf[selected_column].max())
                colormap.caption = selected_column
                colormap.add_to(carte)
            elif category_choice == 'Foreigners':
                # Add a Choropleth legend
                colormap = linear.YlOrRd_09.scale(gdf[selected_column].min(), gdf[selected_column].max())
                colormap.caption = selected_column
                colormap.add_to(carte)

        minimap = plugins.MiniMap()
        carte.add_child(minimap)

        plugins.MarkerCluster().add_to(carte)
        plugins.MeasureControl(primary_length_unit='kilometers').add_to(carte)
        plugins.Fullscreen().add_to(carte)
        plugins.Draw(export=True).add_to(carte)
        folium.LatLngPopup().add_to(carte)

        folium_static(carte)
        return carte

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la création de la carte : {e}")

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

def convert_png_to_pdf(png_path, pdf_path, image_name, user_choice):
    image = Image.open(png_path)
    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer, pagesize=image.size)
    pdf.drawInlineImage(png_path, 0, 0, width=image.width, height=image.height)

    # Add image name and user choice to the PDF
    pdf.drawString(10, 10, f"Image Name: {image_name}")
    pdf.drawString(10, 20, f"User Choice: {user_choice}")

    pdf.save()

    pdf_buffer.seek(0)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

def app():
    st.title("Cartography of Hotels in Morocco")
    carte = None
    try:
        df = pd.read_parquet(r"D:\iav\3ci\S5\web_mapping\projet_streanlit\donnee\Hotels.parquet", engine='fastparquet')
        df['geometry'] = df['geometry'].apply(lambda x: loads(x))
        gdf = gpd.GeoDataFrame(df, geometry='geometry')

        excluded_columns = ['id', 'Hotel name', 'Rank ', 'Price (MAD) ', 'Date', 'geometry']
        selectable_columns = [col for col in gdf.columns if col not in excluded_columns]

        category_choice = st.radio("Choose category :", ['Visitors', 'Moroccans', 'Foreigners'])

        if category_choice == 'Visitors':
            selected_column = st.selectbox("Choose attribute :",
                                           ["Visitors today (J)", "Visitors yesterday (J-1)", "Visitors J-2",
                                            "Visitors J-3", "Visitors J-4", "Visitors J-5", "Visitors J-6"])
        elif category_choice == 'Moroccans':
            selected_column = st.selectbox("Choose attribute :",
                                           ["Moroccans today (J)", "Moroccans yesterday (J-1)", "Moroccans J-2",
                                            "Moroccans J-3", "Moroccans J-4", "Moroccans J-5", "Moroccans J-6"])
        elif category_choice == 'Foreigners':
            selected_column = st.selectbox("Choose attribute :",
                                           ["Foreigners today (J)", "Foreigners yesterday (J-1)",
                                            "Foreigners J-2", "Foreigners J-3", "Foreigners J-4", "Foreigners J-5",
                                            "Foreigners J-6"])

        carte_type = st.radio("Choose thematic map type", ['Graduated symbols', 'Choropleth map'])

        if carte_type == 'Graduated symbols':
            st.subheader("Graduated symbols map")
            col1, col2 = st.columns(2)
            with col1:
                carte = create_map(gdf, selected_column, 'Graduated symbols', 'Visitors')

            with col2:
                image = Image.open(
                    r"D:\iav\3ci\S5\web_mapping\projet_streanlit\donnee\WhatsApp Image 2023-11-26 at 20.49.29.jpeg")
                st.image(image, caption='Legend', width=150)

        elif carte_type == 'Choropleth map':
            st.subheader("Choropleth map")
            if category_choice == 'Visitors':
                carte = create_map(gdf, selected_column, 'Choropleth map', 'Visitors')
            elif category_choice == 'Moroccans':
                carte = create_map(gdf, selected_column, 'Choropleth map', 'Moroccans')
            elif category_choice == 'Foreigners':
                carte = create_map(gdf, selected_column, 'Choropleth map', 'Foreigners')

        if st.button("Download PDF"):
            screenshot_path = 'output.png'
            pdf_path = 'output.pdf'

            save_folium_map_as_png(carte, screenshot_path)
            convert_png_to_pdf(screenshot_path, pdf_path, selected_column, category_choice)

            st.success('Conversion terminée! Téléchargez le PDF ci-dessous:')

            # Utiliser st.file_download pour télécharger le fichier PDF
            with open(pdf_path, 'rb') as f:
                pdf_download_button_key = f'pdf_download_button_{category_choice}_{selected_column}_{carte_type.replace(" ", "_")}'
                st.download_button('Télécharger le PDF', f, key=pdf_download_button_key,
                                   help="Cliquez pour télécharger le PDF", file_name='output.pdf', mime='application/pdf')

    except URLError as e:
        st.error(f"Erreur d'URL : {e}")

    except pd.errors.EmptyDataError:
        st.warning("Le fichier Parquet est vide. Veuillez vérifier le fichier source.")

    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
