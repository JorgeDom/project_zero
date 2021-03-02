/**
 * Created by JorgeD on 30/05/2019.
 */

$(window).on('load', function(){
    $('button#boton_modalProductos').focus()
});

function eliminarFilaV2(articulo, articulo_id){
    var cantidad_reponer = parseInt($('table#ventaActual tbody tr#venta_' + articulo_id + ' td input#cantidad').val()); //se recupera el valor a reponer
    var precio_venta = $('table#ventaActual tbody tr#venta_' + articulo_id + ' td input#subtotal'); //se recupera el subtotal para ese producto
    var precio_venta_total = $('#suma_total');  //se recupera el valor total de la compra
    var operacion = '';
    var url = '';

    if(articulo == 'promocion'){
        operacion = 'quitar_promo';
        url = "/actualizar_tabla_promociones_modal_template_registro_venta/"
    }else if(articulo == 'producto'){
        operacion = 'quitar_prod';
        url = "/actualizar_tabla_productos_modal_template_registro_venta/"
    }

    $.ajax({
        url: url,
        type: "POST",
        data: {articulo_id: articulo_id,
               cantidad_reponer: cantidad_reponer,
               operacion: operacion},    // 2 opciones, 'quitar_promo' o 'quitar_prod'
        success: function (json){
            // ya que se actualizo en la BD, se recarga la tabla dentro del modal y trabajo listo
            $("#listaPromocionesModal").DataTable().ajax.reload();
            $("#listaProductosModal").DataTable().ajax.reload();

            $('tr#venta_' + articulo_id).remove();   //se remueve la fila dentro de la tabla de venta actual

            var cant_filas = $('table#ventaActual tbody').children().length;
            var select_metodo = $('select#metodo_pago');
            var fact_monto = $('input#factura_monto');
            var fact_vuelto = $('input#factura_vuelto');
            var suma_total = $('input#suma_total');

            precio_venta_total.val(parseInt(precio_venta_total.val()) - parseInt(precio_venta.val()));

            // si ya no hay filas en la lista de productos a vender, se procede a reiniciar el formulario completo
            if(cant_filas > 0){
                select_metodo.attr('disabled', false);
                fact_vuelto.val(fact_monto.val() - suma_total.val());
            }else{
                window.location.reload();
            }
        },
        error: function(){}
    });
}

