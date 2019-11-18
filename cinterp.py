from clex import toks, scope_list
from cparse_revised import result, endline_of_file
from Scope import Scope
from FlowNode import FlowNode

## MAKE (GLOBAL) FUNCTION TABLE #########
func_table = {}

for i in range(len(result)):
  if result[i][0] == "func":
    ast = result[i]
    if len(ast[3]) == 1 and ast[3][0] == "void":
      func_table[ast[2]] = {'ret_type':ast[1], 'param_num': 0, 'param_list': [], 'flow_graph': None}
    else:
      func_table[ast[2]] = {'name':ast[2], 'ret_type':ast[1], 'param_num': len(ast[3]), 'param_list': ast[3], 'flow_graph':None}

# print("** FUNCTION TABLE: dictionary of dictionaries **")
# print(func_table)
#########################################


## MAKE SCOPE and SYMBOL TABLE ##########
Scope_list = []

# Make Scope object per scope
for i in range(len(scope_list)):
  new_scope = Scope(scope_list[i])
  Scope_list.append(new_scope)

# Set parent scope for each Scope object
for i in range(len(Scope_list)):
  if (Scope_list[i].start_line == 1 and Scope_list[i].end_line == endline_of_file):
      Scope_list[i].parent_scope = None
  else:
    for j in range(i):
      if (Scope_list[j].start_line <= Scope_list[i].start_line and Scope_list[j].end_line >= Scope_list[i].end_line):
        Scope_list[i].parent_scope = Scope_list[j]

# Print Scope (for debugging)
# print("** SCOPE LIST **")
# for i in range(len(Scope_list)):
#   print(Scope_list[i])
#########################################

def make_flow(ast, line_scope, stat_list):
  statement_idx = 0
  start_node = FlowNode(line_scope[0])
  cur_node = start_node
  
  j = line_scope[0]+1
  while (j <= line_scope[1]):
    if (statement_idx < len(stat_list)):
      if (type(stat_list[statement_idx][-1]) is tuple and stat_list[statement_idx][-1][0] == j+1):
        cur_node.next_node = FlowNode(j)
        cur_node = cur_node.next_node
        if (stat_list[statement_idx][0] == 'FOR'):
          cur_node.statement = stat_list[statement_idx][0:6]
        elif (stat_list[statement_idx][0] == 'IF'):
          cur_node.statement = stat_list[statement_idx][0:4]
        cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2], cur_node)
        j = stat_list[statement_idx][-1][1]
        statement_idx += 1
      elif ((type(stat_list[statement_idx][-1]) is int) and stat_list[statement_idx][-1] == j):
        cur_node.next_node = FlowNode(j)
        cur_node.next_node.statement = stat_list[statement_idx]
        statement_idx += 1
        cur_node = cur_node.next_node
      else:
        cur_node.next_node = FlowNode(j)
        cur_node = cur_node.next_node
    else:
      cur_node.next_node = FlowNode(j)
      cur_node = cur_node.next_node
    
    # Advance
    j += 1

  return start_node

def make_flow_branch(ast, line_scope, stat_list, prev_node):
  statement_idx = 0
  start_node = FlowNode(line_scope[0])
  cur_node = start_node
  
  j = line_scope[0]+1
  while (j <= line_scope[1]):
    if (statement_idx < len(stat_list)):
      if (type(stat_list[statement_idx][-1]) is tuple and stat_list[statement_idx][-1][0] == j+1):
        cur_node.next_node = FlowNode(j)
        cur_node = cur_node.next_node
        if (stat_list[statement_idx][0] == 'FOR'):
          cur_node.statement = stat_list[statement_idx][0:6]
        elif (stat_list[statement_idx][0] == 'IF'):
          cur_node.statement = stat_list[statement_idx][0:4]
        cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2], cur_node)
        j = stat_list[statement_idx][-1][1]
        statement_idx += 1
      elif ((type(stat_list[statement_idx][-1]) is int) and stat_list[statement_idx][-1] == j):
        cur_node.next_node = FlowNode(j)
        cur_node.next_node.statement = stat_list[statement_idx]
        statement_idx += 1
        cur_node = cur_node.next_node
      else:
        cur_node.next_node = FlowNode(j)
        cur_node = cur_node.next_node
    else:
      cur_node.next_node = FlowNode(j)
      cur_node = cur_node.next_node
    
    # Advance
    j += 1

  cur_node.next_node = prev_node
  return start_node

