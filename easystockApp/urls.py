from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', TemplateView.as_view(template_name='home.html'), name='home'),

    # urls relacionados a productos
    path('nuevo_producto/', views.nuevo_producto, name='nuevo_producto'),
    path('listar_productos/', views.listar_productos, name='listar_productos'),
    path('agregar_al_stock/', views.agregar_al_stock, name='agregar_al_stock'),
    path('editar_datos_producto/$', views.editar_datos_producto, name='editar_datos'),
    path('eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),
    path('crear_clasificacion/', views.crear_clasificacion, name = 'crear_clasificacion'),
    path('cargar_distribuidor/', views.cargar_distribuidor, name = 'cargar_distribuidor'),
    path('registrar_marca/', views.registrar_marca, name = 'registrar_marca'),
    path('ver_CMD/', views.ver_CMD, name = 'ver_CMD'),
    path('editar_CMD/', views.editar_CMD, name = 'editar_CMD'),
    path('eliminar_CMD/', views.eliminar_CMD, name = 'eliminar_CMD'),

    #urls relacionados a promociones
    path('crear_promo/', views.crear_promocion, name='crear_promo'),
    path('listar_promociones/', views.listar_promociones, name='listar_promociones'),
    path('eliminar_promocion/', views.eliminar_promocion, name='eliminar_promocion'),

    #url relacionado a ventas
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('verificar_ventas/', views.verificar_ventas, name='verificar_ventas'),
    path('venta_exitosa/', views.registrar_venta, name='venta_exitosa'),
    path('anular_factura/', views.anular_factura, name='anular_factura'),

    #url relacionado a clientes
    path('nuevo_cliente/', views.nuevo_cliente, name='nuevo_cliente'),
    path('listar_clientes/', views.listar_clientes, name='listar_clientes'),
    path('editar_datos_cliente/$', views.editar_datos_cliente, name='editar_datos_cliente'),
    path('eliminar_cliente/', views.eliminar_cliente, name='eliminar_cliente'),

    #url gets varios
    path('get_lista_clientes/', views.get_lista_clientes, name='get_lista_clientes'),
    path('get_productos_template_stock/', views.get_productos_template_stock, name='get_productos_template_stock'),
    path('get_productos_modal/', views.get_productos_modal, name='get_productos_modal'),
    path('get_promociones_modal_template_registro_venta/', views.get_promociones_modal_template_registro_venta, name='get_promociones_modal_template_registro_venta'),
    path('get_ventas_template_verificar_ventas/', views.get_ventas_template_verificar_ventas, name='get_ventas_template_verificar_ventas'),
    path('get_lista_articulos_vendidos_modal_template_verificar_ventas/', views.get_lista_articulos_vendidos_modal_template_verificar_ventas, name='get_lista_articulos_vendidos_modal_template_verificar_ventas'),
    path('get_detalles_cliente_modal_template_verificar_ventas/', views.get_detalles_cliente_modal_template_verificar_ventas, name='get_detalles_cliente_modal_template_verificar_ventas'),
    path('get_detalles_factura_modal_template_verificar_ventas/', views.get_detalles_factura_modal_template_verificar_ventas, name='get_detalles_factura_modal_template_verificar_ventas'),
    path('get_detalles_promocion_modal_template_listar_productos/', views.get_detalles_promocion_modal_template_listar_productos, name='get_detalles_promocion_modal_template_listar_productos'),
    path('actualizar_tabla_promociones_modal_template_registro_venta/', views.actualizar_tabla_promociones_modal_template_registro_venta, name='actualizar_tabla_promociones_modal_template_registro_venta'),
    path('actualizar_tabla_productos_modal_template_registro_venta/', views.actualizar_tabla_productos_modal_template_registro_venta, name='actualizar_tabla_productos_modal_template_registro_venta'),
    path('get_CMD/', views.get_CMD, name='get_CMD'),
    path('get_clasificaciones/', views.get_clasificaciones, name = 'get_clasificaciones'),
    path('get_marcas/', views.get_marcas, name = 'get_marcas'),
    path('get_distribuidores/', views.get_distribuidores, name = 'get_distribuidores'),
    path('get_promocion_condicion_eliminar_producto/', views.get_promocion_condicion_eliminar_producto, name='get_promocion_condicion_eliminar_producto'),
    path('get_info_cajas/', views.get_info_cajas, name='get_info_cajas'),
    path('get_monto_apertura_caja/', views.get_monto_apertura_caja, name='get_monto_apertura_caja'),
    path('get_logs/', views.get_logs, name='get_logs'),
    path('get_valor_stock_detallado/', views.get_valor_stock_detallado, name='get_valor_stock_detallado'),
    path('get_valores_historicos_stock/', views.get_valores_historicos_stock, name='get_valores_historicos_stock'),


    path('rollback_bd/', views.rollback_bd, name='rollback_bd'),
    path('consultar_disponibilidad_datos/', views.consultar_disponibilidad_datos, name='consultar_disponibilidad_datos'),

    #url relacionado a los libros
    path('libro_egreso/', views.libro_egreso, name='libro_egreso'),
    path('libro_ingreso/', views.libro_ingreso, name='libro_ingreso'),

    #url relacionado a las estadisticas
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('estadisticas/ganancias', views.ganancias, name='ganancias'),
    path('estadisticas/ranking_articulos', views.ranking_articulos, name='ranking_articulos'),
    path('estadisticas/ventas_totales', views.ventas_totales, name='ventas_totales'),
    path('estadisticas/ventas_dias_semana', views.ventas_dias_semana, name='ventas_dias_semana'),
    path('estadisticas/clasificaciones_stock', views.clasificaciones_stock, name='clasificaciones_stock'),
    path('estadisticas/valores_historicos_stock', views.valores_historicos_stock, name='valores_historicos_stock'),
    path('get_ganancias_diarias/', views.get_ganancias_diarias, name='get_ganancias_diarias'),
    path('get_ranking_articulos/', views.get_ranking_articulos, name='get_ranking_articulos'),
    path('get_top_100/', views.get_top_100, name='get_top_100'),
    path('get_ventas_dias_x_semana/', views.get_ventas_dias_x_semana, name='get_ventas_dias_x_semana'),
    path('get_distribucion_stock/', views.get_distribucion_stock, name='get_distribucion_stock'),
    path('get_meses_x_anho/', views.get_meses_x_anho, name= 'get_meses_x_anho'),

    #url relacionado a la apertura y al cierre de caja
    path('abrir_caja/', views.abrir_caja, name='abrir_caja'),
    path('cerrar_caja/', views.cerrar_caja, name='cerrar_caja'),
    path('verificar_caja/', views.verificar_caja, name='verificar_caja'),

    path('ver_logs/', views.ver_logs, name='ver_logs'),
]