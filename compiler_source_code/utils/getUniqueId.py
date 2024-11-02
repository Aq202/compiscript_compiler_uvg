from uuid import uuid4

def getUniqueId():
  return uuid4().hex[:6]