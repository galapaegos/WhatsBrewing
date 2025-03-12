import datetime
import json
import os
import time

import requests
import sys

from PySide6 import QtWidgets, QtGui, QtCore


def read_api_tokens():
    with open("auth.json", "r") as infile:
        json_object = json.load(infile)

        return json_object['username'], json_object['passkey']

    return '', ''


def request_brew_father_data(tokens):
    response = requests.get("https://api.brewfather.app/v2/batches", auth=tokens)

    batches = json.loads(response.text)

    batch_names = []
    batch_statuses = []
    batch_abv = []
    batch_brew_date = []
    batch_bottling_date = []
    # batch_og = []
    # batch_fg = []
    batch_style = []

    dump_beer_details = []

    for batch in batches:
        recipe = batch['recipe']
        batch_id = batch['_id']
        status = batch['status']

        if status == "Archived":
            continue

        batch_details = json.loads(requests.get("https://api.brewfather.app/v2/batches/{}".format(batch_id), auth=tokens).text)

        batch_names.append(recipe['name'])
        batch_statuses.append(status)
        batch_abv.append(batch_details['measuredAbv'])
        batch_brew_date.append(batch_details['brewDate'])
        batch_bottling_date.append(batch_details['bottlingDate'])
        # batch_og.append(batch_details['measuredOg'])
        # batch_fg.append(batch_details['measuredFg'])
        batch_style.append(batch_details['recipe']['style']['name'])

        dump_beer_details.append(batch_details)

    with open("cache.dump.json", "w") as outfile:
        json.dump(dump_beer_details, outfile, indent=4)

    return batch_names, batch_statuses, batch_abv, batch_brew_date, batch_bottling_date, batch_style


