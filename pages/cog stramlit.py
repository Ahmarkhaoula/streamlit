# !pip install streamlit
# !pip install leafmap==0.2.0

import streamlit as st
import leafmap

def main():
    st.title("Application Streamlit avec COG")

    # Fournir le chemin local du jeu de données TIFF
    tif_path = "donnee/AAAA.tif"

    # Valider le format COG (Cloud-Optimized GeoTIFF)
    st.subheader("Validation COG du fichier TIFF")
    cog_validation_result = leafmap.cog_validate(tif_path, verbose=True)
    st.write(cog_validation_result)

    # Convertir l'image en COG (Cloud-Optimized GeoTIFF) tuilé
    out_cog = "cog.tif"
    st.subheader("Conversion en COG")
    leafmap.image_to_cog(tif_path, out_cog)

    # Valider le format COG pour le fichier de sortie
    st.subheader("Validation COG du fichier de sortie")
    cog_validation_result_out = leafmap.cog_validate(out_cog, verbose=True)
    st.write(cog_validation_result_out)

    # Créer une carte leafmap dans Streamlit avec client
    st.subheader("Carte leafmap avec COG local")
    m = leafmap.Map()
    m.add_raster(out_cog, palette="terrain", layer_name="Local COG")

    # Utiliser st.pydeck_chart pour afficher la carte
    st.pydeck_chart(m.to_dict())

if __name__ == "__main__":
    main()
