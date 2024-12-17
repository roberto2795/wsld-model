import xml.etree.ElementTree as ET
import requests
import os
import json
import sys
from lxml import etree

def descargar_wsdl(url, archivo_destino):
    """
    Descarga el archivo WSDL desde una URL y lo guarda localmente.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(archivo_destino, "wb") as file:
            file.write(response.content)
        print(f"Archivo WSDL descargado: {archivo_destino}")
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo WSDL: {e}")
        sys.exit(1)

def cargar_wsdl(file_path):
    """
    Carga el archivo WSDL y retorna el árbol raíz.
    """
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except ET.ParseError as e:
        print(f"Error al analizar el archivo WSDL: {e}")
        sys.exit(1)

def listar_mensajes(root):
    print("\nAnálisis: Listar todos los mensajes")
    print("Este análisis muestra todos los mensajes definidos en el WSDL y sus partes:")
    for message in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message"):
        print(f"- Mensaje: {message.attrib['name']}")
        for part in message:
            print(f"  Parte: {part.attrib}")

def listar_operaciones(root):
    print("\nAnálisis: Listar todas las operaciones")
    print("Este análisis muestra todas las operaciones disponibles en el servicio y sus mensajes de entrada/salida:")
    for operation in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
        print(f"- Operación: {operation.attrib['name']}")
        input_node = operation.find(".//{http://schemas.xmlsoap.org/wsdl/}input")
        output_node = operation.find(".//{http://schemas.xmlsoap.org/wsdl/}output")
        if input_node is not None:
            print(f"  Entrada: {input_node.attrib.get('message')}")
        if output_node is not None:
            print(f"  Salida: {output_node.attrib.get('message')}")

def listar_tipos(root):
    print("\nAnálisis: Ver tipos definidos en el esquema")
    print("Este análisis lista los tipos de datos definidos en el esquema del WSDL:")
    for schema in root.findall(".//{http://www.w3.org/2001/XMLSchema}schema"):
        for element in schema.findall("{http://www.w3.org/2001/XMLSchema}element"):
            print(f"- Elemento: {element.attrib.get('name')}, Tipo: {element.attrib.get('type')}")

def obtener_url_servicio(root):
    print("\nAnálisis: Obtener la URL del servicio")
    print("Este análisis obtiene la dirección del servicio web (SOAP):")
    address = root.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}address")
    if address is not None:
        print(f"- URL del servicio: {address.attrib['location']}")
    else:
        print("No se encontró dirección del servicio.")

def analizar_bindings(root):
    print("\nAnálisis: Analizar bindings (protocolo y formato)")
    print("Este análisis muestra los bindings definidos, incluyendo protocolo y formato:")
    for binding in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}binding"):
        print(f"- Binding: {binding.attrib['name']}")
        soap_binding = binding.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}binding")
        if soap_binding is not None:
            print(f"  Protocolo: {soap_binding.attrib.get('transport')}")

def analizar_excepciones(root):
    print("\nAnálisis: Identificar excepciones o fallos")
    print("Este análisis lista los mensajes de error o excepciones definidos en el WSDL:")
    for message in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message"):
        if "Exception" in message.attrib.get('name', ''):
            print(f"- Excepción: {message.attrib['name']}")

def mapa_relaciones(root):
    print("\nAnálisis: Generar mapa de relaciones")
    print("Este análisis muestra cómo se relacionan las operaciones con sus mensajes de entrada y salida:")
    for operation in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
        print(f"- Operación: {operation.attrib['name']}")
        input_msg = operation.find(".//{http://schemas.xmlsoap.org/wsdl/}input")
        output_msg = operation.find(".//{http://schemas.xmlsoap.org/wsdl/}output")
        if input_msg is not None:
            print(f"  Entrada: {input_msg.attrib['message']}")
        if output_msg is not None:
            print(f"  Salida: {output_msg.attrib['message']}")

def validar_estructura(file_path):
    print("\nAnálisis: Validar la estructura del WSDL")
    print("Este análisis valida si el archivo WSDL cumple con el estándar XML:")
    try:
        etree.parse(file_path)
        print("El archivo WSDL es válido.")
    except etree.XMLSyntaxError as e:
        print(f"Error de validación: {e}")

def exportar_json(root):
    print("\nAnálisis: Exportar la estructura a JSON")
    print("Este análisis convierte la estructura del WSDL en un archivo JSON para facilitar su análisis:")
    def nodo_a_diccionario(nodo):
        return {
            "tag": nodo.tag,
            "atributos": nodo.attrib,
            "hijos": [nodo_a_diccionario(hijo) for hijo in nodo]
        }
    estructura = nodo_a_diccionario(root)
    with open("estructura_wsdl.json", "w") as json_file:
        json.dump(estructura, json_file, indent=2)
    print("\nEstructura exportada a 'estructura_wsdl.json'.")

def mostrar_menu():
    print("\nMenú de análisis exploratorio del WSDL:")
    opciones = [
        "Listar todos los mensajes",
        "Listar todas las operaciones",
        "Ver tipos definidos en el esquema",
        "Obtener la URL del servicio",
        "Analizar bindings (protocolo y formato)",
        "Identificar excepciones o fallos",
        "Generar mapa de relaciones",
        "Validar la estructura del WSDL",
        "Exportar la estructura a JSON"
    ]
    for i, opcion in enumerate(opciones, 1):
        print(f"{i}. {opcion}")
    return opciones

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analisis_wsdl.py <url_wsdl>")
        sys.exit(1)

    url = sys.argv[1]
    temp_file = "temp.wsdl"

    # Descargar el archivo WSDL
    wsdl_path = descargar_wsdl(url, temp_file)
    if wsdl_path:
        root = cargar_wsdl(wsdl_path)
        if root:
            opciones = mostrar_menu()
            seleccion = int(input("\nElige una opción (1-9): "))
            if 1 <= seleccion <= 9:
                print(f"\nHas seleccionado: {opciones[seleccion - 1]}")
                if seleccion == 1:
                    listar_mensajes(root)
                elif seleccion == 2:
                    listar_operaciones(root)
                elif seleccion == 3:
                    listar_tipos(root)
                elif seleccion == 4:
                    obtener_url_servicio(root)
                elif seleccion == 5:
                    analizar_bindings(root)
                elif seleccion == 6:
                    analizar_excepciones(root)
                elif seleccion == 7:
                    mapa_relaciones(root)
                elif seleccion == 8:
                    validar_estructura(wsdl_path)
                elif seleccion == 9:
                    exportar_json(root)
            else:
                print("Opción no válida.")
        else:
            print("No se pudo analizar el archivo WSDL.")
        os.remove(temp_file)
