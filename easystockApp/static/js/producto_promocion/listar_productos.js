/**
 * Created by JorgeD on 09/08/2019.
 */

$(document).ready(function(){

    var modal_delete_producto = $('#modalDelete');
    modal_delete_producto.on('show.bs.modal', function(event){
        var prod_id = $(event.relatedTarget).attr('data-prod_id'); //se extrae lo que se almaceno en data-*
        var prod_marca = $(event.relatedTarget).attr('data-prod_marca');
        var div_pregunta_lista_promos = $('div#pregunta_lista_promos');
        var div_lista_promos = $('div#lista_promos');

        var modal = $(this);
        // se obtienen la cantidad y una lista con la descripcion/nombre de todas las promocioens a la que pertenece el prod
        $.ajax({
            url:"/get_promocion_condicion_eliminar_producto/",
            type:"POST",
            data:{prod_id: prod_id},

            success: function(json){
                modal.find('input#prod_id').val(prod_id);   // se carga el id del prod al input para la poseterior eliminacion

                if(json['cantidad'] > 0){   // si la cantidad es mayor a 0 se muestra una pregunta y la lista de promos
                    div_pregunta_lista_promos.append("<p> Si continúa con la operación las siguientes promociones " +
                        "también serán eliminadas:</p>");

                    div_pregunta_lista_promos.attr('hidden', false);
                    div_lista_promos.attr('hidden', false);
                }

                for(i=0; i < json['cantidad']; i++){    // se crea la lista para mostrar
                    div_lista_promos.append("<p><li><b>" + json['lista'][i] + "</b></li></p>")
                }
            },
            error : function() {
                console.log("error!");
            }
        });
    });

    // cuando se cierra el modal, hay que devolverlo a su estado neutral, sin pregunta y sin lista de promos
    modal_delete_producto.on('hide.bs.modal', function(event){
        var div_pregunta_lista_promos = $('div#pregunta_lista_promos');
        var div_lista_promos = $('div#lista_promos');

        div_lista_promos.html('');
        div_lista_promos.attr('hidden', true);

        div_pregunta_lista_promos.html('');
        div_pregunta_lista_promos.attr('hidden', true);
    });


    $('#modalDeletePromo').on('show.bs.modal', function(event){
        var promo_id = $(event.relatedTarget).attr('data-promo_id'); //se extrae lo que se almaceno en data-*
        var promo_desc = $(event.relatedTarget).attr('data-promo_desc');

        var modal = $(this);
        modal.find('input#promo_id').val(promo_id)
    });

});

$('#formModalDelete').on('submit', function(event){
    event.preventDefault();
    deleteProducto();
});

