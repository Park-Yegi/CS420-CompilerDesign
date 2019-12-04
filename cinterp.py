from clex import clex,scope_list_ext
from cparse_revised import cparse
from Scope import Scope
from FlowNode import FlowNode
from Memory import Memory
import re
import copy
import sys

debug=True

## global variables
# These variables are going to be used in interperter and calc_value function.
current_address = 0 
func_table={}                 # interpreter(global w),calc_value(global r)
main_flow = None              # interpreter(global w),calc_value(global w)
current_scope = None          # interpreter(global w),calc_value(global w)
flow_stack = []               # interpreter(global w),calc_value(global w)
param_pass = []               # calc_value(global w),interpreter(global r)
param_pass_addr = []
jump_to_new_func = False      # interpreter(global w),calc_value(global w)
new_func = None               # interpreter(global r),calc_value(global w)
ret_val = None                # interpreter(global w),calc_value(global w)
memory = None
isError=False

def interpreter(input_path="exampleInput.c",debugging=False):
  ### STEP 0:declaration of (global) variables and preprocessing ###

  # Declarate variables
  global func_table,main_flow,current_scope,flow_stack,jump_to_new_func, ret_val,current_scope, memory, isError, debug

  program_end = False

  # Set debugging mode
  if debugging:
    debug=True

  # Make AST
  with open(input_path,'r') as outfile:
    result=cparse().parse(
      input=outfile.read(),
      lexer=clex(),
      tracking=True
    )

  # in case of Syntax error -> end program  
  if result==None:
    isError=True
    return
    
  # Make function table
  for i in range(len(result)):
    if result[i][0] == "func":
      ast = result[i]
      if len(ast[3]) == 1 and ast[3][0] == "void":
        func_table[ast[2]] = {'ret_type':ast[1], 'param_num': 0, 'param_list': [], 'flow_graph': None}
      else:
        func_table[ast[2]] = {'name':ast[2], 'ret_type':ast[1], 'param_num': len(ast[3]), 'param_list': ast[3], 'flow_graph':None}

  # make symbol table
  # sub 1: Convert scope list to Scope objects 
  Scope_list=list(map(lambda x: Scope(x),scope_list_ext(input_path=input_path)))
  # sub 2: Find parent scope for each scopes
  # note: Scope_list[0] is always global scope(see scope_list_ext)
  for i in range(1,len(Scope_list)):
      for j in range(i):
        if (Scope_list[j].start_line <= Scope_list[i].start_line and Scope_list[j].end_line >= Scope_list[i].end_line):
          Scope_list[i].parent_scope = Scope_list[j]
  
  current_scope = Scope_list[0]
  # Print Scope (for debugging)
  if debug:
    print("** SCOPE LIST **")
    for output in Scope_list:
      print(output)
    print("** FUNCTION TABLE: dictionary of dictionaries **")
    print(func_table)

  # make flow graph for each functions
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

  # Make memory structure
  memory = Memory()

  ### STEP 1:main loop ###
  syntax=re.compile(r"(\Anext( (0|[1-9]\d*))?\Z)|(\Aprint [A-Za-z_]\w*(\[\d*\])?\Z)|(\Atrace [A-Za-z_]\w*\Z)|(\Aquit\Z)|(\Amem\Z)")
  while True:
    global current_address
    cmd = input(">> ").strip()

    #Catch incorrect syntax
    if syntax.match(cmd) is None:
      print("Wrong expression!!\n <code syntax>\n")
      print((" next\n"
             " next <integer>\n"
             " print <ID>\n"
             " trace <ID>\n"
             " quit\n"))
      continue

    #instruction handler
    if (cmd[0:4] == "next"):
      if (len(cmd) == 4):
        line_num = 1
      else:
        line_num = int(cmd[5:])
      
      for i in range(line_num):
        if program_end:
          break
        
        if debug:
          print("line", main_flow.lineno, main_flow.statement)

        try:
          if (main_flow.statement is None):
            prev_scope = None
            for j in range(len(Scope_list)):
              if main_flow.lineno == Scope_list[j].start_line:
                scope_copy = copy.deepcopy(Scope_list[j])
                prev_scope = current_scope
                current_scope = scope_copy
                if debug:
                  print("Change scope to", current_scope)
                if jump_to_new_func:
                  # save parameter to new symbol_table
                  params = func_table[new_func]['param_list']
                  for k in range(func_table[new_func]['param_num']):
                    if type(params[k][1]) is tuple:
                      current_scope.symbol_table[params[k][1][1]] = {'address': current_address, 'type': params[k][0]+"arr", 'value':[param_pass[k]], 'history':[(main_flow.lineno, param_pass_addr.pop(0))]}
                      current_address += 4
                    else:
                      current_scope.symbol_table[params[k][1]] = {'address': current_address, 'type':params[k][0] , 'value':[param_pass[k]], 'history':[(main_flow.lineno, param_pass[k])]}
                      current_address += 4
                  if debug:
                    current_scope.print_symboltable()
                  jump_to_new_func = False
                else:
                  current_scope.parent_scope = prev_scope
                break
              elif main_flow.lineno == Scope_list[j].end_line:
                prev_scope = current_scope
                current_scope = current_scope.parent_scope
                if debug:
                  print("Change scope to", current_scope)
                break
            main_flow = main_flow.next_node
            
            if (main_flow is None):
              current_scope = prev_scope
              print("End of program")
              program_end = True

          elif main_flow.statement[0] == 'declare':
            for j in range(len(main_flow.statement[2])):
              if type(main_flow.statement[2][j]) is tuple:  
                if (main_flow.statement[2][j][0] == 'TIMES'):  # declaration of pointer
                  current_scope.symbol_table[main_flow.statement[2][j][1]] = {"address": current_address, "type":main_flow.statement[1]+"ptr", "value":[None], "size":0, "history": [(main_flow.statement[-1], 'N/A')]}
                  current_address += 4
                else:    # declaration of array
                  current_scope.symbol_table[main_flow.statement[2][j][0]] = {"address": current_address, "type":main_flow.statement[1]+"arr", "value":[None], "size":int(main_flow.statement[2][j][1]), "value":[['N/A' for k in range(int(main_flow.statement[2][j][1]))]], "history": [(main_flow.statement[-1], current_address)]}
                  current_address += 4 * int(main_flow.statement[2][j][1])
              else:
                current_scope.symbol_table[main_flow.statement[2][j]] = {"address": current_address, "type":main_flow.statement[1], "value":[None], "history": [(main_flow.statement[-1], 'N/A')]}
                current_address += 4
            if debug:
              current_scope.print_symboltable()
            main_flow = main_flow.next_node

          elif main_flow.statement[0] == 'assign':
            assign_value(main_flow.statement[1], main_flow.statement[3], current_scope, main_flow.statement[-1])
            if debug:
              current_scope.print_symboltable()
              current_scope.parent_scope.print_symboltable()
            if jump_to_new_func == False:
              main_flow = main_flow.next_node

          elif main_flow.statement[0] == 'FOR':
            if main_flow.visited:
              if main_flow.statement[4][0] in current_scope.symbol_table.keys():
                if main_flow.statement[4][1] == '++':
                  assign_value(main_flow.statement[4][0], get_value(main_flow.statement[4][0],current_scope)+1, current_scope, main_flow.statement[4][2])
                elif main_flow.statement[4][1] == '--':
                  assign_value(main_flow.statement[4][0], get_value(main_flow.statement[4][0],current_scope)-1, current_scope, main_flow.statement[4][2])
              #assign_value(main_flow.statement[4][0], get_value(main_flow.statement[4][0],current_scope)+1, current_scope, main_flow.statement[2][-1])
              if (get_value(main_flow.statement[3][0], current_scope) < get_value(main_flow.statement[3][2],current_scope)):
                main_flow = main_flow.next_node_branch
              else:
                main_flow.visited = False
                main_flow = main_flow.next_node
            else:
              assign_value(main_flow.statement[2][1], main_flow.statement[2][3], current_scope, main_flow.statement[2][-1])
              main_flow.visited = True
              if (calc_value(main_flow.statement[3], current_scope)):
                main_flow = main_flow.next_node_branch
              else:
                main_flow = main_flow.next_node
            
            if debug:
              current_scope.print_symboltable()

          elif main_flow.statement[0] == 'IF':
            if main_flow.visited:
              main_flow.visited = False
              main_flow = main_flow.next_node
            else:
              main_flow.visited = True
              if calc_value(main_flow.statement[2], current_scope):
                main_flow = main_flow.next_node_branch
              else:
                if main_flow.next_node_branch2 is not None:
                  main_flow = main_flow.next_node_branch2
                else:
                  main_flow.visited = False
                  main_flow = main_flow.next_node

          elif main_flow.statement[0] == 'WHILE':
            if calc_value(main_flow.statement[2], current_scope):
              main_flow = main_flow.next_node_branch
            else:
              main_flow = main_flow.next_node

          elif main_flow.statement[0] == 'RETURN':
            ret_val = calc_value(main_flow.statement[1], current_scope)
            ret_addr = flow_stack.pop()
            main_flow = ret_addr[0]
            current_scope = ret_addr[1]

          elif main_flow.statement[0] == 'printf':
            print_string = None
            if "%f" in main_flow.statement[1][0]:
              print_string = main_flow.statement[1][0][1:-1].replace('%f', str(calc_value(main_flow.statement[1][1], current_scope)))
            elif "%d" in main_flow.statement[1][0]:
              print_string = main_flow.statement[1][0][1:-1].replace('%d', str(calc_value(main_flow.statement[1][1], current_scope)))
            else:  # printf(const char*)
              print_string = main_flow.statement[1][0][1:-1]
            print(print_string.replace(r'\n', '\n'), end="")
            main_flow = main_flow.next_node

          elif main_flow.statement[0] == 'free':
            memory.free(int(current_scope.symbol_table[main_flow.statement[1][0]]['value']))
            current_scope.symbol_table[main_flow.statement[1][0]]['history'].append((main_flow.lineno, 'N/A'))
            del current_scope.symbol_table[main_flow.statement[1][0]]['value']
            main_flow = main_flow.next_node
          
          elif main_flow.statement[0] in current_scope.symbol_table.keys():
            if main_flow.statement[1] == '++':
              assign_value(main_flow.statement[0], get_value(main_flow.statement[0],current_scope)+1, current_scope, main_flow.statement[2])
            elif main_flow.statement[1] == '--':
              assign_value(main_flow.statement[0], get_value(main_flow.statement[0],current_scope)-1, current_scope, main_flow.statement[2])
            main_flow = main_flow.next_node
        except:
          print("Run-time error: line", main_flow.lineno)
          isError=True
          break
        if isError:
          break
      
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
    elif (cmd[0:3] == "mem"):
      print("Dynamic allocation : {}, {}".format(memory.num_used_fragment, memory.total_memory - memory.free_memory))
    else:
      print("Exception!")
    if isError:
      break



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
          cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2], cur_node)
        elif (stat_list[statement_idx][0] == 'IF'):
          cur_node.statement = stat_list[statement_idx][0:4]
          if len(stat_list[statement_idx][-1]) >= 3:
            cur_node.next_node_branch2 = make_flow_branch(stat_list[statement_idx][5:], stat_list[statement_idx][-1][2:], stat_list[statement_idx][-2], cur_node)
            cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1][0:2], stat_list[statement_idx][4], cur_node)
          else:
            cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2], cur_node)
        elif (stat_list[statement_idx][0] == 'WHILE'):
          cur_node.statement = stat_list[statement_idx][0:4]
          cur_node.next_node_branch = make_flow_branch(stat_list[statement_idx], stat_list[statement_idx][-1], stat_list[statement_idx][-2], cur_node)
        j = stat_list[statement_idx][-1][-1]
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
        elif (stat_list[statement_idx][0] == 'WHILE'):
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

