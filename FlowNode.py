class FlowNode(object):
  def __init__(self, lineno, next_node = None, statement = None):
    self.lineno = lineno
    self.next_node = next_node
    self.next_node_branch = None
    self.next_node_branch2 = None
    self.statement = statement
    self.visited = False
  
  def __str__(self):
    if (self.next_node is None):
      return str(self.lineno) + "th line and I dont have next node"
    else:
      return str(self.lineno) + "th line and next node is " + str(self.next_node.lineno)


  # def make_flow(self, ast, line_scope, stat_list):
  #   statement_idx = 0
  #   start_node = FlowNode(line_scope[0])
  #   cur_node = start_node

  #   for j in range(line_scope[0]+1, line_scope[1]+1):
  #     cur_node.next_node = FlowNode(j)
  #     cur_node = cur_node.next_node
  #     if (type(stat_list[statement_idx][-1]) is tuple and stat_list[statement_idx][-1][0] == j):
  #       cur_node = cur_node.make_flow(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2])
  #     elif ((type(stat_list[statement_idx][-1]) is int) and stat_list[statement_idx][-1] == j):
  #       cur_node.statement = stat_list[statement_idx]
  #       statement_idx += 1

  #   return start_node