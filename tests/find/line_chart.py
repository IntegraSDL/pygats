import matplotlib.pyplot as plt
import numpy as np

y = [0, 82, 89, 96, 99, 100, 100, 100]
x = [1, 1.0025, 1.0039, 1.009, 1.01, 1.1, 2.0078, 4.0156]
plt.plot(x, y)
plt.xlabel("коэффициент контрастности")
plt.ylabel("качество распознавания изображений")
plt.title("качество распознававния от контрастности")
plt.grid(True)
plt.xticks(np.arange(1, 4.0156, 0.2))  # От 1 до 5 с шагом 0.2
# Устанавливаем деления по оси Y
plt.yticks(np.arange(0, 102, 2)) 
plt.show()