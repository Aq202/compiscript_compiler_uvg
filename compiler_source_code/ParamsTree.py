class Params:
  def __init__(self, parent):
    self.parent = parent
    self.data = {}

  def add(self, key, value):
    self.data[key] = value

  def get(self, key):
    return self.data.get(key, None)
  
  def __repr__(self) -> str:
    return f"Params({self.data})"
  
class ParamsTree:
  """
  Clase para almacenar parametros de nodos en un árbol.
  Importante siempre destruir los parametros de un nodo al terminar de usarlos.
  No acceder directamente a _currentNodeParams, siempre inicializar los parametros de un nodo con
  initNodeParams antes de acceder a los parametros de un padre.
  """
  def __init__(self):
    self._currentNodeParams = None

  def initNodeParams(self):
    """
    Agrega un nuevo nivel de parametros al arbol de parametros.
    Todos los valores que se agreguen a partir de esta llamada pertenecerán al mismo grupo de parametros.
    @return: (parentParams, currentNodeParams) Tupla con los parametros del nodo padre y del nodo actual.
    """
    parentParams = self._currentNodeParams
    self._currentNodeParams = Params(parent=parentParams)

    return parentParams, self._currentNodeParams
  
  def removeNodeParams(self):
    """
    Elimina el grupo de parametros actual y regresa al grupo de parametros anterior.
    return: Los parametros del nodo actual.
    """
    currentParams = self._currentNodeParams
    self._currentNodeParams = self._currentNodeParams.parent
    return currentParams