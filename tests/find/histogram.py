import matplotlib.pyplot as plt

colors = ['#000000', '#000500', '#000A00', '#000F00', '#00FF00']

bar_width = 0.3
x = range(len(colors))
fig, ax = plt.subplots()
ax.set_facecolor('lightblue')

plt.bar(0, 0, width=bar_width, color='#000000')
plt.bar(0 + bar_width, 100, width=bar_width, label='Не распознанно', color='gray')

plt.bar(1, 100, width=bar_width, color='#000500')
plt.bar(1 + bar_width, 0, width=bar_width, color='gray')

plt.bar(2, 100, width=bar_width, color='#000A00')
plt.bar(2 + bar_width, 0, width=bar_width, color='gray')

plt.bar(3, 100, width=bar_width, color='#000F00')
plt.bar(3 + bar_width, 0, width=bar_width, color='gray')

plt.bar(4, 100, width=bar_width, color='#00FF00')
plt.bar(4 + bar_width, 0, width=bar_width, color='gray')

plt.xlabel('Цвета')
plt.ylabel('Количество')
plt.title('Распознанные и нераспознанные цвета')
plt.xticks([i + bar_width / 2 for i in x], colors)

plt.legend()
plt.show()