// NO TOCAR, SI SIRVE!. se carga junto con los datos de la tabla dentro del modal de
// productos/promociones en el template de registro de venta
function cargarLista(articulo, articulo_id){
    var input_suma_actual = $('#suma_total');
    var input_factura_monto = $('#factura_monto');
    var input_factura_vuelto = $('#factura_vuelto');
    var suma_actual = input_suma_actual.val();  //se recupera el valor de la suma total

    var precio_venta = $('input#precio_venta_' + articulo_id);
    var input_cant_disponible = $('input#cantidad_disponible_' + articulo_id);
    var cantidad = $('input#cantidad_' + articulo_id);

    var procesar = $('input#botonProcesar');

    if (articulo == 'promocion'){
        var alert_modal_promo = $('div#modalPromociones div.modal-body div#alert');
        var nuevo_precio_prom = precio_venta.val().replace(',', '');

        //si la cantidad a vender es mayor a la cantidad disponible, se emite un alert y se vuelve a limpiar el input
        if (parseInt(input_cant_disponible.val()) < parseInt(cantidad.val()) && parseInt(cantidad.val()) != 0) {
            alert_modal_promo.addClass('alert alert-warning fade show').show();
            alert_modal_promo.html("<button type='button' class='close'>&times;</button>" +
                       "<strong><i class='fa fa-exclamation-circle'></i></strong> La cantidad solicitada supera la cantidad disponible!");
            $('.close').on('click', function(){
                $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
            });
            cantidad.val('');   // se limpia el input para volver a intentar
        //si se da click en el boton agregar pero no se completa ningun caracter en el input, o si el alor ingresado es cero
        }else if (cantidad.val() == '' || cantidad.val() == 0){
            alert_modal_promo.addClass('alert alert-warning fade show').show();
            alert_modal_promo.html("<button type='button' class='close'>&times;</button>" +
                       "<strong><i class='fa fa-exclamation-circle'></i></strong> Por favor, verifique la cantidad ingresada.");
            $('.close').on('click', function(){
                $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
            });
            cantidad.val('');
        //si no se cumple ninguna de las condiciones de arriba, se procede a agregar la promo a la lista de venta
        }else {
            // quitar el 5paso en la funcion (ROLLBACK)
            var subtotal_a_agregar = ((parseInt(nuevo_precio_prom) * parseInt(cantidad.val()))); //se calcula el precio de venta - lo que se tiene que sumar a la lista

            $.ajax({
                url: "/actualizar_tabla_promociones_modal_template_registro_venta/",
                type: "POST",
                data: {promo_id: articulo_id,
                       cantidad_venta: cantidad.val(),
                       operacion: "agregar_promo"},
                success: function (json) {
                    // ya que se actualizo en la BD, se recarga la tabla dentro del modal y trabajo listo
                    $("#listaPromocionesModal").DataTable().ajax.reload();
                    $("#listaProductosModal").DataTable().ajax.reload();

                    if($('table tbody tr#venta_' + articulo_id).length) {    //se verifica que no existan ya productos de ese tipo dentro de los que despacharan
                        var input_cantidad = $('table tbody tr#venta_' + articulo_id + ' td input#cantidad');   //la cantidad del producto ya en lista
                        var input_precio_unit = $('table tbody tr#venta_' + articulo_id + ' td input#articulo_precio_unit'); //precio unitario en Gs. ya en la lista
                        var nueva_cant = parseInt(input_cantidad.val()) + parseInt(cantidad.val()); // lo que ahora deberia haber en la lista
                        var nuevo_precio_venta = parseInt(input_precio_unit.val()) * parseInt(nueva_cant);  //lo que se deberia cobrar ahora

                        $('table tbody tr#venta_' + articulo_id + ' td.col2 ').html(nueva_cant +
                            "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value="+ nueva_cant + " hidden>");
                        $('table tbody tr#venta_' + articulo_id + ' td.col4 ').html(nuevo_precio_venta +
                            "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value="+ nuevo_precio_venta + " hidden>");

                    }else{  // si no existe de ese tipo de producto, se procede a agregar una linea nueva a la lista
                        //se formula la nueva linea que irá en la lista de productos a vender
                        var articulo = "Prom. - " + json['data']['descripcion'];
                        var nueva_linea = "<tr id=\"venta_" + articulo_id + "\" align=\"center\">" +
                            "<td class='col1'>" +
                                 articulo +
                                 "<input type=\"text\" id=\"articulo_id\" name=\"articulo_id\" value=\""+ articulo_id + "\" hidden>" +
                                 "<input type=\"text\" id=\"articulo\" name=\"articulo\" value=\""+ articulo + "\" hidden>" +
                            "</td>" +
                            "<td class='col2'>" +
                                 cantidad.val() +
                                "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value=\"" + cantidad.val() + "\" hidden>" +
                            "</td>" +
                            "<td class='col3'>" +
                                 (parseInt(nuevo_precio_prom)) +
                                 "<input type=\"text\" id=\"articulo_precio_unit\" name=\"articulo_precio_unit\" value="+ parseInt(nuevo_precio_prom) + " hidden>" +
                            "</td>" +
                            "<td class='col4'>" +
                                 subtotal_a_agregar +
                                 "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value=\""+ subtotal_a_agregar + "\" hidden>" +
                            "</td>" +
                            "<td><i onclick=\"eliminarFilaV2('promocion', '" + articulo_id + "');\" class=\"far fa-times-circle\" id=\"deletebtn\"></i></td>" +
                        "</tr>";

                        $("table#ventaActual tbody").append(nueva_linea);
                    }
                },
                error: function () {
                    console.log("error!");
                    //location.reload(true);
                }
            });

            input_suma_actual.val(0);   //se cera el valor de la suma total
            input_suma_actual.val(parseInt(suma_actual) + parseInt(subtotal_a_agregar)); //se coloca el nuevo valor de la suma total
            input_factura_vuelto.val(0);    //se cera el valor del vuelto
            input_factura_vuelto.val(parseInt(input_factura_monto.val()) - parseInt(input_suma_actual.val())) ;  // se recalcula el vuelto en base al monto ya especificado

            if (parseInt(input_suma_actual.val()) > parseInt(input_factura_monto.val())){
                procesar.removeClass('btn-success').addClass('btn-danger');
                procesar.attr('disabled', true);
            }else{
                procesar.removeClass('btn-danger').addClass('btn-success');
                procesar.attr('disabled', false);
            }

        }
    }else if(articulo == 'producto'){
        var alert_modal_prod = $('div#modalProductos div.modal-body div#alert');
        var nuevo_precio_prod = precio_venta.val().replace(',', '');

        //si la cantidad a vender es mayor a la cantidad disponible, se emite un alert y se vuelve a limpiar el input
        if (parseInt(input_cant_disponible.val()) < parseInt(cantidad.val()) && parseInt(cantidad.val()) != 0) {
            alert_modal_prod.addClass('alert alert-warning fade show').show();
            alert_modal_prod.html("<button type='button' class='close'>&times;</button>" +
                       "<strong><i class='fa fa-exclamation-circle'></i></strong> La cantidad solicitada supera la cantidad disponible!");
            $('.close').on('click', function(){
                $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
            });
            cantidad.val('');   // se limpia el input para volver a intentar
        //si se da click en el boton agregar pero no se completa ningun caracter en el input, o si el alor ingresado es cero
        }else if (cantidad.val() == '' || cantidad.val() == 0){
            alert_modal_prod.addClass('alert alert-warning fade show').show();
            alert_modal_prod.html("<button type='button' class='close'>&times;</button>" +
                       "<strong><i class='fa fa-exclamation-circle'></i></strong> Por favor, verifique la cantidad ingresada.");
            $('.close').on('click', function(){
                $('#alert').removeClass('alert alert-warning fade show').addClass('hide').slideUp().hide();
            });
            cantidad.val('');
        //si no se cumple ninguna de las condiciones de arriba, se procede a agregar el producto a la lista de venta
        }else{
            // quitar el 5paso en la funcion (ROLLBACK)
            var subtotal_a_agregar_prods = ((parseInt(nuevo_precio_prod) * parseInt(cantidad.val()))); //se calcula el precio de venta - lo que se tiene que sumar a la lista

            $.ajax({
                url: "/actualizar_tabla_productos_modal_template_registro_venta/",
                type: "POST",
                data: {prod_id: articulo_id,
                       cantidad_venta: cantidad.val(),
                       operacion: "agregar_prod"},
                success: function (json) {
                     // ya que se actualizo en la BD, se recarga la tabla dentro del modal y trabajo listo
                    $("#listaPromocionesModal").DataTable().ajax.reload();
                    $("#listaProductosModal").DataTable().ajax.reload();

                    if($('table tbody tr#venta_' + articulo_id).length) {    //se verifica que no existan ya productos de ese tipo dentro de los que despacharan
                        var input_cantidad = $('table tbody tr#venta_' + articulo_id + ' td input#cantidad');   //la cantidad del producto ya en lista
                        var input_precio_unit = $('table tbody tr#venta_' + articulo_id + ' td input#articulo_precio_unit'); //precio unitario en Gs. ya en la lista
                        var nueva_cant = parseInt(input_cantidad.val()) + parseInt(cantidad.val()); // lo que ahora deberia haber en la lista
                        var nuevo_precio_venta = parseInt(input_precio_unit.val()) * parseInt(nueva_cant);  //lo que se deberia cobrar ahora

                        $('table tbody tr#venta_' + articulo_id + ' td.col2 ').html(nueva_cant +
                            "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value="+ nueva_cant + " hidden>");
                        $('table tbody tr#venta_' + articulo_id + ' td.col4 ').html(nuevo_precio_venta +
                            "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value="+ nuevo_precio_venta + " hidden>");

                    }else{  // si no existe de ese tipo de producto, se procede a agregar una linea nueva a la lista
                        //se formula la nueva linea que irá en la lista de productos a vender
                        var articulo = json['data']['marca'] + " - " + json['data']['descripcion'] +  " - " + json['data']['presentacion'];
                        var nueva_linea = "<tr id=\"venta_" + articulo_id + "\" align=\"center\">" +
                            "<td class='col1'>" +
                                 articulo +
                                 "<input type=\"text\" id=\"articulo_id\" name=\"articulo_id\" value=\""+ articulo_id + "\" hidden>" +
                                 "<input type=\"text\" id=\"articulo\" name=\"articulo\" value=\""+ articulo + "\" hidden>" +
                            "</td>" +
                            "<td class='col2'>" +
                                 cantidad.val() +
                                "<input type=\"text\" id=\"cantidad\" name=\"cantidad\" value=\"" + cantidad.val() + "\" hidden>" +
                            "</td>" +
                            "<td class='col3'>" +
                                 (parseInt(nuevo_precio_prod)) +
                                 "<input type=\"text\" id=\"articulo_precio_unit\" name=\"articulo_precio_unit\" value="+ parseInt(nuevo_precio_prod) + " hidden>" +
                            "</td>" +
                            "<td class='col4'>" +
                                 subtotal_a_agregar_prods +
                                 "<input type=\"text\" id=\"subtotal\" name=\"subtotal\" value=\""+ subtotal_a_agregar_prods + "\" hidden>" +
                            "</td>" +
                            "<td><i onclick=\"eliminarFilaV2('producto', '" + articulo_id + "');\" class=\"far fa-times-circle\" id=\"deletebtn\"></i></td>" +
                        "</tr>";

                        $("table#ventaActual tbody").append(nueva_linea);
                    }
                },
                error: function () {}
            });

            input_suma_actual.val(0);   //se cera el valor de la suma total
            input_suma_actual.val(parseInt(suma_actual) + parseInt(subtotal_a_agregar_prods)); //se coloca el nuevo valor de la suma total
            input_factura_vuelto.val(0);    //se cera el valor del vuelto
            input_factura_vuelto.val(parseInt(input_factura_monto.val()) - parseInt(input_suma_actual.val())) ;  // se recalcula el vuelto en base al monto ya especificado

            if (parseInt(input_suma_actual.val()) > parseInt(input_factura_monto.val())){
                procesar.removeClass('btn-success').addClass('btn-danger');
                procesar.attr('disabled', true);
            }else{
                procesar.removeClass('btn-danger').addClass('btn-success');
                procesar.attr('disabled', false);
            }
        }
    }
}

