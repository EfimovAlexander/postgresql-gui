from PySide6 import QtCore, QtWidgets, QtGui
from main import logger, connection

def list_schema():
    list_schemas = ['Не выбрано']
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT schema_name FROM information_schema.schemata
                    """)
            schemas = cursor.fetchall()
            for s in schemas:
                list_schemas.append(s[0])
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка",
            f"Не удалось получить список схем:\n{e}"
        )
        logger.info('Ошибка при получении списка схем, %s', e)

    return list_schemas
def lists_tables():
    list_table = ["Не выбрано"]
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s 
                ORDER BY table_name;
            """, (schema,))
            tables = cursor.fetchall()
            for t in tables:
                list_table.append(t[0])
    except Exception as e:
        print("Ошибка:", e)
    return list_table
def list_attributes(schema, table):
    list_attributes = ["Не выбрано"]
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    AND table_name = %s
                """, (schema, table))
            attributes = cursor.fetchall()
            for a in attributes:
                list_attributes.append(a[0])
    except Exception as e:
        QtWidgets.QMessageBox.critical("Ошибка", f"Не удалось получить список атрибутов:\n{e}")
    return list_attributes
def list_unique_attributes(schema, table):
    pass

schema = ''

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
                    QWidget {
                        background-image: url('E:/Питон. Проекты/Лаба БД/background.jpg');
                        background-repeat: no-repeat;
                        background-position: center;
                        background-attachment: fixed;
                    }
                """)
        self.layout = QtWidgets.QVBoxLayout(self) #Распологает кнопки вертикально
        # Объявление кнопок
        self.buttonSetSchema = QtWidgets.QPushButton("Выбрать схему")
        self.buttonCreateUser = QtWidgets.QPushButton("Добавить пользователя")
        self.buttonCreateSchema = QtWidgets.QPushButton("Создать схему")
        self.buttonCreateTable = QtWidgets.QPushButton("Создать таблицу")
        self.buttonCreateColumn = QtWidgets.QPushButton("Создать колонку в таблице")
        self.buttonCreateData = QtWidgets.QPushButton("Внести запись в таблицу")
        self.buttonDropTable = QtWidgets.QPushButton("Удалить таблицу")
        # Добавление кнопок на главный экран
        self.layout.addWidget(self.buttonSetSchema)
        self.layout.addWidget(self.buttonCreateUser)
        self.layout.addWidget(self.buttonCreateSchema)
        self.layout.addWidget(self.buttonCreateTable)
        self.layout.addWidget(self.buttonCreateColumn)
        self.layout.addWidget(self.buttonCreateData)
        self.layout.addWidget(self.buttonDropTable)
        # Сигналы кнопок
        self.buttonCreateColumn.clicked.connect(self.openCreateColumn)
        self.buttonSetSchema.clicked.connect(self.openSetSchema)
        self.buttonCreateUser.clicked.connect(self.openCreateUser)
        self.buttonCreateSchema.clicked.connect(self.openCreateSchema)
        self.buttonCreateData.clicked.connect(self.openCreateData)
        self.buttonDropTable.clicked.connect(self.openDropTable)
        self.buttonCreateTable.clicked.connect(self.openCreateTable)
        #self.setEnabledButton()
        #self.warning()
    def warning(self):
        QtWidgets.QMessageBox.information(
            self, "Приветствие",
            f"Перед началом работы выберите схему!"
        )
    def openCreateColumn(self):
        self.col_window = CreateColumn()
        self.col_window.exec()
    def setEnabledButton(self):
        if schema == '':
            self.buttonCreateTable.setEnabled(False)
            self.buttonDropTable.setEnabled(False)
            self.buttonCreateData.setEnabled(False)
        else:
            self.buttonCreateTable.setEnabled(True)
            self.buttonDropTable.setEnabled(True)
            self.buttonCreateData.setEnabled(True)
    def openSetSchema(self):
        self.col_window = SetSchema()
        self.col_window.exec()
        self.setEnabledButton()  # обновляем доступность кнопок
    def openCreateData(self):
        # создаём экземпляр окна
        self.col_window = CreateData()
        # self.col_window.show()   # немодальное окно
        self.col_window.exec() # если нужно модальное окно (блокирует родителя)
    def openDropTable(self):
        self.col_window = DropTable()
        self.col_window.exec()
    def openCreateTable(self):
        self.col_window = CreateTable()
    def openCreateSchema(self):
        self.col_window = CreateSchema()
        self.col_window.exec()
    def openCreateUser(self):
        self.col_window = CreateUser()
        self.col_window.exec()
