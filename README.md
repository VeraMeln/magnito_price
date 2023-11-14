# Mодель стоимости жилья в зависимости от параметров этого жилья

## Задача 1. 

[код для парсинга данных](parsing.py)

[тетрадка с подбором гипрепараметров модели: magnito_price_model_selection.ipynb](magnito_price_model_selection.ipynb)

[РЕШЕНИЕ: тетрадка обученной моделью: magnito_price_prediction.ipynb](magnito_price_prediction.ipynb)

[Отчет по исследованию](Отчет.pdf)

**Постановка задачи**

Построить математическую модель стоимости жилья в зависимости от параметров этого жилья.

В качестве источника исходных данных предлагается использовать данные сайта магнитогорской недвижимости www.citystar.ru. Задание может выполнено на любом языке любым известным статистическим методом, методом анализа данных или прочими методами на усмотрение исполнителя. По результатам выполнения задачи должен быть написан отчет о результате работы и ходе исследования.

**Резальтаты**

В ходе проведенного исследования **построена модель предсказания цены квартиры по ее параметрам**. 

**Источник данных** - сайт магнитогорской недвижимости **www.citystar.ru**. Объвления с сайта получены с помощью **парсинга**. Код парсера находится в файле parsing.py. **Данные сохраняются в базу данных SQLight**. Написаны **собственные трансформеры для предварительной обработки данных** – DataCleaner и FeaturesTransformer. **Все шаги предварительной обработки данных собраны в PipeLine**.

На тренировочной выборке **обучена модель RandomForestRegressor** с гиперпараметрами
•	max_depth=10, 
•	n_estimators=100,
•	random_state=12345

**На вход модели подаются параметры квартиры в формате JSON на выходе получается цена квартиры в формате JSON**. 

**Средняя ошибка на прогнозе 484 тыс рублей, что составляет примерно 14,4 % от цены квартиры**.


## Задача 2.

**Постановка задачи**

На основе данных собранных в задании 1 разбить исходную выборку на кластеры методами кластерного анализа. Цель задания определить  район продажи квартиры на основе данных о ценах, площадях и количестве комнат. Сравнить полученный результат с реальным расположением квартир по районам. В качестве района рассматривать Ленинский, Орджоникидзевский, Правобережный, Орджоникидзевский (Левый берег) и Ленинский (левый берег).

**Резальтаты**

Решение с помошью кластерного анализа: [clustering.ipynb](clustering.ipynb)

Решение с помощью методов классификации [knn.ipynb](knn.ipynb)