// ================= PRODUCTOS =================

const productos = productosBD;

console.log("Productos recibidos desde MySQL:", productos);



// ======================================================
// CARRITO
// ======================================================

let carrito = JSON.parse(
    localStorage.getItem("carrito")
) || [];

if (!Array.isArray(carrito)) {
    carrito = [];
}

carrito = carrito.map(p => ({
    ...p,
    cantidad: Number(p.cantidad) > 0
        ? Number(p.cantidad)
        : 1,
    precio: Number(p.precio) || 0
}));

let total = 0;


// ======================================================
// MOSTRAR PRODUCTOS
// ======================================================

function mostrar(lista) {

    const cont = document.getElementById("productos");

    if (!cont) return;

    cont.innerHTML = "";

    if (!Array.isArray(lista) || lista.length === 0) {

        cont.innerHTML = `
            <p class="sin-productos">
                No hay productos disponibles.
            </p>
        `;

        return;
    }

    lista.forEach(p => {

        const imagen = p.imagen
            ? `/static/img/${encodeURIComponent(p.imagen)}`
            : "";

        cont.innerHTML += `

        <div class="card">

            <img
                src="${imagen}"
                alt="${p.nombre}"
                onerror="this.style.display='none'"
            >

            <h3>
                ${p.nombre}
            </h3>

            <div class="stars">
                ${estrellas(p.rating)}
            </div>

            <p class="precio">
                $${Number(p.precio).toLocaleString("es-CO")}
            </p>

            ${
                p.tallas
                ?
                `
                <div class="tallas">

                    ${p.tallas.map(t => `
                        <span
                            onclick="seleccionarTalla(this)"
                        >
                            ${t}
                        </span>
                    `).join("")}

                </div>
                `
                :
                ""
            }

            ${
                p.suelas
                ?
                `
                <div class="tallas">

                    ${p.suelas.map(s => `
                        <span
                            onclick="seleccionarTalla(this)"
                        >
                            ${s}
                        </span>
                    `).join("")}

                </div>
                `
                :
                ""
            }

            ${
                p.colores
                ?
                `
                <div class="colores">

                    ${p.colores.map(c => `
                        <span
                            onclick="seleccionarColor(this)"
                        >
                            ${c}
                        </span>
                    `).join("")}

                </div>
                `
                :
                ""
            }

            <button
                type="button"
                class="add"
                onclick='agregarProducto(
                    this,
                    ${JSON.stringify(p.nombre)},
                    ${Number(p.precio)},
                    ${JSON.stringify(imagen)},
                    ${Number(p.id_producto)}
                )'
            >
                Agregar
            </button>

        </div>

        `;

    });

}


// ======================================================
// ESTRELLAS
// ======================================================

function estrellas(rating) {

    const valor = Number(rating) || 0;

    let resultado = "";

    for (let i = 1; i <= 5; i++) {

        resultado += i <= valor
            ? "★"
            : "☆";

    }

    return resultado;
}


// ======================================================
// SELECCIONAR TALLA / SUELA
// ======================================================

function seleccionarTalla(elemento) {

    const grupo = elemento.parentElement;

    grupo
        .querySelectorAll("span")
        .forEach(span =>
            span.classList.remove("active")
        );

    elemento.classList.add("active");
}


// ======================================================
// SELECCIONAR COLOR
// ======================================================

function seleccionarColor(elemento) {

    const grupo = elemento.parentElement;

    grupo
        .querySelectorAll("span")
        .forEach(span =>
            span.classList.remove("active")
        );

    elemento.classList.add("active");
}


// ======================================================
// AGREGAR PRODUCTO
// ======================================================

