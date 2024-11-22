import sys

from PyQt5.QtWidgets import QApplication
from Application import Application

def main():
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

