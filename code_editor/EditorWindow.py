import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.uic import loadUi
from EditorTab import EditorTab

class EditorWindow(QMainWindow):

    def __init__(self, parent=None):
        super(EditorWindow, self).__init__(parent)
        loadUi("code_editor\\ui_files\\editor_window.ui", self)

        self.action_open_file.triggered.connect(self.browse_files) # Evento al presionar abrir archivo
        self.action_save_file.triggered.connect(self.save_file)
        self.action_new_file.triggered.connect(self.new_file)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.remove_tab(index)) # Evento al cerrar tab
        

    def create_editor_tab(self, file_path, file_name):
        tab = EditorTab(file_path=file_path)
        index = self.tabWidget.addTab(tab, file_name)
        self.tabWidget.setCurrentIndex(index)

    def browse_files(self):
        # Evento al abrir un archivo
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "D:/diego/OneDrive - UVG/Documentos Universidad/Semestre 7/Diseño de lenguajes/proyecto compilador/lexical_analyzer")
        
        if len(file_path) > 0:
            file_name = file_path.split("/")[-1]
            
            self.create_editor_tab(file_path, file_name)

    def save_file(self):

        curr_widget = self.tabWidget.currentWidget()

        if isinstance(curr_widget, EditorTab):

            update_tab_name = curr_widget.file_path == None
            # Obtener editor tab actual y guardar archivo
            curr_widget.save_file_content()

            if update_tab_name and curr_widget.file_path != None:
                # Actualizar nombre de tab actual
                file_name = curr_widget.file_path.split("/")[-1]
                curr_index = self.tabWidget.currentIndex()
                self.tabWidget.setTabText(curr_index, file_name)

    def remove_tab(self, tab_index):
        self.tabWidget.removeTab(tab_index)

    def new_file(self):
        self.create_editor_tab(None, "sin_titulo")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    app.exec_()                                                                                                                         