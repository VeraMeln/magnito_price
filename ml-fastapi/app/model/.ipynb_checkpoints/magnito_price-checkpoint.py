{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "2c2626ae-a809-4048-bdcd-daa59cc7b75d",
   "metadata": {},
   "source": [
    "# Модель стоимости жилья в Магнитогорске"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "29994b28-1fd9-468a-a22d-c5ec6aa02738",
   "metadata": {},
   "source": [
    "**id для демонстрации на собеседовании**\n",
    "id = 3, 37, 82"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e7ea8e44-32e5-49d6-b6bc-238885645f0e",
   "metadata": {},
   "source": [
    "## Введение"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c5b0168d-d84e-437e-8ade-46b5d6d1cb00",
   "metadata": {},
   "source": [
    "**Задача**\n",
    "\n",
    "Построить математическую модель стоимости жилья в зависимости от параметров этого жилья.\n",
    "\n",
    "\n",
    "Модель должна иметь REST API. На вход модели подаются параметры квартиры в формате JSON на выходе получается цена квартиры в формате JSON.\n",
    "\r\n",
    "Испытание проводится в режиме демонстрации экрана на собеседовании. Модель тестируется на 3х квартирах на выбор кандидата. (Просьба подготовить исходные данные (запросы) заранее)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2404ee59-c5e5-4cf1-93b5-2c4f0170e0bd",
   "metadata": {},
   "source": [
    "\n",
    "**Данные**\n",
    "\n",
    "\n",
    "В качестве источника исходных данных предлагается использовать данные сайта магнитогорской недвижимости www.citystar.ru.\n",
    "\n",
    "Размер выборки исходных данных не имеет значения, однако она должна быть представительной (не следует делать ее слишком большой, т.к. задача тестовая).\n",
    "\n",
    "Данные должны быть загружены в базу данных."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "09f28052-6e75-439d-bf1e-660f0a1048e6",
   "metadata": {},
   "source": [
    "## Импорт библиотек и загрузка данных"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "5bd465e7-4ee0-44b5-ab0b-fe7217837dea",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sqlite3\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import pickle\n",
    "\n",
    "from sklearn.model_selection import train_test_split, GridSearchCV\n",
    "from sklearn.base import BaseEstimator, TransformerMixin\n",
    "from sklearn.compose import ColumnTransformer\n",
    "from sklearn.preprocessing import OrdinalEncoder, StandardScaler\n",
    "from sklearn.pipeline import Pipeline\n",
    "from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error\n",
    ", \n",
    "RANDOM_STATE = 12345"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a846f2ee-b8da-4aff-8e3b-790a034e7cfb",
   "metadata": {},
   "outputs": [],
   "source": [
    "# подключаемся к базе данных\n",
    "cnx = sqlite3.connect('db/magnitogorsk.db')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "b1e0d78b-6818-48b6-b14c-600aae7104f7",
   "metadata": {},
   "outputs": [],
   "source": [
    "# загружаем данные\n",
    "data = pd.read_sql_query(\"SELECT * FROM offers\", cnx)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "13e0f458-562e-424d-9e6a-a55da04cad45",
   "metadata": {},
   "outputs": [],
   "source": [
    "# закрываем соединение с базой данных\n",
    "cnx.close()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "adc068c7-4d44-4567-97e3-12ae752cf902",
   "metadata": {},
   "source": [
    "## Первичное знакомство с данными"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "9e5381df-7762-4244-8eb7-ff621b4697ae",
   "metadata": {},
   "outputs": [],
   "source": [
    "def first_look(df, num_of_srtings=5):\n",
    "    print('Общая информация')\n",
    "    display(df.info())\n",
    "    \n",
    "    print(f'Первые {num_of_srtings} строк(и) данных')\n",
    "    display(df.head(num_of_srtings))\n",
    "    \n",
    "    print('Основные статистические характеристики данных')\n",
    "    display(df.describe())\n",
    "    print('Количество пропусков:')\n",
    "    print(df.isna().sum())\n",
    "    print()\n",
    "    \n",
    "    print('Количество дубликатов:', df.duplicated().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "f53d6f4e-af9b-44f6-b71e-ff8d5948842d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Общая информация\n",
      "<class 'pandas.core.frame.DataFrame'>\n",
      "RangeIndex: 456 entries, 0 to 455\n",
      "Data columns (total 9 columns):\n",
      " #   Column          Non-Null Count  Dtype  \n",
      "---  ------          --------------  -----  \n",
      " 0   id              456 non-null    int64  \n",
      " 1   type            445 non-null    object \n",
      " 2   district        254 non-null    object \n",
      " 3   adress          456 non-null    object \n",
      " 4   floor           456 non-null    object \n",
      " 5   total_square    456 non-null    float64\n",
      " 6   living_square   456 non-null    float64\n",
      " 7   kitchen_square  456 non-null    float64\n",
      " 8   price           456 non-null    int64  \n",
      "dtypes: float64(3), int64(2), object(4)\n",
      "memory usage: 32.2+ KB\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "None"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Первые 5 строк(и) данных\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1</td>\n",
       "      <td>Трехкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 145/2</td>\n",
       "      <td>1/5</td>\n",
       "      <td>64.0</td>\n",
       "      <td>43.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>3750</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>Ленинский</td>\n",
       "      <td>Октябрьская 12</td>\n",
       "      <td>2/5</td>\n",
       "      <td>87.2</td>\n",
       "      <td>60.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>8300</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>3</td>\n",
       "      <td>Однокомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 135</td>\n",
       "      <td>6/14</td>\n",
       "      <td>36.1</td>\n",
       "      <td>20.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3330</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>4</td>\n",
       "      <td>Трехкомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 129</td>\n",
       "      <td>5/16</td>\n",
       "      <td>105.0</td>\n",
       "      <td>75.0</td>\n",
       "      <td>14.0</td>\n",
       "      <td>7700</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>5</td>\n",
       "      <td>Двухкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Сиреневый проезд 12</td>\n",
       "      <td>7/9</td>\n",
       "      <td>50.6</td>\n",
       "      <td>43.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3800</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   id                         type           district               adress  \\\n",
       "0   1     Трехкомнатная улучшенная  Орджоникидзевский    Ленина пр-т 145/2   \n",
       "1   2               Трехкомнатная           Ленинский       Октябрьская 12   \n",
       "2   3  Однокомнатная нестандартная  Орджоникидзевский      Ленина пр-т 135   \n",
       "3   4  Трехкомнатная нестандартная  Орджоникидзевский      Ленина пр-т 129   \n",
       "4   5     Двухкомнатная улучшенная  Орджоникидзевский  Сиреневый проезд 12   \n",
       "\n",
       "  floor  total_square  living_square  kitchen_square  price  \n",
       "0   1/5          64.0           43.0             8.0   3750  \n",
       "1   2/5          87.2           60.0             9.0   8300  \n",
       "2  6/14          36.1           20.0             9.0   3330  \n",
       "3  5/16         105.0           75.0            14.0   7700  \n",
       "4   7/9          50.6           43.0             9.0   3800  "
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Основные статистические характеристики данных\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>count</th>\n",
       "      <td>456.00000</td>\n",
       "      <td>456.000000</td>\n",
       "      <td>456.000000</td>\n",
       "      <td>456.000000</td>\n",
       "      <td>456.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>mean</th>\n",
       "      <td>228.50000</td>\n",
       "      <td>53.514912</td>\n",
       "      <td>32.120175</td>\n",
       "      <td>8.771250</td>\n",
       "      <td>3744.561404</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>std</th>\n",
       "      <td>131.78012</td>\n",
       "      <td>21.751910</td>\n",
       "      <td>17.343334</td>\n",
       "      <td>4.007841</td>\n",
       "      <td>1631.107124</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>min</th>\n",
       "      <td>1.00000</td>\n",
       "      <td>14.100000</td>\n",
       "      <td>0.000000</td>\n",
       "      <td>0.000000</td>\n",
       "      <td>0.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>25%</th>\n",
       "      <td>114.75000</td>\n",
       "      <td>40.175000</td>\n",
       "      <td>19.000000</td>\n",
       "      <td>6.000000</td>\n",
       "      <td>2700.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>50%</th>\n",
       "      <td>228.50000</td>\n",
       "      <td>50.000000</td>\n",
       "      <td>30.000000</td>\n",
       "      <td>8.050000</td>\n",
       "      <td>3500.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>75%</th>\n",
       "      <td>342.25000</td>\n",
       "      <td>65.000000</td>\n",
       "      <td>43.000000</td>\n",
       "      <td>10.000000</td>\n",
       "      <td>4600.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>max</th>\n",
       "      <td>456.00000</td>\n",
       "      <td>220.000000</td>\n",
       "      <td>150.000000</td>\n",
       "      <td>30.000000</td>\n",
       "      <td>10000.000000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "              id  total_square  living_square  kitchen_square         price\n",
       "count  456.00000    456.000000     456.000000      456.000000    456.000000\n",
       "mean   228.50000     53.514912      32.120175        8.771250   3744.561404\n",
       "std    131.78012     21.751910      17.343334        4.007841   1631.107124\n",
       "min      1.00000     14.100000       0.000000        0.000000      0.000000\n",
       "25%    114.75000     40.175000      19.000000        6.000000   2700.000000\n",
       "50%    228.50000     50.000000      30.000000        8.050000   3500.000000\n",
       "75%    342.25000     65.000000      43.000000       10.000000   4600.000000\n",
       "max    456.00000    220.000000     150.000000       30.000000  10000.000000"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Количество пропусков:\n",
      "id                  0\n",
      "type               11\n",
      "district          202\n",
      "adress              0\n",
      "floor               0\n",
      "total_square        0\n",
      "living_square       0\n",
      "kitchen_square      0\n",
      "price               0\n",
      "dtype: int64\n",
      "\n",
      "Количество дубликатов: 0\n"
     ]
    }
   ],
   "source": [
    "first_look(data)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0c6b9a30-5595-481d-951b-bdb8198c5731",
   "metadata": {},
   "source": [
    "Посмотрим, есть ли в данных дубликаты, если мы не будем учитывать столбец id."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "0e935065-a2a3-4b02-a72e-90bf54abcf37",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Количество дубликатов: 2\n"
     ]
    }
   ],
   "source": [
    "print('Количество дубликатов:', data.drop('id', axis=1).duplicated().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "a5db09cb-6585-4404-b1a8-1f1e1d61f3b6",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>354</th>\n",
       "      <td>355</td>\n",
       "      <td>Двухкомнатная раздельная</td>\n",
       "      <td>Орджоникидзевский (левый берег)</td>\n",
       "      <td>Трамвайная 25</td>\n",
       "      <td>1/3</td>\n",
       "      <td>43.0</td>\n",
       "      <td>31.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>2350</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>413</th>\n",
       "      <td>414</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>Правобережный</td>\n",
       "      <td>Им. газеты \"Правда\" 23</td>\n",
       "      <td>4/5</td>\n",
       "      <td>46.1</td>\n",
       "      <td>29.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>2600</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "      id                      type                         district  \\\n",
       "354  355  Двухкомнатная раздельная  Орджоникидзевский (левый берег)   \n",
       "413  414            Двухкомнатная                     Правобережный   \n",
       "\n",
       "                     adress floor  total_square  living_square  \\\n",
       "354           Трамвайная 25   1/3          43.0           31.0   \n",
       "413  Им. газеты \"Правда\" 23   4/5          46.1           29.0   \n",
       "\n",
       "     kitchen_square  price  \n",
       "354             6.0   2350  \n",
       "413             6.0   2600  "
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data.drop('id', axis=1).duplicated()]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "c09ee71b-eafa-4019-99a8-7866f57aa537",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(456, 9)"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "98066ede-ff30-4cc1-9512-9d251db4d392",
   "metadata": {},
   "outputs": [],
   "source": [
    "data.drop_duplicates(\n",
    "    subset=['type', 'district', 'adress', 'floor', 'total_square', 'living_square', 'kitchen_square', 'price'],\n",
    "    inplace=True\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "47798c8f-82b4-4098-ab1d-0f5b0e8b7ca2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(454, 9)"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.shape"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e75c0a57-1a23-4493-819d-f830b03af1af",
   "metadata": {},
   "source": [
    "### Цена"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "04f8b4a1-a767-4fa1-bc12-e4e93d816da3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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",
      "text/plain": [
       "<Figure size 1200x500 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "data['price'].plot(figsize=(12, 5));"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "394cf70f-19d2-409e-a70e-f79dc273a13b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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5uL48eMAeK7i7b777sNbb72FDz/8ECUlJfLtw3m/czgcQ77upPsous53roayePFiABj0uuK5ig+z2YwpU6agvLwcGzZswLx58/Bv//ZvfE2p0PnO1VD4mlJGVVUVWlpasHDhQhiNRhiNRmzfvh3PP/88jEYjCgoK+LpSiYudq1AodM7XJNvrioH2Wbq7u3HixAkUFhaivLwcJpMJW7dule8/cuQIamtrB+3pofiaOHEiHA7HoPPidruxc+dO+bxUVFTA5XKhqqpKPmbbtm0QBEF+kZMy6uvr0d7ejsLCQgA8V/EiiiLuu+8+vPrqq9i2bRsmTpw46P7hvN9VVFSgurp60AcjW7ZsQUZGhlx+SWN3sXM1lL179wLAoNcVz5UyBEGAz+fja0oDpHM1FL6mlLFkyRJUV1dj79698p9FixbhjjvukP/O15U6XOxcGQyGc74m6V5XSndjU9r3v/998aOPPhJPnTolfvbZZ2JlZaWYm5srtrS0iKIoin//938vjhs3Tty2bZu4e/dusaKiQqyoqFB41YnP4/GIX331lfjVV1+JAMSf//zn4ldffSWeOXNGFEVRfPrpp8XMzEzx9ddfF/fv3y+uXLlSnDhxotjX1yc/xrJly8QFCxaIO3fuFD/99FNx6tSp4l/91V8p9S0lrAudK4/HI/7TP/2TuGPHDvHUqVPiBx98IC5cuFCcOnWq6PV65cfguYq9e++9V7Tb7eJHH30kNjU1yX96e3vlYy72fhcMBsU5c+aIN954o7h3715x8+bNYl5enrh+/XolvqWEdbFzdfz4cfGJJ54Qd+/eLZ46dUp8/fXXxUmTJolXX321/Bg8V/Hx0EMPidu3bxdPnTol7t+/X3zooYdEnU4nvv/++6Io8jWlJhc6V3xNqdvZnav5ulKvgeeKrytRTPpA+2tf+5pYWFgoms1msbi4WPza174mHj9+XL6/r69P/Id/+AcxKytLTElJEW+//XaxqalJwRUnhw8//FAEcM6fO++8UxTF8IivRx55RCwoKBAtFou4ZMkS8ciRI4Meo729Xfyrv/orMS0tTczIyBC/9a1viR6PR4HvJrFd6Fz19vaKN954o5iXlyeaTCZx/Pjx4t133z1ojIMo8lzFw1DnCID429/+Vj5mOO93p0+fFpcvXy7abDYxNzdX/P73vy8GAoE4fzeJ7WLnqra2Vrz66qvF7Oxs0WKxiFOmTBEffPBBsaura9Dj8FzF3t/93d+J48ePF81ms5iXlycuWbJEDrJFka8pNbnQueJrSt3ODrT5ulKvgeeKrytR1ImiKMYvf05ERERERESU2LhHm4iIiIiIiCiKGGgTERERERERRREDbSIiIiIiIqIoYqBNREREREREFEUMtImIiIiIiIiiiIE2ERERERERURQx0CYiIiIiIiKKIgbaRERERERERFHEQJuIiIiIiIgoihhoExEREREREUURA20iIiIiIiKiKPr/ASkvi+T6jH9zAAAAAElFTkSuQmCC",
      "text/plain": [
       "<Figure size 1200x500 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "data[data['price'] < 1000]['price'].plot(figsize=(12, 5));"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "d13f357e-8e09-4c56-95db-d21a6641d549",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "3.0837004405286343"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data['price'] < 800].shape[0] / data.shape[0] * 100"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "0d5db257-f9e6-4177-a6a4-142745aa2081",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>58</th>\n",
       "      <td>59</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Школьная 10</td>\n",
       "      <td>1/1</td>\n",
       "      <td>59.5</td>\n",
       "      <td>47.0</td>\n",
       "      <td>12.0</td>\n",
       "      <td>500</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>61</th>\n",
       "      <td>62</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Новая 1/5</td>\n",
       "      <td>1/2</td>\n",
       "      <td>47.0</td>\n",
       "      <td>29.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>550</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>63</th>\n",
       "      <td>64</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Новая 1/5</td>\n",
       "      <td>1/2</td>\n",
       "      <td>47.0</td>\n",
       "      <td>29.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>480</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>73</th>\n",
       "      <td>74</td>\n",
       "      <td>Однокомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Первомайская 16</td>\n",
       "      <td>2/4</td>\n",
       "      <td>42.6</td>\n",
       "      <td>20.0</td>\n",
       "      <td>15.0</td>\n",
       "      <td>0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>141</th>\n",
       "      <td>142</td>\n",
       "      <td>Однокомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Труда 47</td>\n",
       "      <td>4/9</td>\n",
       "      <td>32.0</td>\n",
       "      <td>19.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>173</th>\n",
       "      <td>174</td>\n",
       "      <td>Однокомнатная малосемейка</td>\n",
       "      <td>Правобережный</td>\n",
       "      <td>Советской Армии 37/1</td>\n",
       "      <td>4/9</td>\n",
       "      <td>22.0</td>\n",
       "      <td>12.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>294</th>\n",
       "      <td>295</td>\n",
       "      <td>Однокомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Привокзальная 29кв1</td>\n",
       "      <td>1/1</td>\n",
       "      <td>42.5</td>\n",
       "      <td>22.0</td>\n",
       "      <td>12.0</td>\n",
       "      <td>450</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>332</th>\n",
       "      <td>333</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Российская 7</td>\n",
       "      <td>2/2</td>\n",
       "      <td>45.0</td>\n",
       "      <td>31.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>500</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>373</th>\n",
       "      <td>374</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>ул Черемушки 13</td>\n",
       "      <td>2/2</td>\n",
       "      <td>40.0</td>\n",
       "      <td>22.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>500</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>389</th>\n",
       "      <td>390</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Труда 2</td>\n",
       "      <td>1/2</td>\n",
       "      <td>63.4</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>530</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>399</th>\n",
       "      <td>400</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>ул Репина 12</td>\n",
       "      <td>1/1</td>\n",
       "      <td>55.0</td>\n",
       "      <td>39.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>416</th>\n",
       "      <td>417</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>сад Горняк</td>\n",
       "      <td>1/1</td>\n",
       "      <td>50.0</td>\n",
       "      <td>29.0</td>\n",
       "      <td>5.0</td>\n",
       "      <td>550</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>429</th>\n",
       "      <td>430</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>None</td>\n",
       "      <td>Центральная 3</td>\n",
       "      <td>2/2</td>\n",
       "      <td>44.0</td>\n",
       "      <td>30.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>450</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "      id                       type           district                adress  \\\n",
       "58    59             Трехкомнатная                None           Школьная 10   \n",
       "61    62             Двухкомнатная                None             Новая 1/5   \n",
       "63    64             Двухкомнатная                None             Новая 1/5   \n",
       "73    74             Однокомнатная                None       Первомайская 16   \n",
       "141  142             Однокомнатная                None              Труда 47   \n",
       "173  174  Однокомнатная малосемейка      Правобережный  Советской Армии 37/1   \n",
       "294  295             Однокомнатная                None   Привокзальная 29кв1   \n",
       "332  333             Двухкомнатная                None          Российская 7   \n",
       "373  374             Двухкомнатная                None       ул Черемушки 13   \n",
       "389  390             Трехкомнатная                None               Труда 2   \n",
       "399  400             Трехкомнатная   Орджоникидзевский          ул Репина 12   \n",
       "416  417             Трехкомнатная                None           сад Горняк    \n",
       "429  430             Двухкомнатная                None         Центральная 3   \n",
       "\n",
       "    floor  total_square  living_square  kitchen_square  price  \n",
       "58    1/1          59.5           47.0            12.0    500  \n",
       "61    1/2          47.0           29.0             8.0    550  \n",
       "63    1/2          47.0           29.0             8.0    480  \n",
       "73    2/4          42.6           20.0            15.0      0  \n",
       "141   4/9          32.0           19.0             6.0      0  \n",
       "173   4/9          22.0           12.0             6.0      1  \n",
       "294   1/1          42.5           22.0            12.0    450  \n",
       "332   2/2          45.0           31.0             6.0    500  \n",
       "373   2/2          40.0           22.0             6.0    500  \n",
       "389   1/2          63.4            0.0             0.0    530  \n",
       "399   1/1          55.0           39.0             6.0      0  \n",
       "416   1/1          50.0           29.0             5.0    550  \n",
       "429   2/2          44.0           30.0             8.0    450  "
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data['price'] < 600]"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8e8be602-95bc-40ed-9e0a-9725f0b20ac6",
   "metadata": {},
   "source": [
    "Для трех квартир цена не указана, поэтому удалим эти строки, так как они не подходят ни для обучения модели ни для контроля качества. \n",
    "\n",
    "Количество квартир с нетипично низкой ценой составляет около 3 % данных. Удалим их, чтобы модель смогла точнее выявить закономерность."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "ec8fb70e-0c24-442d-aca0-0896268ce052",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(454, 9)"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# контроль размерности\n",
    "data.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "25e8f942-e643-4d87-909e-d0b96dfc1e19",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = data[data['price'] >= 800]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "8002012f-c218-4ba6-ba8f-2411fc3a880f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(440, 9)"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# контроль размерности\n",
    "data.shape"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "239b1631-ea6a-47d8-9036-823163e77e03",
   "metadata": {},
   "source": [
    "### Этаж"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "6d682fca-6144-451d-ac55-b9cab4de92b8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['floor'].isna().sum()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "bd37bdf2-a9ec-43be-a6b7-dac0ff13cf28",
   "metadata": {},
   "source": [
    "Первоначально генерировала характеристики «первый этаж», «последний этаж». Но после анализа работы лучшей модели, выяснилось, что эти характеристики в рейтинге полезности заняли последние места, а модель, обученная без них, дает более высокие оценки."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "27bca13a-d972-44b4-82e2-5b2ad44c32ae",
   "metadata": {},
   "source": [
    "### Тип квартиры"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0a676db7-00c1-4c36-9a7f-511792de3615",
   "metadata": {},
   "source": [
    "В столбце с типом квартиры хранятся данные о количестве комнат и типе квартиры. Разделим их и сохраним в двух разных столбцах."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "dcffb3c8-3a42-497b-b759-a99918ef7779",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "11"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['type'].isna().sum()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "3415cbfa-927c-4749-8ce9-22970668f45e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2.5"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['type'].isna().sum() / data.shape[0] * 100"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "c4e0fe04-fa0c-45ca-bf98-366d0a562f46",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>59</th>\n",
       "      <td>60</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Ленина пр-т 212а</td>\n",
       "      <td>1/1</td>\n",
       "      <td>18.4</td>\n",
       "      <td>12.0</td>\n",
       "      <td>5.0</td>\n",
       "      <td>1100</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>83</th>\n",
       "      <td>84</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Карла Маркса 233</td>\n",
       "      <td>8/10</td>\n",
       "      <td>70.0</td>\n",
       "      <td>50.0</td>\n",
       "      <td>7.0</td>\n",
       "      <td>4860</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>97</th>\n",
       "      <td>98</td>\n",
       "      <td>None</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Завенягина 1</td>\n",
       "      <td>5/9</td>\n",
       "      <td>65.1</td>\n",
       "      <td>44.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>4750</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>140</th>\n",
       "      <td>141</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Торфяная 5/2</td>\n",
       "      <td>1/2</td>\n",
       "      <td>46.8</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>4950</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>161</th>\n",
       "      <td>162</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Карла Маркса 119/1</td>\n",
       "      <td>2/5</td>\n",
       "      <td>41.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>3600</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>162</th>\n",
       "      <td>163</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Карла Маркса 117</td>\n",
       "      <td>2/5</td>\n",
       "      <td>41.0</td>\n",
       "      <td>26.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>3400</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>163</th>\n",
       "      <td>164</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>ул Жукова 17/1</td>\n",
       "      <td>4/9</td>\n",
       "      <td>40.1</td>\n",
       "      <td>18.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3100</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>176</th>\n",
       "      <td>177</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Западное шоссе 101</td>\n",
       "      <td>2/3</td>\n",
       "      <td>68.0</td>\n",
       "      <td>40.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>6000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>355</th>\n",
       "      <td>356</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>ул Лесопарковая 93/1</td>\n",
       "      <td>10/10</td>\n",
       "      <td>41.2</td>\n",
       "      <td>28.0</td>\n",
       "      <td>12.5</td>\n",
       "      <td>3150</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>365</th>\n",
       "      <td>366</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Ленина пр-т 114/4</td>\n",
       "      <td>5/14</td>\n",
       "      <td>40.0</td>\n",
       "      <td>18.0</td>\n",
       "      <td>13.0</td>\n",
       "      <td>2620</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>387</th>\n",
       "      <td>388</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>Ленина пр-т 87а</td>\n",
       "      <td>6/14</td>\n",
       "      <td>45.0</td>\n",
       "      <td>37.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>2800</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "      id  type           district                adress  floor  total_square  \\\n",
       "59    60  None               None      Ленина пр-т 212а    1/1          18.4   \n",
       "83    84  None               None      Карла Маркса 233   8/10          70.0   \n",
       "97    98  None  Орджоникидзевский          Завенягина 1    5/9          65.1   \n",
       "140  141  None               None          Торфяная 5/2    1/2          46.8   \n",
       "161  162  None               None    Карла Маркса 119/1    2/5          41.0   \n",
       "162  163  None               None      Карла Маркса 117    2/5          41.0   \n",
       "163  164  None               None        ул Жукова 17/1    4/9          40.1   \n",
       "176  177  None               None    Западное шоссе 101    2/3          68.0   \n",
       "355  356  None               None  ул Лесопарковая 93/1  10/10          41.2   \n",
       "365  366  None               None     Ленина пр-т 114/4   5/14          40.0   \n",
       "387  388  None               None       Ленина пр-т 87а   6/14          45.0   \n",
       "\n",
       "     living_square  kitchen_square  price  \n",
       "59            12.0             5.0   1100  \n",
       "83            50.0             7.0   4860  \n",
       "97            44.0             8.0   4750  \n",
       "140            0.0             0.0   4950  \n",
       "161            0.0             6.0   3600  \n",
       "162           26.0             6.0   3400  \n",
       "163           18.0             9.0   3100  \n",
       "176           40.0             0.0   6000  \n",
       "355           28.0            12.5   3150  \n",
       "365           18.0            13.0   2620  \n",
       "387           37.0             8.0   2800  "
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data['type'].isna()]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "c8ea91cc-b9bc-4d4d-a189-a660a0c38599",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = data[data['type'].notna()]"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "20c0ff1f-5bf9-4ff1-aeaa-ba9af9a3c893",
   "metadata": {},
   "source": [
    "### Улица"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "1ce66fad-de6e-472f-b2fb-e28a8c97c71c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(4, 9)"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data['adress'] == ' '].shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "1c656172-75ad-4723-9dc0-bac56ef8dce4",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = data[data['adress'] != ' ']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "a95cdfbf-55bf-406f-9f3b-85d24b1a4dd9",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "366"
      ]
     },
     "execution_count": 26,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# sorted(data['adress'].unique())\n",
    "data['adress'].nunique()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "cc49fd9f-882a-4007-97af-90e72c02f015",
   "metadata": {},
   "source": [
    "### Район"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "88ae5b92-9b31-418f-b66a-6e8dfe267ec7",
   "metadata": {},
   "source": [
    "Посмотрим количество пропусков в столбце с данными о районе."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "e3b97046-e8e6-48ff-acc6-2953748038a6",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "176"
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['district'].isna().sum()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "46109abb-282b-4a5a-96b2-9459a3be2d56",
   "metadata": {},
   "source": [
    "Заполним пропуски значением 'неизвестно'."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6edc7abf-c50c-4840-a9e6-44a573bb1807",
   "metadata": {},
   "source": [
    "## Построение модели"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "b574cd27-785f-47a3-a571-c8479dc542be",
   "metadata": {},
   "source": [
    "### Предварительна обработка данных"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ccc7260e-c8cb-40a3-bf1f-a464b20b2e73",
   "metadata": {},
   "source": [
    "Разделим характеристики и целевую переменную."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "e84bff10-f328-4e06-8cec-384dc09df959",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1</td>\n",
       "      <td>Трехкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 145/2</td>\n",
       "      <td>1/5</td>\n",
       "      <td>64.0</td>\n",
       "      <td>43.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>3750</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>Ленинский</td>\n",
       "      <td>Октябрьская 12</td>\n",
       "      <td>2/5</td>\n",
       "      <td>87.2</td>\n",
       "      <td>60.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>8300</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>3</td>\n",
       "      <td>Однокомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 135</td>\n",
       "      <td>6/14</td>\n",
       "      <td>36.1</td>\n",
       "      <td>20.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3330</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>4</td>\n",
       "      <td>Трехкомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 129</td>\n",
       "      <td>5/16</td>\n",
       "      <td>105.0</td>\n",
       "      <td>75.0</td>\n",
       "      <td>14.0</td>\n",
       "      <td>7700</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>5</td>\n",
       "      <td>Двухкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Сиреневый проезд 12</td>\n",
       "      <td>7/9</td>\n",
       "      <td>50.6</td>\n",
       "      <td>43.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3800</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   id                         type           district               adress  \\\n",
       "0   1     Трехкомнатная улучшенная  Орджоникидзевский    Ленина пр-т 145/2   \n",
       "1   2               Трехкомнатная           Ленинский       Октябрьская 12   \n",
       "2   3  Однокомнатная нестандартная  Орджоникидзевский      Ленина пр-т 135   \n",
       "3   4  Трехкомнатная нестандартная  Орджоникидзевский      Ленина пр-т 129   \n",
       "4   5     Двухкомнатная улучшенная  Орджоникидзевский  Сиреневый проезд 12   \n",
       "\n",
       "  floor  total_square  living_square  kitchen_square  price  \n",
       "0   1/5          64.0           43.0             8.0   3750  \n",
       "1   2/5          87.2           60.0             9.0   8300  \n",
       "2  6/14          36.1           20.0             9.0   3330  \n",
       "3  5/16         105.0           75.0            14.0   7700  \n",
       "4   7/9          50.6           43.0             9.0   3800  "
      ]
     },
     "execution_count": 28,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "fb744a56-b2cb-4ca5-a3f8-b302ca090e3a",
   "metadata": {},
   "outputs": [],
   "source": [
    "features = data.drop(['id', 'price'], axis=1)\n",
    "target = data['price']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "3350556c-0542-4f85-a12c-93be420ce0bd",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Трехкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 145/2</td>\n",
       "      <td>1/5</td>\n",
       "      <td>64.0</td>\n",
       "      <td>43.0</td>\n",
       "      <td>8.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>Ленинский</td>\n",
       "      <td>Октябрьская 12</td>\n",
       "      <td>2/5</td>\n",
       "      <td>87.2</td>\n",
       "      <td>60.0</td>\n",
       "      <td>9.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Однокомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 135</td>\n",
       "      <td>6/14</td>\n",
       "      <td>36.1</td>\n",
       "      <td>20.0</td>\n",
       "      <td>9.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Трехкомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 129</td>\n",
       "      <td>5/16</td>\n",
       "      <td>105.0</td>\n",
       "      <td>75.0</td>\n",
       "      <td>14.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Двухкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Сиреневый проезд 12</td>\n",
       "      <td>7/9</td>\n",
       "      <td>50.6</td>\n",
       "      <td>43.0</td>\n",
       "      <td>9.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                          type           district               adress floor  \\\n",
       "0     Трехкомнатная улучшенная  Орджоникидзевский    Ленина пр-т 145/2   1/5   \n",
       "1               Трехкомнатная           Ленинский       Октябрьская 12   2/5   \n",
       "2  Однокомнатная нестандартная  Орджоникидзевский      Ленина пр-т 135  6/14   \n",
       "3  Трехкомнатная нестандартная  Орджоникидзевский      Ленина пр-т 129  5/16   \n",
       "4     Двухкомнатная улучшенная  Орджоникидзевский  Сиреневый проезд 12   7/9   \n",
       "\n",
       "   total_square  living_square  kitchen_square  \n",
       "0          64.0           43.0             8.0  \n",
       "1          87.2           60.0             9.0  \n",
       "2          36.1           20.0             9.0  \n",
       "3         105.0           75.0            14.0  \n",
       "4          50.6           43.0             9.0  "
      ]
     },
     "execution_count": 30,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "features.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "f96a68c9-382b-4b43-96b4-f6fe21c514b8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    3750\n",
       "1    8300\n",
       "2    3330\n",
       "3    7700\n",
       "4    3800\n",
       "Name: price, dtype: int64"
      ]
     },
     "execution_count": 31,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "target.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ad4231ab-7f2b-487e-81d3-201cf0714d9a",
   "metadata": {},
   "source": [
    "### Трансформер для предварительной обработки данных"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a3e9755b-bf19-4bba-a4dd-757da5793297",
   "metadata": {},
   "source": [
    "Напишем два трансформера для предварительной обработки данных\n",
    "\n",
    "**Чистка данных**\n",
    "- 'adress': у названий улиц уберем номера домов\n",
    "- 'adress': в названиях улиц исправим неявные дубликаты\n",
    "- 'district': исправим неявные дубликаты\n",
    "\n",
    "**Преобразование характеристик**\n",
    "    \n",
    "- 'floor': добавляем столбец с номером этажа\n",
    "- 'floor': добавляем столбец с общим количеством этажей в доме.\n",
    "- 'type': добавляем столбец с количеством комнат\n",
    "- 'type': добавляем столбец с типом планировки. пропуски заполняем значением «неизвестно»\n",
    "- 'floor': удалим, потому что вместо него будем использовать столбцы, сгенерированные на его основе \n",
    "- 'type': удалим, потому что вместо него будем использовать столбцы, сгенерированные на его основе \n",
    "- 'adress': удалим, потому что вместо него будем использовать столбцы, сгенерированные на его основе\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "f2b88aaa-12de-4e11-849c-c9bc513c6fe5",
   "metadata": {},
   "outputs": [],
   "source": [
    "class DataCleaner(BaseEstimator, TransformerMixin):\n",
    "    '''\n",
    "    Класс для обработки неявных дубликатов и пропусков\n",
    "    '''\n",
    "    def __init__(self):\n",
    "        self.districts_to_replace = {\n",
    "            'ленинский' : 'Ленинский',\n",
    "            'Орджоникидзевский район' : 'Орджоникидзевский',\n",
    "            'Орджо' : 'Орджоникидзевский',\n",
    "            'правобережный' : 'Правобережный'\n",
    "        }\n",
    "        self.streets_to_replace = {\n",
    "            'зеленый лог' : 'Зеленый Лог',\n",
    "            'Зеленый лог' : 'Зеленый Лог',\n",
    "            'Зеленый лог 30 к' : 'Зеленый Лог',\n",
    "            'Им. газеты \\\\\"Правда\\\\\"' : 'имени газеты Правда',\n",
    "            'Им. газеты \"Правда\"' : 'имени газеты Правда',\n",
    "            'проспект Сиреневый' : 'Сиреневый проезд',\n",
    "            'карла маркса' : 'Карла Маркса',\n",
    "            '50 лет Магнитки' : '50-летия Магнитки',\n",
    "            'Ленина пр-т 210' : 'Ленина пр-т',\n",
    "            'Советский переулок 12' : 'Советский переулок',\n",
    "            '26 Горнолыжная' : 'Горнолыжная'\n",
    "        }\n",
    "        \n",
    "    def __get_street(self, row):\n",
    "        dirt = ['ул. ', 'ул.', 'ул ', 'пр.']\n",
    "        for dot in dirt:\n",
    "            if dot in row:\n",
    "                row = row.replace(dot, '')\n",
    "        if row.find('. ') == 0:\n",
    "            row = row[2:]\n",
    "        return row[: row.rfind(' ')]\n",
    "    \n",
    "    def fit(self, X):\n",
    "        return self\n",
    "\n",
    "    def transform(self, X):\n",
    "         \n",
    "        # обработка дубликатов и пропусков района\n",
    "        X['district'].replace(to_replace=self.districts_to_replace, inplace=True)\n",
    "        X['district'].fillna('неизвестно', inplace=True)\n",
    "        \n",
    "        # обработка дубликатов улиц\n",
    "        X['adress'] = X['adress'].apply(self.__get_street)\n",
    "        X['adress'].replace(to_replace=self.streets_to_replace, inplace=True)\n",
    "                        \n",
    "        return X"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "ca91d7dc-7038-4d6f-8194-c763fb9e3951",
   "metadata": {},
   "outputs": [],
   "source": [
    "class FeaturesTransformer(BaseEstimator, TransformerMixin):\n",
    "    '''\n",
    "    Класс для преобразования характеристик.\n",
    "    \n",
    "    Добавляет:\n",
    "        floor_num - номер этажа\n",
    "        total_floors - общее количество этажей\n",
    "        num_of_rooms - количество комнат\n",
    "        flat_type - тип планировки\n",
    "\n",
    "    Удаляет: \n",
    "        floor - так как заменен на два более информативных признака\n",
    "        type - так как заменен на два более информативных признака\n",
    "    '''\n",
    "    columns_ = [\n",
    "        'district', \n",
    "        'adress', \n",
    "        'total_square', \n",
    "        'living_square', \n",
    "        'kitchen_square', \n",
    "        'floor_num', \n",
    "        'total_floors', \n",
    "        'num_of_rooms', \n",
    "        'flat_type'\n",
    "    ]\n",
    "    def __init__(self):\n",
    "        pass\n",
    "        \n",
    "    def __get_floor_num(self, row):\n",
    "        return int(row[:row.find('/')])\n",
    "    \n",
    "    def __get_total_floors(self, row):\n",
    "        return int(row[row.find('/')+1:])\n",
    "\n",
    "    def __get_num_of_rooms(self, row):\n",
    "        return row[: row.find(' ')] if row.find(' ') > 0 else None\n",
    "\n",
    "    def __get_flat_type(self, row):\n",
    "        return 'неизвестно' if (len(row) - row.find(' ') == 1) or (row.find(' ') == -1) else row[row.find(' ')+1:]\n",
    "    \n",
    "    def fit(self, X):\n",
    "        return self\n",
    "\n",
    "    def transform(self, X):\n",
    "         \n",
    "        # номер этажа квартиры\n",
    "        floor_num = X['floor'].apply(self.__get_floor_num)\n",
    "\n",
    "        # общее количество этажей в доме\n",
    "        total_floors = X['floor'].apply(self.__get_total_floors)\n",
    "\n",
    "        num_of_rooms = X['type'].apply(self.__get_num_of_rooms)\n",
    "        flat_type = X['type'].apply(self.__get_flat_type)\n",
    "        \n",
    "        X = pd.DataFrame(np.c_[X.drop(['floor', 'type'], axis=1), floor_num, total_floors, num_of_rooms, flat_type])    \n",
    "        X.columns = self.columns_\n",
    "        return X"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a9926ee8-c2c2-44b6-8f7e-cca5108dc115",
   "metadata": {},
   "source": [
    "Выделим категориальные и числовые признаки."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "83ac31ca-5d0b-4188-9913-10b660988df3",
   "metadata": {},
   "source": [
    "### Подготовка обучающей и валидационной выборки."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4682e01c-5358-4bed-aea2-388eb200c26a",
   "metadata": {},
   "source": [
    "Выделим характеристики, которые будем использовать для обучения модели."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "45c4c7ed-a276-4f91-a306-afc2a43ca330",
   "metadata": {},
   "source": [
    "|столбец|комментарий|\n",
    "|:--|:--|\n",
    "|id|не влияет на цену квартиры|\n",
    "|type|вместо него будем использовать более информативные столбцы, сгенерированные на основе данных из этого столбца|\n",
    "|**district**|может оказывать влияние|\n",
    "|**adress**|может оказывать влияние|\n",
    "|floor|вместо него будем использовать более информативные столбцы, сгенерированные на основе данных из этого столбца|\n",
    "|**total_square**|может оказывать влияние|\n",
    "|**living_square**|может оказывать влияние|\n",
    "|**kitchen_square**|может оказывать влияние|\n",
    "|**price**|целевой признак|\n",
    "|**floor_num**|может оказывать влияние|\n",
    "|**total_floors**|может оказывать влияние|\n",
    "|**num_of_rooms**|может оказывать влияние|\n",
    "|**flat_type**|может оказывать влияние|"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0398c59a-7238-41fb-a273-e932ff8d0216",
   "metadata": {},
   "source": [
    "Разобьем выборки на обучающую и валидационную в отношении 4 : 1."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "27f50d5d-e8e4-461e-8367-5cbcf2ae210d",
   "metadata": {},
   "outputs": [],
   "source": [
    "features_train, features_val, target_train, target_val = train_test_split(\n",
    "    features,\n",
    "    target,\n",
    "    test_size=0.2,\n",
    "    random_state=RANDOM_STATE\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "8cce391e-4266-4cff-a499-0abcf5c8f7a3",
   "metadata": {},
   "outputs": [],
   "source": [
    "numeric = ['total_square', 'living_square', 'kitchen_square',\n",
    "       'floor_num', 'total_floors']\n",
    "categorical = ['district', 'adress', 'num_of_rooms', 'flat_type']"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "53a8c0f0-889b-46b7-94e4-3c35457c2167",
   "metadata": {},
   "source": [
    "Количество комнат попадает в категориальные признаки, потому что содержит значение «многоквартирная», которое нельзя заменить конкретным числовым значением."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "302f19a7-b817-4b7d-a461-82b4dbdbd07c",
   "metadata": {},
   "source": [
    "Преобразуем категориальные признаки в числа с помощью порядкового кодирования. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "id": "29924a4f-0ca3-4665-b394-dfc0b1478da6",
   "metadata": {},
   "outputs": [],
   "source": [
    "# my_pipeline[1].columns_"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "c0156806-8a71-46ff-87d7-a181d7a93163",
   "metadata": {},
   "outputs": [],
   "source": [
    "my_pipeline = Pipeline([\n",
    "    ('data_cleaner', DataCleaner()),\n",
    "    ('features_transformer', FeaturesTransformer()),\n",
    "    ('col_transformer', ColumnTransformer(\n",
    "   transformers=[\n",
    "       ('oe', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value = -1), categorical)\n",
    "       ],\n",
    "    remainder=\"passthrough\",\n",
    "    verbose_feature_names_out=False\n",
    ")),\n",
    "    ('scaler', StandardScaler())\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "14e9eeb5-25c9-4fd9-8e37-4fc912b48690",
   "metadata": {},
   "outputs": [],
   "source": [
    "features_train_piped = pd.DataFrame(my_pipeline.fit_transform(features_train))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "ceae8c79-317a-4c81-85d6-fa8df6a7972a",
   "metadata": {},
   "outputs": [],
   "source": [
    "features_val_piped = pd.DataFrame(my_pipeline.transform(features_val))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "id": "5b0f4455-c54b-4a14-a2b9-eec670e423df",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>num_of_rooms</th>\n",
       "      <th>flat_type</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>floor_num</th>\n",
       "      <th>total_floors</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-1.587622</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-1.431076</td>\n",
       "      <td>-1.115889</td>\n",
       "      <td>-0.963241</td>\n",
       "      <td>0.839670</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-0.667000</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-0.232604</td>\n",
       "      <td>-1.286261</td>\n",
       "      <td>3.935852</td>\n",
       "      <td>0.075312</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>-1.434185</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-1.790338</td>\n",
       "      <td>0.228347</td>\n",
       "      <td>0.587835</td>\n",
       "      <td>-0.473332</td>\n",
       "      <td>0.457491</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>-1.421498</td>\n",
       "      <td>-1.229602</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>1.928315</td>\n",
       "      <td>0.652422</td>\n",
       "      <td>0.241411</td>\n",
       "      <td>0.506487</td>\n",
       "      <td>-0.689046</td>\n",
       "      <td>-1.279314</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>0.765079</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>0.551012</td>\n",
       "      <td>-1.797378</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>-0.689046</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>335</th>\n",
       "      <td>0.413854</td>\n",
       "      <td>0.918516</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>-1.790338</td>\n",
       "      <td>-0.416984</td>\n",
       "      <td>-0.150445</td>\n",
       "      <td>-0.473332</td>\n",
       "      <td>0.457491</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>336</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-0.411271</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-0.831840</td>\n",
       "      <td>-0.661562</td>\n",
       "      <td>-1.208196</td>\n",
       "      <td>0.075312</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>337</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-0.411271</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-1.408028</td>\n",
       "      <td>-0.945516</td>\n",
       "      <td>-0.963241</td>\n",
       "      <td>-0.689046</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>338</th>\n",
       "      <td>-1.421498</td>\n",
       "      <td>0.202477</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>1.642265</td>\n",
       "      <td>-0.924030</td>\n",
       "      <td>-0.661562</td>\n",
       "      <td>-0.473332</td>\n",
       "      <td>-0.306867</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>339</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>0.765079</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>0.689298</td>\n",
       "      <td>0.587835</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>0.457491</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>340 rows × 9 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "     district    adress  num_of_rooms  flat_type  total_square  living_square  \\\n",
       "0    1.025638 -1.587622      0.277145  -0.360087     -1.431076      -1.115889   \n",
       "1    1.025638 -0.667000      0.277145  -0.360087     -0.232604      -1.286261   \n",
       "2   -0.809714 -1.434185      1.037059  -1.790338      0.228347       0.587835   \n",
       "3   -1.421498 -1.229602     -1.242682   1.928315      0.652422       0.241411   \n",
       "4    1.025638  0.765079      1.037059  -0.360087      0.551012      -1.797378   \n",
       "..        ...       ...           ...        ...           ...            ...   \n",
       "335  0.413854  0.918516     -1.242682  -1.790338     -0.416984      -0.150445   \n",
       "336  1.025638 -0.411271      0.277145  -0.360087     -0.831840      -0.661562   \n",
       "337  1.025638 -0.411271      0.277145  -0.360087     -1.408028      -0.945516   \n",
       "338 -1.421498  0.202477      0.277145   1.642265     -0.924030      -0.661562   \n",
       "339 -0.809714  0.765079      1.037059  -0.360087      0.689298       0.587835   \n",
       "\n",
       "     kitchen_square  floor_num  total_floors  \n",
       "0         -0.963241   0.839670      0.813310  \n",
       "1          3.935852   0.075312      0.813310  \n",
       "2         -0.473332   0.457491      0.813310  \n",
       "3          0.506487  -0.689046     -1.279314  \n",
       "4          0.016578  -0.689046      0.813310  \n",
       "..              ...        ...           ...  \n",
       "335       -0.473332   0.457491     -0.382475  \n",
       "336       -1.208196   0.075312     -0.382475  \n",
       "337       -0.963241  -0.689046     -0.382475  \n",
       "338       -0.473332  -0.306867     -0.382475  \n",
       "339        0.016578   0.457491      0.813310  \n",
       "\n",
       "[340 rows x 9 columns]"
      ]
     },
     "execution_count": 40,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "features_train_piped.columns = categorical + numeric\n",
    "features_train_piped"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "id": "a412d7dc-b776-4cad-8da4-b418e9786228",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>num_of_rooms</th>\n",
       "      <th>flat_type</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>floor_num</th>\n",
       "      <th>total_floors</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-1.025019</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-0.601364</td>\n",
       "      <td>-0.661562</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>-0.306867</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>-0.360126</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>0.444994</td>\n",
       "      <td>0.814998</td>\n",
       "      <td>-0.105900</td>\n",
       "      <td>1.221849</td>\n",
       "      <td>1.112256</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>-0.411271</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>1.703389</td>\n",
       "      <td>1.610069</td>\n",
       "      <td>-0.473332</td>\n",
       "      <td>-0.689046</td>\n",
       "      <td>-1.279314</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>-1.421498</td>\n",
       "      <td>0.151331</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-0.074037</td>\n",
       "      <td>0.965868</td>\n",
       "      <td>1.382906</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>0.457491</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>0.413854</td>\n",
       "      <td>0.509351</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-0.440032</td>\n",
       "      <td>-0.264027</td>\n",
       "      <td>-0.718286</td>\n",
       "      <td>0.075312</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>80</th>\n",
       "      <td>-1.421498</td>\n",
       "      <td>0.100185</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>1.928315</td>\n",
       "      <td>0.320537</td>\n",
       "      <td>0.019927</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>-1.071225</td>\n",
       "      <td>-0.681422</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>81</th>\n",
       "      <td>1.025638</td>\n",
       "      <td>0.816225</td>\n",
       "      <td>-1.242682</td>\n",
       "      <td>-0.360087</td>\n",
       "      <td>-0.163461</td>\n",
       "      <td>0.019927</td>\n",
       "      <td>-0.105900</td>\n",
       "      <td>0.075312</td>\n",
       "      <td>0.813310</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>82</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>-1.792204</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-1.790338</td>\n",
       "      <td>0.689298</td>\n",
       "      <td>0.758207</td>\n",
       "      <td>-0.718286</td>\n",
       "      <td>0.457491</td>\n",
       "      <td>-0.382475</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>83</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>-0.360126</td>\n",
       "      <td>0.277145</td>\n",
       "      <td>-0.074037</td>\n",
       "      <td>-0.587536</td>\n",
       "      <td>-0.661562</td>\n",
       "      <td>0.016578</td>\n",
       "      <td>2.368386</td>\n",
       "      <td>1.112256</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>84</th>\n",
       "      <td>-0.809714</td>\n",
       "      <td>-1.843350</td>\n",
       "      <td>1.037059</td>\n",
       "      <td>-0.074037</td>\n",
       "      <td>1.334629</td>\n",
       "      <td>1.042161</td>\n",
       "      <td>0.261532</td>\n",
       "      <td>1.221849</td>\n",
       "      <td>2.905934</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>85 rows × 9 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "    district    adress  num_of_rooms  flat_type  total_square  living_square  \\\n",
       "0   1.025638 -1.025019      0.277145  -0.360087     -0.601364      -0.661562   \n",
       "1  -0.809714 -0.360126     -1.242682  -0.360087      0.444994       0.814998   \n",
       "2   1.025638 -0.411271      1.037059  -0.360087      1.703389       1.610069   \n",
       "3  -1.421498  0.151331      1.037059  -0.074037      0.965868       1.382906   \n",
       "4   0.413854  0.509351     -1.242682  -0.360087     -0.440032      -0.264027   \n",
       "..       ...       ...           ...        ...           ...            ...   \n",
       "80 -1.421498  0.100185     -1.242682   1.928315      0.320537       0.019927   \n",
       "81  1.025638  0.816225     -1.242682  -0.360087     -0.163461       0.019927   \n",
       "82 -0.809714 -1.792204      1.037059  -1.790338      0.689298       0.758207   \n",
       "83 -0.809714 -0.360126      0.277145  -0.074037     -0.587536      -0.661562   \n",
       "84 -0.809714 -1.843350      1.037059  -0.074037      1.334629       1.042161   \n",
       "\n",
       "    kitchen_square  floor_num  total_floors  \n",
       "0         0.016578  -0.306867      0.813310  \n",
       "1        -0.105900   1.221849      1.112256  \n",
       "2        -0.473332  -0.689046     -1.279314  \n",
       "3         0.016578   0.457491     -0.382475  \n",
       "4        -0.718286   0.075312     -0.382475  \n",
       "..             ...        ...           ...  \n",
       "80        0.016578  -1.071225     -0.681422  \n",
       "81       -0.105900   0.075312      0.813310  \n",
       "82       -0.718286   0.457491     -0.382475  \n",
       "83        0.016578   2.368386      1.112256  \n",
       "84        0.261532   1.221849      2.905934  \n",
       "\n",
       "[85 rows x 9 columns]"
      ]
     },
     "execution_count": 41,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "features_val_piped.columns = categorical + numeric\n",
    "features_val_piped"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "id": "b2145059-731a-4888-9247-76cc04f74cdc",
   "metadata": {},
   "outputs": [],
   "source": [
    "target_train = target_train.reset_index(drop=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "036ca421-e37a-45ea-84ac-ce0600dccd0d",
   "metadata": {},
   "outputs": [],
   "source": [
    "target_val = target_val.reset_index(drop=True)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9bd65cd1-475f-45a5-ad50-6a51601961f2",
   "metadata": {},
   "source": [
    "Модель линейной регрессии"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "id": "51cf6011-6cef-4c11-8427-968ca17baf6e",
   "metadata": {},
   "outputs": [],
   "source": [
    "class MyLinearRegression:\n",
    "    \n",
    "    def fit(self, train_features, train_target):\n",
    "        X = np.concatenate((np.ones((train_features.shape[0], 1)), train_features), axis=1)\n",
    "        y = train_target\n",
    "        w = np.linalg.inv(X.T @ X) @ X.T @ y\n",
    "        self.w = w[1:]\n",
    "        self.w0 = w[0]\n",
    "\n",
    "    def predict(self, test_features):\n",
    "        return test_features.dot(self.w) + self.w0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "id": "58b8df52-66c4-4c23-8b4b-18488f3afbe6",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "664.8244052685571\n"
     ]
    }
   ],
   "source": [
    "# наша модель\n",
    "model_1 = MyLinearRegression()\n",
    "model_1.fit(features_train_piped, target_train)\n",
    "predictions = model_1.predict(features_val_piped)\n",
    "\n",
    "# метрика MAE\n",
    "mae = mean_absolute_error(target_val, predictions)\n",
    "print(mae)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "id": "0f3b2bd4-9914-4fd1-adda-4db1d2f45cdd",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0     3050\n",
       "1     5950\n",
       "2     7400\n",
       "3     5500\n",
       "4     2650\n",
       "      ... \n",
       "80    3840\n",
       "81    3400\n",
       "82    4130\n",
       "83    3300\n",
       "84    6200\n",
       "Name: price, Length: 85, dtype: int64"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "target_val"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "id": "7e237e40-4d9a-4a9d-9cbc-c3e0530af3ab",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "3050 3267.7070993571897\n",
      "5950 4533.4168818013895\n",
      "7400 5549.792917958559\n",
      "5500 5159.7563727256\n",
      "2650 3027.4608064842996\n",
      "3000 3266.5331128096204\n",
      "4200 4476.107689289267\n",
      "2800 2722.296552297572\n",
      "4300 4759.778454810906\n",
      "2750 4623.611591793881\n"
     ]
    }
   ],
   "source": [
    "for i in range(10):\n",
    "    print(target_val.iloc[i], predictions.iloc[i])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "id": "ef8f546e-1993-4c69-a720-6e203cb1646d",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.tree import DecisionTreeRegressor"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "id": "ab6ce193-fc60-45a0-90b8-9fbe76420b82",
   "metadata": {},
   "outputs": [],
   "source": [
    "DTR = DecisionTreeRegressor(\n",
    "    max_depth=10,\n",
    "    random_state=RANDOM_STATE\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "id": "5551caec-1e60-4adb-b873-399f8ed50f15",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<style>#sk-container-id-1 {color: black;}#sk-container-id-1 pre{padding: 0;}#sk-container-id-1 div.sk-toggleable {background-color: white;}#sk-container-id-1 label.sk-toggleable__label {cursor: pointer;display: block;width: 100%;margin-bottom: 0;padding: 0.3em;box-sizing: border-box;text-align: center;}#sk-container-id-1 label.sk-toggleable__label-arrow:before {content: \"▸\";float: left;margin-right: 0.25em;color: #696969;}#sk-container-id-1 label.sk-toggleable__label-arrow:hover:before {color: black;}#sk-container-id-1 div.sk-estimator:hover label.sk-toggleable__label-arrow:before {color: black;}#sk-container-id-1 div.sk-toggleable__content {max-height: 0;max-width: 0;overflow: hidden;text-align: left;background-color: #f0f8ff;}#sk-container-id-1 div.sk-toggleable__content pre {margin: 0.2em;color: black;border-radius: 0.25em;background-color: #f0f8ff;}#sk-container-id-1 input.sk-toggleable__control:checked~div.sk-toggleable__content {max-height: 200px;max-width: 100%;overflow: auto;}#sk-container-id-1 input.sk-toggleable__control:checked~label.sk-toggleable__label-arrow:before {content: \"▾\";}#sk-container-id-1 div.sk-estimator input.sk-toggleable__control:checked~label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-1 div.sk-label input.sk-toggleable__control:checked~label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-1 input.sk-hidden--visually {border: 0;clip: rect(1px 1px 1px 1px);clip: rect(1px, 1px, 1px, 1px);height: 1px;margin: -1px;overflow: hidden;padding: 0;position: absolute;width: 1px;}#sk-container-id-1 div.sk-estimator {font-family: monospace;background-color: #f0f8ff;border: 1px dotted black;border-radius: 0.25em;box-sizing: border-box;margin-bottom: 0.5em;}#sk-container-id-1 div.sk-estimator:hover {background-color: #d4ebff;}#sk-container-id-1 div.sk-parallel-item::after {content: \"\";width: 100%;border-bottom: 1px solid gray;flex-grow: 1;}#sk-container-id-1 div.sk-label:hover label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-1 div.sk-serial::before {content: \"\";position: absolute;border-left: 1px solid gray;box-sizing: border-box;top: 0;bottom: 0;left: 50%;z-index: 0;}#sk-container-id-1 div.sk-serial {display: flex;flex-direction: column;align-items: center;background-color: white;padding-right: 0.2em;padding-left: 0.2em;position: relative;}#sk-container-id-1 div.sk-item {position: relative;z-index: 1;}#sk-container-id-1 div.sk-parallel {display: flex;align-items: stretch;justify-content: center;background-color: white;position: relative;}#sk-container-id-1 div.sk-item::before, #sk-container-id-1 div.sk-parallel-item::before {content: \"\";position: absolute;border-left: 1px solid gray;box-sizing: border-box;top: 0;bottom: 0;left: 50%;z-index: -1;}#sk-container-id-1 div.sk-parallel-item {display: flex;flex-direction: column;z-index: 1;position: relative;background-color: white;}#sk-container-id-1 div.sk-parallel-item:first-child::after {align-self: flex-end;width: 50%;}#sk-container-id-1 div.sk-parallel-item:last-child::after {align-self: flex-start;width: 50%;}#sk-container-id-1 div.sk-parallel-item:only-child::after {width: 0;}#sk-container-id-1 div.sk-dashed-wrapped {border: 1px dashed gray;margin: 0 0.4em 0.5em 0.4em;box-sizing: border-box;padding-bottom: 0.4em;background-color: white;}#sk-container-id-1 div.sk-label label {font-family: monospace;font-weight: bold;display: inline-block;line-height: 1.2em;}#sk-container-id-1 div.sk-label-container {text-align: center;}#sk-container-id-1 div.sk-container {/* jupyter's `normalize.less` sets `[hidden] { display: none; }` but bootstrap.min.css set `[hidden] { display: none !important; }` so we also need the `!important` here to be able to override the default hidden behavior on the sphinx rendered scikit-learn.org. See: https://github.com/scikit-learn/scikit-learn/issues/21755 */display: inline-block !important;position: relative;}#sk-container-id-1 div.sk-text-repr-fallback {display: none;}</style><div id=\"sk-container-id-1\" class=\"sk-top-container\"><div class=\"sk-text-repr-fallback\"><pre>DecisionTreeRegressor(max_depth=10, random_state=12345)</pre><b>In a Jupyter environment, please rerun this cell to show the HTML representation or trust the notebook. <br />On GitHub, the HTML representation is unable to render, please try loading this page with nbviewer.org.</b></div><div class=\"sk-container\" hidden><div class=\"sk-item\"><div class=\"sk-estimator sk-toggleable\"><input class=\"sk-toggleable__control sk-hidden--visually\" id=\"sk-estimator-id-1\" type=\"checkbox\" checked><label for=\"sk-estimator-id-1\" class=\"sk-toggleable__label sk-toggleable__label-arrow\">DecisionTreeRegressor</label><div class=\"sk-toggleable__content\"><pre>DecisionTreeRegressor(max_depth=10, random_state=12345)</pre></div></div></div></div></div>"
      ],
      "text/plain": [
       "DecisionTreeRegressor(max_depth=10, random_state=12345)"
      ]
     },
     "execution_count": 50,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "DTR.fit(features_train_piped, target_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "id": "d46adbf4-183d-403e-b119-2959ea87ecb5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "565.4717647058824\n"
     ]
    }
   ],
   "source": [
    "predictionsDTR = DTR.predict(features_val_piped)\n",
    "\n",
    "# метрика MAE\n",
    "maeDTR = mean_absolute_error(target_val, predictionsDTR)\n",
    "print(maeDTR)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "id": "ca094643-3886-40b6-9fe3-e93cc04ead87",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.ensemble import RandomForestRegressor"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "id": "035e390c-8ea1-4aad-b75b-df7eb3b2105f",
   "metadata": {},
   "outputs": [],
   "source": [
    "# список гиперпараметров и их значений\n",
    "search_space = {\n",
    "    'criterion' : ['squared_error', 'absolute_error', 'friedman_mse', 'poisson'],\n",
    "    'max_depth' : [5, 10, 15],\n",
    "    'n_estimators' : [50, 100, 200],\n",
    "    'max_features' : ['sqrt', 'log2', 1]\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "id": "88bc8b2b-9747-45c7-94c1-03e30d85da0b",
   "metadata": {},
   "outputs": [],
   "source": [
    "model_rfr = RandomForestRegressor(\n",
    "    random_state=RANDOM_STATE\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "id": "baf5d16c-4cdb-459a-a908-9767ba1863e0",
   "metadata": {},
   "outputs": [],
   "source": [
    "GS = GridSearchCV(\n",
    "    estimator=model_rfr,\n",
    "    param_grid=search_space,\n",
    "    scoring='neg_mean_absolute_error',\n",
    "    cv=3,\n",
    "    verbose=4\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "id": "2c0a4fa2-bc23-45b5-a984-4c4368244202",
   "metadata": {},
   "outputs": [],
   "source": [
    "# GS.fit(features_train_sc, target_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "id": "5f94f7a1-7434-40ac-b9ae-3a3c7286cda3",
   "metadata": {},
   "outputs": [],
   "source": [
    "# GS.best_score_"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "id": "95769eac-7bc2-46a6-b552-345acbb2677e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# GS.best_estimator_"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "id": "4bd1a873-6479-4c38-be7c-fee5815abdfa",
   "metadata": {},
   "outputs": [],
   "source": [
    "RFR = RandomForestRegressor(\n",
    "    # criterion='poisson',\n",
    "    max_depth=10, \n",
    "    # max_features='sqrt',\n",
    "    n_estimators=100,\n",
    "    random_state=RANDOM_STATE\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 60,
   "id": "1c501962-2cb3-40af-9290-de0189c3cd53",
   "metadata": {},
   "outputs": [],
   "source": [
    "# RFR = RandomForestRegressor(\n",
    "#     max_depth=10,\n",
    "#     random_state=RANDOM_STATE,\n",
    "#     n_estimators=100\n",
    "# )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 61,
   "id": "af108726-54ef-4490-84aa-fb2d1922ff0b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<style>#sk-container-id-2 {color: black;}#sk-container-id-2 pre{padding: 0;}#sk-container-id-2 div.sk-toggleable {background-color: white;}#sk-container-id-2 label.sk-toggleable__label {cursor: pointer;display: block;width: 100%;margin-bottom: 0;padding: 0.3em;box-sizing: border-box;text-align: center;}#sk-container-id-2 label.sk-toggleable__label-arrow:before {content: \"▸\";float: left;margin-right: 0.25em;color: #696969;}#sk-container-id-2 label.sk-toggleable__label-arrow:hover:before {color: black;}#sk-container-id-2 div.sk-estimator:hover label.sk-toggleable__label-arrow:before {color: black;}#sk-container-id-2 div.sk-toggleable__content {max-height: 0;max-width: 0;overflow: hidden;text-align: left;background-color: #f0f8ff;}#sk-container-id-2 div.sk-toggleable__content pre {margin: 0.2em;color: black;border-radius: 0.25em;background-color: #f0f8ff;}#sk-container-id-2 input.sk-toggleable__control:checked~div.sk-toggleable__content {max-height: 200px;max-width: 100%;overflow: auto;}#sk-container-id-2 input.sk-toggleable__control:checked~label.sk-toggleable__label-arrow:before {content: \"▾\";}#sk-container-id-2 div.sk-estimator input.sk-toggleable__control:checked~label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-2 div.sk-label input.sk-toggleable__control:checked~label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-2 input.sk-hidden--visually {border: 0;clip: rect(1px 1px 1px 1px);clip: rect(1px, 1px, 1px, 1px);height: 1px;margin: -1px;overflow: hidden;padding: 0;position: absolute;width: 1px;}#sk-container-id-2 div.sk-estimator {font-family: monospace;background-color: #f0f8ff;border: 1px dotted black;border-radius: 0.25em;box-sizing: border-box;margin-bottom: 0.5em;}#sk-container-id-2 div.sk-estimator:hover {background-color: #d4ebff;}#sk-container-id-2 div.sk-parallel-item::after {content: \"\";width: 100%;border-bottom: 1px solid gray;flex-grow: 1;}#sk-container-id-2 div.sk-label:hover label.sk-toggleable__label {background-color: #d4ebff;}#sk-container-id-2 div.sk-serial::before {content: \"\";position: absolute;border-left: 1px solid gray;box-sizing: border-box;top: 0;bottom: 0;left: 50%;z-index: 0;}#sk-container-id-2 div.sk-serial {display: flex;flex-direction: column;align-items: center;background-color: white;padding-right: 0.2em;padding-left: 0.2em;position: relative;}#sk-container-id-2 div.sk-item {position: relative;z-index: 1;}#sk-container-id-2 div.sk-parallel {display: flex;align-items: stretch;justify-content: center;background-color: white;position: relative;}#sk-container-id-2 div.sk-item::before, #sk-container-id-2 div.sk-parallel-item::before {content: \"\";position: absolute;border-left: 1px solid gray;box-sizing: border-box;top: 0;bottom: 0;left: 50%;z-index: -1;}#sk-container-id-2 div.sk-parallel-item {display: flex;flex-direction: column;z-index: 1;position: relative;background-color: white;}#sk-container-id-2 div.sk-parallel-item:first-child::after {align-self: flex-end;width: 50%;}#sk-container-id-2 div.sk-parallel-item:last-child::after {align-self: flex-start;width: 50%;}#sk-container-id-2 div.sk-parallel-item:only-child::after {width: 0;}#sk-container-id-2 div.sk-dashed-wrapped {border: 1px dashed gray;margin: 0 0.4em 0.5em 0.4em;box-sizing: border-box;padding-bottom: 0.4em;background-color: white;}#sk-container-id-2 div.sk-label label {font-family: monospace;font-weight: bold;display: inline-block;line-height: 1.2em;}#sk-container-id-2 div.sk-label-container {text-align: center;}#sk-container-id-2 div.sk-container {/* jupyter's `normalize.less` sets `[hidden] { display: none; }` but bootstrap.min.css set `[hidden] { display: none !important; }` so we also need the `!important` here to be able to override the default hidden behavior on the sphinx rendered scikit-learn.org. See: https://github.com/scikit-learn/scikit-learn/issues/21755 */display: inline-block !important;position: relative;}#sk-container-id-2 div.sk-text-repr-fallback {display: none;}</style><div id=\"sk-container-id-2\" class=\"sk-top-container\"><div class=\"sk-text-repr-fallback\"><pre>RandomForestRegressor(max_depth=10, random_state=12345)</pre><b>In a Jupyter environment, please rerun this cell to show the HTML representation or trust the notebook. <br />On GitHub, the HTML representation is unable to render, please try loading this page with nbviewer.org.</b></div><div class=\"sk-container\" hidden><div class=\"sk-item\"><div class=\"sk-estimator sk-toggleable\"><input class=\"sk-toggleable__control sk-hidden--visually\" id=\"sk-estimator-id-2\" type=\"checkbox\" checked><label for=\"sk-estimator-id-2\" class=\"sk-toggleable__label sk-toggleable__label-arrow\">RandomForestRegressor</label><div class=\"sk-toggleable__content\"><pre>RandomForestRegressor(max_depth=10, random_state=12345)</pre></div></div></div></div></div>"
      ],
      "text/plain": [
       "RandomForestRegressor(max_depth=10, random_state=12345)"
      ]
     },
     "execution_count": 61,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "RFR.fit(features_train_piped, target_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "id": "dad8c915-8ab3-4588-80b0-4a90671853c0",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "489.68761813934765\n"
     ]
    }
   ],
   "source": [
    "predictionsRFR = RFR.predict(features_val_piped)\n",
    "\n",
    "# метрика MAE\n",
    "maeRFR = mean_absolute_error(target_val, predictionsRFR)\n",
    "print(maeRFR)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "id": "304ede7a-aa3c-48ff-8921-53dd070bccc8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "14.551127744777027"
      ]
     },
     "execution_count": 63,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mean_absolute_percentage_error(target_val, predictionsRFR)*100"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "id": "888691a8-bb57-4e28-8719-699508dfdb09",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "722.3377981485312"
      ]
     },
     "execution_count": 64,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mean_squared_error(target_val, predictionsRFR) ** 0.5"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "id": "85eba103-615f-48bc-841e-9dffdd89f6a8",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "3050 3037.532532992569\n",
      "5950 5041.795213952713\n",
      "7400 6043.4\n",
      "5500 5616.993880447037\n",
      "2650 3138.790570373176\n",
      "3000 2618.297596453667\n",
      "4200 4224.286746031746\n",
      "2800 2510.6049428326864\n",
      "4300 4685.249626557652\n",
      "2750 4666.16429197995\n"
     ]
    }
   ],
   "source": [
    "for i in range(10):\n",
    "    print(target_val.iloc[i], predictionsRFR[i])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "id": "9d7dc68e-7cdd-487d-be19-305f609e6261",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "85"
      ]
     },
     "execution_count": 66,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "len(target_val)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "id": "a10e2b4e-96c7-43ff-bd51-836c3b54acf9",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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uG4tWrRQdna2rda/GzBggOn0ffv26cSJE/n2uZ6tW7fq4Ycf1uXLl/Xf//5XPXr0cHiM9PR0vffee5Kk9u3b59vn+PHjevvtt/X000+rQ4cOuueee3TPPfdo2LBhkq6e91CQf/zjH6pWrVqe6VFRUWrRooWkq8cZF5dXXnlFOTk5mjRpksqVK3fd/sX5fBUHwzD04YcfKj09XSEhIapTp85NWa7VatX777+vXr16KSYmRvfee6/uuecedezYUW5ubrpw4UKBhwsVdCjOK6+8Im9vb6Wnp+u7777Lt0/usfY+Pj43VP+ECRNs59o0b978hsYqyGeffaacnBw99NBD+b4HJNkOB9y0aZOys7MdXkbuOVW+vr4Oz5uWlqYZM2aoe/fueuCBB2zPYe75BIcOHdJff/3l8LilQa1atWx/E1599VU9/vjjOnHihNq0aVOoewsB+eGcBuAG9e7d+7r/Ced33Ogvv/xi+yNav379fOcLDAxU5cqVlZycrJ9//ln33Xdfnj5lypTRs88+q2nTpum7775TVFSUkpOTtXLlSnXu3NnuOOBr7d27V5Lk7u6uhx56qMDaDx8+LEkFfpAsqPbatWvLw8NDV65c0cGDBxUeHl7gMvKzY8cOjRs3ThcvXpS7u7saNmxYqPkmTJigDz74QNLVcxp+/vlnlSlTRv369dP48ePz9J8xY4Zef/1105Ns//jjjwLbClp/SapXr5527txZ4InqN2rRokXaunWroqKi1K1bt0J9GCjq85WSkqJ77rlH0tXXs7e3typXrqz7779fzzzzTJE+1OVn9+7dtuXkntOQlpamDh066J133nHacsxs2bJFTz75pNLS0kz7FfS6+Pu5Kbn8/PxUrVo1HT58WD///LM6duxo124YhtLT0yVdfV8X1f/93//pP//5jwICAjRhwgQdOHCgyGOZyf0/JDEx0fac/Z3x/59o+9dff+mPP/7Icy7J9eQ+B4UJxNf67LPP1KtXL124cKHAPoZh6OzZs6pcuXKeto8++kjr1q3Ld759+/aZLvva1/DfJScnm84ryW5eb29vBQcHq02bNurevbsCAgKuO3+u7t27a926dVqwYIE2b96sgIAALV68WB4efPRD0fDKAVwk9wosbm5upn9IQ0NDlZycnO8VW3K9/PLLmj59umbNmqWoqCj997//VXZ2tuLj4wuc59y5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MLDINTtay//93//p8uXL6tSpkwIDA3X+/HmtXLlSvXr10m+//abhw4cXuZaiIDQAAACgVDl8+LD2798vf39/SdLo0aPVqlUrTZ06Vc8884yaN28uSfqf//kfffnll7r//vu1du1aeXl5SZKGDRumZs2aafDgwXr00Ud155132o3/2GOPFbgXoagcreXFF1/Uiy++aDfG22+/rdDQUH3yySc3PTRweBIAAABKlTfffNMWGCTJ399fw4cPl2EYdudB5P48adIk24d0SapataoGDhyoK1euaNGiRTel5hut5Y8//tC8efN08eJFVa9evbjLzYM9DQAAAChV7r333gKn7d692zZt9+7dKlOmjFq2bJmnf7t27SRJe/bsKXIde/bsyfdE7vzGLGot0dHRWr9+ve331q1ba8aMGUWuuagIDQAAAChVgoODC5yWnp5um2a1WhUeHp7vGKGhobY+RbV3717t3bu3UH2LWkvPnj0VFRWlU6dOafXq1apdu7bKlStX5JqLitAAAACAUiU1NVVVq1bNM02S3WFLfn5+SktLy3eMlJQUW5+iiouLy/dqRs8++2yey8UWtZaePXvafk5LS1Pjxo118OBBbd++vch1FwXnNAAAAKBU+fbbbwuc1qRJE9u0Jk2a6NKlS9qxY0ee/ps2bZKkfK+SVBycUUtQUJBatWqlHTt26I8//iiGKgtGaAAAAECpMnbsWLvDkNLT0zVu3DhZLBbFxcXZpuf+PGzYMGVlZdmmnzhxQlOmTJGHh4e6det2U2p2tJYzZ87kGePYsWP69ttv5e3trbJlyxZ/0dfg8CQAAACUKnfddZfq169vd5+G3377TYMGDbJdblWSevTooeXLl+vLL79Uw4YN1blzZ9u9Ec6ePavJkyfnudxqcXG0lo4dO6ps2bKqX7++AgICdPz4cX355Ze6dOmShg0bJh8fn5tSdy5CAwAAAEqVpUuXauTIkfr444+VmpqqiIgIzZgxQ/369bPrZ7FY9Nlnn2n69OlasGCBZs6cKS8vLzVt2lSDBg3SI488ctNqdrSWbt26aenSpVqyZImsVqv8/PzUsmVL9e7dWz169LhpddvqN/K73zbsWK1W+fv7Kz09/YZOlgGAopqze5Vpe98F5u0OLSsutuDlNCm4DUDhXL58WUePHlVERMRN/7a4tGvbtq02b94sPr5eX2FfZ4X9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AQBAMXI4NKSlpalr167atGmTAgICJEnnz59Xu3bt9Mknn+iOO+5wdo0AAAAAXMjhS66+8sor+vPPP3XgwAGdPXtWZ8+e1f79+2W1WtW/f//iqBEAAACACzm8p2H16tVat26d6tSpY5tWt25dzZo1Sx07dnRqcQAAAABcz+HQkJOTI09PzzzTPT09lZOT45SiAORleoWIm7QciatRAABwO3L48KT27dvr1Vdf1alTp2zTTp48qYEDB6pDhw5OLQ4AAACA6zkcGt59911ZrVZVr15dNWrUUI0aNRQRESGr1aqZM2cWR40AAAAAXMjhw5PCw8O1a9curVu3Tj///LMkqU6dOoqOjnZ6cQAAAABcz+HQsHDhQj399NN64IEH9MADDxRHTQAAAABKEIcPT+rVq5fS09OLoxYAAAAAJZDDocEwDKctfM6cOWrYsKH8/Pzk5+enyMhIffPNN7b2y5cvKz4+XhUrVlS5cuXUpUsXpaam2o2RnJys2NhYlSlTRkFBQXr99dd15coVuz6bNm1S06ZN5e3trZo1a2r+/PlOWwcAAADgVufw4UmStHTpUvn5+eXb1rNnz0KPU6VKFb311luqVauWDMPQggUL9Oijj2r37t2qV6+eBg4cqFWrVunTTz+Vv7+/+vXrp8cff1zfffedJCk7O1uxsbEKCQnR999/r9OnT6tnz57y9PTUhAkTJElHjx5VbGysXnrpJS1atEjr16/Xc889p9DQUMXExBRl9QEAKFH6LjC/VLIj5sRxWWUAeRUpNEyaNEnu7u55plssFodCw8MPP2z3+/jx4zVnzhxt27ZNVapU0YcffqjFixerffv2kqR58+apTp062rZtm1q3bq21a9fqp59+0rp16xQcHKzGjRtr7NixGjJkiEaNGiUvLy/NnTtXERERmjx5sqSrJ21v3bpVU6dOJTQAAAAAheDw4UmS9MMPP+jo0aN5Hr/++muRC8nOztYnn3yiixcvKjIyUklJScrKyrK7KtPdd9+tqlWrKjExUZKUmJioBg0aKDg42NYnJiZGVqtVBw4csPX5+5WdYmJibGPkJyMjQ1ar1e4BAAAA3K6KtKfBmfbt26fIyEhdvnxZ5cqV0+eff666detqz5498vLyUkBAgF3/4OBgpaSkSJJSUlLsAkNue26bWR+r1aq//vpLvr6+eWqaOHGiRo8e7axVBFBKccgHAABXObynoVq1avkemlRUtWvX1p49e7R9+3b17dtXcXFx+umnn5w2flEMGzZM6enptseJEydcWg8AAADgSg7vaTh69KhTC/Dy8lLNmjUlSc2aNdPOnTs1ffp0Pf3008rMzNT58+ft9jakpqYqJCREkhQSEqIdO3bYjZd7daVr+/z9ikupqany8/PLdy+DJHl7e8vb29sp6wcAAACUdoXe07BhwwbVrVs33+P709PTVa9ePX377bc3XFBOTo4yMjLUrFkzeXp6av369ba2Q4cOKTk5WZGRkZKkyMhI7du3T2lpabY+CQkJ8vPzU926dW19rh0jt0/uGAAAAADMFXpPw7Rp0/T888/ne6lVf39/vfjii5oyZYruvffeQi982LBheuihh1S1alX9+eefWrx4sTZt2qQ1a9bI399fffr00aBBgxQYGCg/Pz+98sorioyMVOvWrSVJHTt2VN26ddWjRw9NmjRJKSkpGj58uOLj4217Cl566SW9++67Gjx4sHr37q0NGzZo6dKlWrXKeccqAwAAALeyQu9p2Lt3rx588MEC2zt27KikpCSHFp6WlqaePXuqdu3a6tChg3bu3Kk1a9bogQcekCRNnTpVnTt3VpcuXXTfffcpJCREy5cvt83v7u6ulStXyt3dXZGRkerevbt69uypMWPG2PpERERo1apVSkhIUKNGjTR58mR98MEHXG4VAAAAKKRC72lITU2Vp6dnwQN5eOj33393aOEffvihabuPj49mzZqlWbNmFdinWrVq+vrrr03Hadu2rXbv3u1Qbbg9zNldMvY49W3ClXUAAEDJVeg9DZUrV9b+/fsLbP/xxx8VGhrqlKIAAAAAlByFDg2dOnXSm2++qcuXL+dp++uvvzRy5Eh17tzZqcUBAAAAcL1CH540fPhwLV++XHfddZf69eun2rVrS5J+/vlnzZo1S9nZ2XrjjTeKrVAAAAAArlHo0BAcHKzvv/9effv21bBhw2QYhiTJYrEoJiZGs2bNynPnZaA0c+bdgCXuCAwAAEovh27ulnvS8blz5/TLL7/IMAzVqlVLFSpUKK76AAAAALiYw3eElqQKFSqoRYsWzq4FAAAAQAlU6BOhAQAAANyeCA0AAAAATBEaAAAAAJgiNAAAAAAwRWgAAAAAYIrQAAAAAMAUoQEAAACAKUIDAAAAAFOEBgAAAACminRHaMDMnN2rCmzrezOX1STWyUsDAAC4PbGnAQAAAIApQgMAAAAAU4QGAAAAAKYIDQAAAABMERoAAAAAmOLqSQAA5GfAy84db9ps544HADcRexoAAAAAmCI0AAAAADBFaAAAAABgitAAAAAAwBShAQAAAIApQgMAAAAAU4QGAAAAAKYIDQAAAABMERoAAAAAmCI0AAAAADBFaAAAAABgitAAAAAAwBShAQAAAIApQgMAAAAAU4QGAAAAAKYIDQAAAABMERoAAAAAmCI0AAAAADBFaAAAAABgitAAAAAAwBShAQAAAIApD1cXAACAq8zZvarAtr43c1lNYp28NABwLpfuaZg4caJatGih8uXLKygoSI899pgOHTpk1+fy5cuKj49XxYoVVa5cOXXp0kWpqal2fZKTkxUbG6syZcooKChIr7/+uq5cuWLXZ9OmTWratKm8vb1Vs2ZNzZ8/v7hXDwAAALgluDQ0bN68WfHx8dq2bZsSEhKUlZWljh076uLFi7Y+AwcO1FdffaVPP/1Umzdv1qlTp/T444/b2rOzsxUbG6vMzEx9//33WrBggebPn68RI0bY+hw9elSxsbFq166d9uzZowEDBui5557TmjVrbur6AgAAAKWRSw9PWr16td3v8+fPV1BQkJKSknTfffcpPT1dH374oRYvXqz27dtLkubNm6c6depo27Ztat26tdauXauffvpJ69atU3BwsBo3bqyxY8dqyJAhGjVqlLy8vDR37lxFRERo8uTJkqQ6depo69atmjp1qmJiYm76egMAAAClSYk6ETo9PV2SFBgYKElKSkpSVlaWoqOjbX3uvvtuVa1aVYmJiZKkxMRENWjQQMHBwbY+MTExslqtOnDggK3PtWPk9skd4+8yMjJktVrtHgAAAMDtqsSEhpycHA0YMEBRUVGqX7++JCklJUVeXl4KCAiw6xscHKyUlBRbn2sDQ257bptZH6vVqr/++itPLRMnTpS/v7/tER4e7pR1BAAAAEqjEhMa4uPjtX//fn3yySeuLkXDhg1Tenq67XHixAlXlwQAAAC4TIm45Gq/fv20cuVKbdmyRVWqVLFNDwkJUWZmps6fP2+3tyE1NVUhISG2Pjt27LAbL/fqStf2+fsVl1JTU+Xn5ydfX9889Xh7e8vb29sp6wYAAACUdi7d02AYhvr166fPP/9cGzZsUEREhF17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xaJp06bdtPpuBkLDbWDJkiUaNGiQRo4cqV27dqlRo0aKiYlRWlqaq0srtTZv3qz4+Hht27ZNCQkJysrKUseOHXXx4kVXl3ZL2Llzp/773/+qYcOGri6l1Dt37pyioqLk6empb775Rj/99JMmT56sChUquLq0Uu3tt9/WnDlz9O677+rgwYN6++23NWnSJM2cOdPVpZUaFy9eVKNGjTRr1qx82ydNmqQZM2Zo7ty52r59u8qWLauYmBhdvnz5Jldaupht10uXLmnXrl168803tWvXLi1fvlyHDh3SI4884oJKS5frvV5zff7559q2bZvCwsJuUmU3kYFbXsuWLY34+Hjb79nZ2UZYWJgxceJEF1Z1a0lLSzMkGZs3b3Z1KaXen3/+adSqVctISEgw7r//fuPVV191dUml2pAhQ4x77rnH1WXccmJjY43evXvbTXv88ceNbt26uaii0k2S8fnnn9t+z8nJMUJCQox33nnHNu38+fOGt7e38fHHH7ugwtLp79s1Pzt27DAkGcePH785Rd0CCtquv/32m1G5cmVj//79RrVq1YypU6fe9NqKE3sabnGZmZlKSkpSdHS0bZqbm5uio6OVmJjowspuLenp6ZKkwMBAF1dS+sXHxys2NtbuNYuiW7FihZo3b64nn3xSQUFBatKkid5//31Xl1XqtWnTRuvXr9fhw4clSXv37tXWrVv10EMPubiyW8PRo0eVkpJi9/+Av7+/WrVqxd8uJ0tPT5fFYlFAQICrSynVcnJy1KNHD73++uuqV6+eq8spFrfNHaFvV2fOnFF2dnaeO18HBwfr559/dlFVt5acnBwNGDBAUVFRql+/vqvLKdU++eQT7dq1Szt37nR1KbeMX3/9VXPmzNGgQYP073//Wzt37lT//v3l5eWluLg4V5dXag0dOlRWq1V333233N3dlZ2drfHjx6tbt26uLu2WkJKSIkn5/u3KbcONu3z5soYMGaJnnnlGfn5+ri6nVHv77bfl4eGh/v37u7qUYkNoAG5QfHy89u/fr61bt7q6lFLtxIkTevXVV5WQkCAfHx9Xl3PLyMnJUfPmzTVhwgRJUpMmTbR//37NnTuX0HADli5dqkWLFmnx4sWqV6+e9uzZowEDBigsLIztilIhKytLTz31lAzD0Jw5c1xdTqmWlJSk6dOna9euXbJYLK4up9hweNItrlKlSnJ3d1dqaqrd9NTUVIWEhLioqltHv379tHLlSm3cuFFVqlRxdTmlWlJSktLS0tS0aVN5eHjIw8NDmzdv1owZM+Th4aHs7GxXl1gqhYaGqm7dunbT6tSpo+TkZBdVdGt4/fXXNXToUHXt2lUNGjRQjx49NHDgQE2cONHVpd0Scv8+8bereOQGhuPHjyshIYG9DDfo22+/VVpamqpWrWr7+3X8+HG99tprql69uqvLcxpCwy3Oy8tLzZo10/r1623TcnJytH79ekVGRrqwstLNMAz169dPn3/+uTZs2KCIiAhXl1TqdejQQfv27dOePXtsj+bNm6tbt27as2eP3N3dXV1iqRQVFZXncsCHDx9WtWrVXFTRreHSpUtyc7P/E+ru7q6cnBwXVXRriYiIUEhIiN3fLqvVqu3bt/O36wblBoYjR45o3bp1qlixoqtLKvV69OihH3/80e7vV1hYmF5//XWtWbPG1eU5DYcn3QYGDRqkuLg4NW/eXC1bttS0adN08eJF9erVy9WllVrx8fFavHixvvzyS5UvX952jK2/v798fX1dXF3pVL58+TznhJQtW1YVK1bkXJEbMHDgQLVp00YTJkzQU089pR07dui9997Te++95+rSSrWHH35Y48ePV9WqVVWvXj3t3r1bU6ZMUe/evV1dWqlx4cIF/fLLL7bfjx49qj179igwMFBVq1bVgAEDNG7cONWqVUsRERF68803FRYWpscee8x1RZcCZts1NDRUTzzxhHbt2qWVK1cqOzvb9vcrMDBQXl5eriq7xLve6/Xv4cvT01MhISGqXbv2zS61+Lj68k24OWbOnGlUrVrV8PLyMlq2bGls27bN1SWVapLyfcybN8/Vpd1SuOSqc3z11VdG/fr1DW9vb+Puu+823nvvPVeXVOpZrVbj1VdfNapWrWr4+PgYd955p/HGG28YGRkZri6t1Ni4cWO+/4/GxcUZhnH1sqtvvvmmERwcbHh7exsdOnQwDh065NqiSwGz7Xr06NEC/35t3LjR1aWXaNd7vf7drXjJVYthcPtKAAAAAAXjnAYAAAAApggNAAAAAEwRGgAAAACYIjQAAAAAMEVoAAAAAGCK0AAAAADAFKEBAAAAgClCAwAAAABThAYAAAAApggNAAAAAEwRGgAAAACYIjQAAAAAMPX/AWnMmEengYVwAAAAAElFTkSuQmCC",
      "text/plain": [
       "<Figure size 900x600 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "# построим диаграмму значений\n",
    "fig, ax = plt.subplots(figsize=(9, 6))\n",
    "plt.rc('font', size=14)\n",
    "x = [i for i in range(15)]\n",
    "\n",
    "ax.bar(x, target_val[70:], color='#96ceb4', label='Факт')\n",
    "ax.bar(x, predictionsRFR[70:], width = .45, color='#ff6f69', label='Прогноз')\n",
    "# ax.plot(x, [y_test[:13].median() for i in range(13)], color='#36454f', label='Медиана')\n",
    "\n",
    "\n",
    "\n",
    "ax.set_ylabel('Стоимость квартиры')\n",
    "ax.set_title('Номер квартиры в таблице данных')\n",
    "ax.legend()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "id": "058e05e9-73ec-4599-b520-c1e5a9e2ce87",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[(0.787584286225009, 'total_square'),\n",
       " (0.0490937542742821, 'kitchen_square'),\n",
       " (0.036396633086722904, 'total_floors'),\n",
       " (0.032477253890963724, 'living_square'),\n",
       " (0.028734086724948028, 'adress'),\n",
       " (0.02301100845566197, 'num_of_rooms'),\n",
       " (0.02004651697353978, 'floor_num'),\n",
       " (0.012174181488267644, 'district'),\n",
       " (0.01048227888060481, 'flat_type')]"
      ]
     },
     "execution_count": 68,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "sorted(zip(RFR.feature_importances_, features_val_piped.columns), reverse=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "id": "a5c575dd-83dc-48a6-862f-35939e6df700",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>id</th>\n",
       "      <th>type</th>\n",
       "      <th>district</th>\n",
       "      <th>adress</th>\n",
       "      <th>floor</th>\n",
       "      <th>total_square</th>\n",
       "      <th>living_square</th>\n",
       "      <th>kitchen_square</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1</td>\n",
       "      <td>Трехкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 145/2</td>\n",
       "      <td>1/5</td>\n",
       "      <td>64.0</td>\n",
       "      <td>43.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>3750</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2</td>\n",
       "      <td>Трехкомнатная</td>\n",
       "      <td>Ленинский</td>\n",
       "      <td>Октябрьская 12</td>\n",
       "      <td>2/5</td>\n",
       "      <td>87.2</td>\n",
       "      <td>60.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>8300</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>3</td>\n",
       "      <td>Однокомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 135</td>\n",
       "      <td>6/14</td>\n",
       "      <td>36.1</td>\n",
       "      <td>20.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3330</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>4</td>\n",
       "      <td>Трехкомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 129</td>\n",
       "      <td>5/16</td>\n",
       "      <td>105.0</td>\n",
       "      <td>75.0</td>\n",
       "      <td>14.0</td>\n",
       "      <td>7700</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>5</td>\n",
       "      <td>Двухкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Сиреневый проезд 12</td>\n",
       "      <td>7/9</td>\n",
       "      <td>50.6</td>\n",
       "      <td>43.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3800</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>6</td>\n",
       "      <td>Двухкомнатная улучшенная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 141</td>\n",
       "      <td>4/9</td>\n",
       "      <td>49.7</td>\n",
       "      <td>35.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>4000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>7</td>\n",
       "      <td>Двухкомнатная</td>\n",
       "      <td>Правобережный</td>\n",
       "      <td>Советской Армии 9</td>\n",
       "      <td>1/5</td>\n",
       "      <td>43.8</td>\n",
       "      <td>28.6</td>\n",
       "      <td>6.0</td>\n",
       "      <td>3200</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>8</td>\n",
       "      <td>Однокомнатная брежневка</td>\n",
       "      <td>Правобережный</td>\n",
       "      <td>Карла Маркса 99</td>\n",
       "      <td>4/9</td>\n",
       "      <td>31.0</td>\n",
       "      <td>17.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>2670</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>9</td>\n",
       "      <td>Однокомнатная хрущевка</td>\n",
       "      <td>Ленинский</td>\n",
       "      <td>Ленинградская 37а</td>\n",
       "      <td>2/5</td>\n",
       "      <td>31.0</td>\n",
       "      <td>19.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>2650</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9</th>\n",
       "      <td>10</td>\n",
       "      <td>Однокомнатная хабаровский вариант</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Сиреневый проезд 14/2</td>\n",
       "      <td>6/6</td>\n",
       "      <td>37.0</td>\n",
       "      <td>19.0</td>\n",
       "      <td>8.0</td>\n",
       "      <td>2990</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>10</th>\n",
       "      <td>11</td>\n",
       "      <td>Однокомнатная нестандартная</td>\n",
       "      <td>Орджоникидзевский</td>\n",
       "      <td>Ленина пр-т 133/1</td>\n",
       "      <td>10/10</td>\n",
       "      <td>40.3</td>\n",
       "      <td>20.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>3300</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "    id                               type           district  \\\n",
       "0    1           Трехкомнатная улучшенная  Орджоникидзевский   \n",
       "1    2                     Трехкомнатная           Ленинский   \n",
       "2    3        Однокомнатная нестандартная  Орджоникидзевский   \n",
       "3    4        Трехкомнатная нестандартная  Орджоникидзевский   \n",
       "4    5           Двухкомнатная улучшенная  Орджоникидзевский   \n",
       "5    6           Двухкомнатная улучшенная  Орджоникидзевский   \n",
       "6    7                     Двухкомнатная       Правобережный   \n",
       "7    8            Однокомнатная брежневка      Правобережный   \n",
       "8    9             Однокомнатная хрущевка          Ленинский   \n",
       "9   10  Однокомнатная хабаровский вариант  Орджоникидзевский   \n",
       "10  11        Однокомнатная нестандартная  Орджоникидзевский   \n",
       "\n",
       "                   adress  floor  total_square  living_square  kitchen_square  \\\n",
       "0       Ленина пр-т 145/2    1/5          64.0           43.0             8.0   \n",
       "1          Октябрьская 12    2/5          87.2           60.0             9.0   \n",
       "2         Ленина пр-т 135   6/14          36.1           20.0             9.0   \n",
       "3         Ленина пр-т 129   5/16         105.0           75.0            14.0   \n",
       "4     Сиреневый проезд 12    7/9          50.6           43.0             9.0   \n",
       "5         Ленина пр-т 141    4/9          49.7           35.0             9.0   \n",
       "6       Советской Армии 9    1/5          43.8           28.6             6.0   \n",
       "7         Карла Маркса 99    4/9          31.0           17.0             6.0   \n",
       "8       Ленинградская 37а    2/5          31.0           19.0             6.0   \n",
       "9   Сиреневый проезд 14/2    6/6          37.0           19.0             8.0   \n",
       "10      Ленина пр-т 133/1  10/10          40.3           20.0             9.0   \n",
       "\n",
       "    price  \n",
       "0    3750  \n",
       "1    8300  \n",
       "2    3330  \n",
       "3    7700  \n",
       "4    3800  \n",
       "5    4000  \n",
       "6    3200  \n",
       "7    2670  \n",
       "8    2650  \n",
       "9    2990  \n",
       "10   3300  "
      ]
     },
     "execution_count": 69,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.head(11)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "id": "a83850e4-6265-4419-8fd2-2552a030dd2e",
   "metadata": {},
   "outputs": [],
   "source": [
    "data.drop(['id', 'price'], axis=1).iloc[10].to_json('test_features.json')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "id": "f0f6e500-63f5-4937-97e8-f42b870901d2",
   "metadata": {},
   "outputs": [],
   "source": [
    "# test = pd.read_json('test.json', typ='series')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "id": "7e16dd08-40fb-45d3-a63e-847d419a3083",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "type              Однокомнатная нестандартная\n",
       "district                    Орджоникидзевский\n",
       "adress                      Ленина пр-т 133/1\n",
       "floor                                   10/10\n",
       "total_square                             40.3\n",
       "living_square                            20.0\n",
       "kitchen_square                            9.0\n",
       "dtype: object"
      ]
     },
     "execution_count": 72,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "test_1 =  pd.read_json('test_features.json', typ='series')\n",
    "test_1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "id": "0121e026-b8db-4e69-aab3-505e1744a7c9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "<class 'pandas.core.series.Series'>\n",
      "Index: 7 entries, type to kitchen_square\n",
      "Series name: None\n",
      "Non-Null Count  Dtype \n",
      "--------------  ----- \n",
      "7 non-null      object\n",
      "dtypes: object(1)\n",
      "memory usage: 412.0+ bytes\n"
     ]
    }
   ],
   "source": [
    "test_1.info()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "id": "599b60a4-e4d4-48b0-a0f5-abefa3196e0a",
   "metadata": {},
   "outputs": [],
   "source": [
    "test_1 = test_1.to_frame().T"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "id": "3a933bc3-8cd7-4fe3-b1af-4c5d84a8fad4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[-0.80971406, -0.36012566,  0.27714497, -0.07403652, -0.58753595,\n",
       "        -0.66156244,  0.01657767,  2.36838619,  1.11225609]])"
      ]
     },
     "execution_count": 75,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "my_pipeline.transform(test_1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "id": "29be9601-e880-4f95-8084-699522a9e393",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\base.py:464: UserWarning: X does not have valid feature names, but RandomForestRegressor was fitted with feature names\n",
      "  warnings.warn(\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "3372.1845027195027"
      ]
     },
     "execution_count": 76,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "RFR.predict(my_pipeline.transform(test_1))[0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 77,
   "id": "8249e336-e87a-4cb4-8739-96451424139c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "3300"
      ]
     },
     "execution_count": 77,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['price'].iloc[10]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "id": "9cd656e6-4001-4af8-a18a-bb411b525e1a",
   "metadata": {},
   "outputs": [],
   "source": [
    "with open ('pipeline-1.0.pkl', 'wb') as f:\n",
    "    pickle.dump(my_pipeline, f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "id": "9dab9881-8612-4d3c-9d99-9f883714a9f5",
   "metadata": {},
   "outputs": [],
   "source": [
    "with open ('model-1.0.pkl', 'wb') as f:\n",
    "    pickle.dump(RFR, f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d91cd11f-dfc3-4706-a79d-6fc3a0786318",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 170,
   "id": "e787cc90-4332-44a0-b54d-93e246ab9701",
   "metadata": {},
   "outputs": [],
   "source": [
    "final_pipeline = Pipeline([\n",
    "    ('data_cleaner', DataCleaner()),\n",
    "    ('features_transformer', FeaturesTransformer()),\n",
    "    ('col_transformer', ColumnTransformer(\n",
    "   transformers=[\n",
    "       ('oe', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value = -1), categorical)\n",
    "       ],\n",
    "    remainder=\"passthrough\",\n",
    "    verbose_feature_names_out=False\n",
    ")),\n",
    "    ('scaler', StandardScaler()),\n",
    "    ('RndomForestRegressor', RFR)\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 171,
   "id": "b76532cc-3e77-475c-bccc-978457867e06",
   "metadata": {},
   "outputs": [
    {
     "ename": "TypeError",
     "evalue": "DataCleaner.fit() takes 2 positional arguments but 3 were given",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mTypeError\u001b[0m                                 Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[171], line 1\u001b[0m\n\u001b[1;32m----> 1\u001b[0m \u001b[43mfinal_pipeline\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mfit\u001b[49m\u001b[43m(\u001b[49m\u001b[43mfeatures_train\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43mtarget_train\u001b[49m\u001b[43m)\u001b[49m\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\base.py:1151\u001b[0m, in \u001b[0;36m_fit_context.<locals>.decorator.<locals>.wrapper\u001b[1;34m(estimator, *args, **kwargs)\u001b[0m\n\u001b[0;32m   1144\u001b[0m     estimator\u001b[38;5;241m.\u001b[39m_validate_params()\n\u001b[0;32m   1146\u001b[0m \u001b[38;5;28;01mwith\u001b[39;00m config_context(\n\u001b[0;32m   1147\u001b[0m     skip_parameter_validation\u001b[38;5;241m=\u001b[39m(\n\u001b[0;32m   1148\u001b[0m         prefer_skip_nested_validation \u001b[38;5;129;01mor\u001b[39;00m global_skip_validation\n\u001b[0;32m   1149\u001b[0m     )\n\u001b[0;32m   1150\u001b[0m ):\n\u001b[1;32m-> 1151\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[43mfit_method\u001b[49m\u001b[43m(\u001b[49m\u001b[43mestimator\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43margs\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mkwargs\u001b[49m\u001b[43m)\u001b[49m\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\pipeline.py:416\u001b[0m, in \u001b[0;36mPipeline.fit\u001b[1;34m(self, X, y, **fit_params)\u001b[0m\n\u001b[0;32m    390\u001b[0m \u001b[38;5;250m\u001b[39m\u001b[38;5;124;03m\"\"\"Fit the model.\u001b[39;00m\n\u001b[0;32m    391\u001b[0m \n\u001b[0;32m    392\u001b[0m \u001b[38;5;124;03mFit all the transformers one after the other and transform the\u001b[39;00m\n\u001b[1;32m   (...)\u001b[0m\n\u001b[0;32m    413\u001b[0m \u001b[38;5;124;03m    Pipeline with fitted steps.\u001b[39;00m\n\u001b[0;32m    414\u001b[0m \u001b[38;5;124;03m\"\"\"\u001b[39;00m\n\u001b[0;32m    415\u001b[0m fit_params_steps \u001b[38;5;241m=\u001b[39m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39m_check_fit_params(\u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mfit_params)\n\u001b[1;32m--> 416\u001b[0m Xt \u001b[38;5;241m=\u001b[39m \u001b[38;5;28;43mself\u001b[39;49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43m_fit\u001b[49m\u001b[43m(\u001b[49m\u001b[43mX\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43my\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mfit_params_steps\u001b[49m\u001b[43m)\u001b[49m\n\u001b[0;32m    417\u001b[0m \u001b[38;5;28;01mwith\u001b[39;00m _print_elapsed_time(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mPipeline\u001b[39m\u001b[38;5;124m\"\u001b[39m, \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39m_log_message(\u001b[38;5;28mlen\u001b[39m(\u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39msteps) \u001b[38;5;241m-\u001b[39m \u001b[38;5;241m1\u001b[39m)):\n\u001b[0;32m    418\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39m_final_estimator \u001b[38;5;241m!=\u001b[39m \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mpassthrough\u001b[39m\u001b[38;5;124m\"\u001b[39m:\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\pipeline.py:370\u001b[0m, in \u001b[0;36mPipeline._fit\u001b[1;34m(self, X, y, **fit_params_steps)\u001b[0m\n\u001b[0;32m    368\u001b[0m     cloned_transformer \u001b[38;5;241m=\u001b[39m clone(transformer)\n\u001b[0;32m    369\u001b[0m \u001b[38;5;66;03m# Fit or load from cache the current transformer\u001b[39;00m\n\u001b[1;32m--> 370\u001b[0m X, fitted_transformer \u001b[38;5;241m=\u001b[39m \u001b[43mfit_transform_one_cached\u001b[49m\u001b[43m(\u001b[49m\n\u001b[0;32m    371\u001b[0m \u001b[43m    \u001b[49m\u001b[43mcloned_transformer\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m    372\u001b[0m \u001b[43m    \u001b[49m\u001b[43mX\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m    373\u001b[0m \u001b[43m    \u001b[49m\u001b[43my\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m    374\u001b[0m \u001b[43m    \u001b[49m\u001b[38;5;28;43;01mNone\u001b[39;49;00m\u001b[43m,\u001b[49m\n\u001b[0;32m    375\u001b[0m \u001b[43m    \u001b[49m\u001b[43mmessage_clsname\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[38;5;124;43m\"\u001b[39;49m\u001b[38;5;124;43mPipeline\u001b[39;49m\u001b[38;5;124;43m\"\u001b[39;49m\u001b[43m,\u001b[49m\n\u001b[0;32m    376\u001b[0m \u001b[43m    \u001b[49m\u001b[43mmessage\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[38;5;28;43mself\u001b[39;49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43m_log_message\u001b[49m\u001b[43m(\u001b[49m\u001b[43mstep_idx\u001b[49m\u001b[43m)\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m    377\u001b[0m \u001b[43m    \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mfit_params_steps\u001b[49m\u001b[43m[\u001b[49m\u001b[43mname\u001b[49m\u001b[43m]\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m    378\u001b[0m \u001b[43m\u001b[49m\u001b[43m)\u001b[49m\n\u001b[0;32m    379\u001b[0m \u001b[38;5;66;03m# Replace the transformer of the step with the fitted\u001b[39;00m\n\u001b[0;32m    380\u001b[0m \u001b[38;5;66;03m# transformer. This is necessary when loading the transformer\u001b[39;00m\n\u001b[0;32m    381\u001b[0m \u001b[38;5;66;03m# from the cache.\u001b[39;00m\n\u001b[0;32m    382\u001b[0m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39msteps[step_idx] \u001b[38;5;241m=\u001b[39m (name, fitted_transformer)\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\joblib\\memory.py:353\u001b[0m, in \u001b[0;36mNotMemorizedFunc.__call__\u001b[1;34m(self, *args, **kwargs)\u001b[0m\n\u001b[0;32m    352\u001b[0m \u001b[38;5;28;01mdef\u001b[39;00m \u001b[38;5;21m__call__\u001b[39m(\u001b[38;5;28mself\u001b[39m, \u001b[38;5;241m*\u001b[39margs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mkwargs):\n\u001b[1;32m--> 353\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[38;5;28;43mself\u001b[39;49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mfunc\u001b[49m\u001b[43m(\u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43margs\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mkwargs\u001b[49m\u001b[43m)\u001b[49m\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\pipeline.py:950\u001b[0m, in \u001b[0;36m_fit_transform_one\u001b[1;34m(transformer, X, y, weight, message_clsname, message, **fit_params)\u001b[0m\n\u001b[0;32m    948\u001b[0m \u001b[38;5;28;01mwith\u001b[39;00m _print_elapsed_time(message_clsname, message):\n\u001b[0;32m    949\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28mhasattr\u001b[39m(transformer, \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mfit_transform\u001b[39m\u001b[38;5;124m\"\u001b[39m):\n\u001b[1;32m--> 950\u001b[0m         res \u001b[38;5;241m=\u001b[39m \u001b[43mtransformer\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mfit_transform\u001b[49m\u001b[43m(\u001b[49m\u001b[43mX\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43my\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mfit_params\u001b[49m\u001b[43m)\u001b[49m\n\u001b[0;32m    951\u001b[0m     \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m    952\u001b[0m         res \u001b[38;5;241m=\u001b[39m transformer\u001b[38;5;241m.\u001b[39mfit(X, y, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mfit_params)\u001b[38;5;241m.\u001b[39mtransform(X)\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\utils\\_set_output.py:140\u001b[0m, in \u001b[0;36m_wrap_method_output.<locals>.wrapped\u001b[1;34m(self, X, *args, **kwargs)\u001b[0m\n\u001b[0;32m    138\u001b[0m \u001b[38;5;129m@wraps\u001b[39m(f)\n\u001b[0;32m    139\u001b[0m \u001b[38;5;28;01mdef\u001b[39;00m \u001b[38;5;21mwrapped\u001b[39m(\u001b[38;5;28mself\u001b[39m, X, \u001b[38;5;241m*\u001b[39margs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mkwargs):\n\u001b[1;32m--> 140\u001b[0m     data_to_wrap \u001b[38;5;241m=\u001b[39m \u001b[43mf\u001b[49m\u001b[43m(\u001b[49m\u001b[38;5;28;43mself\u001b[39;49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43mX\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43margs\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mkwargs\u001b[49m\u001b[43m)\u001b[49m\n\u001b[0;32m    141\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28misinstance\u001b[39m(data_to_wrap, \u001b[38;5;28mtuple\u001b[39m):\n\u001b[0;32m    142\u001b[0m         \u001b[38;5;66;03m# only wrap the first output for cross decomposition\u001b[39;00m\n\u001b[0;32m    143\u001b[0m         return_tuple \u001b[38;5;241m=\u001b[39m (\n\u001b[0;32m    144\u001b[0m             _wrap_data_with_container(method, data_to_wrap[\u001b[38;5;241m0\u001b[39m], X, \u001b[38;5;28mself\u001b[39m),\n\u001b[0;32m    145\u001b[0m             \u001b[38;5;241m*\u001b[39mdata_to_wrap[\u001b[38;5;241m1\u001b[39m:],\n\u001b[0;32m    146\u001b[0m         )\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\sklearn\\base.py:918\u001b[0m, in \u001b[0;36mTransformerMixin.fit_transform\u001b[1;34m(self, X, y, **fit_params)\u001b[0m\n\u001b[0;32m    915\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mfit(X, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mfit_params)\u001b[38;5;241m.\u001b[39mtransform(X)\n\u001b[0;32m    916\u001b[0m \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m    917\u001b[0m     \u001b[38;5;66;03m# fit method of arity 2 (supervised transformation)\u001b[39;00m\n\u001b[1;32m--> 918\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[38;5;28;43mself\u001b[39;49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mfit\u001b[49m\u001b[43m(\u001b[49m\u001b[43mX\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43my\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mfit_params\u001b[49m\u001b[43m)\u001b[49m\u001b[38;5;241m.\u001b[39mtransform(X)\n",
      "\u001b[1;31mTypeError\u001b[0m: DataCleaner.fit() takes 2 positional arguments but 3 were given"
     ]
    }
   ],
   "source": [
    "final_pipeline.fit(features_train, target_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6a4d26f7-b8ba-4cb4-88ff-5e9a209d8902",
   "metadata": {},
   "outputs": [],
   "source": [
    " 3, 37, 82"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "30103a19-8875-4382-ac33-dba0cd7cc444",
   "metadata": {},
   "outputs": [],
   "source": [
    "example_1 = data[data['id'] == 3]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d8758779-31d8-454e-9343-27c7e13cf301",
   "metadata": {},
   "outputs": [],
   "source": [
    "example_1['price']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5a99288c-f81d-4bd0-88e9-bcbccbb9f399",
   "metadata": {},
   "outputs": [],
   "source": [
    "model_1.predict(sscaler.transform())"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
