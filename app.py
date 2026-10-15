from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import conectar
from decimal import Decimal, InvalidOperation
from datetime import datetime
import traceback

app = Flask(__name__)

app.secret_key = "flashop_clave_secreta_2026"

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False


# ============================================================
# UTILIDADES
# ============================================================

def cerrar_db(conexion=None, cursor=None):

    try:
        if cursor:
            cursor.close()
    except Exception:
        pass

    try:
        if conexion:
            conexion.close()
    except Exception:
        pass


def error_json(mensaje, codigo=400, **extra):

    respuesta = {
        "ok": False,
        "error": mensaje
    }

    respuesta.update(extra)

    return jsonify(respuesta), codigo


def ok_json(mensaje, **datos):

    respuesta = {
        "ok": True,
        "mensaje": mensaje
    }

    respuesta.update(datos)

    return jsonify(respuesta)


def decimal_seguro(valor):

    try:
        return Decimal(str(valor))

    except (InvalidOperation, ValueError, TypeError):

        raise ValueError(
            "Valor numérico inválido."
        )


def normalizar_texto(valor):

    if valor is None:
        return ""

    return str(valor).strip()


def entero_seguro(valor, nombre="valor"):

    try:
        return int(valor)

    except (TypeError, ValueError):

        raise ValueError(
            f"{nombre} no es válido."
        )


def datos_json():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return None

    return datos


def registrar_error(nombre, error):

    print("=" * 70)
    print(f"ERROR: {nombre}")
    print(str(error))

    traceback.print_exc()

    print("=" * 70)


# ============================================================
# INICIO
# ============================================================

