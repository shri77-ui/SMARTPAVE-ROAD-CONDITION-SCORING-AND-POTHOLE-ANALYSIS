import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("runs/detect/train4/results.csv")

# Loss Curve
plt.figure()
plt.plot(df['epoch'], df['train/box_loss'], label='Train Box Loss')
plt.plot(df['epoch'], df['val/box_loss'], label='Val Box Loss')
plt.legend()
plt.title("Loss Curve")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()