class SetSchema(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбрать схему")
        self.resize(100, 100)
        self.layout = QtWidgets.QFormLayout(self)
        # Объявление объектов
        self.nameSchema = QtWidgets.QComboBox(self)
        schemas = list_schema()
        if schemas:
            self.nameSchema.addItems(schemas)
        else:
            self.nameSchema.addItem("Нет схем")
            self.nameSchema.setEnabled(False)
        self.layout.addRow("Наименование схемы",self.nameSchema)
        self.ok_button = QtWidgets.QPushButton("Выбрать")
        self.cancel_button = QtWidgets.QPushButton("Отмена")
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        self.layout.addRow(btn_layout)
        self.ok_button.clicked.connect(self.setSchema)
        self.cancel_button.clicked.connect(self.reject)

    def setSchema(self):
        global schema
        schema = self.nameSchema.currentText()
        QtWidgets.QMessageBox.information(
            self,
            "Успех",
            f"Выбрана схема {schema}."
        )
        logger.info(f"Выбрана схема {schema}.")
        self.accept()
class CreateColumn(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить колонку")
        self.resize(400, 250)

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addRow("Рабочая схема", QtWidgets.QLabel(schema))

        # --- Поля для колонки ---
        self.nameColumn = QtWidgets.QLineEdit(self)
        self.layout.addRow("Наименование колонки", self.nameColumn)

        self.dataType = QtWidgets.QComboBox(self)
        self.dataType.addItems(
            ['BIGINT', 'BOOLEAN', 'CHAR', 'DATE', 'DATETIME', 'DECIMAL', 'INTEGER', 'INTERVAL', 'SERIAL', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'VARCHAR']
        )
        self.layout.addRow("Тип данных:", self.dataType)

        # --- Флаги ---
        self.setPrimeryKey = QtWidgets.QCheckBox(self)
        self.layout.addRow("PRIMARY KEY", self.setPrimeryKey)

        self.setNull = QtWidgets.QCheckBox(self)
        self.layout.addRow("NOT NULL", self.setNull)

        self.setUnique = QtWidgets.QCheckBox(self)
        self.layout.addRow("UNIQUE", self.setUnique)

        self.setForeignKey = QtWidgets.QCheckBox(self)
        self.layout.addRow("FOREIGN KEY", self.setForeignKey)

        # --- Виджеты для внешнего ключа (создаём сразу, но скрываем) ---
        self.nameTable = QtWidgets.QComboBox(self)
        self.nameAttribute = QtWidgets.QComboBox(self)
        self.nameTable.hide()
        self.nameAttribute.hide()
        self.layout.addRow("Название таблицы", self.nameTable)
        self.layout.addRow("Название атрибута", self.nameAttribute)

        # --- Сигналы ---
        self.setPrimeryKey.stateChanged.connect(self.setPrimeryKeyState)
        self.setForeignKey.stateChanged.connect(self.setForeignKeyState)
        self.nameTable.currentIndexChanged.connect(self.updateAttributes)

    def setPrimeryKeyState(self):
        if self.setPrimeryKey.isChecked():
            self.setNull.setChecked(False)
            self.setNull.setEnabled(False)
            self.setUnique.setChecked(False)
            self.setUnique.setEnabled(False)
            self.setForeignKey.setChecked(False)
            self.setForeignKey.setEnabled(False)
        else:
            self.setNull.setChecked(False)
            self.setNull.setEnabled(True)
            self.setUnique.setChecked(False)
            self.setUnique.setEnabled(True)
            self.setForeignKey.setChecked(False)
            self.setForeignKey.setEnabled(True)

    def setForeignKeyState(self):
        if self.setForeignKey.isChecked():
            tables = lists_tables()
            self.nameTable.clear()
            if tables:
                self.nameTable.addItems(["Не выбрано"] + tables)
                self.nameTable.setEnabled(True)
            else:
                self.nameTable.addItem("Нет доступных таблиц")
                self.nameTable.setEnabled(False)

            # показываем виджеты
            self.nameTable.show()
            self.nameAttribute.show()
        else:
            self.nameTable.hide()
            self.nameAttribute.hide()

    def updateAttributes(self):
        table_name = self.nameTable.currentText()
        if table_name in ("Не выбрано", "Нет доступных таблиц", ""):
            self.nameAttribute.clear()
            return

        attributes = list_attributes(schema, table_name)
        self.nameAttribute.clear()
        self.nameAttribute.addItems(attributes)
class CreateTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.createTableDialog()

    def createTableDialog(self):
        # Диалог для ввода текста
        table_name, ok = QtWidgets.QInputDialog.getText(
            self.parent,
            "Создание таблицы",
            "Введите имя таблицы:"
        )

        if ok and table_name:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f'CREATE TABLE {schema}.{table_name} ();')
                connection.commit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.parent, "Ошибка",
                                               f"Ошибка при работе с PostgreSQL:\n{e}")
                logger.error(f"Ошибка при работе с PostgreSQL:\n{e}")
                return
            QtWidgets.QMessageBox.information(self.parent, "Успех",
                                              f"Таблица '{table_name}' создана!")
            logger.info(f" PostgreSQL: Таблица {table_name} создана")
        else:
            QtWidgets.QMessageBox.warning(self.parent, "Отмена",
                                          "Создание таблицы отменено.")
