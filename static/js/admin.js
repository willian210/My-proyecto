// ======================================================
// FLASHOP - PANEL ADMINISTRADOR
// ======================================================


// ======================================================
// MOSTRAR CONTENIDO
// ======================================================

function mostrarContenido(html) {

    const contenedor =
        document.getElementById("adminContenido");

    if (contenedor) {
        contenedor.innerHTML = html;
    }
}


// ======================================================
// PRODUCTOS
// ======================================================

function cargarProductosAdmin() {

    fetch("/admin/productos")

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                mostrarContenido(`
                    <p class="admin-error">
                        Error: ${data.error}
                    </p>
                `);

                return;
            }


            let html = `

                <div class="admin-titulo">

                    <h2>📦 Productos</h2>

                    <button
                        type="button"
                        class="btn-admin-agregar"
                        onclick="mostrarFormularioProducto()">

                        ➕ Agregar producto

                    </button>

                </div>


                <div class="tabla-contenedor">

                    <table>

                        <thead>

                            <tr>

                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Precio</th>
                                <th>Categoría</th>
                                <th>Stock</th>
                                <th>Acciones</th>

                            </tr>

                        </thead>

                        <tbody>
            `;


            if (
                !data.productos ||
                data.productos.length === 0
            ) {

                html += `

                    <tr>

                        <td colspan="6">

                            No hay productos registrados.

                        </td>

                    </tr>

                `;

            }


            data.productos.forEach(p => {

                html += `

                    <tr>

                        <td>
                            ${p.id_producto}
                        </td>

                        <td>
                            ${p.nombre}
                        </td>

                        <td>
                            $${Number(
                                p.precio
                            ).toLocaleString("es-CO")}
                        </td>

                        <td>
                            ${p.categoria || ""}
                        </td>

                        <td>
                            ${p.stock}
                        </td>

                        <td>

                            <button
                                type="button"
                                class="btn-editar"
                                onclick='mostrarFormularioProducto(
                                    ${JSON.stringify(p)}
                                )'>

                                ✏️ Editar

                            </button>


                            <button
                                type="button"
                                class="btn-eliminar"
                                onclick="eliminarProductoAdmin(
                                    ${Number(p.id_producto)}
                                )">

                                🗑️ Eliminar

                            </button>

                        </td>

                    </tr>

                `;

            });


            html += `

                        </tbody>

                    </table>

                </div>

            `;


            mostrarContenido(html);

        })

        .catch(error => {

            console.error(
                "ERROR PRODUCTOS:",
                error
            );

            mostrarContenido(`

                <p class="admin-error">

                    No se pudieron cargar los productos.

                </p>

            `);

        });

}


// ======================================================
// FORMULARIO PRODUCTO
// ======================================================

