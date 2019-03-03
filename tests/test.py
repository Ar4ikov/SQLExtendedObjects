# | Created by Ar4ikov
# | Время: 25.02.2019 - 20:52
from typing import List, Type
import unittest
from sql_extended_objects import ExtRequests, ExtObject


class ExtTest(unittest.TestCase):

    def test_connection(self):
        # Проверка соединения с бд
        self.assertTrue(ExtRequests(":memory:"))

    # После первого юнит-теста создаем ряд экземпляров и наследников
    class User(ExtObject):
        def __init__(self, **data):
            super().__init__(**data)

    db = ExtRequests(":memory:")

    db.commit(
        """
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            name TEXT(50) ,
            age INTEGER(4)
        );
        """
    )

    def test_class_create(self):
        # Проверка на получение списка после пустого ответа
        self.assertIsInstance(ExtTest.db.select_all("test", ExtTest.User), List)

        ExtTest.db.commit("""INSERT INTO test (`name`, `age`) VALUES ('Ar4ikov', '16');""")

        # Проверка на получение ряда из бд как класса
        self.assertIsInstance(ExtTest.db.select_all("test", ExtTest.User, where="`id`=1"), List)

        statement = ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")[0]
        statement["name"] = "Ar4ikov228"

        # Проверка на обновлении в бд данного ряда
        self.assertEqual(ExtTest.db.select_all("test", ExtTest.User)[0].name, "Ar4ikov228")

    def test_class_attrs(self):
        ExtTest.db.commit("""INSERT INTO test (`name`, `age`) VALUES ('Ar4ikov', '16');""")

        # Primary key test
        self.assertIsNotNone(ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")[0].pk)

        # Other columns test
        self.assertIsNotNone(ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")[0].name)
        self.assertIsNotNone(ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")[0].age)

    def test_other_equals(self):
        ExtTest.db.commit("""INSERT INTO test (`name`, `age`) VALUES ('Ar4ikov', '16');""")
        ExtTest.db.commit("""INSERT INTO test (`name`, `age`) VALUES ('Nikita', '16');""")

        user_1 = ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")
        user_2 = ExtTest.db.select_all("test", ExtTest.User, where="`id`=1")
        user_3 = ExtTest.db.select_all("test", ExtTest.User, where="`id`=2")

        self.assertTrue(user_1 == user_2)
        self.assertFalse(user_1 != user_2)

        self.assertFalse(user_1 == user_3)
        self.assertTrue(user_1 != user_3)

        self.assertTrue(user_1 < user_3)
        self.assertFalse(user_1 > user_3)

        self.assertFalse(user_1 < user_2)
        self.assertFalse(user_1 > user_2)

        self.assertTrue(user_1 <= user_2)
        self.assertTrue(user_1 >= user_2)

        self.assertTrue(user_1 <= user_3)
        self.assertFalse(user_1 >= user_3)

    def test_insert_into(self):
        class NewUser(ExtObject):
            def __init__(self, **data):
                super().__init__(**data)

        new_user = NewUser()

        new_user.name = "TestingUser228"
        new_user.age = 10

        self.assertIsInstance(ExtTest.db.insert_into("test", new_user), List)

        new_user = ExtTest.db.select_all("test", new_user, where="`id` = 3")[0]
        new_user_ = ExtTest.db.insert_into("test", new_user)[0]

        # print(new_user, new_user_)
        self.assertTrue(new_user < new_user_)

    def test_reset_row(self):
        user = ExtTest.db.select_all("test", ExtTest.User, where="`id` = 1")[0]

        user.remove()

        self.assertEqual(ExtTest.db.select_all("test", ExtTest.User, where="`id` = 1"), [])

    def test_utils(self):
        users = ExtTest.db.select_all("test", ExtTest.User)
        user = ExtTest.db.select_all("test", ExtTest.User, where="`id` = 2")[0]

        self.assertEqual(ExtTest.db.utils.get(
            users, id=2
        ), user)

        ExtTest.db.utils.update_all(users, age=17)
        self.assertEqual(ExtTest.db.select_all("test", ExtTest.User, where="`id` = 3")[0].age, 17)

        ExtTest.db.utils.remove_all(users)
        self.assertEqual(ExtTest.db.select_all("test", ExtTest.User), [])


if __name__ == "__main__":
    unittest.main()
