from sys import exception

from PySide6 import QtWidgets
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
        logger.info('Список схем успешно загружен')
    except Exception as e:
        logger.exception('Ошибка при получении списка схем', e)
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка",
            "Не удалось получить список схем"
        )
    return list_schemas


def list_tables():
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
        logger.info(f'Cписок таблиц для схемы {schema} успешно получен')
    except Exception as e:
        logger.exception('Ошибка при получении списка таблиц', e)
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка",
            "Не удалось получить список таблиц"
        )
    return list_table


def list_attributes(schema, table):
    list_attributes = []
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
        logger.info(f'Список атрибутов для схемы {schema} таблицы {table} успешно получен')
    except Exception as e:
        logger.exception('Не удалось получить список атрибутов, %s', e)
        QtWidgets.QMessageBox.critical("Ошибка", "Не удалось получить список атрибутов")
    return list_attributes


def list_unique_attributes(schema, table):
    pass


def list_enum():
    list_enum = [
        'Не выбрано', 'BIGINT', 'BOOLEAN', 'CHAR', 'DATE', 'DATETIME',
        'DECIMAL', 'INTEGER', 'INTERVAL', 'SERIAL', 'SMALLINT',
        'TEXT', 'TIME', 'TIMESTAMP', 'VARCHAR'
    ]
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.typname
                FROM pg_type t
                JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                WHERE (t.typrelid = 0 OR (
                SELECT c.relkind = 'c'
                FROM pg_catalog.pg_class c
                WHERE c.oid = t.typrelid))
                AND NOT EXISTS (
                SELECT 1
                FROM pg_catalog.pg_type el
                WHERE el.oid = t.typelem
                AND el.typarray = t.oid)
                AND n.nspname = %s
                ORDER BY t.typname;
            """, (schema,))
            enum = cursor.fetchall()
        for e in enum:
            list_enum.append(e[0])
        logger.info('Список пользователских типов успешно загружен')
    except Exception as e:
        logger.exception('Ошибка при получении списка пользовательских типов',e)
    return list_enum

def list_column(table_name):
    list_columns = ["Не выбрано"]
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s
            AND table_name = %s
            ORDER BY ordinal_position;
            """, (schema, table_name))
            columns = cursor.fetchall()
            for c in columns:
                list_columns.append(c[0])
        logger.info(f'Cписок колонок для схемы {schema} таблицы {table_name} успешно получен')
    except Exception as e:
        logger.exception('Ошибка при получении списка колонок', e)
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка",
            "Не удалось получить список таблиц"
        )
    return list_columns


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
        self.layout = QtWidgets.QVBoxLayout(self) #  Распологает кнопки вертикально
        #  Объявление кнопок
        self.buttonSetSchema = QtWidgets.QPushButton("Выбрать схему")
        self.buttonCreateUser = QtWidgets.QPushButton("Добавить пользователя")
        self.buttonCreateSchema = QtWidgets.QPushButton("Создать схему")
        self.buttonCreateTable = QtWidgets.QPushButton("Создать таблицу")
        self.buttonCreateEnum = QtWidgets.QPushButton("Создать пользовательский тип данных")
        self.buttonCreateColumn = QtWidgets.QPushButton("Создать колонку в таблице")
        self.buttonCreateData = QtWidgets.QPushButton("Внести запись в таблицу")
        self.buttonDropTable = QtWidgets.QPushButton("Удалить таблицу")
        self.buttonDataViewer = QtWidgets.QPushButton("Вывести данные на экран")
        # Добавление кнопок на главный экран
        self.layout.addWidget(self.buttonSetSchema)
        self.layout.addWidget(self.buttonCreateUser)
        self.layout.addWidget(self.buttonCreateSchema)
        self.layout.addWidget(self.buttonCreateTable)
        self.layout.addWidget(self.buttonCreateEnum)
        self.layout.addWidget(self.buttonCreateColumn)
        self.layout.addWidget(self.buttonCreateEnum)
        self.layout.addWidget(self.buttonCreateData)
        self.layout.addWidget(self.buttonDropTable)
        self.layout.addWidget(self.buttonDataViewer)
        # Сигналы кнопок
        self.buttonCreateEnum.clicked.connect(lambda: self.openWindow(CreateEnum()))
        self.buttonCreateColumn.clicked.connect(lambda: self.openWindow(CreateColumn()))
        self.buttonSetSchema.clicked.connect(lambda: self.openWindow(SetSchema()))
        self.buttonCreateSchema.clicked.connect(lambda: self.openWindow(CreateSchema()))
        self.buttonCreateUser.clicked.connect(lambda: self.openWindow(CreateUser()))
        self.buttonCreateData.clicked.connect(lambda: self.openWindow(CreateData()))
        self.buttonDropTable.clicked.connect(lambda: self.openWindow(DropTable()))
        self.buttonCreateTable.clicked.connect(lambda: self.openWindow(CreateTable()))
        self.buttonDataViewer.clicked.connect(lambda: self.openWindow(DataViewer()))
        #self.setEnabledButton()
        #self.warning()

    def openWindow(self, window):
        window.exec()

    def warning(self):
        QtWidgets.QMessageBox.information(
            self, "Приветствие",
            "Перед началом работы выберите схему!"
        )


