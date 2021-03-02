/**
 * Created by JorgeD on 28/07/2019.
 */
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

function get_clasificaciones_producto(id_select){
    var select_clasificacion = $('select#' + id_select);

    select_clasificacion.html('');  //se vacia el select
    // se agrega la primera opcion de cualquier select
    select_clasificacion.append($('<option>', {value: '',
                                                text: 'Seleccione una clasificación...',
                                                selected: 'selected',
                                                disabled: 'disabled'}));
    //se solicitan las demas opciones del select
    $.ajax({
        url:"/get_CMD/",
        type:"POST",
        data:{tipo: 'Clasificacion'},

        success: function(json){
            for (i=0; i<json['cantidad']; i++){
                select_clasificacion.append($('<option>', {
                    value: json['lista'][i],
                    text: json['lista'][i]
                }))
            }
        },
        error : function() {
            console.log("error!");
        }
    });
}

//CLASIFICACIONES
// 1er. PASO: al abrir el modal, se obtiene la info que se quiere editar
$('#modalEditarClasificacion').on('show.bs.modal', function(event){
    // se entresaca la info necesaria para hacer el query
    var item_id = event.relatedTarget.getAttribute('data-item_id');
    var input_nueva_clasificacion = $('input#id_nueva_clasificacion');
    var input_item_id = $('input#item_id');

    input_item_id.val(item_id); // se carga el input escondido en el modal

    //al principio el alert esta escondido, si se vuelve a abrir cualquier modal, se blanquea el alert
    var alert = $('div#alert');
    alert.attr('hidden', true);
    alert.html('');

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id,
              tipo: 'Clasificacion',
              operacion: 'get_data'},

        success: function(json){
            input_nueva_clasificacion.val(json['descripcion'])
        },
        error : function() {
            console.log("error!");
        }
    });
});

// 2do PASO: al darle submit al form, se deben guardar los cambios y ver traducidos en el view
$('#formModalEditarClasificacion').on('submit', function(event) {
    event.preventDefault();
    var item_id = $('input#item_id');   // se obtiene el item_id del input escondido en el modal
    var clasificacion = $('input#id_nueva_clasificacion');  // se obtiene la nueva clasificacion
    var lista_clasificaciones = $("table#listaClasificaciones").DataTable();

    var alert = $('div#alert');

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id.val(),
              tipo: 'Clasificacion',
              nueva_clasificacion: clasificacion.val(),
              operacion: 'editar'},

        success: function(json){
            // una vez que la edicion ha sido exitosa, se procede cerrar el modal, mostrar el alert y recargar la tabla
            $('#modalEditarClasificacion').modal('hide');

            alert.addClass('alert ' + json['propiedad_alerts']['tipo']);
            var contenido_alert = "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                                  "<strong><i class=\"fa " + json['propiedad_alerts']['icono'] + "\"></i></strong> &nbsp;" + json['propiedad_alerts']['mensaje'];
            alert.html(contenido_alert);
            alert.attr('hidden', false);

            lista_clasificaciones.ajax.reload();
        },
        error : function() {
            console.log("error!");
        }
    });
});

//MARCAS
// 1er. PASO: al abrir el modal, se obtiene la info que se quiere editar
$('#modalEditarMarca').on('show.bs.modal', function(event){
    // se entresaca la info necesaria para hacer el query
    var item_id = event.relatedTarget.getAttribute('data-item_id');
    var input_nueva_marca = $('input#id_nueva_marca');
    var input_item_id = $('input#item_id');
    var select_clasificacion = $('select#id_clasificacion_x_marca');

    input_item_id.val(item_id); // se carga el input escondido en el modal

    //al principio el alert esta escondido, si se vuelve a abrir cualquier modal, se blanquea el alert
    var alert = $('div#alert');
    alert.attr('hidden', true);
    alert.html('');

    get_clasificaciones_producto('id_clasificacion_x_marca');   // se carga el select al abrir el modal

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id,
              tipo: 'Marca',
              operacion: 'get_data'},

        success: function(json){
            input_nueva_marca.val(json['descripcion']);
            select_clasificacion.val(json['clasificacion_actual']).attr('selected', true)
        },
        error : function() {
            console.log("error!");
        }
    });
});