function mostrarFormularioProducto(producto = null) {

    const editar =
        producto !== null;


    const id =
        editar
            ? producto.id_producto
            : "";


    const nombre =
        editar
            ? producto.nombre
            : "";


    const precio =
        editar
            ? producto.precio
            : "";


    const categoria =
        editar
            ? producto.categoria
            : "";


    const imagen =
        editar
            ? producto.imagen || ""
            : "";


    const stock =
        editar
            ? producto.stock
            : "";


    const rating =
        editar
            ? producto.rating || 5
            : 5;


    mostrarContenido(`

        <div class="formulario-admin">

            <h2>
                ${editar
                    ? "✏️ Editar producto"
                    : "➕ Agregar producto"}
            </h2>


            <label>
                Nombre
            </label>

            <input
                type="text"
                id="adminNombre"
                value="${nombre}"
                placeholder="Nombre del producto"
            >


            <label>
                Precio
            </label>

            <input
                type="number"
                id="adminPrecio"
                value="${precio}"
                min="0"
                step="0.01"
                placeholder="Precio"
            >


            <label>
                Categoría
            </label>

            <select id="adminCategoria">

                <option value="">
                    Selecciona categoría
                </option>

                <option
                    value="ropa"
                    ${categoria === "ropa" ? "selected" : ""}>
                    Ropa
                </option>

                <option
                    value="calzado"
                    ${categoria === "calzado" ? "selected" : ""}>
                    Calzado
                </option>

                <option
                    value="electronica"
                    ${categoria === "electronica" ? "selected" : ""}>
                    Electrónica
                </option>

                <option
                    value="accesorios"
                    ${categoria === "accesorios" ? "selected" : ""}>
                    Accesorios
                </option>

            </select>


            <label>
                Imagen
            </label>

            <input
                type="text"
                id="adminImagen"
                value="${imagen}"
                placeholder="ejemplo.jpg"
            >


            <label>
                Stock
            </label>

            <input
                type="number"
                id="adminStock"
                value="${stock}"
                min="0"
                step="1"
                placeholder="Cantidad"
            >


            <label>
                Rating
            </label>

            <input
                type="number"
                id="adminRating"
                value="${rating}"
                min="0"
                max="5"
                step="0.1"
            >


            <div class="admin-form-buttons">

                <button
                    type="button"
                    onclick="guardarProductoAdmin(
                        ${editar ? id : "null"}
                    )">

                    💾 Guardar

                </button>


                <button
                    type="button"
                    onclick="cargarProductosAdmin()">

                    ❌ Cancelar

                </button>

            </div>

        </div>

    `);

}


// ======================================================
// GUARDAR PRODUCTO
// ======================================================

function guardarProductoAdmin(idProducto) {

    const nombre =
        document.getElementById(
            "adminNombre"
        ).value.trim();


    const precio =
        Number(
            document.getElementById(
                "adminPrecio"
            ).value
        );


    const categoria =
        document.getElementById(
            "adminCategoria"
        ).value;


    const imagen =
        document.getElementById(
            "adminImagen"
        ).value.trim();


    const stock =
        Number(
            document.getElementById(
                "adminStock"
            ).value
        );


    const rating =
        Number(
            document.getElementById(
                "adminRating"
            ).value
        );


    if (!nombre) {

        alert(
            "Escribe el nombre del producto."
        );

        return;
    }


    if (
        Number.isNaN(precio) ||
        precio < 0
    ) {

        alert(
            "Escribe un precio válido."
        );

        return;
    }


    if (!categoria) {

        alert(
            "Selecciona una categoría."
        );

        return;
    }


    if (
        Number.isNaN(stock) ||
        stock < 0
    ) {

        alert(
            "Escribe un stock válido."
        );

        return;
    }


    const datos = {

        nombre: nombre,

        precio: precio,

        categoria: categoria,

        imagen: imagen,

        stock: stock,

        rating: rating

    };


    let url =
        "/admin/productos/agregar";


    let metodo =
        "POST";


    if (idProducto !== null) {

        url =
            `/admin/productos/${idProducto}`;

        metodo =
            "PUT";

    }


    fetch(url, {

        method: metodo,

        headers: {

            "Content-Type":
                "application/json"

        },

        body:
            JSON.stringify(datos)

    })

    .then(res => res.json())

    .then(data => {

        if (data.error) {

            alert(
                "Error: " +
                data.error
            );

            return;
        }


        alert(
            data.mensaje ||
            "Producto guardado correctamente."
        );


        cargarProductosAdmin();

    })

    .catch(error => {

        console.error(
            "ERROR GUARDANDO PRODUCTO:",
            error
        );

        alert(
            "No se pudo guardar el producto."
        );

    });

}


// ======================================================
// ELIMINAR PRODUCTO
// ======================================================