def calc_value(val_val, cur_scope):
  global jump_to_new_func
  if type(val_val) is not tuple:
    if type(val_val) is int:
      return val_val
    elif type(val_val) is float:
      return val_val
    elif re.match(r'^-?\d+(?:\.\d+)?$', val_val) is not None:
      if val_val.count('.') == 0:
        return int(val_val)
      else:
        return float(val_val)
    elif type(val_val) is str:
      result = get_value(val_val, cur_scope)
      if type(result) == list and jump_to_new_func:
        param_pass_addr.append(get_address(val_val, cur_scope))
      return result
  else:
    if len(val_val) == 3 and val_val[1] == '*':
      return calc_value(val_val[0], cur_scope) * calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '+':
      return calc_value(val_val[0], cur_scope) + calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '-':
      return calc_value(val_val[0], cur_scope) - calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '/':
      return calc_value(val_val[0], cur_scope) / calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '<':
      return calc_value(val_val[0], cur_scope) < calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '>':
      return calc_value(val_val[0], cur_scope) > calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '<=':
      return calc_value(val_val[0], cur_scope) <= calc_value(val_val[2], cur_scope)
    elif len(val_val) == 3 and val_val[1] == '>=':
      return calc_value(val_val[0], cur_scope) >= calc_value(val_val[2], cur_scope)
    elif len(val_val) == 2 and val_val[0] == '&':
      return get_value(val_val, cur_scope)
    elif len(val_val) == 2 and val_val[0] in func_table.keys():  # function call
      global ret_val
      if ret_val == None:
        global main_flow, current_scope,flow_stack
        flow_stack.append((main_flow, current_scope))
        func_flow_copy = copy.deepcopy(func_table[val_val[0]]['flow_graph'])
        main_flow = func_flow_copy
        jump_to_new_func = True
        global new_func
        new_func = val_val[0]
        global param_pass
        param_pass = [calc_value(val_val[1][k], cur_scope) for k in range(len(val_val[1]))]
        if debug:
          print(param_pass)
        return 0
      else:
        ret_val_copy = ret_val
        ret_val = None
        return ret_val_copy
    elif val_val[0] == "malloc":
      ret_address, break_table = memory.malloc(int(val_val[1][0]))

      # Update reference if compaction was used
      if break_table:
        for original_address, new_address in break_table:
          for val_name, val_val in current_scope.symbol_table.items():
            if 'value' in val_val and val_val['value'] == original_address:
              target_name = val_name
              break

          assign_value(target_name, new_address, cur_scope, main_flow.lineno)

      return ret_address
      # assign_value(, ret_address, cur_scope, )

    else:   # array 접근
      return get_value(val_val, cur_scope)

