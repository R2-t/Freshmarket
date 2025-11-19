# 📊 Análisis de Ventas y Logística - Fresh Market

Sistema de análisis de datos para evaluar el desempeño de ventas y logística de Fresh Market, incluyendo identificación de productos más vendidos, problemas de entrega y tasas de éxito por ciudad.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura de Datos](#estructura-de-datos)

## 📖 Descripción

Este proyecto analiza datos de ventas y entregas de Fresh Market para proporcionar insights sobre:

- **Rendimiento por ciudad**: Identifica qué productos son más populares en cada ubicación
- **Problemas logísticos**: Detecta productos con mayor tasa de retrasos y cancelaciones
- **Eficiencia de entrega**: Calcula el porcentaje de entregas exitosas por ciudad

## ⚡ Inicio Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar análisis
python main.py analysis

# 3. Ver resultados
# Los reportes estarán en la carpeta reportes/
```

## 🔧 Requisitos

### Software

- Python 3.8 o superior

### Librerías

```
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.13.0
```

3. **Instalar las dependencias**

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Ejecución Básica

1. Asegúrate de tener el archivo `ventas_pedidos_500.csv` en el directorio raíz del proyecto

2. Ejecuta el script principal con el comando deseado:

```bash
python main.py analysis
```

3. Los resultados se generarán en el directorio `reportes/`

### Comandos Disponibles

```bash
# Ejecutar análisis de ventas y logística
python main.py analysis

# Operaciones de base de datos (próximamente)
python main.py database

# Interfaz de usuario (próximamente)
python main.py ui
```

**Nota**: Si ejecutas `main.py` sin argumentos, verás un mensaje de ayuda:

```bash
python main.py
# Output: No arguments provided
#         functionality: python main.py <command>
```
## 📊 Estructura de Datos

### Archivo de Entrada: `ventas_pedidos_500.csv`

El archivo CSV debe contener las siguientes columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_venta` | int | Identificador único de la venta |
| `fecha` | string | Fecha de la orden (formato: YYYY-MM-DD) |
| `ciudad` | string | Ciudad donde se realizó la venta |
| `producto` | string | Nombre del producto |
| `cantidad` | int | Cantidad de productos vendidos |
| `precio_unitario` | float | Precio por unidad del producto |
| `cliente_id` | int | Identificador del cliente |
| `tiempo_entrega_dias` | int | Días estimados de entrega |
| `estado_entrega` | string | Estado: "Entregado", "Retrasado", "Cancelado" |
| `stock_inicial_producto` | int | Stock inicial del producto |
| `stock_final_producto` | int | Stock final del producto |