function agregarProducto(
    btn,
    nombre,
    precio,
    img,
    idProducto
) {

    const card = btn.parentElement;

    let talla = "";
    let color = "";

    const tallaActiva =
        card.querySelector(".tallas .active");

    const colorActivo =
        card.querySelector(".colores .active");

    if (tallaActiva) {
        talla = tallaActiva.innerText.trim();
    }

    if (colorActivo) {
        color = colorActivo.innerText.trim();
    }


    // ==================================================
    // VALIDAR TALLA
    // ==================================================

    if (
        card.querySelector(".tallas") &&
        talla === ""
    ) {

        toast(
            "Selecciona una talla o suela ⚠️"
        );

        return;
    }


    // ==================================================
    // BUSCAR PRODUCTO EXISTENTE
    // ==================================================

    const existe =
        carrito.find(p =>
            Number(p.id_producto) ===
                Number(idProducto)

            &&

            p.talla === talla

            &&

            p.color === color
        );


    // ==================================================
    // AUMENTAR CANTIDAD
    // ==================================================

    if (existe) {

        existe.cantidad++;

    }


    // ==================================================
    // AGREGAR PRODUCTO NUEVO
    // ==================================================

    else {

        carrito.push({

            id_producto:
                Number(idProducto),

            nombre:
                nombre,

            precio:
                Number(precio),

            img:
                img,

            talla:
                talla,

            color:
                color,

            cantidad:
                1
        });

    }


    actualizar();

    actualizarContador();

    toast(
        "Producto agregado al carrito 🛒"
    );
}


// ======================================================
// ACTUALIZAR CARRITO
// ======================================================

function actualizar() {

    const lista =
        document.getElementById("lista");

    if (!lista) return;


    // ============================
    // CALCULAR TOTAL
    // ============================

    total = carrito.reduce(
        (suma, producto) => {

            return suma +
                (
                    Number(producto.precio) *
                    Number(producto.cantidad)
                );

        },
        0
    );


    // ============================
    // LIMPIAR LISTA
    // ============================

    lista.innerHTML = "";


    // ============================
    // CARRITO VACÍO
    // ============================

    if (carrito.length === 0) {

        lista.innerHTML = `
            <div class="carrito-vacio">
                <p>🛒 Tu carrito está vacío</p>
                <p>Agrega productos para comenzar.</p>
            </div>
        `;

    }


    // ============================
    // MOSTRAR PRODUCTOS
    // ============================

    carrito.forEach((p, i) => {

        lista.innerHTML += `

        <div class="cart-item">

            <img
                src="${p.img || ""}"
                alt="${p.nombre}"
                onerror="this.style.display='none'"
            >

            <div class="cart-info">

                <p>
                    <strong>
                        ${p.nombre}
                    </strong>
                </p>

                <p>
                    $${Number(p.precio).toLocaleString("es-CO")}
                </p>

                ${
                    p.talla
                    ?
                    `<p>
                        Talla/Suela: ${p.talla}
                    </p>`
                    :
                    ""
                }

                ${
                    p.color
                    ?
                    `<p>
                        Color: ${p.color}
                    </p>`
                    :
                    ""
                }

                <div class="cantidad">

                    <button
                        type="button"
                        onclick="cambiarCantidad(${i}, -1)"
                    >
                        −
                    </button>

                    <span>
                        ${p.cantidad}
                    </span>

                    <button
                        type="button"
                        onclick="cambiarCantidad(${i}, 1)"
                    >
                        +
                    </button>

                </div>

            </div>

            <button
                type="button"
                class="btn-eliminar"
                onclick="eliminar(${i})"
            >
                ❌
            </button>

        </div>

        `;

    });


    // ============================
    // MOSTRAR TOTAL
    // ============================

    const totalElemento =
        document.getElementById("total");

    if (totalElemento) {

        totalElemento.textContent =
            total.toLocaleString("es-CO");

    }


    // ============================
    // GUARDAR CARRITO
    // ============================

    localStorage.setItem(
        "carrito",
        JSON.stringify(carrito)
    );

}


// ======================================================
// CAMBIAR CANTIDAD
// ======================================================

