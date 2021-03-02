/**
 * Created by JorgeD on 09/07/2019.
 */

$('#seleccionar_mes').on('change', function(event){
    mostrarGraficoBarras();
});

$('#seleccionar_anho').on('change', function(event){
    mostrarGraficoBarras();
});


function mostrarGraficoBarras(){
    var opcion_mes = $('#seleccionar_mes').val();
    var opcion_mes_text = $('#seleccionar_mes option:selected').text();
    var opcion_anho = $('#seleccionar_anho').val();

    if(opcion_mes != null && opcion_anho != null){
        $.ajax({
            url: "/get_ranking_articulos/",
            type: "POST",
            data: {mes: opcion_mes,
                   anho: opcion_anho},
            success: function (datos) {
                Highcharts.chart('grafico_ranking_articulos', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Ranking de los ' + datos['ranking'] + ' articulos más vendidos'
                    },
                    subtitle: {
                        text: 'En base a las ventas diarias en ' + opcion_mes_text + ' del ' + opcion_anho
                    },
                    xAxis: {
                        categories: datos['categorias'],
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Cantidad (Un.)'
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">Día {point.key}/'+ opcion_mes +'</span><table>',
                        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                            '<td style="padding:0"><b>{point.y}</b></td></tr>',
                        footerFormat: '</table>',
                        shared: true,
                        useHTML: true
                    },
                    plotOptions: {
                        column: {
                            pointPadding: 0.2,
                            borderWidth: 0
                        }
                    },
                    series: datos['series']
                });


            },
            error: function () {

            }
        });
    }
}