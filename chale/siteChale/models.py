from django.db import models

# Create your models here.
class Foto(models.Model):
    '''
    Representa uma foto na galeria dos chalés.

    Este modelo é usado para armazenar informações sobre as fotos que serão exibidas na galeria, incluindo o título, imagem, descrição e a 
    data de upload.

    Campos:
    - titulo (CharField): O título da foto, com um comprimento máximo de 100 caracteres.
    - imagem (ImageField): O campo para armazenar a imagem da foto, com o caminho de upload definido para 'fotos/'.
    - descricao (TextField): Uma descrição opcional da foto, que pode ser deixada em branco.
    - data_upload (DateField): A data em que a foto foi carregada no sistema, preenchida automaticamente no momento do upload.

    Métodos:
    - __str__(): Retorna o título da foto, o que é útil para exibição e para identificar a instância de Foto no Django Admin.

    Fluxo:
    1. O título e a descrição são fornecidos pelo usuário.
    2. A imagem é carregada para o diretório especificado no campo `imagem`.
    3. A data de upload é automaticamente preenchida no momento do carregamento da foto.

    Retorna:
    Modelo: A instância do modelo `Foto`, representando uma foto na galeria.
    '''
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='fotos/')
    descricao = models.TextField(blank=True)
    data_upload = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo
