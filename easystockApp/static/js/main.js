$(document).ready(function(){

    $('#modalDeleteCliente').on('show.bs.modal', function(event){
        var cliente_id = $(event.relatedTarget).attr('data-cliente_id'); //se extrae lo que se almaceno en data-*

        var modal = $(this);
        modal.find('input#cliente_id').val(cliente_id)
    });
});

function additems(origen, destino){
    //$(origen).find(':selected').appentTo(destino);
    var item_val = $(origen).find(':selected').val();
    var item_text = $(origen).find(':selected').text();
    var cantidad = $('#id_cantidad_promocional').val();

    var nueva_linea = "<tr align=\"center\">" +
                        "<td><input name='cantidad_" + item_val + "' value='" + cantidad + "' hidden>" +
                            "<input type='checkbox' name='record'></td>" +
                        "<td>" + item_text + "</td>" +
                        "<td>" + cantidad + "</td>" +
                      "</tr>";

    $("table tbody").append(nueva_linea);
}

$('#formModalDeleteCliente').on('submit', function(event){
    event.preventDefault();
    deleteCliente();
});

function deleteCliente(){
    console.log('entrando en la funcion deleteCliente');

    $.ajax({
        url:"/eliminar_cliente/",
        type:"POST",
        data:{cliente_id: $('#cliente_id').val()},

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

/*verificacion en registro_venta.html*/
$('#boton_agregar_item').on('click', function(){
    $("table tbody #tabla_vacia").remove();
    additems('#id_productos', '#tabla_productos')
});

$('#boton_quitar_item').on('click', function(){
    $("table tbody").find('input[name="record"]').each(function(){
        if($(this).is(":checked")){
            $(this).parents("tr").remove();
        }
    });
});


