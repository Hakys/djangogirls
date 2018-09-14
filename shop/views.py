# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import operator
import xml.etree.ElementTree as ET
from .filters import *
from .forms import *
from .models import *
from decimal import *
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, IntegrityError
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.http import *
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import *
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views import View
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView
from sbadmin.views import *

# http://yuji.wordpress.com/2013/01/30/django-form-field-in-initial-data-requires-a-fieldfile-instance/
class FakeField(object):
    storage = default_storage

fieldfile = FieldFile(None, FakeField, "dummy.txt")

''' 
#modal.html
context['salida'] = {
    'estado': 'danger',
    'title': 'Mensaje del Sistema',
    'txto': 'Producto NO Encontrado',
    'detail': '',
    }
'''
class HomePageView(TemplateView):
    template_name = "shop/home.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        #header-main.html#
        context['select_categorias'] = Category.objects.filter(parent=None).order_by('name')
        
        #prod_list = Product.objects.all() 
        #prod_filter = ProductFilter(self.request.GET, queryset=prod_list)
        #context['filter']=prod_filter
        #messages.info(self.request, "hello http://example.com")
        
        return context

def todas_categorias(request, salida=[]):
    #header-main.html#
    select_categorias = Category.objects.filter(parent=None).order_by('name') 
    #listing-grid.html#
    product_set = Product.objects.all()
    #pagination.html#
    prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
    paginator = Paginator(product_set, prod_page)
    page = request.GET.get("page")
    if page:
        p_ini = int(page)-11
        if p_ini < 1: p_ini = 1
        p_fin = int(page)+11
        if p_fin > paginator.num_pages: p_fin = paginator.num_pages
    else:
        p_ini = 1
        if p_ini < 1: p_ini = 1
        p_fin = 11
        if p_fin > paginator.num_pages: p_fin = paginator.num_pages
    return render(request,'shop/listing-grid.html',{ 
        'select_categorias': select_categorias,
        'num_result': product_set.count(),
        'search': '',
        'sub_categories': select_categorias,
        'product_set': paginator.get_page(page),
        'p_range': range(p_ini,p_fin+1),
        'date_min': datetime(1900, 1, 1, 0, 0),
        'hoy': datetime.today(),
        
    })

def categorias(request, jerarquia, salida=[]):
    #header-main.html#
    select_categorias = Category.objects.filter(parent=None).order_by('name')

    category_slug = jerarquia.split('/')
    category_queryset = list(Category.objects.all())
    all_slugs = [ x.slug for x in category_queryset ]
    parent = None
    for slug in category_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Category,slug=slug,parent=parent)
        else:
            instance = get_object_or_404(Product,Q(ref=slug)|Q(slug=slug))
            '''
            instance = get_object_or_404(Product, slug=slug)
            breadcrumbs_link = instance.get_cat_list()
            category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
            breadcrumbs = zip(breadcrumbs_link, category_name)
            '''
            return product_detail(request, instance.slug, salida)
            #return render(request, "postDetail.html", {'instance':instance,'breadcrumbs':breadcrumbs})
    
    #filter-row.html - breadcrumb.html#
    breadcrumbs_link = parent.get_cat_list()
    category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, category_name)
    
    #pagination.html#
    product_set=parent.product_set.all()
    prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
    paginator = Paginator(product_set, prod_page)
    page = request.GET.get("page")
    if page:
        p_ini = int(page)-11
        if p_ini < 1: p_ini = 1
        p_fin = int(page)+11
        if p_fin > paginator.num_pages: p_fin = paginator.num_pages
    else:
        p_ini = 1
        if p_ini < 1: p_ini = 1
        p_fin = 11
        if p_fin > paginator.num_pages: p_fin = paginator.num_pages
    return render(request,'shop/listing-grid.html',{
        'select_categorias': select_categorias,
        'breadcrumbs': breadcrumbs,
        'sub_categories': parent.children.all(),
        'num_result':parent.product_set.all().count(),
        'search': parent.name,
        'hoy': datetime.today(),
        'date_min': datetime(1900, 1, 1, 0, 0),
        'product_set': paginator.get_page(page),
        'p_range': range(p_ini,p_fin+1),
    })

