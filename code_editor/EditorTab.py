import sys
sys.path.append("compiler_source_code")

from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.uic import loadUi
from Editor import Editor
from compiler_source_code.semanticAnalyzer import executeSemanticAnalyzer


class EditorTab(QWidget):


  def __init__(self, filePath=None):
    super(EditorTab, self).__init__()
    loadUi("code_editor\\ui_files\\editor_tab.ui", self)
    
    
    self.filePath = filePath
    self.editor = Editor()
    
    self.loadFileContent()

    self.editor_container_layout.addWidget(self.editor) # Añadir componente editor

    # Eventos
    self.execute_button.clicked.connect(lambda x: self.executeCode())
    
    # Habilitar o deshabilitar botón ejecutar dependiendo de si está guardado el archivo
    self.execute_button.setEnabled(filePath != None)



  def getFileExtension(self):
    if self.filePath == None:
        return None
    
    fileName = self.filePath.split("/")[-1]

    fileExtension = None
    if len(fileName.split(".")) >= 2:
        fileExtension = fileName.split(".", maxsplit=1)[-1]
    
    return fileExtension

  def loadFileContent(self):
    
    if self.filePath != None:
        with open(self.filePath, mode="r", encoding="utf-8") as file:
            self.editor.setText(file.read())

  def saveFileContent(self):

    if self.filePath == None:
        # Guardar archivo
        file, _type = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Compiscript Files (*.csp)",)
        
        if len(file) == 0: # Cancel
            return
        
        self.filePath = file

    self.execute_button.setEnabled(self.filePath != None)

    with open(self.filePath, mode="w", encoding="utf-8") as file:
        file.write(self.editor.text())
  
  def consoleLog(self, message):
    self.console.appendPlainText(message)
    

  def executeCode(self):
    
    # Guardar archivo antes de ejecutar
    self.saveFileContent()
    filePath = self.filePath
    
    self.consoleLog(">>\n")
    
    self.consoleLog("Ejecutando análisis del programa...")
    
    hasErrors, errors, code = executeSemanticAnalyzer(filePath)
    
    if not hasErrors:
        self.consoleLog("\nEl programa no contiene errores.")
        
        self.consoleLog("\nCódigo intermedio generado:")
        self.consoleLog(code)        
        
    else:
        self.consoleLog("\nErrores encontrados:")
        for error in errors:
            self.consoleLog(str(error))


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = EditorTab()
  window.show()
  app.exec_()                                                                                                                         