class CreateSchema(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить схему")
        self.resize(350, 150)
        self.listUser = QtWidgets.QComboBox(self)
        users = self.list_user()
        if users:
            self.listUser.addItems(users)
        else:
            self.listUser.addItem("Нет пользователей")
            self.listUser.setEnabled(False)
        # Формовый layout (подпись + поле в строку)
        self.layout = QtWidgets.QFormLayout(self)
        self.nameSchema = QtWidgets.QLineEdit(self)
        self.nameUser = QtWidgets.QLineEdit(self)
        self.nameUser.setPlaceholderText("Введите имя пользователя:")
        self.forUser = QtWidgets.QCheckBox("Для пользователя", self)
        self.layout.addRow("Наименование схемы:", self.nameSchema)
        self.layout.addRow(self.forUser)
        self.layout.addRow(self.nameUser)
        self.layout.addRow(self.listUser)
        self.nameUser.hide()
        self.listUser.hide()
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Отмена")
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.ok_button)
        self.btn_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.btn_layout)
        self.ok_button.clicked.connect(self.sendRequest)
        self.cancel_button.clicked.connect(self.reject)
        self.forUser.stateChanged.connect(self.setForUser)
        self.listUser.currentTextChanged.connect(self.setUserName)

    def setForUser(self):
        if self.forUser.isChecked():
            self.nameUser.show()
            self.nameSchema.setEnabled(False)
            self.listUser.show()
        else:
            self.nameUser.hide()
            self.nameSchema.setEnabled(True)
            self.listUser.hide()

    def setUserName(self, text):
        if text != 'Не выбрано' and text != 'Нет пользователей':
            self.nameUser.setText(text)
            self.nameUser.setEnabled(False)
        else:
            self.nameUser.clear()
            self.nameUser.setEnabled(True)
    def sendRequest(self):
        try:
            with connection.cursor() as cursor:
                if self.forUser.isChecked():
                    # создаём схему для конкретного пользователя
                    user = self.nameUser.text()  # значение по умолчанию
                    cursor.execute(
                        f'CREATE SCHEMA "{user}" AUTHORIZATION "{user}";'
                    )
                    QtWidgets.QMessageBox.information(
                        self, "Успех",
                        f"Схема '{user}' создана!"
                    )
                else:
                    # создаём схему без указания владельца
                    cursor.execute(
                        f'CREATE SCHEMA "{self.nameSchema.text()}";'
                    )
                    QtWidgets.QMessageBox.information(
                        self, "Успех",
                        f"Схема '{self.nameSchema.text()}' создана!"
                    )

            connection.commit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Ошибка при работе с PostgreSQL:\n{e}"
            )

    def list_user(self):
        list_user = ['Не выбрано']
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
SELECT usename AS role_name,
 CASE
  WHEN usesuper AND usecreatedb THEN
    CAST('superuser, create database' AS pg_catalog.text)
  WHEN usesuper THEN
    CAST('superuser' AS pg_catalog.text)
  WHEN usecreatedb THEN
    CAST('create database' AS pg_catalog.text)
  ELSE
    CAST('' AS pg_catalog.text)
 END role_attributes