def product_detail(request, slug, salida=[]):
    try:
        product = Product.objects.get(Q(ref=slug)|Q(slug=slug))
    except:
        salida.append({'retorno': -1, 'salida': "Producto No Encontrado" })
        #return todas_categorias(request,salida)
        return redirect(todas_categorias)    
        #return productos(request, salida)

    #breadcrumb.html#
    breadcrumbs_link = product.get_cat_list()
    category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, category_name)
    
    #breadcrumb-fab.html#
    breadcrumbs_link_fab = product.get_fab_list()
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link_fab]
    breadcrumbs_fab = zip(breadcrumbs_link_fab, fabricante_name)


    #pvp=product.get_pvp()
    iva=Decimal(product.vat/100)
    beneficio = Configuracion.objects.get(variable='beneficio').get_valor_dec()
    rec_equivalencia = Configuracion.objects.get(variable='rec_equivalencia').get_valor_dec()
    
    req=Decimal(rec_equivalencia/1000)
    porc_benef=Decimal(beneficio/100)
    coste_total=product.cost_price+(product.cost_price*iva)+(product.cost_price*req)
    #'pvp':  coste_total/(1-porc_benef),
    #'price_iva': product.price*(1+iva),
    #'recommended_retail_price_iva': product.recommended_retail_price*(1+iva),
    #'default_shipping_cost_iva': product.default_shipping_cost,
    return render(request, 'shop/product-detail.html', {
        'porc_benef': porc_benef,
        'beneficio': (coste_total/(1-porc_benef))-coste_total,
        'hoy': datetime.today(),
        'date_min': datetime(1900, 1, 1, 0, 0),
        'ficha': product, 
        'breadcrumbs':breadcrumbs,
        'breadcrumbs_fab':breadcrumbs_fab,
        'salida':salida,
    })

def product_borrar(request, jerarquia, slug):
    instance = get_object_or_404(Product,Q(ref=slug)|Q(slug=slug))
    n,r=instance.delete()
    print(n,r)
    return HttpResponseRedirect('/categorias/'+jerarquia+'/')  

def product_actualizar(request, jerarquia, slug):
    externo = get_object_or_404(Externo, name='Productos de DreamLove')
    tree=ET.parse(externo.path())
    root=tree.getroot()
    product = Product.objects.filter(Q(ref=slug)|Q(slug=slug))
    lista=[p.ref for p in product]
    for prod in root.findall('product'):
        ref = prod.find('public_id').text
        if not ref in lista:
            root.remove(prod)
        #else: ET.dump(prod)
    if not root:
        print('Producto Borrado '+slug)
        product_borrar(request, jerarquia, slug)
    else:
        print('Producto Actualizado '+lista[0])
        procesar_productos(root,True)
        procesar_categorias(root)
        procesar_fabricantes(root)
        procesar_imagenes(root,True)
    
    #messages.info(self.request, "SALIDA: "+estado+' '+str(context['salida']))
    return HttpResponseRedirect('/categorias/'+jerarquia+'/'+slug)

