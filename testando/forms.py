from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Produto, Estoque, Funcionario, PedidoItem
from django.db import transaction

class ProdutoForm(forms.ModelForm):
    quantidade_estoque = forms.IntegerField(
        label="Quantidade em estoque",
        min_value=0,
        required=True,
        help_text="Quantidade inicial em estoque"
    )

    class Meta:
        model = Produto
        fields = ["nome", "tipo", "descricao", "preco"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            estoque = self.instance.estoques.first()
            self.fields["quantidade_estoque"].initial = estoque.quantidade if estoque else 0

    def save(self, commit=True):
        produto = super().save(commit=commit)
        estoque_qs = produto.estoques.all()
        if estoque_qs.exists():
            estoque = estoque_qs.first()
            estoque.quantidade = self.cleaned_data["quantidade_estoque"]
            estoque.save()
        else:
            Estoque.objects.create(
                produto=produto,
                quantidade=self.cleaned_data["quantidade_estoque"]
            )
        return produto

class FuncionarioForm(forms.ModelForm):
    username = forms.CharField(
        label="Login (Usuário)", 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Defina o login'})
    )
    password = forms.CharField(
        label="Senha", 
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Defina ou mude a senha'}),
        help_text="Ao editar: deixe em branco para manter a senha atual."
    )

    class Meta:
        model = Funcionario
        fields = ["nome", "tipo", "endereco", "idade", "cpf", "rg", "email", "telefone"]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_exists = User.objects.filter(username=username).exclude(pk=self.instance.user.pk if self.instance.user else None).exists()
        if user_exists:
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    @transaction.atomic
    def save(self, commit=True):
        funcionario = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not funcionario.user:
            novo_usuario = User.objects.create_user(
                username=username, 
                password=password if password else '123'
            )
            funcionario.user = novo_usuario
        else:
            funcionario.user.username = username
            if password: 
                funcionario.user.set_password(password)
            funcionario.user.save()

        if commit:
            funcionario.save()
        return funcionario

# --- FORMULÁRIO DE ITENS DO PEDIDO COM VALIDAÇÃO DE ESTOQUE ---
class PedidoItemForm(forms.ModelForm):
    class Meta:
        model = PedidoItem
        fields = ["produto", "quantidade"]
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get("produto")
        quantidade = cleaned_data.get("quantidade")

        if produto and quantidade:
            # Verifica o estoque total usando a property que você tem no Model Produto
            disponivel = produto.estoque_total 
            if quantidade > disponivel:
                # Vincula o erro diretamente ao campo 'quantidade', removendo o __all__
                self.add_error('quantidade', f"Estoque insuficiente para {produto.nome}. Disponível: {disponivel}")
        
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuário", widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Digite seu usuário'}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Digite sua senha'}))