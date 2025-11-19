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

# Operaciones de base de datos
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

### Descripción de Comandos

| Comando | Estado | Descripción |
|---------|--------|-------------|
| `analysis` | ✅ Activo | Genera reportes CSV y visualizaciones de ventas |
| `database` | ✅ Activo | Migra datos a SQLite con estructura normalizada |
| `ui` | 🚧 Próximamente | Interfaz de usuario interactiva |

#### 📊 Comando `analysis`

Ejecuta el análisis completo de ventas y logística, generando:

**Archivos CSV:**
- `productos_mas_vendidos_por_ciudad.csv` - Top producto por ciudad
- `productos_con_mayor_retraso_o_cancelacion.csv` - Productos problemáticos
- `logistica_exito_por_ciudad.csv` - Tasa de entregas exitosas

**Visualizaciones:**
- `analisis_ventas_completo.png` - Dashboard con 3 gráficos combinados

```bash
python main.py analysis
# Genera archivos en: reportes/
```

#### 🗄️ Comando `database`

Crea una base de datos SQLite normalizada (3NF) con la siguiente estructura:

**Tablas creadas (5):**

| Tabla | Descripción | Registros Típicos |
|-------|-------------|-------------------|
| `ciudades` | Catálogo de ciudades | 3-10 |
| `productos` | Catálogo de productos | 10-100 |
| `clientes` | Información de clientes (id como TEXT) | 100-1000 |
| `ventas` | Transacciones (fusionada con detalle) | 500-10000 |
| `inventario` | Stock actual por ciudad/producto | 30-300 |

**Características:**
- ✅ Estructura normalizada (elimina redundancia)
- ✅ Foreign keys con integridad referencial
- ✅ Campo `subtotal` calculado automáticamente
- ✅ `cliente_id` como TEXT (acepta alfanuméricos)
- ✅ Inventario por ciudad y producto


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

### Detalles de las Tablas

#### 1. **ciudades**
```sql
CREATE TABLE ciudades (
    id_ciudad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_ciudad TEXT NOT NULL UNIQUE
);
```
- Catálogo normalizado de ciudades
- Elimina redundancia de nombres repetidos

#### 2. **productos**
```sql
CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT NOT NULL UNIQUE
);
```
- Catálogo de productos
- Precios se almacenan en cada venta

#### 3. **clientes**
```sql
CREATE TABLE clientes (
    id_cliente TEXT PRIMARY KEY
);
```
- **Nota**: `id_cliente` es TEXT para aceptar IDs alfanuméricos
- Extensible para agregar más campos en el futuro

#### 4. **ventas** (fusionada con detalle)
```sql
CREATE TABLE ventas (
    id_venta INTEGER PRIMARY KEY,
    id_cliente TEXT NOT NULL,
    id_ciudad INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    fecha DATE NOT NULL,
    fecha_entrega DATE,
    tiempo_entrega_dias INTEGER,
    estado_entrega TEXT CHECK(...),
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    subtotal REAL GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    stock_inicial INTEGER,
    stock_final INTEGER,

    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
```
- **Simplificación**: Una venta = Un producto (no hay tabla separada de detalles)
- Campo `subtotal` calculado automáticamente
- Incluye snapshot del stock al momento de la venta

#### 5. **inventario**
```sql
CREATE TABLE inventario (
    id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_ciudad INTEGER NOT NULL,
    stock_actual INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
    UNIQUE(id_producto, id_ciudad)
);
```
- Stock actual por combinación producto-ciudad
- Se inicializa con el `stock_final` más reciente de las ventas

### Diagrama de Relaciones

```
ciudades ──┐
           ├──► ventas ◄── productos
clientes ──┘      │
                  ▼
             inventario
```
