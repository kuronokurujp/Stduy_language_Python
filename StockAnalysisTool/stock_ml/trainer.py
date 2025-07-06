"""Training helper using full DB history."""

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from .data import ensure_history_up_to_date
from .features import make_features
from .model import SimpleMLP

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


def train_model(ticker: str, lag: int = 5, n_epochs: int = 30):
    df = ensure_history_up_to_date(ticker)
    data, feature_cols = make_features(df, window=lag)
    x = torch.tensor(data[feature_cols].values, dtype=torch.float32)
    y = torch.tensor(data["target"].values, dtype=torch.float32)
    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = SimpleMLP(len(feature_cols))
    criterion = nn.BCELoss()
    # optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    # L2 正則化を追加
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    model.train()
    for _ in range(n_epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
    save_path = MODEL_DIR / f"{ticker.upper()}_lag{lag}.pt"
    torch.save(
        {"model_state": model.state_dict(), "features": feature_cols, "lag": lag},
        save_path,
    )
    return save_path
