import matplotlib.pyplot as plt

x = [ 98, 100, 99, 89]
y =  1.0039, 1.0039, 1.0039, 1.0039
plt.plot(x, y)
plt.xlabel("качество распознавания изображений")
plt.ylabel("коэффициент контрастности")
plt.title("качество распознававния от контрастности")
plt.grid(True)
plt.show()