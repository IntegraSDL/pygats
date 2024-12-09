import matplotlib.pyplot as plt
import numpy as np

y = [0,    42,     46,    99,   99,    91,    99,    96,    99 ]
x = [1.0, 1.002, 1.004, 1.005, 1.006, 1.007, 1.008, 1.009, 1.01]
plt.plot(x, y)
plt.xlabel("коэффициент контрастности")
plt.ylabel("качество распознавания изображений")
plt.title("качество распознававния от контрастности")
plt.grid(True)
plt.xticks(np.arange(1, 1.01, 0.001))
plt.yticks(np.arange(0, 102, 2)) 
plt.show()