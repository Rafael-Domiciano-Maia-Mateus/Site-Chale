from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

    Retorna:
    Modelo: A instância do modelo `Foto`, representando uma foto na galeria.
    '''
    titulo = models.CharField(max_length=200, null=True, blank=True)
    imagem = models.ImageField(upload_to='fotos/')
    descricao = models.TextField(max_length=500, null=True, blank=True)
    data_upload = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Cliente(models.Model):
    '''
    Representa um cliente do sistema.

    Campos:
    - nome (CharField): Nome do cliente, até 200 caracteres.
    - email (CharField): Email do cliente, até 200 caracteres.
    - telefone (CharField): Telefone do cliente, até 200 caracteres.
    - id_sessao (CharField): Identificador da sessão, até 200 caracteres.
    - usuario (OneToOneField): Relacionamento com o modelo `User` do Django, pode ser nulo.

    Métodos:
    - __str__(): Retorna uma string representativa do cliente, com nome e ID de sessão.

    Retorna:
    Modelo: A instância do modelo `Cliente`.
    '''
    nome = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=200, null=True, blank=True)
    id_sessao = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Nome: {self.nome}, ID Sessão: {self.id_sessao}'


class Chale(models.Model):
    '''
    Representa os chalés no sistema.

    Campos:
    - nomeChale (Charfield): Nome do chalé, até 200 caracteres.
    - preco (DecimalField): Preço do chalé, até 10 digitos, 2 decimais.
    - taxa: (DecimalField): Taxa a ser paga, até 10 digitos, 2 dicimais.
    - descricao (Charfield): Descrição dos chalés, até 500 caracteres.
    - max_pessoas (IntegerField): Máximo de pessoas por chalé.
    - ativo (BooleanField): Ativo para locações.

    Métodos:
    - __str__(): Retorna uma string representativa do nome do chalé.

    Retorna:
    - A instância do modelo `Chele`, representando um chalé no sistema.
    '''
    nomeChale = models.CharField(max_length=200, null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    taxa = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=500, null=True, blank=True)
    max_pessoas = models.IntegerField()  
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nomeChale


class Reserva(models.Model):
    '''
    Representa uma reserva no sistema.

    Campos:
    - cliente (ForeignKey): Pega o cliente na tabela Cliente.
    - chale (ForeignKey): Pega o chalé na tabela Chale.
    - checkin (DateField): Data de entrada.
    - checkout (DateField): Data de saída.
    - quantidadePessoas (IntegerField): Quantidade de pessoas (O limite depende do chalé).
    - finalizado (BooleanField): Verifica se a reserva já foi finalizada.
    - codigo_transacao (CharField): Código de transação.
    - data_finalizacao (DateField): Data que a reserva foi finalizada.
    - telefone (CharField): Telefone do cliente.

    Métodos:
    - __str__(): Retorna uma string representativa do nome do cliente, chalé e data de finalização.
    - chaleAtivo: Verifica se o chalé selecionado pelo cliente está ativo para locação.
    - precoTotal: Calcula o preço total da reserva baseado na quantidade de diárias + a taxa.
    - clean: Verifica se a data de checkout é posterior a data de checkin.
    - save: Salvar as informações.

    Retorna:
    - A instância do modelo `Reserva`, representando uma reserva realizada pelo usuário.
    '''
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    chale = models.ForeignKey(Chale, on_delete=models.CASCADE)  
    checkin = models.DateField()
    checkout = models.DateField()
    quantidadePessoas = models.IntegerField(default=1)
    finalizado = models.BooleanField(default=False)
    codigo_transacao = models.CharField(max_length=200, null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'Cliente: {self.cliente}, Chalé: {self.chale}, Data de Finalização: {self.data_finalizacao}'


    def chaleAtivo(self):
        if self.chale.ativo == False:
            raise ValidationError("Este chalé não está disponivel para locação")


    def precoTotal(self):   
        dias = (self.checkout - self.checkin).days
        if dias <= 0:
            return 0
        return (dias * self.chale.preco) + self.chale.taxa  

    

    def clean(self):
        if self.checkout <= self.checkin:
            raise ValidationError("A data de checkout deve ser posterior à de checkin.")
    

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ItemReserva(models.Model):
    '''
    Representa um chalé reservado em uma reserva.

    Campos:
    - chale (ForeignKey): Chalé relacionado à reserva.
    - pedido (ForeignKey): Reserva à qual o chalé está vinculado.

    Métodos:
    - __str__(): Retorna o chalé relacionado à reserva.
    - save(): Verifica se a quantidade de pessoas da reserva não excede o limite do chalé.

    Retorna:
    Modelo: A instância do modelo `ItemReserva`.
    '''
    chale = models.ForeignKey(Chale, null=True, blank=True, on_delete=models.SET_NULL)
    pedido = models.ForeignKey(Reserva, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.chale)
    
    def save(self, *args, **kwargs):
        if self.pedido.quantidadePessoas > self.chale.max_pessoas:
            raise ValueError(f"O chalé '{self.chale.nomeChale}' não suporta {self.pedido.quantidadePessoas} pessoas.")
        super().save(*args, **kwargs)