/*verificacion en registro_venta.html*/
//Paso 1
var modal_productos = $('#modalProductos');
modal_productos.on('hide.bs.modal', function(){
    var cant_filas = $('table#ventaActual tbody').children().length;

    if(cant_filas > 0){
        $('select#metodo_pago').attr('disabled', false);
    }
});

modal_productos.on('show.bs.modal', function(){
    $('input[type="search"]').attr('autofocus', true);
});

var modal_promociones = $('#modalPromociones');
modal_promociones.on('hide.bs.modal', function(){
    var cant_filas = $('table#ventaActual tbody').children().length;

    if(cant_filas >0){
        $('select#metodo_pago').attr('disabled', false);
    }
});

modal_promociones.on('show.bs.modal', function(){
    $('input[type="search"]').attr('autofocus', true);
});

//Paso 2
$('#modalClientes').on('hide.bs.modal', function(){
    var cant_filas = $('table#ventaActual tbody').children().length;
    var select_metodo = $('select#metodo_pago');

    /*if(cant_filas > 0){
        select_metodo.attr('disabled', false)
    }else{
        select_metodo.attr('disabled', true);
        select_metodo.val('default')
    }*/
});

//Paso 3
$('select#metodo_pago').on('change', function (){
    var select_metodo = $('select#metodo_pago option:selected');
    var input_metodo_pago_hidden = $('input#metodo_pago_hidden');
    var monto = $('input#monto');
    var input_boleta_nro = $('input#boletaNro');

    var fact_vuelto = $('input#factura_vuelto');

    var procesar = $('input#botonProcesar');

    monto.attr('disabled', false);
    input_metodo_pago_hidden.val(select_metodo.val());

    if(select_metodo.val() == 'efectivo' && fact_vuelto.val() >= 0 && monto.val() != ''){
        input_boleta_nro.hide();
        input_boleta_nro.val('');
        //procesar.removeClass('btn-danger').addClass('btn-success');
        //procesar.attr('disabled', false);
    }else if (select_metodo.val() == 'td' || select_metodo.val() == 'tc'){
        $('input#boletaNro').show();
        //procesar.removeClass('btn-success').addClass('btn-danger');
        //procesar.attr('disabled', true);
    }else{
        input_boleta_nro.hide();
        input_boleta_nro.val('');
    }
});

