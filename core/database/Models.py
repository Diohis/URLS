import asyncpg
from core.database import config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    class Object:
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


class Model(metaclass=Singleton):
    def __init__(self):
        self.table = self.__class__.__name__

    async def get(self, *args,**kwargs):
        data = "*"
        connection = None
        if args:
            data = ", ".join(args)
        try:
            connection = await asyncpg.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                               port=config.PORT, database=config.DATABASE)
        except Exception as e:
            print(e)
            print("[ERROR] - Не удалось подключиться к базе")
            return None
        query = []
        for key, value in kwargs.items():
            query.append(f"{key} = '{value}'")
        params = await connection.fetch(f"SELECT {data} FROM {self.table} WHERE {' AND '.join(query)} ;")
        await connection.close()
        if len(params)>1:
            return tuple(self.__class__.Object(**value) for value in params)
        elif len(params)==1:
            return self.__class__.Object(**dict(params[0]))
        else:
            return None


    async def set(self, record):
        connection = None
        try:
            connection = await asyncpg.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                               port=config.PORT, database=config.DATABASE)
        except:
            print("[ERROR] - Не удалось подключиться к базе")
        query = []
        for key, value in record.__dict__.items():
            if key == "types":
                continue
            query.append(f"{key} = '{value}'")
        try:
            await connection.execute(f"UPDATE {self.table} SET {' , '.join(query)} WHERE {query[0]} ;")
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
        finally:
            await connection.close()

    async def remove(self, record: Singleton.Object):
        connection = None
        try:
            connection = await asyncpg.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                               port=config.PORT, database=config.DATABASE)
        except:
            print("[ERROR] - Не удалось подключиться к базе")
            return
        try:
            await connection.execute(f"DELETE FROM {self.table} WHERE id = {record.__dict__["id"]} ;")
        except AttributeError:
            print("[WARNING] AttributeError - Возможно записи не существует")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
        finally:
            await connection.close()

    async def create(self, record:dict):
        connection = None
        try:
            connection = await asyncpg.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                               port=config.PORT, database=config.DATABASE)
        except:
            print("[ERROR] - Не удалось подключиться к базе")
            return
        try:
            await connection.execute(f"INSERT INTO {self.table} ({", ".join(list(record.keys()))}) VALUES {tuple(record.values())} ;")
        except Exception as e:
            print(f"[WARNING] Exception - {e}")
        finally:
            await connection.close()
    #Для скачивания csv файла. Передавать уникальный ключ (id или что-то такое)
    async def download(self,**kwargs):
        connection = await asyncpg.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                           port=config.PORT, database=config.DATABASE)
        query = []
        un = ""
        for key, value in kwargs.items():
            un = value
            query.append(f"{key} = '{value}'")
        print()
        result = await connection.copy_from_query(
            f"SELECT * FROM redirects WHERE {' AND '.join(query)}",
            output=f'{un}.csv', format='csv')
        print(result)