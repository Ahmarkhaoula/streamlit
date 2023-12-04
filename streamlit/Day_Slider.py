import os
import folium
from folium import raster_layers
from streamlit_folium import folium_static
import streamlit as st
import numpy as np
import rasterio as rio
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import tempfile
from reportlab.pdfgen import canvas
from io import BytesIO
from branca.colormap import linear

def get_image_coordinates(tiff_path):
    with rio.open(tiff_path) as src:
        bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
    return bounds

def create_images(image_folder):
    images = []
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(".tif"):
            img_path = os.path.join(image_folder, filename)
            with rio.open(img_path) as src:
                img = np.moveaxis(src.read(), 0, -1)
            images.append((filename, img, get_image_coordinates(img_path)))
    return images

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
    st.title("Slider")
    st.write("Slide between different days relative to the attribute ")

    # Liste des options
    options = ["visitors", "moroccans", "foreigners"]
        
    # Sélection de l'utilisateur
    user_choice = st.selectbox("Choose an option :", options)

    if user_choice == 'visitors':
# Add a Choropleth legend
       c = linear.viridis.scale(0, 70)
       c.caption = 'Visitors'
    
    elif user_choice == 'moroccans':
        # Add a Choropleth legend
        c = linear.viridis.scale(0, 50)
        c.caption = 'Moroccans'

    elif user_choice == 'foreigners':
        # Add a Choropleth legend
        c = linear.viridis.scale(0, 20)
        c.caption = 'Foreigners'

    # Dossier des images
    image_folder = os.path.join('donnee', user_choice.lower())


    my_map = folium.Map(location=[30.5, -6.2], zoom_start=5, tiles='OpenStreetMap')

    # Récupérer les images, leurs noms et coordonnées
    images = create_images(image_folder)

    if images:
        # Slider pour sélectionner une image
        selected_image_name = st.select_slider("Slide to image", options=['J', 'J-1', 'J-2', 'J-3', 'J-4', 'J-5', 'J-6'])

        # Récupérer l'image sélectionnée par son nom
        selected_image = next((img[1] for img in images if img[0] == f'{selected_image_name}.tif'), None)
        bounds = next((img[2] for img in images if img[0] == f'{selected_image_name}.tif'), None)

        if selected_image is not None and bounds is not None:
            # Ajouter une superposition d'image à la carte
            image_overlay = folium.raster_layers.ImageOverlay(
                name=user_choice,
                image=selected_image,
                bounds=bounds,
                interactive=True,
                zindex=1,
            )
        image_overlay.add_to(my_map)

        c.add_to(my_map)

        # Utiliser folium_static pour afficher la carte Folium sur Streamlit
        folium_static(my_map, width=1000, height=800)

        if st.button("Download PDF"):
            screenshot_path = 'output.png'
            pdf_path = 'output.pdf'

            save_folium_map_as_png(my_map, screenshot_path)
            convert_png_to_pdf(screenshot_path, pdf_path, selected_image_name, user_choice)

            st.success('Conversion terminée! Téléchargez le PDF ci-dessous:')
    
            # Utiliser st.file_download pour télécharger le fichier PDF
            with open(pdf_path, 'rb') as f:
                st.download_button('Télécharger le PDF', f, key='pdf_download_button', help="Cliquez pour télécharger le PDF", file_name='output.pdf', mime='application/pdf')


