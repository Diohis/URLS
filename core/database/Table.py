from core.database.Models import Model,ConnectPostgreSQL
from core.database import config
#===============Здесь создавать классы===============#
# Пример:
class Test(Model): # Название должно быть один в один с названием таблицы в базе. В наследниках обязательно Model
    pass # Здесь ничего писать не надо, pass будет достаточно

class users(Model):
    pass

class urls(Model):
    pass

class redirects(Model):
    pass

#===============Здесь создаем экземпляр класса для дальшейней работы с конкретной таблицей===============#
connect = ConnectPostgreSQL(config.USER,config.PASSWORD,config.HOST,config.PORT,config.DATABASE)
table_user = users(connect)
table_url = urls(connect)
table_redirects = redirects(connect)
#===============После создания данных экземпляров - импортируем эти переменные в модули, где нужна работа с соответствующей таблицей===============#