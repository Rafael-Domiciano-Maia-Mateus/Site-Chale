from django import forms
from .models import Foto

class FotoForm(forms.ModelForm):
  '''
  Formulário para o upload de fotos, utilizando o modelo Foto.

  Esta classe é um formulário do tipo `ModelForm`, que é automaticamente gerado a partir do modelo `Foto`.
  Ela facilita a criação e validação de um formulário HTML para enviar as informações necessárias para a criação de uma nova foto no banco de 
  dados.

  Campos incluídos no formulário:
  - titulo: Um campo de texto para o título da foto.
  - imagem: Um campo de arquivo para a imagem da foto.
  - descricao: Um campo de texto para a descrição da foto.

  A classe FotoForm usa o modelo `Foto` para garantir que os dados sejam validados e salvos de forma consistente com o modelo do banco de dados.

  Parâmetros:
  Nenhum parâmetro adicional é necessário para criar uma instância deste formulário. O formulário pode ser instanciado diretamente com os dados da 
  requisição, como mostrado no `views.py`.

  Fluxo:
  1. Quando instanciado, o formulário automaticamente usa os campos definidos no modelo `Foto` para gerar os campos de entrada.
  2. O formulário pode ser validado, o que garante que os dados do título, imagem e descrição sejam preenchidos corretamente antes de serem salvos.
  3. Após a validação, o formulário salva a nova foto no banco de dados.

  Retorna:
  ModelForm: O formulário que pode ser utilizado para renderizar um formulário HTML em uma página e receber dados de um usuário.
  '''
  class Meta:
    model = Foto
    fields = ['titulo', 'imagem', 'descricao']
    