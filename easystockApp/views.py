from django.http import JsonResponse
from django.shortcuts import render, redirect
from pymongo import errors
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from datetime import datetime, timedelta, date
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group, Permission
from bson.json_util import dumps

from easystockApp.forms import *

import pymongo, operator, json, math, time

# VARIABLES GLOBALES
# Se establece la conexion a la bd cada vez que se necesite, recibe la coleccion de donde se quiere obtener los datos.
clienteMongo = pymongo.MongoClient("mongodb://localhost:27017")
db = clienteMongo["EasyStock"]
col_producto = db["easystockApp_producto"]
col_eventos = db["eventosApp_evento"]
col_ventas = db["easystockApp_venta"]
col_promocion = db["easystockApp_promocion"]
col_clientes = db["easystockApp_cliente"]
col_CMD = db["easystockApp_CMD"]    # coleccion donde se almacenan las clasificaciones, marcas y distribuidores de los productos
col_caja = db['easystockApp_caja']
col_stock = db['easystockApp_stock']    #coleccion donde se almacenan los datos historicos del valor del stock

DATOS_EMPRESA = {
    'razon_social': 'Nombre de la empresa',
    'direccion': 'Dirección de la empresa',
    'telefono': '021-123456',
    'ruc': 'RUC de la empresa',
    'timbrado_nro': 00000000,
    'vigencia_desde': '00/00/0000',
    'vigencia_hasta': '00/00/0000'
}

DATOS_FACTURA = {
    'nro_suc': 1,
    'nro_caja': 1,
}

MESES_DEL_ANHO = (
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Setiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre'),
)

DIAS_DE_LA_SEMANA = (
    (0, 'Lunes'),
    (1, 'Martes'),
    (2, 'Miercoles'),
    (3, 'Jueves'),
    (4, 'Viernes'),
    (5, 'Sábado'),
    (6, 'Domingo')
)

#TODO para devolver HTML directo desde DJANGO (no a AJAX) en el template se coloca de la siguiente manera -> {{ respuesta | safe }}
#TODO agregar indices a las colecciones

# se registra la operacion dentro de la coleccion EventosAPP_evento
def reg_evento(evento, descripcion, fecha_hora, responsable):
    # tipos de operacion: compra_producto, crear_promocion, agregar_cliente, venta, editar_datos_producto,
    # editar_datos_cliente, eliminar_producto, elminar_promocion, eliminar_cliente, anular
    evento = {'evento': evento,
              'descripcion': descripcion,
              'fecha_hora': fecha_hora,
              'responsable': responsable}

    #evento.update({'_id': str(uuid.uuid4())})  # se genera un codigo aleatorio, a parte el _id que genera mongodb

    col_eventos.insert_one(evento)

    return

# se genera el numero de factura, preguntando por la factura anterior en el BD.
# primeros 3 digitos corresponden al numero de sucursal
# siguientes 3 digitos corresponden al numero de caja
# sigueintes 7 digitos corresponden al numero de factura
# El diccionario se carga con Int, y antes de devolver se trasnforma a str y se completa con los ceros correspondientes
def generar_nro_factura():
    ult_factura = {}

    # se busca en la base de datos el ultimo documento agregado a la coleccion easystockApp_ventas
    resultado_query = col_ventas.find({}).sort('_id', pymongo.DESCENDING).limit(1)
    # si el .count() devuelve 0 no existe, si devuelve 1, si existe
    existe_doc = resultado_query.count()
    for item in resultado_query:
        ult_factura = item['nro_factura']

    # se genera el numero de factura
    if existe_doc == 0: # se genera la primera factura si es que no se encuentra ninguna factura al principio
        sig_factura = {
            'nro_suc': 1,
            'nro_caja': 1,
            'nro_factura': 1
        }
    else:   # si no es cero, se pregunta los datos de la ultima factura
        sig_factura = {
            'nro_suc': DATOS_FACTURA['nro_caja'],
            'nro_caja': DATOS_FACTURA['nro_caja'],
            'nro_factura': int(ult_factura['nro_factura']) + 1
        }
    return sig_factura

def separadaroDeMiles(valor):
    valor_transformado = str("{0:,}".format(int(valor)))
    return valor_transformado

# recibe el request y el indice donde se encuentra el articulo dentro de la lista de articulos vendidos
def calcular_iva_gravadas_producto(request, i):

    articulo = col_producto.find_one({'_id': ObjectId(request.POST.getlist('articulo_id')[i])}) # se busca en la BD el articulo
    tipo_impuesto = articulo['impuesto']    # se obtiene su tipo de impuesto 5 / 10 / exenta
    precio_costo = articulo['precio_costo'] # se obtiene el precio de costo unitario del articulo
    impuesto = 0    # donde se calculara el valor del impuesto que se debe abonar por el articulo en base a la cantidad vendida

    # dependiendo del tipo de impuesto, el subtotal pagado por el articulo se divide por 21 o 11
    if tipo_impuesto == '5':
        impuesto = int(request.POST.getlist('subtotal')[i]) / 21
    elif tipo_impuesto == '10':
        impuesto = int(request.POST.getlist('subtotal')[i]) / 11
    elif tipo_impuesto == 'exenta':
        impuesto = 0

    dict_ivas_gravadas = {
        'iva_5': int(impuesto) if tipo_impuesto == '5' else 0,
        'iva_10': int(impuesto) if tipo_impuesto == '10' else 0,
        'exenta': int(request.POST.getlist('subtotal')[i]) if tipo_impuesto == 'exenta' else 0,
        'gravadas_5': int(request.POST.getlist('subtotal')[i]) if tipo_impuesto == '5' else 0,
        'gravadas_10': int(request.POST.getlist('subtotal')[i]) if tipo_impuesto == '10' else 0,
    }

    # se arma el diccionario para este articulo en particular
    dict_articulo = {
        'articulo_id': request.POST.getlist('articulo_id')[i],
        'articulo': request.POST.getlist('articulo')[i],
        'cantidad': request.POST.getlist('cantidad')[i],
        'precio_costo': int(precio_costo) * int(request.POST.getlist('cantidad')[i]),
        'subtotal': int(request.POST.getlist('subtotal')[i]),
        'tipo_impuesto': tipo_impuesto,
        'total_impuesto': int(impuesto)
    }

    return {'datos_articulo': dict_articulo, 'datos_iva_grav': dict_ivas_gravadas}

# recibe lo mismo que la funcion calcular_iva_gravadas_producto
def calcular_iva_gravadas_promocion(request, i):
    lista_productos_en_promo = []

    iva_5 = iva_10 = exenta = total_iva = 0
    grav_5 = grav_10 = 0

    articulo = col_promocion.find_one({'_id': ObjectId(request.POST.getlist('articulo_id')[i])}) # se busca en la BD la promo
    porcentaje = round(float(1 - (float(articulo['porcentaje_promocional']) / 100)), 2) # se calcula el porcentaje de descuento
    precio_costo = articulo['precio_costo_sin_descuento']   # se obtiene el precio que tendria la promo si no se le aplicara ningun descuento promocional
    cantidad_a_vender = int(request.POST.getlist('cantidad')[i])  # cantidad de paquetes de la promocion a ser vendidos

    for producto in articulo['productos']:
        impuesto = 0    # donde se calculara el valor del impuesto que se debe abonar por el articulo en base a la cantidad vendida
        # por cada articulo dentro de la lista de productos de la promo, se obtiene el tipo de impuesto que posee
        aux = col_producto.find_one({'_id': ObjectId(producto['articulo_id'])})
        tipo_impuesto = aux['impuesto'] # se almacena el tipo de impuesto del articulo 5/ 10 / exentas

        if tipo_impuesto == '5':
            impuesto = round(int(int(aux['precio_venta']) * producto['cantidad_promocional'] * cantidad_a_vender) / 21, 2)
        elif tipo_impuesto == '10':
            impuesto = round(int(int(aux['precio_venta']) * producto['cantidad_promocional'] * cantidad_a_vender) / 11, 2)
        elif tipo_impuesto == 'exenta':
            impuesto = 0

        #diccionario auxiliar de ivas y gravadas por cada uno de los articulos descriptos dentro de la promocion
        dict_aux = {
            'iva_5': round(impuesto * porcentaje) if tipo_impuesto == '5' else 0,
            'iva_10': round(impuesto * porcentaje) if tipo_impuesto == '10' else 0,
            'exenta': round((int(aux['precio_venta']) * producto['cantidad_promocional'] * cantidad_a_vender) * porcentaje) if tipo_impuesto == 'exenta' else 0,
            'gravadas_5': round((int(aux['precio_venta']) * producto['cantidad_promocional'] * cantidad_a_vender) * porcentaje) if tipo_impuesto == '5' else 0,
            'gravadas_10': round((int(aux['precio_venta']) * producto['cantidad_promocional'] * cantidad_a_vender) * porcentaje) if tipo_impuesto == '10' else 0,
        }

        lista_productos_en_promo.append(dict_aux)

    for prod_en_prom in lista_productos_en_promo:
        iva_5 += prod_en_prom['iva_5']
        iva_10 += prod_en_prom['iva_10']
        exenta += prod_en_prom['exenta']
        grav_5 += prod_en_prom['gravadas_5']
        grav_10 += prod_en_prom['gravadas_10']

    # diccionario final de ivas y gravadas por la promocion completa
    dict_ivas_gravadas = {
        'iva_5': int(iva_5),
        'iva_10': int(iva_10),
        'exenta': int(exenta),
        'gravadas_5': int(grav_5),
        'gravadas_10': int(grav_10),
    }

    total_iva = iva_5 + iva_10

    # se arma el diccionario para este articulo (promocion) en particular
    dict_promo = {
        'articulo_id': request.POST.getlist('articulo_id')[i],
        'articulo': request.POST.getlist('articulo')[i],
        'cantidad': int(request.POST.getlist('cantidad')[i]),
        'precio_costo': int(precio_costo) * int(request.POST.getlist('cantidad')[i]),
        'subtotal': int(request.POST.getlist('subtotal')[i]),
        'tipo_impuesto': ' - ',
        'total_impuesto': total_iva
    }

    return {'datos_articulo': dict_promo, 'datos_iva_grav': dict_ivas_gravadas}


def calcular_iva_gravadas(request):
    iva_5 = iva_10 = exenta = total_iva = 0
    grav_5 = grav_10 = 0

    lista_articulos_vendidos = []   #lista donde se almacena el diccionario conteniendo todos los datos del articulo que se guarda en la BD
    lista_ivas_gravadas = []    #lista donde se almancenan los diccionarios conteniendo todos los calculos de las gravadas e impuestos por articulos

    for i in range(0, len(request.POST.getlist('articulo_id'))):
        # se averigua si es que existe el articulo en una u otra coleccion.
        # se usa el Limit = 1 para truncar la busqueda cuando se encuentra una coincidencia
        is_producto = col_producto.count_documents({'_id': ObjectId(request.POST.getlist('articulo_id')[i])}, limit= 1)
        is_promocion = col_promocion.count_documents({'_id': ObjectId(request.POST.getlist('articulo_id')[i])}, limit= 1)

        if is_producto:
            # se le pasa el request y el indice de la lista para no recorrerla dos veces - retorna un diccionario de dos
            # claves (los datos para la factura y el calculo del iva y las grav)
            aux = calcular_iva_gravadas_producto(request, i)

            lista_articulos_vendidos.append(aux['datos_articulo'])
            lista_ivas_gravadas.append(aux['datos_iva_grav'])
        elif is_promocion:
            # se le pasa el request y el indice de la lista para no recorrerla dos veces - retorna un diccionario de dos
            # claves (los datos para la factura y el calculo del iva y las grav)
            aux = calcular_iva_gravadas_promocion(request, i)

            lista_articulos_vendidos.append(aux['datos_articulo'])
            lista_ivas_gravadas.append(aux['datos_iva_grav'])

    for ivas_gravadas in lista_ivas_gravadas:
        iva_5 += ivas_gravadas['iva_5']
        iva_10 += ivas_gravadas['iva_10']
        exenta += ivas_gravadas['exenta']
        grav_5 += ivas_gravadas['gravadas_5']
        grav_10 += ivas_gravadas['gravadas_10']

    impuestos = {'impuesto_5': separadaroDeMiles(iva_5), 'impuesto_10': separadaroDeMiles(iva_10),
             'exenta': separadaroDeMiles(exenta), 'total_impuesto': separadaroDeMiles(iva_5 + iva_10)}
    gravadas = {'gravadas_5': separadaroDeMiles(grav_5), 'gravadas_10': separadaroDeMiles(grav_10)}

    return {'impuestos': impuestos, 'gravadas': gravadas, 'articulos': lista_articulos_vendidos}


def get_ganancia_diaria():
    fecha_apertura = ''
    mensaje = ''

    datos_ventas_del_dia = {'fecha':  '', 'mensaje': '', 'suma_costo': 0, 'suma_venta': 0, 'suma_ganancia': 0, 'total_ventas': 0}
    # str(datetime.strftime(ranking['fecha'], '%d/%m/%Y'))

    suma_venta = suma_costo = suma_total = total_ventas = 0

    # 1ro. Se solicita el registro de apertura de la caja
    resultado_query_caja = col_caja.find({'estado': 'abierta'}, sort=[('fecha_apertura', pymongo.DESCENDING)], limit=1)

    # 2do. se verifica que haya alguna caja abierta
    if resultado_query_caja.count() != 0:
        mensaje = 'Si existe caja abierta'
        for item in resultado_query_caja: fecha_apertura = item['fecha_apertura']

        # 3ro. Si existe caja abierta, Se solicitan todas las ventas registradas desde el fecha/hora de la apertura, hasta ahora
        pipeline = [
            {'$match':{
                'ts':{'$gte': fecha_apertura},
                'anulado': 'FALSE'
            }},
            {'$unwind': '$productos'},  # se recorre por el subgrupo
            {'$group': {
                '_id': 'null',
                'suma_costo': {'$sum': '$productos.precio_costo'},
                'suma_venta': {'$sum': '$productos.subtotal'}
            }}
        ]

        resultado_query_ventas = col_ventas.aggregate(pipeline)

        for item in resultado_query_ventas:
            suma_costo = item['suma_costo']
            suma_venta = item['suma_venta']

        #4to. Se hace una solicitud mas para obtener el total de ventas
        pipeline = [
            {'$match':{
                'ts':{'$gte': fecha_apertura},
                'anulado': 'FALSE'
            }},
            {'$count': "total_ventas"}
        ]

        resultado_query_ventas = col_ventas.aggregate(pipeline)

        for item in resultado_query_ventas: total_ventas = item['total_ventas']

        # 5to. se arma el diccionario final
        datos_ventas_del_dia = {
            'fecha':  str(datetime.strftime(fecha_apertura, '%d/%m/%Y - %H:%M:%S')),
            'mensaje': mensaje,
            'suma_costo': str("{0:,}".format(suma_costo)),
            'suma_venta': str("{0:,}".format(suma_venta)),
            'suma_ganancia': str("{0:,}".format(suma_venta - suma_costo)),
            'total_ventas': str("{0:,}".format(total_ventas))
        }

        return datos_ventas_del_dia

    else:
        mensaje = 'No existe caja abierta'

        datos_ventas_del_dia = {
            'fecha':  '',
            'mensaje': mensaje,
            'suma_costo': 0,
            'suma_venta': 0,
            'suma_ganancia': 0,
            'total_ventas': 0
        }

        return datos_ventas_del_dia