@app.route("/")
def inicio():

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                precio,
                categoria,
                imagen,
                stock,
                rating
            FROM productos
            ORDER BY id_producto DESC
        """)

        productos = cursor.fetchall()

        return render_template(
            "index.html",
            productos=productos
        )

    except Exception as e:

        registrar_error(
            "INICIO",
            e
        )

        return error_json(
            "No se pudieron cargar los productos.",
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# ESTADO DEL SERVIDOR
# ============================================================

@app.route("/estado-servidor")
def estado_servidor():

    return jsonify({

        "ok": True,

        "servidor": "Flash Shop",

        "estado": "Activo",

        "fecha": datetime.now().isoformat()

    })


# ============================================================
# PRODUCTOS
# ============================================================

@app.route("/productos", methods=["GET"])
def obtener_productos():

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        categoria = normalizar_texto(
            request.args.get("categoria")
        )

        busqueda = normalizar_texto(
            request.args.get("buscar")
        )

        consulta = """
            SELECT
                id_producto,
                nombre,
                precio,
                categoria,
                imagen,
                stock,
                rating
            FROM productos
            WHERE 1 = 1
        """

        parametros = []

        if categoria:

            consulta += """
                AND categoria = %s
            """

            parametros.append(
                categoria
            )

        if busqueda:

            consulta += """
                AND nombre LIKE %s
            """

            parametros.append(
                f"%{busqueda}%"
            )

        consulta += """
            ORDER BY id_producto DESC
        """

        cursor.execute(
            consulta,
            tuple(parametros)
        )

        productos = cursor.fetchall()

        return ok_json(

            "Productos obtenidos correctamente.",

            productos=productos,

            cantidad=len(productos)

        )

    except Exception as e:

        registrar_error(
            "OBTENER PRODUCTOS",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


@app.route("/producto/<int:id_producto>", methods=["GET"])
def obtener_producto(id_producto):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                precio,
                categoria,
                imagen,
                stock,
                rating
            FROM productos
            WHERE id_producto = %s
            LIMIT 1
        """, (
            id_producto,
        ))

        producto = cursor.fetchone()

        if not producto:

            return error_json(
                "El producto no existe.",
                404
            )

        return ok_json(

            "Producto encontrado.",

            producto=producto

        )

    except Exception as e:

        registrar_error(
            "OBTENER PRODUCTO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# PRUEBA BASE DE DATOS
# ============================================================

@app.route("/prueba-db")
def prueba_db():

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM clientes"
        )

        clientes = cursor.fetchall()

        return jsonify({

            "ok": True,

            "clientes": clientes

        })

    except Exception as e:

        registrar_error(
            "PRUEBA DB",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# REGISTRO DE CLIENTES
# ============================================================

@app.route("/registro", methods=["POST"])
def registro():

    datos = datos_json()

    if not datos:

        return error_json(
            "No se recibieron datos."
        )

    nombre = normalizar_texto(
        datos.get("nombre")
    )

    apellido = normalizar_texto(
        datos.get("apellido")
    )

    correo = normalizar_texto(
        datos.get("correo")
    )

    contraseña = normalizar_texto(
        datos.get("contraseña")
    )

    telefono = normalizar_texto(
        datos.get("telefono")
    )

    direccion = normalizar_texto(
        datos.get("direccion")
    )

    ciudad = normalizar_texto(
        datos.get("ciudad")
    )

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if not nombre:

        return error_json(
            "Falta el nombre."
        )

    if not apellido:

        return error_json(
            "Falta el apellido."
        )

    if not correo:

        return error_json(
            "Falta el correo."
        )

    if not contraseña:

        return error_json(
            "Falta la contraseña."
        )

    if len(contraseña) < 4:

        return error_json(
            "La contraseña debe tener mínimo 4 caracteres."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        # ----------------------------------------------------
        # VERIFICAR CORREO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id_cliente
            FROM clientes
            WHERE correo = %s
            LIMIT 1
        """, (
            correo,
        ))

        existente = cursor.fetchone()

        if existente:

            return error_json(
                "Ese correo ya está registrado.",
                409
            )

        # ----------------------------------------------------
        # INSERTAR CLIENTE
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO clientes
            (
                nombre,
                apellido,
                correo,
                contraseña,
                telefono,
                direccion,
                ciudad
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (

            nombre,

            apellido,

            correo,

            contraseña,

            telefono,

            direccion,

            ciudad

        ))

        id_cliente = cursor.lastrowid

        conexion.commit()

        return ok_json(

            "Cuenta creada correctamente.",

            id_cliente=id_cliente

        )

    except Exception as e:

        if conexion:

            conexion.rollback()

        registrar_error(
            "REGISTRO CLIENTE",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# LOGIN CON MYSQL
# ======================================================

@app.route("/login", methods=["POST"])
def login():

    datos = request.get_json()

    if not datos:
        return jsonify({
            "ok": False,
            "error": "No se recibieron datos"
        }), 400

    correo = datos.get("correo", "").strip()
    contrasena = datos.get("contrasena", "").strip()

    if not correo or not contrasena:
        return jsonify({
            "ok": False,
            "error": "Completa todos los campos"
        }), 400

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                id_cliente,
                nombre,
                apellido,
                correo,
                rol
            FROM clientes
            WHERE correo = %s
            AND contraseña = %s
        """, (correo, contrasena))

        cliente = cursor.fetchone()

        if not cliente:

            return jsonify({
                "ok": False,
                "error": "Correo o contraseña incorrectos"
            }), 401

        # GUARDAR LOS DATOS DEL USUARIO EN LA SESIÓN
        session["id_cliente"] = cliente["id_cliente"]
        session["nombre_cliente"] = cliente["nombre"]
        session["apellido_cliente"] = cliente["apellido"]
        session["correo"] = cliente["correo"]
        session["rol"] = cliente["rol"]

        return jsonify({

            "ok": True,

            "id_cliente": cliente["id_cliente"],
            "nombre": cliente["nombre"],
            "apellido": cliente["apellido"],
            "correo": cliente["correo"],
            "rol": cliente["rol"]

        })

    except Exception as e:

        print("ERROR LOGIN MYSQL:", e)

        return jsonify({
            "ok": False,
            "error": "Error al consultar la base de datos"
        }), 500

    finally:

        cursor.close()
        conexion.close()

# ============================================================
# CLIENTE
# ============================================================

@app.route("/cliente/<int:id_cliente>", methods=["GET"])
def obtener_cliente(id_cliente):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_cliente,
                nombre,
                apellido,
                correo,
                telefono,
                direccion,
                ciudad
            FROM clientes
            WHERE id_cliente = %s
            LIMIT 1
        """, (
            id_cliente,
        ))

        cliente = cursor.fetchone()

        if not cliente:

            return error_json(
                "Cliente no encontrado.",
                404
            )

        return ok_json(

            "Cliente encontrado.",

            cliente=cliente

        )

    except Exception as e:

        registrar_error(
            "CLIENTE",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# PEDIDOS
# ============================================================

def cargar_producto_para_pedido(
    cursor,
    id_producto
):

    cursor.execute("""
        SELECT
            id_producto,
            nombre,
            precio,
            stock
        FROM productos
        WHERE id_producto = %s
        LIMIT 1
    """, (
        id_producto,
    ))

    return cursor.fetchone()


@app.route("/crear-pedido", methods=["POST"])
def crear_pedido():

    datos = datos_json()

    if not datos:

        return error_json(
            "No se recibieron datos."
        )

    id_cliente = datos.get(
        "id_cliente"
    )

    productos = datos.get(
        "productos",
        []
    )

    if not id_cliente:

        return error_json(
            "Falta el cliente."
        )

    if not isinstance(productos, list) or not productos:

        return error_json(
            "El carrito está vacío."
        )

    conexion = None
    cursor = None

    try:

        id_cliente = entero_seguro(
            id_cliente,
            "id_cliente"
        )

        conexion = conectar()
        cursor = conexion.cursor()

        # ----------------------------------------------------
        # CLIENTE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id_cliente
            FROM clientes
            WHERE id_cliente = %s
            LIMIT 1
        """, (
            id_cliente,
        ))

        if not cursor.fetchone():

            return error_json(
                "El cliente no existe."
            )

        carrito_validado = []

        total = Decimal("0.00")

        # ----------------------------------------------------
        # VALIDAR PRODUCTOS
        # ----------------------------------------------------

        for item in productos:

            if not isinstance(item, dict):

                raise ValueError(
                    "Hay un producto inválido en el carrito."
                )

            id_producto = item.get(
                "id_producto"
            )

            cantidad = item.get(
                "cantidad"
            )

            if not id_producto:

                raise ValueError(
                    "Falta el id del producto."
                )

            id_producto = entero_seguro(
                id_producto,
                "id_producto"
            )

            cantidad = entero_seguro(
                cantidad,
                "cantidad"
            )

            if cantidad <= 0:

                raise ValueError(
                    "La cantidad debe ser mayor que cero."
                )

            producto = cargar_producto_para_pedido(
                cursor,
                id_producto
            )

            if not producto:

                raise ValueError(
                    f"El producto {id_producto} no existe."
                )

            stock = entero_seguro(
                producto["stock"],
                "stock"
            )

            if stock < cantidad:

                raise ValueError(
                    f"No hay suficiente stock para "
                    f"'{producto['nombre']}'. "
                    f"Disponible: {stock}."
                )

            precio = decimal_seguro(
                producto["precio"]
            )

            subtotal = precio * cantidad

            total += subtotal

            carrito_validado.append({

                "id_producto": id_producto,

                "nombre": producto["nombre"],

                "precio": precio,

                "cantidad": cantidad,

                "subtotal": subtotal

            })

        # ----------------------------------------------------
        # CREAR PEDIDO
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO pedidos
            (
                id_cliente,
                estado,
                total
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (

            id_cliente,

            "Pendiente",

            total

        ))

        id_pedido = cursor.lastrowid

        # ----------------------------------------------------
        # DETALLES Y STOCK
        # ----------------------------------------------------

        for item in carrito_validado:

            cursor.execute("""
                INSERT INTO detalles_pedidos
                (
                    id_pedido,
                    id_producto,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (

                id_pedido,

                item["id_producto"],

                item["cantidad"],

                item["precio"],

                item["subtotal"]

            ))

            cursor.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id_producto = %s
                  AND stock >= %s
            """, (

                item["cantidad"],

                item["id_producto"],

                item["cantidad"]

            ))

            if cursor.rowcount != 1:

                raise ValueError(
                    f"No se pudo descontar el stock de "
                    f"'{item['nombre']}'."
                )

        conexion.commit()

        return ok_json(

            "Pedido creado correctamente.",

            id_pedido=id_pedido,

            total=float(total),

            estado="Pendiente"

        )

    except ValueError as e:

        if conexion:
            conexion.rollback()

        return error_json(
            str(e),
            400
        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "CREAR PEDIDO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# REGISTRAR PAGO
# ============================================================

METODOS_PAGO = {

    "efectivo",

    "tarjeta",

    "nequi",

    "daviplata",

    "pse"

}


@app.route("/registrar-pago", methods=["POST"])
def registrar_pago():

    datos = datos_json()

    if not datos:

        return error_json(
            "No se recibieron datos."
        )

    id_pedido = datos.get(
        "id_pedido"
    )

    metodo_pago = normalizar_texto(
        datos.get("metodo_pago")
    ).lower()

    monto_recibido = datos.get(
        "monto"
    )

    if not id_pedido:

        return error_json(
            "Falta el id del pedido."
        )

    try:

        id_pedido = entero_seguro(
            id_pedido,
            "id_pedido"
        )

    except ValueError as e:

        return error_json(
            str(e)
        )

    if metodo_pago not in METODOS_PAGO:

        return error_json(
            "Método de pago no permitido."
        )

    if monto_recibido is None:

        return error_json(
            "Falta el monto."
        )

    try:

        monto = decimal_seguro(
            monto_recibido
        )

    except ValueError:

        return error_json(
            "El monto no es válido."
        )

    if monto <= 0:

        return error_json(
            "El monto debe ser mayor que cero."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        # ----------------------------------------------------
        # PEDIDO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id_pedido,
                id_cliente,
                estado,
                total
            FROM pedidos
            WHERE id_pedido = %s
            LIMIT 1
        """, (
            id_pedido,
        ))

        pedido = cursor.fetchone()

        if not pedido:

            return error_json(
                "El pedido no existe.",
                404
            )

        total = decimal_seguro(
            pedido["total"]
        )

        # ----------------------------------------------------
        # EVITAR DOBLE PAGO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id_pago
            FROM pagos
            WHERE id_pedido = %s
              AND estado = 'Pagado'
            LIMIT 1
        """, (
            id_pedido,
        ))

        pago_existente = cursor.fetchone()

        if pago_existente:

            return error_json(
                "Este pedido ya tiene un pago registrado.",
                409
            )

        # ----------------------------------------------------
        # MONTO
        # ----------------------------------------------------

        if monto < total:

            faltante = total - monto

            return error_json(

                "El monto es insuficiente.",

                400,

                total_pedido=float(total),

                monto_recibido=float(monto),

                faltante=float(faltante)

            )

        cambio = monto - total

        # ----------------------------------------------------
        # INSERTAR PAGO
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO pagos
            (
                id_pedido,
                metodo_pago,
                monto,
                estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
        """, (

            id_pedido,

            metodo_pago,

            total,

            "Pagado"

        ))

        id_pago = cursor.lastrowid

        # ----------------------------------------------------
        # ACTUALIZAR PEDIDO
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE pedidos
            SET estado = 'Pagado'
            WHERE id_pedido = %s
        """, (
            id_pedido,
        ))

        conexion.commit()

        return ok_json(

            "Pago registrado correctamente.",

            id_pago=id_pago,

            id_pedido=id_pedido,

            total=float(total),

            monto_recibido=float(monto),

            cambio=float(cambio),

            metodo_pago=metodo_pago,

            estado="Pagado"

        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "REGISTRAR PAGO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# CONSULTAR PAGO
# ============================================================

@app.route("/pago/<int:id_pedido>", methods=["GET"])
def consultar_pago(id_pedido):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_pago,
                id_pedido,
                metodo_pago,
                monto,
                estado
            FROM pagos
            WHERE id_pedido = %s
            ORDER BY id_pago DESC
            LIMIT 1
        """, (
            id_pedido,
        ))

        pago = cursor.fetchone()

        if not pago:

            return error_json(
                "El pedido todavía no tiene pago.",
                404
            )

        return ok_json(

            "Pago encontrado.",

            pago=pago

        )

    except Exception as e:

        registrar_error(
            "CONSULTAR PAGO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# PEDIDO
# ============================================================

@app.route("/pedido/<int:id_pedido>", methods=["GET"])
def obtener_pedido(id_pedido):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_pedido,
                id_cliente,
                estado,
                total
            FROM pedidos
            WHERE id_pedido = %s
            LIMIT 1
        """, (
            id_pedido,
        ))

        pedido = cursor.fetchone()

        if not pedido:

            return error_json(
                "El pedido no existe.",
                404
            )

        cursor.execute("""
            SELECT
                dp.id_producto,
                pr.nombre,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal
            FROM detalles_pedidos dp
            INNER JOIN productos pr
                ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
            ORDER BY dp.id_producto
        """, (
            id_pedido,
        ))

        detalles = cursor.fetchall()

        cursor.execute("""
            SELECT
                id_pago,
                metodo_pago,
                monto,
                estado
            FROM pagos
            WHERE id_pedido = %s
            ORDER BY id_pago DESC
            LIMIT 1
        """, (
            id_pedido,
        ))

        pago = cursor.fetchone()

        return ok_json(

            "Pedido encontrado.",

            pedido=pedido,

            detalles=detalles,

            pago=pago

        )

    except Exception as e:

        registrar_error(
            "OBTENER PEDIDO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# PEDIDOS DEL CLIENTE
# ============================================================

@app.route(
    "/cliente/<int:id_cliente>/pedidos",
    methods=["GET"]
)
def pedidos_cliente(id_cliente):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_pedido,
                id_cliente,
                estado,
                total
            FROM pedidos
            WHERE id_cliente = %s
            ORDER BY id_pedido DESC
        """, (
            id_cliente,
        ))

        pedidos = cursor.fetchall()

        return ok_json(

            "Pedidos obtenidos correctamente.",

            pedidos=pedidos,

            cantidad=len(pedidos)

        )

    except Exception as e:

        registrar_error(
            "HISTORIAL PEDIDOS",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# CANCELAR PEDIDO
# ============================================================

@app.route(
    "/cancelar-pedido/<int:id_pedido>",
    methods=["POST"]
)
def cancelar_pedido(id_pedido):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_pedido,
                estado
            FROM pedidos
            WHERE id_pedido = %s
            LIMIT 1
        """, (
            id_pedido,
        ))

        pedido = cursor.fetchone()

        if not pedido:

            return error_json(
                "El pedido no existe.",
                404
            )

        estado = normalizar_texto(
            pedido["estado"]
        ).lower()

        if estado == "pagado":

            return error_json(
                "No se puede cancelar un pedido pagado."
            )

        if estado == "cancelado":

            return error_json(
                "El pedido ya está cancelado."
            )

        cursor.execute("""
            SELECT
                id_producto,
                cantidad
            FROM detalles_pedidos
            WHERE id_pedido = %s
        """, (
            id_pedido,
        ))

        detalles = cursor.fetchall()

        for detalle in detalles:

            cursor.execute("""
                UPDATE productos
                SET stock = stock + %s
                WHERE id_producto = %s
            """, (

                detalle["cantidad"],

                detalle["id_producto"]

            ))

        cursor.execute("""
            UPDATE pedidos
            SET estado = 'Cancelado'
            WHERE id_pedido = %s
        """, (
            id_pedido,
        ))

        conexion.commit()

        return ok_json(

            "Pedido cancelado correctamente.",

            id_pedido=id_pedido,

            estado="Cancelado"

        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "CANCELAR PEDIDO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# BÚSQUEDA
# ============================================================

@app.route("/buscar", methods=["GET"])
def buscar():

    conexion = None
    cursor = None

    texto = normalizar_texto(
        request.args.get("q")
    )

    if not texto:

        return ok_json(

            "Escribe algo para buscar.",

            productos=[]

        )

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                precio,
                categoria,
                imagen,
                stock,
                rating
            FROM productos
            WHERE nombre LIKE %s
               OR categoria LIKE %s
            ORDER BY
                CASE
                    WHEN nombre LIKE %s THEN 0
                    ELSE 1
                END,
                nombre ASC
        """, (

            f"%{texto}%",

            f"%{texto}%",

            f"{texto}%"

        ))

        productos = cursor.fetchall()

        return ok_json(

            "Búsqueda completada.",

            productos=productos,

            cantidad=len(productos)

        )

    except Exception as e:

        registrar_error(
            "BUSCAR",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# CATEGORÍAS
# ============================================================

@app.route("/categorias", methods=["GET"])
def categorias():

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT DISTINCT categoria
            FROM productos
            WHERE categoria IS NOT NULL
              AND categoria <> ''
            ORDER BY categoria ASC
        """)

        categorias_db = cursor.fetchall()

        return ok_json(

            "Categorías obtenidas correctamente.",

            categorias=categorias_db

        )

    except Exception as e:

        registrar_error(
            "CATEGORÍAS",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# STOCK
# ============================================================

@app.route(
    "/stock/<int:id_producto>",
    methods=["GET"]
)
def consultar_stock(id_producto):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                stock
            FROM productos
            WHERE id_producto = %s
            LIMIT 1
        """, (
            id_producto,
        ))

        producto = cursor.fetchone()

        if not producto:

            return error_json(
                "Producto no encontrado.",
                404
            )

        return ok_json(

            "Stock consultado.",

            producto=producto

        )

    except Exception as e:

        registrar_error(
            "STOCK",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# RESUMEN DE COMPRA
# ============================================================

@app.route(
    "/resumen-compra",
    methods=["POST"]
)
def resumen_compra():

    datos = datos_json()

    if not datos:

        return error_json(
            "No se recibieron datos."
        )

    productos = datos.get(
        "productos",
        []
    )

    if not productos:

        return error_json(
            "El carrito está vacío."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        subtotal = Decimal("0.00")

        cantidad_total = 0

        productos_resumen = []

        for item in productos:

            id_producto = entero_seguro(
                item.get("id_producto"),
                "id_producto"
            )

            cantidad = entero_seguro(
                item.get("cantidad"),
                "cantidad"
            )

            if cantidad <= 0:

                raise ValueError(
                    "La cantidad debe ser mayor que cero."
                )

            producto = cargar_producto_para_pedido(
                cursor,
                id_producto
            )

            if not producto:

                raise ValueError(
                    f"El producto {id_producto} no existe."
                )

            stock = entero_seguro(
                producto["stock"],
                "stock"
            )

            if stock < cantidad:

                raise ValueError(
                    f"Stock insuficiente para "
                    f"{producto['nombre']}."
                )

            precio = decimal_seguro(
                producto["precio"]
            )

            total_producto = (
                precio * cantidad
            )

            subtotal += total_producto

            cantidad_total += cantidad

            productos_resumen.append({

                "id_producto":
                    id_producto,

                "nombre":
                    producto["nombre"],

                "precio":
                    float(precio),

                "cantidad":
                    cantidad,

                "subtotal":
                    float(total_producto),

                "stock":
                    stock

            })

        return ok_json(

            "Resumen calculado correctamente.",

            productos=productos_resumen,

            cantidad_total=cantidad_total,

            subtotal=float(subtotal),

            total=float(subtotal)

        )

    except ValueError as e:

        return error_json(
            str(e)
        )

    except Exception as e:

        registrar_error(
            "RESUMEN COMPRA",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# GENERAR FACTURA
# ============================================================

@app.route("/generar-factura/<int:id_pedido>", methods=["GET"])
def generar_factura(id_pedido):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        # ----------------------------------------------------
        # DATOS DEL PEDIDO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                p.id_pedido,
                p.id_cliente,
                p.estado,
                p.total,
                c.nombre,
                c.apellido,
                c.correo
            FROM pedidos p
            INNER JOIN clientes c
                ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
            LIMIT 1
        """, (
            id_pedido,
        ))

        pedido = cursor.fetchone()

        if not pedido:

            return error_json(
                "El pedido no existe.",
                404
            )

        # ----------------------------------------------------
        # VERIFICAR PAGO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id_pago,
                metodo_pago,
                monto,
                estado
            FROM pagos
            WHERE id_pedido = %s
              AND estado = 'Pagado'
            ORDER BY id_pago DESC
            LIMIT 1
        """, (
            id_pedido,
        ))

        pago = cursor.fetchone()

        if not pago:

            return error_json(
                "El pedido todavía no ha sido pagado.",
                400
            )

        # ----------------------------------------------------
        # PRODUCTOS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                dp.id_producto,
                pr.nombre,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal
            FROM detalles_pedidos dp
            INNER JOIN productos pr
                ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
            ORDER BY dp.id_producto
        """, (
            id_pedido,
        ))

        detalles = cursor.fetchall()

        if not detalles:

            return error_json(
                "El pedido no tiene productos.",
                400
            )

        # ----------------------------------------------------
        # RESPUESTA DE FACTURA
        # ----------------------------------------------------

        factura = {

            "numero_factura":
                f"FS-{id_pedido:06d}",

            "fecha":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),

            "cliente": {

                "id_cliente":
                    pedido["id_cliente"],

                "nombre":
                    f'{pedido["nombre"]} {pedido["apellido"]}',

                "correo":
                    pedido["correo"]

            },

            "pedido": {

                "id_pedido":
                    pedido["id_pedido"],

                "estado":
                    pedido["estado"],

                "total":
                    float(pedido["total"])

            },

            "pago": {

                "id_pago":
                    pago["id_pago"],

                "metodo_pago":
                    pago["metodo_pago"],

                "monto":
                    float(pago["monto"]),

                "estado":
                    pago["estado"]

            },

            "productos": [

                {

                    "id_producto":
                        item["id_producto"],

                    "nombre":
                        item["nombre"],

                    "cantidad":
                        item["cantidad"],

                    "precio":
                        float(item["precio_unitario"]),

                    "subtotal":
                        float(item["subtotal"])

                }

                for item in detalles

            ]

        }

        return jsonify({

            "ok": True,

            "mensaje":
                "Factura generada correctamente.",

            "factura":
                factura

        })

    except Exception as e:

        registrar_error(
            "GENERAR FACTURA",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )
