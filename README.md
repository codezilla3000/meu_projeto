# Sistema de Gestão de Vendas e Estoque 🚀

**Aluno:** Eduardo Junior  
**Projeto de Conclusão:** Capacita Python

---

## 🎯 Problema que o Sistema Resolve
O sistema resolve a falta de controle e os prejuízos financeiros causados por falhas de inventário e erros de registro manual. Através de um motor de integridade em tempo real, o software impede a venda de mercadorias inexistentes e blinda a operação contra concorrência de vendas simultâneas (**Race Conditions**).

## ✨ Diferenciais Técnicos e Funcionalidades
* **Locking de Estoque:** Uso de `select_for_update` no banco de dados para evitar vendas duplicadas do mesmo item.
* **Estorno Reativo (Signals):** Implementação de `pre_delete` para devolução automática de produtos ao estoque em caso de exclusão de pedidos.
* **Transações Atômicas:** Uso de `@transaction.atomic` para garantir que a venda e a baixa no estoque ocorram como uma unidade única.
* **Auditoria Automática:** Herança de `BaseAuditModel` para rastreabilidade de criação e modificação em todas as tabelas.
* **Busca Inteligente:** Normalização de strings para evitar duplicidade entre registros (ex: "João" e "joao").

## 🛠️ Tecnologias Utilizadas
* **Python 3.13**
* **Django Framework** (ORM, Signals, Auth)
* **SQLite** (Banco de dados local incluído)
* **Bootstrap 5** (Interface Visual)

---

## ⚙️ Como Executar o Projeto

1.  **Clone o repositório** ou baixe o código-fonte.
2.  Certifique-se de ter o **Python** instalado.
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute as migrações:**
    ```bash
    python manage.py migrate
    ```
5.  **Inicie o servidor local:**
    ```bash
    python manage.py runserver
    ```

Acesse em seu navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
