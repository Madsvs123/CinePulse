from celery import shared_task

from analytics.services import rollup_today


@shared_task
def rollup_daily_metrics():
    rollup_today()
    return "ok"
