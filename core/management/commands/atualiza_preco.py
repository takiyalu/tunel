from django.core.management.base import BaseCommand
from core.models import Ativo
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Agenda as tarefas de atualização de preço dos Ativos baseado na periodicidade de cada um.'

    def handle(self, *args, **kwargs):
        print("Command is being executed")
        PeriodicTask.objects.all().delete()
        ativos = Ativo.objects.all()
        print(f"Found {ativos.count()} ativos")
        for ativo in ativos:
            interval, created = IntervalSchedule.objects.get_or_create(
                every=ativo.periodicidade,
                period=IntervalSchedule.MINUTES,
            )
            print(f"Created interval: {interval}, created: {created}")
            PeriodicTask.objects.create(
                interval=interval,
                name=f"Atualiza preço de ativo {ativo.id}",
                task='core.tasks.atualiza_preco_ativo',
                args=json.dumps([ativo.id]),
            )