$('input#monto').on('keyup', function(){
    var select_metodo = $('select#metodo_pago option:selected');
    var monto = $('input#monto');
    var input_boleta_nro = $('input#boletaNro');
    var fact_monto = $('input#factura_monto');
    var fact_vuelto = $('input#factura_vuelto');
    var suma_total = $('input#suma_total');

    var procesar = $('input#botonProcesar');

    fact_monto.val(monto.val());
    fact_vuelto.val(monto.val() - suma_total.val());

    if(select_metodo.val() == 'efectivo' && fact_vuelto.val() >= 0){
        procesar.removeClass('btn-danger').addClass('btn-success');
        procesar.attr('disabled', false);
    }else if ((select_metodo.val() == 'tc' || select_metodo.val() == 'td') && fact_vuelto.val() == 0 && input_boleta_nro.val() != '') {
        procesar.removeClass('btn-danger').addClass('btn-success');
        procesar.attr('disabled', false);
    }else{
        procesar.removeClass('btn-success').addClass('btn-danger');
        procesar.attr('disabled', true);
    }
});

$('input#boletaNro').on('keyup', function(){
    var input_boleta_nro = $('input#boletaNro');
    var select_metodo = $('select#metodo_pago option:selected');
    var fact_vuelto = $('input#factura_vuelto');
    var input_nro_boleta_hidden = $('input#nro_boleta_hidden');

    var procesar = $('input#botonProcesar');
    input_nro_boleta_hidden.val(input_boleta_nro.val());

    if ((select_metodo.val() == 'tc' || select_metodo.val() == 'td') && fact_vuelto.val() == 0 && input_boleta_nro.val() != '') {
        procesar.removeClass('btn-danger').addClass('btn-success');
        procesar.attr('disabled', false);
    }else{
        procesar.removeClass('btn-success').addClass('btn-danger');
        procesar.attr('disabled', true);
    }
});