def get_value(val_name, cur_scope):
  if type(val_name) is tuple:  # In case of address (&a) / In case of array
    if val_name[0] == '&':
      return cur_scope.symbol_table[val_name[1]]['value']
    elif (val_name[0] in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name[0]]['value'][0][get_value(val_name[1], cur_scope)]
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_value(val_name, cur_scope.parent_scope)
  elif isNum(val_name):
    return float(val_name)
  else:
    if (val_name in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name]['value'][0]
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_value(val_name, cur_scope.parent_scope)

def get_address(val_name, cur_scope):
  if type(val_name) is tuple:  # In case of array
    if (val_name[0] in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name[0]]['address']
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_address(val_name, cur_scope.parent_scope)
  else:
    if (val_name in cur_scope.symbol_table.keys()):
      return cur_scope.symbol_table[val_name]['address']
    else:
      if cur_scope.parent_scope is None:
        return None
      else:
        return get_address(val_name, cur_scope.parent_scope)

def print_value(val_name, cur_scope):
  if (val_name in cur_scope.symbol_table.keys()):
    if 'ptr' in cur_scope.symbol_table[val_name]['type'] or 'arr' in cur_scope.symbol_table[val_name]['type']:
      v = cur_scope.symbol_table[val_name]['history'][-1][1]
      if type(v) == int:
        v = hex(v)
      print(v)
    else:
      print(cur_scope.symbol_table[val_name]['history'][-1][1])
  elif val_name.endswith(']'):
    s = val_name.index('[')
    e = val_name.index(']')
    name = val_name[:s]
    index = int(val_name[s+1:e])
    if (name in cur_scope.symbol_table.keys()):
      if index < cur_scope.symbol_table[name]['size']:
        print(cur_scope.symbol_table[name]['value'][0][index])
      else:
        print(f"List index out of range: variable {name} has size {cur_scope.symbol_table[name]['size']}")
    elif cur_scope.parent_scope is None:
      print("Invisible variable: ", name)
    else:
      print_value(val_name, cur_scope.parent_scope)
  else:
    if cur_scope.parent_scope is None:
      print("Invisible variable: ", val_name)
    else:
      print_value(val_name, cur_scope.parent_scope)

