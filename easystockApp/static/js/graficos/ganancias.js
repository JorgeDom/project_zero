/**
 * Created by JorgeD.
 */

$(window).on('load', function(event){
    Highcharts.setOptions({
        lang: {
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar imagen PDF',
            downloadSVG: 'Descargar imagen SVG',
            printChart: 'Imprimir',
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom',
            thousandsSep: ",",
            decimalPoint: '.'
        }
    });
    $.ajax({
        url:"/get_ganancias_diarias/",
        type:"POST",
        data:{},
        success: function(datos){

            Highcharts.stockChart('grafico_costo_venta_ganancia', {
                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: 'Variación diaria de los Valores de Venta, Costo y Ganancia'
                },

                yAxis: [{
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'Venta vs. Costo'
                    },
                    height: '60%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'Ganancia'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }],

                tooltip: {
                    split: true
                },

                series: [{
                    type: 'arearange',
                    name: 'Venta vs. Costo',
                    data: datos['costo_venta'],
                    dataGrouping: {
                        units: [[
                            'week',                         // unit name
                            [1]                             // allowed multiples
                        ], [
                            'month',
                            [1, 2, 3, 4, 6]
                        ]]
                    }
                }, {
                    type: 'column',
                    name: 'Ganancia',
                    data: datos['ganancia'],
                    yAxis: 1,
                    dataGrouping: {
                        units: [[
                            'week',                         // unit name
                            [1]                             // allowed multiples
                        ], [
                            'month',
                            [1, 2, 3, 4, 6]
                        ]]
                    }
                }]
            });
        },
        error: function(){}
    });
});