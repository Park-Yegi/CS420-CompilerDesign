# -----------------------------------------------------------------------------
# cparse.py
#
# Simple parser for ANSI C.  Based on the grammar in K&R, 2nd Ed.
# -----------------------------------------------------------------------------

import sys
import clex
from clex import clex,tokens
import ply.yacc as yacc

# translation-unit:
def p_translation_unit(t):
    """ translation_unit : external_declaration
                         | translation_unit external_declaration """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[1].extend(t[2])
        t[0] = t[1]


# external-declaration:
def p_external_declaration_1(t):
    """ external_declaration : function_definition """
    t[0] = [t[1]]

def p_external_declaration_2(t):
    """ external_declaration : declaration """
    t[0] = t[1]

def p_function_definition(t):
    """ function_definition : type_specifier declarator compound_statement """
    # t[1]: function return type
    # t[2][0]: function name
    # t[2][1]: function parameter type and name
    # t[3]: statements in the function
    t[0] = ('func', t[1], t[2][0], t[2][1], t[3], (t.linespan(3)[0], t.linespan(3)[1]))

# type-specifier:
def p_type_specifier(t):
    """ type_specifier : VOID
                      | CHAR
                      | SHORT
                      | INT
                      | LONG
                      | FLOAT
                      | DOUBLE
                      | SIGNED
                      | UNSIGNED
    """
    t[0] = t[1]


# declarator:
def p_declarator_1(t):
    """ declarator : pointer direct_declarator """
    t[0] = (t[1], t[2])

def p_declarator_2(t):
    """ declarator : direct_declarator """
    t[0] = t[1]


# pointer:
def p_pointer_1(t):
    """ pointer : TIMES """
    t[0] = 'TIMES'

def p_pointer_2(t):
    """ pointer : TIMES pointer """
    t[0] = ('TIMES', t[2])


# direct-declarator:
def p_direct_declarator_1(t):
    """ direct_declarator : ID """
    t[0] = t[1]

def p_direct_declarator_2(t):
    """ direct_declarator : LPAREN declarator RPAREN """
    t[0] = t[2]

def p_direct_declarator_3(t):
    """ direct_declarator : direct_declarator LBRACKET constant_expression RBRACKET """
    t[0] = (t[1], t[3])

def p_direct_declarator_4(t):
    """ direct_declarator : direct_declarator LBRACKET RBRACKET """
    t[0] = t[1]

def p_direct_declarator_5(t):
    """ direct_declarator : direct_declarator LPAREN parameter_type_list RPAREN """
    t[0] = (t[1], t[3])

def p_direct_declarator_6(t):
    """ direct_declarator : direct_declarator LPAREN identifier_list RPAREN """
    t[0] = (t[1], t[3])

def p_direct_declarator_7(t):
    """ direct_declarator : direct_declarator LPAREN RPAREN """
    t[0] = (t[1],['void'])


# constant-expression
def p_constant_expression(t):
    """ constant_expression : conditional_expression """
    t[0] = t[1]

# conditional-expression
def p_conditional_expression(t):
    """ conditional_expression : logical_or_expression
                               | logical_or_expression CONDOP expression COLON conditional_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'CONDOP', t[3], 'COLON', t[5])    

# logical-or-expression
def p_logical_or_expression(t):
    """ logical_or_expression : logical_and_expression
                              | logical_or_expression LOR logical_and_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'LOR', t[3])

# logical-and-expression
def p_logical_and_expression(t):
    """ logical_and_expression : inclusive_or_expression
                               | logical_and_expression LAND inclusive_or_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'LAND', t[3])

# inclusive-or-expression:
def p_inclusive_or_expression(t):
    """ inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression OR exclusive_or_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'OR', t[3])

# exclusive-or-expression:
def p_exclusive_or_expression(t):
    """ exclusive_or_expression :  and_expression
                                |  exclusive_or_expression XOR and_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'XOR', t[3])

# AND-expression
def p_and_expression(t):
    """ and_expression : equality_expression
                       | and_expression AND equality_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], 'AND', t[3])

# equality-expression:
def p_equality_expression(t):
    """ equality_expression : relational_expression
                            | equality_expression EQ relational_expression
                            | equality_expression NE relational_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2], t[3])

# relational-expression:
def p_relational_expression(t):
    """ relational_expression : shift_expression
                              | relational_expression LT shift_expression
                              | relational_expression GT shift_expression
                              | relational_expression LE shift_expression
                              | relational_expression GE shift_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2], t[3])

