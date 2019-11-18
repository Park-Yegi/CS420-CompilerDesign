class Scope(object):
  def __init__(self, scope):
    self.start_line = scope[0]
    self.end_line = scope[1]
    self.symbol_table = {}
    self.parent_scope = None
    # SYMBOL TABLE
    # symbol name
    # current value
    # history (ith line, value)

  def __str__(self):
    if (self.parent_scope is None):
      return "From " + str(self.start_line) + " to " + str(self.end_line) + "\n\t" + "I don't have parent. I am the root" 
    else:
      return "From " + str(self.start_line) + " to " + str(self.end_line) + "\n\t" + "My parent is " + str(self.parent_scope.start_line) +  " to " + str(self.parent_scope.end_line)

  def print_symboltable(self):
    print(self.symbol_table)
    # for i in range(len(self.symbol_table)):
    #   print(self.symbol_table[i])
