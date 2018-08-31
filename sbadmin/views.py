# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import operator
import xml.etree.ElementTree as ET
from .filters import *
from .forms import *
from shop.models import *
from decimal import *
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, IntegrityError
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.http import *
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views import View
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView

class HomeView(TemplateView):
    template_name = "sbadmin/index.html"

class ConfigView(TemplateView):
    template_name = "sbadmin/configuracion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista'] = Configuracion.objects.all()
        context['num_config'] = Configuracion.objects.all().count
        context['salida'] = ''
        return context
        
def config_desactivar(request,pk):
    config = get_object_or_404(Configuracion, pk=pk)
    config.desactivar()
    return HttpResponseRedirect('/sbadmin/config/')

class ExternoView(TemplateView):
    template_name = "sbadmin/externo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['run_cron'] = get_object_or_404(Configuracion, variable='run_cron')
        lista = Externo.objects.all()
        context['num_exte'] = lista.count()
        context['lista'] = lista
        #Model Resumen
        context['n_externo']=Externo.objects.all().count
        context['n_configuracion']=Configuracion.objects.all().count
        context['n_myurls']=MyURLs.objects.all().count
        context['n_product']=Product.objects.all().count
        context['n_category']=Category.objects.all().count
        context['n_marcas']=Category.objects.filter(parent__name="Marcas").count
        context['n_imagenes']=Imagen.objects.all().count
        context['salida'] = None
        return context