def get_ganancia_mensual():
    #datos del mes actual
    dato_ganancia_mes_actual = ''
    dato_ganancia_mes_anterior = ''
    fecha = datetime.now()
    ultimo_dia_mes = int((datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)).day)

    pipeline = [
        {'$match':{
            'ts':{
                '$gte': datetime(fecha.year, fecha.month, 1),
                '$lte': datetime(fecha.year, fecha.month, ultimo_dia_mes)
            },
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$ts'}},
            'suma_costo': {'$sum': '$productos.precio_costo'},
            'suma_venta': {'$sum': '$productos.subtotal'}
        }},
        {'$sort': {'_id': 1}}
    ]

    resultado_mes_actual = col_ventas.aggregate(pipeline)

    suma_costos_act = suma_ventas_act = 0
    for doc in resultado_mes_actual:
        suma_costos_act += doc['suma_costo']
        suma_ventas_act += doc['suma_venta']

    ganancia_mes_actual = suma_ventas_act - suma_costos_act

    #datos del mes anterior********************************************************************************************
    mes_anterior = fecha.month - 1 if fecha.month != 1 else 12
    anho_anterior = fecha.year if mes_anterior != 12 else fecha.year - 1
    ultimo_dia_mes_anterior = int((datetime(anho_anterior, mes_anterior, 1) + relativedelta(months=1, days=-1)).day)

    pipeline = [
        {'$match':{
            'ts':{
                '$gte': datetime(anho_anterior, mes_anterior, 1),
                '$lte': datetime(anho_anterior, mes_anterior, ultimo_dia_mes_anterior)
            },
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$ts'}},
            'suma_costo': {'$sum': '$productos.precio_costo'},
            'suma_venta': {'$sum': '$productos.subtotal'}
        }},
        {'$sort': {'_id': 1}}
    ]

    resultado_mes_anterior = col_ventas.aggregate(pipeline)

    suma_costos_ant = suma_ventas_ant = 0
    for doc in resultado_mes_anterior:
        suma_costos_ant += doc['suma_costo']
        suma_ventas_ant += doc['suma_venta']

    ganancia_mes_anterior = suma_ventas_ant - suma_costos_ant

    diferencia_entre_ganancias = ganancia_mes_actual - ganancia_mes_anterior

    indice = 'p' if diferencia_entre_ganancias >=0 else 'n' # verificar si el porcentaje de ganancias es positivo o negativo

    porcentaje_ganancia_respecto_mes_anterior = float(float(ganancia_mes_actual * 100) / ganancia_mes_anterior) - 100 if ganancia_mes_anterior != 0 else float(ganancia_mes_actual)

    #******************************************************************************************************************

    for mes in MESES_DEL_ANHO:
        if int(mes[0]) == fecha.month:
            dato_ganancia_mes_actual = mes[1]

    for mes in MESES_DEL_ANHO:
        if int(mes[0]) == mes_anterior:
            dato_ganancia_mes_anterior = mes[1]

    return {'ganancia_mes_actual': str("{0:,}".format(int(ganancia_mes_actual))),
            'mes_actual': dato_ganancia_mes_actual,
            'anho_actual': fecha.year,
            'ganancia_mes_anterior': str("{0:,}".format(int(ganancia_mes_anterior))),
            'mes_anterior': dato_ganancia_mes_anterior,
            'anho_anterior': anho_anterior,
            'indice': indice,
            'porcentaje': "{0:.1f}".format(porcentaje_ganancia_respecto_mes_anterior)}


def crear_boton_editar_eliminar(item_id, tipo):
    #se obtiene toda la info a partir del item_id
    dict_aux = col_CMD.find_one({'_id': ObjectId(item_id)})
    descripcion = dict_aux['descripcion']

    #para poder utilizar el tipo, tenemos que poner todos los caracteres en minusculas
    tipo_minusculas = tipo.lower()

    query_productos = col_producto.find({tipo_minusculas: descripcion}).count()

    boton_editar = "<a href=\"#\" data-item_id=\"" + str(item_id) + "\" data-toggle=\"modal\" data-target=\"#modalEditar" + tipo + "\"><i class=\"far fa-edit fa-lg\"></i></a>"
    boton_eliminar = "<a href=\"#\" data-item_id=\"" + str(item_id) + \
                     "\" data-toggle=\"modal\" data-tipo=\"" + tipo + \
                     "\" data-desc=\"" + descripcion + \
                     "\" data-target=\"#modalDeleteCMD\"><i class=\"far fa-trash-alt fa-lg\"></i></a>"

    prohibido = "<i class=\"fas fa-ban fa-lg\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"Este elemento no puede ser eliminado\"></i>"
    dict_aux = {'editar': boton_editar, 'eliminar': prohibido if query_productos > 0 else boton_eliminar}

    return dict_aux
#**********************************************************************************************************************
#**********************************************************************************************************************
#**********************************************************************************************************************
def get_count_digits(numero: int):
    """Return number of digits in a number."""
    if numero == 0:
        return 1

    numero = abs(numero)

    if numero <= 999999999999997:
        return math.floor(math.log10(numero)) + 1

    count = 0
    while numero:
        count += 1
        numero //= 10
    return count


def get_productos_template_stock(request):
    resultado_query = col_producto.find()
    cantidad = resultado_query.count()

    permiso = True if request.user.has_perm('easystockApp.delete_producto') else False

    data = []

    for item in resultado_query:
        if int(item['stock']['actual']) < int(item['stock']['minimo']) and int(item['stock']['actual']) != 0:
            obs = "<i class=\"fas fa-exclamation-circle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La cantidad disponible es MENOR a la cantidad mínima\"></i>" \
                  "<span hidden> 1 menor minima minimo reponer </span>"
        elif int(item['stock']['actual']) == 0:
            obs = "<i class=\"fas fa-exclamation-triangle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"Se necesita reposición del stock\"></i>" \
                  "<span hidden> 0 reposicion vacio sin stock reponer cero </span>"
        else:
            obs = "<i class=\"fas fa-check-circle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La cantidad disponible es MAYOR a la cantidad mínima\"></i>" \
                  "<span hidden> 2 optimo ok</span>"

        boton_agregar = "<a href=\"#\" data-prod_id=\"" + str(item['_id']) + \
                        "\" data-prod_marca=\"" + item["marca"] + \
                        "\" data-prod_desc=\"" + item["descripcion"] + \
                        "\" data-prod_pres=\"" + item["presentacion"] + \
                        "\"data-toggle=\"modal\" data-target=\"#modalAddStock\"><i class=\"fas fa-plus-square fa-lg\"></i></a>"
        boton_editar = "<a href=\"/editar_datos_producto/$?id= " + str(item['_id']) + "\" id=\"editar_datos\"><i class=\"far fa-edit fa-lg\"></i></a>"

        #se verifica que el usuario posea el permiso necesario para realizar la operacion
        if permiso:
            boton_eliminar = "<a href=\"#\" data-prod_id=\"" + str(item['_id']) + "\" data-prod_marca=\"" + item["marca"] + "\" data-toggle=\"modal\" data-target=\"#modalDelete\"><i class=\"far fa-trash-alt fa-lg\"></i></a>"
        else:
            boton_eliminar = '<i class="fas fa-ban fa-lg" data-toggle="tooltip" title="No posee los permisos para realizar esta operación"></i>'

        diccionario = {
            "DT_RowId": str(item['_id']),
            "obs": obs,
            "distribuidor": item['distribuidor'],
            "clasificacion": item["clasificacion"],
            "marca": item["marca"],
            "descripcion": item["descripcion"],
            "presentacion": item["presentacion"],
            "precio_venta": str("Gs. " + "{0:,}".format(int(item['precio_venta']))),        #el Gs. esta fundiendo, verificar con la nueva forma de cargar el datatable
            "cantidad": str("{0:,}".format(int(item['stock']['actual']))),
            "agregar": boton_agregar,
            "editar": boton_editar,
            "eliminar": boton_eliminar
        }

        data.append(diccionario)

    return JsonResponse({'data': data})


def get_productos_modal(request):
    resultado_query = col_producto.find()
    cantidad = resultado_query.count()

    data = []

    for item in resultado_query:
        if int(item['stock']['actual']) < int(item['stock']['minimo']) and int(item['stock']['actual']) != 0:
            obs = "<i class=\"fas fa-exclamation-circle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La cantidad disponible es MENOR a la cantidad mínima\"></i>" \
                  "<span hidden> 1 menor minima minimo reponer </span>"
        elif int(item['stock']['actual']) == 0:
            obs = "<i class=\"fas fa-exclamation-triangle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"Se necesita reposición del stock\"></i>" \
                  "<span hidden> 0 reposicion vacio sin stock reponer cero </span>"
        else:
            obs = "<i class=\"fas fa-check-circle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La cantidad disponible es MAYOR a la cantidad mínima\"></i>" \
                  "<span hidden> 2 optimo ok</span>"

        agregar = "<div class=\"input-group input-group-sm mb-3\">" \
                       "<input class=\"form-control cantidad_venta\" type=\"number\" id=\"cantidad_" + str(item['_id']) + "\" name=\"cantidad_" + str(item['_id']) + "\" placeholder=\"Cantidad\">" \
                       "<div class=\"input-group-prepend\">" \
                            "<button class=\"btn btn-primary\" onclick=\"cargarLista('producto', '" + str(item['_id']) + "')\"><i class=\"fa fa-plus\"></i></button>" \
                        "</div>" \
                    "</div>"

        input_precio_venta = "<input id=\"precio_venta_" + str(item['_id']) + "\" name=\"precio_venta_" + str(item['_id']) + "\" type=\"text\" value=\"" + str("{0:,}".format(int(item['precio_venta']))) + "\" hidden>"
        input_cantidad_disponible = "<input id=\"cantidad_disponible_" + str(item['_id']) + "\" name=\"cantidad_disponible_" + str(item['_id']) + "\" type=\"text\" value=\"" + str(item['stock']['actual']) + "\" hidden>"
        #input_cantidad_minima = "<input id=\"cantidad_minima_" + str(item['_id']) + "\" name=\"cantidad_minima_" + str(item['_id']) + "\" type=\"text\" value=\"" + str(item['stock']['minimo']) + "\" hidden>"

        diccionario = {
            "DT_RowId": str(item['_id']),
            "obs": obs,
            "clasificacion": item["clasificacion"],
            "marca": item["marca"],
            "descripcion": item["descripcion"],
            "presentacion": item["presentacion"],
            "precio_venta": str("Gs. " + "{0:,}".format(int(item['precio_venta']))) + input_precio_venta,        #el Gs. esta fundiendo, verificar con la nueva forma de cargar el datatable
            "cantidad": str("{0:,}".format(int(item['stock']['actual']))) + input_cantidad_disponible ,
            "agregar": agregar
        }

        data.append(diccionario)

    return JsonResponse({'data': data})


def get_promociones_modal_template_registro_venta(request):
    resultado_query = col_promocion.find()
    cantidad = resultado_query.count()

    data = []
    for item in resultado_query:
        cantidad_menor = [] #se reinicia la lista al entrar dentro de cada promoción
        for producto in item['productos']:
            # por cada producto que fue agregado a la promocion, se solicita su stock actual
            resultado_query_producto = col_producto.find_one({'_id':ObjectId(producto['articulo_id'])}, {'stock.actual':1})
            # se calcula la cantidad disponible que se obtendra de la promo, dividiendo el stock actual del producto por la cantidad promocional
            cantidad_disp = int(resultado_query_producto['stock']['actual']) / int(producto['cantidad_promocional'])
            # se actualiza la lista de cantidades menores, la cantidad disponible de la promo depende del menor numero que se obtenga de esta lista
            cantidad_menor.append(cantidad_disp if cantidad_disp > 0 else 0)

        agregar = "<div class=\"input-group input-group-sm mb-3\">" \
                       "<input class=\"form-control cantidad_venta\" type=\"number\" id=\"cantidad_" + str(item['_id']) + "\" name=\"cantidad_" + str(item['_id']) + "\" placeholder=\"Cantidad\">" \
                       "<div class=\"input-group-prepend\">" \
                            "<button class=\"btn btn-primary\" onclick=\"cargarLista('promocion', '" + str(item['_id']) + "')\"><i class=\"fa fa-plus\"></i></button>" \
                        "</div>" \
                    "</div>"

        input_precio_prom = "<input id=\"precio_venta_" + str(item['_id']) + "\" name=\"precio_venta_" + str(item['_id']) + "\" type=\"text\" value=\"" + str("{0:,}".format(int(item['precio_venta_con_descuento']))) + "\" hidden>"
        input_cant_disponible = "<input id=\"cantidad_disponible_" + str(item['_id']) + "\" name=\"cantidad_disponible_" + str(item['_id']) + "\" type=\"text\" value=\"" + str(min(cantidad_menor)) + "\" hidden>"

        diccionario = {
            "DT_RowId": str(item['_id']),
            "obs": '',
            "descripcion": item["descripcion"],
            "info_extra": item["info_extra"],
            "precio_venta_con_descuento": str("Gs. " + "{0:,}".format(int(item['precio_venta_con_descuento']))) + input_precio_prom,        #el Gs. esta fundiendo, verificar con la nueva forma de cargar el datatable
            "cantidad": str(int(min(cantidad_menor)) if len(cantidad_menor) != 0 else 0) + input_cant_disponible,
            "agregar": agregar
        }
        data.append(diccionario)

    return JsonResponse({'data': data})


def get_ventas_template_verificar_ventas(request):

    resultado_query = col_ventas.find()
    cantidad_ventas = resultado_query.count()

    lista = []
    cliente_id = ''
    nro_factura = ''
    obs = ''

    for item in resultado_query:
        # se obtiene el id del cliente para poblar el boton "boton_detalles_cliente"
        resultado_query_cliente = col_clientes.find({'nombre_apellido': item['cliente'], 'ci_ruc': str(item['ruc'])[:-2]}, {'_id': 1})
        count_cliente = resultado_query_cliente.count()

        if count_cliente == 0 :
            existe_cliente = "no"
            cliente_id = ''
        else:
            existe_cliente = "si"
            for item_cliente in resultado_query_cliente:
                cliente_id = str(item_cliente['_id'])

        nro_factura = ''.join([char*(3-get_count_digits(item['nro_factura']['nro_suc']))for char in '0']) + str(int(item['nro_factura']['nro_suc'])) + '-' + \
                      ''.join([char*(3-get_count_digits(item['nro_factura']['nro_caja']))for char in '0']) + str(int(item['nro_factura']['nro_caja'])) + '-' + \
                      ''.join([char*(7-get_count_digits(item['nro_factura']['nro_factura']))for char in '0']) + str(int(item['nro_factura']['nro_factura'])),

        if item['anulado'] == 'TRUE':
            obs = "<i class=\"fas fa-exclamation-triangle\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La Factura ha sido anulada\"></i>"
            boton_anular = "<i class=\"fas fa-lock fa-2x\"></i>"
        else:
            obs = "<i class=\"fas fa-check-circle\"></i>"
            boton_anular = "<a href=\"#\" data-nro_factura=\"" + str(nro_factura[0]) + "\" data-venta_id=\"" + str(item['_id']) + "\" data-toggle=\"modal\" data-target=\"#modalAnularFactura\"><i class=\"fas fa-ban fa-2x\"></i></a>"

        # se crean los botones para cada linea de la tabla
        boton_detalles_cliente = "<a href=\"#\" data-existe_cliente=\"" + existe_cliente + "\" data-cliente_id=\"" + cliente_id + "\" data-toggle=\"modal\" data-target=\"#modalDetallesCliente\"><i class=\"fas fa-address-card fa-2x\"></i></a>"

        boton_factura = "<a href=\"#\" data-nro_factura=\"" + str(nro_factura[0]) + "\" data-venta_id=\"" + str(item['_id']) + "\" data-toggle=\"modal\" data-target=\"#modalDetallesFactura\"><i class=\"fas fa-receipt fa-2x\"></i></a>"

        diccionario = {
            'DT_RowId': str(item['_id']),
            'obs': obs,
            'fecha':  str(datetime.strftime(item['ts'], '%Y/%m/%d')) + ' ' + str(datetime.strftime(item['ts'], '%H:%M:%S')),
            'nro_factura': nro_factura,
            'cliente': item['cliente'],
            'ruc': item['ruc'],
            'detalles_cliente': boton_detalles_cliente,
            'suma_total': str("{0:,}".format(int(item['suma_total']))),
            'factura': boton_factura,
            'anular': boton_anular
        }

        lista.append(diccionario)

    return JsonResponse({'data': lista})


