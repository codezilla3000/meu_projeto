from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Cliente, Funcionario, Produto, Tipo, Pedido, PedidoItem, Estoque

# --- CONFIGURAÇÃO PARA ACOPLAR FUNCIONÁRIO AO USUÁRIO ---

class FuncionarioInline(admin.StackedInline):
    model = Funcionario
    fk_name = 'user'  # <--- ISSO RESOLVE O ERRO E202: Diz ao Django para usar o campo 'user' para o vínculo
    can_delete = False
    verbose_name_plural = 'Perfil de Funcionário (Sistema)'
    fields = ('tipo', 'nome', 'cpf', 'rg', 'email', 'telefone', 'idade')

class UserAdmin(BaseUserAdmin):
    inlines = (FuncionarioInline,)

# Re-registra o User padrão com a nossa nova configuração
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# --- CONFIGURAÇÕES DOS MODELOS EXISTENTES ---

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'idade')
    search_fields = ('nome', 'nome_normalizado', 'email')
    ordering = ('nome',)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'cpf', 'email', 'telefone')
    list_filter = ('tipo',)
    search_fields = ('nome', 'nome_normalizado', 'cpf', 'rg', 'email')
    ordering = ('nome',)

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'preco')
    search_fields = ('nome',)
    list_filter = ('tipo',)

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade', 'ativo')
    list_filter = ('ativo',)

class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'funcionario', 'status', 'total')
    list_filter = ('status',)
    inlines = [PedidoItemInline]
    readonly_fields = ('total',)