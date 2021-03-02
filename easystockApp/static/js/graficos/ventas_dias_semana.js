/**
 * Created by JorgeD on 19/07/2019.
 */

$('#seleccionar_mes').on('change', function(event){
    mostrarMapaCalor();
});

$('#seleccionar_anho').on('change', function(event){
    mostrarMapaCalor();
});

function mostrarMapaCalor(){
    var opcion_mes = $('#seleccionar_mes').val();
    var opcion_mes_text = $('#seleccionar_mes option:selected').text();
    var opcion_anho = $('#seleccionar_anho').val();

    if(opcion_mes != null && opcion_anho != null){
        $.ajax({
            url: "/get_ventas_dias_x_semana/",
            type: "POST",
            data: {mes: opcion_mes,
                   anho: opcion_anho},
            success: function (datos) {


                Highcharts.chart('grafico_ventas_dias_x_semana', {

                chart: {
                    type: 'heatmap',
                    marginTop: 40,
                    marginBottom: 80,
                    plotBorderWidth: 1
                },

                title: {
                    text: 'Venta de artículos por día de la semana'
                },

                xAxis: {
                    categories: datos['xAxis_categories']
                },

                yAxis: {
                    categories: datos['yAxis_categories'],
                    title: null
                },

                colorAxis: {
                    min: 0,
                    minColor: '#FFFFFF',
                    maxColor: Highcharts.getOptions().colors[0]
                },

                legend: {
                    align: 'right',
                    layout: 'vertical',
                    margin: 0,
                    verticalAlign: 'top',
                    y: 25,
                    symbolHeight: 280
                },

                tooltip: {
                    formatter: function () {
                        return '<b>' + this.series.xAxis.categories[this.point.x] + '</b><br><b>' +
                            this.point.value + '</b> vendidos en <b>' + this.series.yAxis.categories[this.point.y] + '</b>';
                    }
                },

                series: [{
                    name: 'Ventas por artículo',
                    borderWidth: 1,
                    data: datos['series_data'],
                    dataLabels: {
                        enabled: true,
                        color: '#000000'
                    }
                }]

            });
            },
            error: function () {

            }
        });
    }
}