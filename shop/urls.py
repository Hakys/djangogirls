# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import views
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path

from .views import *

urlpatterns = [
    url(r"^$", HomePageView.as_view(), name="home"),
    
    url(r"^sb-admin/$", SBAdminHomeView.as_view(), name="sbadmin_home"),
    url(r"^sb-admin/externo/$", SBAdminExternoView.as_view(), name="sbadmin_externo"),
    url(r'^sb-admin/externo/(?P<pk>[0-9]+)/importar/$', SBAdminExternoImportar.as_view(), name='externo_importar'),
    url(r'^sb-admin/externo/(?P<pk>[0-9]+)/procesar-productos/$', SBAdminExternoProcesarProductos.as_view(), name='procesar_productos'),
    url(r'^sb-admin/externo/(?P<pk>[0-9]+)/procesar-categorias/$', SBAdminExternoProcesarCategorias.as_view(), name='procesar_categorias'),
    url(r'^cron/$', views.cron, name='cron'),
    url(r"^sb-admin/config/$", SBAdminConfigView.as_view(), name="sbadmin_config"),
    url(r'^sb-admin/config/(?P<pk>[0-9]+)/desactivar/$', views.config_desactivar, name='config_desactivar'),
    url(r'^sb-admin/config/(?P<pk>[0-9]+)/desactivar0/$', SBAdminConfigDesactivar.as_view(), name='config_desactivar0'),
    url(r'^sb-admin/config/(?P<pk>[0-9]+)/desactivar1/$', SBAdminConfigDesactivarRedirectView.as_view(), name='config_desactivar1'),
    url(r"^sb-admin/myurls/$", SBAdminMyURLsView.as_view(), name="sbadmin_myurls"),
    url(r"^sb-admin/productos/$", SBAdminProductView.as_view(), name="sbadmin_productos"),
    url(r"^sb-admin/categorias/$", SBAdminCategoryView.as_view(), name="sbadmin_categorias"),
    url(r'^sb-admin/categorias/(?P<pk>[0-9]+)/desactivar/$', views.catego_desactivar, name='catego_desactivar'),
    url(r'^sb-admin/categorias/(?P<slug>.+)/$', SBAdminCategoryView.as_view(), name="sbadmin_categorias"),
    #Examples
    url(r"^formset$", DefaultFormsetView.as_view(), name="formset_default"),
    url(r"^form$", DefaultFormView.as_view(), name="form_default"),
    url(r"^form_by_field$", DefaultFormByFieldView.as_view(), name="form_by_field"),
    url(r"^form_horizontal$", FormHorizontalView.as_view(), name="form_horizontal"),
    url(r"^form_inline$", FormInlineView.as_view(), name="form_inline"),
    url(r"^form_with_files$", FormWithFilesView.as_view(), name="form_with_files"),
    url(r"^pagination$", PaginationView.as_view(), name="pagination"),
    url(r"^misc$", MiscView.as_view(), name="misc"),
    url(r"^sb-admin/tables/$", SBAdminTablesView.as_view(), name="sbadmin_tables"),
    url(r"^sb-admin/forms/$", SBAdminFormsView.as_view(), name="sbadmin_forms"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
