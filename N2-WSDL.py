import xml.etree.ElementTree as ET
import requests
import sys
import os
import json

def descargar_archivo(url, archivo_destino):
    """ Descarga un archivo desde una URL y lo guarda localmente. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(archivo_destino, "wb") as file:
            file.write(response.content)
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
        sys.exit(1)

def analizar_schema(schema_path):
    """ Analiza el XSD y devuelve todos los complexType. """
    try:
        tree = ET.parse(schema_path)
        root = tree.getroot()
        ns = {"xs": "http://www.w3.org/2001/XMLSchema"}

        complex_types = {}
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
            complex_types[name] = elements
        return complex_types
    except ET.ParseError as e:
        print(f"Error al analizar el esquema: {e}")
        sys.exit(1)

def analizar_wsdl(file_path):
    """ Analiza el WSDL y extrae detalles del servicio, mensajes y operaciones. """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "soap": "http://schemas.xmlsoap.org/wsdl/soap/",
            "xsd": "http://www.w3.org/2001/XMLSchema"
        }

        data = {
            "service_name": root.attrib.get("name"),
            "target_namespace": root.find(".//xsd:schema", ns).attrib.get("targetNamespace", ""),
            "schema_location": root.find(".//xsd:schema/xsd:include", ns).attrib.get("schemaLocation", ""),
            "messages": [],
            "operations": [],
            "services": [],
            "binding": None
        }

        # Extraer mensajes
        for message in root.findall("wsdl:message", ns):
            message_name = message.attrib.get("name")
            parts = []
            for part in message.findall("wsdl:part", ns):
                parts.append({
                    "name": part.attrib.get("name"),
                    "element": part.attrib.get("element")
                })
            data["messages"].append({"name": message_name, "parts": parts})

        # Extraer operaciones
        for operation in root.findall(".//wsdl:portType/wsdl:operation", ns):
            data["operations"].append({
                "name": operation.attrib.get("name"),
                "input": operation.find("wsdl:input", ns).attrib.get("message"),
                "output": operation.find("wsdl:output", ns).attrib.get("message"),
                "fault": operation.find("wsdl:fault", ns).attrib.get("message")
            })

        # Extraer binding
        binding = root.find(".//wsdl:binding", ns)
        if binding is not None:
            data["binding"] = binding.attrib.get("name")

        # Extraer servicios y puertos
        for service in root.findall("wsdl:service", ns):
            ports = []
            for port in service.findall("wsdl:port", ns):
                address = port.find("soap:address", ns)
                ports.append({
                    "name": port.attrib.get("name"),
                    "binding": port.attrib.get("binding"),
                    "address": address.attrib.get("location") if address is not None else None
                })
            data["services"].append({
                "name": service.attrib.get("name"),
                "ports": ports
            })

        return data
    except ET.ParseError as e:
        print(f"Error al analizar el WSDL: {e}")
        sys.exit(1)

def anidar_complex_type(messages, complex_types):
    """ Anida el ComplexType correspondiente dentro de cada part en messages. """
    for message in messages:
        for part in message["parts"]:
            element_name = part.get("element", "").split(":")[-1]
            complex_type_name = element_name[0].upper() + element_name[1:]  # Capitalizar
            if complex_type_name in complex_types:
                part["ComplexType"] = complex_types[complex_type_name]
    return messages

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso: python script.py <url_wsdl>")
        sys.exit(1)

    url = sys.argv[1]
    temp_wsdl = "temp.wsdl"

    # Descargar y analizar el WSDL
    wsdl_path = descargar_archivo(url, temp_wsdl)
    wsdl_data = analizar_wsdl(wsdl_path)

    # Descargar y analizar el esquema XSD si existe
    if wsdl_data["schema_location"]:
        temp_schema = "temp_schema.xsd"
        schema_path = descargar_archivo(wsdl_data["schema_location"], temp_schema)
        complex_types = analizar_schema(schema_path)
        wsdl_data["messages"] = anidar_complex_type(wsdl_data["messages"], complex_types)
        os.remove(temp_schema)

    # Crear carpeta N1-WSDL si no existe
    output_folder = "N1-WSDL"
    os.makedirs(output_folder, exist_ok=True)

    # Nombre del archivo JSON
    file_name = f"{wsdl_data['service_name']}_N1-WSDL.json"
    output_path = os.path.abspath(os.path.join(output_folder, file_name))

    # Guardar salida JSON
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(wsdl_data, file, indent=4, ensure_ascii=False)

    os.remove(temp_wsdl)
    print(output_path)