def get_elapsed_time(posix):
    current_time = datetime.date.today()

    past_time = datetime.date.fromtimestamp(posix/1000)

    return (current_time - past_time).days


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.beer_cache = []

        self.beers_completed = []
        self.beers_conditioning = []
        self.beers_fermenting = []

        self.completed_buttons = []

        self.api_tokens = read_api_tokens()

        self.update_beer_cache(False)

    def update_beer_cache(self, fetch):
        self.beer_cache = []

        self.beers_completed = []
        self.beers_conditioning = []
        self.beers_fermenting = []

        if fetch is True:
            self.beer_cache = request_brew_father_data(tokens=self.api_tokens)
            with open('cache.json', 'w') as json_file:
                json.dump(self.beer_cache, json_file)
        else:
            if os.path.isfile("cache.json"):
                with open('cache.json', 'r') as json_file:
                    self.beer_cache = json.load(json_file)

        if len(self.beer_cache) > 0:
            for name, status, abv, brew_date, bottle_date, style in zip(self.beer_cache[0],
                                                                        self.beer_cache[1],
                                                                        self.beer_cache[2],
                                                                        self.beer_cache[3],
                                                                        self.beer_cache[4],
                                                                        self.beer_cache[5]):
                if status == 'Fermenting':
                    self.beers_fermenting.append([name, status, abv, brew_date, bottle_date, style])

                if status == 'Conditioning':
                    self.beers_conditioning.append([name, status, abv, brew_date, bottle_date, style])

                if status == 'Completed':
                    self.beers_completed.append([name, status, abv, brew_date, bottle_date, style])

        self.initUI()

    def initUI(self):
        self.setWindowTitle("What's Brewing?")
        # self.showFullScreen()

        self.completed_buttons.clear()

        self.resize(1024, 600)

        header_font = QtGui.QFont()
        header_font.setBold(True)
        header_font.setPointSize(24)

        listing_font = QtGui.QFont()
        listing_font.setPointSize(18)

        tap_font = QtGui.QFont()
        tap_font.setBold(True)
        tap_font.setPointSize(20)

        vbox = QtWidgets.QVBoxLayout(self)

        on_tap_label = QtWidgets.QLabel(self)
        on_tap_label.setText("On Tap")
        on_tap_label.setFont(header_font)
        vbox.addWidget(on_tap_label)

        icon_size = 96
        icon_width = icon_size + 32
        icon_height = icon_size + 8

        for i, beer in enumerate(self.beers_completed):
            hbox = QtWidgets.QHBoxLayout(self)
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} [{}] {}%  - ({} days)'.format(beer[0], beer[5], beer[2], get_elapsed_time(beer[4])))
            beer_label.setFont(listing_font)
            hbox.addWidget(beer_label)
            tap_one = QtWidgets.QPushButton(self)
            tap_one.setObjectName('{}.1'.format(i))
            tap_one.setFixedSize(icon_width, icon_height)
            tap_one.setIcon(QtGui.QIcon("Icons/TapIcon1.png"))
            tap_one.setIconSize(QtCore.QSize(icon_size, icon_size))
            tap_one.setCheckable(True)
            tap_one.clicked.connect(self.on_tap_pressed)
            self.completed_buttons.append(tap_one)
            hbox.addWidget(tap_one)
            tap_two = QtWidgets.QPushButton(self)
            tap_two.setObjectName('{}.2'.format(i))
            tap_two.setFixedSize(icon_width, icon_height)
            tap_two.setIconSize(QtCore.QSize(icon_size, icon_size))
            tap_two.setIcon(QtGui.QIcon("Icons/TapIcon2.png"))
            tap_two.setCheckable(True)
            tap_two.clicked.connect(self.on_tap_pressed)
            self.completed_buttons.append(tap_two)
            hbox.addWidget(tap_two)
            party_tap = QtWidgets.QPushButton(self)
            party_tap.setObjectName('{}.3'.format(i))
            party_tap.setFixedSize(icon_width, icon_height)
            party_tap.setIconSize(QtCore.QSize(icon_size, icon_size))
            party_tap.setIcon(QtGui.QIcon("Icons/FloorIcon.png"))
            party_tap.setCheckable(True)
            party_tap.clicked.connect(self.on_tap_pressed)
            self.completed_buttons.append(party_tap)

            hbox.addWidget(party_tap)
            vbox.addLayout(hbox)

        conditioning_label = QtWidgets.QLabel(self)
        conditioning_label.setText("Conditioning")
        conditioning_label.setFont(header_font)
        vbox.addWidget(conditioning_label)

        for beer in self.beers_conditioning:
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} [{}] {}%  ({} days)'.format(beer[0], beer[5], beer[2], get_elapsed_time(beer[4])))
            beer_label.setFont(listing_font)
            vbox.addWidget(beer_label)

        fermenting_label = QtWidgets.QLabel(self)
        fermenting_label.setText("Fermenting")
        fermenting_label.setFont(header_font)
        vbox.addWidget(fermenting_label)

        for beer in self.beers_fermenting:
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} [{}] {}%  ({}days)'.format(beer[0], beer[5], beer[2], get_elapsed_time(beer[4])))
            beer_label.setFont(listing_font)
            vbox.addWidget(beer_label)

        big_red_update = QtWidgets.QToolButton(self)
        big_red_update.setIcon(QtGui.QIcon("Icons/Refresh.png"))
        big_red_update.setFixedSize(icon_size, icon_size)
        big_red_update.setIconSize(QtCore.QSize(icon_size, icon_size))
        big_red_update.clicked.connect(self.on_fetch_brewfather_data)
        vbox.addWidget(big_red_update, alignment=QtCore.Qt.AlignRight)

        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.show()

    def on_fetch_brewfather_data(self):
        self.update_beer_cache(fetch=True)

    def on_tap_pressed(self):
        sender_name = self.sender().objectName()
        parts = sender_name.split('.')

        beer = parts[0]
        tap = parts[1]

        for button in self.completed_buttons:
            names = button.objectName()

            if names == sender_name:
                continue

            pieces = names.split('.')

            if pieces[0] == beer:
                button.setChecked(False)
                button.repaint()

            if pieces[1] == '3':
                continue

            if pieces[1] == tap:
                button.setChecked(False)
                button.repaint()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