class ExternoImportar(ExternoView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        externo.importar()
        externo.save()
        context['salida'] = {
            'estado': 'success',
            'title': 'IMPORTAR FICHERO',
            'txto': 'Fichero IMPORTADO con Éxito',
            'detail': '',
            }
        context['lista'] = Externo.objects.all()
        return context

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

                if insertar: p.updated = timezone.now()
                else: p.updated = updated       
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
                error+=1  
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

class ExternoProcesarProductos(ExternoView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_productos(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        context['salida'] = {
            'estado': estado,
            'title': 'IMPORTAR PRODUCTOS',
            'txto': 'Productos IMPORTADOS con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def procesar_categorias(root):
    if not root: return { 'retorno': -1, 'salida': 'no root' }
    limite = get_object_or_404(Configuracion,variable='categoria_limite').get_valor_int()
    varios = get_object_or_404(Category, name='Varios', parent=None)
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    error=0
    for prod in root.findall('product'):   
        if nuevo>limite: break   
        ref = prod.find('public_id').text
        if prod.find('categories'):
            try:
                p = Product.objects.get(ref=ref)
            except ObjectDoesNotExist:
                error+=1
                break
            for categoria in prod.find('categories'):                    
                cat_jerarquia = categoria.text
                parent=None
                for cat_name in cat_jerarquia.split('|'):
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
                error+=1 
        n=n+1         
    return {
        'retorno': nuevo, 
        'salida': 'Productos Procesados: '+str(n)
            +'<br> Categorías Encontradas: '+str(encontrado)
            +'<br> Nuevos: '+str(nuevo)
            +'<br> Actualizadas: '+str(actualizado)
            +'<br> Errores: '+str(error)
            +'<br> Total: '+str(encontrado+nuevo)
        }

class ExternoProcesarCategorias(ExternoView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_categorias(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        context['salida'] = {
            'estado': estado,
            'title': 'IMPORTAR CATEGORÍAS',
            'txto': 'Catégorias IMPORTADAS con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def procesar_fabricantes(root):
    if not root: return { 'retorno': -1, 'salida': 'no root' }
    limite = get_object_or_404(Configuracion,variable='fabricante_limite').get_valor_int()
    marcas = get_object_or_404(Category, name='Marcas', parent=None)
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    error=0
    for prod in root.findall('product'):   
        if nuevo>limite: break   
        ref = prod.find('public_id').text
        try:
            p = Product.objects.get(ref=ref)
        except ObjectDoesNotExist:
            error+=1
            break 
        #<brand_hierarchy><![CDATA[REAL ROCK|REALROCK 100% FLESH]]></brand_hierarchy>      
        try:
            fab_jerarquia=prod.find('brand_hierarchy').text    
            fab_parent = marcas
            for fab_name in fab_jerarquia.split('|'):
                if fab_name:
                    try:
                        fab = Category.objects.get(name=fab_name, parent=fab_parent)
                        encontrado=encontrado+1
                    except ObjectDoesNotExist: 
                        #Nuevo añadido                
                        fab = Category(name=fab_name, slug=slugify(fab_name), parent=fab_parent)
                        fab.save()
                        nuevo=nuevo+1  
                else:
                    fab=marcas
                    error=error+1
                if p:
                    p.categories.add(fab)
                    p.save()
                else:
                    error=error+1 
                fab_parent = fab  
        except:     
            error+=1
        '''
        #<brand><![CDATA[REALROCK 100% FLESH]]></brand> 
        if prod.find('brand'):
            fab_name = prod.find('brand').text
            #fab_parent = marcas
            try:
                fab = Category.objects.get(name=fab_name, parent=fab_parent)
                encontrado=encontrado+1
            except ObjectDoesNotExist: 
                #Nuevo añadido                
                fab = Category(name=fab_name, slug=slugify(fab_name), parent=fab_parent)
                fab.save()
                nuevo+=1
        else:
            fab=marcas 
        '''
        if p:        
            p.fabricante = fab
            p.save()          
        n=n+1        
    return {
        'retorno': nuevo, 
        'salida': 'Productos Procesados: '+str(n)
            +'<br> Fabricantes Encontrados: '+str(encontrado)
            +'<br> Nuevos: '+str(nuevo)
            +'<br> Actualizados: '+str(actualizado)
            +'<br> Errores: '+str(error)
            +'<br> Total: '+str(encontrado+nuevo)
        }

class ExternoProcesarFabricantes(ExternoView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_fabricantes(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        #messages.info(self.request, "SALIDA"+str(salida['retorno'])+' '+salida['salida'])
        context['salida'] = {
           'estado': estado,
            'title': 'IMPORTAR FABRICANTES Y MARCAS',
            'txto': 'Fabricantes y Marcas IMPORTADOS con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def procesar_imagenes(root,insertar=False):
    if not root: return { 'retorno': -1, 'salida': 'no root' }
    limite = get_object_or_404(Configuracion,variable='imagen_limite').get_valor_int()
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    error=0
    for prod in root.findall('product'):   
        #ref = prod.find('public_id').text     
        if nuevo>limite: break    
        #else: print(prod.find('public_id').text)
        #updated = parse_datetime(prod.find('updated').text)
        try:
            p = Product.objects.get(ref=prod.find('public_id').text)
        except:
            error+=1         
            break             
        #if insertar:  #Imagen.objects.filter(ref=p.ref).delete()       
        for image in prod.find('images'):             
            #url = image.find('src').text                   
            #if urlopen(url): 
            try:
                img = Imagen.objects.get(url=image.find('src').text)
                encontrado+=1
            except:
                #Nueva imagen añadida 
                img = Imagen(url=image.find('src').text)  
                #print(prod.find('public_id').text)  
                nuevo+=1                        
            #if insertar: img.image.delete()          
            img.name = p.name      
            #img.name = image.find('name').text
            img.preferred = image.get('preferred')       
            img.save()     
            p.imagenes.add(img) 
        p.save()
        n=n+1               
    return {
        'retorno': nuevo, 
        'salida': 'Productos Procesados: '+str(n)
            +'<br> Imagenes Encontrados: '+str(encontrado)
            +'<br> Nuevos: '+str(nuevo)
            +'<br> Actualizados: '+str(actualizado)
            +'<br> Errores: '+str(error)
            +'<br> Total: '+str(encontrado+nuevo)
    }

class ExternoProcesarImagenes(ExternoView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        externo = get_object_or_404(Externo, pk=kwargs['pk'])
        context['tamano'] = externo.file.size/1048576
        tree = ET.parse(externo.path()) 
        root = tree.getroot() 
        salida = procesar_imagenes(root)
        if salida['retorno']: estado = 'success'
        else: estado = 'danger'
        #messages.info(self.request, "SALIDA"+str(salida['retorno'])+' '+salida['salida'])
        context['salida'] = {
           'estado': estado,
            'title': 'IMPORTAR IMAGENES',
            'txto': 'Imagenes IMPORTADAS con Éxito',
            'detail': salida['salida'],
            }
        context['lista'] = Externo.objects.all()
        return context

def cron(request):
    run_cron = get_object_or_404(Configuracion, variable='run_cron')
    salida='[ '
    if run_cron.activo:
        ext = get_object_or_404(Externo, name='Productos de DreamLove')
        tree=ET.parse(ext.path())
        root=tree.getroot() 
        if not procesar_productos(root).get('retorno'): 
            if not procesar_categorias(root).get('retorno'): 
                if not procesar_fabricantes(root).get('retorno'):  
                    if not procesar_imagenes(root).get('retorno'):  
                        ext.importar()
                        salida+='fichero '
                    else:
                        salida+='imagenes '
                else:
                    salida+='fabricantes '
            else:
                salida+='categorías '
        else:
            salida+='productos '
        #ext.n_productos = Product.objects.all().count()
        #ext.n_fabricantes = Fabricante.objects.all().count()
        #ext.n_imagenes = Imagen.objects.all().count()
        #ext.n_categorias = Category.objects.all().count()
        #ext.save()
    else:
        salida+='inactivo'
    return HttpResponse('ESTADO: '+salida+']')