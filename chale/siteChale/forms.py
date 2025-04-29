from django import forms
from .models import *
import re
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import date

class FotoForm(forms.ModelForm):
    '''
    Formulário para o upload de fotos, utilizando o modelo Foto.

    Este formulário é gerado automaticamente a partir do modelo `Foto`.
    Ele facilita a criação de um formulário HTML para o envio de informações
    necessárias para o cadastro de uma nova foto no banco de dados.

    Campos:
    - titulo: Campo de texto para o título da foto.
    - imagem: Campo de upload de imagem.
    - descricao: Campo de texto para a descrição da foto.

    Utilização:
    - Instanciar diretamente no `views.py`, passando `request.POST` e `request.FILES`.
    '''
    class Meta:
        model = Foto
        fields = ['titulo', 'imagem', 'descricao']


def validar_telefone(value):
    '''
    Validador de telefone personalizado.

    Valida se o telefone informado está no formato correto:
    (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.

    Parâmetros:
    - value (str): O valor do telefone a ser validado.

    Lança:
    - ValidationError: Caso o formato esteja incorreto.
    '''
    if not re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', value):
        raise ValidationError('Telefone inválido. Use o formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.')


class ReservaForm(forms.Form):
    '''
    Formulário de Reserva de Chalé.

    Este formulário gerencia o processo de reserva de chalés, incluindo a escolha do chalé,
    datas de check-in e checkout, telefone de contato e quantidade de pessoas.

    Campos:
    - chale: Campo de seleção de chalés disponíveis.
    - checkin: Data de entrada no chalé.
    - checkout: Data de saída do chalé.
    - telefone: Número de telefone do responsável pela reserva.
    - qtd_pessoas: Quantidade de pessoas hospedadas (definido dinamicamente).

    Validações:
    - Datas: Check-in posterior ao dia atual, checkout posterior ao check-in.
    - Limite de pessoas: Conforme regras específicas do chalé e capacidade máxima cadastrada.

    Utilização:
    - Instanciar diretamente no `views.py`, passar `request.POST` como argumento.
    '''
    chale = forms.ModelChoiceField(queryset=Chale.objects.all(), label='Chalé')
    checkin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    checkout = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    telefone = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        '''
        Inicializa o formulário.

        Se o chalé for selecionado, gera dinamicamente a lista de opções
        para a quantidade de pessoas baseada na capacidade máxima do chalé.
        '''
        super().__init__(*args, **kwargs)

        self.fields['qtd_pessoas'] = forms.ChoiceField(
            choices=[],  
            label='Quantidade de pessoas',
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        if 'chale' in self.data:
            chale_id = self.data.get('chale')
            try:
                chale = Chale.objects.get(id=chale_id)
                limite_maximo = chale.max_pessoas
                self.fields['qtd_pessoas'].choices = [(i, i) for i in range(1, limite_maximo + 1)]
            except (Chale.DoesNotExist, ValueError, TypeError):
                self.fields['qtd_pessoas'].choices = []


    def clean(self):
        '''
        Valida os campos do formulário.

        Regras de validação aplicadas:
        - Check-in deve ser após o dia atual.
        - Checkout deve ser após o check-in.
        - Quantidade de pessoas deve respeitar o limite personalizado e a capacidade máxima do chalé.

        Retorna:
        - dict: Dados limpos se todas as validações forem aprovadas.
        '''
        cleaned_data = super().clean()
        checkin = cleaned_data.get('checkin')
        checkout = cleaned_data.get('checkout')
        chale = cleaned_data.get('chale')
        qtd_pessoas = cleaned_data.get('qtd_pessoas')
        
        if not checkin:
            self.add_error('checkin', 'Informe uma data de check-in válida.')
        elif checkin <= date.today():
            self.add_error('checkin', 'A data de check-in deve ser posterior ao dia de hoje.')

        if not checkout:
            self.add_error('checkout', 'Informe uma data de checkout válida.')
        elif checkin and checkout and checkin >= checkout:
            self.add_error('checkout', 'A data de checkout deve ser posterior à de check-in.')

        if chale and qtd_pessoas:
            try:
                qtd_pessoas = int(qtd_pessoas)
                limite_personalizado = 6 if chale.id in [5, 10] else 4
                if qtd_pessoas > limite_personalizado:
                    self.add_error('qtd_pessoas', f'O chalé {chale.nomeChale} permite no máximo {limite_personalizado} pessoas.')

                if qtd_pessoas > chale.max_pessoas:
                    self.add_error('qtd_pessoas', f'O número de pessoas excede a capacidade máxima do chalé {chale.nomeChale} ({chale.max_pessoas} pessoas).')
            except (ValueError, TypeError):
                self.add_error('qtd_pessoas', 'Selecione uma quantidade de pessoas válida.')

        return cleaned_data