class CreateEnum(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить пользовательский тип данных")
        self.resize(350, 250)

        self.layout = QtWidgets.QFormLayout(self)

        # Поле для ввода количества значений ENUM
        self.nameEnum = QtWidgets.QLineEdit(self)
        self.nameEnum.setPlaceholderText("Введите наименование пользовательского типа")
        self.layout.addRow("Рабочая схема", QtWidgets.QLabel(schema))
        self.countEnum = QtWidgets.QLineEdit(self)
        self.countEnum.setPlaceholderText("Введите количество значений")
        self.layout.addRow("Наименование:", self.nameEnum)
        self.layout.addRow("Количество элементов:", self.countEnum)

        # Кнопка для создания полей
        self.acceptButton = QtWidgets.QPushButton("Создать поля")
        self.layout.addWidget(self.acceptButton)
        self.acceptButton.clicked.connect(self.addRowEnum)

        # Список для хранения полей
        self.enum_count = []

    def addRowEnum(self):
        # Очищаем старые поля, если они уже были добавлены
        for widget in self.enum_count:
            self.layout.removeRow(widget)
        self.enum_count.clear()

        # Проверка, что введено число
        try:
            count = int(self.countEnum.text())
            if count <= 0:
                raise ValueError
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите корректное положительное число!")
            return

        # Добавляем строки для ввода значений ENUM
        for i in range(count):
            line_edit = QtWidgets.QLineEdit(self)
            self.enum_count.append(line_edit)
            self.layout.addRow(f"Значение {i + 1}:", line_edit)

        # Добавляем кнопку подтверждения
        self.saveButton = QtWidgets.QPushButton("Сохранить ENUM")
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.saveEnumValues)

    def saveEnumValues(self):
        list_enum = []
        for e in self.enum_count:
            text = e.text().strip()
            if text:
                list_enum.append("'" + text + "'")
        list_enum = ",".join(list_enum)
        print(list_enum)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'CREATE TYPE {schema}.{self.nameEnum.text()} AS ENUM ({list_enum});'
                               )
                QtWidgets.QMessageBox.information(
                    self, "Успех",
                    f"Создан пользоваский тип {self.nameEnum.text()} со значениями {list_enum}!"

                )
                self.accept()
            logger.info(f'Создан ENUM {self.nameEnum.text()} со значениями {list_enum}')
        except Exception as e:
            logger.exception('Ошибка при создании пользовательского типа', e)
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Ошибка при создании пользовательского типа:\n{e}"
            )


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
        self.layout.addRow("Наименование схемы", self.nameSchema)
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

        enums = list_enum()
        if enums:
            self.dataType.addItems(enums)
        else:
            self.dataType.addItem("Нет доступных таблиц")

        self.layout.addRow("Тип данных", self.dataType)
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
            tables = list_tables()
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


