# ================================================================
# Plots the accuracy over epochs for multiclass classification with
# two batch sizes, including standard deviation shading.
# ================================================================

import matplotlib.pyplot as plt
import numpy as np

# --- Measurement data ---------------------------------------------------------

# Epochs
epochs = [3, 4, 5]

# Mean accuracy values
accuracy_batch16 = [0.8517, 0.8542, 0.8446]
accuracy_batch32 = [0.8507, 0.8556, 0.8522]

# Standard deviations
std_batch16 = [0.0320, 0.0348, 0.0246]
std_batch32 = [0.0304, 0.0298, 0.0296]

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
plt.title('Accuracy-Verlauf bei der Multiklassen-Klassifikation')
plt.xticks(epochs)  # only integer values on X-axis
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right')

plt.tight_layout()
plt.savefig("9_4_accuracy_multiclass.png", dpi=300)
plt.show()