function eliminarProductoAdmin(idProducto) {

    const confirmar =
        confirm(
            "¿Seguro que quieres eliminar este producto?"
        );


    if (!confirmar) {
        return;
    }


    fetch(
        `/admin/productos/${idProducto}`,
        {
            method: "DELETE"
        }
    )

    .then(res => res.json())

    .then(data => {

        if (data.error) {

            alert(
                "Error: " +
                data.error
            );

            return;
        }


        alert(
            data.mensaje ||
            "Producto eliminado correctamente."
        );


        cargarProductosAdmin();

    })

    .catch(error => {

        console.error(
            "ERROR ELIMINANDO PRODUCTO:",
            error
        );

        alert(
            "No se pudo eliminar el producto."
        );

    });

}


// ======================================================
// CLIENTES
// ======================================================

function cargarClientesAdmin() {

    fetch("/admin/clientes")

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                mostrarContenido(`
                    <p class="admin-error">
                        Error: ${data.error}
                    </p>
                `);

                return;
            }


            let html = `

                <h2>👥 Clientes</h2>

                <div class="tabla-contenedor">

                    <table>

                        <thead>

                            <tr>

                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Correo</th>
                                <th>Rol</th>

                            </tr>

                        </thead>

                        <tbody>

            `;


            data.clientes.forEach(c => {

                html += `

                    <tr>

                        <td>
                            ${c.id_cliente}
                        </td>

                        <td>
                            ${c.nombre || ""}
                            ${c.apellido || ""}
                        </td>

                        <td>
                            ${c.correo || ""}
                        </td>

                        <td>
                            ${c.rol || ""}
                        </td>

                    </tr>

                `;

            });


            html += `

                        </tbody>

                    </table>

                </div>

            `;


            mostrarContenido(html);

        })

        .catch(error => {

            console.error(
                "ERROR CLIENTES:",
                error
            );

            mostrarContenido(`
                <p class="admin-error">
                    No se pudieron cargar los clientes.
                </p>
            `);

        });

}


// ======================================================
// PEDIDOS
// ======================================================

function cargarPedidosAdmin() {

    fetch("/admin/pedidos")

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                mostrarContenido(`
                    <p class="admin-error">
                        Error: ${data.error}
                    </p>
                `);

                return;
            }


            let html = `

                <h2>🛒 Pedidos</h2>

                <div class="tabla-contenedor">

                    <table>

                        <thead>

                            <tr>

                                <th>Pedido</th>
                                <th>Cliente</th>
                                <th>Estado</th>
                                <th>Total</th>
                                <th>Acción</th>

                            </tr>

                        </thead>

                        <tbody>

            `;


            data.pedidos.forEach(p => {

                html += `

                    <tr>

                        <td>
                            #${p.id_pedido}
                        </td>

                        <td>
                            ${p.nombre || ""}
                            ${p.apellido || ""}
                        </td>

                        <td>

                            <select
                                id="estado-${p.id_pedido}">

                                <option
                                    value="Pendiente"
                                    ${p.estado === "Pendiente"
                                        ? "selected"
                                        : ""}>
                                    Pendiente
                                </option>

                                <option
                                    value="Pagado"
                                    ${p.estado === "Pagado"
                                        ? "selected"
                                        : ""}>
                                    Pagado
                                </option>

                                <option
                                    value="Preparando"
                                    ${p.estado === "Preparando"
                                        ? "selected"
                                        : ""}>
                                    Preparando
                                </option>

                                <option
                                    value="Enviado"
                                    ${p.estado === "Enviado"
                                        ? "selected"
                                        : ""}>
                                    Enviado
                                </option>

                                <option
                                    value="Entregado"
                                    ${p.estado === "Entregado"
                                        ? "selected"
                                        : ""}>
                                    Entregado
                                </option>

                                <option
                                    value="Cancelado"
                                    ${p.estado === "Cancelado"
                                        ? "selected"
                                        : ""}>
                                    Cancelado
                                </option>

                            </select>

                        </td>

                        <td>

                            $${Number(
                                p.total
                            ).toLocaleString("es-CO")}

                        </td>

                        <td>

                            <button
                                type="button"
                                onclick="cambiarEstadoPedido(
                                    ${Number(p.id_pedido)}
                                )">

                                💾 Guardar

                            </button>

                        </td>

                    </tr>

                `;

            });


            html += `

                        </tbody>

                    </table>

                </div>

            `;


            mostrarContenido(html);

        })

        .catch(error => {

            console.error(
                "ERROR PEDIDOS:",
                error
            );

            mostrarContenido(`
                <p class="admin-error">
                    No se pudieron cargar los pedidos.
                </p>
            `);

        });

}