def get_lista_productos(funcion):
    lista = []

    if funcion == 'lista_productos' or funcion == 'eliminar_producto':
        resultado_query = col_producto.find()
        cantidad = resultado_query.count()

        for item in resultado_query:
            diccionario = {
                "id": item['_id'],
                "clasificacion": item["clasificacion"],
                "distribuidor": item['distribuidor'],
                "marca": item["marca"],
                "descripcion": item["descripcion"],
                "presentacion": item["presentacion"],
                "etiqueta": item["etiqueta_opcional"],
                "precio_venta": str("{0:,}".format(int(item['precio_venta']))),
                "cantidad": str("{0:,}".format(int(item['stock']['actual']))),
                "menor_al_minimo": True if (int(item['stock']['actual']) < int(item['stock']['minimo']) and int(item['stock']['actual']) != 0) else False,
                "stock_cero": True if (int(item['stock']['actual']) == 0) else False
            }

            lista.append(diccionario)

        return {'lista': lista, 'cantidad': cantidad}

    elif funcion == 'ventas':
        resultado_query = col_producto.find()
        cantidad = resultado_query.count()

        for item in resultado_query:
            diccionario = {
                "id": str(item['_id']),
                "clasificacion": item["clasificacion"],
                "marca": item["marca"],
                "descripcion": item["descripcion"],
                "presentacion": item["presentacion"],
                "precio_venta": str("{0:,}".format(int(item['precio_venta']))),
                "cantidad": int(item['stock']['actual']),
                "cantidad_minima": int(item['stock']['minimo'])
            }

            lista.append(diccionario)

        return {'lista': lista, 'cantidad': cantidad}

    elif funcion == 'asignar_promo':
        resultado_query = col_producto.find()
        cantidad = resultado_query.count()

        for item in resultado_query:
            diccionario = {
                "id": item['_id'],
                "clasificacion": item["clasificacion"],
                "distribuidor": item['distribuidor'],
                "marca": item["marca"],
                "descripcion": item["descripcion"],
                "presentacion": item["presentacion"],
                "promocion": item["promocion"]
            }

            lista.append(diccionario)

        return {'lista': lista, 'cantidad': cantidad}

    elif funcion == 'verificar_ventas':
        resultado_query = col_ventas.find()
        cantidad = resultado_query.count()

        for item in resultado_query:
            query = col_producto.find_one({'_id': ObjectId(item['prod_id'])}, {'_id': 0,'marca': 1, 'descripcion':1})

            marca = str(query['marca'])
            descripcion = str(query['descripcion'])

            diccionario = {
                'id': item['_id'],
                'producto': marca,
                'descripcion': descripcion,
                'cantidad': item['cantidad'],
                'precio_venta': str("{0:,}".format(int(item['prod_precio_venta']))),
                'fecha_hora': str(datetime.strftime(item['timestamp'], '%d/%m/%Y')) + ' ' + str(datetime.strftime(item['timestamp'], '%H:%M:%S')),
            }

            lista.append(diccionario)

        return {'lista': lista, 'cantidad': cantidad}


def get_lista_promociones():
    lista_return = []

    resultado_query_promociones = col_promocion.find()  # se solicitan todas las promociones
    cantidad_promociones = resultado_query_promociones.count()  # se cuenta la cantidad de promociones existentes

    for promocion in resultado_query_promociones:
        cantidad_menor = [] #se reinicia la lista al entrar dentro de cada promoción

        for producto in promocion['productos']:
            # por cada producto que fue agregado a la promocion, se solicita su stock actual
            resultado_query_producto = col_producto.find_one({'_id':ObjectId(producto['articulo_id'])}, {'stock.actual':1})
            # se calcula la cantidad disponible que se obtendra de la promo, dividiendo el stock actual del producto por la cantidad promocional
            cantidad_disp = int(resultado_query_producto['stock']['actual']) / int(producto['cantidad_promocional'])
            # se actualiza la lista de cantidades menores, la cantidad disponible de la promo depende del menor numero que se obtenga de esta lista
            cantidad_menor.append(cantidad_disp if cantidad_disp > 0 else 0)
        # se arma el boton para abrir el modal y mostrar los productos que son parte de la promo
        boton_detalles_promo = "<a href=\"#\" data-promo_id=\"" + str(promocion['_id']) + "\" data-toggle=\"modal\" data-target=\"#modalDetallesPromo\"><i class=\"fas fa-clipboard-list fa-2x\"></i></a>"
        # se arma el diccionario final para devolver
        diccionario = {
            'promo_id' : promocion['_id'],
            'descripcion': promocion['descripcion'],
            'precio_promocional': str("{0:,}".format(int(promocion['precio_venta_con_descuento']))),
            'porcentaje_promocional': str(promocion['porcentaje_promocional']),
            'cantidad_disponible': int(min(cantidad_menor)) if len(cantidad_menor) != 0 else 0,
            'productos': boton_detalles_promo,
            'info_extra': promocion['info_extra'] if len(promocion['info_extra']) != 0 else "------"
        }

        lista_return.append(diccionario)

    return {'lista':lista_return, 'cantidad': cantidad_promociones}

@csrf_exempt
def get_lista_clientes(request):
    lista = []

    resultado_query = col_clientes.find()
    cantidad = int(resultado_query.count())

    for item in resultado_query:
        diccionario = {
            'id': item['_id'],
            'nombre_apellido': item['nombre_apellido'],
            'ci_ruc': item['ci_ruc'],
            'dig_verif': item['dig_verif'],
            'tel_nro': item['tel_nro'],
            'direccion': item['direccion'],
            'email': item['email'],
            'ci_ruc_dv': str(item['ci_ruc']) + '-' + str(item['dig_verif'])
        }

        boton = "<button type=\"button\" class=\"btn btn-primary btn-sm\" onclick=\"cargarCliente('" + diccionario['nombre_apellido'] +"', '" + diccionario['ci_ruc_dv'] + "')\"><i class=\"fa fa-plus\"></i></button>"
        # se prepara una nueva lista en caso de que se llame desde el modal para agregar clientes en el template de registro de venta
        aux = [diccionario['nombre_apellido'], diccionario['ci_ruc_dv'], diccionario['tel_nro'], diccionario['email'], boton]
        # se pasa la lista simple al llamado desde datatables o se pasa el diccionario normal si se llama desde otro lado
        lista.append(aux if request.is_ajax() else diccionario)

    if request.is_ajax():
        return JsonResponse({'data': lista})
    else:
        return {'lista': lista, 'cantidad': cantidad}

@csrf_exempt
def get_detalles_cliente_modal_template_verificar_ventas(request):

    diccionario = {}

    if request.method == 'POST':
        if request.POST.get('existe_cliente') == 'si':
            resultado_query = col_clientes.find({'_id': ObjectId(request.POST.get('cliente_id'))})

            for item in resultado_query:
                diccionario = {
                    'nombre_apellido': item['nombre_apellido'],
                    'ci_ruc': str(item['ci_ruc']) + '-' + str(item['dig_verif']),
                    'tel_nro': item['tel_nro'],
                    'direccion': item['direccion'],
                    'email': item['email']
                }

            mensaje = ''

            return JsonResponse({'mensaje': mensaje, 'detalles_cliente': diccionario})
        else:
            diccionario = {}
            mensaje = "La factura se generó sin nombre, o el cliente ya no pertenece a la nómina."

            return JsonResponse({'mensaje': mensaje, 'detalles_cliente': diccionario})

    return

@csrf_exempt
def get_detalles_factura_modal_template_verificar_ventas(request):
    metodo_pago = ''

    resultado_query = col_ventas.find_one({'_id': ObjectId(request.POST.get('venta_id'))})

    if resultado_query['metodo_pago'] == 'efectivo':
        metodo_pago = 'Efectivo'
    elif resultado_query['metodo_pago'] == 'tc':
        metodo_pago = 'Tarjeta de Crédito'
    elif resultado_query['metodo_pago'] == 'td':
        metodo_pago = 'Tarjeta de Débito'

    dict_final = {
        'nro_factura': ''.join([char*(3-get_count_digits(resultado_query['nro_factura']['nro_suc']))for char in '0']) + str(int(resultado_query['nro_factura']['nro_suc'])) + '-' +
                       ''.join([char*(3-get_count_digits(resultado_query['nro_factura']['nro_caja']))for char in '0']) + str(int(resultado_query['nro_factura']['nro_caja'])) + '-' +
                       ''.join([char*(7-get_count_digits(resultado_query['nro_factura']['nro_factura']))for char in '0']) + str(int(resultado_query['nro_factura']['nro_factura'])),
        'cliente': resultado_query['cliente'],
        'ruc': resultado_query['ruc'],
        'productos': resultado_query['productos'],
        'suma_total': str("{0:,}".format(int(resultado_query['suma_total']))),
        'suma_pagada': str("{0:,}".format(int(resultado_query['suma_pagada']))),
        'suma_vuelto': str("{0:,}".format(int(resultado_query['suma_pagada']) - int(resultado_query['suma_total']))),
        'metodo_pago': metodo_pago,
        'exenta': str("{0:,}".format(int(resultado_query['exenta']))),
        'gravadas': {'gravadas_5': resultado_query['gravadas']['gravadas_5'],
                     'gravadas_10': resultado_query['gravadas']['gravadas_10']},
        'impuestos': {'impuesto_5': resultado_query['impuestos']['impuesto_5'],
                      'impuesto_10': resultado_query['impuestos']['impuesto_10'],
                      'total_impuesto': resultado_query['impuestos']['total_impuesto']},
        'ts': str(datetime.strftime(resultado_query['ts'], '%d/%m/%Y')) + ' - ' + str(datetime.strftime(resultado_query['ts'], '%H:%M:%S'))
    }

    return JsonResponse({'data': dict_final})

@csrf_exempt
def get_lista_articulos_vendidos_modal_template_verificar_ventas(request):
    fecha_apertura = ''
    lista_articulos = []
    pipeline = []

    if request.POST.get('funcion') == 'desde_apertura_caja':
        # 1ro. Se solicita el registro de la ultima apertura de la caja
        resultado_query_caja = col_caja.find({'estado': 'abierta'}, sort=[('fecha_apertura', pymongo.DESCENDING)], limit=1)

        # 2do. se verifica que haya alguna caja abierta
        if resultado_query_caja.count() != 0:
            for item in resultado_query_caja: fecha_apertura = item['fecha_apertura']

            # 3ro. Si existe caja abierta, Se solicitan todas las ventas registradas desde el fecha/hora de la apertura, hasta ahora
            pipeline = [
                {'$match':{
                    'ts':{'$gte': fecha_apertura},
                    'anulado': 'FALSE'
                }},
                { "$unwind": "$productos" },
                { "$project": {
                    "_id": 0,
                    "fecha": {'$dateToString': {'format': '%Y/%m/%d %H:%M', 'date': '$ts'}},
                    "articulo": "$productos.articulo",
                    "cantidad": "$productos.cantidad",
                    "subtotal": "$productos.subtotal",
                }}
            ]
        # si no hay caja abierta, se mandan todos los datos a la tabla
        else:
            pipeline = [
                { "$unwind": "$productos" },
                { "$project": {
                    "_id": 0,
                    "fecha": {'$dateToString': {'format': '%Y/%m/%d %H:%M', 'date': '$ts'}},
                    "articulo": "$productos.articulo",
                    "cantidad": "$productos.cantidad",
                    "subtotal": "$productos.subtotal",
                }}
            ]

    if request.POST.get('funcion') == 'todos_los_datos' or request.POST.get('funcion') is None:

        pipeline = [
            { "$unwind": "$productos" },
            { "$project": {
                "_id": 0,
                "fecha": {'$dateToString': {'format': '%Y/%m/%d %H:%M', 'date': '$ts'}},
                "articulo": "$productos.articulo",
                "cantidad": "$productos.cantidad",
                "subtotal": "$productos.subtotal",
            }}
        ]

    resultado_query = col_ventas.aggregate(pipeline)

    for item in resultado_query:
        diccionario = {
            'fecha': item['fecha'],
            'articulo': item['articulo'],
            'cantidad': item['cantidad'],
            'subtotal': str("{0:,}".format(item['subtotal']))
        }

        lista_articulos.append(diccionario)

    return JsonResponse({'data': lista_articulos})

@csrf_exempt
def get_detalles_promocion_modal_template_listar_productos(request):

    lista_productos = []

    if request.method == 'POST':
        promo_id = request.POST.get('promo_id')

        resultado_query = col_promocion.find_one({'_id': ObjectId(promo_id)}, {'productos': 1})

        for producto in resultado_query['productos']:
            lista_productos.append(producto)

    print(lista_productos)

    return JsonResponse({'data': lista_productos})

@csrf_exempt
def actualizar_tabla_productos_modal_template_registro_venta(request):
    data = ''

    if request.method == 'POST':
        if request.POST.get('operacion') == 'agregar_prod':
            prod_id = request.POST.get('prod_id')
            cantidad_venta = request.POST.get('cantidad_venta')

            producto = col_producto.find_one({'_id': ObjectId(prod_id)})

            try:
                col_producto.update_one({'_id': ObjectId(prod_id)},{'$inc': {'stock.actual': - (int(cantidad_venta))}})
            except pymongo.errors.WriteError as err:
                print('Ha ocurrido un error! Error #{0}'.format(err))

            data = {
                "marca": producto["marca"],
                "descripcion": producto["descripcion"],
                "presentacion": producto["presentacion"]
            }

        elif request.POST.get('operacion') == 'quitar_prod':
            prod_id = request.POST.get('articulo_id')
            cantidad_reponer = request.POST.get('cantidad_reponer')

            #producto = col_producto.find_one({'_id': ObjectId(prod_id)})

            try:
                col_producto.update_one({'_id': ObjectId(prod_id)}, {'$inc': {'stock.actual': int(cantidad_reponer)}})
            except pymongo.errors.WriteError as err:
                print('Ha ocurrido un error! Error #{0}'.format(err))

    return JsonResponse({'data': data})

@csrf_exempt
def actualizar_tabla_promociones_modal_template_registro_venta(request):
    data = ''
    cantidad_menor = []

    if request.method == 'POST':
        if request.POST.get('operacion') == 'agregar_promo':
            promo_id = request.POST.get('promo_id')
            cantidad_venta = request.POST.get('cantidad_venta')

            promocion = col_promocion.find_one({'_id': ObjectId(promo_id)})

            for producto in promocion['productos']:
                # 1ro. se resta del stock de cada producto la cantidad promocional
                try:
                    col_producto.update_one({'_id': ObjectId(producto['articulo_id'])}, {'$inc': {'stock.actual': - (int(producto['cantidad_promocional']) * int(cantidad_venta))}})
                except pymongo.errors.WriteError as err:
                    print('Ha ocurrido un error! Error #{0}'.format(err))

                # 2do. se vuelve a solicitar el stock actual de cada producto
                resultado_query_producto = col_producto.find_one({'_id': ObjectId(producto['articulo_id'])}, {'stock.actual': 1})
                # 3ro. se calcula la cantidad disponible que se obtendra de la promo, dividiendo el stock actual del producto por la cantidad promocional
                cantidad_disp = int(resultado_query_producto['stock']['actual']) / int(producto['cantidad_promocional'])
                # 4to. se actualiza la lista de cantidades menores, la cantidad disponible de la promo depende del menor numero que se obtenga de esta lista
                cantidad_menor.append(cantidad_disp if cantidad_disp > 0 else 0)
                # 5to. ROLLBACK
                #col_producto.update_one({'_id': ObjectId(producto['id_producto'])}, {'$inc': {'stock.actual': (int(producto['cantidad_promocional']) * int(cantidad_venta))}})

            data = {
                "_id": promo_id,
                "descripcion": promocion['descripcion'],
                "precio_venta_con_descuento": promocion['precio_venta_con_descuento'],
                "cantidad_disponible": int(min(cantidad_menor)) if len(cantidad_menor) != 0 else 0
            }

        elif request.POST.get('operacion') == 'quitar_promo':
            promo_id = request.POST.get('articulo_id')
            cantidad_reponer = request.POST.get('cantidad_reponer')

            promocion = col_promocion.find_one({'_id': ObjectId(promo_id)})

            for producto in promocion['productos']:
                try:
                    col_producto.update_one({'_id': ObjectId(producto['articulo_id'])}, {'$inc': {'stock.actual': (int(producto['cantidad_promocional']) * int(cantidad_reponer))}})
                except pymongo.errors.WriteError as err:
                    print('Ha ocurrido un error! Error #{0}'.format(err))

    return JsonResponse({'data': data})

