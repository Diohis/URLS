import asyncpg
from core.database import  config
import sqlite3

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]

class Record:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__dict__ = {}
        types = {}
        for key, value in kwargs.items():
            instance.__dict__[key] = value
            types[key] = type(value)
        instance.__dict__["types"] = types
        return instance

    def __setattr__(self, name, value):
        if name in ('id', "types"):
            raise AttributeError('Unable to edit')
        if dict(self.__dict__).get("types"):
            if dict(self.__dict__).get("types")[name] != type(value):
                raise AttributeError('Unable to edit')
        return super().__setattr__(name, value)

class ConnectPostgreSQL(metaclass=Singleton):

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.connection = None

    async def checkConnection(self):
        if (not (self.connection)):
            self.connection = await asyncpg.connect(user=self.user, password=self.password, host=self.host,
                                                    port=self.port, database=self.database)

    async def get(self, SQL):
        await self.checkConnection()
        params = await self.connection.fetch(SQL)
        return params

    async def set(self, SQL):
        await self.checkConnection()
        try:
            await self.connection.execute(SQL)
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def remove(self, SQL):
        await self.checkConnection()
        try:
            await self.connection.execute(SQL)
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def create(self, SQL):
        await self.checkConnection()
        try:
            await self.connection.execute(SQL)
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
class ConnectSQLite3(metaclass=Singleton):
    def dict_factory(self, cursor,row):
        d = {}  # Создаем пустой словарь
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]  # Заполняем его значениями
        return d
    def __init__(self,path:str):
        self.path = path
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = self.dict_factory
        self.cursor = self.connection.cursor()

    async def checkConnection(self):
        if (not(self.connection)or not(self.cursor)):
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
    async def get(self, SQL):
        await self.checkConnection()
        params = self.cursor.execute(SQL)
        return params.fetchall()

    async def set(self, SQL):
        await self.checkConnection()
        try:
            self.cursor.execute(SQL)
            self.connection.commit()
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def remove(self, SQL):
        await self.checkConnection()
        try:
            self.cursor.execute(SQL)
            self.connection.commit()
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def create(self, SQL):
        await self.checkConnection()
        try:
            self.cursor.execute(SQL)
            self.connection.commit()
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
class Model():
    def __init__(self,connection: ConnectPostgreSQL|ConnectSQLite3):
        self.table = self.__class__.__name__
        self.connection = connection
    async def get(self, *args,**kwargs):
        data = "*"
        where = ""
        if args:
            data = ", ".join(args)
        query = []
        if kwargs:
            where = "WHERE"
        for key, value in kwargs.items():
            query.append(f"{key} = '{value}'")
        where +=" "+' AND '.join(query)
        params = await self.connection.get(f'SELECT {data} FROM {self.table} {where};')
        if len(params)>1:
            return tuple(Record(**value) for value in params)
        elif len(params)==1:
            return [Record(**dict(params[0]))]
        else:
            return None


    async def set(self, record):
        query = []
        for key, value in record.__dict__.items():
            if key == "types":
                continue
            query.append(f"{key} = '{value}'")
        try:
            await self.connection.set(f"UPDATE {self.table} SET {' , '.join(query)} WHERE {query[0]} ;")
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def remove(self, record: Record):
        try:
            await self.connection.remove(f"DELETE FROM {self.table} WHERE id = {record.__dict__['id']} ;")
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")

    async def create(self, record:dict):
        try:
            print(f"INSERT INTO {self.table} ({", ".join(list(record.keys()))}) VALUES {tuple(record.values())} ;")
            await self.connection.create(f'INSERT INTO {self.table} ({", ".join(list(record.keys()))}) VALUES {tuple(record.values())} ;')
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
