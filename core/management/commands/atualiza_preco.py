from django.core.management.base import BaseCommand
from core.models import AtivoDetalhe
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Agenda as tarefas de atualização de preço dos Ativos baseado na periodicidade de cada um.'

    def handle(self, *args, **kwargs):
        print("Command is being executed")
        PeriodicTask.objects.all().delete()
        detalhes = AtivoDetalhe.objects.all()
        for detalhe in detalhes:
            interval, created = IntervalSchedule.objects.get_or_create(
                every=detalhe.periodicidade,
                period=IntervalSchedule.MINUTES,
            )
            PeriodicTask.objects.create(
                interval=interval,
                name=f"Atualiza preço de ativo {detalhe.id}",
                task='core.tasks.atualiza_preco_ativo',
                args=json.dumps([detalhe.id]),
            )