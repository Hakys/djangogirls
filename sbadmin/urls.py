from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path

from sbadmin.views import *

urlpatterns = [
    url(r"^$", HomeView.as_view(), name="sbadmin_home"),
    url(r"^externo/$", ExternoView.as_view(), name="externo"),
    url(r'^externo/(?P<pk>[0-9]+)/importar/$', ExternoImportar.as_view(), name='externo_importar'),
    url(r'^externo/(?P<pk>[0-9]+)/procesar-productos/$', ExternoProcesarProductos.as_view(), name='procesar_productos'),
    url(r'^externo/(?P<pk>[0-9]+)/procesar-categorias/$', ExternoProcesarCategorias.as_view(), name='procesar_categorias'),
    url(r'^externo/(?P<pk>[0-9]+)/procesar-fabricantes/$', ExternoProcesarFabricantes.as_view(), name='procesar_fabricantes'),
    url(r'^externo/(?P<pk>[0-9]+)/procesar-imagenes/$', ExternoProcesarImagenes.as_view(), name='procesar_imagenes'),
    url(r"^config/$", ConfigView.as_view(), name="config"),
    url(r'^config/(?P<pk>[0-9]+)/desactivar/$', config_desactivar, name='config_desactivar'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  