'''
class ProductDetailView(TemplateView):
    template_name = "shop/product-detail.html"

class ListingGridView(TemplateView):
    template_name = "shop/listing-grid.html"


class ProductListView(TemplateView):
    template_name = "shop/product_grid.html"

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        
        lista = Product.objects.filter(imagenes__preferred=True)
        prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
        paginator = Paginator(lista, prod_page)
        page = self.request.GET.get("page")
        context['num_prod'] = lista.count()
        context['num_pages'] = paginator.num_pages
        context['hoy'] = datetime.today()
        context['date_min'] = datetime.min
        context['lista'] = paginator.get_page(page)
        return context
    
    def post(self, request):
        template = loader.get_template(self.template)
        query = request.POST.get('search', '')

        # A simple query for Item objects whose title contain 'query'
        items = Product.objects.filter(name__icontains=query)

        context = {'title': self.response_message, 'query': query, 'items': items}

        rendered_template = template.render(context, request)
        return HttpResponse(rendered_template, content_type='text/html') 
       
def productos(request,salida=[]):
    lista = Product.objects.filter(imagenes__preferred=True)
    prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
    paginator = Paginator(lista, prod_page)
    page = request.GET.get("page")
    
    return render(request, 'shop/product_grid.html',{
        'num_prod':lista.count(),
        'num_pages':paginator.num_pages,
        'hoy': datetime.today(),
        'date_min': datetime.min,
        'lista':paginator.get_page(page),
        'salida':salida,
    })

class ProductView(TemplateView):
    template_name = "shop/product_ficha.html"

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        slug=kwargs['slug']
        try:
            query = Product.objects.filter(Q(ref=slug)|Q(slug=slug))
        except:
        context['n_result']=query.count()
        if query.count() == 1:
            context['ficha'] = query
            return context
        else:
            return HttpResponseRedirect('productos')
            return context
            
def search(request):
    user_list = User.objects.all()
    user_filter = UserFilter(request.GET, queryset=user_list)
    return render(request, 'shop/user_list.html', {'filter': user_filter})

def autocompleteModel(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        #search_qs = Product.objects.filter(ref__startswith=q)
        search_qs = Product.objects.filter(ref__icontains=q)
        ''
                    Q(ref__contains=search_text) |
                    Q(title__contains=search_text) |
                    Q(description__contains=search_text) |
                    Q(html_description__contains=search_text)
                    )
         ''           
        results = []
        for r in search_qs:
            results.append(r.ref+'-'+r.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
    
from django.views.generic.base import View

from django.template import loader

class SearchSubmitView(View):
    template = 'shop/search_submit.html'
    response_message = 'This is the response'

    def post(self, request):
        template = loader.get_template(self.template)
        query = request.POST.get('search', '')

        # A simple query for Item objects whose title contain 'query'
        items = Product.objects.filter(name__icontains=query)

        context = {'title': self.response_message, 'query': query, 'items': items}

        rendered_template = template.render(context, request)
        return HttpResponse(rendered_template, content_type='text/html') 

class SearchAjaxSubmitView(SearchSubmitView):
    template = 'shop/search_results.html'
    response_message = 'This is the AJAX response'
''
class ProductView(SearchSubmitView):
    template = 'shop/product.html'
    response_message = 'This is the AJAX response'
''
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
        context = super(SBAdminProductView, self).get_context_data(**kwargs)
        #productos-sub#
        lista2 = Product.objects.filter(imagenes__preferred=True)
        prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
        paginator2 = Paginator(lista2, prod_page)
        page2 = self.request.GET.get("page2")
        context['num_prod'] = lista2.count()
        context['num_pages2'] = paginator2.num_pages
        context['lista2'] = paginator2.get_page(page2)
        return context

class ProductView(TemplateView):
    template_name = "shop/product.html"

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        slug=kwargs['slug']
        query = Product.objects.filter((Q(ref=slug)|Q(slug=slug)))#&Q(imagenes__preferred=True)
        if query.count() == 1:
            #product_ficha.html
            context['ficha'] = query
        else:
            #product_grid.html
            prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
            paginator = Paginator(query, prod_page)
            page = self.request.GET.get("page")
            context['num_prod'] = query.count()
            context['num_pages'] = paginator.num_pages
            context['lista'] = paginator.get_page(page)
        return context

def product_borrar(request, ref):
    n, resultado = Product.objects.filter(Q(ref=ref)|Q(slug=ref)).delete()
    return { 'retorno': n, 'salida': 'borrado/s '+str(resultado)}

def product_actualizar(request, breadcrumb, ref):
    externo = get_object_or_404(Externo, name='Productos de DreamLove')
    tree=ET.parse(externo.path())
    root=tree.getroot()
    product = Product.objects.filter(Q(ref=ref)|Q(slug=ref))
    lista=[p.ref for p in product]
    for prod in root.findall('product'):
        ref = prod.find('public_id').text
        if not ref in lista:
            root.remove(prod)
        #else: ET.dump(prod)
   
    if not root:
        print('Producto Borrado '+ref)
        product_borrar(request,ref)
    else:
        print('Producto Actualizado '+lista[0])
        procesar_productos(root,True)
        procesar_categorias(root)
        procesar_fabricantes(root)
        procesar_imagenes(root,True)
    
    #messages.info(self.request, "SALIDA: "+estado+' '+str(context['salida']))
    return HttpResponseRedirect('/categorias/'+breadcrumb+'/'+ref)

class SBAdminCategoryView(TemplateView):
    template_name = "sb-admin/categorias.html"

    def get_context_data(self, **kwargs):
        context = super(SBAdminCategoryView, self).get_context_data(**kwargs)
        parent = None
        cate_page = get_object_or_404(Configuracion, variable='cate_page').get_valor_int()
        if 'slug' in kwargs:
            slug_split = kwargs['slug'].split('/')
            cat_list = list(Category.objects.all())
            slug_list = [ x.slug for x in cat_list ]
            for slug in slug_split:
                if slug in slug_list:
                    parent = get_object_or_404(Category, slug=slug, parent=parent)
            breadcrumbs_link = parent.get_cat_list('/')
            name=parent.name
        else:
            breadcrumbs_link = ''
            name='Categorías'
        breadcumbs_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
        breadcrumbs = zip(breadcrumbs_link, breadcumbs_name)
        lista = Category.objects.filter(parent=parent)
        paginator = Paginator(lista, cate_page)
        page = self.request.GET.get("page")
        context['breadcrumbs'] = breadcrumbs
        context['cat_name'] = name
        context['lista'] = paginator.get_page(page)
        context['num_pages'] = paginator.num_pages
        context['num_cate'] = lista.count()
        #productos-sub#
        prod_page=get_object_or_404(Configuracion, variable='prod_page').get_valor_int()
        lista2 = Product.objects.filter(Q(category=parent)|Q(categories=parent)|Q(fabricante=parent)).distinct().filter(imagenes__preferred=True)
        paginator2 = Paginator(lista2, prod_page)
        page2 = self.request.GET.get("page2")
        context['num_prod'] = lista2.count()
        context['num_pages2'] = paginator2.num_pages
        context['lista2'] = paginator2.get_page(page2)
        return context

def catego_desactivar(request,pk):
    catego = get_object_or_404(Category, pk=pk)
    catego.desactivar()
    return HttpResponseRedirect('/sb-admin/categorias/')

class SBAdminProductFichaView(FormView):
    template_name = "shop/form.html"
    form_class = ContactForm

class SBAdminTablesView(TemplateView):
    template_name = "sb-admin/tables.html"

class SBAdminFormsView(TemplateView):
    template_name = "sb-admin/forms.html"
'''