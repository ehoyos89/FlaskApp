"""Funciones de utilidad compartidas"""
import os
from io import BytesIO
from PIL import Image

# Números mágicos de http://www.exiv2.org/tags.html
EXIF_ORIENTATION = 274

def random_hex_bytes(n_bytes):
    """Crea una cadena codificada en hexadecimal de bytes aleatorios."""
    return os.urandom(n_bytes).hex()

def resize_image(file_p, size):
    """Redimensiona una imagen para que se ajuste al tamaño y la guarda en el directorio de la ruta."""
    dest_ratio = size[0] / float(size[1])
    try:
        image = Image.open(file_p)
    except IOError:
        print("Error: No se puede abrir la imagen")
        return None

    try:
        exif = dict(image._getexif().items())
        if exif[EXIF_ORIENTATION] == 3:
            image = image.rotate(180, expand=True)
        elif exif[EXIF_ORIENTATION] == 6:
            image = image.rotate(270, expand=True)
        elif exif[EXIF_ORIENTATION] == 8:
            image = image.rotate(90, expand=True)
    except:
        print("No hay datos EXIF")

    source_ratio = image.size[0] / float(image.size[1])

    # La imagen es más pequeña que el destino en ambos ejes,
    # no la escales.
    if image.size < size:
        new_width, new_height = image.size
    elif dest_ratio > source_ratio:
        new_width = int(image.size[0] * size[1]/float(image.size[1]))
        new_height = size[1]
    else:
        new_width = size[0]
        new_height = int(image.size[1] * size[0]/float(image.size[0]))
    image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    final_image = Image.new("RGBA", size)
    topleft = (int((size[0]-new_width) / float(2)),
               int((size[1]-new_height) / float(2)))
    final_image.paste(image, topleft)
    bytes_stream = BytesIO()
    final_image.save(bytes_stream, 'PNG')
    return bytes_stream.getvalue()
