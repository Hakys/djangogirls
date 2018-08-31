from django.contrib.auth.models import User
from shop.models import *
import django_filters

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    ref = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    html_description = django_filters.CharFilter(lookup_expr='icontains')
    product_url = django_filters.CharFilter(lookup_expr='icontains')
    category__name = django_filters.CharFilter(lookup_expr='icontains')
    fabricante__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Product
        #fields = ['ref', 'name', 'description', 'html_description', 'product_url', ]
        fields = {
            'ref': ['contains'],
            
        }

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]