// ======================================================
// CAMBIAR ESTADO DEL PEDIDO
// ======================================================

function cambiarEstadoPedido(idPedido) {

    const select =
        document.getElementById(
            `estado-${idPedido}`
        );


    if (!select) {
        return;
    }


    const estado =
        select.value;


    fetch(
        `/admin/pedidos/${idPedido}/estado`,
        {

            method: "PUT",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body:
                JSON.stringify({
                    estado: estado
                })

        }
    )

    .then(res => res.json())

    .then(data => {

        if (data.error) {

            alert(
                "Error: " +
                data.error
            );

            return;
        }


        alert(
            "Estado actualizado correctamente."
        );


        cargarPedidosAdmin();

    })

    .catch(error => {

        console.error(
            "ERROR ESTADO PEDIDO:",
            error
        );

        alert(
            "No se pudo actualizar el pedido."
        );

    });

}


// ======================================================
// PAGOS
// ======================================================

function cargarPagosAdmin() {

    fetch("/admin/pagos")

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                mostrarContenido(`
                    <p class="admin-error">
                        Error: ${data.error}
                    </p>
                `);

                return;
            }


            let html = `

                <h2>💳 Pagos</h2>

                <div class="tabla-contenedor">

                    <table>

                        <thead>

                            <tr>

                                <th>ID</th>
                                <th>Pedido</th>
                                <th>Método</th>
                                <th>Monto</th>
                                <th>Estado</th>

                            </tr>

                        </thead>

                        <tbody>

            `;


            data.pagos.forEach(p => {

                html += `

                    <tr>

                        <td>
                            ${p.id_pago}
                        </td>

                        <td>
                            #${p.id_pedido}
                        </td>

                        <td>
                            ${p.metodo_pago}
                        </td>

                        <td>
                            $${Number(
                                p.monto
                            ).toLocaleString("es-CO")}
                        </td>

                        <td>
                            ${p.estado}
                        </td>

                    </tr>

                `;

            });


            html += `

                        </tbody>

                    </table>

                </div>

            `;


            mostrarContenido(html);

        })

        .catch(error => {

            console.error(
                "ERROR PAGOS:",
                error
            );

            mostrarContenido(`
                <p class="admin-error">
                    No se pudieron cargar los pagos.
                </p>
            `);

        });

}


// ======================================================
// STOCK
// ======================================================

function cargarStockAdmin() {

    fetch("/admin/stock")

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                mostrarContenido(`
                    <p class="admin-error">
                        Error: ${data.error}
                    </p>
                `);

                return;
            }


            let html = `

                <h2>📊 Stock</h2>

                <div class="tabla-contenedor">

                    <table>

                        <thead>

                            <tr>

                                <th>ID</th>
                                <th>Producto</th>
                                <th>Stock</th>

                            </tr>

                        </thead>

                        <tbody>

            `;


            data.productos.forEach(p => {

                html += `

                    <tr>

                        <td>
                            ${p.id_producto}
                        </td>

                        <td>
                            ${p.nombre}
                        </td>

                        <td>
                            ${p.stock}
                        </td>

                    </tr>

                `;

            });


            html += `

                        </tbody>

                    </table>

                </div>

            `;


            mostrarContenido(html);

        })

        .catch(error => {

            console.error(
                "ERROR STOCK:",
                error
            );

            mostrarContenido(`
                <p class="admin-error">
                    No se pudo cargar el stock.
                </p>
            `);

        });

}


// ======================================================
// SALIR
// ======================================================

function salirAdmin() {

    window.location.href = "/";

}