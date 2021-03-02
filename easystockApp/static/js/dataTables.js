$(document).ready(function() {
    // template: listar_productos.html / stock
    $('#listaProductos').DataTable({
        "scrollCollapse": true,
        "bInfo": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con productos en el stock",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay productos disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ productos)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_productos_template_stock/",
        "columns": [
            { "data": "obs" },
            { "data": "distribuidor" },
            { "data": "clasificacion" },
            { "data": "marca" },
            { "data": "descripcion" },
            { "data": "presentacion" },
            { "data": "precio_venta" },
            { "data": "cantidad" },
            { "data": "agregar" },
            { "data": "editar" },
            { "data": "eliminar" }
        ],
        "columnDefs": [
            {"className": "obs", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "texto", "targets": [2]},
            {"className": "texto marca", "targets": [3]},
            {"className": "texto desc", "targets": [4]},
            {"className": "texto pres", "targets": [5]},
            {"className": "monto precio", "targets": [6]},
            {"className": "cantidad", "targets": [7]},
            {"className": "input", "targets": [8]},
            {"className": "input", "targets": [9]},
            {"className": "input", "targets": [10]}
        ]
    });

    // template: registrar_venta.html
    $('#listaProductosModal').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con productos en el stock",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay productos disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ productos)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_productos_modal/",
        "columns": [
            { "data": "obs" },
            { "data": "clasificacion" },
            { "data": "marca" },
            { "data": "descripcion" },
            { "data": "presentacion" },
            { "data": "precio_venta" },
            { "data": "cantidad" },
            { "data": "agregar" }
        ],
        "columnDefs": [
            {"className": "obs", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "texto marca", "targets": [2]},
            {"className": "texto desc", "targets": [3]},
            {"className": "texto pres", "targets": [4]},
            {"className": "monto precio", "targets": [5]},
            {"className": "cantidad", "targets": [6]},
            {"className": "input", "targets": [7]}
        ]
    });

    //template: registrar_venta.html
    $('#listaPromocionesModal').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con promociones creadas",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay promociones disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ promociones)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_promociones_modal_template_registro_venta/",
        "columns": [
            { "data": "obs" },
            { "data": "descripcion" },
            { "data": "info_extra" },
            { "data": "precio_venta_con_descuento" },
            { "data": "cantidad" },
            { "data": "agregar" }
        ],
        "columnDefs": [
            {"className": "obs", "targets": [0]},
            {"className": "texto desc", "targets": [1]},
            {"className": "texto", "targets": [2]},
            {"className": "monto precio", "targets": [3]},
            {"className": "cantidad", "targets": [4]},
            {"className": "input", "targets": [5]}
        ]
    });

    // template: listar_productos.html / stock
    $('#listaPromociones').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con promociones creadas",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay promociones disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ promociones)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        }
    });

    // template: nuevo_producto.html
    $('#listaUltimosProductos').DataTable({
        "ordering": false,
        "paging": false,
        "info": false,
        "searching": false,
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con productos en el stock",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay productos disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ productos)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        }
    });

    // template: listar_clientes.html
    $('#listaClientes').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con clientes en la nómina",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay clientes registrados",
            "infoFiltered": "(filtrado de un total de _MAX_ clientes)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        }
    });

    // template: registrar_venta.html
    $('#listaClientesModal').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con clientes en la nómina",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay clientes registrados",
            "infoFiltered": "(filtrado de un total de _MAX_ clientes)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": '/get_lista_clientes/'
    });

    // template: verificar_ventas.html
    $('#listaVentas').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con ventas registradas",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ ventas)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": '/get_ventas_template_verificar_ventas/',
        "columns": [
            { "data": "obs" },
            { "data": "fecha" },
            { "data": "nro_factura" },
            { "data": "cliente" },
            { "data": "ruc" },
            { "data": "detalles_cliente" },
            { "data": "suma_total" },
            { "data": "factura" },
            { "data": "anular" }
        ],
        "columnDefs": [
            {"className": "obs", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "texto", "targets": [2]},
            {"className": "texto", "targets": [3]},
            {"className": "texto", "targets": [4]},
            {"className": "obs", "targets": [5]},
            {"className": "monto", "targets": [6]},
            {"className": "obs", "targets": [7]},
            {"className": "obs", "targets": [8]}
        ]
    });

    $('#listaArticulosVendidos').DataTable({
        "scrollCollapse": true,
        "order": [[0, "desc"]],
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con artículos vendidos",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ articulos)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": {
            "url": "/get_lista_articulos_vendidos_modal_template_verificar_ventas/",
            "type": "POST",
            "data": {
                "funcion": "todos_los_datos"
            }
        },
        "columns": [
            { "data": "fecha" },
            { "data": "articulo" },
            { "data": "cantidad" },
            { "data": "subtotal" }
        ],
        "columnDefs": [
            {"className": "texto", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "texto", "targets": [2]},
            {"className": "monto", "targets": [3]}
        ]
    });

    // template: ver_CMD.html
    $('#listaClasificaciones').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con clasificaciones definidas",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay clasificaciones disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ clasificaciones)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_clasificaciones/",
        "columns": [
            { "data": "descripcion" },
            { "data": "editar" },
            { "data": "eliminar" }
        ],
        "columnDefs": [
            {"className": "texto desc", "targets": [0]},
            {"className": "input", "targets": [1]},
            {"className": "input", "targets": [2]}
        ]
    });

    $('#listaMarcas').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con marcas registradas",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay marcas disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ marcas)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_marcas/",
        "columns": [
            { "data": "descripcion" },
            { "data": "clasificacion" },
            { "data": "editar" },
            { "data": "eliminar" }
        ],
        "columnDefs": [
            {"className": "texto desc", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "input", "targets": [2]},
            {"className": "input", "targets": [3]}
        ]
    });

    $('#listaDistribuidores').DataTable({
        "scrollCollapse": true,
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con ditribuidores registrados",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay distribuidores disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ distribuidores)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_distribuidores/",
        "columns": [
            { "data": "descripcion" },
            { "data": "editar" },
            { "data": "eliminar" }
        ],
        "columnDefs": [
            {"className": "texto desc", "targets": [0]},
            {"className": "input", "targets": [1]},
            {"className": "input", "targets": [2]}
        ]
    });

    // template verificar_caja.html
    $('#listaCajas').DataTable({
        "scrollCollapse": true,
        "order": [[0, "desc"]],
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuenta con información en estos momentos",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay información disponible",
            "infoFiltered": "(filtrado de un total de _MAX_)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_info_cajas/",
        "columns": [
            { "data": "fecha_apertura" },
            { "data": "fecha_cierre" },
            { "data": "monto_apertura" },
            { "data": "total_ventas" },
            { "data": "monto_cierre" },
            { "data": "efectivo" },
            { "data": "tc" },
            { "data": "td" },
            { "data": "costos" },
            { "data": "ganancias" },
            { "data": "estado" },
            { "data": "editar" }
        ],
        "columnDefs": [
            {"className": "texto", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "monto", "targets": [2]},
            {"className": "monto", "targets": [3]},
            {"className": "monto", "targets": [4]},
            {"className": "monto", "targets": [5]},
            {"className": "monto", "targets": [6]},
            {"className": "monto", "targets": [7]},
            {"className": "monto", "targets": [8]},
            {"className": "monto", "targets": [9]},
            {"className": "texto", "targets": [10]},
            {"className": "input", "targets": [11]}
        ]
    });

    //template view_logs.html
    $('#logs').DataTable({
        "scrollCollapse": true,
        "order": [[0, "desc"]],
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuenta con información en estos momentos",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay información disponible",
            "infoFiltered": "(filtrado de un total de _MAX_)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": "/get_logs/",
        "columns": [
            { "data": "fecha_hora" },
            { "data": "evento" },
            { "data": "descripcion" },
            { "data": "responsable" }
        ],
        "columnDefs": [
            {"className": "texto", "targets": [0]},
            {"className": "texto", "targets": [1]},
            {"className": "texto", "targets": [2]},
            {"className": "texto", "targets": [3]}
        ]
    });
});