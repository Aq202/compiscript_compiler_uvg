import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.uic import loadUi
from EditorTab import EditorTab

class EditorWindow(QMainWindow):

  def __init__(self, parent=None):
    super(EditorWindow, self).__init__(parent)
    loadUi("code_editor\\ui_files\\editor_window.ui", self)
    
    # Cambiar el título de la ventana
    self.setWindowTitle("IDE Compiscript")


    self.action_open_file.triggered.connect(self.browseFiles) # Evento al presionar abrir archivo
    self.action_save_file.triggered.connect(self.saveFile)
    self.action_new_file.triggered.connect(self.newFile)
    self.tabWidget.tabCloseRequested.connect(lambda index: self.removeTab(index)) # Evento al cerrar tab
      

  def createEditorTab(self, filePath, fileName):
    tab = EditorTab(filePath=filePath)
    index = self.tabWidget.addTab(tab, fileName)
    self.tabWidget.setCurrentIndex(index)

  def browseFiles(self):
    # Evento al abrir un archivo
    filePath, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "D:/diego/OneDrive - UVG/Documentos Universidad/Semestre 7/Diseño de lenguajes/proyecto compilador/lexical_analyzer")
    
    if len(filePath) > 0:
      fileName = filePath.split("/")[-1]
      
      self.createEditorTab(filePath, fileName)

  def saveFile(self):

    currWidget = self.tabWidget.currentWidget()

    if isinstance(currWidget, EditorTab):

      updateTabName = currWidget.filePath == None
      # Obtener editor tab actual y guardar archivo
      currWidget.saveFileContent()

      if updateTabName and currWidget.filePath != None:
        # Actualizar nombre de tab actual
        fileName = currWidget.filePath.split("/")[-1]
        currIndex = self.tabWidget.currentIndex()
        self.tabWidget.setTabText(currIndex, fileName)

  def removeTab(self, tab_index):
    self.tabWidget.removeTab(tab_index)

  def newFile(self):
    self.createEditorTab(None, "sin_titulo")
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = EditorWindow()
  window.show()
  app.exec_()                                                                                                                         