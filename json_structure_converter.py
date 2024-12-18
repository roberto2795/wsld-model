import os
import json
import sys

def reorganizar_json(ruta_json):
    """
    Reorganiza un archivo JSON en una estructura específica y lo guarda en una nueva carpeta.

    Argumentos:
        ruta_json (str): Ruta al archivo JSON original.

    Retorno:
        str: Ruta absoluta del archivo JSON generado.
    """
    # Leer el archivo JSON original
    with open(ruta_json, "r", encoding="utf-8") as archivo:
        datos_originales = json.load(archivo)

    # Crear la estructura requerida
    estructura = {
        "control": {
            "service_name": datos_originales.get("service_name")
        },
        "metadatos": {},  # Puedes agregar más lógica si es necesario
        "datos": {
            k: v for k, v in datos_originales.items() if k != "service_name"
        }
    }

    # Crear la carpeta de salida si no existe
    carpeta_salida = "N1-WSDL"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Generar el nombre del nuevo archivo
    nombre_original = os.path.basename(ruta_json)
    nuevo_nombre = f"modelo-datos-{nombre_original}"
    ruta_salida = os.path.join(carpeta_salida, nuevo_nombre)

    # Guardar el nuevo archivo JSON
    with open(ruta_salida, "w", encoding="utf-8") as archivo_salida:
        json.dump(estructura, archivo_salida, indent=4, ensure_ascii=False)

    # Imprimir y retornar la ruta absoluta del archivo generado
    ruta_absoluta = os.path.abspath(ruta_salida)
    print(f"Archivo JSON generado: {ruta_absoluta}")
    return ruta_absoluta

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <ruta_json>")
        sys.exit(1)

    # Obtener la ruta del JSON desde los argumentos
    ruta_json = sys.argv[1]

    if not os.path.exists(ruta_json):
        print("El archivo JSON especificado no existe.")
    else:
        reorganizar_json(ruta_json)
