# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.fields.files import FieldFile
from django.http import *
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView

from .forms import *
from .models import *

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
        context['lista'] = Externo.objects.all()
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
            'txto': 'Archivo importado con exito',
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

class SBAdminTablesView(TemplateView):
    template_name = "sb-admin/tables.html"