@csrf_exempt
def rollback_bd(request):
    lista_articulos = []    #lista de todos los productos que estan dentro del form
    dict_articulo = {}      #diccionario auxiliar para guardar cada articulo

    form_data_dict = {}
    form_data_list = json.loads(request.POST.get('datos_form')) #se vacian todos los campos del form (vacios o no) dentro de una lista

    #por cada campo dentro del form, se va armando un campo en el diccionario final
    for field in form_data_list:
        # si el nombre del campo esta dentro de estas opciones, se guarda dentro del diccionario auxiliar para los articulos
        if field['name'] in ('articulo_id', 'articulo', 'cantidad', 'articulo_precio_unit', 'subtotal'):
            dict_articulo[field['name']] = field['value']
            # si el nombre es 'subtotal' significa que se llego al 'final' de cada articulo
            if field['name'] == 'subtotal':
                lista_articulos.append(dict_articulo)   #se arma la lista de todos los articulo
                dict_articulo = {}  #se vuelve a reiniciar el diccionario auxiliar por cada articulo
        else:
            form_data_dict[field['name']] = field['value']

    for articulo in lista_articulos:
        # se averigua si es que existe el articulo en una u otra coleccion.
        # se usa el Limit = 1 para truncar la busqueda cuando se encuentra una coincidencia
        is_producto = col_producto.count_documents({'_id': ObjectId(articulo['articulo_id'])}, limit= 1)
        is_promocion = col_promocion.count_documents({'_id': ObjectId(articulo['articulo_id'])}, limit= 1)

        if is_producto: # si existe al menos una coincidencia, se revierte la cantidad descontada
            try:
                col_producto.update_one({'_id': ObjectId(articulo['articulo_id'])}, {'$inc': {'stock.actual': (int(articulo['cantidad']))}})
            except pymongo.errors.WriteError as err:
                print('Ha ocurrido un error! Error #{0}'.format(err))
        elif is_promocion:  # si existe al menos una coincidencia, se solicita los detalles de la promocion
            promocion = col_promocion.find_one({'_id': ObjectId(articulo['articulo_id'])})

            for producto in promocion['productos']: #por cada producto dentro de la promocion, se revierte la cantidad descontada
                try:
                    col_producto.update_one({'_id': ObjectId(producto['articulo_id'])}, {'$inc': {'stock.actual': (int(producto['cantidad_promocional']) * int(articulo['cantidad']))}})
                except pymongo.errors.WriteError as err:
                    print('Ha ocurrido un error! Error #{0}'.format(err))

    form_data_dict['productos'] = lista_articulos   #se anexa la lista de productos a la lista de diccionarios final

    return JsonResponse({'data': ''})

# Funcion que deberia devolver una lista de diccionarios (producto + total de ocurrencia) de los 6 articulos mas vendidos
def ranking_articulos_top_6():
    hoy = datetime.now()
    semana_pasada = hoy - timedelta(days = 7)
    ranking = []

    pipeline = [
        {'$match':{
            'ts':{'$gte': semana_pasada},
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': '$productos.articulo',
            'suma_cantidad': {'$sum': {'$toInt': '$productos.cantidad'}}
        }},
        {'$sort': {'suma_cantidad': -1}},
        {'$limit': 6}
    ]

    resultado = col_ventas.aggregate(pipeline)

    for res in resultado: ranking.append(res)

    return {'fecha': semana_pasada,
            'articulos': ranking}

@csrf_exempt
def get_ganancias_diarias(request):
    costo_venta = []
    ganancia = []

    pipeline = [
        {'$match':{
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$ts'}},
            'suma_costo': {'$sum': '$productos.precio_costo'},
            'suma_venta': {'$sum': '$productos.subtotal'}
        }},
        {'$sort': {'_id': 1}}
    ]

    resultado = col_ventas.aggregate(pipeline)

    for item in resultado:
        fecha = datetime.strptime(str(item['_id']) + ' 00:00:01', '%Y-%m-%d %H:%M:%S')
        punto_costo_venta = [int(str(int(time.mktime(fecha.timetuple()))) + '000'), item['suma_costo'], item['suma_venta']]
        resta = item['suma_venta'] - item['suma_costo']
        punto_ganancia = [int(str(int(time.mktime(fecha.timetuple()))) + '000'), resta]
        costo_venta.append(punto_costo_venta)
        ganancia.append(punto_ganancia)

    return JsonResponse({'costo_venta': costo_venta, 'ganancia': ganancia})

@csrf_exempt
def get_ranking_articulos(request):
    dias_del_mes = []
    lista_articulos_top = []
    data = []
    articulos = []

    mes = int(request.POST.get('mes'))
    anho = int(request.POST.get('anho'))
    ultimo_dia_mes = int((datetime(anho, mes, 1) + relativedelta(months=1, days=-1)).day)

    pipeline = [
        {'$match':{
            'ts':{'$gte': datetime(anho, mes, 1), '$lte': datetime(anho, mes, ultimo_dia_mes)},
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': '$productos.articulo',
            'suma_cantidad': {'$sum': {'$toInt': '$productos.cantidad'}}
        }},
        {'$sort': {'suma_cantidad': -1}},
        {'$limit': 3}
    ]

    resultado_query = col_ventas.aggregate(pipeline)

    for res in resultado_query: articulos.append(res)

    for i in range(1, ultimo_dia_mes + 1): dias_del_mes.append(i)   #se arma la lista para las categorias
    for i in range(0, len(articulos)): lista_articulos_top.append(articulos[i]['_id'])  #se arma la lista para los nombres de las series

    for articulo in lista_articulos_top:
        series_name = articulo
        series_data = []

        for dia in dias_del_mes:
            suma = 0    # se reinicia la suma por cada dia del mes
            query = col_ventas.find({'productos.articulo': articulo,
                                     'ts':{'$gte': datetime(anho, mes, dia, 0, 0, 0), '$lt': datetime(anho, mes, dia, 23, 59, 59)},
                                     'anulado': 'FALSE'})
            existe_registro = query.count()

            if existe_registro == 0:
                series_data.append(0)
            else:
                for doc in query:
                    for producto in doc['productos']:
                        if producto['articulo'] == articulo:
                            suma += int(producto['cantidad'])

                series_data.append(suma)

        diccionario = {'name': series_name, 'data': series_data}

        data.append(diccionario)

    return JsonResponse({'categorias': dias_del_mes,
                         'series': data,
                         'ranking': len(articulos)})

@csrf_exempt
def get_top_100(request):
    ranking = []
    data = []

    mes = int(request.POST.get('mes'))
    anho = int(request.POST.get('anho'))
    ultimo_dia_mes = int((datetime(anho, mes, 1) + relativedelta(months=1, days=-1)).day)

    pipeline = [
        {'$match':{
            'ts':{'$gte': datetime(anho, mes, 1), '$lte': datetime(anho, mes, ultimo_dia_mes)},
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': '$productos.articulo',
            'suma_cantidad': {'$sum': {'$toInt': '$productos.cantidad'}}
        }},
        {'$sort': {'suma_cantidad': -1}},
        {'$limit': 100}
    ]

    resultado = col_ventas.aggregate(pipeline)

    for res in resultado: ranking.append(res)

    # el primer item de los articulos siempre sera el mayor de todos
    mayor_cantidad = ranking[0]['suma_cantidad']
    for articulo in ranking:
        porcentaje = "{0:.2f}".format(float((int(articulo['suma_cantidad']) * 100)/mayor_cantidad))
        lista = list(articulo.values())
        barra = "<div class=\"progress\" style=\"height: 20px;\">" \
                    "<div class=\"progress-bar\" role=\"progressbar\" style=\"width: " + porcentaje + "%;\" aria-valuenow=\"" + porcentaje + "\" aria-valuemin=\"0\" aria-valuemax=\"100\"></div>" \
                "</div>"
        lista.append(barra)

        data.append(lista)

    return JsonResponse({'data': data})

@csrf_exempt
def get_ventas_dias_x_semana(request):
    mes = int(request.POST.get('mes'))
    anho = int(request.POST.get('anho'))
    ultimo_dia_mes = int((datetime(anho, mes, 1) + relativedelta(months=1, days=-1)).day)

    articulos = []
    lista_final = []
    dias_del_mes = []
    lista_articulos_top = []

    xAxis = []
    yAxis = []

    pipeline = [
        {'$match':{
            'ts':{'$gte': datetime(anho, mes, 1), '$lte': datetime(anho, mes, ultimo_dia_mes)},
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': '$productos.articulo',
            'suma_cantidad': {'$sum': {'$toInt': '$productos.cantidad'}}
        }},
        {'$sort': {'suma_cantidad': -1}},
        {'$limit': 10}
    ]

    resultado_query = col_ventas.aggregate(pipeline)

    for res in resultado_query: articulos.append(res)

    for i in range(1, ultimo_dia_mes + 1): dias_del_mes.append(i)   #se arma la lista para las categorias
    for i in range(0, len(articulos)): lista_articulos_top.append(articulos[i]['_id'])  #se arma la lista para los nombres de las series

    indice_articulo = 0
    for articulo in lista_articulos_top:
        xAxis.append(articulo)
        indices_dias_semana = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}    # se reinicia la suma por cada dia del mes

        for dia in dias_del_mes:

            query = col_ventas.find({'productos.articulo': articulo,
                                     'ts':{'$gte': datetime(anho, mes, dia, 0, 0, 0), '$lt': datetime(anho, mes, dia, 23, 59, 59)},
                                     'anulado': 'FALSE'})
            existe_registro = query.count()

            dia_de_la_semana = str(datetime(anho, mes, dia).weekday())

            if existe_registro == 0:
                indices_dias_semana[dia_de_la_semana] += 0
            else:
                for doc in query:
                    for producto in doc['productos']:
                        if producto['articulo'] == articulo:
                            indices_dias_semana[dia_de_la_semana] += int(producto['cantidad'])

        #se procede a armar la lista final
        for i in range(0, len(indices_dias_semana)):
            lista_final.append([indice_articulo, i, indices_dias_semana[str(i)]])

        indice_articulo += 1    # se aumenta en uno el indice del articulo

    for i in range(0, len(DIAS_DE_LA_SEMANA)):  yAxis.append(DIAS_DE_LA_SEMANA[i][1])

    print(lista_final)
    return JsonResponse({'series_data': lista_final,
                         'xAxis_categories': xAxis,
                         'yAxis_categories': yAxis})

@csrf_exempt
def get_distribucion_stock(request):
    suma_total = 0
    series = []
    drilldown_series = []

    # se arman los queries para obtener las clasificaciones
    query_clasificacion = [
        {'$group':{
            '_id': '$clasificacion',
            'cantidad': {'$sum': '$stock.actual'}
        }}
    ]

    resultado1 = col_producto.aggregate(query_clasificacion)

    query_suma_total = [
        {'$group':{
            '_id': 'null',
            'total_suma': {'$sum': '$stock.actual'}
        }}
    ]

    resultado2 = col_producto.aggregate(query_suma_total)

    for res in resultado2: suma_total = res['total_suma']

    for item in resultado1:
        diccionario = {
            'name': item['_id'],
            'y': float((item['cantidad'] / suma_total) * 100),
            'cantidad': int(item['cantidad']),
            'suma_total': int(suma_total),
            'drilldown': item['_id']
        }
        series.append(diccionario)

    # se arma el query para obtener las marcas en base a las clasificaciones
    query_marca_x_clasificacion = [
        {'$group':{
            '_id': {
                'clasificacion': '$clasificacion',
                'marca': '$marca'},
            'cantidad': {'$sum': '$stock.actual'},
        }},
        {'$group':{
            '_id': {'clasificacion': '$_id.clasificacion'},
            'data': {'$addToSet': {
                'marca':'$_id.marca',
                'cantidad': '$cantidad'
            }}
        }}
    ]

    resultado3 = col_producto.aggregate(query_marca_x_clasificacion)

    for categoria in resultado3:
        lista_marcas = []
        for marca in categoria['data']:
            lista_marcas.append({'name': marca['marca'],
                                 'y':float((marca['cantidad'] / suma_total) * 100),
                                 'cantidad': int(marca['cantidad']),
                                 'suma_total': int(suma_total)})

        diccionario_marcas = {
            'name': str(categoria['_id']['clasificacion']),
            'id': str(categoria['_id']['clasificacion']),
            'data': lista_marcas}

        drilldown_series.append(diccionario_marcas)

    return JsonResponse({'series': series, 'drilldown_series': drilldown_series})

@csrf_exempt
def consultar_disponibilidad_datos(request):
    mes = int(request.POST.get('mes'))
    anho = int(request.POST.get('anho'))
    ultimo_dia_mes = int((datetime(anho, mes, 1) + relativedelta(months=1, days=-1)).day)

    query_ventas = col_ventas.find({'ts':{'$gte': datetime(anho, mes, 1), '$lte': datetime(anho, mes, ultimo_dia_mes)}})

    cantidad = query_ventas.count()

    return JsonResponse({'cantidad': cantidad})

@csrf_exempt
def get_CMD(request):
    lista = []

    if request.POST.get('tipo') == 'Marca': # se consulta si el tipo es igual a Marca
        # si es igual a marca, se utiliza un filtro mas, que es el de la clasificacion,
        resultado_query = col_CMD.find({'tipo': str(request.POST.get('tipo')), 'clasificacion': str(request.POST.get('clasificacion'))})
    else:   # para los demas se solicita sin restricciones
        resultado_query = col_CMD.find({'tipo': str(request.POST.get('tipo'))})

    cantidad = int(resultado_query.count())

    for res in resultado_query: lista.append(res['descripcion']);
    lista.sort()

    return JsonResponse({'lista': lista, 'cantidad': cantidad})

@csrf_exempt
def get_promocion_condicion_eliminar_producto(request):
    lista_promos = []

    resultado_query = col_promocion.find({'productos.articulo_id': request.POST.get('prod_id')})
    cantidad = resultado_query.count()

    for promo in resultado_query: lista_promos.append(promo['descripcion'])

    return JsonResponse({'lista': lista_promos, 'cantidad': int(cantidad)})

@csrf_exempt
def get_meses_x_anho(request):
    anho = int(request.POST.get('anho'))
    lista_meses = []

    pipeline = [
        {'$match':
            {'ts':{
                '$gte': datetime(anho, 1, 1, 0, 0, 0),
                '$lte': datetime(anho, 12, 31, 23, 59, 59)}}
        },
        {'$group':{
            '_id': {'$dateFromParts':{
                'year': {'$year':'$ts'},
                'month': {'$month':'$ts'}
            }},
        }},
    ]

    resultado_query = col_ventas.aggregate(pipeline)

    for fecha in resultado_query: lista_meses.append(MESES_DEL_ANHO[int(fecha['_id'].month) - 1])

    print(lista_meses[0][0], lista_meses[0][1])

    return JsonResponse({'meses': lista_meses, 'cantidad': len(lista_meses)})

@csrf_exempt
def get_clasificaciones(request):
    lista_clasificaciones = []

    query_clasificaciones = col_CMD.find({'tipo': 'Clasificacion'})

    for clasificacion in query_clasificaciones:
        botones = crear_boton_editar_eliminar(clasificacion['_id'], 'Clasificacion')
        dict_clasificaciones = {
            'DT_RowId': str(clasificacion['_id']),
            'descripcion': clasificacion['descripcion'],
            'editar': botones['editar'],
            'eliminar': botones['eliminar']
        }

        lista_clasificaciones.append(dict_clasificaciones)

    return JsonResponse({'data': lista_clasificaciones})

@csrf_exempt
def get_marcas(request):
    lista_marcas = []

    query_marcas = col_CMD.find({'tipo': 'Marca'})

    for marca in query_marcas:
        botones = crear_boton_editar_eliminar(marca['_id'], 'Marca')
        dict_marcas = {
            'DT_RowId': str(marca['_id']),
            'descripcion': marca['descripcion'],
            'clasificacion': marca['clasificacion'],
            'editar': botones['editar'],
            'eliminar': botones['eliminar']
        }

        lista_marcas.append(dict_marcas)

    return JsonResponse({'data': lista_marcas})

@csrf_exempt
def get_distribuidores(request):
    lista_distribuidores = []

    query_distribuidores = col_CMD.find({'tipo': 'Distribuidor'})

    for distribuidor in query_distribuidores:
        botones = crear_boton_editar_eliminar(distribuidor['_id'], 'Distribuidor')
        dict_clasificaciones = {
            'DT_RowId': str(distribuidor['_id']),
            'descripcion': distribuidor['descripcion'],
            'editar': botones['editar'],
            'eliminar': botones['eliminar']
        }

        lista_distribuidores.append(dict_clasificaciones)

    return JsonResponse({'data': lista_distribuidores})

