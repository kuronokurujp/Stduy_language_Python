"""Interactive CLI with scheduler."""

import threading
from stock_ml.scheduler import start_scheduler
from stock_ml.trainer import train_model
from stock_ml.predictor import predict_buy_sell
from stock_ml.backtest import run_backtests

TARGET_TICKERS = ["7203.T"]


def _manual_train(ticker: str):
    path = train_model(ticker)
    print(f"Training finished. Model saved to {path}")


def _predict(ticker: str):
    decision, prob = predict_buy_sell(ticker)
    print(f"{ticker}: {decision} (prob={prob:.2f})")


def _backtest(ticker: str):
    results = run_backtests(ticker)
    if not results:
        print("Not enough data for backtest.")
        return
    print(" TrainDays | Lag | Strategy× | Buy&Hold× | Excess×")
    for r in results:
        print(
            f" {r['train_days']:>9} | {r['lag']:>3} | "
            f"{r['strategy_mult']:.2f}      | {r['buy_hold_mult']:.2f}      | "
            f"{r['excess']:+.2f}"
        )

def repl():
    print("Commands: train <TICKER>, predict <TICKER>, backtest <TICKER>, exit")
    while True:
        try:
            cmd_line = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        if not cmd_line:
            continue
        if cmd_line == "exit":
            break
        parts = cmd_line.split()
        if len(parts) < 2:
            print("Invalid command.")
            continue
        action, ticker = parts[0], parts[1]
        if action == "train":
            _manual_train(ticker)
        elif action == "predict":
            _predict(ticker)
        elif action == "backtest":
            _backtest(ticker)
        else:
            print("Unknown command.")


def main():
    threading.Thread(
        target=start_scheduler, args=(TARGET_TICKERS,), daemon=True
    ).start()
    repl()


if __name__ == "__main__":
    main()
