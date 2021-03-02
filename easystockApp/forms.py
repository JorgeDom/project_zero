from django import forms
from django.forms import ModelForm
from easystockApp.models import *

IMPUESTOS = [
    ('5', '5%'),
    ('10', '10%'),
    ('EX', 'Exenta'),
]

OPERACION_TIPO_completo = [
    ('1', 'Factura'), ('2', 'Autofactura'), ('3', 'Boleta de Venta'), ('4', 'Nota de Crédito'),
    ('5', 'Liquidación de Salarios'), ('6', 'Extracto de Cuenta IPS'), ('7', 'Extracto de Tarjeta de Crédito/Tarjeta de Débito'),
    ('9', 'Transferencias o Giros Bancarios / Boleta de Depósito'), ('10', 'Comprobante del Exterior Legalizado'),
    ('11', 'Comprobante de Ingreso de Entidades Públicas, Religiosas o de Beneficio Público'), ('12', 'Ticket (Máquina Registradora)'),
    ('13', 'Despacho de Importación'),
    ('14', 'Otros comprobantes de venta que respaldan los egresos (pasaje aéreos, entradas a espectáculos públicos, boletos de transporte público) o cuando no exista la obligación de emitir comprobantes de venta')
]

OPERACION_TIPO = [
    ('1', 'Factura')
]

EGRESO_TIPO = [
    ('gasto', 'Gasto'),
    ('inversion_actividad', 'Inversiones Relacionadas a la Actividad Gravada'),
    ('inversion_personas', 'Inversiones Personales y de familiares a Cargo')
]

EGRESO_CLASIFICACION = [
    ('GPERS', 'Gastos personales y de familiares a cargo realizados en el país'),
    ('GPERSSINCV', 'Gastos personales y de familiares a cargo realizados en el país, cuando no exista obligación de contar con comprobantes de venta'),
    ('GACT', 'Gastos relacionados a la actividad gravada realizados en el país'),
    ('DONAC', 'Donaciones'),
    ('PREST', 'Amortización o cancelación de préstamos obtenidos antes de ser contribuyente del IRP, así como sus intereses, comisiones y otros recargos'),
    ('CUOTA', 'Cuotas de capital de las financiaciones, así como los intereses, las comisiones y otros recargos pagados por la adquisición de bienes o servicios'),
    ('MEH', 'Muebles, Equipos y Herramientas'),
    ('INM', 'Adquisición de inmuebles, construcción o mejoras de inmuebles'),
    ('EDU', 'Educación y/o Capacitación'),
    ('COLOC', 'Colocaciones de dinero'),
    ('DESCJBPN', 'Descuentos legales por Aporte al Régimen de Jubilaciones y Pensiones en carácter de trabajador dependiente'),
    ('REMDEP', 'Salarios y otras remuneraciones pagados a trabajadores dependientes'),
    ('APRTSS', 'Aportes al régimen de seguridad social en carácter de empleador'),
    ('GPERSEXT', 'Gastos personales y de familiares a cargo realizados en el exterior'),
    ('GACTEXT', 'Gastos relacionados a la actividad gravada realizados en el exterior'),
    ('GSTADM', 'Intereses, comisiones y demás gastos administrativos'),
    ('RECPOS', 'Intereses, comisiones y otros recargos pagados por los préstamos obtenidos, con posterioridad a ser contribuyentes del IRP'),
    ('CMPOF', 'Compra de útiles de oficina, gastos de limpieza y mantenimiento'),
    ('GSTACT', 'Otros gastos realizados relacionados a la actividad gravada'),
    ('REMINDEP', 'Honorarios y otras remuneraciones pagados al personal independiente'),
    ('GSTACTEXT', 'Gastos realizados en el exterior relacionados a la actividad gravada'),
    ('OG', 'Otros gastos realizados en el ejercicio'),
    ('INVLF', 'Inversión en licencias, franquicias y otros similares'),
    ('INVLFEXT', 'Inversión en licencias, franquicias y otros similares, adquiridos del exterior'),
    ('IMPBIENES', 'Importación ocasional de bienes'),
    ('ACCIONES', 'Compra de acciones o cuotas partes de sociedades constituidas en el país'),
    ('CAPITAL', 'Aporte de capital realizado en sociedades constituidas en el país'),
    ('SALUD', 'Salud'),
]

CONDICION_VENTA = [
    ('contado', 'Contado'),
    ('credito', 'Crédito')
]

