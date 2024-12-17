import xml.etree.ElementTree as ET
import requests
import sys
import os

def descargar_wsdl(url, archivo_destino):
    """
    Descarga el archivo WSDL desde una URL y lo guarda localmente.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo errores en la solicitud
        with open(archivo_destino, "wb") as file:
            file.write(response.content)
        print(f"Archivo WSDL descargado: {archivo_destino}")
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo WSDL: {e}")
        sys.exit(1)

def mostrar_estructura_niveles(nodo, nivel=0):
    """
    Muestra la estructura general de un archivo WSDL, incluyendo niveles y subniveles.
    """
    espacio = "  " * nivel  # Espaciado para representar la jerarquía
    print(f"{espacio}- Nodo: {nodo.tag}, Atributos: {nodo.attrib}")
    for subnodo in nodo:
        mostrar_estructura_niveles(subnodo, nivel + 1)

if __name__ == "__main__":
    # Verificar si se proporcionó una URL como argumento
    if len(sys.argv) < 2:
        print("Uso: python script.py <url_wsdl>")
    else:
        url_wsdl = sys.argv[1]
        temp_file = "temp.wsdl"

        # Descargar el archivo WSDL
        wsdl_path = descargar_wsdl(url_wsdl, temp_file)

        # Analizar y mostrar la estructura general
        try:
            tree = ET.parse(wsdl_path)
            root = tree.getroot()
            print("Estructura general del WSDL:")
            mostrar_estructura_niveles(root)
        except ET.ParseError:
            print("Error al analizar el archivo. Asegúrate de que sea un archivo WSDL válido.")
        finally:
            # Eliminar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
