/**
 * Created by JorgeD on 03/06/2019.
 */
function eliminarFila(articulo_id, subtotal){
    var radio_precio_promocional = $('input#radio_precio_promocional');
    var radio_porcentaje_promocional = $('input#radio_porcentaje_promocional');

    var input_precio_promocional = $('input#precio_promocional');
    var input_porcentaje_promocional = $('input#porcentaje_promocional');

    var input_precio_sin_descuento = $('input#precio_venta_sin_descuento');
    var input_precio_con_descuento = $('input#precio_venta_con_descuento');


    // 1ro. recuperamos el viejo precio sin descuento, antes de querer eliminar una linea
    var actual_precio_sin_descuento = input_precio_sin_descuento.val();
    // 2do. se calcula el nuevo precion sin descuento, despues de eliminar ya la linea
    var nuevo_precio_sin_descuento = parseInt(actual_precio_sin_descuento) - parseInt(subtotal);
    // 3ro. se elimina la fila y se modifica el input del precio sin descuento
    $('tr#producto_' + articulo_id).remove();
    input_precio_sin_descuento.val(nuevo_precio_sin_descuento);

    // si al eliminar una linea, se queda vacia la lista, se reinicia el formulario
    if(input_precio_sin_descuento.val() == '0' || input_porcentaje_promocional.val() == ''){
        input_precio_con_descuento.val(0);

        radio_porcentaje_promocional.prop('checked', false);
        input_porcentaje_promocional.attr('disabled', true);
        input_porcentaje_promocional.val('');

        radio_precio_promocional.prop('checked', false);
        input_precio_promocional.attr('disabled', true);
        input_precio_promocional.val('');
    }else {  //si al eliminar una linea, la lista, NO se queda vacia, se calcula el nuevo precio con descuento
        if (input_precio_promocional.val() != '') {
            input_precio_con_descuento.val(input_precio_promocional.val())
        } else if(input_porcentaje_promocional.val() != ''){
            input_precio_con_descuento.val(parseFloat(parseFloat(input_precio_sin_descuento.val()) * parseFloat(100 - parseFloat(input_porcentaje_promocional.val())))/100)
        }
    }
}

