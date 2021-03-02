from djongo import models


IMPUESTOS = [{
    ('5', '5%'),
    ('10', '10%'),
    ('EX', 'Exenta'),
}]

class Stock(models.Model):
    minimo = models.PositiveIntegerField(default=1, blank=False, verbose_name="Cantidad mínima")
    optimo = models.PositiveIntegerField(default=1, blank=False, verbose_name="Cantidad óptima")
    actual = models.PositiveIntegerField(default=0, blank=False, verbose_name="Cantidad actual")

    def __unicode__(self):
        return self.actual

    class Meta:
        abstract = True


class Producto(models.Model):
    clasificacion = models.CharField(max_length=50, default='', blank=False, help_text="Cerveza, Licor, Cigarrillo, etc.", verbose_name="Clasificación")
    distribuidor = models.CharField(max_length=100, default='', blank=False, help_text="Cerverpar, etc.", verbose_name="Distribuidor")
    marca = models.CharField(max_length=50, default='', blank=False, help_text="Pilsen, Beldent, Lucky Strike, etc.", verbose_name="Marca")
    descripcion = models.CharField(max_length=50, blank=False, help_text="Pilsen'i, Infinity, etc.", verbose_name="Descripción")
    presentacion = models.CharField(max_length=50, blank=False, help_text="350ml, 1Ltr., etc.", verbose_name="Presentación")
    barcode = models.BigIntegerField(blank=False, verbose_name='Código de barras')
    etiqueta_opcional = models.CharField(max_length=100, blank=True, default='', help_text="Cualquier otra carateristica", verbose_name="Etiqueta opcional")
    precio_costo = models.PositiveIntegerField(blank=False, verbose_name="Precio de costo")
    precio_venta = models.PositiveIntegerField(blank=False, verbose_name="Precio de venta")
    impuesto = models.CharField(blank=False, max_length=2, default='10')
    stock = models.EmbeddedField(model_container=Stock)
    #imagen = models.ImageField(verbose_name="Imagen")

    #def __str__(self):
    #    return str(self.marca + ' - ' + self.descripcion + ' - ' + self.presentacion)


class Venta(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now=True)


class ProductosPromocion(models.Model):
    id_producto = models.CharField(max_length=50),
    cantidad = models.PositiveIntegerField(default=1, max_length=10)

    class Meta:
        abstract = True


class Promocion(models.Model):
    descripcion = models.CharField(default='', blank=True, max_length=200, verbose_name="Descripción")
    productos = models.EmbeddedField(verbose_name="", model_container=ProductosPromocion)
    precio_promocional = models.PositiveIntegerField(default='', blank=False, verbose_name="Precio promocional")


class Cliente(models.Model):
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombres y Apellidos", blank=False)
    ci_ruc = models.CharField(max_length=15, verbose_name="C.I./R.U.C.", blank=False)
    dig_verif = models.IntegerField(verbose_name="DIV", blank=True)
    tel_nro = models.CharField(max_length=20, verbose_name="Número de Teléfono", default='', blank=True)
    direccion = models.CharField(max_length=200, verbose_name="Dirección part.", default='', blank=True)
    email = models.EmailField(max_length=50, verbose_name="E-mail", default='', blank=True)

class LibroEgreso(models.Model):
    operacion_tipo = models.CharField(max_length=200, verbose_name="Tipo de documento que respalda el Egreso")
    operacion_fecha = models.DateField(max_length=20, verbose_name="Fecha", blank=False)
    comprobante_timbrado = models.IntegerField(verbose_name="Timbrado", blank=False)
    comprobante_nro = models.CharField(max_length=20, verbose_name="Número", blank=False)
    comprobante_condicion = models.CharField(max_length=20, verbose_name="Condición de venta")
    proveedor_tipo_identificacion = models.CharField(max_length=20, verbose_name="Tipo de Identificación", blank=False)
    proveedor_nro_identificacion = models.CharField(max_length=20, verbose_name="Número de Identificación", blank=False)
    proveedor_razon = models.CharField(max_length=200, verbose_name="Nombres y Apellidos o Razón Social", blank=False)
    gravadas_10 = models.IntegerField(verbose_name="Gravadas 10%", blank=False)
    gravadas_5 = models.IntegerField(verbose_name="Gravadas 5%", blank=False)
    exentas = models.IntegerField(verbose_name="Exentas", blank=False)
    egreso_tipo = models.CharField(max_length=200, verbose_name="Tipo de Egreso", blank=False)
    egreso_clasificacion = models.CharField(max_length=500, verbose_name="Clasificación de Egreso")

class Clasificacion(models.Model):
    nueva_clasificacion =  models.CharField(max_length=100, blank=False, verbose_name='Clasificación', default='')

class Distribuidor(models.Model):
    nuevo_distribuidor =  models.CharField(max_length=100, blank=False, verbose_name='Distribuidor', default='')

class Marca(models.Model):
    nueva_marca =  models.CharField(max_length=100, blank=False, verbose_name='Marca', default='')
    clasificacion_x_marca =  models.CharField(max_length=100, blank=False, verbose_name='Clasificacion', default='')

class Caja(models.Model):
    caja_apertura = models.BigIntegerField(verbose_name='Monto inicial', blank=False)
    caja_cierre = models.BigIntegerField(verbose_name='Monto al cierre', blank=False)