IDENTIFICACION_TIPO = [
    ('RUC', 'RUC'),
    ('PASAPORTE', 'Pasaporte'),
    ('CEDULA', 'Cédula de Identidad'),
    ('CEDULA_EXTRANJERA', 'Cédula Extranjera'),
    ('IDENTIFICACION_TRIBUTARIA', 'Identificación Tributaria'),
]

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

        widgets = {
            'clasificacion': forms.Select(choices=[('default', 'Seleccione una clasificación...')], attrs={'class':'form-control', 'required': 'required'}),
            'distribuidor': forms.Select(choices=[('default', 'Seleccione un distribuidor...')], attrs={'class':'form-control', 'required': 'required'}),
            'marca': forms.Select(choices=[('default', 'Seleccione una marca...')], attrs={'class':'form-control', 'required': 'required'}),
            'descripcion': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Descripción (Pilsen\'i, Guaraná, etc.)', 'required': 'required'}),
            'presentacion': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Presentación (tamaño, volúmen, unidades, etc.)', 'required': 'required'}),
            'barcode': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Código de barras', 'required': 'required'}),
            'etiqueta_opcional': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Etiqueta opcional'}),
            'precio_costo': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Precio de costo', 'required': 'required'}),
            'precio_venta': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Precio de venta', 'required': 'required'}),
            'impuesto': forms.Select(choices=IMPUESTOS, attrs={'class':'form-control', 'required': 'required'}),
            'stock-minimo': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Mínimo', 'required': 'required'}),
            'stock-optimo': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Óptimo', 'required': 'required'}),
            'stock-actual': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Actual', 'required': 'required'}),
        }

class VentaForm(ModelForm):
    class Meta:
        model = Venta
        fields = '__all__'

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Nombre/s y Apellido/s', 'required': 'required'}),
            'ci_ruc': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'C.I./R.U.C. (sin dig. verif.)', 'required': 'required'}),
            'dig_verif': forms.NumberInput(attrs={'min': '0', 'max':'9', 'size':'1', 'class':'form-control'}),
            'tel_nro': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Tel. Celular o Particular'}),
            'direccion': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Dirección'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
        }

class EgresoForm(ModelForm):
    class Meta:
        model = LibroEgreso
        fields = '__all__'

        widgets = {
            'operacion_tipo': forms.Select(choices=OPERACION_TIPO, attrs={'class':'form-control form-control-sm'}),
            'operacion_fecha': forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'comprobante_timbrado': forms.NumberInput(attrs={'min': '1', 'max': '99999999', 'class':'form-control form-control-sm'}),
            'comprobante_nro': forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'comprobante_condicion': forms.Select(choices=CONDICION_VENTA, attrs={'class':'form-control form-control-sm'}),
            'proveedor_tipo_identificacion': forms.Select(choices=IDENTIFICACION_TIPO, attrs={'class':'form-control form-control-sm'}),
            'proveedor_nro_identificacion': forms.NumberInput(attrs={'min': '1', 'max': '99999999', 'class':'form-control form-control-sm'}),
            'proveedor_razon': forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'gravadas_10': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'gravadas_5': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'exentas': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'egreso_tipo': forms.Select(choices=EGRESO_TIPO, attrs={'class':'form-control form-control-sm'}),
            'egreso_clasificacion': forms.Select(choices=EGRESO_CLASIFICACION, attrs={'class': 'form-control form-control-sm'})
        }

class ClasificacionForm(ModelForm):
    class Meta:
        model = Clasificacion
        fields = '__all__'

        widgets = {
            'nueva_clasificacion': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Clasificación (Cerveza, Gaseosa, Alimento, etc.)', 'required': 'required'})
        }

class DistribuidorForm(ModelForm):
    class Meta:
        model = Distribuidor
        fields = '__all__'

        widgets = {
            'nuevo_distribuidor': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Nombre (Cervepar, Gloria S.A., etc.)', 'required': 'required'})
        }

class MarcaForm(ModelForm):
    class Meta:
        model = Marca
        fields = '__all__'

        widgets = {
            'nueva_marca': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Marca (Pilsen, Coca-Cola, Santa Helena, etc.)', 'required': 'required'}),
            'clasificacion_x_marca': forms.Select(choices=[('default', 'Seleccione una clasificacón...')], attrs={'class':'form-control', 'required': 'required'})
        }

class CajaAperturaForm(ModelForm):
    class Meta:
        model = Caja
        fields = {'caja_apertura'}

        widgets = {
            'caja_apertura': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Monto inicial (Gs.)', 'required': 'required'})
        }

class CajaCierreForm(ModelForm):    # no se utiliza
    class Meta:
        model = Caja
        fields = {'caja_cierre'}

        widgets = {
            'caja_cierre': forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Monto al cierre (Gs.)', 'required': 'required'})
        }