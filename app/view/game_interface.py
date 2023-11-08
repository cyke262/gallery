# coding:utf-8
import sys, os, subprocess, ctypes
import pandas as pd
from pathlib import Path

from PyQt5.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QKeySequence
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,
                             QListWidgetItem, QFileDialog, QShortcut, QSpacerItem, QSizePolicy,
                             QCompleter)

from qfluentwidgets import *
from .gallery_interface import GalleryInterface

from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush
from qfluentwidgets import FluentIcon as FIF
from ..common.config import cfg

def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


class AppCard(CardWidget):
    """ App card """

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.openButton = PushButton('打开', self)
        self.moreButton = TransparentToolButton(FluentIcon.MORE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(48, 48)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.openButton.setFixedWidth(120)

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignRight)

        self.moreButton.setFixedSize(32, 32)
        self.moreButton.clicked.connect(self.onMoreButtonClicked)

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, '共享', self))
        menu.addAction(Action(FluentIcon.CHAT, '写评论', self))
        menu.addAction(Action(FluentIcon.PIN, '固定到任务栏', self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)


class EmojiCard(ElevatedCardWidget):
    """ Emoji card """

    def __init__(self, iconPath: str, parent=None):
        super().__init__(parent)
        self.iconWidget = ImageLabel(iconPath, self)
        self.label = CaptionLabel(Path(iconPath).stem, self)

        self.iconWidget.scaledToHeight(68)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(
            self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.setFixedSize(168, 176)


class StatisticsWidget(QWidget):
    """ Statistics widget """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignBottom)

        setFont(self.valueLabel, 18, QFont.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class AppInfoCard(SimpleCardWidget):
    """ App information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('gameInterface')
        # self.iconLabel = ImageLabel("", self)
        # self.iconLabel.setBorderRadius(8, 8, 8, 8)
        # self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('游戏', self)
        self.nameLabel.setWordWrap(True)
        self.openGameButton = PrimarySplitPushButton('打开游戏', self)
        self.companyLabel = HyperlinkLabel(
            QUrl(''), '官网网址', self)
        # self.openGameButton.setFixedWidth(160)

        self.scoreWidget = StatisticsWidget('评分', '0', self)
        self.separator = VerticalSeparator(self)
        self.statusWidget = StatisticsWidget('状态', '未开始', self)
        self.separator2 = VerticalSeparator(self)
        self.saleTimeWIdget = StatisticsWidget('发售日期', '1970-01-01', self)

        self.descriptionLabel = BodyLabel(
            '点击左侧栏的“从这里开始”，开始编辑你的游戏吧！', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('标签', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        menu = RoundMenu(parent=self)
        self.addTagAct = Action(FluentIcon.ADD, "添加")
        self.clearTagAct = Action(FluentIcon.CLEAR_SELECTION, "清空")
        menu.addAction(self.addTagAct)
        menu.addAction(self.clearTagAct)

        self.addButton = TransparentDropDownPushButton("操作标签", self, FluentIcon.EDIT)
        self.addButton.setMenu(menu)
        # self.addButton.setFixedSize(64, 32)
        self.addButton.setIconSize(QSize(14, 14))

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.twoButtLayout = QHBoxLayout()
        self.buttonLayout1 = QHBoxLayout()
        self.buttonLayout2 = QHBoxLayout()
        self.H_spacerItem = QSpacerItem(1000, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.initLayout()

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        # self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addWidget(self.openGameButton, 0, Qt.AlignRight)

        # company label
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addWidget(self.companyLabel)

        # statistics widgets
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        self.statisticsLayout.addWidget(self.scoreWidget)
        self.statisticsLayout.addWidget(self.separator)
        self.statisticsLayout.addWidget(self.statusWidget)
        self.statisticsLayout.addWidget(self.separator2)
        self.statisticsLayout.addWidget(self.saleTimeWIdget)
        self.statisticsLayout.setAlignment(Qt.AlignLeft)

        # description label
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.twoButtLayout.setContentsMargins(0,0,0,0)
        self.buttonLayout1.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout2.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.twoButtLayout)
        self.twoButtLayout.addLayout(self.buttonLayout1, 1)
        self.twoButtLayout.addItem(self.H_spacerItem)
        self.twoButtLayout.addLayout(self.buttonLayout2, 2)
        self.buttonLayout1.addWidget(self.tagButton, 0, Qt.AlignLeft)
        self.buttonLayout2.addWidget(self.addButton, 0, Qt.AlignRight)

    def _clear_buttonLayout1(self):
        """删除buttonLayout1的标签"""

        item_list = list(range(self.buttonLayout1.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序

        for i in item_list:
            item = self.buttonLayout1.itemAt(i)
            self.buttonLayout1.removeItem(item)
            if item.widget():
                item.widget().deleteLater()


class GalleryCard(HeaderCardWidget):
    """ Gallery card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('游戏截图')

        self.flipView = HorizontalFlipView(self)
        self.expandButton = TransparentToolButton(
            FluentIcon.CHEVRON_RIGHT_MED, self)

        self.expandButton.setFixedSize(32, 32)
        self.expandButton.setIconSize(QSize(12, 12))

        self.flipView.addImages([
            ':/gallery/images/Shoko1.jpg',
            ':/gallery/images/Shoko2.jpg',
            ':/gallery/images/Shoko3.jpg'
        ])
        self.flipView.setBorderRadius(8)
        self.flipView.setSpacing(10)

        self.headerLayout.addWidget(self.expandButton, 0, Qt.AlignRight)
        self.viewLayout.addWidget(self.flipView)


class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = TextEdit(self)
        self.descriptionLabel.setMarkdown("## 示例1 \n * 示例2 🦄 \n * 示例3 🐴 ")
        self.descriptionLabel.installEventFilter(ToolTipFilter(self.descriptionLabel))
        self.descriptionLabel.setToolTip("编写完成后可点按Ctrl+S进行保存")

        # self.descriptionLabel.setWordWrapMode(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('游玩感想')


class SystemRequirementCard(HeaderCardWidget):
    """ System requirements card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统及汉化信息')
        self.sysLabel = BodyLabel('此处显示系统信息', self)
        self.hanHuaLabel = BodyLabel('此处显示汉化信息', self)
        self.sysIcon = IconWidget(InfoBarIcon.SUCCESS, self)
        self.hanHuaIcon = IconWidget(InfoBarIcon.SUCCESS, self)
        self.editButton = HyperlinkLabel('修改信息', self)

        self.vBoxLayout = QVBoxLayout()
        self.hBoxLayout_1 = QHBoxLayout()
        self.hBoxLayout_2 = QHBoxLayout()

        self.sysIcon.setFixedSize(16, 16)
        self.hanHuaIcon.setFixedSize(16, 16)
        self.hBoxLayout_1.setSpacing(10)
        self.hBoxLayout_2.setSpacing(10)
        self.vBoxLayout.setSpacing(16)
        self.hBoxLayout_1.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout_2.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout_1.addWidget(self.sysIcon)
        self.hBoxLayout_1.addWidget(self.sysLabel)
        self.hBoxLayout_2.addWidget(self.hanHuaIcon)
        self.hBoxLayout_2.addWidget(self.hanHuaLabel)
        self.vBoxLayout.addLayout(self.hBoxLayout_1)
        self.vBoxLayout.addLayout(self.hBoxLayout_2)
        self.vBoxLayout.addWidget(self.editButton)

        self.viewLayout.addLayout(self.vBoxLayout)


class LightBox(QWidget):
    """ Light box """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
        else:
            tintColor = QColor(255, 255, 255, 160)

        self.acrylicBrush = AcrylicBrush(self, 30, tintColor, QColor(0, 0, 0, 0))

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity", self)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.vBoxLayout = QVBoxLayout(self)
        self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        self.flipView = HorizontalFlipView(self)
        self.nameLabel = BodyLabel('游戏截图 1', self)
        self.pageNumButton = PillPushButton('1 / 4', self)

        self.pageNumButton.setCheckable(False)
        self.pageNumButton.setFixedSize(80, 32)
        setFont(self.nameLabel, 16, QFont.DemiBold)

        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIconSize(QSize(14, 14))
        self.closeButton.clicked.connect(self.fadeOut)

        self.vBoxLayout.setContentsMargins(26, 28, 26, 28)
        self.vBoxLayout.addWidget(self.closeButton, 0, Qt.AlignRight | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.flipView, 1)
        self.vBoxLayout.addWidget(self.nameLabel, 0, Qt.AlignHCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.pageNumButton, 0, Qt.AlignHCenter)

        self.flipView.addImages([
            ':/gallery/images/Shoko1.jpg',
            ':/gallery/images/Shoko2.jpg',
            ':/gallery/images/Shoko3.jpg'
        ])
        self.flipView.currentIndexChanged.connect(self.setCurrentIndex)

    def setCurrentIndex(self, index: int):
        self.nameLabel.setText(f'游戏截图 {index + 1}')
        self.pageNumButton.setText(f'{index + 1} / {self.flipView.count()}')
        self.flipView.setCurrentIndex(index)

    def paintEvent(self, e):
        if self.acrylicBrush.isAvailable():
            return self.acrylicBrush.paint()

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if isDarkTheme():
            painter.setBrush(QColor(32, 32, 32))
        else:
            painter.setBrush(QColor(255, 255, 255))

        painter.drawRect(self.rect())

    def resizeEvent(self, e):
        w = self.width() - 52
        self.flipView.setItemSize(QSize(w, w * 9 // 16))

    def fadeIn(self):
        rect = QRect(self.mapToGlobal(QPoint()), self.size())
        self.acrylicBrush.grabImage(rect)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.start()
        self.show()

    def fadeOut(self):
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.setDuration(150)
        self.opacityAni.finished.connect(self._onAniFinished)
        self.opacityAni.start()

    def _onAniFinished(self):
        self.opacityAni.finished.disconnect()
        self.hide()


class MicaWindow(Window):

    def __init__(self):
        super().__init__()
        self.setTitleBar(MSFluentTitleBar(self))
        if isWin11():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())


class gameInterface(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('gameInterface')

        self.view = QWidget(self)

        self.globalLayout = QHBoxLayout(self.view)

        self.vBoxLayout_1 = QVBoxLayout()
        self.vBoxLayout_2 = QVBoxLayout()
        self.lineEdit = SearchLineEdit(self)
        self.listWidget = ListWidget(self)
        self.appCard = AppInfoCard(self)
        self.galleryCard = GalleryCard(self)
        self.descriptionCard = DescriptionCard(self)
        self.systemCard = SystemRequirementCard(self)

        self.lightBox = LightBox(self)
        self.lightBox.hide()
        self.galleryCard.flipView.itemClicked.connect(self.showLightBox)

        # 向listWidget中添加游戏名
        self.listWidget.setMinimumHeight(800)
        self.stands = [] # 游戏名，列表
        self.tags = [] # 所有标签，列表
        self.game_xq = {} # 游戏详情信息，二重字典
        self.load()
        for stand in self.stands:
            self.listWidget.addItem(QListWidgetItem(stand))
        
        # 设置listWidget右键菜单
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.list_menu)        
        self.listWidget.clicked.connect(lambda: self.show_game()) # 点击listWidget，在右侧显示内容

        # 设置自动补全输入框
        self.lineEdit.setPlaceholderText("在此处进行搜索")
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.searchButton.clicked.connect(lambda: self._scroll_to_game(self.lineEdit.text()))
        self.lineEdit.returnPressed.connect(lambda: self._scroll_to_game(self.lineEdit.text()))
        completer = QCompleter(self.stands, self.lineEdit)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.lineEdit.setCompleter(completer)

        # 设置打开游戏按钮
        self.appCard.openGameButton.clicked.connect(self._open_exe)
        self.appCard.openGameButton.setFlyout(self._create_fly_menu())

        # 设置打开图片文件夹按钮
        self.galleryCard.expandButton.clicked.connect(self._open_pic_folder)

        # 创建一个快捷键对象，并且绑定到按钮的点击事件
        shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self.descriptionCard)
        shortcut.activated.connect(self._save_reflection)

        # 设置标签处的两个Action
        self.appCard.addTagAct.triggered.connect(self._add_tag)
        self.appCard.clearTagAct.triggered.connect(self._clear_all_tags)

        # 设置修改信息按钮
        self.systemCard.editButton.clicked.connect(self._edit_misc_info)

        # --------------
        # 以下为布局部分
        # --------------

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("appInterface")

        self.vBoxLayout_1.setSpacing(10)
        self.vBoxLayout_1.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout_1.addWidget(self.lineEdit, 1, Qt.AlignTop)
        self.vBoxLayout_1.addWidget(self.listWidget, 100, Qt.AlignTop)
        
        self.vBoxLayout_2.setSpacing(10)
        self.vBoxLayout_2.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout_2.addWidget(self.appCard, 0, Qt.AlignTop)
        self.vBoxLayout_2.addWidget(self.galleryCard, 0, Qt.AlignTop)
        self.vBoxLayout_2.addWidget(self.descriptionCard, 0, Qt.AlignTop)
        self.vBoxLayout_2.addWidget(self.systemCard, 0, Qt.AlignTop)

        vBox1 = QWidget()
        vBox1.setLayout(self.vBoxLayout_1)
        vBox2 = QWidget()
        vBox2.setLayout(self.vBoxLayout_2)
        self.globalLayout.addWidget(vBox1, 1)
        self.globalLayout.addWidget(vBox2, 4)

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet('QWidget {background:transparent}')

    def list_menu(self, pos):
        """
        列表项右键菜单
        """

        menu = RoundMenu(parent=self)

        # add actions
        creAct = Action(FIF.ADD, "新建")
        delAct = Action(FIF.DELETE, "删除")

        editSubmenu = RoundMenu("编辑", self)
        editSubmenu.setIcon(FIF.EDIT)

        editCompAct = Action(FIF.LABEL, "编辑厂商名")
        editScoreAct = Action(FIF.LABEL, "编辑分数")
        editStaAct = Action(FIF.LABEL, "编辑游戏状态")
        editTimeAct = Action(FIF.LABEL, "编辑发售日期")
        editDesAct = Action(FIF.LABEL, "编辑游戏说明")
        editPicPathAct = Action(FIF.LABEL, "编辑图片文件夹路径")
        editExePathAct = Action(FIF.LABEL, "编辑exe文件路径")
        editSubmenu.addActions([editCompAct, editScoreAct, editStaAct, 
                                editTimeAct, editDesAct ,editPicPathAct, editExePathAct])

        renameAct = Action(FIF.TAG, "重命名")

        menu.addAction(creAct)
        # add separator
        menu.addSeparator()

        if self.listWidget.itemAt(pos):
            menu.addAction(delAct)
            menu.addMenu(editSubmenu)
            menu.addAction(renameAct)

        creAct.triggered.connect(self.cre_item)
        delAct.triggered.connect(self.del_item)
        editCompAct.triggered.connect(lambda: self.edit_item(actType="EDIT_COMP"))
        editScoreAct.triggered.connect(lambda: self.edit_item(actType="EDIT_SCORE"))
        editStaAct.triggered.connect(lambda: self.edit_item(actType="EDIT_STA"))
        editTimeAct.triggered.connect(lambda: self.edit_item(actType="EDIT_TIME"))
        editDesAct.triggered.connect(lambda: self.edit_item(actType="EDIT_DES"))
        editPicPathAct.triggered.connect(lambda: self.edit_item(actType="EDIT_PIC_PATH"))
        editExePathAct.triggered.connect(lambda: self.edit_item(actType="EDIT_EXE_PATH"))
        renameAct.triggered.connect(self.rename_item)

        menu.exec(self.listWidget.mapToGlobal(pos), ani=True)
    
    def cre_item(self):
        # pop message box window
        w = Cus_MessageBox(self.window(), type="CREATE")

        if w.exec():
            gameName = w.gameNameLineEdit.text()
            gameComp = w.gameCompanyLineEdit.text()
            gameScore = w.gameScoreLineEdit.text()
            gameSta = w.gameStatusBox.text()
            gamePicFolderPath = w.picButton.text()
            gameExePath = w.exeButton.text()
            gameTime = w.gameTimePicker.getDate().toString(Qt.ISODate)
            
            if gamePicFolderPath == "选择图片文件夹" or gamePicFolderPath == "":
                gamePicFolderPath = "NONE"

            if gameExePath == "选择游戏exe文件" or gameExePath == "":
                gameExePath = "NONE"

            # add item to listwidget
            self.listWidget.addItem(QListWidgetItem(gameName))

            # add data and scroll to bottom of listwidget , and save
            self.stands.append(gameName)
            self.game_xq[gameName] = {'Comp':gameComp, 'Score':gameScore, 'Status':gameSta, 'Reflection':"NONE",
                                      'PicFolderPath':gamePicFolderPath, 'ExePath':gameExePath, 'Description':"NONE", 
                                      'Bugs':"NONE", 'CHN':"NONE", 'Tags':"NONE", 'SaleTime':gameTime}
            self.listWidget.scrollToBottom()
            self.save()
    
    def del_item(self):
        gameName = self.listWidget.item(self.listWidget.currentRow()).text()

        # delete item in listwidget
        self.listWidget.takeItem(self.listWidget.currentRow())

        # delete data and save
        self.stands.remove(gameName)
        del self.game_xq[gameName]
        self.save()

    def edit_item(self, actType="EDIT_COMP"):
        w = Cus_MessageBox(self.window(), type=actType)

        if w.exec():
            gameName = self.listWidget.item(self.listWidget.currentRow()).text()

            match actType:
                case "EDIT_COMP":
                    self.game_xq[gameName]['Comp'] = w.gameCompanyLineEdit.text()
                case "EDIT_SCORE":
                    self.game_xq[gameName]['Score'] = w.gameScoreLineEdit.text()
                case "EDIT_STA":
                    self.game_xq[gameName]['Status'] = w.gameStatusBox.text()
                case "EDIT_TIME":
                    self.game_xq[gameName]['SaleTime'] = w.gameTimePicker.getDate().toString(Qt.ISODate)
                case "EDIT_DES":
                    self.game_xq[gameName]['Description'] = w.gameDescription.toPlainText()[:150] + "..."
                case "EDIT_PIC_PATH":
                    gamePicFolderPath = w.picButton.text()
                    if gamePicFolderPath == "选择图片文件夹":
                        gamePicFolderPath = ""
                    self.game_xq[gameName]['PicFolderPath'] = gamePicFolderPath
                case "EDIT_EXE_PATH":
                    gameExePath = w.exeButton.text()
                    if gameExePath == "选择游戏exe文件":
                        gameExePath = ""
                    self.game_xq[gameName]['ExePath'] = gameExePath

            self.save()
            self.show_game()

    def rename_item(self):
        old_gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        # pop message box window
        w = Cus_MessageBox(self.window(), type="RENAME")

        if w.exec():
            new_gameName = w.gameNameLineEdit.text()

            # change item in listwidget
            self.listWidget.item(self.listWidget.currentRow()).setText(new_gameName)

            # edit data and save
            self.stands.remove(old_gameName)
            self.stands.append(new_gameName)
            old_dict_item = self.game_xq[old_gameName]
            del self.game_xq[old_gameName]
            self.game_xq[new_gameName] = old_dict_item
            self.save()

    def _search_and_click(self):
        gameName = self.lineEdit.text()
        self._scroll_to_game(gameName)

    def _create_fly_menu(self):
        menu = RoundMenu(parent=self)
        openLE_Act = Action("用LE打开游戏", triggered=lambda: self._open_exe(if_LE=True))
        menu.addActions([openLE_Act])
        return menu

    def _open_exe(self, if_LE=False):
        gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        exePath = self.game_xq[gameName]['ExePath']
        if exePath == "NONE":
            w = MessageBox("系统找不到指定的文件", 
                           "系统找不到游戏exe文件的路径，请先为当前游戏选择exe文件，右键点击左侧游戏栏即可添加exe文件。", 
                           self.window())
            w.exec()
            return
        
        if if_LE:
            print(gameName, " 以Locale Emulator（管理员权限）打开")
            try:
                subprocess.run([cfg.get(cfg.LEprocPath), "-runas", "370317ca-3615-4b24-a9c3-c5ddd850c0f4", exePath])
            except:
                w = MessageBox("出错了！", "以Locale Emulator（管理员权限）打开游戏出现错误，请到设置界面检查LEProc.exe的路径是否正确。", self.window())
                w.exec()
            return
        
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
            
        if is_admin():
            print(gameName, " 以管理员权限打开")
            subprocess.run(exePath)
        else:
            print(gameName, " 以非管理员权限打开")
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", exePath)
            else:#in python2.x
                ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
    
    def _open_pic_folder(self):
        gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        try:
            os.startfile(self.game_xq[gameName]['PicFolderPath'])
        except Exception as e:
            title = "系统找不到指定的文件"
            content = "系统找不到游戏截图文件夹，请检查当前游戏是否选择了截图文件夹，右键点击左侧游戏栏即可添加截图文件夹。"
            content += ("\n返回错误信息: "+ str(e))
            w = MessageBox(title, content, self.window())
            w.exec()

    def _save_reflection(self):
        gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        self.game_xq[gameName]['Reflection'] = self.descriptionCard.descriptionLabel.toMarkdown()
        self.save()
        self.show_game()

    def _add_tag(self):
        w = Cus_MessageBox(self.window(), type="ADDTAG", arg=self.tags)

        if w.exec():
            gameName = self.listWidget.item(self.listWidget.currentRow()).text()
            newTag = w.comboBox.text()
            # 添加标签
            if self.game_xq[gameName]['Tags'] == "NONE":
                self.game_xq[gameName]['Tags'] = newTag
            else:
                self.game_xq[gameName]['Tags'] += newTag
            self.game_xq[gameName]['Tags'] += "|" # tags规定以 | 为结尾
            
            # 向标签列表添加，并去重
            self.tags.append(newTag)
            self.tags = list(set(self.tags))

            self.save()
            self.show_game()

    def _clear_all_tags(self):
        gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        self.game_xq[gameName]['Tags'] = "NONE"
        self.save()
        self.show_game()
    
    def _edit_misc_info(self):
        w = Cus_MessageBox(self.window(), type="MISC")

        if w.exec():
            gameName = self.listWidget.item(self.listWidget.currentRow()).text()
            self.game_xq[gameName]['Bugs'] = w.bugComboBox.text()
            self.game_xq[gameName]['CHN'] = w.langComboBox.text()

            self.save()
            self.show_game()

    def load(self):
        game_df = pd.read_excel('./app/resource/data/game_list.xlsx', index_col=0)
        tags_df = pd.read_excel('./app/resource/data/tags_list.xlsx', index_col=1)
        self.stands = list(game_df.index)
        self.tags = list(tags_df.index)
        # print(self.stands)
        self.game_xq = game_df.to_dict('index')

    def save(self):
        InfoBar.warning(
            title="提示",
            content="正在进行保存",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=1500,
            parent=self
            )
        
        game_df_new = pd.DataFrame(self.game_xq).T
        game_df_new.to_excel('./app/resource/data/game_list.xlsx')
        tags_df_new = pd.DataFrame(self.tags)
        tags_df_new.to_excel('./app/resource/data/tags_list.xlsx')

    def show_game(self, gameName=""):
        """
        点击列表项事件
        """

        if gameName == "":
            gameName = self.listWidget.item(self.listWidget.currentRow()).text()
        self.appCard.nameLabel.setText(gameName) # 游戏名
        self.appCard.companyLabel.setText(self.game_xq[gameName]['Comp']) # 厂商名
        self.appCard.scoreWidget.valueLabel.setText(str(self.game_xq[gameName]['Score'])) # 分数
        self.appCard.statusWidget.valueLabel.setText(self.game_xq[gameName]['Status']) # 状态
        self.appCard.saleTimeWIdget.valueLabel.setText(self.game_xq[gameName]['SaleTime']) # 发售日期

        # 有两个flipview，需要对两者进行更新
        self.galleryCard.flipView.clear()
        self.lightBox.flipView.clear()

        # list to store files path
        if self.game_xq[gameName]['PicFolderPath'] != "NONE":
            pic_path = []
            for (_, _, file_name) in os.walk(self.game_xq[gameName]['PicFolderPath']):
                pic_path.extend(file_name)

            for i in range(len(pic_path)):
                pic_path[i] = self.game_xq[gameName]['PicFolderPath'] + '/' + pic_path[i]
        
            self.galleryCard.flipView.addImages(pic_path)
            self.lightBox.flipView.addImages(pic_path)

            # 当图片超过3张时，顶部出现警告
            if len(pic_path) > 3:
                InfoBar.warning(
                title="警告",
                content="当前游戏的图片数量较多，会影响软件运行速度",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=1500,    # won't disappear automatically
                parent=self
                )
            
        self.appCard.descriptionLabel.setText(self.game_xq[gameName]['Description'])
        self.descriptionCard.descriptionLabel.setMarkdown(self.game_xq[gameName]['Reflection']) # 游戏感想

        # 展示系统信息
        self.systemCard.sysLabel.setText(self.game_xq[gameName]['Bugs'])
        match self.game_xq[gameName]['Bugs']:
            case "此游戏存在恶性bug":
                self.systemCard.sysIcon.setIcon(InfoBarIcon.ERROR)
            case "此游戏需要使用LE转区运行":
                self.systemCard.sysIcon.setIcon(InfoBarIcon.WARNING)
            case "此游戏可开箱即用":
                self.systemCard.sysIcon.setIcon(InfoBarIcon.SUCCESS)
            case _:
                self.systemCard.sysIcon.setIcon(InfoBarIcon.WARNING)

        # 展示汉化信息
        self.systemCard.hanHuaLabel.setText(self.game_xq[gameName]['CHN'])
        match self.game_xq[gameName]['CHN']:
            case "此游戏没有中文":
                self.systemCard.hanHuaIcon.setIcon(InfoBarIcon.ERROR)
            case "此游戏存在汉化版补丁":
                self.systemCard.hanHuaIcon.setIcon(InfoBarIcon.WARNING)
            case "此游戏原生支持中文":
                self.systemCard.hanHuaIcon.setIcon(InfoBarIcon.SUCCESS)
            case _:
                self.systemCard.hanHuaIcon.setIcon(InfoBarIcon.WARNING)

        #添加标签
        self.appCard._clear_buttonLayout1()
        if self.game_xq[gameName]['Tags'] != "NONE":
            # tags_list以 | 为结尾，所以分开后要pop掉最后的空字符串
            tags_list = self.game_xq[gameName]['Tags'].split('|')
            tags_list.pop()
        
            for t in tags_list:
                self.tagButton = PillPushButton(t, self)
                self.tagButton.setCheckable(False)
                setFont(self.tagButton, 12)
                self.tagButton.setFixedSize(80, 32)
                self.appCard.buttonLayout1.addWidget(self.tagButton, 1, Qt.AlignLeft)
                self.appCard.buttonLayout1.addSpacing(3)

    def showLightBox(self):
        index = self.galleryCard.flipView.currentIndex()
        self.lightBox.setCurrentIndex(index)
        self.lightBox.fadeIn()

    def _scroll_to_game(self, gameName):
        """
        滑动至gameName对应的项，并点击
        """
        if gameName in self.stands:
            g = self.listWidget.findItems(gameName, Qt.MatchContains)[0]
            self.listWidget.scrollToItem(g)
            self.listWidget.setCurrentItem(g)
            self.show_game(gameName)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.lightBox.resize(self.size())


class Demo3(MSFluentWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.appInterface = gameInterface(self)

        # add sub interfaces
        self.addSubInterface(self.appInterface, FluentIcon.LIBRARY, "库", FluentIcon.LIBRARY_FILL, isTransparent=True)
        self.navigationInterface.addItem("editInterface", FluentIcon.EDIT, "编辑", selectable=False)

        self.navigationInterface.addItem(
            "settingInterface", FluentIcon.SETTING, "设置", position=NavigationItemPosition.BOTTOM, selectable=False)

        self.resize(880, 760)
        self.setWindowTitle('PyQt-Fluent-Widgets')
        # self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))

        self.titleBar.raise_()

class Cus_MessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None, type="CREATE", arg=None):
        super().__init__(parent)
        if type == "CREATE":
            self.titleLabel = SubtitleLabel("添加游戏", self)
        
            self.gameNameLineEdit = LineEdit(self)
            self.gameNameLineEdit.setPlaceholderText('填写游戏名称')
            self.gameNameLineEdit.setClearButtonEnabled(True)

            self.gameCompanyLineEdit = LineEdit(self)
            self.gameCompanyLineEdit.setPlaceholderText('填写厂商名称')
            self.gameCompanyLineEdit.setClearButtonEnabled(True)

            self.gameTimePicker = CalendarPicker(self)
            self.gameTimePicker.installEventFilter(ToolTipFilter(self.gameTimePicker))
            self.gameTimePicker.setToolTip("填写游戏的发售（开服）日期")

            self.gameScoreLineEdit = LineEdit(self)
            self.gameScoreLineEdit.setPlaceholderText('填写游戏评分')
            self.gameScoreLineEdit.setClearButtonEnabled(True)

            self.gameStatusBox = ComboBox(self)
            self.gameStatusBox.addItems(["已通关", "大部分通关", "部分通关", "弃坑", "正在玩"])
            self.gameStatusBox.setCurrentIndex(0)

            self.picButton = PushButton("选择图片文件夹")
            self.picButton.clicked.connect(self._select_folder)
            self.picButton.installEventFilter(ToolTipFilter(self.picButton))
            self.picButton.setToolTip("选择含有图片的文件夹，注意确保文件夹下只有图片，且没有其他文件夹")

            self.exeButton = PushButton("选择游戏exe文件")
            self.exeButton.clicked.connect(self._select_file)
            self.exeButton.installEventFilter(ToolTipFilter(self.exeButton))
            self.exeButton.setToolTip("选择游戏的exe文件，文件后缀不是exe会导致启动游戏失败")

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameNameLineEdit)
            self.viewLayout.addWidget(self.gameCompanyLineEdit)
            self.viewLayout.addWidget(self.gameTimePicker)
            self.viewLayout.addWidget(self.gameScoreLineEdit)
            self.viewLayout.addWidget(self.gameStatusBox)
            self.viewLayout.addWidget(self.picButton)
            self.viewLayout.addWidget(self.exeButton)

            self.yesButton.setDisabled(True)
            self.gameNameLineEdit.textChanged.connect(self._checkvalidate)
        elif type == "RENAME":
            self.titleLabel = SubtitleLabel("重命名游戏", self)

            self.gameNameLineEdit = LineEdit(self)
            self.gameNameLineEdit.setPlaceholderText('填写游戏名称')
            self.gameNameLineEdit.setClearButtonEnabled(True)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameNameLineEdit)

            self.yesButton.setDisabled(True)
            self.gameNameLineEdit.textChanged.connect(self._checkvalidate)
        elif type == "EDIT_COMP":
            self.titleLabel = SubtitleLabel("编辑厂商名", self)
            self.gameCompanyLineEdit = LineEdit(self)
            self.gameCompanyLineEdit.setPlaceholderText('填写厂商名称')
            self.gameCompanyLineEdit.setClearButtonEnabled(True)

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameCompanyLineEdit)

            self.yesButton.setDisabled(True)
            self.gameCompanyLineEdit.textChanged.connect(self._checkvalidate)
        elif type == "EDIT_SCORE":
            self.titleLabel = SubtitleLabel("编辑分数", self)
            self.gameScoreLineEdit = LineEdit(self)
            self.gameScoreLineEdit.setPlaceholderText('填写游戏评分')
            self.gameScoreLineEdit.setClearButtonEnabled(True)

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameScoreLineEdit)

            self.yesButton.setDisabled(True)
            self.gameScoreLineEdit.textChanged.connect(self._checkvalidate)
        elif type == "EDIT_STA":
            self.titleLabel = SubtitleLabel("编辑游戏状态", self)
            self.gameStatusBox = ComboBox(self)
            self.gameStatusBox.addItems(["已通关", "大部分通关", "部分通关", "弃坑", "正在玩"])
            self.gameStatusBox.setCurrentIndex(0)

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameStatusBox)
        elif type == "EDIT_TIME":
            self.titleLabel = SubtitleLabel("编辑发售日期", self)
            self.gameTimePicker = CalendarPicker(self)
            
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameTimePicker)
        elif type == "EDIT_DES":
            self.titleLabel = SubtitleLabel("编辑游戏说明", self)
            self.gameDescription = TextEdit(self)
            self.gameDescription.installEventFilter(ToolTipFilter(self.gameDescription))
            self.gameDescription.setToolTip("游戏说明超过150字的部分将会被截断，请注意")

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.gameDescription)
        elif type == "EDIT_PIC_PATH":
            self.titleLabel = SubtitleLabel("编辑图片文件夹路径", self)
            self.picButton = PushButton("选择图片文件夹")
            self.picButton.clicked.connect(self._select_folder)
            self.picButton.installEventFilter(ToolTipFilter(self.picButton))
            self.picButton.setToolTip("选择含有图片的文件夹，注意确保文件夹下只有图片，且没有其他文件夹")

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.picButton)
        elif type == "EDIT_EXE_PATH":
            self.titleLabel = SubtitleLabel("编辑exe文件路径", self)
            self.exeButton = PushButton("选择游戏exe文件")
            self.exeButton.clicked.connect(self._select_file)
            self.exeButton.installEventFilter(ToolTipFilter(self.exeButton))
            self.exeButton.setToolTip("选择游戏的exe文件，文件后缀不是exe会导致启动游戏失败")

            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.exeButton)
        elif type == "ADDTAG":
            self.titleLabel = SubtitleLabel("添加标签", self)
            self.comboBox = EditableComboBox()
            self.comboBox.addItems(arg)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.comboBox)

            self.yesButton.setDisabled(True)
            self.comboBox.textChanged.connect(self._checkvalidate)           
        elif type == "MISC":
            self.titleLabel = SubtitleLabel("修改信息", self)

            self.bugComboBox = EditableComboBox()
            self.bugComboBox.setPlaceholderText("填写游戏系统信息")
            self.bugComboBox.addItems([
                "此游戏需要使用LE转区运行",
                "此游戏可开箱即用",
                "此游戏存在恶性bug"
            ])

            self.langComboBox = EditableComboBox()
            self.langComboBox.setPlaceholderText("填写游戏语言信息")
            self.langComboBox.addItems([
                "此游戏原生支持中文",
                "此游戏存在汉化版补丁",
                "此游戏没有中文"
            ])

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.bugComboBox)
            self.viewLayout.addWidget(self.langComboBox)
        
        # change the text of button
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(360)
            
    def _select_folder(self):
        # folder path
        m = QFileDialog.getExistingDirectory(self, "选取文件夹", "C:/")
        self.picButton.setText(m)
    
    def _select_file(self):
        dir = QFileDialog.getOpenFileName(self,  "选择文件","C:/", "exe Files (*.exe)")
        self.exeButton.setText(dir[0]) # dir是元组

    def _checkvalidate(self, text):
        if text:
            self.yesButton.setEnabled(True)

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w3 = Demo3()
    w3.show()
    app.exec_()
