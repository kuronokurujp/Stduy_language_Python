
"""APScheduler background training scheduler."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from .trainer import train_model

SCHEDULER = BackgroundScheduler()

def scheduled_train(ticker: str):
    print(f"[{datetime.now()}] Scheduled training for {ticker}")
    path = train_model(ticker)
    print(f"Model saved: {path}")

def start_scheduler(tickers: list[str]):
    for time_spec in [dict(hour=9, minute=0), dict(hour=15, minute=30)]:
        for ticker in tickers:
            trigger = CronTrigger(**time_spec)
            SCHEDULER.add_job(
                scheduled_train, trigger, args=[ticker], id=f"{ticker}_{time_spec['hour']}"
            )
    SCHEDULER.start()