function cargarLista(articulo, articulo_id) {
    //datos del producto
    var marca = $('table#listaProductosModal tr#' + articulo_id + ' td.marca').html();
    var descripcion = $('table#listaProductosModal tr#' + articulo_id + ' td.desc').html();
    var presentacion = $('table#listaProductosModal tr#' + articulo_id + ' td.pres').html();
    var input_precio_unit = $('table#listaProductosModal tr#' + articulo_id + ' input#precio_venta_' + articulo_id).val().replace(',', '');
    var input_cant_disponible = $('input#cantidad_disponible_' + articulo_id);
    var cantidad = $('input#cantidad_' + articulo_id);

    var alert_modal = $('div#modalProductos div.modal-body div#alert');

    //datos de los valores de venta
    var input_precio_promocional = $('input#precio_promocional');
    var radio_porcentaje_promocional = $('input#radio_porcentaje_promocional');
    var input_porcentaje_promocional = $('input#porcentaje_promocional');
    var input_precio_sin_descuento = $('input#precio_venta_sin_descuento');
    var input_precio_con_descuento = $('input#precio_venta_con_descuento');

    var precio_sin_descuento = input_precio_sin_descuento.val();

    //si la cantidad a vender es mayor a la cantidad disponible, se emite un alert y se vuelve a limpiar el input
    if (parseInt(input_cant_disponible.val()) < parseInt(cantidad.val()) && parseInt(cantidad.val()) != 0) {
        alert_modal.addClass('alert alert-warning fade show').show();
        alert_modal.html("<button type='button' class='close'>&times;</button>" +
                   "<strong><i class='fa fa-exclamation-circle'></i></strong> La cantidad solicitada supera la cantidad disponible!");
        $('.close').on('click', function(){
            $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
        });
        cantidad.val('');   // se limpia el input para volver a intentar
    //si se da click en el boton agregar pero no se completa ningun caracter en el input, o si el alor ingresado es cero
    }else if (cantidad.val() == '' || cantidad.val() == 0){
        alert_modal.addClass('alert alert-warning fade show').show();
        alert_modal.html("<button type='button' class='close'>&times;</button>" +
                   "<strong><i class='fa fa-exclamation-circle'></i></strong> Por favor, verifique la cantidad ingresada.");
        $('.close').on('click', function(){
            $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
        });
        cantidad.val('');
    //si no se cumple ninguna de las condiciones de arriba, se procede a agregar la promo a la lista de venta
    }else {
        var subtotal_a_agregar = ((parseInt(input_precio_unit) * parseInt(cantidad.val()))); //se calcula el precio de venta - lo que se tiene que sumar a la lista

        if($('table tbody tr#producto_' + articulo_id).length) {    //se verifica que no existan ya productos de ese tipo dentro de los que despacharan
            var input_cantidad = $('table tbody tr#producto_' + articulo_id + ' td input#cantidad');   //la cantidad del producto ya en lista
            var nueva_cant = parseInt(input_cantidad.val()) + parseInt(cantidad.val()); // lo que ahora deberia haber en la lista
            var nuevo_precio_venta = parseInt(input_precio_unit) * parseInt(nueva_cant);  //lo que se deberia cobrar ahora

            $('table tbody tr#producto_' + articulo_id + ' td.col2 ').html(nueva_cant +
                "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value="+ nueva_cant + " hidden>");
            $('table tbody tr#producto_' + articulo_id + ' td.col4 ').html(nuevo_precio_venta +
                "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value="+ nuevo_precio_venta + " hidden>");
            $('table tbody tr#producto_' + articulo_id + ' td.col5 ').html(
                "<i onclick=\"eliminarFila('" + parseInt(nuevo_precio_venta) + "');\" class=\"far fa-times-circle\" id=\"deletebtn\"></i>");

        }else{  // si no existe de ese tipo de producto, se procede a agregar una linea nueva a la lista
            //se formula la nueva linea que irá en la lista de productos a vender
            var nueva_linea = "<tr id=\"producto_" + articulo_id + "\" align=\"center\">" +
                "<td class='col1'>" +
                     marca + " - " +  descripcion + " - " + presentacion +
                     "<input type=\"text\" id=\"articulo_id\" name=\"articulo_id\" value=\""+ articulo_id + "\" hidden>" +
                     "<input type=\"text\" id=\"articulo\" name=\"articulo\" value=\""+ marca + "-" +  descripcion + "-" + presentacion + "\" hidden>" +
                "</td>" +
                "<td class='col2'>" +
                     cantidad.val() +
                    "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value=\"" + cantidad.val() + "\" hidden>" +
                "</td>" +
                "<td class='col3'>" +
                     (parseInt(input_precio_unit)) +
                     "<input type=\"text\" id=\"articulo_precio_unit\" name=\"articulo_precio_unit\" value="+ parseInt(input_precio_unit) + " hidden>" +
                "</td>" +
                "<td class='col4'>" +
                     subtotal_a_agregar +
                     "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value=\""+ subtotal_a_agregar + "\" hidden>" +
                "</td>" +
                "<td class='col5'><i onclick=\"eliminarFila('" + articulo_id + "', " + parseInt(subtotal_a_agregar) + ");\" class=\"far fa-times-circle\" id=\"deletebtn\"></i></td>" +
            "</tr>";

            $("table#promocion tbody").append(nueva_linea);
            cantidad.val('');
        }

        input_precio_sin_descuento.val(0);
        input_precio_sin_descuento.val(parseInt(precio_sin_descuento) + parseInt(subtotal_a_agregar));

        if(input_porcentaje_promocional.val() != ''){
            var precio_con_descuento = parseFloat(parseFloat(parseInt(input_precio_sin_descuento.val()) * parseFloat(100 - input_porcentaje_promocional.val())) / 100);
            input_precio_con_descuento.val(precio_con_descuento)
        }else{
            input_precio_con_descuento.val(input_precio_promocional.val())
        }
    }
}

$(window).on('load', function(){
    $('input#id_descripcion').focus();
});

var modalProductos = $('#modalProductos');

modalProductos.on('show.bs.modal', function(){
    $('input[type="search"]').attr('autofocus', 'true');
});

modalProductos.on('hide.bs.modal', function(){
    $("#listaProductosModal").DataTable().ajax.reload();
});

$('input#radio_precio_promocional').on('change', function(){
    var input_precio_promocional = $('input#precio_promocional');
    var input_porcentaje_promocional = $('input#porcentaje_promocional');
    var input_precio_venta_con_descuento = $('input#precio_venta_con_descuento');

    // se quitan y colocan los correspondientes disables a los inputs
    input_precio_promocional.attr('disabled', false);
    input_porcentaje_promocional.attr('disabled', true);
    input_porcentaje_promocional.val('');

    // si se llegase a seleccionar de nuevo, se vuelve a colocar el valor que estaba en el input_precio_promocional
    // al input_precio_con_descuento
    input_precio_venta_con_descuento.val(input_precio_promocional.val());
});

