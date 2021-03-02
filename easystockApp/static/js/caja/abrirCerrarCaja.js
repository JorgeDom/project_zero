/**
 * Created by JorgeD on 31/07/2019.
 */

$('#formCajaApertura').on('submit', function(event){
    event.preventDefault();
    var monto_apertura = $('#id_caja_apertura');
    var modal = $('#modalAbrirCaja');

    $.ajax({
        url:"/abrir_caja/",
        type:"POST",
        data:{monto_apertura: monto_apertura.val(),
              operacion: 'apertura'},

        success: function(json){
            console.log('apertura de caja exitosa');
            window.location.reload();
        },

        error : function() {
            console.log("error!");
        }
    });
});

$('#boton_pregunta_cerrar_caja').on('click', function(event){
    $.ajax({
        url:"/cerrar_caja/",
        type:"POST",
        data:{},

        success: function(json){
            window.location.reload();
        },

        error : function() {
            console.log("error!");
        }
    });
});