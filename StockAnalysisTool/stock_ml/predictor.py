
"""Single-day ahead buy/sell predictor."""
import torch
from pathlib import Path
from .data import ensure_history_up_to_date
from .features import make_features
from .model import SimpleMLP

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

def load_model(ticker: str, lag: int = 5):
    path = MODEL_DIR / f"{ticker.upper()}_lag{lag}.pt"
    if not path.exists():
        raise FileNotFoundError("Model not trained. Run train first.")
    checkpoint = torch.load(path, map_location="cpu")
    model = SimpleMLP(len(checkpoint["features"]))
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint["features"]

def predict_buy_sell(ticker: str, lag: int = 5):
    df = ensure_history_up_to_date(ticker, lookback_days=lag+10)
    data, feature_cols = make_features(df, window=lag)
    if data.empty:
        raise ValueError("Not enough data")
    latest = data.iloc[-1]
    model, expected_features = load_model(ticker, lag)
    import torch
    x = torch.tensor(latest[expected_features].values, dtype=torch.float32)
    prob = model(x).item()
    return ("BUY" if prob > 0.5 else "SELL", prob)
