# | Created by Ar4ikov
# | Время: 25.02.2019 - 20:17
import sqlite3
from sqlite3 import connect
from typing import List


class ExtObject:
    def __init__(self, **data):

        self.working_params = ["working_params", "database", "table_name", "data_", "primary_key", "pk"]

        self.database: ExtRequests = data.get("database")

        self.table_name = data.get("table_name")
        self.data_ = data.get("data")
        self.primary_key = data.get("pk")

        if self.data_:
            for k, v in self.data_.items():
                self.__setattr__(k, v)

    def __getattr__(self, item):
        """Динамическоп получение аттрибудтов класса"""

        return self.__dict__.get(item)

    def __gt__(self, other):
        return getattr(self, self.pk, "id") > getattr(other, other.pk, "id")

    def __lt__(self, other):
        return getattr(self, self.pk, "id") < getattr(other, other.pk, "id")

    def __ge__(self, other):
        return getattr(self, self.pk, "id") >= getattr(other, other.pk, "id")

    def __le__(self, other):
        return getattr(self, self.pk, "id") <= getattr(other, other.pk, "id")

    def __eq__(self, other):
        return getattr(self, self.pk, "id") == getattr(other, other.pk, "id") and self.table_name == other.table_name

    def __ne__(self, other):
        return getattr(self, self.pk, "id") != getattr(other, other.pk, "id") or self.table_name != other.table_name

    def __setitem__(self, key, value):
        """
        Обновление ряда в таблице путём изменения атрибута класса

        :param key: атрибут
        :param value: значение артибута
        :return: idk
        """

        self.database.commit(
            """UPDATE `{table_name}` SET `{key}` = '{value}' WHERE `{pk}` = '{pk_val}';""".format(
                table_name=self.table_name,
                key=key,
                value=value,
                pk=self.database.get_pk_column(self.table_name),
                pk_val=getattr(self, self.database.get_pk_column(self.table_name), "id")
            )
        )

        return self.__setattr__(key, value)

    def reset(self):
        self.__dict__ = {}

        return self

    def remove(self):
        """Удаление класса и ряда из таблицы"""

        self.database.commit("""DELETE FROM `{table_name}` WHERE `{pk}` = '{pk_val}';""".format(
            table_name=self.table_name,
            pk=self.database.get_pk_column(self.table_name),
            pk_val=getattr(self, self.database.get_pk_column(self.table_name), "id")
        ))

        del self

    def __call__(self, **data):
        return ExtObject(**data)

    def get(self, where):
        """Получение нового класса взамен на текущий путём поиска в таблице по указателю (например `id`=1"""
        return self.database.select_all(
            self.table_name,
            """SELECT * FROM `{table_name}` WHERE {sql};""".format(
                table_name=self.table_name,
                sql=where
            ), self
        )


class ExtUtils:
    @staticmethod
    def get(list_: List[ExtObject], **keys):
        for cls in list_:
            for key in keys.keys():
                if getattr(cls, key, None) == keys[key]:
                    return cls

        return None

    @staticmethod
    def update_all(list_: List[ExtObject], **data):
        for cls in list_:
            for k, v in data.items():
                cls[k] = v

        return list_

    @staticmethod
    def remove_all(list_: List[ExtObject]):
        for cls in list_:
            cls.remove()

        return True


class ExtRequests:
    def __init__(self, name, check_same_thread=False):
        self.name = name

        self.database = connect(database=name, check_same_thread=check_same_thread)
        self.cursor = self.database.cursor()

    @property
    def utils(self):
        return ExtUtils

    def execute(self, sql) -> sqlite3.Cursor:
        """
        Обычный query запрос

        :param sql: запрос
        :return: sqlite3.Cursor
        """

        return self.cursor.execute(sql)

    def select_all(self, table_name, cls, where=None, limit=None) -> List[ExtObject]:
        """
        Возвращает список с классами при полной выборке элементов

        :param table_name: имя таблицы
        :param cls: класс, в который надо подгрузить ряды в таблице
        :param where: точное указание ряда, который нам нужен по параметру (например `id`=1)
        :return: List[None] или List[ExtObject] - классами наследниками
        """

        if not where and not limit:
            where = """SELECT * FROM `{table_name}`;""".format(table_name=table_name)
        elif not limit:
            where = """SELECT * FROM `{table_name}` WHERE {where};""".format(table_name=table_name, where=where)
        elif not where:
            where = """SELECT * FROM `{table_name}` LIMIT {limit};""".format(table_name=table_name, limit=limit)
        else:
            where = """SELECT * FROM `{table_name}` WHERE {where} LIMIT {limit};""".format(table_name=table_name,
                                                                                           where=where, limit=limit)

        query = self.cursor.execute(where).fetchall()
        table_structure = self.cursor.execute("""PRAGMA table_info(`{}`)""".format(table_name)).fetchall()

        table_structure = [x[1] for x in table_structure]

        response = []
        for data in query:
            data_ = dict(zip(table_structure, data))
            data_["pk"] = self.get_pk_column(table_name)

            response.append(cls(database=self, table_name=table_name, data=data_))

        return response

    def get_pk_column(self, table_name) -> str:
        """
        Получение колонны PRIMARY KEY

        :param table_name: имя таблицы
        :return: str имя PRIMARY KEY COLUMN
        """

        tstruct = self.cursor.execute("""PRAGMA table_info(`{}`);""".format(table_name)).fetchall()
        primary_key = None
        for column in tstruct:
            if column[5]:
                primary_key = column[1]
                break

        if not primary_key:
            primary_key = "id"

        return primary_key

    def insert_into(self, table_name, cls: ExtObject):
        """
        Добавления ряда в таблицу

        :param table_name: имя таблицы
        :param cls: класс, который надо загрузить в таблицу
        :return: List[ExtObject] or List[None]
        """

        keys, values = [], []

        for k, v in cls.__dict__.items():
            if k not in cls.working_params and k != cls.pk:
                keys.append("`{}`".format(k))
                values.append("'{}'".format(v))

        if not getattr(cls, "table_name", None):
            cls.table_name = table_name

        return self.commit("""INSERT INTO `{table_name}` ({keys}) VALUES ({values});""".format(
            table_name=table_name,
            keys=", ".join(keys),
            values=", ".join(values)
        ), cls)

    def commit(self, sql, cls: ExtObject = None) -> ExtObject or bool:
        """
        Запрос с автокоммитом. При указании класса, возвращает список с обновлёнными классами

        :param sql: query запрос
        :param cls: класс для подргузки рядов в таблице
        :return: True или список с классами-наследниками ExtObject
        """

        self.cursor.execute(sql)
        self.database.commit()

        if cls:
            table_name = cls.table_name
            tstruct = self.cursor.execute("""PRAGMA table_info(`{}`);""".format(table_name)).fetchall()
            primary_key = None
            for column in tstruct:
                if column[5]:
                    primary_key = column[1]
                    break

            if not primary_key:
                primary_key = "id"

            return self.select_all(table_name, cls, where="`{}` = '{}'".format(primary_key, self.cursor.lastrowid))

        return True