class CreateTable(QtWidgets.QDialog):
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



from PySide6 import QtWidgets, QtCore
import psycopg2

class CreateData(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Внести данные в таблицу")
        self.resize(500, 350)

        self.layout = QtWidgets.QVBoxLayout(self)

        # --- Базовая форма ---
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Рабочая схема", QtWidgets.QLabel(schema))

        self.nameTable = QtWidgets.QComboBox(self)
        tables = list_tables()
        if tables:
            self.nameTable.addItems(tables)
        else:
            self.nameTable.addItem("Нет доступных таблиц")

        form_layout.addRow("Название таблицы", self.nameTable)

        self.nameAttributes = QtWidgets.QComboBox(self)
        form_layout.addRow("Название атрибута", self.nameAttributes)

        self.layout.addLayout(form_layout)

        # --- Контейнер для динамических строк ---
        self.fields_layout = QtWidgets.QFormLayout()
        self.layout.addLayout(self.fields_layout)

        # --- Кнопка сохранения ---
        self.saveButton = QtWidgets.QPushButton("Сохранить данные")
        self.layout.addWidget(self.saveButton)

        # --- Сигналы ---
        self.nameTable.currentIndexChanged.connect(self.updateAttributes)
        self.nameAttributes.currentIndexChanged.connect(self.addAttributeRow)
        self.saveButton.clicked.connect(self.saveDataToDB)

        # --- Хранение строк и типов ---
        self.attribute_rows = {}
        self.attribute_types = {}  # {атрибут: тип данных}

    def updateAttributes(self):
        """Обновляет список атрибутов и типы данных"""
        table_name = self.nameTable.currentText()
        self.nameAttributes.clear()
        self.attribute_types.clear()

        if table_name in ("Не выбрано", "Нет доступных таблиц", ""):
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                """, (schema, table_name))
                attrs = cursor.fetchall()
                for name, dtype in attrs:
                    self.attribute_types[name] = dtype
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось получить атрибуты:\n{e}")
            return

        self.nameAttributes.addItem("Выберите атрибут")
        self.nameAttributes.addItems(self.attribute_types.keys())

    def addAttributeRow(self):
        """Добавляет строку для выбранного атрибута"""
        attr_name = self.nameAttributes.currentText()
        if attr_name in ("Выберите атрибут", "", None):
            return
        if attr_name in self.attribute_rows:
            return

        label = QtWidgets.QLabel(f"{attr_name} ({self.attribute_types[attr_name]})")
        line_edit = QtWidgets.QLineEdit()
        remove_button = QtWidgets.QPushButton("🗑")
        remove_button.clicked.connect(lambda _, name=attr_name: self.removeAttributeRow(name))

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(line_edit)
        h_layout.addWidget(remove_button)
        self.fields_layout.addRow(label, h_layout)

        self.attribute_rows[attr_name] = (label, line_edit, remove_button)

    def removeAttributeRow(self, attr_name):
        """Удаляет строку"""
        if attr_name not in self.attribute_rows:
            return
        label, line_edit, remove_button = self.attribute_rows.pop(attr_name)
        self.fields_layout.removeWidget(label)
        self.fields_layout.removeWidget(line_edit)
        self.fields_layout.removeWidget(remove_button)
        label.deleteLater()
        line_edit.deleteLater()
        remove_button.deleteLater()

    def get_values(self):
        """Возвращает словарь {атрибут: значение}"""
        result = {}
        for name, (_, line_edit, _) in self.attribute_rows.items():
            value = line_edit.text().strip()
            if value:
                result[name] = value
        return result

    def validate_value(self, attr_name, value):
        """Проверяет соответствие типа данных"""
        expected_type = self.attribute_types.get(attr_name, "")
        if not value:
            return True  # пустое допустимо, если NOT NULL не проверяется

        try:
            if "int" in expected_type:
                int(value)
            elif "double" in expected_type or "numeric" in expected_type or "real" in expected_type:
                float(value)
            elif "bool" in expected_type:
                if value.lower() not in ("true", "false", "1", "0", "t", "f"):
                    raise ValueError
            elif "date" in expected_type:
                import datetime
                datetime.date.fromisoformat(value)
            # текстовые типы не требуют проверки
            return True
        except Exception:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка типа данных",
                f"Значение '{value}' не соответствует типу {expected_type.upper()} для атрибута '{attr_name}'."
            )
            return False

    def saveDataToDB(self):
        """Формирует INSERT INTO и выполняет запрос с проверкой типов"""
        table_name = self.nameTable.currentText()
        data = self.get_values()

        if not data:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Вы не ввели ни одного значения!")
            return

        # Проверка типов данных
        for attr, val in data.items():
            if not self.validate_value(attr, val):
                return  # если хотя бы одно поле не прошло проверку

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f'INSERT INTO "{schema}"."{table_name}" ({columns}) VALUES ({placeholders})'

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                connection.commit()
            QtWidgets.QMessageBox.information(self, "Успех", "Данные успешно добавлены!")
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось вставить данные:\n{e}")




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
        tables = list_tables()

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


class DataViewer(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конструктор SELECT-запроса")
        self.resize(800, 600)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        form.addRow("Рабочая схема", QtWidgets.QLabel(schema))
        # --- Панель параметров ---
        self.nameTable = QtWidgets.QComboBox(self)
        tables = list_tables()
        if tables:
            self.nameTable.addItems(tables)
        else:
            self.nameTable.addItem("Нет доступных таблиц")

        self.nameColumns = QtWidgets.QComboBox()
        self.where_edit = QtWidgets.QLineEdit()
        self.groupby_edit = QtWidgets.QLineEdit()
        self.having_edit = QtWidgets.QLineEdit()
        self.orderby_edit = QtWidgets.QLineEdit()

        form.addRow("Таблица:", self.nameTable)
        form.addRow("Столбцы:", self.nameColumns)
        form.addRow("WHERE:", self.where_edit)
        form.addRow("GROUP BY:", self.groupby_edit)
        form.addRow("HAVING:", self.having_edit)
        form.addRow("ORDER BY:", self.orderby_edit)

        layout.addLayout(form)

        self.run_button = QtWidgets.QPushButton("Выполнить запрос")
        layout.addWidget(self.run_button)

        # --- Таблица вывода ---
        self.result_view = QtWidgets.QTableWidget()
        layout.addWidget(self.result_view)

        self.run_button.clicked.connect(self.runQuery)
        self.nameTable.currentTextChanged.connect(self.updateColumn)

    def updateColumn(self):
        table_name = self.nameTable.currentText()
        if table_name in ("Не выбрано", "Нет доступных таблиц", ""):
            self.nameColumns.clear()
            return

        columns = list_column(table_name)
        self.nameColumns.clear()
        self.nameColumns.addItems(columns)
    def runQuery(self):
        query = self.buildQuery()
        print(query)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]

            # Отображаем результат
            self.result_view.setColumnCount(len(headers))
            self.result_view.setRowCount(len(rows))
            self.result_view.setHorizontalHeaderLabels(headers)

            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.result_view.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def buildQuery(self):
        table = self.nameTable.text().strip()
        columns = self.nameColumns.text().strip()
        where = self.where_edit.text().strip()
        group_by = self.groupby_edit.text().strip()
        having = self.having_edit.text().strip()
        order_by = self.orderby_edit.text().strip()

        query = f"SELECT {schema}.{columns or '*'} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if group_by:
            query += f" GROUP BY {group_by}"
        if having:
            query += f" HAVING {having}"
        if order_by:
            query += f" ORDER BY {order_by}"
        return query + ";"