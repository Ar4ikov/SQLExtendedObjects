# SQL Extended Objects

- Q: А зачем?
- A: А затем. Вместо обычного получения списка-матрицы с рядами в таблице, можно
получить классы и обращаться к атрибутам класса, как к колонкам в таблице SQL.
---
- Q: Полезно ли?
- A: Да, полезно и удобно.
---
- Q: А что по багам? Тесты хоть есть?
- A: Да, и юнит, и даже интеграционные (в мыслях у разраба).
---

### Установка
```console
root@Ar4ikov:~$ pip install sql_extended_objects
```

###Коротко о функционале

- Создание класса, который будет отвечать за ряд в таблице.
```python

from sql_extended_objects import ExtObject

class User(ExtObject):
    def __init__(self, **data):
        super().__init__(**data)
    
    def my_method(self):
        pass
        
    def other_method(self):
        pass
        
```

- Подключение к SQLite3 БД и получение из таблицы
```python
from sql_extended_objects import ExtRequests

database = ExtRequests("database.db")

users = database.select_all("my_table", User, where="`id` = 1")

if users:
    user = users[0]

# Обращение к атрибутам класса
# Таблица вида: 
# -------------------
# id | first_name | last_name | age | nickname

print(user.first_name)
# Out: "Nikita"

print(user.last_name)
# Out: "Archikov"

print(user.id)
# Out: 1

print(user.pk)  # -> PRIMARY KEY нашей таблицы. Если нет - "id"
# Out: "id"

# Изменеие атрибута и автоматическая синхронизация с таблицей
user["age"] = 17

# Удаление класса и удаление ряда из таблицы
user.remove()

# Очистка атрибутов в экземляре
user.reset()

# Сравнение экземпляров по PRIMARY KEY

print(user == user)
# Out: True

print(user <= user)
# Out: True

print(user > user)
# Out: False

```

- Стандартные SQL-запросы
```python
from sql_extended_objects import ExtRequests

database = ExtRequests("database.db")

database.execute("""SELECT * FROM `my_table` WHERE `id` = 1;""")

# Запрос с авто-коммитом
database.commit("""UPDATE `my_table` SET `age` = 17 WHERE `id` = 1;""")

```

- Парочка встроенных методов для помощи в поиске из классов
```python
from sql_extended_objects import ExtRequests, ExtObject


class User(ExtObject):
    def __init__(self, **data):
        super().__init__(**data)
    
    def my_method(self):
        pass
        
    def other_method(self):
        pass
        


database = ExtRequests("database.db")

# Получение класса из списка
users = database.select_all("my_table", User)
this_user = database.utils.get(users, id=1)

# Обвноление атрибутов у всех классов
users = database.utils.update_all(users, age=17)

# Удаление всех классов из списка и из таблицы
database.utils.remove_all(users)

```

Ну, собственно, всё. Если у вас есть какие-то пожелания - смело прошу в `Pull-Requests` писать.