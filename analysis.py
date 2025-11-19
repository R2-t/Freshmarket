"""
Análisis de Ventas y Logística - Fresh Market
==============================================

Este módulo realiza un análisis completo de ventas y logística para Fresh Market,
incluyendo productos más vendidos, problemas de entrega y tasas de éxito por ciudad.

"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_csv_into_df(file_name: str) -> pd.DataFrame:
    """
    Carga un archivo CSV en un DataFrame de pandas.

    Args:
        file_name (str): Nombre del archivo CSV a cargar

    Returns:
        pd.DataFrame: DataFrame con los datos del CSV

    Ejemplo:
        >>> df = load_csv_into_df("ventas_pedidos_500.csv")
    """
    return pd.read_csv(Path.cwd() / file_name)


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza y limpia el DataFrame de ventas.

    Realiza las siguientes transformaciones:
    - Convierte el campo 'fecha' a tipo datetime
    - Calcula la fecha de entrega basada en días de entrega
    - Calcula el ingreso total (cantidad × precio unitario)
    - Elimina filas con valores faltantes

    Args:
        df (pd.DataFrame): DataFrame con datos crudos de ventas

    Returns:
        pd.DataFrame: DataFrame normalizado y limpio

    Columnas requeridas:
        - fecha: Fecha del pedido
        - tiempo_entrega_dias: Días hasta la entrega
        - cantidad: Cantidad de productos
        - precio_unitario: Precio por unidad
    """
    # Convertir campos de texto a campos de tipo fecha
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Calcular fecha de entrega
    df["fecha_entrega"] = df["fecha"] + pd.to_timedelta(
        df["tiempo_entrega_dias"], unit="D"
    )

    # Calcular ingreso total
    df["ingreso_total"] = df["cantidad"] * df["precio_unitario"]

    # Retornar dataset con datos limpios (sin valores nulos)
    return df.dropna()


def most_sold_product_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica el producto más vendido en cada ciudad.

    Agrupa las ventas por ciudad y producto, luego selecciona el producto
    con mayor cantidad vendida en cada ciudad.

    Args:
        df (pd.DataFrame): DataFrame normalizado de ventas

    Returns:
        pd.DataFrame: DataFrame con columnas [ciudad, producto, cantidad]
                      mostrando el producto más vendido por ciudad

    Ejemplo de salida:
        ciudad    producto           cantidad
        Bogotá    Frutas Orgánicas   150
        Cali      Leche Vegetal      120
        Medellín  Granola            180
    """
    # Agrupar por ciudad y producto, luego sumar cantidades
    sales_by_city_product = (
        df.groupby(["ciudad", "producto"])["cantidad"].sum().reset_index()
    )

    # Retornar el producto con mayor cantidad por ciudad
    return sales_by_city_product.loc[
        sales_by_city_product.groupby("ciudad")["cantidad"].idxmax()
    ]


def higher_product_delay_or_cancelled(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica productos con mayor número de retrasos o cancelaciones.

    Filtra las órdenes con estado "Retrasado" o "Cancelado" y cuenta
    cuántas veces aparece cada producto con estos problemas.

    Args:
        df (pd.DataFrame): DataFrame normalizado de ventas

    Returns:
        pd.DataFrame: DataFrame con columnas [producto, cantidad_ordenes]
                      ordenado por número de órdenes problemáticas

    Ejemplo de salida:
        producto              cantidad_ordenes
        Granola               21
        Leche Vegetal         20
        Frutas Orgánicas      17
    """
    # Filtrar órdenes retrasadas o canceladas y contar por producto
    return (
        df[df["estado_entrega"].isin(["Retrasado", "Cancelado"])]
        .groupby("producto")
        .size()
        .reset_index(name="cantidad_ordenes")
    )


