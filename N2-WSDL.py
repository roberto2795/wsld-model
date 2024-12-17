import xml.etree.ElementTree as ET
import requests
import sys
import os
import json

def descargar_archivo(url, archivo_destino):
    """
    Descarga un archivo desde una URL y lo guarda localmente.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(archivo_destino, "wb") as file:
            file.write(response.content)
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
        sys.exit(1)

def analizar_schema(schema_path, messages):
    """
    Analiza el esquema XSD y agrega información de complexType a los mensajes.
    """
    try:
        tree = ET.parse(schema_path)
        root = tree.getroot()
        ns = {"xs": "http://www.w3.org/2001/XMLSchema"}

        complex_types = {}
        complex_type_names = []
        imported_elements = []

        # Procesar complexType
        for complex_type in root.findall(".//xs:complexType", ns):
            name = complex_type.attrib.get("name")
            elements = []
            sequence = complex_type.find("xs:sequence", ns)
            if sequence is not None:
                for element in sequence.findall("xs:element", ns):
                    elements.append({
                        "name": element.attrib.get("name"),
                        "type": element.attrib.get("type")
                    })
            if name:
                complex_types[name] = elements
                complex_type_names.append(name)

        # Procesar xs:import para extraer elementos adicionales
        for imp in root.findall(".//xs:import", ns):
            import_location = imp.attrib.get("schemaLocation")
            if import_location:
                temp_import_schema = "temp_import_schema.xsd"
                import_path = descargar_archivo(import_location, temp_import_schema)
                imported_elements += analizar_imported_schema(import_path)
                os.remove(import_path)

        # Relacionar complexType con los mensajes
        for message in messages:
            for part in message["parts"]:
                element_name = part.get("element")
                if element_name and ":" in element_name:
                    type_name = element_name.split(":")[1]
                    if type_name in complex_types:
                        part["complexType"] = complex_types[type_name]

        return complex_type_names, imported_elements

    except ET.ParseError as e:
        print(f"Error al analizar el esquema: {e}")
        sys.exit(1)

def analizar_imported_schema(import_path):
    """
    Analiza un esquema XSD importado y extrae los elementos name.
    """
    try:
        tree = ET.parse(import_path)
        root = tree.getroot()
        ns = {"xs": "http://www.w3.org/2001/XMLSchema"}

        imported_elements = []
        for element in root.findall(".//xs:element", ns):
            element_name = element.attrib.get("name")
            if element_name:
                imported_elements.append(element_name)

        return imported_elements
    except ET.ParseError as e:
        print(f"Error al analizar el esquema importado: {e}")
        sys.exit(1)

def analizar_wsdl(file_path):
    """
    Analiza el archivo WSDL y extrae los datos especificados.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "soap": "http://schemas.xmlsoap.org/wsdl/soap/",
            "xsd": "http://www.w3.org/2001/XMLSchema"
        }

        datos_wsdl = {}
        service_name = root.attrib.get("name", "UnnamedService")
        datos_wsdl["service_name"] = service_name

        schema = root.find(".//xsd:schema", ns)
        schema_location = None
        if schema is not None:
            datos_wsdl["target_namespace"] = schema.attrib.get("targetNamespace")
            include = schema.find("xsd:include", ns)
            if include is not None:
                schema_location = include.attrib.get("schemaLocation")
                datos_wsdl["schema_location"] = schema_location

        mensajes = []
        message_names = []
        for message in root.findall("wsdl:message", ns):
            name = message.attrib.get("name")
            mensaje = {"name": name, "parts": []}
            message_names.append(name)
            for part in message.findall("wsdl:part", ns):
                mensaje["parts"].append({
                    "name": part.attrib.get("name"),
                    "element": part.attrib.get("element")
                })
            mensajes.append(mensaje)
        datos_wsdl["messages"] = mensajes

        return service_name, datos_wsdl, schema_location, mensajes, message_names
    except ET.ParseError as e:
        print(f"Error al analizar el archivo WSDL: {e}")
        sys.exit(1)

def guardar_json(data, service_name):
    """
    Guarda los datos extraídos en un archivo JSON estructurado.
    """
    folder = "N1-WSDL"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.abspath(os.path.join(folder, f"{service_name}_N1-WSDL.json"))
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    return file_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso: python script.py <url_wsdl>")
        sys.exit(1)

    url = sys.argv[1]
    temp_wsdl = "temp.wsdl"

    wsdl_path = descargar_archivo(url, temp_wsdl)
    service_name, datos_wsdl, schema_location, messages, message_names = analizar_wsdl(wsdl_path)

    complex_type_names = []
    imported_elements = []
    if schema_location:
        temp_schema = "temp_schema.xsd"
        schema_path = descargar_archivo(schema_location, temp_schema)
        complex_type_names, imported_elements = analizar_schema(schema_path, messages)
        os.remove(schema_path)

    # Identificar coincidencias entre mensajes y complexTypes
    matching_names = list(set(message_names) & set(complex_type_names))

    # Agregar elementos importados al JSON
    datos_wsdl["imported_elements"] = imported_elements

    # Imprimir las tres listas
    print("\nLista de nombres de mensajes:")
    print(message_names)
    print("\nLista de nombres de complexType:")
    print(complex_type_names)
    print("\nLista de nombres coincidentes:")
    print(matching_names)
    print("\nLista de elementos importados:")
    print(imported_elements)

    output_path = guardar_json(datos_wsdl, service_name)
    os.remove(wsdl_path)

    # Mostrar salida final
    print(f"\nArchivo JSON generado: {output_path}")
