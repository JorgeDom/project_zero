/**
 * Created by JorgeD on 26/07/2019.
 */

$('select#seleccionar_anho').on('change', function(){
    var anho = $(this).val();
    var select_mes = $('select#seleccionar_mes');

    select_mes.html('');  //se vacia el select
    // se agrega la primera opcion de cualquier select
    select_mes.append($('<option>', {value: '',
                                                text: 'Eliga el Mes...',
                                                selected: 'selected',
                                                disabled: 'disabled'}));

    $.ajax({
        url:"/get_meses_x_anho/",
        type:"POST",
        data:{anho: anho},
        success: function(json){
            select_mes.attr('disabled', false);
            for(i=0; i<json['cantidad']; i++){
                select_mes.append($('<option>', {
                    value: json['meses'][i][0],
                    text: json['meses'][i][1]
                }))
            }
        },
        error: function(){}
    });
});