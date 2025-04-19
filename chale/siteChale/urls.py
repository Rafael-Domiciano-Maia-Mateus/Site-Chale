from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),    
    path('register/', register, name="register"),
    path('homepage/', homepage, name="homepage"),
    path('minhaconta/', minha_conta, name="minha_conta"),
    path('ajuda/', ajuda, name='ajuda'),
    path('upload_foto/', upload_foto, name='upload_foto'),
    path('reservas/', reservas, name='reservas'),
    path('galeria/', galeria, name='galeria'),
]

