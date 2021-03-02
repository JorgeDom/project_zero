/**
 * Created by JorgeD on 08/10/2018.
 */

$(document).ready(function () {
    $("#calendario").zabuto_calendar({
        cell_border: true,
        today: true,
        weekstaron: 0,
        nav_icon:{
            prev: '<i class="fa fa-chevron-left"></i>',
            next: '<i class="fa fa-chevron-right"></i>'
        },
        show_previous: 3,
        show_next: 0,
        language: "es",
        legend:[
            {type: "block", label: "Presente", classname: "presente"},
            {type: "block", label: "Ausente", classname:"ausente"},
            {type: "block", label: "Día libre", classname:"libre"}
        ],
        data: getAsistencia(),
        action: function () {
            return mostrarModal(this.id, false);
        },
        action_nav: function(){
            getTablaAsistencia(this.id);
            getGraficoAJAX(this.id);
            return true
        }
    });

    function mostrarModal(id) {
        var date = $("#" + id).data("date");
        var modalCalendar = $("#modalCalendar");

        modalCalendar.find('p#fecha').text(date);
        modalCalendar.find('input#fecha').val(date);
        modalCalendar.find('input#fecha').attr('value', date);
        modalCalendar.modal('show');

        return true;
    }

    function getAsistencia(){
        var funcionario_id = window.location.search;
        var resultado='';
        //console.log(funcionario_id);

        $.ajax({
        url:"../../get_asistencia/",
        type:"POST",
        data:{func_id: funcionario_id},
        async: false,

        success: function(json){
            console.log("obtenida asistencia!");
            resultado = json;
        },

        error : function() {
            console.log("error!");
            //location.reload(true);
        }});
        return resultado;
    }

    function getTablaAsistencia(id){
        var identificador = $("#" + id);
        var nav = identificador.data("navigation");
        var to = identificador.data("to");
        console.log('nav ' + nav + ' to: ' + to.month + '-' +  to.year);

        $.ajax({
        url:"../../get_tabla_asistencia/",
        type:"POST",
        data:{
            func_id: window.location.search,
            mes: to.month,
            anho: to.year
        },

        success: function(lista_asistencia){
            var trTablaAsistencia = '';
            var trTablaJornadaMenor = '';
            var cantidadesHTML = '';
            $("#tablaAsistencia tr:has(td)").remove();
            $("#tablaCantidades tr:has(td)").remove();
            $("#tablaJornadaMenor tr:has(td)").remove();

            /*TABLA donde se muestran todos los dias del mes*/
            if(lista_asistencia.cantidades.presente == 0 && lista_asistencia.cantidades.ausente == 0 && lista_asistencia.cantidades.libre == 0)
                trTablaAsistencia +=
                        '<tr align="center">' +
                            '<td colspan="5"> No se cuentan con registros de asistencia </td>' +
                        '</tr>';
                $.each(lista_asistencia.lista, function (i, lista_asistencia){
                    trTablaAsistencia +=
                        '<tr align="center">' +
                            '<td>' + lista_asistencia.fecha + '</td>' +
                            '<td>' + lista_asistencia.hora_entrada + '</td>' +
                            '<td>' + lista_asistencia.hora_salida + '</td>' +
                            '<td>' + lista_asistencia.horas_trabajadas + '</td>' +
                            '<td>' + lista_asistencia.horas_extras + '</td>' +
                        '</tr>';
                });
            cantidadesHTML =
                '<tr align="center">' +
                    '<td><strong>Días presente:</strong> ' +  lista_asistencia.cantidades.presente + '</td>' +
                    '<td><strong>Días ausente:</strong> ' + lista_asistencia.cantidades.ausente + '</td>' +
                    '<td><strong>Días libres:</strong> ' + lista_asistencia.cantidades.libre + '</td>' +
                '</tr>';

            /*TABLA con los dias en donde el funcionario no cumplio con la jornada minima establecida*/
            if(Object.keys(lista_asistencia.jornada_menor).length == 0)
                trTablaJornadaMenor += '<tr align="center">' +
                                           '<td colspan="4"> Se han cumplido con todas las jornadas laborales mínimas </td>' +
                                       '</tr>';
                $.each(lista_asistencia.jornada_menor, function (i, lista_asistencia){
                    trTablaJornadaMenor +=
                        '<tr align="center">' +
                            '<td>' + lista_asistencia.fecha + '</td>' +
                            '<td>' + lista_asistencia.hora_entrada + '</td>' +
                            '<td>' + lista_asistencia.hora_salida + '</td>' +
                            '<td>' + lista_asistencia.horas_trabajadas + '</td>' +
                        '</tr>';
                });

            $('#tablaAsistencia').append(trTablaAsistencia);
            $('#tablaCantidades').append(cantidadesHTML);
            $('#tablaJornadaMenor').append(trTablaJornadaMenor);
        },

        error : function() {
            console.log("error!");
        }

    });
    }

    function getGraficoAJAX(id){
        var funcionario_id = window.location.search;
        var identificador = $("#" + id);
        var nav = identificador.data("navigation");
        var to = identificador.data("to");
        console.log('nav ' + nav + ' to: ' + to.month + '-' +  to.year);
        console.log('hola');

        $.ajax({
            url:"../../get_datos_grafico_horas_trabajadas/",
            type:"POST",
            data:{
                func_id: funcionario_id,
                mes: to.month,
                anho: to.year
            },

            success: function(json){
                Highcharts.chart('graficoHorasTrabajadas', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Cantidad de Horas trabajadas'
                    },
                    xAxis: {
                        categories: json['dias_del_mes']
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Cantidad de horas trabajadas'
                        },
                        stackLabels: {
                            enabled: false,
                            style: {
                                fontWeight: 'bold',
                                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                            }
                        }
                    },
                    legend: {
                        align: 'center',
                        x: 0,
                        verticalAlign: 'top',
                        y: 20,
                        floating: true,
                        backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
                        borderColor: '#CCC',
                        borderWidth: 1,
                        shadow: true
                    },
                    tooltip: {
                        headerFormat: '<b>{point.x}</b><br/>',
                        pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            dataLabels: {
                                enabled: true,
                                color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                            }
                        }
                    },
                    colors:[ '#008000', '#4d4dff'],
                    series: [{
                        name: 'Hrs. Extras',
                        data: json['horas_extras']
                    }, {
                        name: 'Hrs. Normales',
                        data: json['horas_normales']
                    }],
                    credits: {
                        enabled: false
                    }
                });
            },

            error : function() {
                console.log("error!");
            }
        });
    }
});