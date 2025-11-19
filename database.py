import sqlite3

import pandas as pd
from analysis import load_csv_into_df, normalize_dataframe


class DatabaseMigrator:
    """Clase para manejar la migración de datos desde CSV a SQLite."""

    def __init__(self, db_path: str = "freshmarket.db"):
        """
        Inicializa el migrador de base de datos.

        Args:
            db_path (str): Ruta del archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def connect(self):
        """Establece conexión con la base de datos SQLite."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # Habilitar foreign keys en SQLite
        self.cursor.execute("PRAGMA foreign_keys = ON")

    def disconnect(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        if self.cursor is None or self.conn is None:
            raise ValueError("No se ha establecido una conexión con la base de datos.")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ciudades (
                id_ciudad INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_ciudad TEXT NOT NULL UNIQUE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_producto TEXT NOT NULL UNIQUE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente TEXT PRIMARY KEY,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY,
                id_cliente TEXT NOT NULL,
                id_ciudad INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                fecha DATE NOT NULL,
                fecha_entrega DATE,
                tiempo_entrega_dias INTEGER,
                estado_entrega TEXT NOT NULL CHECK(estado_entrega IN ('Entregado', 'Retrasado', 'Cancelado', 'En tránsito')),
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
                stock_inicial INTEGER,
                stock_final INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                id_ciudad INTEGER NOT NULL,
                stock_actual INTEGER NOT NULL DEFAULT 0,
                ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
                UNIQUE(id_producto, id_ciudad)
            )
        """)

        self.conn.commit()

    def migrate_cities(self, df: pd.DataFrame) -> dict[str, int]:
        if self.cursor is None or self.conn is None:
            raise ValueError("No se ha establecido una conexión con la base de datos.")

        ciudades_unicas = df["ciudad"].unique()
        ciudad_map = {}

        for ciudad in ciudades_unicas:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO ciudades (nombre_ciudad)
                VALUES (?)
            """,
                (ciudad,),
            )

            self.cursor.execute(
                "SELECT id_ciudad FROM ciudades WHERE nombre_ciudad = ?", (ciudad,)
            )
            ciudad_map[ciudad] = self.cursor.fetchone()[0]

        self.conn.commit()
        return ciudad_map

    def migrate_products(self, df: pd.DataFrame) -> dict[str, int]:
        if self.cursor is None or self.conn is None:
            raise ValueError("No se ha establecido una conexión con la base de datos.")

        productos_unicos = df["producto"].unique()
        producto_map = {}

        for producto in productos_unicos:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO productos (nombre_producto)
                VALUES (?)
            """,
                (producto,),
            )

            self.cursor.execute(
                "SELECT id_producto FROM productos WHERE nombre_producto = ?",
                (producto,),
            )
            producto_map[producto] = self.cursor.fetchone()[0]

        self.conn.commit()
        return producto_map

    def migrate_clients(self, df: pd.DataFrame):
        if self.cursor is None or self.conn is None:
            raise ValueError("No se ha establecido una conexión con la base de datos.")

        clientes_unicos = df["cliente_id"].unique()

        for cliente in clientes_unicos:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO clientes (id_cliente)
                VALUES (?)
            """,
                (cliente,),
            )

        self.conn.commit()

    def migrate_sales(self, df: pd.DataFrame, ciudad_map: dict, producto_map: dict):
        if self.cursor is None or self.conn is None:
            raise ValueError("No se ha establecido una conexión con la base de datos.")

        for _, row in df.iterrows():
            # Calcular fecha de entrega
            fecha = row["fecha"]
            fecha_entrega = row["fecha_entrega"]

            # Insertar venta con datos del producto
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO ventas
                (id_venta, id_cliente, id_ciudad, id_producto, fecha, fecha_entrega,
                 tiempo_entrega_dias, estado_entrega, cantidad, precio_unitario,
                 stock_inicial, stock_final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    int(row["id_venta"]),
                    str(row["cliente_id"]),
                    ciudad_map[row["ciudad"]],
                    producto_map[row["producto"]],
                    fecha.strftime("%Y-%m-%d"),
                    fecha_entrega.strftime("%Y-%m-%d"),
                    int(row["tiempo_entrega_dias"]),
                    row["estado_entrega"],
                    int(row["cantidad"]),
                    float(row["precio_unitario"]),
                    int(row["stock_inicial_producto"]),
                    int(row["stock_final_producto"]),
                ),
            )

        self.conn.commit()

    def initialize_inventory(
        self, df: pd.DataFrame, ciudad_map: dict, producto_map: dict
    ):
        if self.cursor is None or self.conn is None:
            raise ValueError("Database connection is not initialized.")

        df_sorted = df.sort_values("fecha", ascending=False)

        # Agrupar por ciudad y producto, tomar el stock final más reciente
        ultimo_stock = df_sorted.groupby(["ciudad", "producto"]).first().reset_index()

        for _, row in ultimo_stock.iterrows():
            id_ciudad = ciudad_map[row["ciudad"]]
            id_producto = producto_map[row["producto"]]
            stock_actual = int(row["stock_final_producto"])

            self.cursor.execute(
                """
                INSERT OR REPLACE INTO inventario
                (id_producto, id_ciudad, stock_actual)
                VALUES (?, ?, ?)
            """,
                (id_producto, id_ciudad, stock_actual),
            )

        self.conn.commit()

    def migrate(self, csv_path: str):
        try:
            print("INICIANDO MIGRACIÓN DE DATOS")

            # Conectar a la base de datos
            self.connect()

            # Crear tablas
            self.create_tables()

            # Cargar CSV
            df = load_csv_into_df(csv_path)

            clean_df = normalize_dataframe(df)

            # Migrar datos
            ciudad_map = self.migrate_cities(clean_df)
            producto_map = self.migrate_products(clean_df)
            self.migrate_clients(clean_df)
            self.migrate_sales(clean_df, ciudad_map, producto_map)
            self.initialize_inventory(clean_df, ciudad_map, producto_map)

            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")

        except Exception as e:
            print(f"ERROR DURANTE LA MIGRACIÓN: {e}")
            if self.conn:
                self.conn.rollback()
            raise

        finally:
            self.disconnect()


def orchestrate_database_migration():
    migrator = DatabaseMigrator()
    migrator.migrate("ventas_pedidos_500.csv")