function deleteProducto(){
    console.log('entrando en la funcion deleteProducto');
    $.ajax({
        url:"/eliminar_producto/",
        type:"POST",
        data:{prod_id: $('#prod_id').val()},

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

$('#formModalDeletePromo').on('submit', function(event){
    event.preventDefault();
    deletePromo();
});

function deletePromo(){
    console.log('entrando en la funcion deletePromo');
    $.ajax({
        url:"/eliminar_promocion/",
        type:"POST",
        data:{promo_id: $('#promo_id').val()},

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

var modalDetallePromo = $('#modalDetallesPromo');
modalDetallePromo.on('show.bs.modal', function(event){
    var promo_id = $(event.relatedTarget).attr('data-promo_id');

    $.ajax({
        url:"/get_detalles_promocion_modal_template_listar_productos/",
        type:"POST",
        data:{promo_id: promo_id},

        success: function(json){
            console.log(json);

            for (i=0; (json['data']).length; i++){
                var nueva_linea = "<tr style=\"text-align: center\">" +
                    "<td>" + json['data'][i]['articulo'] + "</td>" +
                    "<td>" + json['data'][i]['cantidad_promocional'] + "</td>" +
                    "<td>" + json['data'][i]['articulo_precio_unit'] + "</td></tr>";

                $('div#modalDetallesPromo table#detallesPromocionProductos tbody').append(nueva_linea)
            }
        },

        error : function() {
            console.log("error!");
            //location.reload(true);
        }
    });
});

modalDetallePromo.on('hide.bs.modal', function(){
    $('div#modalDetallesPromo table#detallesPromocionProductos tbody').html('')
});

$('#modalAddStock').on('show.bs.modal', function(event){
    $('#cantidad').val('');

    var prod_id = $(event.relatedTarget).attr('data-prod_id');
    var marca = $(event.relatedTarget).attr('data-prod_marca');
    var descripcion = $(event.relatedTarget).attr('data-prod_desc');
    var presentacion = $(event.relatedTarget).attr('data-prod_pres');

    var linea = marca + " - " + descripcion + " - " + presentacion;

    $('strong#marca_desc').html(linea);
    $('#prod_id').val(prod_id)
});

$('#formModalAddStock').on('submit', function(event){
    event.preventDefault();
    var alert = "";
    var div_alerts = $('div#alerts');

    var lista_productos = $('#listaProductos').DataTable();

    $.ajax({
        url:"/agregar_al_stock/",
        type:"POST",
        data:{prod_id: $('#prod_id').val(),
              cantidad: $('#cantidad').val()},

        success: function(json){
            //recargar solo la tabla no toda la pagina
            $('#modalAddStock').modal('hide');
            var tipo = json['propiedad_alerts']['tipo'];
            var icono = json['propiedad_alerts']['icono'];
            var mensaje = json['propiedad_alerts']['mensaje'];

            alert = "<div class= \"alert "  + tipo + "\">" +
                        "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                        "<strong><i class='fa " + icono + "'></i>&ensp;</strong>" +  mensaje +
                    "</div>";
            div_alerts.html(alert);

            lista_productos.ajax.reload()
        },

        error : function() {
        }
    });
});

$('#boton_ver_detalles').click(function(){
    var detalle = $('#select_detalles_stock').val();
    var titulo_modal = $('#titulo_modal');

    if(detalle == 'Distribuidor'){
        titulo_modal.html('Valores del stock en base al ' + detalle);
    }else{
        titulo_modal.html('Valores del stock en base a la ' + detalle);
    }

    $('#columna_detalle').html(detalle);

    $('#valoresDetallados').DataTable({
        "scrollCollapse": true,
        "order": [[0, "desc"]],
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con registros",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": {
            "url": "/get_valor_stock_detallado/",
            "type": "POST",
            "data": {
                "detalle": detalle
            }
        },
        "columns": [
            { "data": detalle.toLowerCase().replace('ó', 'o') },
            { "data": "valor_de_costo" },
            { "data": "valor_de_venta" }
        ],
        "columnDefs": [
            {"className": "texto", "targets": [0]},
            {"className": "monto", "targets": [1]},
            {"className": "monto", "targets": [2]}
        ]
    });

    $('#modalValorStockDetallado').modal('show');
});

$('#modalValorStockDetallado').on('hide.bs.modal', function(){
    $('#valoresDetallados').DataTable().destroy()
});

$('#boton_ver_historial_stock').click(function(){

    $('#valoresHistoricos').DataTable({
        "scrollCollapse": true,
        "order": [[0, "desc"]],
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se cuentan con registros",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "search": "Filtrar resultados: ",
            "paginate":{
                "previous": "Anterior",
                "next": "Siguiente"
            }
        },
        "ajax": {
            "url": "/get_valores_historicos_stock/",
            "type": "POST",
            "data": {
                solicitante: 'modal'
            }
        },
        "columns": [
            { "data": "fecha"},
            { "data": "valor_de_costo" },
            { "data": "valor_de_venta" }
        ],
        "columnDefs": [
            {"className": "texto", "targets": [0]},
            {"className": "monto", "targets": [1]},
            {"className": "monto", "targets": [2]}
        ]
    });

    $('#modalValorStockHistorico').modal('show');

    $('[data-toggle="tooltip"]').tooltip('hide')

});

$('#modalValorStockHistorico').on('hide.bs.modal', function(){
    $('#valoresHistoricos').DataTable().destroy()
});

$(window).on('load', function(){
    $('input[type="search"]').focus();
});