# ============================================================
# ERRORES
# ============================================================

@app.errorhandler(404)
def error_404(error):

    return jsonify({

        "ok": False,

        "error":
            "La ruta solicitada no existe."

    }), 404


@app.errorhandler(405)
def error_405(error):

    return jsonify({

        "ok": False,

        "error":
            "Método HTTP no permitido para esta ruta."

    }), 405


@app.errorhandler(500)
def error_500(error):

    return jsonify({

        "ok": False,

        "error":
            "Error interno del servidor."

    }), 500

# ======================================================
# MIS PEDIDOS
# ======================================================

@app.route("/mis-pedidos/<int:id_cliente>")
def mis_pedidos(id_cliente):

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                p.id_pedido,
                p.fecha,
                p.estado,
                p.total
            FROM pedidos p
            WHERE p.id_cliente = %s
            ORDER BY p.id_pedido DESC
        """, (id_cliente,))

        pedidos = cursor.fetchall()

        return jsonify({
            "pedidos": pedidos
        })

    except Exception as e:

        print("ERROR MIS PEDIDOS:", e)

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()

# ======================================================
# PANEL ADMIN
# ======================================================

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/productos")
def admin_productos():

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                precio,
                categoria,
                stock
            FROM productos
            ORDER BY id_producto DESC
        """)

        productos = cursor.fetchall()

        return jsonify({
            "productos": productos
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()

@app.route("/admin/clientes")
def admin_clientes():

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                id_cliente,
                nombre,
                apellido,
                correo,
                rol
            FROM clientes
            ORDER BY id_cliente DESC
        """)

        clientes = cursor.fetchall()

        return jsonify({
            "clientes": clientes
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()


@app.route("/admin/pedidos")
def admin_pedidos():

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                p.id_pedido,
                p.id_cliente,
                c.nombre,
                c.apellido,
                p.estado,
                p.total
            FROM pedidos p
            INNER JOIN clientes c
                ON p.id_cliente = c.id_cliente
            ORDER BY p.id_pedido DESC
        """)

        pedidos = cursor.fetchall()

        return jsonify({
            "pedidos": pedidos
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()

@app.route("/admin/pagos")
def admin_pagos():

    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                id_pago,
                id_pedido,
                fecha_pago,
                metodo_pago,
                monto,
                estado
            FROM pagos
            ORDER BY id_pago DESC
        """)

        pagos = cursor.fetchall()

        return jsonify({
            "pagos": pagos
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()

@app.route("/admin/stock")
def admin_stock():


    conexion = conectar()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                stock
            FROM productos
            ORDER BY stock ASC
        """)

        productos = cursor.fetchall()

        return jsonify({
            "productos": productos
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        conexion.close()

# ============================================================
# ADMIN - AGREGAR PRODUCTO
# ============================================================

@app.route("/admin/productos/agregar", methods=["POST"])
def agregar_producto_admin():

    datos = datos_json()

    if not datos:
        return error_json(
            "No se recibieron datos."
        )

    nombre = normalizar_texto(
        datos.get("nombre")
    )

    categoria = normalizar_texto(
        datos.get("categoria")
    )

    imagen = normalizar_texto(
        datos.get("imagen")
    )

    try:
        precio = decimal_seguro(
            datos.get("precio")
        )

        stock = entero_seguro(
            datos.get("stock"),
            "stock"
        )

        rating = decimal_seguro(
            datos.get("rating", 5)
        )

    except ValueError as e:

        return error_json(
            str(e)
        )

    if not nombre:
        return error_json(
            "El nombre es obligatorio."
        )

    if not categoria:
        return error_json(
            "La categoría es obligatoria."
        )

    if precio < 0:
        return error_json(
            "El precio no puede ser negativo."
        )

    if stock < 0:
        return error_json(
            "El stock no puede ser negativo."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO productos
            (
                nombre,
                precio,
                categoria,
                imagen,
                stock,
                rating
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            nombre,
            precio,
            categoria,
            imagen,
            stock,
            rating
        ))

        id_producto = cursor.lastrowid

        conexion.commit()

        return ok_json(
            "Producto agregado correctamente.",
            id_producto=id_producto
        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "ADMIN AGREGAR PRODUCTO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# ADMIN - EDITAR PRODUCTO
# ============================================================

@app.route(
    "/admin/productos/<int:id_producto>",
    methods=["PUT"]
)
def editar_producto_admin(id_producto):

    datos = datos_json()

    if not datos:
        return error_json(
            "No se recibieron datos."
        )

    nombre = normalizar_texto(
        datos.get("nombre")
    )

    categoria = normalizar_texto(
        datos.get("categoria")
    )

    imagen = normalizar_texto(
        datos.get("imagen")
    )

    try:

        precio = decimal_seguro(
            datos.get("precio")
        )

        stock = entero_seguro(
            datos.get("stock"),
            "stock"
        )

        rating = decimal_seguro(
            datos.get("rating", 5)
        )

    except ValueError as e:

        return error_json(
            str(e)
        )

    if not nombre:
        return error_json(
            "El nombre es obligatorio."
        )

    if not categoria:
        return error_json(
            "La categoría es obligatoria."
        )

    if precio < 0:
        return error_json(
            "El precio no puede ser negativo."
        )

    if stock < 0:
        return error_json(
            "El stock no puede ser negativo."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET
                nombre = %s,
                precio = %s,
                categoria = %s,
                imagen = %s,
                stock = %s,
                rating = %s
            WHERE id_producto = %s
        """, (
            nombre,
            precio,
            categoria,
            imagen,
            stock,
            rating,
            id_producto
        ))

        if cursor.rowcount == 0:

            return error_json(
                "El producto no existe.",
                404
            )

        conexion.commit()

        return ok_json(
            "Producto actualizado correctamente.",
            id_producto=id_producto
        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "ADMIN EDITAR PRODUCTO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# ADMIN - ELIMINAR PRODUCTO
# ============================================================

@app.route(
    "/admin/productos/<int:id_producto>",
    methods=["DELETE"]
)
def eliminar_producto_admin(id_producto):

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        # Primero comprobamos si existe

        cursor.execute("""
            SELECT
                id_producto
            FROM productos
            WHERE id_producto = %s
            LIMIT 1
        """, (
            id_producto,
        ))

        producto = cursor.fetchone()

        if not producto:

            return error_json(
                "El producto no existe.",
                404
            )

        # Comprobar si está relacionado
        # con algún detalle de pedido

        cursor.execute("""
            SELECT
                COUNT(*) AS cantidad
            FROM detalles_pedidos
            WHERE id_producto = %s
        """, (
            id_producto,
        ))

        relacion = cursor.fetchone()

        if relacion and relacion["cantidad"] > 0:

            return error_json(
                "No se puede eliminar este producto porque tiene pedidos relacionados."
            )

        cursor.execute("""
            DELETE FROM productos
            WHERE id_producto = %s
        """, (
            id_producto,
        ))

        conexion.commit()

        return ok_json(
            "Producto eliminado correctamente.",
            id_producto=id_producto
        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "ADMIN ELIMINAR PRODUCTO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# ADMIN - CAMBIAR ESTADO DEL PEDIDO
# ============================================================

@app.route(
    "/admin/pedidos/<int:id_pedido>/estado",
    methods=["PUT"]
)
def cambiar_estado_pedido_admin(id_pedido):

    datos = datos_json()

    if not datos:
        return error_json(
            "No se recibieron datos."
        )

    estado = normalizar_texto(
        datos.get("estado")
    )

    estados_validos = {
        "Pendiente",
        "Pagado",
        "Preparando",
        "Enviado",
        "Entregado",
        "Cancelado"
    }

    if estado not in estados_validos:

        return error_json(
            "Estado de pedido no válido."
        )

    conexion = None
    cursor = None

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_pedido
            FROM pedidos
            WHERE id_pedido = %s
            LIMIT 1
        """, (
            id_pedido,
        ))

        pedido = cursor.fetchone()

        if not pedido:

            return error_json(
                "El pedido no existe.",
                404
            )

        cursor.execute("""
            UPDATE pedidos
            SET estado = %s
            WHERE id_pedido = %s
        """, (
            estado,
            id_pedido
        ))

        conexion.commit()

        return ok_json(
            "Estado del pedido actualizado.",
            id_pedido=id_pedido,
            estado=estado
        )

    except Exception as e:

        if conexion:
            conexion.rollback()

        registrar_error(
            "ADMIN CAMBIAR ESTADO PEDIDO",
            e
        )

        return error_json(
            str(e),
            500
        )

    finally:

        cerrar_db(
            conexion,
            cursor
        )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )


