import xml.etree.ElementTree as ET
import sys
import requests
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

def analizar_wsdl(file_path):
    """
    Analiza un archivo WSDL y extrae información clave.
    """
    try:
        tree = ET.parse(file_path)  # Parsear el archivo WSDL
        root = tree.getroot()       # Obtener el nodo raíz

        # Mostrar el nombre del nodo raíz y su espacio de nombres
        print(f"Tag raíz: {root.tag}")
        print(f"Espacio de nombres (URI): {root.tag.split('}')[0][1:]}")  # Extraer el espacio de nombres

        # Listar los nodos principales del WSDL
        print("\nNodos principales:")
        for child in root:
            print(f"- Tag: {child.tag}, Atributos: {child.attrib}")

        # Buscar definiciones específicas (mensajes, operaciones)
        print("\nMensajes en el WSDL:")
        for message in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message"):
            print(f"- Message Name: {message.attrib['name']}")
            for part in message:
                print(f"  - Part: {part.tag}, Atributos: {part.attrib}")

        print("\nOperaciones en el WSDL:")
        for operation in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
            print(f"- Operation Name: {operation.attrib['name']}")

        # Extraer la URL del servicio (si existe)
        service_address = root.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}address")
        if service_address is not None:
            print("\nURL del servicio:")
            print(f"- {service_address.attrib['location']}")
        else:
            print("\nNo se encontró una dirección para el servicio.")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta especificada: {file_path}")
    except ET.ParseError:
        print(f"Error: No se pudo analizar el archivo. Asegúrate de que sea un archivo WSDL válido.")

if __name__ == "__main__":
    # Verificar si se proporcionó un argumento
    if len(sys.argv) < 2:
        print("Uso: python script.py <ruta_al_archivo_wsdl_o_url>")
    else:
        wsdl_path = sys.argv[1]

        # Verificar si es una URL
        if wsdl_path.startswith("http://") or wsdl_path.startswith("https://"):
            # Descargar el archivo WSDL y analizarlo
            local_file = "temp.wsdl"  # Archivo temporal para guardar el WSDL
            wsdl_path = descargar_wsdl(wsdl_path, local_file)

        # Analizar el archivo WSDL
        analizar_wsdl(wsdl_path)

        # Limpiar el archivo temporal si se descargó
        if os.path.exists("temp.wsdl"):
            os.remove("temp.wsdl")

'''
1. Recibe una URL o archivo local como entrada:
    Si es una URL, descarga el archivo WSDL usando la librería requests.
    Si es un archivo local, simplemente lo analiza directamente.

2. Analiza el archivo con ElementTree:
    El archivo WSDL es un tipo de archivo XML que organiza la información en "etiquetas" (<tag>).
    El script examina estas etiquetas para encontrar:
        Mensajes: Cómo se llama cada parte de la comunicación.
        Operaciones: Qué "acciones" puedes pedirle al servicio.
        Dirección del servicio: La URL donde se encuentra el servicio.

3. Muestra la información:
    Imprime los detalles encontrados, como:
        El tipo de archivo (su raíz y espacio de nombres).
        Las operaciones que soporta (como comandos en un menú).
        La dirección del servicio, para que sepas dónde conectarte.

4. Elimina archivos temporales:
    Si descargó el archivo desde una URL, lo borra al final para mantener limpio el sistema.

'''