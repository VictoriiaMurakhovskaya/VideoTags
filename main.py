from db_api import dbAPI
from PyQt6 import QtWidgets as qw
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQueryModel
from gui.main_window import Ui_MainWindow
from gui.locals import Ui_Dialog as local_dialog
from gui.net import Ui_Dialog as network_dialog
from gui.lst_dialog import Ui_Dialog as lst_dlg
from PyQt6.QtCore import QDir
import sys
from PyQt6.QtCore import Qt
import requests as rq
import pandas as pd
import traceback as tb


class TheWindow(qw.QMainWindow):
    """
    Класс графического интерфейса программы
    """

    def __init__(self):
        """
        Конструктор основного окна программы
        """
        # инициализация основного окна
        super(TheWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = dbAPI()

        # инициализация БД приложения (работа с PyQt)
        self.qtdb = QSqlDatabase.addDatabase('QSQLITE')
        self.qtdb.setDatabaseName('assets/data.db')
        if not self.qtdb.open():
            print(self.qtdb.lastError().text())
            sys.exit(1)

        self.ui.action.triggered.connect(self.on_exit)
        self.ui.action_2.triggered.connect(self.locals)
        self.ui.action_3.triggered.connect(self.netsources)

        # инициализация таблицы сетевых файлов
        self.netmodel = QSqlTableModel(self)
        self.netmodel.setEditStrategy(QSqlTableModel.EditStrategy.OnRowChange)
        self.netmodel.setTable('nets')
        self.netmodel.select()

        self.netproxy = QtCore.QSortFilterProxyModel()
        self.netproxy.setSourceModel(self.netmodel)

        self.ui.tableView.setModel(self.netproxy)
        self.ui.tableView.setEditTriggers(qw.QAbstractItemView.EditTriggers.NoEditTriggers)
        self.ui.tableView.setSortingEnabled(True)

        header = self.ui.tableView.horizontalHeader()
        header.moveSection(6, 2)
        header.moveSection(4, 3)
        header.setSectionResizeMode(0, qw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, qw.QHeaderView.ResizeMode.ResizeToContents)

        # инициализация таблицы локальных файлов
        self.localmodel = QSqlTableModel(self)
        self.localmodel.setEditStrategy(QSqlTableModel.EditStrategy.OnRowChange)
        self.localmodel.setTable('lfiles')
        self.localmodel.select()

        self.localproxy = QtCore.QSortFilterProxyModel()
        self.localproxy.setSourceModel(self.localmodel)

        self.ui.tableView_2.setModel(self.localproxy)

        header = self.ui.tableView_2.horizontalHeader()
        header.moveSection(3, 1)
        header.moveSection(6, 4)
        header.setSectionResizeMode(0, qw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, qw.QHeaderView.ResizeMode.ResizeToContents)

        self.ui.pushButton_2.clicked.connect(self.delete_row)
        self.ui.pushButton_3.clicked.connect(self.collect)
        self.ui.pushButton_4.clicked.connect(self.generate_playlist)
        self.ui.pushButton_5.clicked.connect(self.export_list)
        self.ui.pushButton.clicked.connect(self.filter_view)
        self.ui.pushButton_6.clicked.connect(self.reset)

        self.ui.tableView.show()

    def reset(self):
        for i in range(self.localproxy.rowCount()):
            self.ui.tableView_2.showRow(i)

        for i in range(self.netproxy.rowCount()):
            self.ui.tableView.showRow(i)


    def locals(self):
        lcls = TheLocalSource(self)
        lcls.show()

    def netsources(self):
        nets = TheNetworkSource(self)
        nets.show()

    def on_exit(self):
        try:
            self.qtbd.close()
        except:
            pass
        sys.exit(0)

    def delete_row(self):
        if self.ui.tabWidget.currentIndex() == 0:
            table = self.ui.tableView_2
            model = self.locamodel
        else:
            table = self.ui.tableView
            model = self.netmodel

        model.removeRow(table.currentIndex().row())
        model.select()

    def collect(self):
        tagList = TagList(self)
        tagList.show()

    def generate_playlist(self):
        print('Generate playlist')

    def export_list(self):
        print('Export list')

    def filter_view(self):
        print('Filtered')

    @QtCore.pyqtSlot(list)
    def select_by_tags(self, lst):
        if not lst:
            return
        if len(lst) == 0:
            return
        rows, tags_lst = [], []
        if self.ui.tabWidget.currentIndex() == 0:
            model = self.localmodel
            view = self.ui.tableView_2
            for row in range(model.rowCount()):
                index = model.index(row, 6)
                tags = model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)
                tags = tags.split(';')
                for t in tags:
                    rows.append(row)
                    tags_lst.append(t)
        else:
            model = self.netmodel
            view = self.ui.tableView
            for row in range(model.rowCount()):
                index = model.index(row, 6)
                tags = model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)
                tags = tags.split(',')
                for t in tags:
                    rows.append(row)
                    tags_lst.append(t)
        df = pd.DataFrame({'tag': tags_lst, 'rown': rows})
        df = df.loc[df.tag.isin(lst)].copy()

        rows = list(set(df['rown']))

        for row in range(model.rowCount()):
            if row not in rows:
                view.hideRow(row)
        view.show()


