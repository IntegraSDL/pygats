import matplotlib.pyplot as plt
import numpy as np

x = [1.0, 1.001, 1.002, 1.004, 1.006, 1.009, 1.01, ]
y = [0,     0,     0,     74,    87,   81,    100,]

plt.plot(x, y)
plt.xlabel("коэффициент контрастности")
plt.ylabel("качество распознавания изображений")
plt.title("качество распознававния от контрастности")
plt.grid(True)
plt.xticks(np.arange(1, 1.01, 0.005))
plt.yticks(np.arange(0, 102, 5))
plt.show()