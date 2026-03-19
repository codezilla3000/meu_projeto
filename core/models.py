# Esse model aqui é criado numa pasta diferente ao invés de criado dentro do model do projeto para que possa ser herdado por outros
#abstract = True → não cria tabela no banco
#%(class)s_created → cria related_name dinâmico para cada model
#save(self, *args, **kwargs) permite passar user ao salvar
#auto_now_add e auto_now cuidam dos timestamps

from django.db import models
from django.conf import settings

class BaseAuditModel(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name="%(class)s_criacao",editable=False,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name="%(class)s_atualizacao",editable=False,null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if not self.pk:
            if user:
                self.created_by = user
                self.updated_by = user
        else:
            if user:
                self.updated_by = user
        super().save(*args, **kwargs)