function cambiarCantidad(indice, cambio) {

    if (!carrito[indice]) return;

    carrito[indice].cantidad += cambio;

    if (
        carrito[indice].cantidad <= 0
    ) {

        carrito.splice(indice, 1);

    }

    actualizar();

    actualizarContador();
}


// ======================================================
// ELIMINAR PRODUCTO
// ======================================================

function eliminar(indice) {

    if (!carrito[indice]) return;

    carrito.splice(indice, 1);

    actualizar();

    actualizarContador();

    toast(
        "Producto eliminado 🗑️"
    );
}


// ======================================================
// VACIAR CARRITO
// ======================================================

function vaciarCarrito() {

    carrito = [];

    actualizar();

    actualizarContador();

    toast(
        "Carrito vacío 🛒"
    );
}


// ======================================================
// CONTADOR DEL CARRITO
// ======================================================

function actualizarContador() {

    const contador =
        document.getElementById("contador");

    if (!contador) return;

    const cantidad =
        carrito.reduce(
            (suma, producto) =>
                suma +
                Number(producto.cantidad),
            0
        );

    contador.textContent =
        cantidad;
}


// ======================================================
// ABRIR / CERRAR CARRITO
// ======================================================

function toggleCart() {

    const carritoElemento =
        document.getElementById("carrito");

    const overlay =
        document.getElementById("overlay");

    if (!carritoElemento) return;

    carritoElemento.classList.toggle(
        "active"
    );

    if (overlay) {

        overlay.classList.toggle(
            "active"
        );

    }

}


// ======================================================
// BUSCADOR
// ======================================================

function buscarProductos(texto) {

    const busqueda =
        texto.toLowerCase().trim();

    if (busqueda === "") {

        mostrar(productos);

        return;
    }

    const resultados =
        productos.filter(p =>

            String(p.nombre)
                .toLowerCase()
                .includes(busqueda)

            ||

            String(p.categoria)
                .toLowerCase()
                .includes(busqueda)

        );

    mostrar(resultados);
}


// ======================================================
// MOSTRAR TODOS
// ======================================================

function mostrarTodos() {

    mostrar(productos);

    const seccion =
        document.getElementById(
            "productos-section"
        );

    if (seccion) {

        seccion.scrollIntoView({
            behavior: "smooth"
        });

    }

}


// ======================================================
// FILTRAR CATEGORÍA
// ======================================================

function filtrar(categoria) {

    const resultados =
        productos.filter(p =>
            String(p.categoria)
                .toLowerCase()
                === categoria.toLowerCase()
        );

    mostrar(resultados);

    const seccion =
        document.getElementById(
            "productos-section"
        );

    if (seccion) {

        seccion.scrollIntoView({
            behavior: "smooth"
        });

    }

}


// ======================================================
// SCROLL PRODUCTOS
// ======================================================

function scrollProductos() {

    const seccion =
        document.getElementById(
            "productos-section"
        );

    if (seccion) {

        seccion.scrollIntoView({
            behavior: "smooth"
        });

    }

}


// ======================================================
// TOAST
// ======================================================

function toast(mensaje) {

    const elemento =
        document.getElementById("toast");

    if (!elemento) return;

    elemento.textContent =
        mensaje;

    elemento.classList.add(
        "show"
    );

    setTimeout(() => {

        elemento.classList.remove(
            "show"
        );

    }, 2500);

}


// ======================================================
// LOGIN
// ======================================================

function abrirLogin() {

    const login =
        document.getElementById("login");

    if (!login) return;

    login.classList.remove(
        "hidden"
    );

}


function cerrarLogin() {

    const login =
        document.getElementById("login");

    if (!login) return;

    login.classList.add(
        "hidden"
    );

}


function mostrarRegistro() {

    const loginForm =
        document.getElementById(
            "loginForm"
        );

    const registerForm =
        document.getElementById(
            "registerForm"
        );

    if (loginForm)
        loginForm.classList.add(
            "hidden"
        );

    if (registerForm)
        registerForm.classList.remove(
            "hidden"
        );

}


