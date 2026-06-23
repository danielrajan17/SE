"""
core/model.py — PyTorch Neural Network for Cyclone Intensity Classification

Architecture:
    Input(6) → Linear(64) → BN → ReLU → Dropout
             → Linear(128)→ BN → ReLU → Dropout
             → Linear(64) → BN → ReLU → Dropout
             → Linear(num_classes)
             → Softmax
"""

import os, sys
import numpy as np
import joblib
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Config

import torch
import torch.nn as nn
import torch.nn.functional as F


# ── Neural Network Definition ─────────────────────────────────────────────────
class CycloneNet(nn.Module):
    def __init__(self, input_size: int, hidden_sizes: list, num_classes: int, dropout: float):
        super().__init__()
        layers = []
        in_size = input_size

        for h in hidden_sizes:
            layers += [
                nn.Linear(in_size, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            in_size = h

        layers.append(nn.Linear(in_size, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


# ── Scaler (manual, no sklearn) ───────────────────────────────────────────────
class StandardScaler:
    """Minimal StandardScaler — no sklearn dependency."""
    def __init__(self):
        self.mean_ = None
        self.std_  = None

    def fit(self, X: np.ndarray):
        self.mean_ = X.mean(axis=0)
        self.std_  = X.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean_) / self.std_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


# ── Label Encoder (manual) ────────────────────────────────────────────────────
class LabelEncoder:
    def __init__(self, classes: list):
        self.classes_   = classes
        self.class2idx_ = {c: i for i, c in enumerate(classes)}

    def transform(self, y):
        return np.array([self.class2idx_[c] for c in y], dtype=np.int64)

    def inverse_transform(self, idx):
        return [self.classes_[i] for i in idx]


# ── Main Model Wrapper ────────────────────────────────────────────────────────
class CycloneClassifier:

    def __init__(self):
        self.cfg       = Config
        self.device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: Optional[CycloneNet] = None
        self.scaler: Optional[StandardScaler] = None
        self.encoder: Optional[LabelEncoder] = None
        self._trained  = False
        self.num_classes = len(Config.CATEGORIES)

    # ── Build network ─────────────────────────────────────────────────────────
    def _build_net(self):
        self.net = CycloneNet(
            input_size   = Config.INPUT_SIZE,
            hidden_sizes = Config.HIDDEN_SIZES,
            num_classes  = self.num_classes,
            dropout      = Config.DROPOUT,
        ).to(self.device)

    # ── Training ──────────────────────────────────────────────────────────────
    def fit(self, df):
        import pandas as pd

        self.scaler  = StandardScaler()
        self.encoder = LabelEncoder(Config.CATEGORIES)
        self._build_net()
        assert self.net is not None

        X = df[Config.FEATURES].values.astype(np.float32)
        y = self.encoder.transform(df[Config.TARGET].values)

        X_scaled = self.scaler.fit_transform(X).astype(np.float32)

        # Data augmentation: add noise to create more samples
        augmented_X = []
        augmented_y = []
        for _ in range(5):  # 5x augmentation
            noise = np.random.normal(0, 0.1, X_scaled.shape).astype(np.float32)  # small noise
            augmented_X.append(X_scaled + noise)
            augmented_y.append(y)
        X_scaled = np.vstack([X_scaled] + augmented_X).astype(np.float32)
        y = np.concatenate([y] + augmented_y)

        # Split into train/val (80/20)
        n = len(X_scaled)
        indices = np.random.permutation(n)
        train_size = int(0.8 * n)
        train_idx, val_idx = indices[:train_size], indices[train_size:]
        
        X_train = X_scaled[train_idx]
        y_train = y[train_idx]
        X_val = X_scaled[val_idx]
        y_val = y[val_idx]

        X_tensor = torch.tensor(X_train, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(y_train, dtype=torch.long).to(self.device)

        optimizer = torch.optim.AdamW(self.net.parameters(), lr=Config.LR, weight_decay=Config.WEIGHT_DECAY)  # type: ignore
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=Config.EPOCHS)
        criterion = nn.CrossEntropyLoss()

        bs = Config.BATCH_SIZE

        print(f"[model] Training on {self.device} | samples={len(X_train)} train, {len(X_val)} val | epochs={Config.EPOCHS}")

        self.net.train()  # type: ignore
        best_val_acc = 0.0
        patience = 50
        patience_counter = 0
        
        for epoch in range(1, Config.EPOCHS + 1):
            # Shuffle train
            perm = torch.randperm(len(X_tensor))
            X_tensor = X_tensor[perm]
            y_tensor = y_tensor[perm]

            total_loss = 0
            for i in range(0, len(X_tensor), bs):
                xb = X_tensor[i:i+bs]
                yb = y_tensor[i:i+bs]
                optimizer.zero_grad()
                loss = criterion(self.net(xb), yb)  # type: ignore
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            scheduler.step()

            # Validation
            val_acc = self._validate(X_val, y_val)
            
            if epoch % 50 == 0 or epoch == 1:
                train_acc = self._train_accuracy(X_train, y_train)
                print(f"  Epoch {epoch:>3}/{Config.EPOCHS}  "
                      f"loss={total_loss/max(len(X_tensor)//bs,1):.4f}  "
                      f"train_acc={train_acc:.4f}  val_acc={val_acc:.4f}")

            # Early stopping
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                # Save best model
                self._save_checkpoint()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"  Early stopping at epoch {epoch}")
                    break

        # Load best model
        self._load_checkpoint()
        self._trained = True
        final_acc = self._train_accuracy(X_scaled, y)
        print(f"[model] Final training accuracy: {final_acc:.4f}")
        return self

    def _train_accuracy(self, X_scaled, y_true):
        assert self.net is not None
        self.net.eval()
        with torch.no_grad():
            xt = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
            logits = self.net(xt)
            preds  = logits.argmax(dim=1).cpu().numpy()
        self.net.train()
        return float((preds == y_true).mean())

    def _validate(self, X_val, y_val):
        assert self.net is not None
        self.net.eval()
        with torch.no_grad():
            xt = torch.tensor(X_val, dtype=torch.float32).to(self.device)
            logits = self.net(xt)
            preds = logits.argmax(dim=1).cpu().numpy()
        self.net.train()
        return float((preds == y_val).mean())

    def _save_checkpoint(self):
        assert self.net is not None
        self._checkpoint = self.net.state_dict()

    def _load_checkpoint(self):
        assert self.net is not None
        if hasattr(self, '_checkpoint'):
            self.net.load_state_dict(self._checkpoint)

    # ── Prediction ────────────────────────────────────────────────────────────
    def predict_one(self, lat, lon, ci, ecp, dp, msw, k=None) -> dict:
        if not self._trained:
            self._try_load()

        assert self.scaler is not None
        assert self.net is not None

        x = np.array([[lat, lon, ci, ecp, dp, msw]], dtype=np.float32)
        x_scaled = self.scaler.transform(x).astype(np.float32)

        self.net.eval()
        with torch.no_grad():
            xt     = torch.tensor(x_scaled).to(self.device)
            logits = self.net(xt)
            probs  = F.softmax(logits, dim=1).cpu().numpy()[0]

        pred_idx  = int(probs.argmax())
        pred_cat  = Config.CATEGORIES[pred_idx]
        confidence= float(probs[pred_idx]) * 100

        # Top-3 categories with probabilities
        top3 = sorted(
            [(Config.CATEGORIES[i], float(probs[i])*100) for i in range(self.num_classes)],
            key=lambda x: -x[1]
        )[:3]

        info = Config.CATEGORY_INFO[pred_cat]
        return {
            "category"   : pred_cat,
            "full_name"  : info["name"],
            "color"      : info["color"],
            "risk"       : info["risk"],
            "order"      : info["order"],
            "confidence" : round(confidence, 1),
            "avg_dist"   : round(float(np.std(probs)), 4),  # uncertainty proxy
            "k_used"     : "NN",
            "neighbors"  : [
                {"category": c, "color": Config.CATEGORY_INFO[c]["color"],
                 "distance": round(100 - p, 2)}
                for c, p in top3
            ],
            "top3"       : [{"category": c, "probability": round(p,1)} for c,p in top3],
            "all_probs"  : {Config.CATEGORIES[i]: round(float(probs[i])*100,1)
                            for i in range(self.num_classes)},
        }

    # ── Save / Load ───────────────────────────────────────────────────────────
    def save(self):
        assert self.net is not None
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        torch.save({
            "state_dict" : self.net.state_dict(),
            "num_classes": self.num_classes,
        }, Config.MODEL_PATH)
        joblib.dump(self.scaler,  Config.SCALER_PATH)
        joblib.dump(self.encoder, Config.ENCODER_PATH)
        print(f"[model] Saved → {Config.MODEL_DIR}")

    def load(self):
        missing = [p for p in [Config.MODEL_PATH, Config.SCALER_PATH, Config.ENCODER_PATH] if not os.path.exists(p)]
        if missing:
            import warnings
            warnings.warn(f"Model files not found: {missing} — model not ready for predictions", RuntimeWarning)
            return self

        self._build_net()
        assert self.net is not None
        ckpt = torch.load(Config.MODEL_PATH, map_location=self.device)
        self.net.load_state_dict(ckpt["state_dict"])
        self.net.eval()
        self.scaler  = joblib.load(Config.SCALER_PATH)
        self.encoder = joblib.load(Config.ENCODER_PATH)
        self._trained = True
        print("[model] PyTorch model loaded from disk.")
        return self

    def _try_load(self):
        try:
            self.load()
        except FileNotFoundError as e:
            raise RuntimeError(f"Model not trained. Run: python core/train.py\n{str(e)}")

    def is_ready(self) -> bool:
        return self._trained or all(
            os.path.exists(p) for p in
            [Config.MODEL_PATH, Config.SCALER_PATH, Config.ENCODER_PATH]
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
_instance: Optional[CycloneClassifier] = None

def get_model() -> CycloneClassifier:
    global _instance
    if _instance is None:
        _instance = CycloneClassifier()
        try:
            _instance.load()
        except FileNotFoundError:
            pass
    return _instance
