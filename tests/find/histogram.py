import matplotlib.pyplot as plt

colors = ['#FEFEFE', '#FDFFF7', '#FCFFFA', '#FBFFFD']

bar_width = 0.3
x = range(len(colors))
fig, ax = plt.subplots()
ax.set_facecolor('lightblue')

plt.bar(0, 89, width=bar_width, color='#FEFEFE')
plt.bar(0 + bar_width, 11, width=bar_width, color='gray')

plt.bar(1, 99, width=bar_width, color='#FDFFF7')
plt.bar(1 + bar_width, 0, width=bar_width, color='gray')

plt.bar(2, 100, width=bar_width, color='#FCFFFA')
plt.bar(2 + bar_width, 0, width=bar_width, color='gray')

plt.bar(3, 98, width=bar_width, color='#FBFFFD')
plt.bar(3 + bar_width, 2, width=bar_width, label='Не распознанно', color='gray')


plt.xlabel('Цвета')
plt.ylabel('Количество')
plt.title('Качество распознававния от контрастности 1.0039')
plt.xticks([i + bar_width / 2 for i in x], colors)

plt.legend()
plt.show()