// NO TOCAR, SI SIRVE!. se carga junto con los datos de la tabla dentro del modal de
// clientes en el template de registro de ventas
function cargarCliente(cliente, ruc){
    var input_nombre_cliente = $('#nombreCliente');
    var input_ruc_cliente = $('#rucCliente');

    input_nombre_cliente.val(cliente);
    input_ruc_cliente.val(ruc);

    $('#modalClientes').modal('hide');
}

$('button#boton_agregar_cliente').on('click', function(){
    $('#modalClientes').modal('hide');
    $('#modalNuevoCliente').modal('show');
});

$('#formModalNuevoCliente').on('submit', function(event){
    event.preventDefault();

    var alert = "";
    var modal = $('div#modalNuevoCliente div#alerts');

    var cliente = $('input#id_nombre_apellido');
    var ci_ruc = $('input#id_ci_ruc');
    var dig_verif = $('input#id_dig_verif');

    var cliente_factura = $('input#nombreCliente');
    var ci_ruc_factura = $('input#rucCliente');

    $.ajax({
        url:"/nuevo_cliente/",
        type:"POST",
        data:{nombre_apellido: cliente.val(),
                ci_ruc: ci_ruc.val(),
                dig_verif: dig_verif.val(),
                tel_nro: $('#id_tel_nro').val(),
                direccion: $('#id_direccion').val(),
                email: $('#id_email').val()},

        success: function(json){
            var tipo = json['propiedad_alerts']['tipo'];
            var icono = json['propiedad_alerts']['icono'];
            var mensaje = json['propiedad_alerts']['mensaje'];

            //si el alert es un warning, significa que el CI/RUC ya existe no se permite avanzar, se muestra el aler
            if(json['propiedad_alerts']['tipo'] == 'alert-warning'){
                alert = "<div class= \"alert "  + tipo + "\">" +
                            "<button type='button' class='close' data-dismiss='alert'>&times;</button>" +
                            "<strong><i class='fa " + icono + "'></i></strong>" +  mensaje +
                        "</div>";
                modal.html(alert)
            } else {    //si no es warning, quiere decir que se almaceno todos sin problemas se procede a lo demas
                alert = "";
                $('#modalNuevoCliente').modal('hide');
                cliente_factura.val(cliente.val());
                ci_ruc_factura.val(ci_ruc.val() + "-" + dig_verif.val());
                $("#listaClientesModal").DataTable().ajax.reload(null, false);
            }
        },

        error : function() {
            console.log("error!");
            //location.reload(true);
        }
    });
});

function setBandera(){
    var bandera = $('input#bandera');
    bandera.val('TRUE');
}

$(window).on('beforeunload', function(event){
    var bandera = $('input#bandera');

    if(bandera.val() == 'FALSE') {  //si es FALSE significa que el input no se cambio a TRUE con la funcion setBandera()
        event.preventDefault();
        console.log('bandera: ', bandera.val());

        var VentaForm = $('#VentaForm');
        var datos_form = VentaForm.serializeArray();
        datos_form = JSON.stringify(datos_form);

        $.ajax({
            url: "/rollback_bd/",
            type: "POST",
            data: {datos_form: datos_form},
            success: function (json) {
                console.log(json)
            },
            error: function () {
            }
        });

        event.returnValue = '';
        return null;
    }else{
        event.preventDefault();
        console.log('bandera: ', bandera.val());
    }
});

$('#formCajaApertura').on('submit', function(event){
    event.preventDefault();
    var monto_apertura = $('#id_caja_apertura');
    var modal = $('#modalAbrirCaja');

    $.ajax({
        url:"/abrir_caja/",
        type:"POST",
        data:{monto_apertura: monto_apertura.val()},

        success: function(json){
            window.location.reload();
        },

        error : function() {
            console.log("error!");
        }
    });
});
