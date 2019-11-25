import ply.lex as lex

# Reserved words
reserved = (
    'BREAK', 'CHAR', 'DOUBLE', 'ELSE', 'FLOAT', 'FOR', 'IF', 'INT', 'LONG',
    'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'UNSIGNED', 'VOID', 'WHILE',
)

tokens = reserved + (
    # Literals (identifier, integer constant, float constant, string constant,
    # char const)
    'ID', 'ICONST', 'FCONST', 'SCONST', 'CCONST',
    # 'ID', 'TYPEID', 'ICONST', 'FCONST', 'SCONST', 'CCONST',

    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
    'LSHIFTEQUAL', 'RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',

    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',

    # Structure dereference (->)
    'ARROW',

    # Conditional operator (?)
    'CONDOP',

    # Delimeters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'SEMI', 'COLON',

    # Ellipsis (...)
    'ELLIPSIS',
)

# Completely ignored characters
t_ignore = ' \t\x0c'

# Newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    # t.lexer.lineno += len(t.value)

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_OR = r'\|'
t_AND = r'&'
t_NOT = r'~'
t_XOR = r'\^'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_LOR = r'\|\|'
t_LAND = r'&&'
t_LNOT = r'!'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='

# Assignment operators
t_EQUALS = r'='
t_TIMESEQUAL = r'\*='
t_DIVEQUAL = r'/='
t_MODEQUAL = r'%='
t_PLUSEQUAL = r'\+='
t_MINUSEQUAL = r'-='
t_LSHIFTEQUAL = r'<<='
t_RSHIFTEQUAL = r'>>='
t_ANDEQUAL = r'&='
t_OREQUAL = r'\|='
t_XOREQUAL = r'\^='

# Increment/decrement
t_PLUSPLUS = r'\+\+'
t_MINUSMINUS = r'--'

# ->
t_ARROW = r'->'

# ?
t_CONDOP = r'\?'

# Delimeters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_PERIOD = r'\.'
t_SEMI = r';'
t_COLON = r':'
t_ELLIPSIS = r'\.\.\.'

# Identifiers and reserved words
reserved_map = {}
for r in reserved:
    reserved_map[r.lower()] = r


def t_ID(t):
    r'[A-Za-z_][\w_]*'
    t.type = reserved_map.get(t.value, "ID")
    return t


# Integer literal
t_ICONST = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

# Floating literal
t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

# String literal
t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_CCONST = r'(L)?\'([^\\\n]|(\\.))*?\''

# Comments
def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    return t

# Preprocessor directive (ignored)
def t_preprocessor(t):
    r'\#(.)*?\n'
    t.lexer.lineno += 1

# Error handling rule
def t_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

#===============================================
def clex():
    '''
    It returns clex 
    '''
    return lex.lex()

def scope_list_ext(input_path=".c"):
    '''
    Read file and return scope list that the first value indicate global scope and other scopes are incrementally ordered.
    '''
    ## step 1: Build the lexer
    lexer = lex.lex()

    ## step 2: read file
    with open(input_path,'r') as input_file:
        input_string = input_file.read()

    ## step 3: tokenize the input and return end of file
    lexer.input(input_string)

    stack_for_scope = [1]
    scope_list = []
    
    while True:
        tok = lexer.token()
        if not tok:    
            scope_list.sort()
            scope_list.insert(0,(stack_for_scope.pop(), lexer.lineno))
            break

        if tok.value == '{':
            stack_for_scope.append(tok.lineno)
        elif tok.value == '}':
            scope_list.append((stack_for_scope.pop(), tok.lineno))

    return scope_list

def clex_test(input_path="exampleInput.c",output_path="token_list.txt"):

    ## step 1: Build the lexer
    lexer = lex.lex()

    ## step 2: read file
    with open(input_path,'r') as input_file:
        input_string = input_file.read()

    ## step 3: tokenize the input
    lexer.input(input_string)

    toks = []
    stack_for_scope = [1]
    scope_list = []
    
    while True:
        tok = lexer.token()
        if not tok:
            scope_list.append((stack_for_scope.pop(), lexer.lineno))
            break      # No more input
        toks.append(tok)
        if tok.value == '{':
            stack_for_scope.append(tok.lineno)
        elif tok.value == '}':
            scope_list.append((stack_for_scope.pop(), tok.lineno))

    scope_list.sort()
    ## step 4: write results
    with open(output_path,'w') as output_file:
        output_file.write('\n'.join(map(lambda x:str(x),toks)))
        output_file.write('\n\n'+'-'*50+'\n\n'+'<scope>\n')
        output_file.write('\n'.join(map(lambda x:str(x),scope_list)))
    

if __name__ == "__main__":
    clex_test()