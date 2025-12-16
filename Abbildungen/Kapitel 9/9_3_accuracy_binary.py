# ================================================================
# Plots the accuracy over epochs for binary classification with
# two batch sizes, including standard deviation shading.
# ================================================================

import matplotlib.pyplot as plt
import numpy as np

# --- Measurement data ---------------------------------------------------------
# Epochs
epochs = [2, 3, 4]

# Mean accuracy values
accuracy_batch16 = [0.9687, 0.9703, 0.9679]
accuracy_batch32 = [0.9670, 0.9700, 0.9709]

# Standard deviations
std_batch16 = [0.0100, 0.0076, 0.0083]
std_batch32 = [0.0059, 0.0069, 0.0090]

# --- Create plot ------------------------------------------------
plt.figure(figsize=(8, 5))

# Main curves
plt.plot(epochs, accuracy_batch16, '-o', label='Batchgröße 16')
plt.plot(epochs, accuracy_batch32, '--s', label='Batchgröße 32')

# Standard deviation shading
plt.fill_between(
    epochs,
    np.array(accuracy_batch16) - np.array(std_batch16),
    np.array(accuracy_batch16) + np.array(std_batch16),
    alpha=0.2
)

plt.fill_between(
    epochs,
    np.array(accuracy_batch32) - np.array(std_batch32),
    np.array(accuracy_batch32) + np.array(std_batch32),
    alpha=0.2
)

# Axes labels, title, layout
plt.xlabel('Epochenzahl')
plt.ylabel('Accuracy')
plt.title('Accuracy-Verlauf bei Binärer Klassifikation')
plt.xticks(epochs)  # only integer values on X-axis
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper center')

plt.tight_layout()
plt.savefig("9_3_accuracy_binary.png", dpi=300)
plt.show()
