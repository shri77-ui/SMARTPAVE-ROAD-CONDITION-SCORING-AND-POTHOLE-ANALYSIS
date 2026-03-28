import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\SMARTPAVE_WEB\pothole_dataset\runs\detect\train3\results.csv")

plt.figure()
plt.plot(df['epoch'], df['train/box_loss'])

plt.xlabel("Epoch")
plt.ylabel("Training Box Loss")
plt.title("Training Loss Curve")

plt.savefig("training_loss_curve.png")
plt.show()