function mostrarLogin() {

    const loginForm =
        document.getElementById(
            "loginForm"
        );

    const registerForm =
        document.getElementById(
            "registerForm"
        );

    if (loginForm)
        loginForm.classList.remove(
            "hidden"
        );

    if (registerForm)
        registerForm.classList.add(
            "hidden"
        );

}

// ======================================================
// MIS PEDIDOS
// ======================================================

function verMisPedidos() {

    const idCliente =
        Number(localStorage.getItem("id_cliente"));

    if (!idCliente) {

        toast("Inicia sesión primero 👤");

        return;
    }

    cerrarPerfil();

    const modal =
        document.getElementById("misPedidos");

    const lista =
        document.getElementById("listaPedidos");

    if (!modal || !lista) return;

    modal.classList.remove("hidden");

    lista.innerHTML =
        "<p>Cargando pedidos...</p>";

    fetch(`/mis-pedidos/${idCliente}`)

        .then(res => res.json())

        .then(data => {

            if (data.error) {

                lista.innerHTML =
                    `<p>Error: ${data.error}</p>`;

                return;
            }

            if (
                !data.pedidos ||
                data.pedidos.length === 0
            ) {

                lista.innerHTML = `
                    <p>
                        Todavía no tienes pedidos.
                    </p>
                `;

                return;
            }

            lista.innerHTML = "";

            data.pedidos.forEach(pedido => {

                lista.innerHTML += `

                    <div class="pedido">

                        <h3>
                            Pedido #${pedido.id_pedido}
                        </h3>

                        <p>
                            Estado:
                            <strong>
                                ${pedido.estado}
                            </strong>
                        </p>

                        <p>
                            Total:
                            $${Number(
                                pedido.total
                            ).toLocaleString("es-CO")}
                        </p>

                    </div>

                `;

            });

        })

        .catch(error => {

            console.error(
                "ERROR PEDIDOS:",
                error
            );

            lista.innerHTML = `
                <p>
                    No se pudieron cargar los pedidos.
                </p>
            `;

        });
}


// ======================================================
// CERRAR MIS PEDIDOS
// ======================================================

function cerrarMisPedidos() {

    const modal =
        document.getElementById("misPedidos");

    if (modal) {

        modal.classList.add("hidden");

    }
}

// ======================================================
// CREAR CUENTA EN MYSQL
// ======================================================

function crearCuenta() {

    const nombre = document.getElementById("registerNombre")?.value.trim() || "";
    const apellido = document.getElementById("registerApellido")?.value.trim() || "";
    const correo = document.getElementById("registerCorreo")?.value.trim() || "";
    const contrasena = document.getElementById("registerPass")?.value.trim() || "";
    const telefono = document.getElementById("registerTelefono")?.value.trim() || "";
    const direccion = document.getElementById("registerDireccion")?.value.trim() || "";
    const ciudad = document.getElementById("registerCiudad")?.value.trim() || "";

    if (!nombre || !apellido || !correo || !contrasena) {
        toast("Completa nombre, apellido, correo y contraseña ⚠️");
        return;
    }

    if (!/^\S+@\S+\.\S+$/.test(correo)) {
        toast("Escribe un correo válido ⚠️");
        return;
    }

    if (contrasena.length < 4) {
        toast("La contraseña debe tener mínimo 4 caracteres ⚠️");
        return;
    }

    fetch("/registro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nombre: nombre,
            apellido: apellido,
            correo: correo,
            "contraseña": contrasena,
            telefono: telefono,
            direccion: direccion,
            ciudad: ciudad
        })
    })
    .then(async res => {
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "No se pudo crear la cuenta");
        }
        return data;
    })
    .then(() => {
        toast("Cuenta creada correctamente ✅");

        const loginUser = document.getElementById("loginUser");
        if (loginUser) loginUser.value = correo;

        [
            "registerNombre",
            "registerApellido",
            "registerCorreo",
            "registerPass",
            "registerTelefono",
            "registerDireccion",
            "registerCiudad"
        ].forEach(id => {
            const campo = document.getElementById(id);
            if (campo) campo.value = "";
        });

        mostrarLogin();
    })
    .catch(error => {
        console.error("ERROR REGISTRO:", error);
        toast("❌ " + error.message);
    });
}