FROM pg_catalog.pg_user
ORDER BY role_name desc;
                """)
                users = cursor.fetchall()
                for u in users:
                    list_user.append(u[0])
        except Exception as e:
            print("Ошибка:", e)
        return list_user
class CreateData(QtWidgets.QDialog):
    pass
class DropTable(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Удалить таблицу")
        self.resize(350, 150)
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addRow ("Рабочая схема", QtWidgets.QLabel(schema))
        self.nameTable = QtWidgets.QComboBox(self)
        self.layout.addRow("Имя таблицы", self.nameTable)
        # Кнопки
        self.ok_button = QtWidgets.QPushButton("Выбрать")
        self.cancel_button = QtWidgets.QPushButton("Отмена")
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        self.layout.addRow(btn_layout)
        #Сигналы
        self.ok_button.clicked.connect(self.windowConfirmation)
        self.cancel_button.clicked.connect(self.reject)
        tables = lists_tables()

        if tables:
            self.nameTable.addItems(tables)
        else:
            self.nameTable.addItem("Нет доступных таблиц")
            self.nameTable.setEnabled(False)
            self.ok_button.setEnabled(False)

    def windowConfirmation(self):
        table_name = self.nameTable.currentText()
        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить таблицу {table_name}? Возврат таблицы будет невозможным, а удаление может повлиять на работу базы данных",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE {schema}.{table_name} CASCADE;")
                connection.commit()
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    f"Таблица '{table_name}' успешно удалена."
                )
                self.accept()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить таблицу:\n{e}"
                )
class CreateUser(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить пользователя")
        self.resize(350, 150)
        self.layout = QtWidgets.QFormLayout(self)
        # Объявление объектов
        self.nameNewUser = QtWidgets.QLineEdit(self)
        self.textPasswordUser = QtWidgets.QLineEdit(self)
        self.login = QtWidgets.QCheckBox("LOGIN", self)
        self.passwordUser = QtWidgets.QCheckBox("C паролем",self)
        self.superUser = QtWidgets.QCheckBox("SUPERUSER", self)
        self.createDB = QtWidgets.QCheckBox("CREATEDB", self)
        self.createROLE = QtWidgets.QCheckBox("CREATE ROLE", self)
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Отмена")
        # Добавление кнопок на главный экран
        self.layout.addRow("Имя пользователя:", self.nameNewUser)
        self.layout.addRow(self.textPasswordUser)
        self.layout.addRow(self.passwordUser)
        self.layout.addRow(self.login)
        self.layout.addRow(self.superUser)
        self.layout.addRow(self.createDB)
        self.layout.addRow(self.createROLE)
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.ok_button)
        self.btn_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.btn_layout)
        # Дополнительные настройки
        self.nameNewUser.setPlaceholderText("Введите имя пользователя:")
        self.textPasswordUser.setPlaceholderText("Введите пароль:")
        self.textPasswordUser.hide()
        # Сигналы кнопок
        self.passwordUser.stateChanged.connect(self.setPassword)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.sendRequest)

    def setPassword(self):
        if self.passwordUser.isChecked():
            self.textPasswordUser.show()
        else:
            self.textPasswordUser.hide()
            self.textPasswordUser.clear()

    def get_privileges(self):
        privileges = []
        if self.superUser.isChecked():
            privileges.append("SUPERUSER")
        if self.createDB.isChecked():
            privileges.append("CREATEDB")
        if self.createROLE.isChecked():
            privileges.append("CREATEROLE")
        if self.login.isChecked():
            privileges.append("LOGIN")

        return " ".join(privileges) if privileges else ""

    def sendRequest(self):
        username = self.nameNewUser.text().strip()
        password = self.textPasswordUser.text().strip()
        privileges = self.get_privileges()
        try:
            if not username:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Имя пользователя не может быть пустым.")
                return

            with connection.cursor() as cursor:
                if password:
                    query = f"CREATE USER \"{username}\" WITH PASSWORD %s {privileges};"
                    cursor.execute(query, (password,))
                    connection.commit()
                else:
                    query = f"CREATE USER {username} WITH {privileges};"
                    cursor.execute(query)

            QtWidgets.QMessageBox.information(self, "Успех", f"Пользователь '{username}' успешно создан.")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось создать пользователя:\n{e}")
            print("Ошибка:", e)

