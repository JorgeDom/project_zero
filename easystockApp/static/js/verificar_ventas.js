/**
 * Created by JorgeD on 24/05/2019.
 */

$('td.obs i.fa-check-circle').attr('data-search', 'vigente');
$('td.obs i.fa-exclamation-triangle').attr('data-search', 'anulada');

$('#modalDetallesCliente').on('show.bs.modal', function(event){
    console.log('abriendo modalDetallesCliente');
    //se extrae lo que se almaceno en data-*
    var existe_cliente = $(event.relatedTarget).attr('data-existe_cliente');
    var cliente_id = $(event.relatedTarget).attr('data-cliente_id');

    $.ajax({
        url:"/get_detalles_cliente_modal_template_verificar_ventas/",
        type:"POST",
        data:{existe_cliente: existe_cliente,
              cliente_id: cliente_id},

        success: function(json){
            //console.log(json);
            if(json['mensaje'] == '') {
                $('div#modalDetallesCliente div.modal-body').html(
                    "<div class=\"table-responsive-md table-responsive-sm\" style=\"font-size: small\">" +
                        "<table class=\"table table-striped\" id=\"detallesCliente\" style=\"width: 100%\">" +
                            "<tr>" +
                                "<th class=\"detalle\">Nombre/s y Apellido/s: </th>" +
                                "<td id=\"nombre_apellido\">" + json['detalles_cliente']['nombre_apellido'] + "</td>" +
                            "</tr><tr>" +
                                "<th class=\"detalle\">C.I. Nro. o R.U.C.: </th>" +
                                "<td id=\"ci_ruc\">" + json['detalles_cliente']['ci_ruc'] + "</td>" +
                            "</tr><tr>" +
                                "<th class=\"detalle\">Teléfono: </th>" +
                                "<td id=\"tel_nro\">" + json['detalles_cliente']['tel_nro'] + "</td>" +
                            "</tr><tr>" +
                                "<th class=\"detalle\">Dirección: </th>" +
                                "<td id=\"direccion\">" + json['detalles_cliente']['direccion'] + "</td>" +
                            "</tr><tr>" +
                                "<th class=\"detalle\">Correo electrónico: </th>" +
                                "<td id=\"email\">" + json['detalles_cliente']['email'] + "</td>" +
                            "</tr>" +
                        "</table>" +
                    "</div>"
                );
            }else{
                $('div#modalDetallesCliente div.modal-body').html("<p>" + json['mensaje'] + "</p>");
            }
        },

        error : function() {
            console.log("error!");
            //location.reload(true);
        }
    });
});

var modalDetallesFactura = $('#modalDetallesFactura');

modalDetallesFactura.on('show.bs.modal', function(event){
    console.log('abriendo modalDetallesFactura');
    //se extrae lo que se almaceno en data-*
    var venta_id = $(event.relatedTarget).attr('data-venta_id');
    var nro_factura = $(event.relatedTarget).attr('data-nro_factura');

    var nro_factura_td = $('div#modalDetallesFactura div.modal-body table#detallesFactura1 td#nro_factura');
    var condicion_venta = $('table#detallesFactura1 td#condicion_venta');
    var fecha = $('table#detallesFactura1 td#fecha');
    var cliente = $('table#detallesFactura1 td#cliente');
    var ruc = $('table#detallesFactura1 td#ruc');
    var metodo = $('table#detallesFactura1 td#metodo');

    var total_venta = $('table#detallesFactura2 td#total_venta');
    var total_abonado = $('table#detallesFactura2 td#total_abonado');
    var total_vuelto = $('table#detallesFactura2 td#total_vuelto');

    var total_exentas = $('table#detallesFactura3 td#total_exentas');
    var total_grav_5 = $('table#detallesFactura3 td#total_grav_5');
    var total_grav_10 = $('table#detallesFactura3 td#total_grav_10');

    var total_imp_5 = $('table#detallesFactura4 td#total_imp_5');
    var total_imp_10 = $('table#detallesFactura4 td#total_imp_10');
    var total_imp = $('table#detallesFactura4 td#total_imp');

    $('div#modalDetallesFactura h4.modal-title').html('Detalle de la Factura Nro. ' + nro_factura);

    $.ajax({
        url:"/get_detalles_factura_modal_template_verificar_ventas/",
        type:"POST",
        data:{venta_id: venta_id},

        success: function(json){
            nro_factura_td.html(json['data']['nro_factura']);
            condicion_venta.html('CONTADO');
            fecha.html(json['data']['ts']);
            cliente.html(json['data']['cliente']);
            ruc.html(json['data']['ruc']);
            metodo.html(json['data']['metodo_pago']);

            total_venta.html(json['data']['suma_total']);
            total_abonado.html(json['data']['suma_pagada']);
            total_vuelto.html(json['data']['suma_vuelto']);

            total_exentas.html(json['data']['exenta']);
            total_grav_5.html(json['data']['gravadas']['gravadas_5']);
            total_grav_10.html(json['data']['gravadas']['gravadas_10']);

            total_imp_5.html(json['data']['impuestos']['impuesto_5']);
            total_imp_10.html(json['data']['impuestos']['impuesto_10']);
            total_imp.html(json['data']['impuestos']['total_impuesto']);

            for (i=0; i<(json['data']['productos']).length; i++){
                var nueva_linea = "<tr>" +
                    "<td>" + json['data']['productos'][i]['articulo'] + " x " + json['data']['productos'][i]['cantidad'] + "</td>" +
                    "<td class='monto'>" + json['data']['productos'][i]['tipo_impuesto'] + "%</td>" +
                    "<td class='monto'>" + json['data']['productos'][i]['subtotal'] + "</td></tr>";

                $("table#detallesFacturaProductos tbody").append(nueva_linea);
            }
        },

        error : function() {
            console.log("error!");
            //location.reload(true);
        }
    });
});

modalDetallesFactura.on('hide.bs.modal', function(){
    $("table#detallesFacturaProductos tbody").html('');
});

$('#modalAnularFactura').on('show.bs.modal', function(event){
    var venta_id = $(event.relatedTarget).attr('data-venta_id'); //se extrae lo que se almaceno en data-*
    var nro_factura = $(event.relatedTarget).attr('data-nro_factura');

    $('.modal-body span').html(nro_factura);

    var modal = $(this);
    modal.find('input#venta_id').val(venta_id);
    modal.find('input#nro_factura').val(nro_factura);
});

$('#formModalAnularFactura').on('submit', function(event){
    event.preventDefault();
    anularFactura();
});

function anularFactura(){

    $.ajax({
        url:"/anular_factura/",
        type:"POST",
        data:{venta_id: $('#venta_id').val(),
              nro_factura: $('#nro_factura').val()},

        success: function(){
            console.log("success!");
            location.reload(true);
        },

        error : function() {
            console.log("error!");
            location.reload(true);
        }
    });
}

$(window).on('load', function(){
    $('input[type="search"]').focus();
});

$('#datos_desde_apertura_caja').click(function(){
    var tabla = $('#listaArticulosVendidos');
    //si el checkbox esta marcado, debo ir a la funcion y solicitar solo desde la apertura de la caja
    if($(this).prop('checked') == true){
        tabla.DataTable().clear().destroy();
        tabla.DataTable({
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
                    "funcion": "desde_apertura_caja"
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

    }
    // si el checkbox se desmarca de nuevo, se debe ir a la misma funcion pero solicitar todos los datos
    else if($(this).prop('checked') == false){

        tabla.DataTable().clear().destroy();
        tabla.DataTable({
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
    }
});