# shift-expression
def p_shift_expression(t):
    """ shift_expression : additive_expression
                         | shift_expression LSHIFT additive_expression
                         | shift_expression RSHIFT additive_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2], t[3])

# additive-expression
def p_additive_expression(t):
    """ additive_expression : multiplicative_expression
                            | additive_expression PLUS multiplicative_expression
                            | additive_expression MINUS multiplicative_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2], t[3])

# multiplicative-expression
def p_multiplicative_expression(t):
    """ multiplicative_expression : cast_expression
                                  | multiplicative_expression TIMES cast_expression
                                  | multiplicative_expression DIVIDE cast_expression
                                  | multiplicative_expression MOD cast_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2], t[3])


# cast-expression:
def p_cast_expression(t):
    """ cast_expression : unary_expression
                        | LPAREN type_name RPAREN cast_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = ('TYPECAST', t[2], t[4])

# unary-expression:
def p_unary_expression_1(t):
    """ unary_expression : postfix_expression """
    t[0] = t[1]

def p_unary_expression_2(t):
    """ unary_expression : PLUSPLUS unary_expression
                         | MINUSMINUS unary_expression
                         | unary_operator cast_expression """
    t[0] = (t[1], t[2])

def p_unary_expression_3(t):
    """ unary_expression : SIZEOF unary_expression
                         | SIZEOF LPAREN type_name RPAREN """
    if len(t) == 3:
        t[0] = ('SIZEOF', t[2])
    else:
        t[0] = ('SIZEOF', t[3])


# postfix-expression:
def p_postfix_expression_1(t):
    """ postfix_expression : primary_expression """
    t[0] = t[1]

def p_postfix_expression_2(t):
    """ postfix_expression : postfix_expression LBRACKET expression RBRACKET """
    t[0] = (t[1], t[3])

def p_postfix_expression_3(t):
    """ postfix_expression : postfix_expression LPAREN argument_expression_list RPAREN
                           | postfix_expression LPAREN RPAREN
    """
    if len(t) == 4:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[3])

def p_postfix_expression_4(t):
    """ postfix_expression : postfix_expression PERIOD ID
                           | postfix_expression ARROW ID 
    """ 
    t[0] = (t[1], t[2], t[3])

def p_postfix_expression_5(t):
    """ postfix_expression : postfix_expression PLUSPLUS
                           | postfix_expression MINUSMINUS
    """
    t[0] = (t[1], t[2])


# primary-expression:
def p_primary_expression(t):
    """ primary_expression : ID
                           | constant
                           | SCONST
                           | LPAREN expression RPAREN """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = t[2]

# constant:
def p_constant(t):
    """ constant : ICONST
                 | FCONST
                 | CCONST
    """
    t[0] = t[1]


# expression:
def p_expression(t):
    """ expression : assignment_expression
                   |  expression COMMA assignment_expression """
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[3])

# assigment_expression:
def p_assignment_expression(t):
    """ assignment_expression : conditional_expression
                              | unary_expression assignment_operator assignment_expression """
    if len(t) == 2:
        if len(t[1]) != 1 and t[1][0] == 'printf':
            t[0] = t[1] + (t.lineno(1), )
        elif len(t[1]) != 1 and t[1][0] == 'free':
            t[0] = t[1] + (t.lineno(1), )
        else:
            t[0] = t[1]
    else:
        t[0] = ('assign', t[1], t[2], t[3], t.lineno(1))

# assignment_operator:
def p_assignment_operator(t):
    """ assignment_operator : EQUALS
                            | TIMESEQUAL
                            | DIVEQUAL
                            | MODEQUAL
                            | PLUSEQUAL
                            | MINUSEQUAL
                            | LSHIFTEQUAL
                            | RSHIFTEQUAL
                            | ANDEQUAL
                            | OREQUAL
                            | XOREQUAL
    """
    t[0] = t[1]


# unary-operator
def p_unary_operator(t):
    """ unary_operator : AND
                       | TIMES
                       | PLUS 
                       | MINUS
                       | NOT
                       | LNOT 
    """
    t[0] = t[1]


# type-name:
def p_type_name_1(t):
    """ type_name : type_specifier abstract_declarator """
    t[0] = (t[1], t[2])
  
def p_type_name_2(t):
    """ type_name : type_specifier """
    t[0] = t[1]


# parameter-type-list:
def p_parameter_type_list_1(t):
    """ parameter_type_list : parameter_list """
    t[0] = t[1]

