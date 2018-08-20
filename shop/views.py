# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .forms import *
from .models import *
from decimal import *
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, IntegrityError
from django.db.models.fields.files import FieldFile
from django.http import *
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView
import xml.etree.ElementTree as ET

# http://yuji.wordpress.com/2013/01/30/django-form-field-in-initial-data-requires-a-fieldfile-instance/
class FakeField(object):
    storage = default_storage

fieldfile = FieldFile(None, FakeField, "dummy.txt")

class HomePageView(TemplateView):
    template_name = "shop/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        messages.info(self.request, "hello http://example.com")
        return context

class DefaultFormsetView(FormView):
    template_name = "shop/formset.html"
    form_class = ContactFormSet

class DefaultFormView(FormView):
    template_name = "shop/form.html"
    form_class = ContactForm

class DefaultFormByFieldView(FormView):
    template_name = "shop/form_by_field.html"
    form_class = ContactForm

class FormHorizontalView(FormView):
    template_name = "shop/form_horizontal.html"
    form_class = ContactForm

class FormInlineView(FormView):
    template_name = "shop/form_inline.html"
    form_class = ContactForm

class FormWithFilesView(FormView):
    template_name = "shop/form_with_files.html"
    form_class = FilesForm

    def get_context_data(self, **kwargs):
        context = super(FormWithFilesView, self).get_context_data(**kwargs)
        context["layout"] = self.request.GET.get("layout", "vertical")
        return context

    def get_initial(self):
        return {"file4": fieldfile}

class PaginationView(TemplateView):
    template_name = "shop/pagination.html"

    def get_context_data(self, **kwargs):
        context = super(PaginationView, self).get_context_data(**kwargs)
        lines = []
        for i in range(200):
            lines.append("Line %s" % (i + 1))
        paginator = Paginator(lines, 10)
        page = self.request.GET.get("page")
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context["lines"] = show_lines
        return context

class MiscView(TemplateView):
    template_name = "shop/misc.html"

class SBAdminHomeView(TemplateView):
    template_name = "sb-admin/index.html"

class SBAdminExternoView(TemplateView):
    template_name = "sb-admin/externo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lista = Externo.objects.all()
        context['num_exte'] = lista.count()
        context['lista'] = lista
        context['salida'] = None
        return context

class SBAdminExternoImportar(TemplateView):
    template_name = "sb-admin/externo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        externo.importar()
        externo.save()
        context['salida'] = {'estado': 'success',
            'txto': 'Fichero IMPORTADO con exito',
            }
        context['lista'] = Externo.objects.all()
        return context

class SBAdminConfigView(TemplateView):
    template_name = "sb-admin/configuracion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista'] = Configuracion.objects.all()
        context['salida'] = ''
        return context

class SBAdminConfigDesactivar(TemplateView):
    template_name = "sb-admin/configuracion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = get_object_or_404(Configuracion, pk=kwargs['pk'])
        config.desactivar()
        context['lista'] = Configuracion.objects.all()
        context['salida'] = None
        return context

class SBAdminConfigDesactivarRedirectView(RedirectView):
    permanent = True
    query_string = True
    pattern_name = 'config_desactivar'

    def get_redirect_url(self, *args, **kwargs):
        #config = get_object_or_404(Configuracion, pk=kwargs['pk'])
        #config.desactivar()
        return super(SBAdminConfigDesactivarRedirectView).get_redirect_url(*args, **kwargs)

def config_desactivar(request,pk):
    config = get_object_or_404(Configuracion, pk=pk)
    config.desactivar()
    return HttpResponseRedirect('/sb-admin/config/')

class SBAdminMyURLsView(TemplateView):
    template_name = "sb-admin/myurls.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista'] = MyURLs.objects.all()
        context['salida'] = None
        return context

class SBAdminProductView(TemplateView):
    template_name = "sb-admin/productos.html"

    def get_context_data(self, **kwargs):
        prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
        context = super(SBAdminProductView, self).get_context_data(**kwargs)
        lista = Product.objects.all()
        paginator = Paginator(lista, prod_page)
        page = self.request.GET.get("page")
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context['num_prod'] = lista.count()
        context['num_pages'] = paginator.num_pages
        context["lines"] = show_lines
        context['lista'] = paginator.get_page(page)
        return context