// ======================================================
// INICIAR SESIÓN CON MYSQL
// ======================================================

function login() {

    const userInput =
        document.getElementById("loginUser");

    const passInput =
        document.getElementById("loginPass");


    if (!userInput || !passInput) {

        toast("No se encontraron los campos ⚠️");

        return;
    }


    const correo =
        userInput.value.trim();

    const contrasena =
        passInput.value.trim();


    if (!correo || !contrasena) {

        toast("Completa los datos ⚠️");

        return;
    }


    fetch("/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            correo: correo,

            contrasena: contrasena

        })

    })

    .then(res => res.json())

    .then(data => {

        if (data.error) {

            toast(
                "❌ " + data.error
            );

            return;
        }


        // Guardar información REAL del cliente

        localStorage.setItem(
            "usuario",
            data.correo
        );

        localStorage.setItem(
            "id_cliente",
            data.id_cliente
        );

        localStorage.setItem(
            "rol",
            data.rol
        );

        localStorage.setItem(
            "nombre_cliente",
            data.nombre
        );

        localStorage.setItem(
            "apellido_cliente",
            data.apellido
        );


        toast(
            "Bienvenido " +
            data.nombre +
            " 👋"
        );


        cerrarLogin();

        actualizarUsuario();

    })

    .catch(error => {

        console.error(
            "ERROR LOGIN:",
            error
        );

        toast(
            "No se pudo conectar con el servidor ❌"
        );

    });

}


// ======================================================
// ACTUALIZAR USUARIO
// ======================================================

function actualizarUsuario() {

    const usuario =
        localStorage.getItem("usuario");

    const nombre =
        localStorage.getItem("nombre_cliente");


    const icono =
        document.getElementById("icon-user");


    if (!icono) return;


    if (usuario) {

        icono.textContent = "👤";

        icono.title =
            "Perfil de " +
            (nombre || usuario);

    } else {

        icono.textContent = "👤";

        icono.title =
            "Iniciar sesión";
    }
}


// ======================================================
// CERRAR SESIÓN
// ======================================================

function cerrarSesion() {

    localStorage.removeItem("usuario");

    localStorage.removeItem("id_cliente");

    localStorage.removeItem("nombre_cliente");

    localStorage.removeItem("apellido_cliente");

    localStorage.removeItem("rol");


    cerrarPerfil();

    actualizarUsuario();


    toast(
        "Sesión cerrada correctamente 👋"
    );
}


// ======================================================
// MODO OSCURO
// ======================================================

function toggleDarkMode() {

    document.body.classList.toggle(
        "dark"
    );

    const activo =
        document.body.classList.contains(
            "dark"
        );

    localStorage.setItem(
        "darkMode",
        activo
    );

}


// ======================================================
// CARRUSEL
// ======================================================

let slideActual = 0;

function iniciarCarrusel() {

    const slides =
        document.querySelectorAll(
            ".hero-slide"
        );

    if (!slides.length) return;

    slides.forEach(slide =>
        slide.classList.remove(
            "active"
        )
    );

    slides[slideActual]
        .classList.add("active");

    setInterval(() => {

        slides[slideActual]
            .classList.remove(
                "active"
            );

        slideActual++;

        if (
            slideActual >=
            slides.length
        ) {

            slideActual = 0;

        }

        slides[slideActual]
            .classList.add(
                "active"
            );

    }, 5000);

}


// ======================================================
// PAGO
// ======================================================

