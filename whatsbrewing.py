import json
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

    dump_beer_details = []

    for batch in batches:
        recipe = batch['recipe']
        brew_date = batch['brewDate']
        batch_id = batch['_id']
        status = batch['status']

        if status == "Archived":
            continue

        batch_details = json.loads(requests.get("https://api.brewfather.app/v2/batches/{}".format(batch_id), auth=tokens).text)

        print(batch_details)
        batch_names.append(recipe['name'])
        batch_statuses.append(status)
        batch_abv.append(batch_details['measuredAbv'])

        dump_beer_details.append(batch_details)

    with open("cache.dump.json", "w") as outfile:
        json.dump(dump_beer_details, outfile, indent=4)

    return batch_names, batch_statuses, batch_abv


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.beer_cache = []

        self.beers_completed = []
        self.beers_conditioning = []
        self.beers_fermenting = []

        self.api_tokens = read_api_tokens()

        self.update_beer_cache(False)

    def update_beer_cache(self, fetch):
        if fetch is True:
            self.beer_cache = request_brew_father_data(tokens=self.api_tokens)
            with open('cache.json', 'w') as json_file:
                json.dump(self.beer_cache, json_file)
        else:
            with open('cache.json', 'r') as json_file:
                self.beer_cache = json.load(json_file)

        for name, status, abv in zip(self.beer_cache[0], self.beer_cache[1], self.beer_cache[2]):
            if status == 'Fermenting':
                self.beers_fermenting.append([name, status, abv])

            if status == 'Conditioning':
                self.beers_conditioning.append([name, status, abv])

            if status == 'Completed':
                self.beers_completed.append([name, status, abv])

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Beer HUD")
        # self.showFullScreen()

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

        tap_1_auto_group = QtWidgets.QButtonGroup()
        tap_2_auto_group = QtWidgets.QButtonGroup()

        for beer in self.beers_completed:
            hbox = QtWidgets.QHBoxLayout(self)
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} - {}%'.format(beer[0], beer[2]))
            beer_label.setFont(listing_font)
            hbox.addWidget(beer_label)
            tap_one = QtWidgets.QPushButton(self)
            tap_one.setFixedSize(64, 64)
            tap_one.setIcon(QtGui.QIcon("Icons/TapIcon1.png"))
            tap_one.setIconSize(QtCore.QSize(64, 64))
            tap_one.setCheckable(True)
            tap_one.autoExclusive = True
            hbox.addWidget(tap_one)
            tap_two = QtWidgets.QPushButton(self)
            tap_two.setFixedSize(64, 64)
            tap_two.setIconSize(QtCore.QSize(64, 64))
            tap_two.setIcon(QtGui.QIcon("Icons/TapIcon2.png"))
            tap_two.setCheckable(True)
            tap_two.autoExclusive = True
            hbox.addWidget(tap_two)
            party_tap = QtWidgets.QPushButton(self)
            party_tap.setFixedSize(64, 64)
            party_tap.setIconSize(QtCore.QSize(64, 64))
            party_tap.setIcon(QtGui.QIcon("Icons/FloorIcon.png"))
            party_tap.setCheckable(True)
            hbox.addWidget(party_tap)
            vbox.addLayout(hbox)

        conditioning_label = QtWidgets.QLabel(self)
        conditioning_label.setText("Conditioning")
        conditioning_label.setFont(header_font)
        vbox.addWidget(conditioning_label)

        for beer in self.beers_conditioning:
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} - {}%'.format(beer[0], beer[2]))
            beer_label.setFont(listing_font)
            vbox.addWidget(beer_label)

        fermenting_label = QtWidgets.QLabel(self)
        fermenting_label.setText("Fermenting")
        fermenting_label.setFont(header_font)
        vbox.addWidget(fermenting_label)

        for beer in self.beers_fermenting:
            beer_label = QtWidgets.QLabel(self)
            beer_label.setText('{} - {}%'.format(beer[0], beer[2]))
            beer_label.setFont(listing_font)
            vbox.addWidget(beer_label)

        big_red_update = QtWidgets.QToolButton(self)
        big_red_update.setIcon(QtGui.QIcon("Icons/Refresh.png"))
        big_red_update.setFixedSize(64, 64)
        big_red_update.setIconSize(QtCore.QSize(64, 64))
        big_red_update.clicked.connect(self.onFetchBrewfatherData)
        vbox.addWidget(big_red_update, alignment=QtCore.Qt.AlignRight)

        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.show()


    def onFetchBrewfatherData(self):
        self.update_beer_cache(fetch=True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