## MAKE FLOW GRAPH FOR EACH FUNCTION(INCLUDING MAIN) ####
main_flow = None
for i in range(len(result)):
  if result[i][0] == 'func':
    ast = result[i]
    ast_scope = ast[5]
    statement_list = ast[4]

    func_flow = make_flow(ast, ast_scope, statement_list)
    if ast[2] in func_table.keys():
      func_table[ast[2]]['flow_graph'] = func_flow

    if ast[2] == 'main':
      main_flow = func_flow
########################################################

def calc_value(val_val, cur_scope):
  if type(val_val) is int:
    return val_val
  elif len(val_val) == 1:
    return int(val_val)
  elif len(val_val) == 3 and val_val[1] == '*':
    return get_value(val_val[0], cur_scope) * int(val_val[2])
  elif len(val_val) == 3 and val_val[1] == '+':
    if get_value(val_val[2], cur_scope) is None:
      return get_value(val_val[0], cur_scope) + calc_value(val_val[2], cur_scope)
    return get_value(val_val[0], cur_scope) + get_value(val_val[2], cur_scope)
  elif len(val_val) == 2 and val_val[0] in func_table.keys():
    global main_flow
    flow_stack.append(main_flow)
    main_flow = func_table[val_val[0]]['flow_graph']
    global jump_to_new_func
    jump_to_new_func = True
    global new_func
    new_func = val_val[0]
    global param_pass
    param_pass = [calc_value(val_val[1][0], cur_scope), get_value(val_val[1][1], cur_scope)]
    print(param_pass)

def get_value(val_name, cur_scope):
  if type(val_name) is tuple:
    if (val_name[0] in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name[0]]['value'][get_value(val_name[1], cur_scope)]
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_value(val_name, cur_scope.parent_scope)
  else:
    if (val_name in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name]['value']
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_value(val_name, cur_scope.parent_scope)

def print_value(val_name, cur_scope):
  if (val_name in cur_scope.symbol_table.keys()):
    if 'value' in cur_scope.symbol_table[val_name].keys():
      print(cur_scope.symbol_table[val_name]['value'])
    else:
      print('N/A')
  else:
    if cur_scope.parent_scope is None:
      print("No", val_name, "in this scope")
    else:
      print_value(val_name, cur_scope.parent_scope)

def print_trace(val_name, cur_scope):
  if (val_name in cur_scope.symbol_table.keys()):
    trace_list = cur_scope.symbol_table[val_name]['history']
    for i in range(len(trace_list)):
      print(val_name, "=", trace_list[i][1], "at line", trace_list[i][0])
  else:
    if cur_scope.parent_scope is None:
      print("No", val_name, "in this scope")
    else:
      print_trace(val_name, cur_scope.parent_scope)

def assign_value(val_name, val_val, cur_scope):
  if type(val_name) is tuple:  # Assign in array
    if (val_name[0] in cur_scope.symbol_table.keys()):
      cur_scope.symbol_table[val_name[0]]['value'][int(get_value(val_name[1] ,cur_scope))] = calc_value(val_val, cur_scope)
    else:
      if cur_scope.parent_scope is None:
        print("No", val_name, "in this scope")
      else:
        assign_value(val_name, val_val, cur_scope.parent_scope)
  else:
    if (val_name in cur_scope.symbol_table.keys()):
      cur_scope.symbol_table[val_name]['value'] = calc_value(val_val, cur_scope)
    else:
      if cur_scope.parent_scope is None:
        print("No", val_name, "in this scope")
      else:
        assign_value(val_name, val_val, cur_scope.parent_scope)