function abrirPago() {

    if (carrito.length === 0) {

        toast(
            "El carrito está vacío 🛒"
        );

        return;
    }

    const usuario =
        localStorage.getItem("usuario");

    const idCliente =
        localStorage.getItem("id_cliente");

    if (!usuario || !idCliente) {

        toast(
            "Inicia sesión antes de comprar 👤"
        );

        return;
    }

    const pago =
        document.getElementById("pago");

    if (pago) {

        pago.classList.remove(
            "hidden"
        );

    }

}


// ======================================================
// CERRAR PAGO
// ======================================================

function cerrarPago() {

    const pago =
        document.getElementById("pago");

    if (pago) {

        pago.classList.add(
            "hidden"
        );

    }

}


// ======================================================
// CONFIRMAR PAGO
// ======================================================

function confirmarPago() {

    if (carrito.length === 0) {

        toast("El carrito está vacío 🛒");

        return;
    }


    const usuario =
        localStorage.getItem("usuario");

    const idCliente =
        Number(
            localStorage.getItem("id_cliente")
        );


    if (!usuario || !idCliente || idCliente <= 0) {

        toast(
            "Inicia sesión antes de comprar 👤"
        );

        return;
    }


    const nombrePago =
        document.getElementById("nombrePago");

    const metodoPago =
        document.getElementById("metodoPago");


    if (!nombrePago || !metodoPago) {

        toast(
            "Faltan campos de pago ⚠️"
        );

        return;
    }


    const nombre =
        nombrePago.value.trim();

    const metodo =
        metodoPago.value;


    if (!nombre) {

        toast(
            "Escribe el nombre completo ⚠️"
        );

        return;
    }


    if (!metodo) {

        toast(
            "Selecciona un método de pago ⚠️"
        );

        return;
    }


    // ==================================================
    // CALCULAR TOTAL
    // ==================================================

    const totalCompra =
        carrito.reduce(
            (suma, producto) => {

                return suma +
                    (
                        Number(producto.precio) *
                        Number(producto.cantidad)
                    );

            },
            0
        );


    if (totalCompra <= 0) {

        toast(
            "El total de la compra no es válido ⚠️"
        );

        return;
    }


    // ==================================================
    // DESACTIVAR BOTÓN
    // ==================================================

    const boton =
        document.querySelector(
            "#pago button[type='submit'], #pago .btn-confirmar"
        );

    if (boton) {

        boton.disabled = true;

        boton.textContent =
            "Procesando...";

    }


    // ==================================================
    // CREAR PEDIDO
    // ==================================================

    fetch("/crear-pedido", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            id_cliente:
                idCliente,

            productos:
                carrito.map(p => ({

                    id_producto:
                        Number(p.id_producto),

                    precio:
                        Number(p.precio),

                    cantidad:
                        Number(p.cantidad),

                    talla:
                        p.talla || "",

                    color:
                        p.color || ""

                }))

        })

    })

    .then(res => {

        if (!res.ok) {

            throw new Error(
                "No se pudo crear el pedido"
            );

        }

        return res.json();

    })

    .then(data => {

        if (data.error) {

            throw new Error(
                data.error
            );

        }


        const idPedido =
            Number(data.id_pedido);


        const totalServidor =
            Number(data.total);


        if (!idPedido) {

            throw new Error(
                "El servidor no devolvió el ID del pedido"
            );

        }


        const montoPago =
            totalServidor > 0
                ? totalServidor
                : totalCompra;


        // ==================================================
        // REGISTRAR PAGO
        // ==================================================

        return fetch("/registrar-pago", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                id_pedido:
                    idPedido,

                metodo_pago:
                    metodo,

                monto:
                    montoPago

            })

        })

        .then(res => {

            if (!res.ok) {

                throw new Error(
                    "No se pudo registrar el pago"
                );

            }

            return res.json();

        })

        .then(pago => {

            if (pago.error) {

                throw new Error(
                    pago.error
                );

            }


            // ==================================================
            // GENERAR FACTURA
            // ==================================================

            return generarFactura(
                idPedido
            );

        })

        .then(() => {

            // ==================================================
            // VACIAR CARRITO
            // ==================================================

            carrito = [];

            localStorage.setItem(
                "carrito",
                JSON.stringify(carrito)
            );

            actualizar();

            actualizarContador();


            // ==================================================
            // CERRAR PAGO
            // ==================================================

            cerrarPago();


            // ==================================================
            // LIMPIAR FORMULARIO
            // ==================================================

            nombrePago.value = "";

            metodoPago.value = "";


            toast(
                "Compra realizada correctamente ✅"
            );

        });

    })

    .catch(error => {

        console.error(
            "ERROR EN EL PAGO:",
            error
        );

        toast(
            error.message ||
            "No se pudo realizar la compra ❌"
        );

    })

    .finally(() => {

        if (boton) {

            boton.disabled = false;

            boton.textContent =
                "Confirmar pago";

        }

    });

}