def successful_logistic_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el porcentaje de éxito logístico por ciudad.

    Determina qué porcentaje de órdenes fue entregado exitosamente
    en cada ciudad (estado "Entregado").

    Args:
        df (pd.DataFrame): DataFrame normalizado de ventas

    Returns:
        pd.DataFrame: DataFrame con columnas:
                      - ciudad: Nombre de la ciudad
                      - total_ordenes: Número total de órdenes
                      - ordenes_exitosas: Número de órdenes entregadas
                      - porcentaje_exitoso: Porcentaje de éxito (0-100)

    Ejemplo de salida:
        ciudad    total_ordenes  ordenes_exitosas  porcentaje_exitoso
        Bogotá    150           120                80.0
        Cali      120           100                83.33
        Medellín  180           140                77.78
    """
    # Agrupar por ciudad y calcular estadísticas de éxito
    success_stats = (
        df.groupby("ciudad")
        .agg(
            total_ordenes=pd.NamedAgg(column="id_venta", aggfunc="count"),
            ordenes_exitosas=pd.NamedAgg(
                column="estado_entrega", aggfunc=lambda x: (x == "Entregado").sum()
            ),
        )
        .reset_index()
    )

    # Calcular porcentaje de éxito
    success_stats["porcentaje_exitoso"] = (
        success_stats["ordenes_exitosas"] / success_stats["total_ordenes"] * 100
    )

    return success_stats


def orchestrate_analysis():
    """
    Orquesta el análisis completo de ventas y logística.

    Esta función:
    1. Carga los datos desde el archivo CSV
    2. Normaliza y limpia los datos
    3. Genera tres análisis principales:
       - Productos más vendidos por ciudad
       - Productos con mayor retraso o cancelación
       - Porcentaje de éxito logístico por ciudad
    4. Guarda los resultados en archivos CSV
    5. Genera visualizaciones en un gráfico combinado

    Archivos generados:
        - reportes/productos_mas_vendidos_por_ciudad.csv
        - reportes/productos_con_mayor_retraso_o_cancelacion.csv
        - reportes/logistica_exito_por_ciudad.csv
        - reportes/analisis_ventas_completo.png

    Raises:
        FileNotFoundError: Si no se encuentra el archivo ventas_pedidos_500.csv
    """
    # Cargar datos desde CSV
    ventas_pedidos = load_csv_into_df("ventas_pedidos_500.csv")

    # Normalizar y limpiar datos
    normalizada_ventas_pedidos = normalize_dataframe(ventas_pedidos)

    # Crear directorio de salida para reportes
    output_dir = Path(Path.cwd() / "reportes")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Análisis 1: Productos más vendidos por ciudad
    productos_mas_vendidos = most_sold_product_by_city(normalizada_ventas_pedidos)
    productos_mas_vendidos.to_csv(
        output_dir / "productos_mas_vendidos_por_ciudad.csv", index=False
    )

    # Análisis 2: Productos con mayor retraso o cancelación
    productos_con_mayor_retraso_o_cancelacion = higher_product_delay_or_cancelled(
        normalizada_ventas_pedidos
    )
    productos_con_mayor_retraso_o_cancelacion.to_csv(
        output_dir / "productos_con_mayor_retraso_o_cancelacion.csv", index=False
    )

    # Análisis 3: Logística de éxito por ciudad
    logistica_exito_por_ciudad = successful_logistic_by_city(normalizada_ventas_pedidos)
    logistica_exito_por_ciudad.to_csv(
        output_dir / "logistica_exito_por_ciudad.csv", index=False
    )

    # Configurar el estilo de visualización
    sns.set_style("whitegrid")

    # Crear figura con 3 subplots (1 fila, 3 columnas)
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # Gráfico 1: Productos más vendidos por ciudad
    sns.barplot(
        data=productos_mas_vendidos,
        x="ciudad",
        y="cantidad",
        hue="ciudad",
        ax=axes[0],
        palette="Blues_d",
        legend=False,
    )
    axes[0].set_title(
        "Productos Más Vendidos por Ciudad", fontsize=14, fontweight="bold"
    )
    axes[0].set_ylabel("Cantidad", fontsize=12)
    axes[0].set_xlabel("Ciudad", fontsize=12)
    axes[0].tick_params(axis="x", rotation=45)

    # Gráfico 2: Productos con mayor retraso o cancelación
    # Ordenar por cantidad de órdenes problemáticas (descendente)
    productos_sorted = productos_con_mayor_retraso_o_cancelacion.sort_values(
        "cantidad_ordenes", ascending=False
    )
    sns.barplot(
        data=productos_sorted,
        x="producto",
        y="cantidad_ordenes",
        hue="producto",
        ax=axes[1],
        palette="Reds_r",
        legend=False,
    )
    axes[1].set_title(
        "Productos con Mayor Retraso o Cancelación", fontsize=14, fontweight="bold"
    )
    axes[1].set_ylabel("Cantidad de Órdenes Problemáticas", fontsize=12)
    axes[1].set_xlabel("Producto", fontsize=12)
    axes[1].tick_params(axis="x", rotation=45)

    # Gráfico 3: Logística de éxito por ciudad
    sns.barplot(
        data=logistica_exito_por_ciudad,
        x="ciudad",
        y="porcentaje_exitoso",
        hue="ciudad",
        ax=axes[2],
        palette="Greens_d",
        legend=False,
    )
    axes[2].set_title(
        "Porcentaje de Éxito Logístico por Ciudad", fontsize=14, fontweight="bold"
    )
    axes[2].set_ylabel("Porcentaje (%)", fontsize=12)
    axes[2].set_xlabel("Ciudad", fontsize=12)
    axes[2].tick_params(axis="x", rotation=45)

    # Ajustar el espaciado entre subplots
    plt.tight_layout()

    # Guardar la figura como imagen de alta resolución
    plt.savefig(
        output_dir / "analisis_ventas_completo.png", dpi=300, bbox_inches="tight"
    )

    # Mostrar la figura
    plt.show()

    print(f"Análisis completado exitosamente")
    print(f"Reportes guardados en: {output_dir}")