$('input#precio_promocional').on('keyup', function(){
    var input_precio_promocional = $('input#precio_promocional');
    //var input_porcentaje_promocional = $('input#porcentaje_promocional');
    var input_precio_venta_con_descuento = $('input#precio_venta_con_descuento');
    //var input_precio_venta_sin_descuento = $('input#precio_venta_sin_descuento');

    //console.log('1. ', parseFloat(parseFloat(input_precio_venta_con_descuento.val()) / parseFloat(input_precio_venta_sin_descuento.val())) * 10);

    //var porcentaje_promocional = parseFloat((1 - parseFloat(input_precio_venta_con_descuento.val() / input_precio_venta_sin_descuento.val())*10) * 100);

    input_precio_venta_con_descuento.val(input_precio_promocional.val());
    //input_porcentaje_promocional.val(porcentaje_promocional)
});

$('input#radio_porcentaje_promocional').on('change', function(){
    var input_precio_promocional = $('input#precio_promocional');
    var input_porcentaje_promocional = $('input#porcentaje_promocional');
    var input_precio_venta_sin_descuento = $('input#precio_venta_sin_descuento');
    var input_precio_venta_con_descuento = $('input#precio_venta_con_descuento');

    // se quitan y colocan los correspondientes disables a los inputs
    input_precio_promocional.attr('disabled', true);
    input_precio_promocional.val('');
    input_porcentaje_promocional.attr('disabled', false);

    // si se llegase a seleccionar de nuevo, se vuelve a colocar el calcular el precio con descuento
    input_precio_venta_con_descuento.val(parseInt(input_precio_venta_sin_descuento.val()) - parseInt(input_precio_venta_sin_descuento.val() * input_porcentaje_promocional.val() / 100))
});

$('input#porcentaje_promocional').on('keyup', function(){
    var input_porcentaje_promocional = $('input#porcentaje_promocional');
    var input_precio_venta_sin_descuento = $('input#precio_venta_sin_descuento');
    var input_precio_venta_con_descuento = $('input#precio_venta_con_descuento');

    input_precio_venta_con_descuento.val(parseInt(input_precio_venta_sin_descuento.val()) - parseInt(input_precio_venta_sin_descuento.val() * input_porcentaje_promocional.val() / 100))



});

$('#PromocionForm').on('submit', function(event){
    var alert = "";
    var div_alert = $('div#alerts');
    var radio_precio_promocional = $('input#radio_precio_promocional');
    var radio_porcentaje_promocional = $('input#radio_porcentaje_promocional');

    var input_precio_promocional = $('input#precio_promocional');
    var input_porcentaje_promocional = $('input#porcentaje_promocional');

    var cant_filas = $('table#promocion tbody').children().length;

    div_alert.html('');

    // si aun no se agrego ningun producto
    if(cant_filas == 0){
        div_alert.html('');
        alert = "<div class= \"alert alert-warning\">" +
                    "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                    "<strong><i class='fa fa-exclamation-circle'></i></strong> Debe agregar al menos un producto a la lista!. Vaya el Paso 2" +
                "</div>";
        div_alert.html(alert);
        event.preventDefault();
    // si ya se agrego algun producto pero aun no se especifico algun precio o porcentaje promocional
    }else if(cant_filas > 0
        && (!radio_precio_promocional.is(':checked') && !radio_porcentaje_promocional.is(':checked'))){

        div_alert.html('');
        alert = "<div class= \"alert alert-warning\">" +
                    "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                    "<strong><i class='fa fa-exclamation-circle'></i></strong> Debe especificar si aplicará precio o porcentaje promocional!. Vaya el Paso 4" +
                "</div>";
        div_alert.html(alert);
        event.preventDefault();
    }else if(cant_filas > 0
        && radio_precio_promocional.is(':checked')
        && input_precio_promocional.val() == ''){

        div_alert.html('');
        alert = "<div class= \"alert alert-warning\">" +
                    "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                    "<strong><i class='fa fa-exclamation-circle'></i></strong> Debe especificar el monto del precio promocional!. Vaya el Paso 4" +
                "</div>";
        div_alert.html(alert);
        event.preventDefault();
    }else if(cant_filas > 0
        && radio_porcentaje_promocional.is(':checked')
        && input_porcentaje_promocional.val() == ''){

        div_alert.html('');
        alert = "<div class= \"alert alert-warning\">" +
                    "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                    "<strong><i class='fa fa-exclamation-circle'></i></strong> Debe especificar el valor del porcentaje promocional!. Vaya el Paso 4" +
                "</div>";
        div_alert.html(alert);
        event.preventDefault();
    }else{
        $('#PromocionForm').submit();
    }

});