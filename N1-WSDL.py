import xml.etree.ElementTree as ET
import requests
import sys
import os
import json

def descargar_wsdl(url, archivo_destino):
    """
    Descarga el archivo WSDL desde una URL y lo guarda localmente.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(archivo_destino, "wb") as file:
            file.write(response.content)
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo WSDL: {e}")
        sys.exit(1)

def imprimir_wsdl(archivo):
    """
    Imprime el contenido completo del archivo WSDL.
    """
    with open(archivo, "r", encoding="utf-8") as file:
        print(file.read())

def analizar_wsdl(file_path):
    """
    Analiza el archivo WSDL y extrae los datos especificados.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Espacio de nombres (ajustar si es necesario)
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "soap": "http://schemas.xmlsoap.org/wsdl/soap/",
            "xsd": "http://www.w3.org/2001/XMLSchema",
            "tns": "http://www.amx.com.mx/mexico/telcel/di/sds/bes/crm/esb/customermanagementservice"
        }

        # Estructura de salida JSON
        datos_wsdl = {}

        # Extraer nombre del servicio
        service_name = root.attrib.get("name", "UnnamedService")
        datos_wsdl["service_name"] = service_name

        # Extraer targetNamespace
        schema = root.find(".//xsd:schema", ns)
        if schema is not None:
            datos_wsdl["target_namespace"] = schema.attrib.get("targetNamespace")

        # Extraer xsd:include
        include = schema.find("xsd:include", ns) if schema is not None else None
        if include is not None:
            datos_wsdl["schema_location"] = include.attrib.get("schemaLocation")

        # Extraer mensajes
        mensajes = []
        for message in root.findall("wsdl:message", ns):
            mensaje = {"name": message.attrib.get("name"), "parts": []}
            for part in message.findall("wsdl:part", ns):
                mensaje["parts"].append({
                    "name": part.attrib.get("name"),
                    "element": part.attrib.get("element")
                })
            mensajes.append(mensaje)
        datos_wsdl["messages"] = mensajes

        # Extraer operaciones
        operaciones = []
        for operation in root.findall(".//wsdl:portType/wsdl:operation", ns):
            operacion = {
                "name": operation.attrib.get("name"),
                "input": None,
                "output": None,
                "fault": None
            }
            input_node = operation.find("wsdl:input", ns)
            output_node = operation.find("wsdl:output", ns)
            fault_node = operation.find("wsdl:fault", ns)
            if input_node is not None:
                operacion["input"] = input_node.attrib.get("message")
            if output_node is not None:
                operacion["output"] = output_node.attrib.get("message")
            if fault_node is not None:
                operacion["fault"] = fault_node.attrib.get("message")
            operaciones.append(operacion)
        datos_wsdl["operations"] = operaciones

        # Extraer binding
        binding = root.find(".//wsdl:binding", ns)
        if binding is not None:
            datos_wsdl["binding"] = binding.attrib.get("name")

        # Extraer servicios
        servicios = []
        for service in root.findall("wsdl:service", ns):
            servicio = {
                "name": service.attrib.get("name"),
                "ports": []
            }
            for port in service.findall("wsdl:port", ns):
                port_data = {
                    "name": port.attrib.get("name"),
                    "binding": port.attrib.get("binding"),
                    "address": None
                }
                address = port.find("soap:address", ns)
                if address is not None:
                    port_data["address"] = address.attrib.get("location")
                servicio["ports"].append(port_data)
            servicios.append(servicio)
        datos_wsdl["services"] = servicios

        return service_name, datos_wsdl

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

def imprimir_instrucciones():
    """
    Imprime las instrucciones del script.
    """
    print("\nUso: python script.py <url_wsdl> [opción]")
    print("- <url_wsdl>: URL del archivo WSDL.")
    print("- [opción]: Opcional. Controla lo que se imprime.")
    print("  0: Imprime solo el contenido del WSDL.")
    print("  1: Imprime solo el JSON generado.")
    print("  2: Imprime tanto el WSDL como el JSON.")
    print("  Default: No imprime nada adicional.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        imprimir_instrucciones()
        sys.exit(1)

    # Leer parámetros de entrada
    url = sys.argv[1]
    opcion = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else -1

    # Validar la opción
    if opcion not in [-1, 0, 1, 2]:
        imprimir_instrucciones()
        print("\nSe han utilizado valores por defecto (no imprime WSDL ni JSON).\n")
        opcion = -1  # Valor predeterminado

    temp_file = "temp.wsdl"

    # Descargar el archivo WSDL
    wsdl_path = descargar_wsdl(url, temp_file)

    # Analizar el archivo WSDL
    service_name, datos_wsdl = analizar_wsdl(wsdl_path)

    # Guardar datos en JSON
    output_path = guardar_json(datos_wsdl, service_name)

    # Imprimir según la opción
    if opcion == 0:
        imprimir_wsdl(wsdl_path)
    elif opcion == 1:
        print("\nJSON Generado:")
        print(json.dumps(datos_wsdl, indent=4, ensure_ascii=False))
    elif opcion == 2:
        imprimir_wsdl(wsdl_path)
        print("\nJSON Generado:")
        print(json.dumps(datos_wsdl, indent=4, ensure_ascii=False))

    # Eliminar archivo temporal
    os.remove(wsdl_path)

    # Mostrar ruta absoluta del archivo JSON generado
    print(f"\nArchivo JSON generado: {output_path}")
