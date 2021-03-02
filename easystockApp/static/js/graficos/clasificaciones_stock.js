/**
 * Created by JorgeD on 23/07/2019.
 */
$(window).on('load', function(event){
    $.ajax({
        url:"/get_distribucion_stock/",
        type:"POST",
        data:{},
        success: function(datos){
            Highcharts.chart('grafico_clasificaciones_stock', {
            chart: {
                type: 'pie'
            },
            title: {
                text: 'Distribución del Stock en base a las clasificaciones'
            },
            subtitle: {
                text: 'Click en las clasificaciones para ver las Marcas'
            },
            plotOptions: {
                series: {
                    dataLabels: {
                        enabled: true,
                        format: '{point.name}: {point.y:.1f}%'
                    }
                }
            },

            tooltip: {
                headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> del total ({point.cantidad} de {point.suma_total})<br/>'
            },

            series: [
                {
                    name: 'Clasificaciones',
                    colorByPoint: true,
                    data: datos['series']
                }
            ],
            drilldown: {
                series: datos['drilldown_series']
            }
            })
        },
        error: function(){}
    });
});