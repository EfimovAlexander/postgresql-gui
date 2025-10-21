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
        self.resize(1000, 700)

        # МОДЕЛЬ
        self.selected_columns = []          # для SELECT
        self.where_conditions = []          # [{'logic': 'AND'|'OR', 'col_expr': 'col', 'op': '=', 'value_sql': '...'}]
        self.groupby_columns = []           # ['col1', 'col2', ...]
        self.having_conditions = []         # как where, но col_expr может быть FUNC(col) или COUNT(*)
        self.orderby_items = []             # [{'col': 'col', 'dir': 'ASC'|'DESC'}]
        self._updating_columns = False      # технический флаг при обновлении списков

        # КОРНЕВОЙ ЛЕЙАУТ
        root_layout = QtWidgets.QVBoxLayout(self)

        # ФОРМА ВЕРХНЕЙ ПАНЕЛИ
        form = QtWidgets.QFormLayout()
        form.addRow("Рабочая схема:", QtWidgets.QLabel(schema))

        # ТАБЛИЦА
        self.nameTable = QtWidgets.QComboBox(self)
        tables = list_tables()
        if tables:
            self.nameTable.addItems(tables)
        else:
            self.nameTable.addItem("Нет доступных таблиц")
        form.addRow("Таблица:", self.nameTable)

        # SELECT: выбор колонок
        self.nameColumns = QtWidgets.QComboBox()
        form.addRow("Столбцы для SELECT:", self.nameColumns)

        # Контейнер для отображения выбранных колонок (SELECT)
        self.selected_list_layout = QtWidgets.QVBoxLayout()
        self.selected_list_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_list_layout.setSpacing(4)
        selected_container = QtWidgets.QWidget(self)
        selected_container.setLayout(self.selected_list_layout)
        form.addRow("Выбранные столбцы:", selected_container)

        # WHERE: конструктор условий
        where_block = self._build_where_block()
        form.addRow("WHERE:", where_block)

        # GROUP BY: выбор колонок
        groupby_block = self._build_groupby_block()
        form.addRow("GROUP BY:", groupby_block)

        # HAVING: конструктор условий с агрегатами
        having_block = self._build_having_block()
        form.addRow("HAVING:", having_block)

        # ORDER BY: выбор колонок и направления
        orderby_block = self._build_orderby_block()
        form.addRow("ORDER BY:", orderby_block)

        root_layout.addLayout(form)

        # Кнопка выполнения
        self.run_button = QtWidgets.QPushButton("Выполнить запрос")
        root_layout.addWidget(self.run_button)

        # Таблица результата
        self.result_view = QtWidgets.QTableWidget()
        root_layout.addWidget(self.result_view)

        # СИГНАЛЫ
        self.run_button.clicked.connect(self.runQuery)
        self.nameTable.currentTextChanged.connect(self.updateColumn)  # обновляет все выпадающие по колонкам
        self.nameColumns.currentTextChanged.connect(self.addColumn)    # подтверждение и добавление в SELECT

        # Инициализация списков колонок для выбранной таблицы
        self.updateColumn()

    # -------------------------- UI BUILDERS --------------------------

    def _build_where_block(self):
        block = QtWidgets.QWidget(self)
        v = QtWidgets.QVBoxLayout(block)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        # строка выбора колонки
        row_top = QtWidgets.QHBoxLayout()
        self.where_col_combo = QtWidgets.QComboBox(block)
        row_top.addWidget(QtWidgets.QLabel("Колонка:"))
        row_top.addWidget(self.where_col_combo, 1)

        # группа операторов
        row_ops = QtWidgets.QHBoxLayout()
        row_ops.addWidget(QtWidgets.QLabel("Оператор:"))
        self.where_op_group = QtWidgets.QButtonGroup(block)
        self.where_op_group.setExclusive(True)
        self.where_ops_buttons = []
        for text in ["=", "<>", ">=", "<=", ">", "<"]:
            btn = QtWidgets.QPushButton(text, block)
            btn.setCheckable(True)
            self.where_op_group.addButton(btn)
            self.where_ops_buttons.append(btn)
            row_ops.addWidget(btn)
        # по умолчанию "="
        self.where_ops_buttons[0].setChecked(True)

        # значение и логика AND/OR
        row_val = QtWidgets.QHBoxLayout()
        self.where_value_edit = QtWidgets.QLineEdit(block)
        self.where_value_edit.setPlaceholderText("Значение (число/NULL/TRUE/FALSE или текст)")
        self.where_logic_combo = QtWidgets.QComboBox(block)
        self.where_logic_combo.addItems(["AND", "OR"])
        self.where_add_btn = QtWidgets.QPushButton("Добавить условие", block)
        row_val.addWidget(QtWidgets.QLabel("Значение:"))
        row_val.addWidget(self.where_value_edit, 1)
        row_val.addWidget(QtWidgets.QLabel("Связка:"))
        row_val.addWidget(self.where_logic_combo)
        row_val.addWidget(self.where_add_btn)

        # список добавленных условий
        self.where_list_layout = QtWidgets.QVBoxLayout()
        self.where_list_layout.setContentsMargins(0, 0, 0, 0)
        self.where_list_layout.setSpacing(4)
        where_list_container = QtWidgets.QWidget(block)
        where_list_container.setLayout(self.where_list_layout)

        v.addLayout(row_top)
        v.addLayout(row_ops)
        v.addLayout(row_val)
        v.addWidget(where_list_container)

        self.where_add_btn.clicked.connect(self._on_add_where_condition)

        return block

    def _build_groupby_block(self):
        block = QtWidgets.QWidget(self)
        v = QtWidgets.QVBoxLayout(block)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        row = QtWidgets.QHBoxLayout()
        self.groupby_col_combo = QtWidgets.QComboBox(block)
        self.groupby_add_btn = QtWidgets.QPushButton("Добавить", block)
        row.addWidget(QtWidgets.QLabel("Колонка:"))
        row.addWidget(self.groupby_col_combo, 1)
        row.addWidget(self.groupby_add_btn)

        self.groupby_list_layout = QtWidgets.QVBoxLayout()
        self.groupby_list_layout.setContentsMargins(0, 0, 0, 0)
        self.groupby_list_layout.setSpacing(4)
        container = QtWidgets.QWidget(block)
        container.setLayout(self.groupby_list_layout)

        v.addLayout(row)
        v.addWidget(container)

        self.groupby_add_btn.clicked.connect(self._on_add_groupby)

        return block

    def _build_having_block(self):
        block = QtWidgets.QWidget(self)
        v = QtWidgets.QVBoxLayout(block)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        # Выбор выражения: агрегат + колонка
        row_expr = QtWidgets.QHBoxLayout()
        self.having_func_combo = QtWidgets.QComboBox(block)
        # Возможные агрегаты; предусмотрим COUNT(*)
        self.having_func_combo.addItems(["", "COUNT", "COUNT(*)", "SUM", "AVG", "MIN", "MAX"])
        self.having_col_combo = QtWidgets.QComboBox(block)
        row_expr.addWidget(QtWidgets.QLabel("Функция:"))
        row_expr.addWidget(self.having_func_combo)
        row_expr.addWidget(QtWidgets.QLabel("Колонка:"))
        row_expr.addWidget(self.having_col_combo, 1)

        # Операторы
        row_ops = QtWidgets.QHBoxLayout()
        row_ops.addWidget(QtWidgets.QLabel("Оператор:"))
        self.having_op_group = QtWidgets.QButtonGroup(block)
        self.having_op_group.setExclusive(True)
        self.having_ops_buttons = []
        for text in ["=", "<>", ">=", "<=", ">", "<"]:
            btn = QtWidgets.QPushButton(text, block)
            btn.setCheckable(True)
            self.having_op_group.addButton(btn)
            self.having_ops_buttons.append(btn)
            row_ops.addWidget(btn)
        self.having_ops_buttons[0].setChecked(True)

        # Значение + логика
        row_val = QtWidgets.QHBoxLayout()
        self.having_value_edit = QtWidgets.QLineEdit(block)
        self.having_value_edit.setPlaceholderText("Значение (число/NULL/TRUE/FALSE или текст)")
        self.having_logic_combo = QtWidgets.QComboBox(block)
        self.having_logic_combo.addItems(["AND", "OR"])
        self.having_add_btn = QtWidgets.QPushButton("Добавить условие", block)
        row_val.addWidget(QtWidgets.QLabel("Значение:"))
        row_val.addWidget(self.having_value_edit, 1)
        row_val.addWidget(QtWidgets.QLabel("Связка:"))
        row_val.addWidget(self.having_logic_combo)
        row_val.addWidget(self.having_add_btn)

        # Список условий HAVING
        self.having_list_layout = QtWidgets.QVBoxLayout()
        self.having_list_layout.setContentsMargins(0, 0, 0, 0)
        self.having_list_layout.setSpacing(4)
        having_list_container = QtWidgets.QWidget(block)
        having_list_container.setLayout(self.having_list_layout)

        v.addLayout(row_expr)
        v.addLayout(row_ops)
        v.addLayout(row_val)
        v.addWidget(having_list_container)

        self.having_add_btn.clicked.connect(self._on_add_having_condition)

        return block

    def _build_orderby_block(self):
        block = QtWidgets.QWidget(self)
        v = QtWidgets.QVBoxLayout(block)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        row = QtWidgets.QHBoxLayout()
        self.orderby_col_combo = QtWidgets.QComboBox(block)
        self.orderby_dir_combo = QtWidgets.QComboBox(block)
        self.orderby_dir_combo.addItems(["ASC", "DESC"])
        self.orderby_add_btn = QtWidgets.QPushButton("Добавить", block)
        row.addWidget(QtWidgets.QLabel("Колонка:"))
        row.addWidget(self.orderby_col_combo, 1)
        row.addWidget(QtWidgets.QLabel("Направление:"))
        row.addWidget(self.orderby_dir_combo)
        row.addWidget(self.orderby_add_btn)

        self.orderby_list_layout = QtWidgets.QVBoxLayout()
        self.orderby_list_layout.setContentsMargins(0, 0, 0, 0)
        self.orderby_list_layout.setSpacing(4)
        container = QtWidgets.QWidget(block)
        container.setLayout(self.orderby_list_layout)

        v.addLayout(row)
        v.addWidget(container)

        self.orderby_add_btn.clicked.connect(self._on_add_orderby)

        return block

    # -------------------------- ДЕЙСТВИЯ SELECT --------------------------

    def addColumn(self):
        # игнорируем событие, если сейчас идёт программное заполнение комбобокса
        if getattr(self, "_updating_columns", False):
            return

        col = self.nameColumns.currentText().strip()
        if not col:
            return

        # подтверждение выбора
        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение",
            f"Добавить столбец «{col}» в выборку?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # проверка на дубликат
        if col in self.selected_columns:
            QtWidgets.QMessageBox.information(self, "Уже добавлено",
                                              f"Столбец «{col}» уже в списке.")
            return

        # добавляем в список
        self.selected_columns.append(col)

        # создаём виджет-строку: [QLabel(col)] [stretch] [Удалить]
        row_widget = QtWidgets.QWidget(self)
        h = QtWidgets.QHBoxLayout(row_widget)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        lbl = QtWidgets.QLabel(col, row_widget)
        btn = QtWidgets.QPushButton("Удалить", row_widget)
        btn.setToolTip(f"Удалить столбец «{col}»")

        # обработчик удаления конкретно этой строки
        def remove_this_row():
            if col in self.selected_columns:
                self.selected_columns.remove(col)
            row_widget.setParent(None)
            row_widget.deleteLater()

        btn.clicked.connect(remove_this_row)

        h.addWidget(lbl)
        h.addStretch(1)
        h.addWidget(btn)

        self.selected_list_layout.addWidget(row_widget)

    # -------------------------- ДЕЙСТВИЯ WHERE --------------------------

    def _on_add_where_condition(self):
        col = self.where_col_combo.currentText().strip()
        if not col:
            return

        op_btn = self._checked_button(self.where_op_group)
        op = op_btn.text() if op_btn else "="
        value_raw = self.where_value_edit.text()
        if value_raw.strip() == "":
            QtWidgets.QMessageBox.information(self, "Пустое значение", "Введите значение для условия WHERE.")
            return

        value_sql = self._to_sql_literal(value_raw)
        logic = self.where_logic_combo.currentText()

        item = {
            "logic": logic,
            "col_expr": col,
            "op": op,
            "value_sql": value_sql,
        }
        self.where_conditions.append(item)

        text = f"{logic if len(self.where_conditions) > 1 else ''} {col} {op} {value_sql}".strip()
        self._add_list_row(self.where_list_layout, text, lambda: self._remove_condition(self.where_conditions, item))

        # очистка поля значения для удобства
        self.where_value_edit.clear()

    # -------------------------- ДЕЙСТВИЯ GROUP BY --------------------------

    def _on_add_groupby(self):
        col = self.groupby_col_combo.currentText().strip()
        if not col:
            return
        if col in self.groupby_columns:
            QtWidgets.QMessageBox.information(self, "Уже добавлено", f"Колонка «{col}» уже в GROUP BY.")
            return

        self.groupby_columns.append(col)
        self._add_list_row(self.groupby_list_layout, col, lambda: self._remove_groupby(col))

    # -------------------------- ДЕЙСТВИЯ HAVING --------------------------

    def _on_add_having_condition(self):
        func = self.having_func_combo.currentText()
        col = self.having_col_combo.currentText().strip()

        # формируем выражение
        if func == "COUNT(*)":
            col_expr = "COUNT(*)"
        elif func:
            if not col:
                QtWidgets.QMessageBox.information(self, "Не выбрана колонка", "Выберите колонку для агрегатной функции.")
                return
            col_expr = f"{func}({col})"
        else:
            if not col:
                QtWidgets.QMessageBox.information(self, "Не выбрана колонка", "Выберите колонку для HAVING.")
                return
            col_expr = col

        op_btn = self._checked_button(self.having_op_group)
        op = op_btn.text() if op_btn else "="
        value_raw = self.having_value_edit.text()
        if value_raw.strip() == "":
            QtWidgets.QMessageBox.information(self, "Пустое значение", "Введите значение для условия HAVING.")
            return
        value_sql = self._to_sql_literal(value_raw)
        logic = self.having_logic_combo.currentText()

        item = {
            "logic": logic,
            "col_expr": col_expr,
            "op": op,
            "value_sql": value_sql,
        }
        self.having_conditions.append(item)

        text = f"{logic if len(self.having_conditions) > 1 else ''} {col_expr} {op} {value_sql}".strip()
        self._add_list_row(self.having_list_layout, text, lambda: self._remove_condition(self.having_conditions, item))

        self.having_value_edit.clear()

    # -------------------------- ДЕЙСТВИЯ ORDER BY --------------------------

    def _on_add_orderby(self):
        col = self.orderby_col_combo.currentText().strip()
        if not col:
            return
        direction = self.orderby_dir_combo.currentText()
        item = {"col": col, "dir": direction}

        # проверим на дубликат одинаковой колонки с тем же направлением
        if any(x["col"] == item["col"] and x["dir"] == item["dir"] for x in self.orderby_items):
            QtWidgets.QMessageBox.information(self, "Уже добавлено", f"{col} {direction} уже в ORDER BY.")
            return

        self.orderby_items.append(item)
        text = f"{col} {direction}"
        self._add_list_row(self.orderby_list_layout, text, lambda: self._remove_orderby(item))

    # -------------------------- ВСПОМОГАТЕЛЬНЫЕ UI-МЕТОДЫ --------------------------

    def _add_list_row(self, layout: QtWidgets.QVBoxLayout, text: str, on_remove):
        row_widget = QtWidgets.QWidget(self)
        h = QtWidgets.QHBoxLayout(row_widget)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        lbl = QtWidgets.QLabel(text, row_widget)
        btn = QtWidgets.QPushButton("Удалить", row_widget)
        btn.clicked.connect(lambda: self._remove_row(row_widget, on_remove))

        h.addWidget(lbl)
        h.addStretch(1)
        h.addWidget(btn)

        layout.addWidget(row_widget)

    def _remove_row(self, row_widget: QtWidgets.QWidget, on_remove):
        # сначала логическая модель
        try:
            on_remove()
        finally:
            # затем UI
            row_widget.setParent(None)
            row_widget.deleteLater()

    def _remove_condition(self, container_list: list, item: dict):
        if item in container_list:
            container_list.remove(item)

    def _remove_groupby(self, col: str):
        try:
            self.groupby_columns.remove(col)
        except ValueError:
            pass

    def _remove_orderby(self, item: dict):
        try:
            self.orderby_items.remove(item)
        except ValueError:
            pass

    def _checked_button(self, group: QtWidgets.QButtonGroup):
        for btn in group.buttons():
            if btn.isChecked():
                return btn
        return None

    def _to_sql_literal(self, value: str) -> str:
        s = value.strip()
        u = s.upper()
        if u == "NULL":
            return "NULL"
        if u in ("TRUE", "FALSE"):
            return u
        # число (целое/вещественное)
        try:
            int(s)
            return s
        except ValueError:
            pass
        try:
            float(s)
            return s
        except ValueError:
            pass
        # строка — экранируем одинарные кавычки
        s_escaped = s.replace("'", "''")
        return f"'{s_escaped}'"

    def _clear_layout(self, layout: QtWidgets.QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    # -------------------------- ОБНОВЛЕНИЕ КОЛОНОК ПРИ СМЕНЕ ТАБЛИЦЫ --------------------------

    def updateColumn(self):
        table_name = self.nameTable.currentText()
        self._updating_columns = True
        try:
            # очистим все модельные списки и UI, т.к. колонок может не быть в новой таблице
            self.selected_columns.clear()
            self.where_conditions.clear()
            self.groupby_columns.clear()
            self.having_conditions.clear()
            self.orderby_items.clear()
            self._clear_layout(self.selected_list_layout)
            self._clear_layout(self.where_list_layout)
            self._clear_layout(self.groupby_list_layout)
            self._clear_layout(self.having_list_layout)
            self._clear_layout(self.orderby_list_layout)

            # обновим все выпадающие списки по колонкам
            if table_name in ("Не выбрано", "Нет доступных таблиц", "", None):
                self.nameColumns.clear()
                self.where_col_combo.clear()
                self.groupby_col_combo.clear()
                self.having_col_combo.clear()
                self.orderby_col_combo.clear()
                return

            columns = list_column(table_name) or []

            def refill(cb: QtWidgets.QComboBox, items):
                cb.blockSignals(True)
                cb.clear()
                if items:
                    cb.addItems(items)
                cb.blockSignals(False)

            refill(self.nameColumns, columns)
            refill(self.where_col_combo, columns)
            refill(self.groupby_col_combo, columns)
            refill(self.having_col_combo, columns)
            refill(self.orderby_col_combo, columns)
        finally:
            self._updating_columns = False

    # -------------------------- ВЫПОЛНЕНИЕ ЗАПРОСА --------------------------

    def runQuery(self):
        query = self.buildQuery()
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
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"{e}\n\nSQL:\n{query}")

    def buildQuery(self):
        table = self.nameTable.currentText().strip()
        if not table or table in ("Не выбрано", "Нет доступных таблиц"):
            raise ValueError("Не выбрана таблица.")

        columns = ", ".join(self.selected_columns) if self.selected_columns else "*"

        query = f"SELECT {columns} FROM {schema}.{table}"

        # WHERE
        if self.where_conditions:
            where_sql = self._conditions_to_sql(self.where_conditions)
            if where_sql:
                query += f" WHERE {where_sql}"

        # GROUP BY
        if self.groupby_columns:
            query += " GROUP BY " + ", ".join(self.groupby_columns)

        # HAVING
        if self.having_conditions:
            having_sql = self._conditions_to_sql(self.having_conditions)
            if having_sql:
                query += f" HAVING {having_sql}"

        # ORDER BY
        if self.orderby_items:
            parts = [f"{x['col']} {x['dir']}" for x in self.orderby_items]
            query += " ORDER BY " + ", ".join(parts)

        return query + ";"

    def _conditions_to_sql(self, conds: list) -> str:
        if not conds:
            return ""
        parts = []
        for i, c in enumerate(conds):
            seg = f"{c['col_expr']} {c['op']} {c['value_sql']}"
            if i == 0:
                parts.append(seg)
            else:
                parts.append(f"{c['logic']} {seg}")
        return " ".join(parts)