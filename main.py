import psycopg2, sys
from config import host, user, password, dbname
from mainWindows import *
import logging

LOG_FILE = "app_log.log"
logger = logging.getLogger("demo_app")
logger.setLevel(logging.INFO)

# Убираем старые обработчики
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Отключаем двойное логирование через root-логгер
logger.propagate = False

connection = None

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=dbname
    )
    connection.autocommit = True
    logger.info("Подключение к БД установлено.")
except Exception as _ex:
   print("Ошибка при работе с PosgreSQL", _ex)


if __name__ == "__main__":
    logger.info('Проект открыт')
    app = QtWidgets.QApplication([])
    widget = MainWidget()
    widget.resize(1000, 800)
    widget.show()
    try:
        sys.exit(app.exec())
    finally:
        logger.info("Приложение завершило работу.")