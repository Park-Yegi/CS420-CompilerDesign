class Memory():
  def __init__(self):
    self.total_memory = 1024
    self.free_memory = 1024
    self.num_used_fragment = 0
    self.root_fragment = Fragment(1024, 1024, True, None, None, None)

  def malloc(self, size, scope):
    if size > self.free_memory:
      print("Out of memory")
      return "OOM", None
    

    best_fragment = self.find_best_fragment(size)
    break_table = None
    if best_fragment == None:
      # print('compaction')
      break_table = self.compaction()
      best_fragment = self.find_best_fragment(size)
    
    if best_fragment.size != size:
      new_fragment = Fragment(best_fragment.size-size, best_fragment.address+size, True, best_fragment, best_fragment.child, None)
      if best_fragment.child is not None:
        best_fragment.child.parent = new_fragment
      best_fragment.child = new_fragment
      best_fragment.size = size
    
    self.free_memory -= size
    self.num_used_fragment += 1
    best_fragment.is_free = False
    best_fragment.scope = scope

    return best_fragment.address, break_table

  def find_best_fragment(self, size):
    fragment_candidate = self.root_fragment
    best_fragment = None
    while(fragment_candidate is not None and (not fragment_candidate.is_free or fragment_candidate.size < size)):
      fragment_candidate = fragment_candidate.child
    
    if fragment_candidate == None:
      return None

    best_fragment = fragment_candidate
    while(fragment_candidate is not None):
      if fragment_candidate.is_free and fragment_candidate.size >= size and fragment_candidate.size < best_fragment.size:
        best_fragment = fragment_candidate
      fragment_candidate = fragment_candidate.child
    
    return best_fragment

  def free(self, address):
    self.num_used_fragment -= 1

    target_fragment = self.root_fragment
    while(target_fragment.address != address):
      target_fragment = target_fragment.child
    self.free_memory += target_fragment.size
    target_scope = target_fragment.scope
    target_fragment.scope = None

    target_parent_fragment = target_fragment.parent
    
    if target_parent_fragment is not None and target_parent_fragment.is_free:
      target_parent_fragment.size += target_fragment.size
      target_parent_fragment.child = target_fragment.child
      target_fragment.child.parent = target_parent_fragment
      target_fragment = target_parent_fragment
    
    if target_fragment.child is not None and target_fragment.child.is_free:
      target_fragment.size += target_fragment.child.size
      target_fragment.child = target_fragment.child.child
      if target_fragment.child is not None:
        target_fragment.child.parent = target_fragment

    target_fragment.is_free = True
    return target_scope

  def compaction(self):
    print("Defragmentation operated")
    break_table = []
    target_free_fragment = self.root_fragment
    while not target_free_fragment.is_free:
      target_free_fragment = target_free_fragment.child
    
    free_address = target_free_fragment.address
    target_allocated_fragment = target_free_fragment.child
    
    while target_allocated_fragment:
      if not target_allocated_fragment.is_free:
        # print('{} -> {}'.format(target_allocated_fragment.address, free_address))
        break_table.append([target_allocated_fragment.scope, target_allocated_fragment.address, free_address])
        # Update reference!

        target_allocated_fragment.address = free_address
        free_address += target_allocated_fragment.size

        parent_fragment = target_allocated_fragment.parent
        if parent_fragment.is_free:
          if parent_fragment.parent:
            parent_fragment.parent.child = target_allocated_fragment
            target_allocated_fragment.parent = parent_fragment.parent
          else:
            target_allocated_fragment.parent = None
            self.root_fragment = target_allocated_fragment
        last_fragment = target_allocated_fragment
              
      target_allocated_fragment = target_allocated_fragment.child
    
    new_free_fragment = Fragment(self.free_memory, free_address, True, last_fragment, None, None)
    last_fragment.child = new_free_fragment
    
    return break_table

  def mem(self):
    print(self.num_used_fragment, self.total_memory-self.free_memory)
      
    fragment = self.root_fragment
    while(fragment):
      print(fragment)
      fragment = fragment.child

class Fragment():
  def __init__(self, size, address, is_free, parent, child, scope):
    self.size = size
    self.address = address
    self.is_free = is_free
    self.parent = parent
    self.child = child
    self.scope = scope

  def __str__(self):
    return_str = 'address : {}, size : {}, is_free : {}, parent : '.format(self.address, self.size, self.is_free)
    if self.parent is None:
        return_str += 'x'
    else:
        return_str += str(self.parent.address)
    return return_str

def compute_static_allocation(result):

  var_cnt = 0
  for func in result:
    if type(func[3][0]) is tuple:
      for var in func[3]:
        if type(var[1]) is tuple and isNum(var[1][1]):
          var_cnt += int(var[1][1])
        else:
          var_cnt += 1
      # print(func[3])

    for command in func[4]:
      if command[0] == 'declare':
        for var in command[2]:
          if type(var) is tuple and isNum(var[1]):
            var_cnt += int(var[1])
          else:
            var_cnt += 1
        # print(command[2])
        # var_cnt += len(command[2])
  print("Static allocation : {}, {}".format(var_cnt, 4*var_cnt))

def isNum(n):
  try:
    float(n)
    return True
  except:
    return False

  # print(result)


# if __name__ == '__main__':
#     memory = Memory()
#     while True:
#         inp = input(">> ").split()
#         if len(inp) == 2:
#             if inp[0] == 'malloc':
#                 memory.malloc(int(inp[1]))
#             elif inp[0] == 'free':
#                 memory.free(int(inp[1]))

#         elif len(inp) == 1:
#             if inp[0] == 'mem':
#                 memory.mem()