import numpy as np
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

# ===============================
# MODEL SCORES (from your output)
# ===============================
scores = [

# video 1
0.0645,0.062,0.0594,0.0813,0.1393,0.1754,0.225,0.2172,0.2013,0.2301,
0.284,0.4533,0.6508,0.6937,0.9299,0.9582,0.8683,

# video 2
0.1049,0.0839,0.0932,0.0958,0.0871,0.0567,0.0691,0.2032,0.4036,0.4066,
0.2993,0.2502,0.3852,0.4525,0.3362,0.1601,0.0951,

# video 3
0.2554,0.2844,0.2792,0.2052,0.3436,0.6113,0.7727,0.9204,1.081,0.859,
0.5139,0.3819,0.3861,0.5739,0.4817,0.2963,0.2601,

# video 4
0.2224,0.2061,0.1913,0.2258,0.2717,0.5024,0.914,0.9089,0.7469,0.8327,
0.846,0.6173,0.3415,0.2705,0.2777,0.286,0.289,

# video 5
0.0999,0.1131,0.1208,0.1312,0.1474,0.1705,0.1571,0.13,0.1155,0.1249,
0.1838,0.193,0.2415,0.3469,0.698,0.8225,0.8883
]

labels = [

# video 1
0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,

# video 2
0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,

# video 3
1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,

# video 4
0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,

# video 5
0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1
]
# ======================================
# GROUND TRUTH LABELS (from UBnormal GT)
# 0 = normal
# 1 = anomaly
# ======================================



# ===============================
# COMPUTE ROC + AUC
# ===============================

fpr, tpr, thresholds = roc_curve(labels, scores)

roc_auc = auc(fpr, tpr)

print("\n==============================")
print("ROC AUC RESULT")
print("==============================")
print("AUC Score:", round(roc_auc, 4))
print("==============================\n")

# ===============================
# DISPLAY ROC CURVE
# ===============================

plt.figure(figsize=(6,5))

plt.plot(fpr, tpr, color="blue", linewidth=2,
         label=f"AUC = {roc_auc:.3f}")

plt.plot([0,1], [0,1], linestyle="--", color="gray")

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Street Anomaly Detection")

plt.legend(loc="lower right")

plt.grid(True)

plt.show()