def print_trace(val_name, cur_scope):
  if (val_name in cur_scope.symbol_table.keys()):
    trace_list = cur_scope.symbol_table[val_name]['history']
    if 'ptr' in cur_scope.symbol_table[val_name]['type'] or 'arr' in cur_scope.symbol_table[val_name]['type']:
      for i in range(len(trace_list)):
        v = trace_list[i][1]
        if type(v) == int:
          v = hex(v)
        print(val_name, "=", v, "at line", trace_list[i][0])
    else:
      for i in range(len(trace_list)):
        print(val_name, "=", trace_list[i][1], "at line", trace_list[i][0])
  else:
    if cur_scope.parent_scope is None:
      print("Invisible variable: ", val_name)
    else:
      print_trace(val_name, cur_scope.parent_scope)

def assign_value(val_name, val_val, cur_scope, lineno):
  global isError
  if type(val_name) is tuple:  # Assign in pointer (*a) / Assign in array
    if val_name[0] == '*':
      cur_scope.symbol_table[val_name[1]]['value'][0][0] = calc_value(val_val, cur_scope)
      cur_scope.symbol_table[val_name[1]]['reference_history'].append((lineno, cur_scope.symbol_table[val_name[1]]['value'][0][0]))
    elif (val_name[0] in cur_scope.symbol_table.keys()):
      cur_scope.symbol_table[val_name[0]]['value'][0][calc_value(val_name[1] ,cur_scope)] = calc_value(val_val, cur_scope)
      # if cur_scope.symbol_table[val_name[0]]['value'][calc_value(val_name[1] ,cur_scope)] is not None:
      #   cur_scope.symbol_table[val_name[0]]['history'].append((lineno, cur_scope.symbol_table[val_name[0]]['value']))
    else:
      if cur_scope.parent_scope is None:
        #print("Invisible variable: ", val_name)
        print("Syntax error: line", lineno)
        isError=True
      else:
        assign_value(val_name, val_val, cur_scope.parent_scope, lineno)
  else:
    if (val_name in cur_scope.symbol_table.keys()):
      if 'ptr' in cur_scope.symbol_table[val_name]['type'] or 'arr' in cur_scope.symbol_table[val_name]['type']: # assign to pointer(array)
        if type(val_val) is tuple: # pointer = &variable form
          cur_scope.symbol_table[val_name]['value'] = [calc_value(val_val, cur_scope)]
          cur_scope.symbol_table[val_name]['size'] = 1
          cur_scope.symbol_table[val_name]['reference_history'] = cur_scope.symbol_table[val_val[1]]['history']
          if jump_to_new_func == False:
            cur_scope.symbol_table[val_name]['history'].append((lineno, cur_scope.symbol_table[val_val[1]]['address']))
        else: # pointer = pointer form
          cur_scope.symbol_table[val_name]['value'][0] = calc_value(val_val, cur_scope)
          cur_scope.symbol_table[val_name]['size'] = cur_scope.symbol_table[val_val]['size']
          if 'reference_history' in cur_scope.symbol_table[val_val].keys():
            cur_scope.symbol_table[val_name]['reference_history'] = cur_scope.symbol_table[val_val]['reference_history']
          if jump_to_new_func == False:
            cur_scope.symbol_table[val_name]['history'].append((lineno, cur_scope.symbol_table[val_val]['history'][-1][1]))
          
      else:
        cur_scope.symbol_table[val_name]['value'][0] = calc_value(val_val, cur_scope)
        if jump_to_new_func == False:
          cur_scope.symbol_table[val_name]['history'].append((lineno, cur_scope.symbol_table[val_name]['value'][0]))
    else:
      if cur_scope.parent_scope is None:
        #print("Invisible variable: ", val_name)
        print("Syntax error: line", lineno)
        isError=True
      else:
        assign_value(val_name, val_val, cur_scope.parent_scope, lineno)

