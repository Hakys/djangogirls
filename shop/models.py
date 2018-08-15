import pytz
from datetime import datetime
from decimal import *
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from urllib.error import URLError, HTTPError 
from urllib.request import Request, urlopen

fs = FileSystemStorage(location=settings.STATIC_ROOT+'\store')

class Configuracion(models.Model):
    variable = models.CharField(default='', max_length=50, null=False, unique=True)
    valor = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        if self.activo: 
            activo='Si' 
        else: 
            activo='No'
        valor=''
        if self.valor: 
            valor=': '+self.valor   
        return self.variable+valor+' ('+activo+')'
    
    def desactivar(self):
        self.activo =not self.activo
        self.save()
        return self.activo

    def get_valor_int(self):
        if self.activo:
            return int(self.valor)
        else:
            return False

    def get_valor(self):
        if self.activo:
            return str(self.valor)
        else:
            return False
 
    def get_valor_dec(self):
        if self.activo:
            return Decimal(self.valor)
        else:
            return False

class Externo(models.Model): 
    name = models.CharField(default='', max_length=50)
    url = models.URLField(default='', max_length=100, unique=True)
    file = models.FileField(storage=fs, null=True)
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Creación')  
    updated_date = models.DateTimeField(default=datetime(1900, 1, 1, 0, 0), verbose_name='Última Actualización')
    
    def __str__(self):
        return self.name+' '+self.file.name+' ('+str(self.updated_date)+')'
    
    def importar(self):
        try:
            response = urlopen(self.url)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: '+e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: '+e.reason)
        else:      
            fecha = datetime.now().strftime("%Y%m%d-%H%M")
            extension = self.url.split('.')[-1]
            self.file.save(self.name+'_'+fecha+'.'+extension, response)    
            self.updated_date=timezone.now()
            #Product.objects.all().update(updated=datetime.min)
            self.save()   

    def path(self):
        return self.file.path

class MyURLS(models.Model): 
    name = models.CharField(default='', max_length=50)
    url = models.URLField(default='', max_length=180, unique=True)  
    usuario = models.CharField(default='', max_length=128, null=True)
    password = models.CharField(default='', max_length=128, null=True)  
    
    def __str__(self):
        return self.name+' ('+self.url+')'