def p_parameter_type_list_2(t):
    """ parameter_type_list : parameter_list COMMA ELLIPSIS """
    t[0] = (t[1], 'ELLIPSIS')


# parameter-list:
def p_parameter_list_1(t):
    """ parameter_list : parameter_declaration """
    t[0] = [t[1]]

def p_parameter_list_2(t):
    """ parameter_list : parameter_list COMMA parameter_declaration """
    t[0] = t[1] + [t[3]]


# parameter-declaration:
def p_parameter_declaration_1(t):
    """ parameter_declaration : type_specifier declarator """
    t[0] = (t[1], t[2])

def p_parameter_declaration_2(t):
    """ parameter_declaration : type_specifier abstract_declarator """
    t[0] = (t[1], t[2])

def p_parameter_declaration_3(t):
    """ parameter_declaration : type_specifier """
    t[0] = t[1]


# abstract-declarator:
def p_abstract_declarator_1(t):
    """ abstract_declarator : pointer """
    t[0] = t[1]

def p_abstract_declarator_2(t):
    """ abstract_declarator : pointer direct_abstract_declarator """
    t[0] = (t[1], t[2])

def p_abstract_declarator_3(t):
    """ abstract_declarator : direct_abstract_declarator """
    t[0] = t[1]


# direct-abstract-declarator:
def p_direct_abstract_declarator_1(t):
    """ direct_abstract_declarator : LPAREN abstract_declarator RPAREN """
    t[0] = t[2]

def p_direct_abstract_declarator_2(t):
    """ direct_abstract_declarator : direct_abstract_declarator LBRACKET constant_expression RBRACKET """
    t[0] = (t[1], t[3])

def p_direct_abstract_declarator_3(t):
    """ direct_abstract_declarator : direct_abstract_declarator LBRACKET RBRACKET """
    t[0] = t[1]

def p_direct_abstract_declarator_4(t):
    """ direct_abstract_declarator : LBRACKET constant_expression RBRACKET """
    t[0] = t[2]

def p_direct_abstract_declarator_5(t):
    """ direct_abstract_declarator : LBRACKET RBRACKET """
    t[0] = None

def p_direct_abstract_declarator_6(t):
    """ direct_abstract_declarator : direct_abstract_declarator LPAREN parameter_type_list RPAREN """
    t[0] = (t[1], t[3])

def p_direct_abstract_declarator_7(t):
    """ direct_abstract_declarator : LPAREN parameter_type_list RPAREN """
    t[0] = t[2]


# declaration:
def p_declaration_1(t):
    """ declaration : type_specifier init_declarator_list SEMI """
    t[0] = ('declare' ,t[1], t[2], t.lineno(2))

def p_declaration_2(t):
    """ declaration : type_specifier SEMI """
    t[0] = ('declare', t[1], t.lineno(1))

# declaration-list:
def p_declaration_list_1(t):
    """ declaration_list : declaration """
    t[0] = [t[1]]

def p_declaration_list_2(t):
    """ declaration_list : declaration_list declaration """
    t[0] = t[1] + [t[2]]


# init-declarator
def p_init_declarator_1(t):
    """ init_declarator : declarator """
    t[0] = t[1]

def p_init_declarator_2(t):
    """ init_declarator : declarator EQUALS initializer """
    t[0] = (t[1], 'EQUALS', t[3])

# init-declarator-list:
def p_init_declarator_list(t):
    """ init_declarator_list : init_declarator
                             | init_declarator_list COMMA init_declarator
    """
    t[0] = t[1] + [t[3]] if len(t) == 4 else [t[1]]


# initializer:
def p_initializer_1(t):
    """ initializer : assignment_expression """
    t[0] = t[1]

def p_initializer_2(t):
    """ initializer : LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE """
    if t[2] is None:
        t[0] = ('EMPTY')
    else:
        t[0] = t[2]


# initializer-list:
def p_initializer_list_1(t):
    """ initializer_list : initializer """
    t[0] = [t[1]]

def p_initializer_list_2(t):
    """ initializer_list : initializer_list COMMA initializer """
    t[0] = t[1] + [t[3]]


# compound-statement:
def p_compound_statement_1(t):
    """ compound_statement : LBRACE declaration_list statement_list RBRACE """
    t[0] = t[2] + t[3]

def p_compound_statement_2(t):
    """ compound_statement : LBRACE statement_list RBRACE """
    t[0] = t[2]