current_scope = Scope_list[0]
flow_stack = []
param_pass = []
program_end = False
jump_to_new_func = False
new_func = None
## MAIN LOOP
while (1):
  cmd = input(">> ")
  if (cmd[0:4] == "next"):
    if (len(cmd) == 4):
      line_num = 1
    else:
      line_num = int(cmd[5:])
    
    for i in range(line_num):
      if program_end:
        break

      print("line", main_flow.lineno, main_flow.statement)
      
      if (main_flow.statement is None):
        for j in range(len(Scope_list)):
          if main_flow.lineno == Scope_list[j].start_line:
            current_scope = Scope_list[j]
            print("Change scope to", current_scope)
            if jump_to_new_func:
              # save parameter to new symbol_table
              params = func_table[new_func]['param_list']
              for k in range(func_table[new_func]['param_num']):
                current_scope.symbol_table[params[k][1]] = {'value':param_pass[k]}
              current_scope.print_symboltable()
              jump_to_new_func = False
            break
          elif main_flow.lineno == Scope_list[j].end_line:
            current_scope = current_scope.parent_scope
            print("Change scope to", current_scope)
            break
        main_flow = main_flow.next_node

      elif main_flow.statement[0] == 'declare':
        for j in range(len(main_flow.statement[2])):
          if type(main_flow.statement[2][j]) is tuple:  # declaration of array
            current_scope.symbol_table[main_flow.statement[2][j][0]] = {"type":main_flow.statement[1]+"arr", "size":int(main_flow.statement[2][j][1]), "value":['N/A' for k in range(int(main_flow.statement[2][j][1]))]}
          else:
            current_scope.symbol_table[main_flow.statement[2][j]] = {"type":main_flow.statement[1]}
        current_scope.print_symboltable()
        main_flow = main_flow.next_node

      elif main_flow.statement[0] == 'assign':
        assign_value(main_flow.statement[1], main_flow.statement[3], current_scope)
        current_scope.print_symboltable()
        current_scope.parent_scope.print_symboltable()
        if jump_to_new_func == False:
          main_flow = main_flow.next_node

      elif main_flow.statement[0] == 'FOR':
        if main_flow.visited:
          assign_value(main_flow.statement[4][0], get_value(main_flow.statement[4][0],current_scope)+1, current_scope)
          if (get_value(main_flow.statement[3][0], current_scope) < get_value(main_flow.statement[3][2],current_scope)):
            main_flow = main_flow.next_node_branch
          else:
            main_flow = main_flow.next_node
        else:
          assign_value(main_flow.statement[2][1], main_flow.statement[2][3], current_scope)
          main_flow.visited = True
          if (get_value(main_flow.statement[3][0], current_scope) < get_value(main_flow.statement[3][2],current_scope)):
            main_flow = main_flow.next_node_branch
          else:
            main_flow = main_flow.next_node
        current_scope.print_symboltable()

      elif main_flow.statement[0] == 'IF':
        if main_flow.visited:
          main_flow = main_flow.next_node
        else:
          main_flow.visited = True
          if (get_value(main_flow.statement[2][0], current_scope) > get_value(main_flow.statement[2][2],current_scope)):
            main_flow = main_flow.next_node_branch
          else:
            main_flow = main_flow.next_node
      
      if (main_flow is None):
        print("End of program")
        program_end = True

  elif (cmd[0:5] == "trace"):
    if len(cmd) == 5:  # No parameter
      pass
    else:
      print_trace(cmd[6:], current_scope)
  elif (cmd[0:5] == "print"):
    if len(cmd) == 5:  # No parameter
      pass
    else:
      print_value(cmd[6:], current_scope)
  elif (cmd[0:4] == "quit"):
    break
  else:
    pass


## Traverse flow graph (for debugging)
"""
func_name = input("Name of function >> ")
if func_name in func_table.keys():
  trav_sub = func_table[func_name]['flow_graph']

while (1):
  cmd = input(">> ")
  if (cmd[0:7] == "printnb") :
    print(trav_sub.next_node_branch)
  elif (cmd[0:6] == "printn"):
    print(trav_sub.next_node)
  elif (cmd[0:5] == "print"):
    print(trav_sub)
  elif (cmd[0:5] == "nextb"):
    trav_sub = trav_sub.next_node_branch
    print(trav_sub)
  elif (cmd[0:4] == "next"):
    trav_sub = trav_sub.next_node
    print(trav_sub)
  elif (cmd[0:6] == "change"):
    func_name = input("Name of function >> ")
    if func_name in func_table.keys():
      trav_sub = func_table[func_name]['flow_graph']
  elif (cmd[0:4] == "quit"):
    break
  else:
    pass
""" 
  