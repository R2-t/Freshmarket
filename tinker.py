"""
Fresh Market - Aplicación de Escritorio
=========================================

Aplicación Tkinter para gestión de pedidos y control de inventario.
Diseñada para uso interno en la sede administrativa.

Funcionalidades:
- Registro manual de nuevos pedidos
- Consulta de disponibilidad de productos
- Alertas automáticas de stock bajo
- Visualización de inventario en tiempo real

Autor: Santiago Torres
Fecha: Noviembre 2024
"""

import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, scrolledtext, ttk
from typing import List, Optional, Tuple

import pandas as pd


class FreshMarketApp:
    """Aplicación principal de Fresh Market."""

    def __init__(self, root: tk.Tk, db_path: str = "freshmarket.db"):
        """
        Inicializa la aplicación.

        Args:
            root: Ventana principal de Tkinter
            db_path: Ruta a la base de datos SQLite
        """
        self.root = root
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

        # Configurar ventana principal
        self.root.title("Fresh Market - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Estilos
        self.setup_styles()

        # Verificar conexión a la base de datos
        if not self.connect_db():
            messagebox.showerror(
                "Error de Base de Datos",
                "No se pudo conectar a la base de datos.\n"
                "Ejecuta primero: python main.py database",
            )
            self.root.quit()
            return

        # Crear interfaz
        self.create_widgets()

        # Cargar datos iniciales
        self.load_initial_data()

        # Verificar alertas de stock
        self.check_stock_alerts()

    def setup_styles(self):
        """Configura los estilos de la aplicación."""
        style = ttk.Style()
        style.theme_use("clam")

        # Colores principales
        self.colors = {
            "primary": "#2ecc71",
            "secondary": "#3498db",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "dark": "#34495e",
            "light": "#ecf0f1",
            "white": "#ffffff",
        }

        # Estilos personalizados
        style.configure(
            "Title.TLabel", font=("Arial", 16, "bold"), foreground=self.colors["dark"]
        )
        style.configure(
            "Header.TLabel", font=("Arial", 12, "bold"), foreground=self.colors["dark"]
        )
        style.configure("Success.TButton", background=self.colors["primary"])
        style.configure("Danger.TButton", background=self.colors["danger"])

    def connect_db(self) -> bool:
        """
        Conecta a la base de datos SQLite.

        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Marco principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña 1: Nuevo Pedido
        self.tab_nuevo_pedido = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_nuevo_pedido, text="📝 Nuevo Pedido")
        self.create_nuevo_pedido_tab()

        # Pestaña 2: Disponibilidad de Productos
        self.tab_disponibilidad = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_disponibilidad, text="📦 Disponibilidad")
        self.create_disponibilidad_tab()

        # Pestaña 3: Alertas de Stock
        self.tab_alertas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_alertas, text="⚠️ Alertas de Stock")
        self.create_alertas_tab()

        # Barra de estado
        self.create_status_bar()

    def create_nuevo_pedido_tab(self):
        """Crea la pestaña de registro de nuevos pedidos."""
        # Título
        title_frame = ttk.Frame(self.tab_nuevo_pedido)
        title_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            title_frame, text="Registrar Nuevo Pedido", style="Title.TLabel"
        ).pack(anchor="w")

        # Marco del formulario
        form_frame = ttk.LabelFrame(
            self.tab_nuevo_pedido, text="Datos del Pedido", padding=20
        )
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cliente ID
        ttk.Label(form_frame, text="ID Cliente:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.entry_cliente_id = ttk.Entry(form_frame, width=30)
        self.entry_cliente_id.grid(row=0, column=1, sticky="w", pady=5, padx=10)

        # Ciudad
        ttk.Label(form_frame, text="Ciudad:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.combo_ciudad = ttk.Combobox(form_frame, width=28, state="readonly")
        self.combo_ciudad.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        self.combo_ciudad.bind("<<ComboboxSelected>>", self.on_ciudad_selected)

        # Producto
        ttk.Label(form_frame, text="Producto:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.combo_producto = ttk.Combobox(form_frame, width=28, state="readonly")
        self.combo_producto.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        self.combo_producto.bind("<<ComboboxSelected>>", self.on_producto_selected)

        # Stock disponible (label informativo)
        ttk.Label(
            form_frame, text="Stock Disponible:", font=("Arial", 10, "bold")
        ).grid(row=3, column=0, sticky="w", pady=5)
        self.label_stock_disponible = ttk.Label(
            form_frame, text="--", foreground=self.colors["secondary"]
        )
        self.label_stock_disponible.grid(row=3, column=1, sticky="w", pady=5, padx=10)

        # Cantidad
        ttk.Label(form_frame, text="Cantidad:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.spinbox_cantidad = ttk.Spinbox(form_frame, from_=1, to=1000, width=28)
        self.spinbox_cantidad.grid(row=4, column=1, sticky="w", pady=5, padx=10)
        self.spinbox_cantidad.set(1)

        # Precio unitario (entrada manual)
        ttk.Label(form_frame, text="Precio Unitario:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, sticky="w", pady=5
        )
        self.entry_precio = ttk.Entry(form_frame, width=30)
        self.entry_precio.grid(row=5, column=1, sticky="w", pady=5, padx=10)
        self.entry_precio.insert(0, "0.00")

        # Días de entrega
        ttk.Label(form_frame, text="Días de Entrega:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky="w", pady=5
        )
        self.spinbox_dias_entrega = ttk.Spinbox(form_frame, from_=1, to=30, width=28)
        self.spinbox_dias_entrega.grid(row=6, column=1, sticky="w", pady=5, padx=10)
        self.spinbox_dias_entrega.set(3)

        # Total calculado
        ttk.Label(form_frame, text="Total:", font=("Arial", 12, "bold")).grid(
            row=7, column=0, sticky="w", pady=15
        )
        self.label_total = ttk.Label(
            form_frame,
            text="$0.00",
            font=("Arial", 14, "bold"),
            foreground=self.colors["primary"],
        )
        self.label_total.grid(row=7, column=1, sticky="w", pady=15, padx=10)

        # Botón calcular total
        ttk.Button(form_frame, text="Calcular Total", command=self.calcular_total).grid(
            row=8, column=0, pady=10, sticky="ew", padx=5
        )

        # Botón registrar pedido
        ttk.Button(
            form_frame,
            text="Registrar Pedido",
            command=self.registrar_pedido,
            style="Success.TButton",
        ).grid(row=8, column=1, pady=10, sticky="ew", padx=5)

        # Botón limpiar formulario
        ttk.Button(form_frame, text="Limpiar", command=self.limpiar_formulario).grid(
            row=8, column=2, pady=10, sticky="ew", padx=5
        )

    def create_disponibilidad_tab(self):
        """Crea la pestaña de disponibilidad de productos."""
        # Título
        title_frame = ttk.Frame(self.tab_disponibilidad)
        title_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            title_frame, text="Disponibilidad de Productos", style="Title.TLabel"
        ).pack(anchor="w")

        # Filtros
        filter_frame = ttk.LabelFrame(
            self.tab_disponibilidad, text="Filtros", padding=10
        )
        filter_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(filter_frame, text="Ciudad:").grid(row=0, column=0, padx=5)
        self.combo_filtro_ciudad = ttk.Combobox(
            filter_frame, width=20, state="readonly"
        )
        self.combo_filtro_ciudad.grid(row=0, column=1, padx=5)
        self.combo_filtro_ciudad.bind(
            "<<ComboboxSelected>>", lambda e: self.actualizar_disponibilidad()
        )

        ttk.Button(
            filter_frame, text="Actualizar", command=self.actualizar_disponibilidad
        ).grid(row=0, column=2, padx=10)

        # Tabla de disponibilidad
        table_frame = ttk.Frame(self.tab_disponibilidad)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree_disponibilidad = ttk.Treeview(
            table_frame,
            columns=("ciudad", "producto", "stock", "estado"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        # Configurar columnas
        self.tree_disponibilidad.heading("ciudad", text="Ciudad")
        self.tree_disponibilidad.heading("producto", text="Producto")
        self.tree_disponibilidad.heading("stock", text="Stock Actual")
        self.tree_disponibilidad.heading("estado", text="Estado")

        self.tree_disponibilidad.column("ciudad", width=150)
        self.tree_disponibilidad.column("producto", width=250)
        self.tree_disponibilidad.column("stock", width=120, anchor="center")
        self.tree_disponibilidad.column("estado", width=120, anchor="center")

        self.tree_disponibilidad.pack(fill="both", expand=True)

        scroll_y.config(command=self.tree_disponibilidad.yview)
        scroll_x.config(command=self.tree_disponibilidad.xview)

        # Tags para colores
        self.tree_disponibilidad.tag_configure("bajo", background="#ffcccc")
        self.tree_disponibilidad.tag_configure("medio", background="#fff4cc")
        self.tree_disponibilidad.tag_configure("ok", background="#ccffcc")

    def create_alertas_tab(self):
        """Crea la pestaña de alertas de stock."""
        # Título
        title_frame = ttk.Frame(self.tab_alertas)
        title_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(title_frame, text="Alertas de Stock Bajo", style="Title.TLabel").pack(
            anchor="w"
        )

        # Información
        info_frame = ttk.Frame(self.tab_alertas)
        info_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            info_frame,
            text="⚠️ Productos que requieren reposición urgente",
            foreground=self.colors["warning"],
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")

        # Tabla de alertas
        table_frame = ttk.Frame(self.tab_alertas)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        # Treeview
        self.tree_alertas = ttk.Treeview(
            table_frame,
            columns=("ciudad", "producto", "stock_actual", "stock_minimo", "faltante"),
            show="headings",
            yscrollcommand=scroll_y.set,
        )

        # Configurar columnas
        self.tree_alertas.heading("ciudad", text="Ciudad")
        self.tree_alertas.heading("producto", text="Producto")
        self.tree_alertas.heading("stock_actual", text="Stock Actual")
        self.tree_alertas.heading("stock_minimo", text="Stock Mínimo")
        self.tree_alertas.heading("faltante", text="Faltante")

        self.tree_alertas.column("ciudad", width=150)
        self.tree_alertas.column("producto", width=250)
        self.tree_alertas.column("stock_actual", width=120, anchor="center")
        self.tree_alertas.column("stock_minimo", width=120, anchor="center")
        self.tree_alertas.column("faltante", width=120, anchor="center")

        self.tree_alertas.pack(fill="both", expand=True)

        scroll_y.config(command=self.tree_alertas.yview)

        # Tag para resaltar
        self.tree_alertas.tag_configure(
            "critico", background="#ffcccc", foreground="#cc0000"
        )

        # Botón actualizar
        ttk.Button(
            self.tab_alertas,
            text="🔄 Actualizar Alertas",
            command=self.actualizar_alertas,
        ).pack(pady=10)

    def create_status_bar(self):
        """Crea la barra de estado en la parte inferior."""
        self.status_bar = ttk.Label(
            self.root,
            text="✅ Conectado a la base de datos",
            relief="sunken",
            anchor="w",
        )
        self.status_bar.pack(side="bottom", fill="x")

    def load_initial_data(self):
        """Carga los datos iniciales de la base de datos."""
        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()

            # Cargar ciudades
            cursor.execute("SELECT nombre_ciudad FROM ciudades ORDER BY nombre_ciudad")
            ciudades = [row[0] for row in cursor.fetchall()]
            self.combo_ciudad["values"] = ciudades
            self.combo_filtro_ciudad["values"] = ["Todas"] + ciudades
            self.combo_filtro_ciudad.current(0)

            # Cargar productos
            cursor.execute(
                "SELECT nombre_producto FROM productos ORDER BY nombre_producto"
            )
            productos = [row[0] for row in cursor.fetchall()]
            self.combo_producto["values"] = productos

            # Actualizar disponibilidad
            self.actualizar_disponibilidad()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")

    def on_ciudad_selected(self, event):
        """Maneja el evento de selección de ciudad."""
        self.on_producto_selected(None)

    def on_producto_selected(self, event):
        """Maneja el evento de selección de producto."""
        ciudad = self.combo_ciudad.get()
        producto = self.combo_producto.get()

        if not ciudad or not producto:
            return

        try:
            cursor = self.conn.cursor()

            # Obtener solo stock disponible (sin precio)
            cursor.execute(
                """
                SELECT i.stock_actual
                FROM inventario i
                JOIN productos p ON i.id_producto = p.id_producto
                JOIN ciudades c ON i.id_ciudad = c.id_ciudad
                WHERE c.nombre_ciudad = ? AND p.nombre_producto = ?
            """,
                (ciudad, producto),
            )

            result = cursor.fetchone()

            if result:
                stock = result[0]
                self.label_stock_disponible.config(
                    text=f"{stock} unidades",
                    foreground=self.colors["primary"]
                    if stock > 10
                    else self.colors["danger"],
                )

                # Verificar si hay suficiente stock
                if stock < 10:
                    messagebox.showwarning(
                        "Stock Bajo",
                        f"⚠️ Advertencia: El stock de '{producto}' en '{ciudad}' es bajo.\n"
                        f"Stock actual: {stock} unidades",
                    )
            else:
                self.label_stock_disponible.config(
                    text="No disponible", foreground=self.colors["danger"]
                )
                messagebox.showwarning(
                    "Producto No Disponible",
                    f"El producto '{producto}' no está disponible en '{ciudad}'",
                )

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al consultar stock: {e}")

    def calcular_total(self):
        """Calcula el total del pedido."""
        try:
            precio_text = (
                self.entry_precio.get().strip().replace("$", "").replace(",", "")
            )
            if not precio_text:
                messagebox.showerror("Error", "Por favor ingresa el precio unitario")
                return

            precio = float(precio_text)
            cantidad = int(self.spinbox_cantidad.get())

            if precio <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor a 0")
                return

            total = precio * cantidad
            self.label_total.config(text=f"${total:,.2f}")

        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido")

    def registrar_pedido(self):
        """Registra un nuevo pedido en la base de datos."""
        # Validar campos
        cliente_id = self.entry_cliente_id.get().strip()
        ciudad = self.combo_ciudad.get()
        producto = self.combo_producto.get()
        precio_text = self.entry_precio.get().strip().replace("$", "").replace(",", "")

        if not all([cliente_id, ciudad, producto, precio_text]):
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return

        try:
            cantidad = int(self.spinbox_cantidad.get())
            dias_entrega = int(self.spinbox_dias_entrega.get())
            precio_unitario = float(precio_text)

            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return

            if precio_unitario <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor a 0")
                return

        except ValueError:
            messagebox.showerror(
                "Error", "Cantidad, días de entrega y precio deben ser números válidos"
            )
            return

        try:
            cursor = self.conn.cursor()

            # Verificar stock disponible (sin precio_unitario)
            cursor.execute(
                """
                SELECT i.stock_actual, i.id_inventario, p.id_producto, c.id_ciudad
                FROM inventario i
                JOIN productos p ON i.id_producto = p.id_producto
                JOIN ciudades c ON i.id_ciudad = c.id_ciudad
                WHERE c.nombre_ciudad = ? AND p.nombre_producto = ?
            """,
                (ciudad, producto),
            )

            result = cursor.fetchone()

            if not result:
                messagebox.showerror(
                    "Error", f"Producto '{producto}' no disponible en '{ciudad}'"
                )
                return

            stock_actual, id_inventario, id_producto, id_ciudad = result

            # Verificar si hay suficiente stock
            if stock_actual < cantidad:
                respuesta = messagebox.askyesno(
                    "Stock Insuficiente",
                    f"⚠️ ALERTA: Stock insuficiente\n\n"
                    f"Stock disponible: {stock_actual} unidades\n"
                    f"Cantidad solicitada: {cantidad} unidades\n"
                    f"Faltante: {cantidad - stock_actual} unidades\n\n"
                    f"¿Deseas continuar de todos modos?",
                )
                if not respuesta:
                    return

            # Generar ID de venta (último ID + 1)
            cursor.execute("SELECT MAX(id_venta) FROM ventas")
            max_id = cursor.fetchone()[0]
            nuevo_id_venta = (max_id or 0) + 1

            # Calcular fechas
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            fecha_entrega = (datetime.now() + timedelta(days=dias_entrega)).strftime(
                "%Y-%m-%d"
            )

            # Insertar venta con precio_unitario ingresado manualmente
            cursor.execute(
                """
                INSERT INTO ventas
                (id_venta, id_cliente, id_ciudad, id_producto, fecha, fecha_entrega,
                 tiempo_entrega_dias, estado_entrega, cantidad, precio_unitario,
                 stock_inicial, stock_final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    nuevo_id_venta,
                    cliente_id,
                    id_ciudad,
                    id_producto,
                    fecha_actual,
                    fecha_entrega,
                    dias_entrega,
                    "En tránsito",
                    cantidad,
                    precio_unitario,  # Precio ingresado manualmente
                    stock_actual,
                    max(0, stock_actual - cantidad),
                ),
            )

            # Actualizar inventario
            nuevo_stock = max(0, stock_actual - cantidad)
            cursor.execute(
                """
                UPDATE inventario
                SET stock_actual = ?, ultima_actualizacion = CURRENT_TIMESTAMP
                WHERE id_inventario = ?
            """,
                (nuevo_stock, id_inventario),
            )

            self.conn.commit()

            # Mensaje de éxito
            messagebox.showinfo(
                "Pedido Registrado",
                f"✅ Pedido #{nuevo_id_venta} registrado exitosamente\n\n"
                f"Cliente: {cliente_id}\n"
                f"Producto: {producto}\n"
                f"Cantidad: {cantidad}\n"
                f"Precio unitario: ${precio_unitario:,.2f}\n"
                f"Total: ${cantidad * precio_unitario:,.2f}\n"
                f"Fecha de entrega: {fecha_entrega}\n"
                f"Stock restante: {nuevo_stock}",
            )

            # Limpiar formulario
            self.limpiar_formulario()

            # Actualizar vistas
            self.actualizar_disponibilidad()
            self.actualizar_alertas()

            # Verificar si necesita reposición
            if nuevo_stock < 10:
                messagebox.showwarning(
                    "Alerta de Reposición",
                    f"⚠️ El stock de '{producto}' en '{ciudad}' es bajo.\n"
                    f"Stock actual: {nuevo_stock} unidades\n\n"
                    f"Se recomienda reponer inventario.",
                )

        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al registrar pedido: {e}")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.entry_cliente_id.delete(0, tk.END)
        self.combo_ciudad.set("")
        self.combo_producto.set("")
        self.spinbox_cantidad.set(1)
        self.spinbox_dias_entrega.set(3)
        self.label_stock_disponible.config(text="--")
        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, "0.00")
        self.label_total.config(text="$0.00")

    def actualizar_disponibilidad(self):
        """Actualiza la tabla de disponibilidad de productos."""
        # Limpiar tabla
        for item in self.tree_disponibilidad.get_children():
            self.tree_disponibilidad.delete(item)

        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()
            ciudad_filtro = self.combo_filtro_ciudad.get()

            query = """
                SELECT
                    c.nombre_ciudad,
                    p.nombre_producto,
                    i.stock_actual
                FROM inventario i
                JOIN productos p ON i.id_producto = p.id_producto
                JOIN ciudades c ON i.id_ciudad = c.id_ciudad
            """

            params = []
            if ciudad_filtro and ciudad_filtro != "Todas":
                query += " WHERE c.nombre_ciudad = ?"
                params.append(ciudad_filtro)

            query += " ORDER BY c.nombre_ciudad, p.nombre_producto"

            cursor.execute(query, params)

            for row in cursor.fetchall():
                ciudad, producto, stock = row

                # Determinar estado y tag
                if stock < 10:
                    estado = "🔴 BAJO"
                    tag = "bajo"
                elif stock < 20:
                    estado = "🟡 MEDIO"
                    tag = "medio"
                else:
                    estado = "🟢 OK"
                    tag = "ok"

                self.tree_disponibilidad.insert(
                    "", "end", values=(ciudad, producto, stock, estado), tags=(tag,)
                )

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar disponibilidad: {e}")

    def actualizar_alertas(self):
        """Actualiza la tabla de alertas de stock bajo."""
        # Limpiar tabla
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)

        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT
                    c.nombre_ciudad,
                    p.nombre_producto,
                    i.stock_actual,
                    10 as stock_minimo,
                    (10 - i.stock_actual) as faltante
                FROM inventario i
                JOIN productos p ON i.id_producto = p.id_producto
                JOIN ciudades c ON i.id_ciudad = c.id_ciudad
                WHERE i.stock_actual < 10
                ORDER BY i.stock_actual ASC, c.nombre_ciudad
            """)

            alertas_count = 0
            for row in cursor.fetchall():
                ciudad, producto, stock_actual, stock_minimo, faltante = row
                self.tree_alertas.insert(
                    "",
                    "end",
                    values=(ciudad, producto, stock_actual, stock_minimo, faltante),
                    tags=("critico",),
                )
                alertas_count += 1

            # Actualizar barra de estado
            if alertas_count > 0:
                self.status_bar.config(
                    text=f"⚠️ {alertas_count} alerta(s) de stock bajo", foreground="red"
                )
            else:
                self.status_bar.config(
                    text="✅ No hay alertas de stock bajo", foreground="green"
                )

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar alertas: {e}")

    def check_stock_alerts(self):
        """Verifica y muestra alertas de stock al iniciar la aplicación."""
        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM inventario
                WHERE stock_actual < 10
            """)

            count = cursor.fetchone()[0]

            if count > 0:
                messagebox.showwarning(
                    "Alertas de Stock",
                    f"⚠️ Hay {count} producto(s) con stock bajo.\n\n"
                    f"Revisa la pestaña 'Alertas de Stock' para más detalles.",
                )

        except sqlite3.Error as e:
            print(f"Error al verificar alertas: {e}")

    def __del__(self):
        """Cierra la conexión a la base de datos al cerrar la aplicación."""
        if self.conn:
            self.conn.close()


def start_ui():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = FreshMarketApp(root)
    root.mainloop()
