# результаты цветов: 
# красный - 62 распознанно 38 нет
# зеленый - 42 распознанно 58 нет
# синий - 100 распознанно 0 нет
# желтый - 100 распознанно 0 нет
# голубой - 100 распознанно 0 нет
# фиолетовый -98 распознанно 2 нет
# белый - 100 распознанно 0 нет
# черный - 0 распознанно 100 нет
import matplotlib.pyplot as plt

# Данные
colors = ['красный', 'зеленый', 'синий', 'желтый', 'голубой', 'фиолетовый', 'белый', 'черный']

bar_width = 0.3
x = range(len(colors))
fig, ax = plt.subplots()
ax.set_facecolor('lightblue') 

plt.bar(0, 62, width=bar_width, color='red')
plt.bar(0 + bar_width , 38, width=bar_width, label='Не распознанно', color='gray')

plt.bar(1, 42, width=bar_width, color='green')
plt.bar(1 + bar_width , 58, width=bar_width, color='gray')

plt.bar(2, 100, width=bar_width,  color='blue')
plt.bar(2 + bar_width , 0, width=bar_width, color='gray')

plt.bar(3, 100, width=bar_width,  color='yellow')
plt.bar(3 + bar_width , 0, width=bar_width, color='gray')

plt.bar(4, 100, width=bar_width,  color='cyan')
plt.bar(4 + bar_width , 0, width=bar_width, color='gray')

plt.bar(5, 98, width=bar_width,  color='violet')
plt.bar(5 + bar_width , 2, width=bar_width, color='gray')

plt.bar(6, 100, width=bar_width,  color='white')
plt.bar(6 + bar_width , 0, width=bar_width, color='gray')

plt.bar(7, 0, width=bar_width,  color='black')
plt.bar(7 + bar_width , 100, width=bar_width, color='gray')

plt.xlabel('Цвета')
plt.ylabel('Количество')
plt.title('Распознанные и нераспознанные цвета')
plt.xticks([i + bar_width / 2 for i in x], colors)  

plt.legend()
plt.show()