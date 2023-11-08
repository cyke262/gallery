# coding: utf-8
from PyQt5.QtCore import QUrl, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen, SimpleCardWidget)
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .setting_interface import SettingInterface
from .game_interface import gameInterface
from .table_interface import tableInterface
from ..common.config import SUPPORT_URL, cfg, GITEE_REPO_URL, FEEDBACK_URL, REPO_URL
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource


class MainWindow(FluentWindow):
    size_signal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        self.gameInterface = gameInterface(self)
        self.tableInterface = tableInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.switchToGameWindow.connect(self.switchToGameWindow)
        signalBus.supportSignal.connect(self.onSupport)
        # self.size_signal.connect(self.viewInterface.mainwindow_size_changed)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.gameInterface, FIF.GAME, "游戏", pos)
        self.addSubInterface(self.tableInterface, FIF.LIBRARY_FILL, "表格", pos)

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('Cyke', ':/gallery/images/kaltsit.png'),
            onClick=self.onSupport,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        w = MessageBox(
            '支持作者',
            '如果你觉得这个软件帮到了你，而你又恰好财力雄厚，那不妨给作者一点支持🍗',
            self
        )
        w.yesButton.setText('狠狠支持')
        w.cancelButton.setText('下次一定')
        if w.exec():
            QDesktopServices.openUrl(QUrl(SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.splashScreen.resize(self.size())
        # 获取新的窗口大小
        new_size = e.size()
        self.size_signal.emit(new_size.width(), new_size.height())

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        match routeKey:
            case "gameInterface":
                self.stackedWidget.setCurrentIndex(1)
            case "tableInterface":
                self.stackedWidget.setCurrentIndex(2)
            case "settingtInterface":
                self.stackedWidget.setCurrentIndex(3)
            case "goToGiteeLink":
                QDesktopServices.openUrl(QUrl(GITEE_REPO_URL))
            case "goToGithubLink":
                QDesktopServices.openUrl(QUrl(REPO_URL))
            case "goToIssueLink":
                QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
    def switchToGameWindow(self, gameName):
        """
        切换至gameInterface界面，并调用点击函数
        """
        self.stackedWidget.setCurrentIndex(1) # 切换至gameInterface界面（第2个界面）
        self.gameInterface._scroll_to_game(gameName)