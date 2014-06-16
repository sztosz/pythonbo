from PySide.QtCore import *
from PySide.QtGui import *

import sys
from urllib.request import urlopen  # In python3 the urlopen is in urllib.request not just the urllib


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        date = self.get_data()
        rates = sorted(self.rates.keys())

        dateLabel = QLabel(date)
        self.fromComboBox = QComboBox()
        self.toComboBox = QComboBox()

        """
        Without iterating trough rates we get
        TypeError: arguments did not match any overloaded call:
        QComboBox.addItem(str, QVariant userData=None): argument 1 has unexpected type 'list'
        QComboBox.addItem(QIcon, str, QVariant userData=None): argument 1 has unexpected type 'list'
        Thus we have to add each rate in loop.
        """
        for rate in rates:
            self.fromComboBox.addItem(rate)
            self.toComboBox.addItem(rate)

        self.fromSpinBox = QDoubleSpinBox()
        self.fromSpinBox.setRange(0.01, 1000)
        self.fromSpinBox.setValue(1.00)

        self.toLabel = QLabel('1.00')

        layout = QGridLayout()
        layout.addWidget(dateLabel, 0, 0)
        layout.addWidget(self.fromComboBox, 1, 0)
        layout.addWidget(self.toComboBox, 2, 0)
        layout.addWidget(self.fromSpinBox, 1, 1)
        layout.addWidget(self.toLabel, 2, 1)
        self.setLayout(layout)

        self.fromComboBox.currentIndexChanged.connect(self.update_ui)
        self.toComboBox.currentIndexChanged.connect(self.update_ui)
        self.fromSpinBox.valueChanged.connect(self.update_ui)

    def get_data(self):
        self.rates = {}
        try:
            date = "Unknown"
            """
            Urlopen returns file-like object in python 3.
            We want string, and ultimately list of lines that are strings.
            To do so, we first read the bytes from the file-like object, so we simply read() it as we would read a file.
            Then we need decode the bytes we read to string (remember it's unicode in python 3) with decode().
            We need list of lines, so we simply split our giant unicode string on new_line with split('\n')
            """
            fh = urlopen('http://www.bankofcanada.ca/en/markets/csv/exchange_eng.csv').read().decode().split('\n')

            for line in fh:
                line = line.rstrip()
                if not line or line.startswith(('#', 'Closing')):
                    continue
                fields = line.split(',')
                if line.startswith('Date '):
                    date = fields[-1]
                else:
                    try:
                        value = float(fields[-1])
                        self.rates[fields[0]] = value
                    except ValueError:
                        pass
            return 'Exchange rates date: {}'.format(date)
        except Exception as e:  # Remember it's python 3 hence deterrent than python 2 construction of error catching.
            return 'Failed to download: {}'.format(e)

    def update_ui(self):
        from_ = self.fromComboBox.currentText()
        to_ = self.toComboBox.currentText()
        results = (self.rates[from_] / self.rates[to_]) * self.fromSpinBox.value()
        self.toLabel.setText("{:.2f}".format(results))

"""
You should be familiar with this, it's to ensure that file is "executed" only if called directly, and not when imported
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
