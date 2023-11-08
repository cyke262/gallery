# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import pandas as pd

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('GalLauncher', self)
        self.banner = QPixmap('./app/resource/images/header2.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        gameInfos, max_sc, sum_sc = self.load_from_excel()

        self.linkCardView.addCard(
            ':/gallery/images/overall.svg',
            str(len(gameInfos)),
            "你的游戏库含有的游戏总数",
            ""
        )

        s = gameInfos[-1][0]
        if len(s) > 6:
            s = s[:6] + "..."
        self.linkCardView.addCard(
            ':/gallery/images/new.svg',
            s,
            "你的游戏库最近添加的新游戏",
            ""
        )

        self.linkCardView.addCard(
            FluentIcon.GLOBE,
            str(round(max_sc, 2)),
            "你的游戏库的所有游戏中最高的评分",
            ""
        )

        self.linkCardView.addCard(
            ':/gallery/images/score.svg',
            str(round(sum_sc, 2)),
            "你的游戏库的所有游戏的平均评分",
            ""
        )

    def load_from_excel(self):
        game_df = pd.read_excel('./app/resource/data/game_list.xlsx')
        gameInfos = game_df.to_dict('split')['data']
        max_sc = 0
        sum_sc = 0
        if len(gameInfos) == 0:
            return gameInfos, max_sc, sum_sc

        for g in gameInfos:
            max_sc = max(max_sc, g[2])
            sum_sc += g[2]
        sum_sc /= len(gameInfos)
        return gameInfos, max_sc, sum_sc

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # draw background color
        if not isDarkTheme():
            painter.fillPath(path, QColor(206, 216, 228))
        else:
            painter.fillPath(path, QColor(0, 0, 0))

        # draw banner image
        # pixmap = self.banner.scaled(self.size(), aspectRatioMode=Qt.KeepAspectRatio)
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(self.banner))


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # basic input samples
        pivotView = SampleCardView("跳转到界面", self.view)
        pivotView.addSampleCard(icon=FluentIcon.DOCUMENT,
            title="温馨提示",
            content="有些Galgame需要管理员权限才能启动，\n所以最好以管理员权限打开本软件哦",
            routeKey="",
            index=0
        ) 
        pivotView.addSampleCard(
            icon=FluentIcon.DOCUMENT,
            title="温馨提示",
            content="基于同样的原因，Locale Emulator最好\n也设置为管理员权限",
            routeKey="",
            index=0
        )
        pivotView.addSampleCard(
            icon=FluentIcon.GAME,
            title="游戏管理",
            content="管理你的游戏库，为每个游戏添加信息",
            routeKey="gameInterface",
            index=0
        )
        pivotView.addSampleCard(
            icon=FluentIcon.LIBRARY,
            title="游戏一览",
            content="以表格的形式总览库中的所有游戏",
            routeKey="tableInterface",
            index=8
        )
        pivotView.addSampleCard(
            icon=FluentIcon.SETTING,
            title="设置",
            content="进入设置界面",
            routeKey="settingtInterface",
            index=10
        )

        self.vBoxLayout.addWidget(pivotView)

        # date time samples
        exLinkView = SampleCardView("外部链接", self.view)
        exLinkView.addSampleCard(
            icon=":/gallery/images/gitee.png",
            title="Gitee仓库",
            content="也许你想看看源代码和使用说明",
            routeKey="goToGiteeLink",
            index=0
        )
        exLinkView.addSampleCard(
            icon=FluentIcon.GITHUB,
            title="Github仓库",
            content="也许你想看看源代码和使用说明",
            routeKey="goToGithubLink",
            index=2
        )
        exLinkView.addSampleCard(
            icon=FluentIcon.QUESTION,
            title="Bug反馈",
            content="我发现了Bug！",
            routeKey="goToIssueLink",
            index=4
        )
        self.vBoxLayout.addWidget(exLinkView)

        