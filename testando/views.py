from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import ProtectedError
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.core.exceptions import ValidationError
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .models import Cliente, Funcionario, Produto, Tipo, Pedido, PedidoItem, Estoque
from .forms import ProdutoForm, LoginForm, FuncionarioForm, PedidoItemForm

# -------------------------
# MIXINS DE PERMISSÃO
# -------------------------

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'perfil_funcionario') and 
                self.request.user.perfil_funcionario.tipo == 'admin')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Acesso restrito a Super Funcionários.")
            return redirect('principal')
        return super().handle_no_permission()

# -------------------------
# AUTENTICAÇÃO
# -------------------------

class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    def get_success_url(self):
        return reverse_lazy('principal')

class UserLogoutView(LogoutView):
    pass

# -------------------------
# PRINCIPAL
# -------------------------

@login_required
def principal(request):
    return render(request, "main/principal.html")

# -------------------------
# CLIENTES
# -------------------------

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/lista.html"
    context_object_name = "clientes"

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    fields = ["nome", "endereco", "idade", "email", "telefone"]
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes_lista")

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    fields = ["nome", "endereco", "idade", "email", "telefone"]
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes_lista")

class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = "clientes/confirm_delete.html"
    success_url = reverse_lazy("clientes_lista")

# -------------------------
# FUNCIONARIOS
# -------------------------

class FuncionarioListView(AdminRequiredMixin, ListView):
    model = Funcionario
    template_name = "funcionarios/lista.html"
    context_object_name = "funcionarios"

class FuncionarioCreateView(AdminRequiredMixin, CreateView):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = "funcionarios/form.html"
    success_url = reverse_lazy("funcionarios_lista")

class FuncionarioUpdateView(AdminRequiredMixin, UpdateView):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = "funcionarios/form.html"
    success_url = reverse_lazy("funcionarios_lista")

class FuncionarioDeleteView(AdminRequiredMixin, DeleteView):
    model = Funcionario
    template_name = "funcionarios/confirm_delete.html"
    success_url = reverse_lazy("funcionarios_lista")

# -------------------------
# PRODUTOS
# -------------------------

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "produtos/lista.html"
    context_object_name = "produtos"

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form.html"
    success_url = reverse_lazy("produtos_lista")

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form.html"
    success_url = reverse_lazy("produtos_lista")

class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model = Produto
    template_name = "produtos/confirm_delete.html"
    success_url = reverse_lazy("produtos_lista")

    def post(self, request, *args, **kwargs):
        produto = self.get_object()
        estoque = produto.estoques.first()
        if estoque and estoque.quantidade > 0:
            messages.error(request, f"O produto '{produto}' ainda possui estoque ({estoque.quantidade}).")
            return redirect(self.success_url)
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, f"Produto '{produto}' removido.")
            return response
        except ProtectedError:
            messages.warning(request, f"Produto '{produto}' vinculado a pedidos existentes.")
            return redirect(self.success_url)

# -------------------------
# TIPOS DE PRODUTO
# -------------------------

class TipoListView(LoginRequiredMixin, ListView):
    model = Tipo
    template_name = "tipos/lista.html"
    context_object_name = "tipos"

class TipoCreateView(LoginRequiredMixin, CreateView):
    model = Tipo
    fields = ["nome","descricao"]
    template_name = "tipos/form.html"
    success_url = reverse_lazy("tipos_lista")

class TipoUpdateView(LoginRequiredMixin, UpdateView):
    model = Tipo
    fields = ["nome","descricao"]
    template_name = "tipos/form.html"
    success_url = reverse_lazy("tipos_lista")

class TipoDeleteView(LoginRequiredMixin, DeleteView):
    model = Tipo
    template_name = "tipos/confirm_delete.html"
    success_url = reverse_lazy("tipos_lista")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Tipo excluído.")
        except ProtectedError:
            messages.error(request, "Tipo em uso por produtos cadastrados.")
        return redirect(self.success_url)

# -------------------------
# PEDIDOS E ITENS (FIX DO TYPEERROR)
# -------------------------

class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = "pedidos/lista.html"
    context_object_name = "pedidos"

class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    fields = ["cliente", "funcionario"]
    template_name = "pedidos/form.html"
    success_url = reverse_lazy("pedidos_lista")

class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = "pedidos/detalhe.html"

class PedidoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pedido
    template_name = "pedidos/confirm_delete.html"
    success_url = reverse_lazy("pedidos_lista")

class PedidoItemCreateView(LoginRequiredMixin, View):
    template_name = "pedidos/item_form.html"

    def get(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoItemForm()
        return render(request, self.template_name, {"form": form, "pedido": pedido})

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoItemForm(request.POST)
        
        # O form.is_valid() chama o clean() do forms.py que já trata o estoque
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.pedido = pedido
                    item.preco_unitario = item.produto.preco
                    # Salvamos diretamente sem chamar full_clean() para evitar o erro de NoneType
                    item.save()
                
                messages.success(request, f"{item.produto.nome} adicionado.")
                return redirect("pedido_detalhe", pk=pedido.pk)
            
            except ValidationError as e:
                # Caso o model ainda lance erro, mapeamos para o campo quantidade
                if hasattr(e, 'message_dict'):
                    for field, messages_list in e.message_dict.items():
                        target_field = field if field != '__all__' else 'quantidade'
                        for msg in messages_list:
                            form.add_error(target_field, msg)
                else:
                    form.add_error('quantidade', str(e))
            except Exception as e:
                form.add_error(None, f"Erro no processamento: {str(e)}")

        return render(request, self.template_name, {"form": form, "pedido": pedido})

class PedidoItemDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(PedidoItem, pk=pk)
        pedido_pk = item.pedido.pk
        item.delete()
        messages.success(request, "Item removido.")
        return redirect("pedido_detalhe", pk=pedido_pk)
@login_required
def criar_tipo_ajax(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        if nome:
            tipo = Tipo.objects.create(nome=nome, descricao=descricao)
            return JsonResponse({"id": tipo.id, "nome": tipo.nome})
        return JsonResponse({"error": "Nome obrigatório"}, status=400)
    return JsonResponse({"error": "Método negado"}, status=405)