@csrf_exempt
def get_info_cajas(request):
    lista_cajas = []

    query_cajas = col_caja.find()

    for caja in query_cajas:
        boton_editar = "<a href=\"#\" data-item_id=\"" + str(caja['_id']) + "\" data-toggle=\"modal\" data-target=\"#modalAbrirCaja\"><i class=\"far fa-edit fa-lg\"></a>"
        dict_caja = {
            'DT_RowId': str(caja['_id']),
            'fecha_apertura': str(caja['fecha_apertura'].strftime('%d/%m/%y %H:%M:%S')),
            'fecha_cierre': str(caja['fecha_cierre'].strftime('%d/%m/%y %H:%M:%S')) if caja['fecha_cierre'] != 'Sin registro' else 'Sin registro' ,
            'monto_apertura': str("{0:,}".format(int(caja['monto_apertura']))),
            'total_ventas': str("{0:,}".format(int(caja['monto_cierre']) - int(caja['monto_apertura']))) if int(caja['monto_cierre']) != 0 else 0,
            'monto_cierre': str("{0:,}".format(int(caja['monto_cierre']))),
            'efectivo': str("{0:,}".format(int(caja['efectivo']))),
            'tc': str("{0:,}".format(int(caja['tc']))),
            'td': str("{0:,}".format(int(caja['td']))),
            'costos': str("{0:,}".format(int(caja['costos']))),
            'ganancias': str("{0:,}".format(int(caja['ganancias']))),
            'estado': str(caja['estado']).capitalize(), # el estado demuestra que aun no se ha cerrado la caja
            'editar': boton_editar if caja['estado'] == 'abierta' else '<i class=\"fas fa-window-close fa-lg\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"La caja ya fue cerrada por lo que ya no puede ser modificada\"></i>'
        }
        lista_cajas.append(dict_caja)

    return JsonResponse({'data': lista_cajas})

@csrf_exempt
def get_monto_apertura_caja(request):
    item_id = ObjectId(request.POST.get('item_id'))
    monto_apertura = 0

    try:
        query_caja = col_caja.find_one({'_id': item_id})
        monto_apertura = query_caja['monto_apertura']
        print(monto_apertura)
    except pymongo.errors.OperationFailure as err:
        print(err)

    return JsonResponse({'monto_apertura': monto_apertura})

@csrf_exempt
def agregar_al_stock(request):
    prod_id = ObjectId(request.POST.get('prod_id'))
    cantidad = request.POST.get('cantidad')

    datos_prod = col_producto.find_one({'_id': prod_id})
    responsable = request.user.username

    try:
        col_producto.update({'_id': prod_id}, {'$inc': {'stock.actual': int(cantidad)}})

        mensaje_alert = descripcion_evento = 'Se ha actualizado con éxito el stock de ' + datos_prod['marca'] + ' - ' + datos_prod['descripcion'] + ' - ' + datos_prod['presentacion'] + ' en ' +  cantidad + ' unidades'

        evento = 'agregar_al_stock'
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

        # alert exito
        propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

    except pymongo.errors.WriteError as err:
        mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
        evento = 'agregar_al_stock'
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

        # alert warning
        propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

    return JsonResponse({'propiedad_alerts': propiedad_alerts})


def get_logs(request):
    lista_logs = []

    query_logs = col_eventos.find()

    for log in query_logs:
        dict_log = {
            'DT_RowId': str(log['_id']),
            'fecha_hora': str(log['fecha_hora'].strftime('%d/%m/%y %H:%M:%S')),
            'evento': str(log['evento']),
            'descripcion': str(log['descripcion']),
            'responsable': str(log['responsable'])
        }
        lista_logs.append(dict_log)

    return JsonResponse({'data': lista_logs})


def get_valor_stock():
    valor_total_costo = valor_total_venta = 0

    pipeline = [
        { "$unwind": "$stock" },    #se recorre el subdocumento stock
        { "$project": { #se especifica que campos documento quiero que vaya a la siguiente etapa (group)
            "valor_costo": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_costo"}, 0 ] },
            ]},
            "valor_venta": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_venta"}, 0 ] },
            ]}
        }},
        { "$group": {
            "_id": "",
            "subtotal_costo": { "$sum": "$valor_costo" },
            "subtotal_venta": { "$sum": "$valor_venta" },
        }},
    ]

    resultado = col_producto.aggregate(pipeline)

    for item in resultado:
        valor_total_costo += item['subtotal_costo']
        valor_total_venta += item['subtotal_venta']

    return {'valor_costo': valor_total_costo,
            'valor_venta': valor_total_venta}

@csrf_exempt
def get_valor_stock_detallado(request):
    lista_valores_stock = []
    detalle = str(request.POST.get('detalle')).lower().replace('ó', 'o')

    pipeline = [
        { "$unwind": "$stock" },    #se recorre el subdocumento stock
        { "$project": { #se especifica que campos documento quiero que vaya a la siguiente etapa (group)
            detalle: 1, #true para el detalle
            "valor_costo": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_costo"}, 0 ] },
            ]},
            "valor_venta": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_venta"}, 0 ] },
            ]}
        }},
        { "$group": {
            "_id": "$" + detalle,
            "subtotal_costo": { "$sum": "$valor_costo" },
            "subtotal_venta": { "$sum": "$valor_venta" },
        }},
    ]

    resultado = col_producto.aggregate(pipeline)

    for item in resultado:
        lista_valores_stock.append({detalle: item['_id'],
                                    'valor_de_costo': str("{0:,}".format(int(item['subtotal_costo']))),
                                    'valor_de_venta': str("{0:,}".format(int(item['subtotal_venta'])))})

    return JsonResponse({'data': lista_valores_stock})


def guardar_valor_stock():
    valor_total_costo = valor_total_venta = 0
    fecha = datetime.today()

    pipeline = [
        { "$unwind": "$stock" },    #se recorre el subdocumento stock
        { "$project": { #se especifica que campos documento quiero que vaya a la siguiente etapa (group)
            "valor_costo": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_costo"}, 0 ] },
            ]},
            "valor_venta": { "$multiply": [   #se realiza la multiplicacion y este es el segundo y ultimo campo
                { "$ifNull": [ "$stock.actual", 0 ] },
                { "$ifNull": [ {'$toInt': "$precio_venta"}, 0 ] },
            ]}
        }},
        { "$group": {
            "_id": "",
            "subtotal_costo": { "$sum": "$valor_costo" },
            "subtotal_venta": { "$sum": "$valor_venta" },
        }},
    ]

    resultado = col_producto.aggregate(pipeline)

    for item in resultado:
        valor_total_costo += item['subtotal_costo']
        valor_total_venta += item['subtotal_venta']

    #se prepara el valor del stock para el dia
    valor_stock = {'fecha': fecha, 'valor_costo': valor_total_costo, 'valor_venta': valor_total_venta}

    try:
        col_stock.replace_one({'fecha': {'$gte': datetime(fecha.year, fecha.month, fecha.day, 0, 0, 0), '$lt': datetime(fecha.year, fecha.month, fecha.day, 23, 59, 59)}}, valor_stock, True)
    except pymongo.errors.WriteError as err:
        print(err)

    return

@csrf_exempt
def get_valores_historicos_stock(request):
    lista_valores_historicos_stock = []

    resultado = col_stock.find()

    if request.POST.get('solicitante') == 'grafico':
        for item in resultado:
            fecha = datetime.strptime(str(item['fecha']), '%Y-%m-%d %H:%M:%S.%f') - timedelta(hours = 4)
            lista_valores_historicos_stock.append([int(str(int(time.mktime(fecha.timetuple()))) + '000'), item['valor_costo']])
        return JsonResponse({'lista_valores_historicos_stock': lista_valores_historicos_stock})

    else:
        for item in resultado:
            lista_valores_historicos_stock.append({'fecha': item['fecha'].strftime('%d/%m/%Y'),
                                        'valor_de_costo': str("{0:,}".format(int(item['valor_costo']))),
                                        'valor_de_venta': str("{0:,}".format(int(item['valor_venta'])))})
        return JsonResponse({'data': lista_valores_historicos_stock})


#**********************************************************************************************************************
#**********************************************************************************************************************
#**********************************************************************************************************************

