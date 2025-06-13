from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
    path('finalizar/<int:reserva_id>/', finalizar, name='finalizar'),
    path('verificar_disponibilidade/', verificar_disponibilidade, name='verificar_disponibilidade'),
    path('datas_indisponiveis/', datas_indisponiveis, name='datas_indisponiveis'),
    path('obter_max_pessoas/', obter_max_pessoas, name='obter_max_pessoas'),
    path('administracao/', administracao, name='administracao'),
    path('home_reservas/', home_reservas, name='home_reservas'),
    path('chat/', chat, name='chat'),
    path('NovoLogin/', NovoLogin, name='NovoLogin'),
    path('recuperarSenha/', recuperarSenha, name='recuperarSenha'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
