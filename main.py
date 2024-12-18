import os
import subprocess
import sys

def ejecutar_n2_wsdl(url_wsdl):
    """
    Ejecuta el script N2-WSDL para generar el primer archivo JSON.

    Argumentos:
        url_wsdl (str): URL del archivo WSDL.

    Retorno:
        str: Ruta del archivo JSON generado por N2-WSDL.
    """
    print("Ejecutando N2-WSDL...")
    resultado = subprocess.run(
        [sys.executable, "N2-WSDL.py", url_wsdl], capture_output=True, text=True
    )

    if resultado.returncode != 0:
        print("Error ejecutando N2-WSDL:")
        print(resultado.stderr)
        sys.exit(1)

    # Extraer la última línea de la salida que contiene la ruta
    ruta_json = resultado.stdout.strip().splitlines()[-1]
    print(f"Archivo JSON generado por N2-WSDL: {ruta_json}")
    return ruta_json

def ejecutar_reorganizador(ruta_json):
    """
    Ejecuta el script de reorganización para procesar el archivo JSON generado por N2-WSDL.

    Argumentos:
        ruta_json (str): Ruta del archivo JSON generado por N2-WSDL.

    Retorno:
        str: Ruta del archivo JSON reorganizado.
    """
    print("Ejecutando el reorganizador de JSON...")
    resultado = subprocess.run(
        [sys.executable, "json_structure_converter.py", ruta_json], capture_output=True, text=True
    )

    if resultado.returncode != 0:
        print("Error ejecutando el reorganizador de JSON:")
        print(resultado.stderr)
        sys.exit(1)

    # Extraer la última línea de la salida que contiene la ruta
    ruta_reorganizada = resultado.stdout.strip().splitlines()[-1]
    print(f"Archivo JSON reorganizado: {ruta_reorganizada}")
    return ruta_reorganizada

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <url_wsdl>")
        sys.exit(1)

    url_wsdl = sys.argv[1]

    # Ejecutar el flujo de scripts
    ruta_json_n2_wsdl = ejecutar_n2_wsdl(url_wsdl)
    ruta_json_reorganizado = ejecutar_reorganizador(ruta_json_n2_wsdl)

    print("\nFlujo completado con éxito.")
    print(f"Archivo final generado: {ruta_json_reorganizado}")
