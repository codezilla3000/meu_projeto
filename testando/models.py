from django.db import models, transaction
from core.models import BaseAuditModel # Model criado que herda models mas adiciona fatores de auditoria para registro em db e futuramente em sistema
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Função para filtrar as letras especiais antes de inserir no db
def normalizar_str(texto):
    if not texto:
        return ""
    mapa = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüç",
        "aaaaaeeeeiiiiooooouuuuc"
    )
    return texto.strip().lower().translate(mapa)

# -------------------------
# CLIENTES
# Requisitos: Nome não pode ser em branco, só pode ser registrado uma vez, campo nome será para exibição no sistema/django admin, nome_normalizado para registro
# no db para evitar qualquer erro de migração entre diferentes db, mesmo com endereço, idade precisa ser preenchido, com valor inteiro positivo entre 1 e 150, 
# Usei o tipo de dado EmailField que já faz validalções de formato, implementações futuras conterão verificações de existencia do e-mail de fato. telefone opcional
# mas se preenchido, sera entre 10~11 numeros
# -------------------------
class Cliente(BaseAuditModel):
    nome = models.CharField(max_length=100, blank=False, help_text="Preencha o nome.", unique=True)    
    nome_normalizado = models.CharField(max_length=100, editable=False, blank=True, db_index=True)    
    endereco = models.CharField(max_length=100, help_text="Preencha seu endereço")
    endereco_normalizado = models.CharField(max_length=100, editable=False, db_index=True, blank=True)
    idade = models.PositiveSmallIntegerField(help_text="Preencha a idade.", blank=False, validators=[MinValueValidator(1), MaxValueValidator(150)])
    email = models.EmailField(help_text="Preencha com um e-mail válido.", blank=True, null=True)
    telefone = models.CharField(max_length=11, blank=True, null=True, help_text="Preencha seu telefone", validators=[RegexValidator(regex=r'^\d{10,11}$', message="Telefone deve ter 10 ou 11 dígitos numéricos.")])

# Métodos / insersões no DB: ----------
# Meta é uma classe do Django que é utilizada nesse codigo para formatação de exibição do Django Admin, será ordenado por nome, e levará em consideração a quantidade
# de registros e mudara o nome entre cliente e clientes.
# Transaction.atomic garante que o procedimento sendo feito dentro de save ( que está sendo modificado da base do Django via polimorfismo) será salva ou 100% ou 0% ( atomicidade)
# __str__ também diz respeito a como será exibido os registros no Django Admin
# --------------------------------------
    class Meta:
        ordering = ['nome']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.nome_normalizado = normalizar_str(self.nome)
        self.endereco_normalizado = normalizar_str(self.endereco)
        try:
            super().save(*args, **kwargs)
        except models.IntegrityError as e:
            raise ValidationError("Erro de integridade no cadastro do Cliente.") from e
            
    def __str__(self):
        return f"{self.nome} ({self.email})" if self.email else self.nome

# -------------------------
# FUNCIONARIOS
# Criado campo tipos que é usado no cadastro para determinar os privilégios que ele tem de acesso dentro de sistema
# user foi importado para delegar a função de login ( salvar senha via hash sum e controle de permissões) para o componente ja pronto do Django
# -------------------------
class Funcionario(BaseAuditModel):
    TIPOS = [('admin', 'Super Funcionário (Admin)'),('comum', 'Funcionário Padrão'),]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_funcionario', null=True, blank=True, help_text="Usuário de acesso ao sistema")    
    tipo = models.CharField(max_length=10, choices=TIPOS, default='comum', help_text="Define o nível de acesso no sistema")
    nome = models.CharField(max_length=100, blank=False, help_text="Preencha o nome.", unique=True)    
    nome_normalizado = models.CharField(max_length=100, editable=False, blank=True, db_index=True)    
    endereco = models.CharField(max_length=100, help_text="Preencha seu endereço")
    endereco_normalizado = models.CharField(max_length=100, editable=False, db_index=True, blank=True)
    idade = models.PositiveSmallIntegerField(help_text="Preencha a idade.", blank=False, validators=[MinValueValidator(1), MaxValueValidator(150)])
    cpf = models.CharField(max_length=11, blank=False, null=False, help_text="Preencha seu CPF", validators=[RegexValidator(regex=r'^\d{11}$', message="CPF deve ter exatamente 11 dígitos numéricos.")], unique=True)
    rg = models.CharField(max_length=10, blank=False, null=False, help_text="Preencha seu RG", validators=[RegexValidator(regex=r'^\d{10}$', message="RG deve ter exatamente 10 dígitos numéricos.")], unique=True)
    email = models.EmailField(help_text="Preencha com um e-mail válido.", blank=True, null=True)
    telefone = models.CharField(max_length=11, blank=True, null=True, help_text="Preencha seu telefone", validators=[RegexValidator(regex=r'^\d{10,11}$', message="Telefone deve ter 10 ou 11 dígitos numéricos.")])

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.nome_normalizado = normalizar_str(self.nome)
        self.endereco_normalizado = normalizar_str(self.endereco)
        try:
            super().save(*args, **kwargs)
        except models.IntegrityError as e:
            raise ValidationError("Erro de integridade: CPF, RG ou Nome já cadastrado.") from e
        
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

