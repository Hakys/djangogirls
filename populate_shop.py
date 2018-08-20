import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')

import django
django.setup()

from shop.models import *
from django.utils.text import slugify

def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.
    '''
    python_pages = [
        {"title": "Official Python Tutorial", "url":"http://docs.python.org/2/tutorial/"},
        {"title":"How to Think like a Computer Scientist", "url":"http://www.greenteapress.com/thinkpython/"},
        {"title":"Learn Python in 10 Minutes", "url":"http://www.korokithakis.net/tutorials/python/"} ]

    django_pages = [
        {"title":"Official Django Tutorial", "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"},
        {"title":"Django Rocks", "url":"http://www.djangorocks.com/"},
        {"title":"How to Tango with Django", "url":"http://www.tangowithdjango.com/"} ]

    other_pages = [
        {"title":"Bottle", "url":"http://bottlepy.org/docs/dev/"},
        {"title":"Flask", "url":"http://flask.pocoo.org"} ]

    cats = {
        "Python": {"pages": python_pages}, 
        "Django": {"pages": django_pages}, 
        "Other Frameworks": {"pages": other_pages} 
    }
    '''
    shop_categories = [
        {"name": "Marcas", "parent": None},
        {"name": "Varios", "parent": None},
        {"name": "Ofertas", "parent": None},
        {"name": "Para Hombre", "parent": None},
        {"name": "Para Mujer", "parent": None},
        {"name": "Para Parejas", "parent": None},
        {"name": "Lista Negra", "parent": None},
    ]
    
    shop_configuracions = [
        {"variable": "product_limite",  "valor": "300", "activo": True},
        {"variable": "imagen_limite",   "valor": "400", "activo": True},
        {"variable": "fabricante_limite", "valor": "300", "activo": True},
        {"variable": "categoria_limite",  "valor": "300", "activo": True},
        {"variable": "prod_page",       "valor": "24",  "activo": True},
        {"variable": "cate_page",       "valor": "24",  "activo": True},
        {"variable": "prod_home",       "valor": "24",  "activo": True},
        {"variable": "run_cron",        "valor": "",    "activo": True},
        {"variable": "beneficio",       "valor": "58",  "activo": True},
        {"variable": "rec_equivalencia","valor": "52",  "activo": True},
        {"variable": "iva",             "valor": "21",  "activo": True},
    ]

    shop_externo =[
        {'name': 'Productos de DreamLove', 'url':'https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml'},
        {'name': 'Marcas de DreamLove', 'url':'https://store.dreamlove.es/UserFiles/Marcas__todos_.csv'},
        {'name': 'Categorías de DreamLove', 'url':'https://store.dreamlove.es/dyndata/exportaciones/csvzip/categories_1_50_c5717766e188bb03da6d308655f4d8dd.csv'},
    ]

    shop_myurls = [
        {"title": "GitHub Hakys",  "url": "https://github.com/Hakys", "usuario": "", "password": ""},
        {"title": "Apuntes-Web Bootstrap",  "url": "http://www.apuntes-web.es/tag/bootstrap/", "usuario": "", "password": ""},
        {"title": "GetBootstrap 4.0",  "url": "https://getbootstrap.com/docs/4.0/", "usuario": "", "password": ""},
        {"title": "GetBootstrap 3.3",  "url": "https://getbootstrap.com/docs/3.3/customize/", "usuario": "", "password": ""},
        {"title": "Dajngo Proyect 2.0",  "url": "https://docs.djangoproject.com/en/2.0/", "usuario": "", "password": ""},
        {"title": "DevCode Cursos",  "url": "https://devcode.la/cursos/", "usuario": "", "password": ""},
        {"title": "Beginner Guide Django",  "url": "https://simpleisbetterthancomplex.com/series/2017/09/25/a-complete-beginners-guide-to-django-part-4.html", "usuario": "", "password": ""},
        {"title": "LOUVIVA",  "url": "http://www.louviva.com/", "usuario": "", "password": ""},        
        {"title": "W3Schools Bootstrap 4",  "url": "https://www.w3schools.com/bootstrap4/", "usuario": "", "password": ""},
        {"title": "GRANTORRENT",  "url": "https://grantorrent.net/", "usuario": "", "password": ""},
        {"title": "ZOOGLE",  "url": "https://zooqle.com", "usuario": "", "password": ""},
        {"title": "TORRENTDOWNLOADS",  "url": "https://www.torrentdownloads.me/", "usuario": "", "password": ""},
        {"title": "Peliculas y Series",  "url": "https://peliculasyseries.org/", "usuario": "", "password": ""},
        {"title": "PHPAdmin Loading.es",  "url": "https://lin135.loading.es:8443/smb/database/list", "usuario": "", "password": ""},
        {"title": "SB Admin 2",  "url": "http://startbootstrap.com/template-overviews/sb-admin-2", "usuario": "", "password": ""},
        #{"title": "",  "url": "", "usuario": "", "password": ""},
    ]

    # If you want to add more catergories or pages,
    # add them to the dictionaries above.

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category.
    # if you are using Python 2.x then use cats.iteritems() see
    # http://docs.quantifiedcode.com/python-anti-patterns/readability/
    # for more information about how to iterate over a dictionary properly.

    print(' Categorías Antes: {0}'.format(Category.objects.all().count()))
    print(' Configuración Antes: {0}'.format(Configuracion.objects.all().count()))
    print(' Externo Antes: {0}'.format(Externo.objects.all().count()))
    print(' MyURLs Antes: {0}'.format(MyURLs.objects.all().count()))
    print("Processing Shop population script...")
    
    for cat in shop_categories:
        add_category(cat["name"],cat["parent"])
    for c in shop_configuracions:
        add_configuracion(c["variable"],c["valor"],c["activo"])
    for e in shop_externo:
        add_externo(e["name"],e["url"])
    for u in shop_myurls:
        add_myurls(u["title"],u["url"],u["usuario"],u["password"])
    
    # Print out the objects we have added.
    #for c in Configuracion.objects.all():
    #    print("{0} ".format(str(c)))
    
    #for c in Configuracion.objects.all():
    #    print("{0} ".format(str(c)))
    
    #for f in Fabricante.objects.all():
    #    print("{0} ".format(str(f)))

    #for cat in Category.objects.all():
    #    print("{0} ".format(str(cat)))

    print(' Categorías Después: {0}'.format(Category.objects.all().count()))
    print(' Configuración Después: {0}'.format(Configuracion.objects.all().count()))
    print(' Externo Después: {0}'.format(Externo.objects.all().count()))
    print(' MyURLs Después: {0}'.format(MyURLs.objects.all().count()))


