from django.urls import path
from . import views

urlpatterns = [
    # Principal
    path('', views.principal, name='principal'),

    # Autenticação
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='clientes_lista'),
    path('clientes/novo/', views.ClienteCreateView.as_view(), name='cliente_criar'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_editar'),
    path('clientes/<int:pk>/deletar/', views.ClienteDeleteView.as_view(), name='cliente_deletar'),

    # Funcionários (Acesso Restrito)
    path('funcionarios/', views.FuncionarioListView.as_view(), name='funcionarios_lista'),
    path('funcionarios/novo/', views.FuncionarioCreateView.as_view(), name='funcionario_criar'),
    path('funcionarios/<int:pk>/editar/', views.FuncionarioUpdateView.as_view(), name='funcionario_editar'),
    path('funcionarios/<int:pk>/deletar/', views.FuncionarioDeleteView.as_view(), name='funcionario_deletar'),

    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produtos_lista'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_criar'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_editar'),
    path('produtos/<int:pk>/deletar/', views.ProdutoDeleteView.as_view(), name='produto_deletar'),

    # Tipos de Produto
    path('tipos/', views.TipoListView.as_view(), name='tipos_lista'),
    path('tipos/novo/', views.TipoCreateView.as_view(), name='tipo_criar'),
    path('tipos/<int:pk>/editar/', views.TipoUpdateView.as_view(), name='tipo_editar'),
    path('tipos/<int:pk>/deletar/', views.TipoDeleteView.as_view(), name='tipo_deletar'),
    
    # AJAX para criar tipo rápido na tela de produto
    path('ajax/criar-tipo/', views.criar_tipo_ajax, name='criar_tipo_ajax'),

    # Pedidos
    path('pedidos/', views.PedidoListView.as_view(), name='pedidos_lista'),
    path('pedidos/novo/', views.PedidoCreateView.as_view(), name='pedido_novo'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detalhe'),
    path('pedidos/<int:pk>/deletar/', views.PedidoDeleteView.as_view(), name='pedido_delete'),

    # Itens do Pedido
    path('pedidos/<int:pk>/adicionar-item/', views.PedidoItemCreateView.as_view(), name='pedido_add_item'),
    path('pedidos/item/<int:pk>/deletar/', views.PedidoItemDeleteView.as_view(), name='remover_item_pedido'),
]