def isNum(n):
  try:
    float(n)
    return True
  except:
    return False

if __name__ == "__main__":
  interpreter(input_path='exampleInput.c', debugging=False)


## Traverse flow graph (for debugging)

# func_name = input("Name of function >> ")
# if func_name in func_table.keys():
#   trav_sub = func_table[func_name]['flow_graph']

# while (1):
#   cmd = input(">> ")
#   if (cmd[0:8] == "printnb2") :
#     print(trav_sub.next_node_branch2)
#   elif (cmd[0:7] == "printnb") :
#     print(trav_sub.next_node_branch)
#   elif (cmd[0:6] == "printn"):
#     print(trav_sub.next_node)
#   elif (cmd[0:5] == "print"):
#     print(trav_sub)
#   elif (cmd[0:5] == "nextb2"):
#     trav_sub = trav_sub.next_node_branch2
#     print(trav_sub)
#   elif (cmd[0:5] == "nextb"):
#     trav_sub = trav_sub.next_node_branch
#     print(trav_sub)
#   elif (cmd[0:4] == "next"):
#     trav_sub = trav_sub.next_node
#     print(trav_sub)
#   elif (cmd[0:6] == "change"):
#     func_name = input("Name of function >> ")
#     if func_name in func_table.keys():
#       trav_sub = func_table[func_name]['flow_graph']
#   elif (cmd[0:4] == "quit"):
#     break
#   else:
#     pass
  