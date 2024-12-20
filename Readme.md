# Proyecto: DocExtractor

## Introducción
**DocExtractor** es una herramienta diseñada para automatizar la extracción, análisis y organización de datos estructurados desde archivos WSDL (Web Services Description Language). Este proyecto facilita el procesamiento de datos en formato XML, generando salidas en JSON listas para integrarse con otros sistemas y flujos de trabajo.

---

## Características Principales
- Descarga de archivos WSDL desde una URL.
- Extracción de información clave como mensajes, operaciones, binding y servicios.
- Análisis de esquemas XSD asociados para identificar tipos complejos.
- Generación de un archivo JSON estructurado con los datos procesados.
- Modularidad mediante la integración de scripts específicos.

---

## Requisitos Previos
Asegúrate de tener instalado:
- **Python 3.8 o superior.**
- Las siguientes librerías de Python:
  - `requests`
  - `xml.etree.ElementTree`
  - `os`
  - `sys`
  - `json`

Puedes instalar las dependencias ejecutando:
```bash
pip install -r requirements.txt
```

---

## Estructura del Proyecto
```plaintext
.
├── src
│   ├── N2-WSDL.py
│   ├── json_structure_converter.py
│   ├── main.py
├── README.md
├── requirements.txt
└── outputs
    └── <Archivos JSON generados>
```

---

## Configuración Inicial
1. Clona el repositorio:
   ```bash
   git clone <url_del_repositorio>
   cd DocExtractor
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Crea las carpetas necesarias:
   ```bash
   mkdir outputs
   ```

---

## Ejecución del Proyecto

### Paso 1: Descargar y analizar un archivo WSDL
Ejecuta el script principal para descargar y analizar un archivo WSDL:
```bash
python src/main.py <url_wsdl>
```
**Parámetros:**
- `<url_wsdl>`: La URL del archivo WSDL a analizar.

Ejemplo:
```bash
python src/main.py https://example.com/service.wsdl
```

### Paso 2: Procesar esquemas XSD asociados
Si el WSDL incluye referencias a esquemas externos, el script los descargará y procesará automáticamente.

### Paso 3: Generación del archivo JSON
Una vez procesado el archivo WSDL, se generará un archivo JSON estructurado en la carpeta `outputs`. Este archivo incluirá:
- Mensajes y partes asociadas.
- Operaciones y sus relaciones input-output.
- Tipos complejos definidos en esquemas.

---

## Estructura del JSON
El archivo JSON generado tendrá la siguiente estructura:
```json
{
    "service_name": "Nombre del Servicio",
    "target_namespace": "Espacio de nombres del esquema",
    "schema_location": "URL del esquema incluido",
    "messages": [
        {
            "name": "Nombre del mensaje",
            "parts": [
                {
                    "name": "Nombre de la parte",
                    "element": "Elemento asociado"
                },
                {
                    "complexType": [
                        {
                            "name": "Nombre del elemento",
                            "type": "Tipo del elemento"
                        }
                    ]
                }
            ]
        }
    ],
    "operations": [
        {
            "name": "Nombre de la operación",
            "input": "Mensaje de entrada",
            "output": "Mensaje de salida",
            "fault": "Mensaje de error"
        }
    ],
    "binding": "Nombre del binding",
    "services": [
        {
            "name": "Nombre del servicio",
            "ports": [
                {
                    "name": "Nombre del puerto",
                    "binding": "Binding asociado",
                    "address": "URL del servicio"
                }
            ]
        }
    ]
}
```

---

## Scripts y Funcionalidades
1. **`N2-WSDL.py`:** Procesa el archivo WSDL y extrae datos clave como mensajes, operaciones y binding.
2. **`json_structure_converter.py`:** Convierte los datos extraídos a una estructura JSON estandarizada.
3. **`main.py`:** Orquesta la ejecución de los scripts y garantiza el flujo correcto.

---

## Contribución
Si deseas contribuir al proyecto:
1. Haz un fork del repositorio.
2. Crea una rama para tus cambios:
   ```bash
   git checkout -b feature/nueva_funcionalidad
   ```
3. Realiza un pull request con tus mejoras.

---

## Contacto
Para cualquier duda o sugerencia, por favor contacta a:
- **Nombre del desarrollador:** Roberto Flores
- **Correo:** roberto.fls.acs@gmail.com

---

## Licencia
Este proyecto está bajo la licencia MIT. Para más información, revisa el archivo `LICENSE` incluido en este repositorio.