class SBAdminCategoryView(TemplateView):
    template_name = "sb-admin/categorias.html"

    def get_context_data(self, **kwargs):
        cate_page = get_object_or_404(Configuracion, variable='cate_page').get_valor_int()
        context = super(SBAdminCategoryView, self).get_context_data(**kwargs)
        if 'slug' in kwargs:
            parent=Category.objects.filter(slug=kwargs['slug'])[0] 
        else:
            parent = None
        lista = Category.objects.filter(parent=parent)
        paginator = Paginator(lista, cate_page)
        page = self.request.GET.get("page")
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context['num_cate'] = lista.count()
        context['num_pages'] = paginator.num_pages
        context["lines"] = show_lines
        context['lista'] = paginator.get_page(page)
        return context

def catego_desactivar(request,pk):
    catego = get_object_or_404(Category, pk=pk)
    catego.desactivar()
    return HttpResponseRedirect('/sb-admin/categorias/')

def procesar_productos(root,insertar=False):
    if not root:
        return { 'retorno': -1, 'salida': 'no root' }
    limite = get_object_or_404(Configuracion, variable='product_limite').get_valor_int()
    iva_21 = get_object_or_404(Configuracion, variable='iva').get_valor_dec()
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    error=0
    for prod in root.findall('product'):
        if actualizado>limite:
            break
        ref = prod.find('public_id').text
        updated = parse_datetime(prod.find('updated').text)
        try:
            p = Product.objects.get(ref=ref)
            encontrado=encontrado+1
        except ObjectDoesNotExist as e:
            #Nuevo producto añadido                
            p = Product(ref=ref,updated=datetime(1900, 1, 1, 0, 0))
            nuevo=nuevo+1
        if p.updated < updated or insertar:
            try:
                if prod.find('title').text:
                    p.name = prod.find('title').text                
                else:
                    if prod.find('description').text:
                        p.name = prod.find('description').text
                    else:    
                        if prod.find('internationalization/title/value').text:
                            p.name = prod.find('internationalization/title/value').text
                        else: 
                            if prod.find('internationalization/description/value').text:
                                p.name = prod.find('internationalization/description/value').text
                            else: 
                                p.name = p.ref
                p.description = p.name
                p.slug = slugify(p.name+' '+p.ref)
                p.available = prod.find('available').text  
                p.product_url = prod.find('product_url').text 

                p.vat = Decimal(prod.find('vat').text)
                iva=1+(p.vat/100)
                p.cost_price = Decimal(prod.find('cost_price').text)
                p.pvp=p.calculate_pvp()
                aux = Decimal(prod.find('price').text)
                p.price = aux*iva
                aux = Decimal(prod.find('recommended_retail_price').text)
                p.recommended_retail_price = aux*iva                       
                aux = Decimal(prod.find('default_shipping_cost').text)
                p.default_shipping_cost = Decimal(aux*(1+iva_21/100)).quantize(Decimal('.01'), rounding=ROUND_UP)+Decimal(0.50)

                p.updated = updated       
                p.html_description = prod.find('html_description').text
                p.delivery_desc = prod.find('delivery_desc').text
                
                if prod.find('unit_of_measurement').text=='units':
                    p.unit_of_measurement = 'unidad/es'
                else:
                    p.unit_of_measurement = prod.find('unit_of_measurement').text
                p.release_date = prod.find('release_date').text
                p.destocking = prod.find('destocking').text   
                p.sale = prod.find('sale').attrib['value']
                p.new = prod.find('new').attrib['value']
                #<stock><location path="General">50</location></stock>
                stock = prod.find('stock')
                p.stock = stock.find('location').text
                p.save() #created_date,               
                actualizado=actualizado+1                 
            except  IntegrityError as e:
                print('INTEGRITYERROR REF: {0} PRICE: {1} ERROR: {2}'.format(p.ref,p.price,e)) 
                #ET.dump(prod)
                error=error+1  
        n=n+1              
    return {
        'retorno': actualizado, 
        'salida': 'Productos Procesados: '+str(n)
            +'<br> Encontrados: '+str(encontrado)
            +'<br> Nuevos: '+str(nuevo)
            +'<br> Actualizados: '+str(actualizado)
            +'<br> Errores: '+str(error)
            +'<br> Total: '+str(encontrado+nuevo)
        }

