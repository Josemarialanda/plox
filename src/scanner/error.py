class Error:  
  def __init__(self,line,column,message):
    self.line  :  int = line
    self.column:  int = column
    self.message: str = message
      
  def __repr__(self):
    return f'''
      line : {self.line}
      column : {self.column}
      {self.message}
      '''