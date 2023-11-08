import pandas as pd
import os

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QListWidgetItem, QFrame, QTreeWidgetItem, QHBoxLayout,
                             QTreeWidgetItemIterator, QTableWidgetItem, QWidget)
from qfluentwidgets import TableWidget, ToolTipFilter, FluentIcon, BodyLabel

from .gallery_interface import GalleryInterface
from .game_interface import gameInterface
from ..common.translator import Translator
from ..common.style_sheet import StyleSheet
from ..common.signal_bus import signalBus

class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName('frame')
        StyleSheet.VIEW_INTERFACE.apply(self)

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)

class TableFrame(Frame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.globalLayout = QHBoxLayout(self.view)
        self.table = TableWidget()

        # self.table.verticalHeader().hide()
        self.table.setColumnCount(12)
        self.table.setRowCount(100)
        self.table.setHorizontalHeaderLabels(["游戏名", "厂商名", "游戏评分", "状态", "游戏截图路径", 
                                              "游戏文件路径", "感想", "系统", "语言", "标签", "游戏发售时间", "描述"])

        self.load_and_show()

        self.token_sort = [True] * 12
        
        # self.setFixedSize(650, 440)
        # self.table.resizeColumnsToContents()

        self.initLayout()
        self.initConnect()

        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet('QWidget {background:transparent}')

    def initLayout(self):
        self.addWidget(self.view)
        self.globalLayout.addWidget(self.table)
        self.table.setMinimumHeight(540)

    def initConnect(self):
        self.table.horizontalHeader().sectionClicked.connect(self._sort_table)
        self.table.installEventFilter(ToolTipFilter(self.table))
        self.table.setToolTip("点击任意列，可以按该列排序\n双击任意行，可以跳转到对应游戏的页面")

        # self.table.cellDoubleClicked.connect(self._goto_game)
        self.table.doubleClicked.connect(self._goto_game)

    def load_and_show(self):
        """
        读取game_list.xlsx，并使其显示在self.table中
        """
        game_df = pd.read_excel('./app/resource/data/game_list.xlsx')
        gameInfos = game_df.to_dict('split')['data']

        
        for i, game in enumerate(gameInfos):
            for j in range(12):
                item = QTableWidgetItem()
                if type(game[j]) == int:
                    item.setData(Qt.DisplayRole, game[j])
                else:
                    item.setText(game[j])
                self.table.setItem(i, j, item) 

    def _sort_table(self, col_index):
        if self.token_sort[col_index]:
            self.table.sortByColumn(col_index, Qt.AscendingOrder)
        else:
            self.table.sortByColumn(col_index, Qt.DescendingOrder)

        self.token_sort[col_index] = not self.token_sort[col_index]

    def _goto_game(self, index):
        """发射含有游戏名的信号"""
        row = index.row()
        match_gameName = self.table.item(row, 0).text()
        signalBus.switchToGameWindow.emit(match_gameName)
        
class tableInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(title="游戏详情预览",
                         subtitle="点击打开文件夹可以看到数据表的位置，如果你嫌在软件里修改游戏信息太麻烦，\n可以直接修改数据表。但请注意修改数据表需要严格按照格式，如果你不清楚格式那就不要修改。",
                         parent = parent)
        self.setObjectName("tableInterface")

        self.tableframe = TableFrame(self)
        self.addCusExampleCard(self.tableframe)

        #-------------
        # 重写按钮功能
        #-------------
        self.toolBar.documentButton.setIcon(FluentIcon.SYNC)
        self.toolBar.documentButton.setText("刷新")
        self.toolBar.documentButton.disconnect()
        self.toolBar.documentButton.clicked.connect(self.tableframe.load_and_show)

        self.toolBar.sourceButton.setIcon(FluentIcon.FOLDER)
        self.toolBar.sourceButton.setText("打开文件夹")
        self.toolBar.sourceButton.disconnect()
        cur_path = os.getcwd().replace('\\', '/')
        data_path = cur_path + '/app/resource/data'
        self.toolBar.sourceButton.clicked.connect(lambda: os.startfile(data_path))

        