//2do. PASO: agregar la clasificacion
$('#formModalEditarMarca').on('submit', function(event) {
    event.preventDefault();
    var item_id = $('input#item_id');   // se obtiene el item_id del input escondido en el modal
    var marca = $('input#id_nueva_marca');  // se obtiene el nuevo distribuidor
    var select_clasificacion = $('select#id_clasificacion_x_marca');
    var lista_marcas = $("table#listaMarcas").DataTable();

    var alert = $('div#alert');

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id.val(),
              tipo: 'Marca',
              nueva_marca: marca.val(),
              clasificacion_x_marca: select_clasificacion.val(),
              operacion: 'editar'},

        success: function(json){
            // una vez que la edicion ha sido exitosa, se procede cerrar el modal, mostrar el alert y recargar la tabla
            $('#modalEditarMarca').modal('hide');

            alert.addClass('alert ' + json['propiedad_alerts']['tipo']);
            var contenido_alert = "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                                  "<strong><i class=\"fa " + json['propiedad_alerts']['icono'] + "\"></i></strong> &nbsp;" + json['propiedad_alerts']['mensaje'];
            alert.html(contenido_alert);
            alert.attr('hidden', false);

            lista_marcas.ajax.reload();
        },
        error : function() {
            console.log("error!");
        }
    });
});

//DISTRIBUIDORES
// 1er. PASO: al abrir el modal, se obtiene la info que se quiere editar
$('#modalEditarDistribuidor').on('show.bs.modal', function(event){
    // se entresaca la info necesaria para hacer el query
    var item_id = event.relatedTarget.getAttribute('data-item_id');
    var input_nuevo_distribuidor = $('input#id_nuevo_distribuidor');
    var input_item_id = $('input#item_id');

    input_item_id.val(item_id); // se carga el input escondido en el modal

    //al principio el alert esta escondido, si se vuelve a abrir cualquier modal, se blanquea el alert
    var alert = $('div#alert');
    alert.attr('hidden', true);
    alert.html('');

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id,
              tipo: 'Distribuidor',
              operacion: 'get_data'},

        success: function(json){
            input_nuevo_distribuidor.val(json['descripcion'])
        },
        error : function() {
            console.log("error!");
        }
    });
});

// 2do PASO: al darle submit al form, se deben guardar los cambios y ver traducidos en el view
$('#formModalEditarDistribuidor').on('submit', function(event) {
    event.preventDefault();
    var item_id = $('input#item_id');   // se obtiene el item_id del input escondido en el modal
    var distribuidor = $('input#id_nuevo_distribuidor');  // se obtiene el nuevo distribuidor
    var lista_distribuidores = $("table#listaDistribuidores").DataTable();

    var alert = $('div#alert');

    $.ajax({
        url:"/editar_CMD/",
        type:"POST",
        data:{item_id: item_id.val(),
              tipo: 'Distribuidor',
              nuevo_distribuidor: distribuidor.val(),
              operacion: 'editar'},

        success: function(json){
            // una vez que la edicion ha sido exitosa, se procede cerrar el modal, mostrar el alert y recargar la tabla
            $('#modalEditarDistribuidor').modal('hide');

            alert.addClass('alert ' + json['propiedad_alerts']['tipo']);
            var contenido_alert = "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                                  "<strong><i class=\"fa " + json['propiedad_alerts']['icono'] + "\"></i></strong> &nbsp;" + json['propiedad_alerts']['mensaje'];
            alert.html(contenido_alert);
            alert.attr('hidden', false);

            lista_distribuidores.ajax.reload();
        },
        error : function() {
            console.log("error!");
        }
    });
});


$('#modalDeleteCMD').on('show.bs.modal', function(event){
    var item_id = event.relatedTarget.getAttribute('data-item_id');
    var tipo = event.relatedTarget.getAttribute('data-tipo');
    var descripcion = event.relatedTarget.getAttribute('data-desc');

    //se actualiza el titulo del modal
    $('.modal-title').html('Eliminar ' + tipo);
    $('input#item_id').val(item_id);
    $('input#tipo').val(tipo);
    $('input#descripcion').val(descripcion);
});


$('#formModalDeleteCMD').on('submit', function(event){
    event.preventDefault();

    var item_id = $('input#item_id');
    var tipo = $('input#tipo');
    var descripcion = $('input#descripcion');
    var lista_clasificaciones = $("table#listaClasificaciones").DataTable();
    var lista_marcas = $("table#listaMarcas").DataTable();
    var lista_distribuidores = $("table#listaDistribuidores").DataTable();

    var alert = $('div#alert');

    $.ajax({
        url: '/eliminar_CMD/',
        type: 'POST',
        data: {item_id: item_id.val(),
                tipo: tipo.val(),
                desc: descripcion.val()},

        success: function(json){
            // una vez que la edicion ha sido exitosa, se procede cerrar el modal, mostrar el alert y recargar la tabla
            $('#modalDeleteCMD').modal('hide');

            alert.addClass('alert ' + json['propiedad_alerts']['tipo']);
            var contenido_alert = "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                                  "<strong><i class=\"fa " + json['propiedad_alerts']['icono'] + "\"></i></strong> &nbsp;" + json['propiedad_alerts']['mensaje'];
            alert.html(contenido_alert);
            alert.attr('hidden', false);

            lista_clasificaciones.ajax.reload();
            lista_marcas.ajax.reload();
            lista_distribuidores.ajax.reload();

        },
        error: function(){}
    });

});