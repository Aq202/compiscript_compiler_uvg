import sys
sys.path.append("lexical_analyzer")
sys.path.append("syntactic_analyzer")

from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QInputDialog, QLineEdit
from PyQt5.uic import loadUi
from Editor import Editor
import subprocess



class EditorTab(QWidget):


    def __init__(self, file_path=None):
        super(EditorTab, self).__init__()
        loadUi("code_editor\\ui_files\\editor_tab.ui", self)
        
        
        self.file_path = file_path
        self.editor = Editor()
        
        self.load_file_content()

        self.editor_container_layout.addWidget(self.editor) # Añadir componente editor

        # Eventos
        self.execute_button.clicked.connect(lambda x: self.execute_code())

        # Habilitar o deshabilitar botón ejecutar dependiendo de si está guardado el archivo
        self.execute_button.setEnabled(file_path != None)


    def get_file_extension(self):
        if self.file_path == None:
            return None
        
        file_name = self.file_path.split("/")[-1]

        file_extension = None
        if len(file_name.split(".")) >= 2:
            file_extension = file_name.split(".", maxsplit=1)[-1]
        
        return file_extension

    def load_file_content(self):
        
        if self.file_path != None:
            with open(self.file_path, mode="r", encoding="utf-8") as file:
                self.editor.setText(file.read())

    def save_file_content(self):

        if self.file_path == None:
            # Guardar archivo
            file, _type = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "YAL Files (*.yal)",)
            
            if len(file) == 0: # Cancel
                return
            
            self.file_path = file


        with open(self.file_path, mode="w", encoding="utf-8") as file:
            file.write(self.editor.text())
    
    def console_log(self, message):
        self.console.appendPlainText(message)

    def execute_external_script(self, script, argument):
        """
        Método que permite ejecutar un script de python en un subproceso e imprimir resultados
        en consola.
        """
        command = ["python", script, argument]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Manejar error en ejecución del script
        error = process.stderr.read()
        if error:
            self.console_log("Error al ejecutar script:\n")
            self.console_log(error)
            return

        # Muestra la salida del proceso
        self.console_log("Resultados del analizador léxico:\n")
        for linea in process.stdout:
            self.console_log(linea.strip())  # Decodifica la salida a una cadena de texto

        process.wait()

    

    def execute_code(self):
        self.console_log(">>\n")
        
        file_extension = self.get_file_extension()
        
        if file_extension == "yal":
            pass
        else:
            self.console_log("No hay acción a ejecutar con este tipo de archivo.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTab()
    window.show()
    app.exec_()                                                                                                                         