// ======================================================
// GENERAR FACTURA
// ======================================================

function generarFactura(idPedido) {

    if (!idPedido) {

        return Promise.reject(
            new Error(
                "No existe el ID del pedido"
            )
        );

    }


    return fetch(
        `/generar-factura/${idPedido}`,
        {
            method: "GET"
        }
    )

    .then(res => {

        if (!res.ok) {

            throw new Error(
                "No se pudo generar la factura"
            );

        }

        return res.blob();

    })

    .then(blob => {

        if (!blob || blob.size === 0) {

            throw new Error(
                "La factura está vacía"
            );

        }


        const url =
            window.URL.createObjectURL(blob);


        const enlace =
            document.createElement("a");

        enlace.href = url;

        enlace.download =
            `factura_${idPedido}.pdf`;

        document.body.appendChild(
            enlace
        );

        enlace.click();

        enlace.remove();

        window.URL.revokeObjectURL(
            url
        );

    });

}


// ======================================================
// INICIO
// ======================================================

window.addEventListener(
    "DOMContentLoaded",
    function () {

        mostrar(productos);

        actualizar();

        actualizarContador();

        actualizarUsuario();

        iniciarCarrusel();


        // ==================================================
        // RESTAURAR MODO OSCURO
        // ==================================================

        if (
            localStorage.getItem(
                "darkMode"
            ) === "true"
        ) {

            document.body.classList.add(
                "dark"
            );

        }


        // ==================================================
        // BUSCADOR
        // ==================================================

        const buscador =
            document.querySelector(
                ".search input"
            );

        if (buscador) {

            buscador.addEventListener(
                "input",
                function () {

                    buscarProductos(
                        this.value
                    );

                }
            );

        }

    }
);

// ======================================================
// CERRAR FACTURA
// ======================================================

function cerrarFactura() {

    const factura = document.getElementById("factura");

    if (factura) {
        factura.classList.add("hidden");
    }

}

// ======================================================
// PERFIL DE USUARIO
// ======================================================

function abrirPerfilOLogin() {

    const usuario =
        localStorage.getItem("usuario");

    if (!usuario) {

        abrirLogin();

        return;
    }

    abrirPerfil();
}


// ======================================================
// ABRIR PERFIL
// ======================================================

function abrirPerfil() {

    const perfil =
        document.getElementById("perfil");

    if (!perfil) return;


    const nombre =
        localStorage.getItem("nombre_cliente") || "";

    const apellido =
        localStorage.getItem("apellido_cliente") || "";

    const correo =
        localStorage.getItem("usuario") || "";


    document.getElementById(
        "perfilNombre"
    ).textContent = nombre;


    document.getElementById(
        "perfilApellido"
    ).textContent = apellido;


    document.getElementById(
        "perfilCorreo"
    ).textContent = correo;


    perfil.classList.remove("hidden");
}


// ======================================================
// CERRAR PERFIL
// ======================================================

function cerrarPerfil() {

    const perfil =
        document.getElementById("perfil");

    if (perfil) {

        perfil.classList.add("hidden");

    }
}

// ======================================================
// IMPRIMIR FACTURA
// ======================================================

function imprimirFactura() {
    window.print();
}