# -------------------------
# PRODUTOS E TIPOS
# -------------------------
class Tipo(BaseAuditModel):
    nome = models.CharField(max_length=100, blank=False, unique=True, help_text="Preencha o nome.") 
    descricao = models.CharField(max_length=200, blank=False, help_text="Preencha informações sobre o tipo do produto")

    def __str__(self):
        return self.nome

class Produto(BaseAuditModel):
    nome = models.CharField(max_length=100, blank=False, unique=True, help_text="Preencha o nome.") 
    tipo = models.ForeignKey('Tipo', on_delete=models.CASCADE, related_name="Produtos", blank=False)
    descricao = models.CharField(max_length=200, blank=False, help_text="Preencha informações sobre o tipo do produto")
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome
# decorator que transforma esse campo em somente leitura, 
    @property
    def estoque_total(self):
        return self.estoques.aggregate(total=models.Sum('quantidade'))['total'] or 0

# -------------------------
# PEDIDOS
# -------------------------
class Pedido(BaseAuditModel):
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, related_name='pedidos')
    funcionario = models.ForeignKey('Funcionario', on_delete=models.PROTECT, related_name='pedidos')
    STATUS = [('aberto', 'Aberto'),('finalizado', 'Finalizado'),('cancelado', 'Cancelado')]
    status = models.CharField(max_length=20, choices=STATUS, default='aberto', db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.itens.all())

    @transaction.atomic
    def finalizar(self):
        if self.status != "aberto":
            raise ValidationError("Pedido não pode ser finalizado.")

        for item in self.itens.select_related('produto').all():
            estoque = item.produto.estoques.select_for_update().first()
            if not estoque:
                raise ValidationError(f"{item.produto.nome} não possui estoque cadastrado.")
            if estoque.quantidade < item.quantidade:
                raise ValidationError(f"Estoque insuficiente para {item.produto.nome}.")

            estoque.remover(item.quantidade)

        self.status = "finalizado"
        self.save()

    @transaction.atomic
    def cancelar(self):
        if self.status != "finalizado":
            raise ValidationError("Pedido não pode ser cancelado pois não foi finalizado.")

        for item in self.itens.select_related('produto').all():
            estoque = item.produto.estoques.select_for_update().first()
            if estoque:
                estoque.adicionar(item.quantidade)

        self.status = "cancelado"
        self.save()

# -------------------------
# ITENS DO PEDIDO
# -------------------------
class PedidoItem(BaseAuditModel):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pedido', 'produto'], name='unique_produto_por_pedido')
        ]

    @property
    def subtotal(self):
        return (self.quantidade or 0) * (self.preco_unitario or 0)

    def clean(self):
        if not self.produto or self.quantidade is None:
            return

        estoque = self.produto.estoques.first()
        if not estoque:
            raise ValidationError(f"Produto {self.produto.nome} não possui registro de estoque.")
        
        if self.pk is None:
            if estoque.quantidade < self.quantidade:
                raise ValidationError(f"Estoque insuficiente para {self.produto.nome}. Disponível: {estoque.quantidade}")
        else:
            try:
                quantidade_anterior = PedidoItem.objects.get(pk=self.pk).quantidade
                if (estoque.quantidade + quantidade_anterior) < self.quantidade:
                    raise ValidationError(f"Estoque insuficiente. Disponível total: {estoque.quantidade + quantidade_anterior}")
            except PedidoItem.DoesNotExist:
                pass

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        
        if is_new:
            estoque = self.produto.estoques.first()
            if estoque:
                estoque.remover(self.quantidade)
        else:
            # Lógica para atualização de quantidade (Edição)
            old_item = PedidoItem.objects.get(pk=self.pk)
            estoque = self.produto.estoques.first()
            if estoque:
                # Devolve o antigo e remove o novo
                estoque.adicionar(old_item.quantidade)
                estoque.remover(self.quantidade)
        
        super().save(*args, **kwargs)

# -------------------------
# ESTOQUE
# -------------------------
class Estoque(BaseAuditModel):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, related_name='estoques', db_index=True)
    ativo = models.BooleanField(default=True)
    quantidade = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Estoque: {self.produto.nome} ({self.quantidade})"

    def adicionar(self, qtd):
        if qtd <= 0:
            raise ValidationError("A quantidade a adicionar deve ser positiva.")
        self.quantidade += qtd
        self.save() 

    def remover(self, qtd):
        if qtd <= 0:
            raise ValidationError("A quantidade a remover deve ser positiva.")
        if qtd > self.quantidade:
            raise ValidationError("Estoque insuficiente para realizar a operação.")
        self.quantidade -= qtd
        self.save()

# -------------------------
# SIGNALS (Garante a devolução no DELETE em cascata)
# -------------------------
@receiver(pre_delete, sender=PedidoItem)
def devolver_estoque_ao_deletar_item(sender, instance, **kwargs):
    """
    Sempre que um PedidoItem for deletado (mesmo se o Pedido for deletado),
    devolvemos a quantidade ao estoque do produto.
    """
    estoque = instance.produto.estoques.first()
    if estoque:
        estoque.adicionar(instance.quantidade)