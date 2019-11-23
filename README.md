예제 테스트 실행 방법: 각각의 clex, cparse_revised, interpreter 파일을 직접 실행하면 "exampleInput.c"를 활용하여 실행 결과를 보여준다. "if __name__=='__main__':" 아래에서 실행되는 함수의 변수를 수정하면 debug 모드에 진입하거나 다른 소스 코드에 대한 결과도 쉽게 볼 수 있다.


# Function explanation
This is brief description of functions available. Functions used for testing like clex.clex_test is not dealt since we don't use it for implementation, and their codes are understandable.
## clex 
**1. clex : None -> lex.lex()**
```
It returns "lex".
```
*example*
```python
>> from clex import clex 
>> lexer = clex()
>> lexer.input("30")
>> lexer.token()

 LexToken(ICONST,'30',1,0)
```
**2. scope_list_ext : (input_path="exampleInput.c") -> list**
```
It retuns list of scopes for given input file. The first elements of the result is global scope, and other scopes are in incremental order. 
```
### cparse_revised
**1. cparse : None -> yacc.yacc**
```
It returns "parser".
```
*example*
```python
>> from clex import clex
>> from cparse_revised import cparse
>> input_string='''int main(void){
... 3+3;} '''
>> parser.parse(input=input_string,lexer=clex(),tracking=True)

[('func', 'int', 'main', ['void'], [('3', '+', '3')], (1, 2))]
```
## cinterp
**1. interpreter : (input_path="exampleInput.c",debugging=False) -> None**
```
It read file and execute interpreter. If debugging=True, debugging mode is activated. There are two steps; preprocessing of input string and main loop.
 In preprocessing step, AST, function table, and symbol tables are created and also global variables are declared. Then main loop takes user's instruction and do corresponding jobs.
```
---
# Issues & task
1. void handler(issue)
```python
>> input_string='''int main(void){3+3;}'''
>> parser.parse(input=input_string,lexer=clex(),tracking=True)

[('func', 'int', 'main', ['void'], [('3', '+', '3')], (1, 1))]
>> input_string='''int main(){3+3;}'''
>> parser.parse(input=input_string,lexer=clex(),tracking=True)

[('func', 'int', 'm', 'a', [('3', '+', '3')], (1, 1))]
```