def p_compound_statement_3(t):
    """ compound_statement : LBRACE declaration_list RBRACE """
    t[0] = t[2]

def p_compound_statement_4(t):
    """ compound_statement : LBRACE RBRACE """
    t[0] = []


# statement:
def p_statement(t):
    """ statement : expression_statement
                  | compound_statement
                  | selection_statement
                  | iteration_statement
                  | jump_statement
    """
    t[0] = t[1]

# statement-list:
def p_statement_list_1(t):
    """ statement_list : statement """
    t[0] = [t[1]]
    # t[0] = [t[1] + (t.lineno(1), )]

def p_statement_list_2(t):
    """ statement_list : statement_list statement """
    t[0] = t[1] + [t[2]]
    # t[0] = t[1] + [t[2] + (t.lineno(2), )]


# expression-statement:
def p_expression_statement(t):
    """ expression_statement : expression SEMI """
    if t[1] is None:
        t[0] = None
    else:
        t[0] = t[1]


# selection-statement
def p_selection_statement_1(t):
    """ selection_statement : IF LPAREN expression RPAREN statement """
    t[0] = ('IF', 'LPAREN', t[3], 'RPAREN', t[5], (t.linespan(5)[0], t.linespan(5)[1]))

def p_selection_statement_2(t):
    """ selection_statement : IF LPAREN expression RPAREN statement ELSE statement """
    t[0] = ('IF', 'LPAREN', t[3], 'RPAREN', t[5], 'ELSE', t[7], (t.linespan(5)[0], t.linespan(5)[1], t.linespan(7)[0], t.linespan(7)[1]))


# iteration_statement:
def p_iteration_statement_1(t):
    """ iteration_statement : WHILE LPAREN expression RPAREN statement """
    t[0] = ('WHILE', 'LPAREN', t[3], 'RPAREN', t[5], (t.linespan(5)[0], t.linespan(5)[1]))

def p_iteration_statement_2(t):
    """ iteration_statement : FOR LPAREN expression SEMI expression SEMI expression RPAREN statement """
    # """ iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement """
    t[0] = ('FOR', 'LPAREN', t[3], t[5], t[7], 'RPAREN', t[9], (t.linespan(9)[0], t.linespan(9)[1]))


# jump_statement:
def p_jump_statement_1(t):
    """ jump_statement : BREAK SEMI """
    t[0] = ('BREAK', t.lineno(1))

def p_jump_statement_2(t):
    """ jump_statement : RETURN expression SEMI """
    t[0] = ('RETURN', t[2], t.lineno(1))

def p_jump_statement_3(t):
    """ jump_statement : RETURN SEMI """
    t[0] = ('RETURN', t.lineno(1))


# argument-expression-list:
def p_argument_expression_list(t):
    """argument_expression_list : assignment_expression
                                | argument_expression_list COMMA assignment_expression
    """
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[1] + [t[3]]


# identifier-list:
def p_identifier_list_1(t):
    """ identifier_list : ID """
    t[0] = t[1]

def p_identifier_list_2(t):
    """ identifier_list : identifier_list COMMA ID """
    t[0] = t[1] + [t[3]]


def p_empty(t):
    'empty : '
    t[0] = None

def p_error(t):
    print("Syntax error: line", t.lineno)

#==============================================================

def cparse():
    '''
    It returns yacc object
    Return: yacc.yacc
    '''
    return yacc.yacc()

def cparse_test(input_path="exampleInput.c",output_path="parse_result.txt",debug=False):
    '''
    It reads file on input path, generate AST, and store it in output path.
    Param: input_path: path of input file
    Param: output_paht: path of storing the result
    Param: debug: If it's true, it print out the result on your screen
    '''
    ## step 1: read file
    with open(input_path,'r') as input_file:
        input_string=input_file.read()
    
    ## step 2: parse the input string
    parser=yacc.yacc()

    result=parser.parse(
        input=input_string,
        lexer=clex(),
        tracking=True
    )
    # pretty the output string        
    output_string=[]
    cnt=0
    for i in str(result):
        if i =="(":
            output_string.append('\n'+'    '*cnt)
            cnt+=1
        elif i ==")":
            cnt-=1
        output_string.append(i)

    ## step 3: write result
    with open(output_path,'w') as output_file:
        output_file.write(''.join(output_string))

    ## step 4(optional): print result
    if debug:
        print("** AST **")
        print(''.join(output_string))

if __name__ == "__main__":
    cparse_test(debug=True)