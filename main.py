import sys
sys.path.append("code_editor")

from PyQt5.QtWidgets import  QApplication
from PyQt5.uic import loadUi
from code_editor.EditorWindow import EditorWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    app.exec_()      