def index(request):
    dict_aux = {}

    grupo = True if Group.objects.get(name='Administradores') in request.user.groups.all() else False

    query_eventos_compra = col_eventos.find({'$or': [{'evento': 'nuevo_producto'}, {'evento': 'agregar_al_stock'}]}, sort=[('fecha_hora', pymongo.DESCENDING)], limit=5)
    query_eventos_venta = col_eventos.find({'evento': 'venta'}, sort=[('fecha_hora', pymongo.DESCENDING)], limit=5)

    #query_caja = col_caja.find_one({'fecha_apertura': {'$gte': datetime(fecha.year, fecha.month, fecha.day, 0, 0, 1), '$lte': datetime(fecha.year, fecha.month, fecha.day, 23, 59, 59)}})
    query_caja = col_caja.find(sort=[('fecha_apertura', pymongo.DESCENDING)], limit=1)

    for item in query_caja: dict_aux = item

    #se verifica que el diccionario hay sido cargado, para poder bloquear o no el boton de apertura
    if bool(query_caja) and len(dict_aux) != 0:
        estado = dict_aux['estado']
        if estado == 'abierta':
            propiedad_boton_apertura = 'disabled'
            propiedad_boton_cierre = ''
            monto_apertura = dict_aux['monto_apertura']
            monto_cierre = dict_aux['monto_cierre']
        else:
            propiedad_boton_apertura = ''
            propiedad_boton_cierre = 'disabled'
            monto_apertura = dict_aux['monto_apertura']
            monto_cierre = dict_aux['monto_cierre']
    else:
        estado = ''
        propiedad_boton_apertura = ''
        propiedad_boton_cierre = 'disabled'
        monto_apertura = 0
        monto_cierre = 0

    lista_aux_compra = []
    lista_aux_venta = []

    for item in query_eventos_compra:
        diccionario = {
            'descripcion': item['descripcion'],
            'fecha_hora': str(datetime.strftime(item['fecha_hora'], '%d/%m/%Y %H:%M:%S')),
        }

        lista_aux_compra.append(diccionario)

    for item in query_eventos_venta:
        diccionario = {
            'descripcion': item['descripcion'],
            'fecha_hora': str(datetime.strftime(item['fecha_hora'], '%d/%m/%Y %H:%M:%S')),
        }

        lista_aux_venta.append(diccionario)

    formCajaApertura = CajaAperturaForm()
    formCajaCierre = CajaCierreForm()

    ranking = ranking_articulos_top_6()

    ganancia_diaria = get_ganancia_diaria()
    ganancia_mensual = get_ganancia_mensual()

    valores_template = {'cantidad_eventos_compra': query_eventos_compra.count(),
                        'cantidad_eventos_venta': query_eventos_venta.count(),
                        'eventos_compra': lista_aux_compra,
                        'eventos_venta': lista_aux_venta,
                        'formCajaApertura': formCajaApertura,
                        'formsCajaCierre': formCajaCierre,
                        'propiedad_boton_apertura': propiedad_boton_apertura,
                        'propiedad_boton_cierre': propiedad_boton_cierre,
                        'monto_apertura': str("{0:,}".format(int(monto_apertura))),
                        'monto_cierre': str("{0:,}".format(int(monto_cierre))),
                        'estado_caja': estado,
                        'fecha_semana_pasada': str(datetime.strftime(ranking['fecha'], '%d/%m/%Y')),
                        'primer_puesto': str(ranking['articulos'][0]['_id']) + ' (' + str(ranking['articulos'][0]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 1 else 'Sin registros',
                        'segundo_puesto': str(ranking['articulos'][1]['_id']) + ' (' + str(ranking['articulos'][1]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 2 else 'Sin registros',
                        'tercer_puesto': str(ranking['articulos'][2]['_id']) + ' (' + str(ranking['articulos'][2]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 3 else 'Sin registros',
                        'cuarto_puesto': str(ranking['articulos'][3]['_id']) + ' (' + str(ranking['articulos'][3]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 4 else 'Sin registros',
                        'quinto_puesto': str(ranking['articulos'][4]['_id']) + ' (' + str(ranking['articulos'][4]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 5 else 'Sin registros',
                        'sexto_puesto': str(ranking['articulos'][5]['_id']) + ' (' + str(ranking['articulos'][5]['suma_cantidad']) + ')' if len(ranking['articulos']) >= 6 else 'Sin registros',
                        'datos_ganancia_mensual': ganancia_mensual,
                        'datos_ventas_del_dia': ganancia_diaria,
                        'refreshTimer': '300'}

    return render(request,
                  'index.html',
                  context=valores_template)


def nuevo_producto(request):
    dict_request = {}
    dict_stock = {}
    ultimos_productos = []
    cant_ultimos_productos = 0
    responsable = request.user.username

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        print(request.POST)
        if form.is_valid():
            for keys, values in request.POST.items():
                if type(values) is str: dict_request.update({keys: str(values).capitalize()})
                else: dict_request.update({keys: int(values)})

                if keys == 'stock-minimo': dict_stock.update({'minimo': int(values)})
                elif keys == 'stock-optimo': dict_stock.update({'optimo': int(values)})
                elif keys == 'stock-actual': dict_stock.update({'actual': int(values)})

            dict_request.update({'stock': dict_stock})
            dict_request.update({'estado': 'activo'})

            # se extirpan los campos del diccionario que NO se necesitan guardar en la BD
            dict_request.pop('csrfmiddlewaretoken')
            dict_request.pop('submit')
            dict_request.pop('stock-minimo')
            dict_request.pop('stock-optimo')
            dict_request.pop('stock-actual')

            try:
                col_producto.insert_one(dict_request)

                mensaje_alert = 'El producto ' + dict_request['marca'] + ' - ' + dict_request['descripcion'] + ' ha sido agregado con éxito'

                evento = 'nuevo_producto'
                descripcion_evento = 'Se agregó al stock una cantidad de ' + str(dict_request['stock']['actual']) + ' de ' + str(dict_request['marca']) + ' - ' + dict_request['descripcion']
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                form_nuevo = ProductoForm() #si la carga fue exitosa, se envia un formulario nuevo

                guardar_valor_stock()   #si la carga fue exitosa, se actualiza el valor del stock

                # alert exito
                propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

            except pymongo.errors.DuplicateKeyError:
                mensaje_alert = descripcion_evento = 'Ha ocurrido un error. El Código de barras ingresado ya lo posee otro producto dentro del stock. Verifiquelo nuevamente.'
                evento = 'error'
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                form_nuevo = form #si se produjo un error en la carga (codigo de barras duplicado), se reenvia el formulario junto los datos que rebotaron

                # alert warning
                propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

            query_ultimos_productos = col_producto.find().sort("_id", -1).limit(10)
            cant_ultimos_productos = query_ultimos_productos.count()

            for producto  in query_ultimos_productos:
                aux_dict = {
                    'marca': producto['marca'],
                    'descripcion': producto['descripcion'],
                    'presentacion': producto['presentacion']
                }
                ultimos_productos.append(aux_dict)

            # se prepare un diccionario con los valores necesarios para el template
            formClasificacion = ClasificacionForm()
            formDistribuidor = DistribuidorForm()
            formMarca = MarcaForm()
            valores_template = {'form': form_nuevo,
                                'formClasi': formClasificacion,
                                'formDistri': formDistribuidor,
                                'formMarca': formMarca,
                                'ultimos_productos': ultimos_productos,
                                'cant_ultimos_productos': cant_ultimos_productos,
                                'propiedad_alerts': propiedad_alerts}

            return render(request,
                          'productos_promociones/nuevo_producto.html',
                          valores_template)

        else:
            propiedad_alerts = {'visibilidad': '', 'mensaje': form.errors, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}
            # se prepare un diccionario con los valores necesarios para el template
            form = ProductoForm()
            formClasificacion = ClasificacionForm()
            formDistribuidor = DistribuidorForm()
            formMarca = MarcaForm()
            valores_template = {'form': form,
                                'formClasi': formClasificacion,
                                'formDistri': formDistribuidor,
                                'formMarca': formMarca,
                                'ultimos_productos': ultimos_productos,
                                'cant_ultimos_productos': cant_ultimos_productos,
                                'propiedad_alerts': propiedad_alerts}

            return render(request,
                          'productos_promociones/nuevo_producto.html',
                          context=valores_template)
    else:
        query_ultimos_productos = col_producto.find().sort("_id", -1).limit(10) # se solicita los ultimos 10 productos agregados
        cant_ultimos_productos = query_ultimos_productos.count()

        for producto  in query_ultimos_productos:
            aux_dict = {
                'marca': producto['marca'],
                'descripcion': producto['descripcion'],
                'presentacion': producto['presentacion']
            }
            ultimos_productos.append(aux_dict)

        form = ProductoForm()
        formClasificacion = ClasificacionForm()
        formDistribuidor = DistribuidorForm()
        formMarca = MarcaForm()
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'form': form,
                        'formClasi': formClasificacion,
                        'formDistri': formDistribuidor,
                        'formMarca': formMarca,
                        'ultimos_productos': ultimos_productos,
                        'cant_ultimos_productos': cant_ultimos_productos,
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'productos_promociones/nuevo_producto.html',
                      context=valores_template)


def crear_promocion(request):

    #articulo_id, articulo, cantidad, articulo_precio_unit, subtotal - cada uno es una lista ordenada
    dict_request = {}
    dict_producto = {}
    dict_promocion = {}

    lista_productos = []
    porcentaje_promocional = precio_costo = 0

    responsable = request.user.username

    if request.method == 'POST':
        # se arma un diccionario con los datos enviados del formulario
        for keys, values in request.POST.items():
            if 'cantidad_' in keys: # se consulta si la clave contiene el substring 'cantidad_'
                dict_request.update({str(keys)[9:]:values}) # se saca el substring 'cantidad_' de cualquier clave
            else:   # caso contrario, se guarda normalmente
                dict_request.update({keys:values})

        for i in range(0, len(request.POST.getlist('articulo_id'))):    #se usa como referencia una de las listas
            subtotal_costo = col_producto.find_one({'_id': ObjectId(request.POST.getlist('articulo_id')[i])}, {'precio_costo': 1})

            dict_producto = {
                'articulo_id': request.POST.getlist('articulo_id')[i],
                'articulo': request.POST.getlist('articulo')[i],
                'cantidad_promocional': int(request.POST.getlist('cantidad')[i]),
                'articulo_precio_unit': int(request.POST.getlist('articulo_precio_unit')[i]),
                'subtotal_costo': int(int(subtotal_costo['precio_costo']) * int(request.POST.getlist('cantidad')[i])),
                'subtotal': int(request.POST.getlist('subtotal')[i])
            }

            precio_costo += int(int(subtotal_costo['precio_costo']) * int(request.POST.getlist('cantidad')[i]))
            lista_productos.append(dict_producto)

        #si la opcion de porcentaje promocional esta marcada
        if dict_request['inlineRadioOptions'] == 'porcentaje_promocional':
            porcentaje_promocional = dict_request['porcentaje_promocional']
        else:   # si no es porcentaje promocional, es precio promocional, entonces se calcula el porcentaje de descuento
            porcentaje_promocional = round(float(1 - float(float(dict_request['precio_venta_con_descuento']) / float(dict_request['precio_venta_sin_descuento']))) * 100, 2)

        # se prepara el diccionario final para guardar en la bd
        dict_promocion = {
            'descripcion': dict_request['descripcion'],
            'info_extra': dict_request['info_extra'],
            'productos': lista_productos,
            'porcentaje_promocional': float(porcentaje_promocional),
            'precio_costo_sin_descuento': int(precio_costo),
            'precio_venta_sin_descuento': int(dict_request['precio_venta_sin_descuento']),
            'precio_venta_con_descuento': int(dict_request['precio_venta_con_descuento'])
        }

        try:
            col_promocion.insert_one(dict_promocion)    #se almacena el diccionario final en la BD
            mensaje = 'La promoción \'' + dict_promocion['descripcion'] + '\' ha sido creada con éxito!'
            # se crea el registro dentro de los  logs
            evento = 'crear_promocion'
            descripcion_evento = 'Se ha creado la promoción \'' + dict_promocion['descripcion'] + '\' a Gs. ' + str(dict_promocion['precio_venta_con_descuento'])
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)
            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}
        except pymongo.errors.WriteError as err:
            mensaje = descripcion_evento= 'Ha ocurrido un error! Error #{0}'.format(err)
            evento = 'crear_promocion'
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        valores_template = {'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'productos_promociones/crear_promo.html',
                      context=valores_template)
    else:
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

        valores_template = {'propiedad_alerts': propiedad_alerts}

        return render(request,
                          'productos_promociones/crear_promo.html',
                          context=valores_template)


def listar_productos(request):
    lista_productos = get_lista_productos('lista_productos')

    guardar_valor_stock()

    if lista_productos['cantidad'] == 0:
        mensaje = 'No se cuenta con ningún producto en stock'
    else:
        mensaje = ''

    propiedad_alerts = {'visibilidad': 'hidden'}

    valores_stock = get_valor_stock()

    valores_template = {'mensaje': mensaje,
                        'cantidad_productos': lista_productos['cantidad'],
                        'productos': lista_productos['lista'],
                        'fecha_hoy': date.today().strftime("%d/%m/%Y"),
                        'valor_costo': str("{0:,}".format(int(valores_stock['valor_costo']))),
                        'valor_venta': str("{0:,}".format(int(valores_stock['valor_venta']))),
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                  'productos_promociones/listar_productos.html',
                  context=valores_template)


def listar_promociones(request):
    lista_promociones = get_lista_promociones()

    if lista_promociones['cantidad'] == 0:
        mensaje = 'No se cuenta con ninguna promoción'
    else:
        mensaje = ''

    propiedad_alerts = {'visibilidad': 'hidden'}

    valores_template = {'mensaje': mensaje,
                        'cantidad_promociones': lista_promociones['cantidad'],
                        'promociones': lista_promociones['lista'],
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                  'productos_promociones/listar_promociones.html',
                  context=valores_template)


def editar_datos_producto(request):
    dict_request = {}
    dict_stock = {}
    dict_editar_producto = {}
    responsable = request.user.username

    guardar_valor_stock()

    valores_stock = get_valor_stock()

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        formClasificacion = ''
        formDistribuidor = ''
        formMarca = ''
        if form.has_changed():
            for keys, values in request.POST.items():
                dict_request.update({keys:values})

                if keys == 'stock-minimo':
                    dict_stock.update({'minimo': int(values)})
                elif keys == 'stock-optimo':
                    dict_stock.update({'optimo': int(values)})
                elif keys == 'stock-actual':
                    dict_stock.update({'actual': int(values)})

            dict_request.update({'stock': dict_stock})

            # se extirpan los campos del diccionario que NO se necesitan guardar en la BD
            dict_request.pop('csrfmiddlewaretoken')
            dict_request.pop('submit')
            dict_request.pop('stock-minimo')
            dict_request.pop('stock-optimo')
            dict_request.pop('stock-actual')

            try:
                col_producto.update_one({'_id': ObjectId(request.GET['id'][1:])}, {'$set': dict_request})

                mensaje_alert = 'Los datos del producto han sido modificados con éxito'

                evento = 'editar_datos_producto'
                descripcion_evento = 'Se modificaron los datos del producto ' + str(dict_request['marca'] + ' - ' + str(dict_request['descripcion']))
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert exito
                propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

            except pymongo.errors.WriteError as err:
                mensaje_alert = descripcion_evento ='Ha ocurrido un error! Error #{0}'.format(err)
                evento = 'editar_datos_producto'
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert warning
                propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

            producto_id = str(request.GET['id'])

            resultado_query = col_producto.find({'_id': producto_id[1:]})

            for item in resultado_query:
                dict_request.update(item)

            form = ProductoForm({
                'clasificacion': dict_request['clasificacion'],
                'marca': dict_request['marca'],
                'descripcion': dict_request['descripcion'],
                'presentacion': dict_request['presentacion'],
                'etiqueta_opcional': dict_request['etiqueta_opcional'],
                'precio_costo': dict_request['precio_costo'],
                'precio_venta': dict_request['precio_venta'],
                'impuesto': dict_request['impuesto'],
                'stock-minimo': dict_request['stock']['minimo'],
                'stock-optimo': dict_request['stock']['optimo'],
                'stock-actual': dict_request['stock']['actual']})

            valores_template = {'form': form,
                                'valor_costo': str("{0:,}".format(int(valores_stock['valor_costo']))),
                                'valor_venta': str("{0:,}".format(int(valores_stock['valor_venta']))),
                                'propiedad_alerts': propiedad_alerts}

            return render(request,
                          'productos_promociones/listar_productos.html',
                          context=valores_template)
        else:
            print(form.errors)

    else:
        producto_id = str(request.GET['id'])

        resultado_query = col_producto.find({'_id': ObjectId(producto_id[1:])})

        for item in resultado_query:    dict_request.update(item)

        resultado_distribuidores = col_CMD.find({'tipo': 'Distribuidor'})
        resultado_clasificaciones = col_CMD.find({'tipo': 'Clasificacion'})
        resultado_marcas = col_CMD.find({'tipo': 'Marca', 'clasificacion': dict_request['clasificacion']})

        lista_distribuidores = []
        lista_clasificaciones = []
        lista_marcas = []

        for distribuidor in resultado_distribuidores:   lista_distribuidores.append(distribuidor['descripcion'])
        for clasificacion in resultado_clasificaciones: lista_clasificaciones.append(clasificacion['descripcion'])
        for marca in resultado_marcas:  lista_marcas.append(marca['descripcion'])

        dict_editar_producto = {
            'distribuidor': lista_distribuidores,
            'distribuidor_actual': dict_request['distribuidor'],
            'clasificacion': lista_clasificaciones,
            'clasificacion_actual': dict_request['clasificacion'],
            'marca': lista_marcas,
            'marca_actual': dict_request['marca'],
            'descripcion': dict_request['descripcion'],
            'presentacion': dict_request['presentacion'],
            'etiqueta_opcional': dict_request['etiqueta_opcional'],
            'precio_costo': dict_request['precio_costo'],
            'precio_venta': dict_request['precio_venta'],
            'impuesto': dict_request['impuesto'],
            'stock_minimo': int(dict_request['stock']['minimo']),
            'stock_optimo': int(dict_request['stock']['optimo']),
            'stock_actual': int(dict_request['stock']['actual'])
        }

        form = ''
        formClasificacion = ClasificacionForm()
        formDistribuidor = DistribuidorForm()
        formMarca = MarcaForm()

    propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'form': form,
                        'formClasi': formClasificacion,
                        'formDistri': formDistribuidor,
                        'formMarca': formMarca,
                        'dict_editar_producto': dict_editar_producto,
                        'propiedad_alerts': propiedad_alerts}
    return render(request,
                      'productos_promociones/editar_datos_producto.html',
                      context=valores_template)


@csrf_exempt
def eliminar_producto(request):
    dict_aux = {}
    responsable = request.user.username

    if request.method == 'POST':
        producto_id = ObjectId(request.POST.get('prod_id'))

        query_col_producto = col_producto.find({'_id': producto_id},{"marca": 1, "descripcion": 1})
        #query_col_promocion = col_promocion.find({'productos.articulo_id': request.POST.get('prod_id')}, {'descripcion': 1})

        # se carga el diccionario auxiliar (para almacenar el Evento)
        for item in query_col_producto:     dict_aux.update({'marca': item['marca'], 'descripcion': item['descripcion']})

        try:
            # se procede a eliminar el documento de la BD
            col_producto.delete_one({'_id': producto_id})
            col_promocion.delete_many({'productos.articulo_id': request.POST.get('prod_id')})
            # se prepara el mensaje para el alert
            mensaje = 'El producto ' + str(dict_aux['marca']) + ' - ' + str(dict_aux['descripcion']) + ' ha sido eliminado del inventario.'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'eliminar_producto'
            reg_evento(evento, mensaje, datetime.now(), responsable)
            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

            guardar_valor_stock()   #si la eliminacion fue exitosa, se actualiza el valor del stock

        except pymongo.errors.WriteError as err:
            mensaje = 'Ha ocurrido un error! Error #{0}'.format(err)
            evento = 'eliminar_producto'
            reg_evento(evento, mensaje, datetime.now(), responsable)
            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        valores_stock = get_valor_stock()

        valores_template = {'mensaje': mensaje,
                            'cantidad_productos': get_lista_productos('eliminar_producto')['cantidad'],
                            'cantidad_promociones': get_lista_promociones()['cantidad'],
                            'productos': get_lista_productos('eliminar_producto')['lista'],
                            'promociones': get_lista_promociones()['lista'],
                            'valor_costo': str("{0:,}".format(int(valores_stock['valor_costo']))),
                            'valor_venta': str("{0:,}".format(int(valores_stock['valor_venta']))),
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'productos_promociones/listar_productos.html',
                      context=valores_template)


@csrf_exempt
def eliminar_promocion(request):
    dict_aux = {}
    responsable = request.user.username

    if request.method == 'POST':
        promo_id = request.POST.get('promo_id')

        resultado_query = col_promocion.find({'_id': ObjectId(promo_id)})

        # se carga el diccionario auxiliar (para almacenar el Evento)
        for item in resultado_query:
            dict_aux.update({'descripcion': item['descripcion']})

        try:
            # se procede a eliminar el documento de la BD
            col_promocion.delete_one({'_id': ObjectId(promo_id)})
            # se prepara el mensaje para el alert
            mensaje = 'La promoción ' + str(dict_aux['descripcion']) + ' ha sido eliminada.'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'eliminar_promocion'
            reg_evento(evento, mensaje, datetime.now(), responsable)
            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.WriteError as err:
            mensaje = 'Ha ocurrido un error! Error #{0}'.format(err)
            evento = 'eliminar_promocion'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        valores_template = {'mensaje': mensaje,
                            'cantidad_productos': get_lista_productos('eliminar_producto')['cantidad'],
                            'cantidad_promociones': get_lista_promociones()['cantidad'],
                            'productos': get_lista_productos('eliminar_producto')['lista'],
                            'promociones': get_lista_promociones()['lista'],
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'productos_promociones/listar_productos.html',
                      context=valores_template)


def registrar_venta(request):
    dict_resultado = {}
    fecha = datetime.now()
    responsable = request.user.username
    resultado_query_caja = col_caja.find(sort=[('fecha_apertura', pymongo.DESCENDING)], limit=1)

    guardar_valor_stock()   #luego de regustrar una venta, se procede a guardar el valor del stock

    for item in resultado_query_caja: dict_resultado = item

    if bool(dict_resultado):
        estado_caja = dict_resultado['estado']
    else:
        estado_caja = 'False'

    if request.method == 'POST':
        cliente = request.POST.get('nombreCliente')
        ruc = request.POST.get('rucCliente')
        suma_total = request.POST.get('suma_total')
        suma_pagada = request.POST.get('factura_monto')
        metodo_pago = request.POST.get('metodo_pago_hidden')
        nro_boleta = request.POST.get('nro_boleta_hidden')

        impuestos_gravadas = calcular_iva_gravadas(request)

        #Diccionario final a ser guardado en la BD
        dict_final = {
            'nro_factura': generar_nro_factura(),
            'cliente': cliente,
            'ruc': ruc,
            'productos': impuestos_gravadas['articulos'],
            'suma_total': suma_total,
            'suma_pagada': suma_pagada,
            'metodo_pago': metodo_pago,
            'nro_boleta': nro_boleta,
            'exenta': impuestos_gravadas['impuestos']['exenta'],
            'gravadas': impuestos_gravadas['gravadas'],
            'impuestos': impuestos_gravadas['impuestos'],
            'ts': datetime.now(),
            'anulado': 'FALSE'
        }

        try:
            col_ventas.insert_one(dict_final)

            mensaje_alert = 'La venta se ha procesado con éxito!'

            evento = 'venta'
            descripcion_evento = 'Se ha registrado una venta por Gs. ' + str("{0:,}".format(int(suma_total)))
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.WriteError as err:
            mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
            evento = 'venta'
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        mensaje = 'La venta ha sido exitosa!'
        valores_template = {'mensaje': mensaje,
                            'datos_empresa': DATOS_EMPRESA,
                            'nro_factura': ''.join([char*(3-get_count_digits(dict_final['nro_factura']['nro_suc']))for char in '0']) + str(int(dict_final['nro_factura']['nro_suc'])) + '-' +
                                           ''.join([char*(3-get_count_digits(dict_final['nro_factura']['nro_caja']))for char in '0']) + str(int(dict_final['nro_factura']['nro_caja'])) + '-' +
                                           ''.join([char*(7-get_count_digits(dict_final['nro_factura']['nro_factura']))for char in '0']) + str(int(dict_final['nro_factura']['nro_factura'])),
                            'cliente': dict_final['cliente'],
                            'ruc': dict_final['ruc'],
                            'productos': impuestos_gravadas['articulos'],
                            'suma_total': separadaroDeMiles(suma_total),
                            'suma_pagada': separadaroDeMiles(suma_pagada),
                            'exenta': separadaroDeMiles(impuestos_gravadas['impuestos']['exenta']),
                            'gravadas': impuestos_gravadas['gravadas'],
                            'impuestos': impuestos_gravadas['impuestos'],
                            'suma_vuelto': separadaroDeMiles(int(suma_pagada) - int(suma_total)),
                            'fecha_hora': str(datetime.strftime(dict_final['ts'], '%d/%m/%Y')) + ' - ' + str(datetime.strftime(dict_final['ts'], '%H:%M:%S')),
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'ventas/venta_exitosa.html',
                      context=valores_template)
    else:
        lista_productos = get_lista_productos('ventas')
        lista_clientes = get_lista_clientes(request)

        form = ClienteForm()
        formCajaApertura = CajaAperturaForm()

        if lista_productos['cantidad'] == 0:
            mensaje = 'No se cuenta con ningún producto en stock'
        else:
            mensaje = ''

        propiedad_alerts = {'visibilidad': 'hidden'}

    valores_template = {'mensaje': mensaje,
                        'cantidad': lista_productos['cantidad'],
                        'productos': lista_productos['lista'],
                        'clientes': lista_clientes['lista'],
                        'form': form,
                        'formCajaApertura': formCajaApertura,
                        'estado_caja': estado_caja,
                        'cant_clientes': lista_clientes['cantidad'],
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                  'ventas/registrar_venta.html',
                  context=valores_template)


def verificar_ventas(request):
    generar_nro_factura()
    mensaje = 'hola'

    propiedad_alerts = {'visibilidad': 'hidden'}

    ganancia_diaria = get_ganancia_diaria()

    valores_template = {'mensaje': mensaje,
                        'datos_ventas_del_dia': ganancia_diaria,
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                  'ventas/verificar_ventas.html',
                  context=valores_template)


@csrf_exempt
def anular_factura(request):

    responsable = request.user.username

    if request.method == 'POST':
        venta_id = ObjectId(request.POST.get('venta_id'))
        nro_factura = request.POST.get('nro_factura')

        try:
            # se procede a cambiar el valor del campo anulado
            col_ventas.update_one({'_id': venta_id}, {'$set': {'anulado': 'TRUE'}})

            mensaje = 'La factura con Nro. ' + nro_factura + ' ha sido anulada'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'anular_factura'
            reg_evento(evento, mensaje, datetime.now(), responsable)
            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.WriteError as err:
            mensaje = 'Ha ocurrido un error! Error #{0}'.format(err)
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'anular_factura'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        valores_template = {'mensaje': mensaje,
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'ventas/verificar_ventas.html',
                      context=valores_template)

    return


@csrf_exempt
def nuevo_cliente(request):
    dict_request = {}
    responsable = request.user.username

    propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            for keys, values in request.POST.items():
                if keys != 'csrfmiddlewaretoken' or keys != 'submit':
                    dict_request.update({keys:str(values).title()} if keys == 'nombre_apellido' else {keys:values})

            try:
                col_clientes.insert_one(dict_request)

                mensaje_alert = 'El cliente ha sido registrado con éxito'

                evento = 'agregar_cliente'
                descripcion_evento = 'Se registro a ' + str(dict_request['nombre_apellido']) + ' como cliente'
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert exito
                propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

            except pymongo.errors.WriteError as err:
                mensaje_alert = descripcion_evento = 'El número de C.I. o R.U.C. ya existe!' if pymongo.errors.DuplicateKeyError else 'Ha ocurrido un error! Error #{0}'.format(err)
                evento = 'agregar_cliente'
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert warning
                propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

            if request.is_ajax():   #cuando se llama desde el template de registro de venta
                return JsonResponse({'propiedad_alerts': propiedad_alerts})

            form = ClienteForm()
            valores_template = {'form': form,
                                'propiedad_alerts': propiedad_alerts}

            return render(request,
                      'clientes/nuevo_cliente.html',
                      context=valores_template)
        else:
            propiedad_alerts = {'visibilidad': 'hidden'}

        valores_template = {'form': form,
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'clientes/nuevo_cliente.html',
                      context=valores_template)

    else:
        form = ClienteForm()
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'form': form,
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'clientes/nuevo_cliente.html',
                      context=valores_template)


