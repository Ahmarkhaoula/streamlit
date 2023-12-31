import subprocess

# Remplacez ces valeurs par le chemin de votre fichier GeoTIFF d'entrée et le nom du fichier COG de sortie
input_tiff = r'donnee\visitors\J-1.tif'
output_cog = r'donnee\J-1.cog.tif'

# Commande gdal_translate pour convertir le GeoTIFF en COG
command = [
    'gdal_translate',
    '-co', 'TILED=YES',
    '-co', 'COMPRESS=DEFLATE',
    '-co', 'COPY_SRC_OVERVIEWS=YES',
    input_tiff,
    output_cog
]

# Exécution de la commande
subprocess.run(command)
