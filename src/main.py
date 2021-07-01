import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvas

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog


class UDiscAnalyzer(QtWidgets.QMainWindow):
    def __init__(self):
        super(UDiscAnalyzer, self).__init__()
        uic.loadUi('../res/ui/udisc-analyzer.ui', self)

        self.courses = None
        self.scores = None
        self.scorecard = None

        self.player = None
        self.course = None
        self.course_layout = None

        self.plot_widget = None

        self.btn_load_scorecard.clicked.connect(self.get_scorecard)
        self.list_players.itemClicked.connect(self.update_lists)
        self.list_courses.itemClicked.connect(self.update_lists)
        self.list_layouts.itemClicked.connect(self.update_lists)
        self.list_plots.itemClicked.connect(self.update_plots)

        self.fig_a, self.ax_a = plt.subplots()
        self.fig_b, self.ax_b = plt.subplots()
        self.fig_c, self.ax_c = plt.subplots()

        self.show()

    def get_scorecard(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            os.getcwd(), "Image files (*.csv)")

        if not fname[0]:
            return

        self.text_scorecard.setText(fname[0])

        self.scorecard = pd.read_csv(fname[0])

        self.list_players_update()
        self.list_courses_update(True)
        self.list_layouts_update(True)

    def update_lists(self):
        cur_player = self.player
        self.list_players_update()
        new_player = cur_player != self.player

        cur_course = self.course
        self.list_courses_update(new_player)
        new_course = cur_course != self.course

        self.list_layouts_update(new_course)

        self.plot_mean()

    def list_players_update(self):
        if len(self.list_players.selectedItems()) == 0:
            self.scores = self.scorecard.loc[self.scorecard['PlayerName'] != 'Par']

            players = sorted(self.scores['PlayerName'].unique(), reverse=True,
                             key=lambda p: (self.scores.PlayerName == p).sum())

            self.list_players.addItems(players)
            self.list_players.setCurrentRow(0)

        self.player = self.list_players.currentItem().text()

    def list_courses_update(self, clear):
        self.courses = self.scorecard.loc[self.scorecard['PlayerName'] == 'Par'].drop_duplicates(
            subset=['CourseName', 'LayoutName'], keep='first')

        courses_by_player = self.scorecard.loc[self.scorecard['PlayerName'] == self.list_players.currentItem().text()]

        courses_only = sorted(courses_by_player['CourseName'].unique())

        if clear:
            self.list_courses.clear()
            self.list_courses.addItems(courses_only)
            self.list_courses.setCurrentRow(0)

        self.course = self.list_courses.currentItem().text()

    def list_layouts_update(self, clear):
        layouts = self.courses.loc[
            self.courses['CourseName'] == self.list_courses.currentItem().text(), 'LayoutName'].unique().tolist()

        if clear:
            self.list_layouts.clear()
            self.list_layouts.addItems(layouts)
            self.list_layouts.setCurrentRow(0)

    def update_plots(self):
        pass

    def plot_mean(self):
        player = self.list_players.currentItem().text()
        course = self.list_courses.currentItem().text()
        layout = self.list_layouts.currentItem().text()

        df = self.scores.loc[(self.scores['PlayerName'] == player) & (self.scores['CourseName'] == course) & (
                self.scores['LayoutName'] == layout)]

        result = df.groupby("PlayerName").mean().select_dtypes(include=[np.number]).iloc[0, 2:]
        par = self.courses.loc[
                  (self.courses['CourseName'] == course) & (self.courses['LayoutName'] == layout)].select_dtypes(
            include=[np.number]).iloc[0, 2:]

        print(self.courses)

        self.ax_a.cla()
        par.plot(kind='line', ax=self.ax_a)
        result.plot(kind='line', ax=self.ax_a)

        self.ax_b.cla()
        par.plot(kind='line', ax=self.ax_b)
        result.plot(kind='line', ax=self.ax_b)

        self.ax_c.cla()
        par.plot(kind='line', ax=self.ax_c)
        result.plot(kind='line', ax=self.ax_c)

        if not self.plot_widget:
            self.plot_widget = FigureCanvas(self.fig_a)

            lay = QtWidgets.QVBoxLayout(self.widget_plot_a)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(self.plot_widget)


            plot_widget_b = FigureCanvas(self.fig_b)

            lay = QtWidgets.QVBoxLayout(self.widget_plot_b)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(plot_widget_b)

            plot_widget_c = FigureCanvas(self.fig_c)

            lay = QtWidgets.QVBoxLayout(self.widget_plot_c)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(plot_widget_c)

        else:
            self.fig_a.canvas.draw_idle()
            self.fig_b.canvas.draw_idle()
            self.fig_c.canvas.draw_idle()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = UDiscAnalyzer()
    sys.exit(app.exec_())