def listar_clientes(request):
    lista_clientes = get_lista_clientes(request)

    if lista_clientes['cantidad'] == 0:
        mensaje = 'No se cuenta con ningún producto en stock'
    elif lista_clientes['cantidad'] == 0:
        mensaje = 'No se cuenta con ninguna promoción'
    else:
        mensaje = ''

    propiedad_alerts = {'visibilidad': 'hidden'}

    valores_template = {'mensaje': mensaje,
                        'cantidad_clientes': lista_clientes['cantidad'],
                        'clientes': lista_clientes['lista'],
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                  'clientes/listar_clientes.html',
                  context=valores_template)


def editar_datos_cliente(request):
    dict_request = {}
    responsable = request.user.username

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.has_changed():
            for keys, values in request.POST.items():
                if keys == 'nombre_apellido':
                    dict_request.update({keys:str(values).title()})
                else:
                    dict_request.update({keys:values})

            # se extirpan los campos del diccionario que NO se necesitan guardar en la BD
            dict_request.pop('csrfmiddlewaretoken')
            dict_request.pop('submit')

            try:
                col_clientes.update_one({'_id': ObjectId(request.GET['id'][1:])}, {'$set': dict_request})

                mensaje_alert = 'Los datos del cliente han sido modificados con éxito'

                evento = 'editar_datos_cliente'
                descripcion_evento = 'Se modificaron los datos de ' + str(dict_request['nombre_apellido'])
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert exito
                propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

            except pymongo.errors.WriteError as err:
                mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
                evento = 'editar_datos_cliente'
                reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                # alert warning
                propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

            cliente_id = str(request.GET['id'])

            resultado_query = col_clientes.find({'_id': cliente_id[1:]})

            for item in resultado_query:
                dict_request.update(item)

            form = ClienteForm({
                'nombre_apellido': dict_request['nombre_apellido'],
                'ci_ruc': dict_request['ci_ruc'],
                'dig_verif': dict_request['dig_verif'],
                'tel_nro': dict_request['tel_nro'],
                'direccion': dict_request['direccion'],
                'email': dict_request['email']})

            valores_template = {'form': form,
                                'propiedad_alerts': propiedad_alerts}

            return render(request,
                          'clientes/editar_datos_cliente.html',
                          context=valores_template)

    else:
        cliente_id = str(request.GET['id'])

        resultado_query = col_clientes.find({'_id': ObjectId(cliente_id[1:])})

        for item in resultado_query:
            dict_request.update(item)

        form = ClienteForm({
            'nombre_apellido': dict_request['nombre_apellido'],
            'ci_ruc': dict_request['ci_ruc'],
            'dig_verif': dict_request['dig_verif'],
            'tel_nro': dict_request['tel_nro'],
            'direccion': dict_request['direccion'],
            'email': dict_request['email']})

    propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'form': form,
                        'propiedad_alerts': propiedad_alerts}
    return render(request,
                      'clientes/editar_datos_cliente.html',
                      context=valores_template)

@csrf_exempt
def eliminar_cliente(request):
    dict_aux = {}
    responsable = request.user.username

    if request.method == 'POST':
        cliente_id = ObjectId(request.POST.get('cliente_id'))

        resultado_query = col_clientes.find({'_id': cliente_id})

        # se carga el diccionario auxiliar (para almacenar el Evento)
        for item in resultado_query:
            dict_aux.update({'nombre_apellido': item['nombre_apellido'],
                             'ci_ruc': item['ci_ruc']})

        try:
            # se procede a eliminar el documento de la BD
            col_clientes.delete_one({'_id': cliente_id})
            # se prepara el mensaje para el alert
            mensaje = 'El cliente ' + str(dict_aux['nombre_apellido']) + ' con C.I. Nro. ' + dict_aux['ci_ruc'] + ' ha sido eliminado de la nómina.'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'eliminar_cliente'
            reg_evento(evento, mensaje, datetime.now(), responsable)
            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.WriteError as err:
            mensaje = 'Ha ocurrido un error! Error #{0}'.format(err)
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'eliminar_cliente'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        lista_clientes = get_lista_clientes(request)

        valores_template = {'mensaje': mensaje,
                            'cantidad_clientes': lista_clientes['cantidad'],
                            'clientes': lista_clientes['lista'],
                            'propiedad_alerts': propiedad_alerts}

        return render(request,
                      'clientes/listar_clientes.html',
                      context=valores_template)


def libro_egreso(request):
    dict_request = {}
    egreso = {}

    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            dict_request = form.cleaned_data

            egreso_total = int(dict_request['gravadas_10']) + int(dict_request['gravadas_5']) + int(dict_request['exentas'])

            # se arma el diccionario que al final se gaurdara en la BD
            print(type(dict_request['operacion_fecha']))
            egreso = {
                'periodo': '',#dict_request['operacion_fecha'].year(),
                'tipo': dict_request['operacion_tipo'],
                'relacionadoTipoIdentificacion': '',    #armar diccionario
                'fecha': str(datetime.strftime(dict_request['operacion_fecha'], '%Y-%m-%d')),
                'ruc': DATOS_EMPRESA['ruc'],
                'egresoMontoTotal': egreso_total,
                'relacionadoNombres': str(dict_request['proveedor_razon']).capitalize(),
                'relacionadoNumeroIdentificacion': dict_request['proveedor_nro_identificacion'],
                'timbradoCondicion': dict_request['comprobante_condicion'],
                'timbradoDocumento': dict_request['proveedor_nro_identificacion'],
                'timbradoNumero': dict_request['comprobante_timbrado'],
                'tipoEgreso': dict_request['egreso_tipo'],
                'tipoEgresoTexto': '',  #armar diccionario
                'subtipoEgreso': dict_request['egreso_clasificacion'],
                'subtipoEgresoTexto': '',   #armar diccionario
            }

            for keys, values in egreso.items():
                print(keys, ': ', values)
        else:
            print(form.errors)



    else:
        form = EgresoForm()

    valores_template = {'form': form}

    return render(request,
                  'libros/libro_egreso.html',
                  context=valores_template)


def libro_ingreso(request):
    return


def estadisticas(request):
    valores_template = {}

    return render(request,
                  'estadisticas/estadisticas.html',
                  context=valores_template)


def ganancias(request):
    valores_template = {}

    return render(request,
                  'estadisticas/ganancias.html',
                  context=valores_template)


def ranking_articulos(request):
    primer_anho = ultimo_anho = 0
    LISTA_ANHOS = []

    primera_venta = col_ventas.find({}, {'ts': 1}).limit(1)
    ultima_venta = col_ventas.find({}, {'ts': 1}).sort([('ts', -1)]).limit(1)

    for item in primera_venta: primer_anho = int(item['ts'].year)

    for item in ultima_venta: ultimo_anho = int(item['ts'].year)

    for i in range(primer_anho, ultimo_anho + 1): LISTA_ANHOS.append(i)

    valores_template = {'meses_del_anho': MESES_DEL_ANHO,
                        'anhos': LISTA_ANHOS}

    return render(request,
                  'estadisticas/ranking_articulos.html',
                  context=valores_template)


def ventas_totales(request):
    primer_anho = ultimo_anho = 0
    LISTA_ANHOS = []

    primera_venta = col_ventas.find({}, {'ts': 1}).limit(1)
    ultima_venta = col_ventas.find({}, {'ts': 1}).sort([('ts', -1)]).limit(1)

    for item in primera_venta: primer_anho = int(item['ts'].year)

    for item in ultima_venta: ultimo_anho = int(item['ts'].year)

    for i in range(primer_anho, ultimo_anho + 1): LISTA_ANHOS.append(i)

    valores_template = {'meses_del_anho': MESES_DEL_ANHO,
                        'anhos': LISTA_ANHOS}

    return render(request,
                  'estadisticas/ventas_totales.html',
                  context=valores_template)


def ventas_dias_semana(request):

    primer_anho = ultimo_anho = 0
    LISTA_ANHOS = []

    primera_venta = col_ventas.find({}, {'ts': 1}).limit(1)
    ultima_venta = col_ventas.find({}, {'ts': 1}).sort([('ts', -1)]).limit(1)

    for item in primera_venta: primer_anho = int(item['ts'].year)

    for item in ultima_venta: ultimo_anho = int(item['ts'].year)

    for i in range(primer_anho, ultimo_anho + 1): LISTA_ANHOS.append(i)

    valores_template = {'meses_del_anho': MESES_DEL_ANHO,
                        'anhos': LISTA_ANHOS}

    return render(request,
                  'estadisticas/ventas_dias_semana.html',
                  context=valores_template)


def clasificaciones_stock(request):
    valores_template = {}

    return render(request,
                  'estadisticas/clasificaciones_stock.html',
                  context=valores_template)

@csrf_exempt
def valores_historicos_stock(request):
    valores_template = {}

    return render(request,
                  'estadisticas/valores_historicos_stock.html',
                  context=valores_template)

@csrf_exempt
def crear_clasificacion(request):
    responsable = request.user.username

    if request.method == 'POST':
        clasificacion = str(request.POST.get('clasificacion')).capitalize()
        dict_request = {'tipo': 'Clasificacion', 'descripcion': clasificacion}

        try:
            col_CMD.insert_one(dict_request)

            mensaje = 'La clasificación \"' + clasificacion + '\" ha sido creada con éxito'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'crear_clasificacion'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.DuplicateKeyError:
            mensaje = 'La clasificación \"' + clasificacion + '\" ya existe dentro del sistema'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'crear_clasificacion'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        if request.is_ajax():   #cuando se llama desde el template de carga de producto
            return JsonResponse({'propiedad_alerts': propiedad_alerts})

    else:
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'productos_promociones/nuevo_producto.html',
                      context=valores_template)\

@csrf_exempt
def cargar_distribuidor(request):
    responsable = request.user.username

    if request.method == 'POST':
        distribuidor = str(request.POST.get('distribuidor')).capitalize()
        dict_request = {'tipo': 'Distribuidor', 'descripcion': distribuidor}

        try:
            col_CMD.insert_one(dict_request)

            mensaje = 'El distribuidor \"' + distribuidor + '\" ha sido registrado con éxito'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'registrar_distribuidor'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.DuplicateKeyError:
            mensaje = 'El distribuidor \"' + distribuidor + '\" ya fue registrado dentro del sistema'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'registrar_distribuidor'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        if request.is_ajax():   #cuando se llama desde el template de carga de producto
            return JsonResponse({'propiedad_alerts': propiedad_alerts})

    else:
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'productos_promociones/nuevo_producto.html',
                      context=valores_template)\

@csrf_exempt
def registrar_marca(request):
    responsable = request.user.username

    if request.method == 'POST':
        marca = str(request.POST.get('marca')).capitalize()
        clasificacion = str(request.POST.get('clasificacion'))

        dict_request = {'tipo': 'Marca', 'descripcion': marca, 'clasificacion': clasificacion}

        try:
            col_CMD.insert_one(dict_request)

            mensaje = 'La marca \"' + marca + '\" ha sido registrada con éxito'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'registrar_marca'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert exito
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

        except pymongo.errors.DuplicateKeyError:
            mensaje = 'La marca \"' + marca + '\" ya ha sido registrada dentro del sistema'
            # se llama a la funcion para registrar el evento dentro de los logs
            evento = 'registrar_marca'
            reg_evento(evento, mensaje, datetime.now(), responsable)

            # alert warning
            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

        if request.is_ajax():   #cuando se llama desde el template de carga de producto
            return JsonResponse({'propiedad_alerts': propiedad_alerts})

    else:
        propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    valores_template = {'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'productos_promociones/nuevo_producto.html',
                      context=valores_template)


