"""
core/train.py — Train PyTorch CycloneNet

Usage:
    python core/train.py
    python core/train.py --epochs 300 --lr 0.0005
"""

import argparse, sys, os, time
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dataset import load_raw, clean, save_processed, get_stats
from core.model   import CycloneClassifier
from core.config  import Config


def train(csv_path=None, epochs=None, lr=None):
    print("=" * 55)
    print("  CycloneOPS PRO — PyTorch Training Pipeline")
    print("=" * 55)

    # ── 1. Load & clean data ──────────────────────────
    print(f"\n[1/4] Loading: {csv_path or Config.DATA_RAW}")
    df = clean(load_raw(csv_path))
    save_processed(df)
    stats = get_stats(df)
    print(f"      Records    : {stats['total']}")
    print(f"      Categories : {stats['categories']}")

    # Apply CLI overrides
    if epochs: Config.EPOCHS = epochs
    if lr:     Config.LR     = lr

    device_name = "CUDA" if torch.cuda.is_available() else "CPU"

    # ── 2. Train ──────────────────────────────────────
    print(f"\n[2/4] Building CycloneNet ...")
    print(f"      Architecture : {Config.INPUT_SIZE} → "
          f"{' → '.join(str(h) for h in Config.HIDDEN_SIZES)} → "
          f"{len(Config.CATEGORIES)}")
    print(f"      Epochs       : {Config.EPOCHS}")
    print(f"      LR           : {Config.LR}")
    print(f"      Batch size   : {Config.BATCH_SIZE}")
    print(f"      Weight decay : {Config.WEIGHT_DECAY}")
    print(f"      Device       : {device_name}\n")

    t0  = time.time()
    clf = CycloneClassifier()
    clf.fit(df)
    elapsed = time.time() - t0

    # ── 3. Evaluate ───────────────────────────────────
    print(f"\n[3/4] Evaluating on full training set ...")

    X      = df[Config.FEATURES].values.astype(np.float32)
    assert clf.encoder is not None
    y_true = clf.encoder.transform(df[Config.TARGET].values)
    assert clf.scaler is not None
    X_sc   = clf.scaler.transform(X).astype(np.float32)

    assert clf.net is not None
    clf.net.eval()
    with torch.no_grad():
        xt    = torch.tensor(X_sc).to(clf.device)
        probs = F.softmax(clf.net(xt), dim=1).cpu().numpy()
        preds = probs.argmax(axis=1)

    acc = (preds == y_true).mean()
    print(f"      Overall Accuracy : {acc:.4f} ({acc*100:.1f}%)")
    print(f"      Per-class:")
    for i, cat in enumerate(Config.CATEGORIES):
        mask = y_true == i
        if mask.sum() == 0:
            continue
        cat_acc = (preds[mask] == i).mean()
        print(f"        {cat:<5} → {cat_acc:.3f}  ({mask.sum()} samples)")

    # ── 4. Save ───────────────────────────────────────
    print(f"\n[4/4] Saving model ...")
    clf.save()

    print(f"\n{'='*55}")
    print(f"  ✅  Training complete! ({elapsed:.1f}s)")
    print(f"  Model  : {Config.MODEL_PATH}")
    print(f"  Run    : python app/main.py")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv",    default=None, type=str)
    parser.add_argument("--epochs", default=None, type=int)
    parser.add_argument("--lr",     default=None, type=float)
    args = parser.parse_args()
    train(args.csv, args.epochs, args.lr)