class TagList(qw.QDialog):
    on_close = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        qw.QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.ui = lst_dlg()
        self.ui.setupUi(self)

        self.ui.toolButton.clicked.connect(self.add_row)
        self.ui.toolButton_2.clicked.connect(self.delete_row)

        self.lst = []

        self.on_close.connect(self.parent.select_by_tags)

    def add_row(self):
        text = ''
        item = qw.QListWidgetItem(text)
        item.setFlags(QtCore.Qt.ItemFlags.ItemIsEnabled | QtCore.Qt.ItemFlags.ItemIsSelectable | QtCore.Qt.ItemFlags.ItemIsEditable)
        self.ui.listWidget.addItem(item)

    def delete_row(self):
        curItem = self.ui.listWidget.selectedItems()
        for item in curItem:
            pass

    def accept(self):
        self.lst = []
        for x in range(self.ui.listWidget.count()):
            self.lst.append(self.ui.listWidget.item(x).text())
        self.on_close.emit(self.lst)
        self.close()


class Query_Result(qw.QDialog):
    pass

class TheLocalSource(qw.QDialog):

    def __init__(self, parent=None):
        qw.QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.ui = local_dialog()
        self.ui.setupUi(self)

        self.filemodel = QFileSystemModel()
        self.filemodel.setRootPath(QtCore.QDir.rootPath())
        self.filemodel.setFilter(QDir.Filters.Dirs)

        self.ui.treeView.setModel(self.filemodel)

        self.basemodel = QSqlTableModel(self)
        self.basemodel.setEditStrategy(QSqlTableModel.EditStrategy.OnRowChange)
        self.basemodel.setTable('locals')
        self.basemodel.setHeaderData(0, Qt.Orientations.Horizontal, 'ID')
        self.basemodel.setHeaderData(1, Qt.Orientations.Horizontal, 'Шлях')
        self.basemodel.select()

        self.ui.tableView.setModel(self.basemodel)
        self.ui.tableView.setEditTriggers(qw.QAbstractItemView.EditTriggers.NoEditTriggers)
        self.ui.tableView.setColumnWidth(0, 20)
        self.ui.tableView.setColumnWidth(1, 200)
        self.ui.tableView.show()

        self.ui.toolButton_2.clicked.connect(self.add_item)
        self.ui.toolButton.clicked.connect(self.delete_item)

    def add_item(self):
        index = self.ui.treeView.selectedIndexes()[0]
        item = self.filemodel.filePath(index)
        r = self.basemodel.record()
        r.setValue('paths', item)
        self.basemodel.insertRecord(-1, r)
        self.basemodel.select()

    def delete_item(self):
        self.basemodel.removeRow(self.ui.tableView.currentIndex().row())
        self.basemodel.select()


class TheNetworkSource(qw.QDialog):

    def __init__(self, parent=None):
        qw.QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.ui = network_dialog()
        self.ui.setupUi(self)

        self.basemodel = QSqlTableModel()
        self.basemodel.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.basemodel.setTable('net_links')
        self.basemodel.setHeaderData(0, Qt.Orientations.Horizontal, 'ID')
        self.basemodel.setHeaderData(1, Qt.Orientations.Horizontal, 'Посилання')
        self.basemodel.select()

        self.ui.pushButton.clicked.connect(self.insert_row)
        self.ui.pushButton_2.clicked.connect(self.delete_row)

        self.ui.tableView.setModel(self.basemodel)
        self.ui.tableView.setColumnWidth(0, 20)
        self.ui.tableView.setColumnWidth(1, 320)
        self.ui.tableView.show()

    def insert_row(self):
        """
        Операция CREATE
        :return: None
        """
        try:
            count = self.model.rowCount()
            self.basemodel.insertRow(count)
        except:
            self.basemodel.insertRow(0)

    def delete_row(self):
        """
        Пометка на удаление записи
        Окончательное удаление происходит после UPDATE
        :return: None
        """
        self.basemodel.removeRow(self.ui.tableView.currentIndex().row())


if __name__ == '__main__':
    app = qw.QApplication([])
    application = TheWindow()
    application.show()
    sys.exit(app.exec())