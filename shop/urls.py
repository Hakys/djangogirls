# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import views
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path

from shop.views import *
from sbadmin.views import *

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name="home"),
    url(r'^cron/$', views.cron, name='cron'),
    #url(r'^producto/(?P<slug>.+)/$', ProductDetailView.as_view(), name="product-detail"),
    #url(r'^categorias/$', ListingGridView.as_view(), name="listing-grid"),
    url(r'^categorias/(?P<jerarquia>.+)/(?P<slug>.+)/actualizar/$', views.product_actualizar, name="product_actualizar"),
    url(r'^categorias/(?P<jerarquia>.+)/(?P<slug>.+)/borrar/$', views.product_borrar, name="product_borrar"),
    url(r'^categorias/(?P<jerarquia>.+)/$', views.categorias, name="product-listado"),
    url(r'^categorias/$', views.todas_categorias, name="listing-grid"),
    url(r'^producto/(?P<slug>.+)/$', views.product_detail, name="product-detail"),
    #url(r"^productos/$", ProductListView.as_view(), name="productos"),
    #url(r"^productos/$", views.productos, name="productos"),
    #url(r"^productos/(?P<slug>.+)/$", views.product_ficha, name="producto-ficha"),
    #url(r'^search/$', views.autocompleteModel, name='search'),
    #url(r'^search-submit/$', views.SearchSubmitView.as_view(), name='search-submit'),
    #url(r'^search-ajax-submit/$', views.SearchAjaxSubmitView.as_view(), name='search-ajax-submit'),
    
    #url(r'^categorias/(?P<breadcrumb>.+)/(?P<ref>.+)/actualizar/$', views.product_actualizar, name="product_actualizar"),
    #url(r'^categorias/(?P<breadcrumb>.+)/(?P<ref>.+)/borrar/$', views.product_borrar, name="product_borrar"),
    #url(r"^sb-admin/$", SBAdminHomeView.as_view(), name="sbadmin_home"),
    #url(r"^sb-admin/myurls/$", SBAdminMyURLsView.as_view(), name="sbadmin_myurls"),
    #url(r"^sb-admin/productos/$", SBAdminProductView.as_view(), name="sbadmin_productos"),
    #url(r"^sb-admin/categorias/$", SBAdminCategoryView.as_view(), name="sbadmin_categorias"),
    #url(r'^sb-admin/categorias/(?P<pk>[0-9]+)/desactivar/$', views.catego_desactivar, name='catego_desactivar'),
    #url(r'^sb-admin/categorias/(?P<slug>.+)/$', SBAdminCategoryView.as_view(), name="sbadmin_categorias"),
    #Examples
    #url(r"^formset$", DefaultFormsetView.as_view(), name="formset_default"),
    #url(r"^form$", DefaultFormView.as_view(), name="form_default"),
    #url(r"^form_by_field$", DefaultFormByFieldView.as_view(), name="form_by_field"),
    #url(r"^form_horizontal$", FormHorizontalView.as_view(), name="form_horizontal"),
    #url(r"^form_inline$", FormInlineView.as_view(), name="form_inline"),
    #url(r"^form_with_files$", FormWithFilesView.as_view(), name="form_with_files"),
    #url(r"^pagination$", PaginationView.as_view(), name="pagination"),
    #url(r"^misc$", MiscView.as_view(), name="misc"),
    #url(r"^sb-admin/tables/$", SBAdminTablesView.as_view(), name="sbadmin_tables"),
    #url(r"^sb-admin/forms/$", SBAdminFormsView.as_view(), name="sbadmin_forms"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
