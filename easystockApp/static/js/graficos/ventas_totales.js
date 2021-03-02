/**
 * Created by JorgeD on 12/07/2019.
 */

$('#seleccionar_mes').on('change', function(event){
    mostrarGrafico();
});

$('#seleccionar_anho').on('change', function(event){
    mostrarGrafico();
});

function mostrarGrafico(){
    var opcion_mes = $('#seleccionar_mes').val();
    var opcion_anho = $('#seleccionar_anho').val();

    var div_tabla = $('#div_tabla_ventas_totales');
    var tabla = $('#tabla_ventas_totales');


    if(opcion_mes != null && opcion_anho != null) {
        $.ajax({
            url: "/consultar_disponibilidad_datos/",
            type: "POST",
            data: {mes: opcion_mes,
                   anho: opcion_anho},
            success: function (datos) {
                if (datos['cantidad'] > 0){
                    div_tabla.attr('hidden', false);
                    tabla.DataTable({
                        "scrollCollapse": true,
                        "paging": false,
                        "order": [2, 'asc'],
                        "info": false,
                        "destroy": true,
                        "language": {
                            "lengthMenu": "Mostrando _MENU_ registros por página",
                            "zeroRecords": "No se cuentan con productos en el stock",
                            "info": "Mostrando la página _PAGE_ de _PAGES_",
                            "infoEmpty": "No hay productos disponibles",
                            "infoFiltered": "(filtrado de un total de _MAX_ productos)",
                            "search": "Filtrar resultados: ",
                            "paginate": {
                                "previous": "Anterior",
                                "next": "Siguiente"
                            }
                        },
                        "ajax": {
                            url: "/get_top_100/",
                            type: "POST",
                            data: {
                                mes: opcion_mes,
                                anho: opcion_anho
                            }
                        },
                        "columnDefs": [
                            {"className": "articulo", "targets": [0]},
                            {"className": "cantidad", "targets": [1]},
                            {"className": "porcentaje", orderable: false, "targets": [2]}
                        ]
                    }).clear().draw();
                }else{
                    div_tabla.attr('hidden', true);
                    tabla.DataTable().destroy()
                }
            },
            error: function () {

            }
        });
    }
}