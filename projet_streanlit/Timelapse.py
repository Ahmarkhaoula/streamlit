import os
import imageio
import folium
from folium import raster_layers
from streamlit_folium import folium_static
import streamlit as st
from PIL import Image
import numpy as np
import rasterio as rio 
import cv2
from branca.colormap import linear

def get_image_coordinates(tiff_path):
    with rio.open(tiff_path) as src:
        bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
    return bounds

def interpolate_images(img1, img2, steps, bounds1, bounds2):
    interpolated_images = []
    for alpha in np.linspace(0, 1, steps):
        interpolated_img = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
        interpolated_bounds = [
            [bounds1[0][0] * (1 - alpha) + bounds2[0][0] * alpha, bounds1[0][1] * (1 - alpha) + bounds2[0][1] * alpha],
            [bounds1[1][0] * (1 - alpha) + bounds2[1][0] * alpha, bounds1[1][1] * (1 - alpha) + bounds2[1][1] * alpha]
        ]
        interpolated_images.append((interpolated_img, interpolated_bounds))
    return interpolated_images

def create_gif(image_folder, gif_name, interpolation_steps=20):
    images = []
    bounds_list = []

    for filename in os.listdir(image_folder):
        if filename.endswith(".tif"):
            img_path = os.path.join(image_folder, filename)
            img = Image.open(img_path)
            img_resized = img.resize((200, 200))
            images.append(np.array(img_resized))
            bounds_list.append(get_image_coordinates(img_path))

    # Créer des images intermédiaires pour une transition plus douce
    interpolated_images = []
    for i in range(len(images) - 1):
        interpolated_images.extend(interpolate_images(images[i], images[i + 1], interpolation_steps, bounds_list[i], bounds_list[i + 1]))

    # Enregistrez la séquence d'images en tant que GIF en boucle continue
    gif_images, gif_bounds = zip(*interpolated_images)
    imageio.mimsave(gif_name, gif_images, duration=1.0 / interpolation_steps, loop=0)
    return gif_bounds

def app():
    st.title("Timelapse")

    # Liste des options
    options = ["visitors", "moroccans", "foreigners"]
    
    # Sélection de l'utilisateur
    user_choice = st.selectbox("Choose an attribute :", options)

    if user_choice == "visitors":
        image_folder = r'donnee\visitors'
        c = linear.viridis.scale(0, 70)
        c.caption = 'Visitors'
    elif user_choice == "moroccans":
        image_folder = r'donnee\moroccans'
        c = linear.viridis.scale(0, 50)
        c.caption = 'Moroccans'
    else:
        image_folder = r'donnee\foreigners'
        c = linear.viridis.scale(0, 20)
        c.caption = 'Foreigners'

       

    # Chemin pour enregistrer le GIF
    gif_path = f'donnee\{user_choice.lower()}\gif.gif'

    # Créer le GIF à partir des images TIFF avec une durée de 1 seconde entre chaque image
    gif_bounds = create_gif(image_folder, gif_path, interpolation_steps=10)

    # Récupérer le chemin d'accès à la première image TIFF
    first_tiff_path = os.path.join(image_folder, os.listdir(image_folder)[0])

    # Créer la carte
    my_map = folium.Map(location=[30.5,-6.2], zoom_start=5, tiles='OpenStreetMap')

    # Ajouter une superposition GIF
    gif_overlay = raster_layers.ImageOverlay(
        gif_path,
        bounds=gif_bounds[0],
        opacity=0.8,
    ).add_to(my_map)
    c.add_to(my_map)
    # Afficher la carte sur Streamlit
    st.markdown(f"This map includes a timelapse for the  {user_choice}.")

    # Utiliser folium_static pour afficher la carte Folium sur Streamlit
    folium_static(my_map)

