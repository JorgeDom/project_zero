/**
 * Created by JorgeD on 01/08/2019.
 */

// se recupera el monto de apertura una vez abierto el modal
$('#modalAbrirCaja').on('show.bs.modal', function(event){
    var item_id = $(event.relatedTarget).attr('data-item_id');
    var input_item_id = $('#item_id');
    var input_caja_apertura = $('#id_caja_apertura');

    $.ajax({
        url:"/get_monto_apertura_caja/",
        type:"POST",
        data:{item_id: item_id},

        success: function(json){
            input_item_id.val(item_id);
            input_caja_apertura.val(json['monto_apertura'])
        },

        error : function() {
            console.log("error!");
        }
    });
});

$('#formCajaApertura').on('submit', function(event){
    event.preventDefault();
    var monto_apertura = $('#id_caja_apertura');
    var input_item_id = $('#item_id');

    $.ajax({
        url:"/abrir_caja/",
        type:"POST",
        data:{monto_apertura: monto_apertura.val(),
              item_id: input_item_id.val(),
              operacion: 'editar'},

        success: function(json){
            window.location.reload();
        },

        error : function() {
            console.log("error!");
        }
    });
});

$(window).on('load', function(){
    $('input[type="search"]').focus();
});