def ver_CMD(request):

    if request.method == 'POST':
        formClasificacion = ''
        formDistribuidor = ''
        formMarca = ''
    else:
        formClasificacion = ClasificacionForm()
        formDistribuidor = DistribuidorForm()
        formMarca = MarcaForm()

    valores_template = {'formClasi': formClasificacion,
                        'formDistri': formDistribuidor,
                        'formMarca': formMarca,
                        'propiedad_alerts': ''}


    return render(request,
                      'productos_promociones/ver_CMD.html',
                      context=valores_template)

@csrf_exempt
def editar_CMD(request):
    item_id = ObjectId(request.POST.get('item_id'))
    tipo = request.POST.get('tipo')
    operacion = request.POST.get('operacion')
    responsable = request.user.username

    propiedad_alerts = {'visibilidad': 'hidden'}    # al inicio el alert se esconde

    if request.method == 'POST':
        formClasificacion = ClasificacionForm(request.POST)
        formMarca = MarcaForm(request.POST)
        formDistribuidor = DistribuidorForm(request.POST)
        # El motor para editar viene desde ver_CMD.js
        if request.is_ajax():
            if operacion == 'get_data': # se llama al abrir el modal #modalEditar*
                lista_clasificaciones = []
                if tipo == 'Marca': #si se solicita una marca, tambien necesitamos la clasificacion de esa marca
                    query_clasificaciones = col_CMD.find({'tipo': 'Clasificacion'})
                    for clasificaciones in query_clasificaciones: lista_clasificaciones.append(clasificaciones['descripcion'])
                try:
                    query = col_CMD.find_one({'_id': item_id, 'tipo': tipo})
                    return JsonResponse({'descripcion': query['descripcion'],
                                         'clasificacion_actual': query['clasificacion'] if tipo == 'Marca' else '',
                                         'lista_clasificaciones': lista_clasificaciones if tipo == 'Marca' else ''})
                except pymongo.errors as err:
                    print(err)

            elif operacion == 'editar':
                if tipo == 'Clasificacion':
                    # se obtiene la nueva clasificacion
                    nueva_clasificacion = request.POST.get('nueva_clasificacion')
                    # se obtiene la vieja clasificacion (para asi editar todos los articulos con la vieja clasificacion)
                    vieja_clasificacion = str(col_CMD.find_one({'_id': item_id, 'tipo': tipo}, {'descripcion': 1})['descripcion'])

                    if formClasificacion.has_changed():
                        try:
                            # se actualiza el documento con la nueva clasificacion
                            col_CMD.update_one({'_id': item_id}, {'$set': {'descripcion': nueva_clasificacion}})
                            # se actualizan los documentos de todas las marcas que estaban en la vieja clasificacion
                            col_CMD.update_many({'tipo': 'Marca', 'clasificacion': vieja_clasificacion}, {'$set': {'clasificacion': nueva_clasificacion}})
                            # se actualizan los documentos de todos los productos que estaban en la vieja clasificacion
                            col_producto.update_many({'clasificacion': vieja_clasificacion}, {'$set': {'clasificacion': nueva_clasificacion}})

                            mensaje = descripcion_evento = 'Se ha modificado con éxito la ' + tipo + ', de ' + vieja_clasificacion.upper() + ' a ' + nueva_clasificacion.upper()

                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert exito
                            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje, 'tipo': 'alert-success', 'icono': 'fa-check'}

                        except pymongo.errors.WriteError as err:
                            mensaje = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert warning
                            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

                        return JsonResponse({'propiedad_alerts': propiedad_alerts})
                    else:
                        print('el form ha tenido un error')

                elif tipo == 'Marca':
                    # se obtiene la nueva marca
                    nueva_marca = request.POST.get('nueva_marca')
                    nueva_clasificacion_x_marca = str(request.POST.get('clasificacion_x_marca'))
                    # se obtiene la vieja marca (para asi editar todos los articulos con la vieja marca)
                    vieja_marca = str(col_CMD.find_one({'_id': item_id, 'tipo': tipo})['descripcion'])
                    vieja_clasificacion_x_marca = str(col_CMD.find_one({'_id': item_id, 'tipo': tipo})['clasificacion'])

                    if formMarca.has_changed():
                        try:
                            # se actualiza el documento con la nueva marca
                            col_CMD.update_one({'_id': item_id}, {'$set': {'descripcion': nueva_marca, 'clasificacion': nueva_clasificacion_x_marca}})
                            # se actualizan los documentos de todos los productos que estaban con la vieja marca / NO se toca la clasificacion del producto
                            if str(nueva_marca).lower() != str(vieja_marca).lower():    # se verifica que haya alguna modificacion, si es asi, se modifican todos los documentos de los productos bajo la misma marca
                                col_producto.update_many({'marca': vieja_marca}, {'$set': {'marca': nueva_marca}})

                            if str(nueva_clasificacion_x_marca).lower() != str(vieja_clasificacion_x_marca).lower() and str(nueva_marca).lower() == str(vieja_marca).lower():
                                # si solo se modifico la clasificacion, se muestra un mensaje
                                mensaje_alert = descripcion_evento = 'Se ha modificado con éxito la clasificación de la Marca ' + vieja_marca.upper() + ', de ' + vieja_clasificacion_x_marca.upper() + ' a ' + nueva_clasificacion_x_marca.upper()
                            elif str(nueva_clasificacion_x_marca).lower() == str(vieja_clasificacion_x_marca).lower() and str(nueva_marca).lower() != str(vieja_marca).lower():
                                # si solo se modifico la marc, se muestra un mensaje
                                mensaje_alert = descripcion_evento = 'Se ha modificado con éxito la ' + tipo + ', de ' + vieja_marca.upper() + ' a ' + nueva_marca.upper()
                            elif str(nueva_clasificacion_x_marca).lower() != str(vieja_clasificacion_x_marca).lower() and str(nueva_marca).lower() != str(vieja_marca).lower():
                                # si se modificacon ambos parametros
                                print('deberia pasar esto')
                                mensaje_alert = descripcion_evento = 'Se ha modificado con éxito la ' + tipo + ', de ' + vieja_marca.upper() + ' a ' + nueva_marca.upper() + ' y ' \
                                                                     'la clasificación de ' + vieja_clasificacion_x_marca.upper() + ' a ' + nueva_clasificacion_x_marca.upper()
                            else:
                                mensaje_alert = descripcion_evento = 'No se ha realizado ninguna modificación'

                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert exito
                            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

                        except pymongo.errors.WriteError as err:
                            mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert warning
                            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

                        return JsonResponse({'propiedad_alerts': propiedad_alerts})
                    else:
                        print('el form ha tenido un error')

                elif tipo == 'Distribuidor':
                    # se obtiene la nuevo distribuidor
                    nuevo_distribuidor = request.POST.get('nuevo_distribuidor')
                    # se obtiene la vieja marca (para asi editar todos los articulos con la vieja marca)
                    viejo_distribuidor = str(col_CMD.find_one({'_id': item_id, 'tipo': tipo}, {'descripcion': 1})['descripcion'])

                    if formDistribuidor.has_changed():
                        try:
                            # se actualiza el documento con la nueva marca
                            col_CMD.update_one({'_id': item_id}, {'$set': {'descripcion': nuevo_distribuidor}})
                            # se actualizan los documentos de todos los productos que estaban con la vieja marca
                            col_producto.update_many({'distribuidor': viejo_distribuidor}, {'$set': {'distribuidor': nuevo_distribuidor}})

                            mensaje_alert = descripcion_evento = 'Se ha modificado con éxito al ' + tipo + ', de ' + viejo_distribuidor.upper() + ' a ' + nuevo_distribuidor.upper()

                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert exito
                            propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

                        except pymongo.errors.WriteError as err:
                            mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)

                            evento = 'editar_datos_CMD'
                            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

                            # alert warning
                            propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

                        return JsonResponse({'propiedad_alerts': propiedad_alerts})
                    else:
                        print(formDistribuidor.errors)
                        print('el form ha tenido un error')

    else:
        formClasificacion = ClasificacionForm()
        formMarca = MarcaForm()
        formDistribuidor = DistribuidorForm()

    valores_template = {'formClasi': formClasificacion,
                        'formMarca': formMarca,
                        'formDistri': formDistribuidor,
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'productos_promociones/ver_CMD.html',
                      context=valores_template)

@csrf_exempt
def eliminar_CMD(request):
    item_id = request.POST.get('item_id')
    tipo = request.POST.get('tipo')
    desc = request.POST.get('desc')
    responsable = request.user.username

    try:
        col_CMD.delete_one({'_id': ObjectId(item_id)})

        mensaje_alert = descripcion_evento = 'Se ha eliminado con exito la ' + tipo + ' - ' + desc

        evento = 'eliminar_CMD'
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

        # alert exito
        propiedad_alerts = {'visibilidad': '', 'mensaje': mensaje_alert, 'tipo': 'alert-success', 'icono': 'fa-check'}

    except pymongo.errors.OperationFailure as err:
        mensaje_alert = descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
        evento = 'eliminar_CMD'
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

        # alert warning
        propiedad_alerts = {'visibilidad': '', 'mensaje':mensaje_alert, 'tipo': 'alert-warning', 'icono': 'fa-exclamation-triangle'}

    return JsonResponse({'propiedad_alerts': propiedad_alerts})

@csrf_exempt
def abrir_caja(request):
    monto_apertura = int(request.POST.get('monto_apertura'))
    operacion = request.POST.get('operacion')

    fecha = datetime.now()

    responsable = request.user.username

    dict_caja = {
        'monto_apertura': monto_apertura,
        'monto_cierre': 0,
        'efectivo': 0,
        'tc': 0,
        'td': 0,
        'costos': 0,
        'ganancias': 0,
        'fecha_apertura': fecha,
        'fecha_cierre': 'Sin registro',
        'estado': 'abierta'  # el estado demuestra que aun no se ha cerrado la caja
    }

    if operacion == 'editar':
        # 1ro. se recupera el viejo monto de apertura y cierre
        item_id = ObjectId(request.POST.get('item_id'))
        query_caja = col_caja.find_one({'_id': item_id}, {'monto_apertura': 1, 'monto_cierre': 1})
        monto_apertura_viejo = query_caja['monto_apertura']
        monto_cierre_viejo = query_caja['monto_cierre']

        # 2do. se resta el viejo monto de apertura al monto de cierre, dando el total de ventas de ese dia
        monto_total = monto_cierre_viejo - monto_apertura_viejo

        # 3ro. se suma el nuevo monto de apertura al monto_total, dando el nuevo monto de cierre
        monto_cierre = monto_total + monto_apertura

        try:
            col_caja.update_one({'_id': item_id}, {'$set': {'monto_apertura': monto_apertura, 'monto_cierre': monto_cierre}})

            evento = 'editar_monto_apertura_caja'
            descripcion_evento = 'Se ha modificado el monto de apertura de la caja, de Gs. ' + str("{0:,}".format(int(monto_apertura_viejo))) + ' a Gs. ' + str("{0:,}".format(int(monto_apertura)))
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

        except pymongo.errors.WriteError as err:
            evento = 'editar_monto_apertura_caja'
            descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)
    else:
        try:
            col_caja.insert_one(dict_caja)
            evento = 'apertura_caja'
            descripcion_evento = 'La caja fue abierta con Gs. ' + str("{0:,}".format(int(dict_caja['monto_apertura'])))
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)
        except pymongo.errors.WriteError as err:
            evento = 'apertura_caja'
            descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
            reg_evento(evento, descripcion_evento, datetime.now(), responsable)

    return JsonResponse({'data': ''})

@csrf_exempt
def cerrar_caja(request):
    fecha_cierre = datetime.now()
    fecha_apertura = ''
    id_apertura = ''
    monto_apertura = 0
    subtotal = efectivo = tc = td = costos = ganancias = 0

    responsable = request.user.username

    #1ro. Se solicita el registro de apertura de la caja
    resultado_query_caja = col_caja.find({'estado': 'abierta'}, sort=[('fecha_apertura', pymongo.DESCENDING)], limit=1)

    for item in resultado_query_caja:
        fecha_apertura = item['fecha_apertura']
        id_apertura = item['_id']
        monto_apertura = item['monto_apertura']

    # 2do. se obtienen todos los datos de las ventas desde el momento de la apertura hasta el momento del cierre
    query_ventas = [
        {'$match':{
            'ts':{'$gte': datetime(fecha_apertura.year, fecha_apertura.month, fecha_apertura.day, fecha_apertura.hour, fecha_apertura.minute, fecha_apertura.second),
                  '$lte': datetime(fecha_cierre.year, fecha_cierre.month, fecha_cierre.day, fecha_cierre.hour, fecha_cierre.minute, fecha_cierre.second)},
            'anulado': 'FALSE'
        }},
        {'$group': {
            '_id': '$metodo_pago',
            'monto': {'$sum': {'$toInt': '$suma_total'}}
        }}
    ]

    resultado_query_ventas = {}
    try:
        resultado_query_ventas = col_ventas.aggregate(query_ventas)
    except pymongo.errors.CursorNotFound as err:
        print(err)

    for item in resultado_query_ventas:
        efectivo += item['monto'] if item['_id'] == 'efectivo' else 0
        td += item['monto'] if item['_id'] == 'td' else 0
        tc += item['monto'] if item['_id'] == 'tc' else 0
        subtotal += item['monto']

    # 3ro. se obtienen los costos y ganancias de las ventas
    query_costos_ganancias = [
        {'$match':{
            'ts':{'$gte': datetime(fecha_apertura.year, fecha_apertura.month, fecha_apertura.day, fecha_apertura.hour, fecha_apertura.minute, fecha_apertura.second),
                  '$lte': datetime(fecha_cierre.year, fecha_cierre.month, fecha_cierre.day, fecha_cierre.hour, fecha_cierre.minute, fecha_cierre.second)},
            'anulado': 'FALSE'
        }},
        {'$unwind': '$productos'},  # se recorre por el subgrupo
        {'$group': {
            '_id': 'null',
            'suma_costos': {'$sum': '$productos.precio_costo'},
            'suma_ganancias': {'$sum': {'$subtract': ['$productos.subtotal', '$productos.precio_costo']}}
        }}
    ]

    resultado_query_costos_ganancias = {}
    try:
        resultado_query_costos_ganancias = col_ventas.aggregate(query_costos_ganancias)
    except pymongo.errors.CursorNotFound as err:
        print(err)

    for item in resultado_query_costos_ganancias:
            costos += item['suma_costos']
            ganancias += item['suma_ganancias']

    # 5to. Se suma el monto de apertura y el monto de cierre
    monto_cierre = subtotal + monto_apertura

    #6to. Se arma el diccionario que debe ser actualizado en la BD
    dict_caja = {
        'monto_apertura': monto_apertura,
        'monto_cierre': monto_cierre,
        'efectivo': efectivo,
        'tc': tc,
        'td': td,
        'costos': costos,
        'ganancias': ganancias,
        'fecha_apertura': fecha_apertura,
        'fecha_cierre': fecha_cierre,
        'estado': 'cerrada'  # el estado demuestra que aun no se ha cerrado la caja
    }

    #6to. se actualiza la BD con el nuevo documento
    try:
        col_caja.update_one({'_id': ObjectId(id_apertura)}, {'$set': dict_caja})

        evento = 'cierre_caja'
        descripcion_evento = 'La caja fue cerrada con Gs. ' + str("{0:,}".format(int(dict_caja['monto_cierre'])))
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

    except pymongo.errors.WriteError as err:
        evento = 'cierre_caja'
        descripcion_evento = 'Ha ocurrido un error! Error #{0}'.format(err)
        reg_evento(evento, descripcion_evento, datetime.now(), responsable)

    return JsonResponse({'data': ''})


def verificar_caja(request):
    formCajaApertura = CajaAperturaForm()

    propiedad_alerts = {'visibilidad': 'hidden', 'mensaje': '', 'tipo': 'alert-success', 'icono': 'fa-check'}

    valores_template = {'formCajaApertura': formCajaApertura,
                        'propiedad_alerts': propiedad_alerts}

    return render(request,
                      'caja/verificar_caja.html',
                      context=valores_template)


def ver_logs(request):

    propiedad_alerts = {'visibilidad': 'hidden', 'mensaje': '', 'tipo': 'alert-success', 'icono': 'fa-check'}

    valores_template = {'propiedad_alerts': propiedad_alerts}


    return render(request,
                      'ver_logs.html',
                      context=valores_template)