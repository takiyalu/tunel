from django.db import models
from django.contrib.auth.models import User


class Base(models.Model):
    created = models.DateTimeField('Creation', auto_now_add=True)
    updated = models.DateTimeField('Last Update', auto_now=True)
    active = models.BooleanField('Active?', default=True)

    class Meta:
        abstract = True

# Represents the stocks/products basic information that will be unique in the database
class Ativo(Base):
    nome = models.CharField('Nome', max_length=100)
    ticker = models.CharField('Ticker', max_length=10, unique=True)
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=20)

    class Meta:
        verbose_name = 'Ativo'
        verbose_name_plural = 'Ativos'

    def __str__(self):
        return f'{self.ticker}'


# Carries the foreign key of usuario and ativo making the bridge between them and also carries the flag and our main
# parameters
class AtivoDetalhe(Base):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ativo_detalhes')
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE, related_name='ativos_detalhes')
    periodicidade = models.IntegerField('Periodicidade')
    limite_inferior = models.DecimalField('Inferior', decimal_places=2, max_digits=20)
    limite_superior = models.DecimalField('Superior', decimal_places=2, max_digits=20)
    email_enviado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Detalhe do Ativo'
        verbose_name_plural = 'Detalhes dos Ativos'

    def __str__(self):
        return f'{self.ativo.ticker} details for {self.usuario.username}'


