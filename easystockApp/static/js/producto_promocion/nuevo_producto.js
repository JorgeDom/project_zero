/**
 * Created by JorgeD on 22/07/2019.
 */
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

function get_distribuidores(){
    var select_distribuidor = $('select#id_distribuidor');

    select_distribuidor.html('');  //se vacia el select
    // se agrega la primera opcion de cualquier select
    select_distribuidor.append($('<option>', {value: '',
                                                text: 'Seleccione un distribuidor...',
                                                selected: 'selected',
                                                disabled: 'disabled'}));
    //se solicitan las demas opciones del select
    $.ajax({
        url:"/get_CMD/",
        type:"POST",
        data:{tipo: 'Distribuidor'},

        success: function(json){
            for (i=0; i<json['cantidad']; i++){
                select_distribuidor.append($('<option>', {
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

function get_marcas_productos(){
    var select_marca = $('select#id_marca');
    var select_clasificacion = $('select#id_clasificacion');

    select_marca.html('');  //se vacia el select
    // se agrega la primera opcion de cualquier select
    select_marca.append($('<option>', {value: '',
                                        text: 'Seleccione una marca...',
                                        selected: 'selected',
                                        disabled: 'disabled'}));
    //se solicitan las demas opciones del select
    $.ajax({
        url:"/get_CMD/",
        type:"POST",
        data:{tipo: 'Marca',
              clasificacion: select_clasificacion.val()},

        success: function(json){
            // una vez que se obtienen todas las marcas en base a la clasificacion seleccionada,
            // se habilitan el select y el boton para registrar marcas
            $('select#id_marca').attr('disabled', false);
            $('button#boton_registrar_marca').attr('disabled', false);

            for (i=0; i<json['cantidad']; i++){
                select_marca.append($('<option>', {
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

$(window).on('load', function(){
    get_clasificaciones_producto('id_clasificacion');
    get_distribuidores();

    $('select#id_distribuidor').focus();

    // al cargar por primera vez la ventana, lo referente al registro de marca esta desabilitado
    $('select#id_marca').attr('disabled', true);
    $('button#boton_registrar_marca').attr('disabled', true);
});

$('select#id_clasificacion').on('change', function(){
    get_marcas_productos();
});


// CLASIFICACIONES
$('#boton_crear_clasificacion').on('click', function(){
    $('#modalCrearClasificacion').modal('show');
    $('input[type="text"]#id_nueva_clasificacion').attr('autofocus', 'true');
});

$('#formModalCrearClasificacion').on('submit', function(event){
    event.preventDefault();
    var alert = "";
    var modal = $('div#modalCrearClasificacion div#alerts');
    var clasificacion = $('input#id_nueva_clasificacion');

    $.ajax({
        url:"/crear_clasificacion/",
        type:"POST",
        data:{clasificacion: clasificacion.val()},

        success: function(json){
            var tipo = json['propiedad_alerts']['tipo'];
            var icono = json['propiedad_alerts']['icono'];
            var mensaje = json['propiedad_alerts']['mensaje'];

            //si el alert es un warning, significa que el CI/RUC ya existe no se permite avanzar, se muestra el aler
            if(json['propiedad_alerts']['tipo'] == 'alert-warning'){
                alert = "<div class= \"alert "  + tipo + "\">" +
                            "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                            "<strong><i class='fa " + icono + "'></i>&ensp;</strong>" +  mensaje +
                        "</div>";
                modal.html(alert);
            //si no es warning, quiere decir que se almaceno todos sin problemas se procede a lo demas
            } else {

                alert = ""; //se limpia el alert
                $('#modalCrearClasificacion').modal('hide');    //se cierra el modal
                clasificacion.val('');  //se limpia el input donde se cargo el distribuidor
                get_clasificaciones_producto('id_clasificacion'); //se repobla el select
            }
        },

        error : function() {
            console.log("error!");
        }
    });
});

$('#modalCrearClasificacion').on('show.bs.modal', function(){
    $('input[type="text"]#id_nueva_clasificacion').attr('autofocus', true);
});

// DISTRIBUIDORES
$('#boton_cargar_distribuidor').on('click', function(){
   $('#modalCargarDistribuidor').modal('show')
});

$('#formModalCargarDistribuidor').on('submit', function(event){
    event.preventDefault();
    var alert = "";
    var modal = $('div#modalCargarDistribuidor div#alerts');
    var distribuidor = $('input#id_nuevo_distribuidor');

    $.ajax({
        url:"/cargar_distribuidor/",
        type:"POST",
        data:{distribuidor: distribuidor.val()},

        success: function(json){
            var tipo = json['propiedad_alerts']['tipo'];
            var icono = json['propiedad_alerts']['icono'];
            var mensaje = json['propiedad_alerts']['mensaje'];

            //si el alert es un warning, significa que el CI/RUC ya existe no se permite avanzar, se muestra el aler
            if(json['propiedad_alerts']['tipo'] == 'alert-warning'){
                alert = "<div class= \"alert "  + tipo + "\">" +
                            "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                            "<strong><i class='fa " + icono + "'></i>&ensp;</strong>" +  mensaje +
                        "</div>";
                modal.html(alert);
            //si no es warning, quiere decir que se almaceno todos sin problemas se procede a lo demas
            } else {
                alert = ""; //se limpia el alert
                $('#modalCargarDistribuidor').modal('hide');    //se cierra el modal
                distribuidor.val('');   //se limpia el input donde se cargo el distribuidor
                get_distribuidores();   //se repobla el select
            }
        },
        error : function() {
            console.log("error!");
        }
    });
});

$('#modalCargarDistribuidor').on('show.bs.modal', function(){
    $('input[type="text"]#id_nuevo_distribuidor').attr('autofocus', true);
});

// MARCAS
$('#boton_registrar_marca').on('click', function(){
    get_clasificaciones_producto('id_clasificacion_x_marca');
   $('#modalRegistrarMarca').modal('show')
});

$('#formModalRegistrarMarca').on('submit', function(event){
    event.preventDefault();
    var alert = "";
    var modal = $('div#modalRegistrarMarca div#alerts');
    var marca = $('input#id_nueva_marca');

    var clasificacion = $('#id_clasificacion_x_marca');   //luego de cargar las clasificaciones se asigna la variable

    $.ajax({
        url:"/registrar_marca/",
        type:"POST",
        data:{marca: marca.val(),
              clasificacion: clasificacion.val()},

        success: function(json){
            var tipo = json['propiedad_alerts']['tipo'];
            var icono = json['propiedad_alerts']['icono'];
            var mensaje = json['propiedad_alerts']['mensaje'];

            //si el alert es un warning, significa que el CI/RUC ya existe no se permite avanzar, se muestra el aler
            if(json['propiedad_alerts']['tipo'] == 'alert-warning'){
                alert = "<div class= \"alert "  + tipo + "\">" +
                            "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                            "<strong><i class='fa " + icono + "'></i>&ensp;</strong>" +  mensaje +
                        "</div>";
                modal.html(alert);
            //si no es warning, quiere decir que se almaceno todos sin problemas se procede a lo demas
            } else {
                alert = ""; //se limpia el alert
                $('#modalRegistrarMarca').modal('hide');    //se cierra el modal
                marca.val('');   //se limpia el input donde se cargo el distribuidor
                get_marcas_productos();   //se popula el select
            }
        },
        error : function() {
            console.log("error!");
        }
    });
});

$('#modalRegistrarMarca').on('show.bs.modal', function(){
    $('input[type="text"]#id_nueva_marca').attr('autofocus', true);
});