class SBAdminExternoProcesarProductos(TemplateView):
    template_name = "sb-admin/externo.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_productos(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        #messages.info(self.request, "SALIDA"+str(salida['retorno'])+' '+salida['salida'])
        context['salida'] = {
            'estado': estado,
            'txto': 'Fichero PROCESADO con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def procesar_categorias(root):
    if not root:
        return { 'retorno': -1, 'salida': 'no root' }
    limite = get_object_or_404(Configuracion,variable='categoria_limite').get_valor_int()
    varios = get_object_or_404(Category, name='Varios', parent=None)
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    error=0
    for prod in root.findall('product'):   
        if nuevo>limite:
            break   
        ref = prod.find('public_id').text
        if prod.find('categories'):
            try:
                p = Product.objects.get(ref=ref)
            except ObjectDoesNotExist as e:
                error=error+1
            for categoria in prod.find('categories'):                    
                cat_jerarquia = categoria.text
                parent=None
                for cat_name in cat_jerarquia.split('|'):
                    parent_ppal=parent
                    if cat_name:
                        try:
                            cat = Category.objects.get(name=cat_name, parent=parent)
                            encontrado=encontrado+1
                        except ObjectDoesNotExist as e: 
                            #Nuevo añadido                
                            cat = Category(name=cat_name, slug=slugify(cat_name), parent=parent)
                            cat.save()
                            nuevo=nuevo+1                             
                        parent = cat       
                #name_ppal = categoria.attrib['ref'] 
                if p:
                    p.categories.add(cat)
                    p.save()
                else:
                    error=error+1         
                cat.gesioid = categoria.attrib['gesioid']
                cat.save() 
            if p:
                p.category = cat
                p.save()
            else:
                error=error+1 
        n=n+1         
    return {
        'retorno': nuevo, 
        'salida': 'Productos Procesados: '+str(n)
            +'<br> Categorias Encontradas: '+str(encontrado)
            +'<br> Nuevos: '+str(nuevo)
            +'<br> Actualizadas: '+str(actualizado)
            +'<br> Errores: '+str(error)
            +'<br> Total: '+str(encontrado+nuevo)
        }

class SBAdminExternoProcesarCategorias(TemplateView):
    template_name = "sb-admin/externo.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_categorias(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        #messages.info(self.request, "SALIDA"+str(salida['retorno'])+' '+salida['salida'])
        context['salida'] = {
            'estado': estado,
            'txto': 'Fichero PROCESADO con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def cron(request):
    run_cron = get_object_or_404(Configuracion, variable='run_cron')
    if run_cron.activo:
        ext = get_object_or_404(Externo, name='Productos de DreamLove')
        tree=ET.parse(ext.path())
        root=tree.getroot() 
        if not procesar_productos(root).get('retorno'): 
            if not procesar_categorias(root).get('retorno'): 
                #if not procesar_imagenes(root).get('retorno'):  
                    #if not procesar_imagenes(root).get('retorno'):  
                ext.importar()
                salida='importado'
                    #else:
                        #salida=-1
                #else:
                    #salida=-2
            else:
                salida='categorías'
        else:
            salida='productos'
        #ext.n_productos = Product.objects.all().count()
        #ext.n_fabricantes = Fabricante.objects.all().count()
        #ext.n_imagenes = Imagen.objects.all().count()
        #ext.n_categorias = Category.objects.all().count()
        #ext.save()
    else:
        salida='inactivo'
    return HttpResponse('ESTADO: '+salida)

class SBAdminProductFichaView(FormView):
    template_name = "shop/form.html"
    form_class = ContactForm

class SBAdminTablesView(TemplateView):
    template_name = "sb-admin/tables.html"

class SBAdminFormsView(TemplateView):
    template_name = "sb-admin/forms.html"