def add_category(name, parent=None):
    obj = Category.objects.get_or_create(name=name, parent=parent)[0]
    obj.slug=slugify(name)
    if parent:
        try:
            obj.parent=Category.objects.get(slug=parent)[0]
        except:
            obj.parent=None
    else:
        obj.parent=None
    obj.save()
    return obj

def add_configuracion(variable, valor, activo=True):
    obj = Configuracion.objects.get_or_create(variable=variable)[0]
    obj.valor=valor
    obj.activo=activo
    obj.save()
    return obj

def add_externo(name, url):
    obj = Externo.objects.get_or_create(name=name, url=url)[0]
    obj.save()
    return obj

def add_myurls(name, url, usuario='', password=''):
    obj = MyURLs.objects.get_or_create(name=name, url=url, usuario=usuario, password=password)[0]
    obj.save()
    return obj
'''
for cat, cat_data in cats.items():
    c = add_cat(cat)
    for p in cat_data["pages"]:
        add_page(c, p["title"], p["url"])

# Print out the categories we have added.
for c in Category.objects.all():
    for p in Page.objects.filter(category=c):
        print("- {0} - {1}".format(str(c), str(p)))

def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    c.save()
    return c
'''
# Start execution here!
if __name__ == '__main__':
    print("Starting Shop population script...")
    populate()
