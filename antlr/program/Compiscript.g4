grammar Compiscript;

program         : declaration* EOF ;

declaration     : classDecl
                | funDecl
                | varDecl
                | statement ;

classDecl       : 'class' IDENTIFIER ('extends' IDENTIFIER)? '{' function* '}' ;
funDecl         : 'fun' function ;
varDecl         : 'var' IDENTIFIER ('=' expression)? ';' ;

statement       : exprStmt
                | forStmt
                | ifStmt
                | printStmt
                | inputStmt
                | returnStmt
                | whileStmt
                | breakStmt
                | continueStmt
                | block ;

breakStmt       : 'break' ';' ;
continueStmt    : 'continue' ';' ;

exprStmt        : expression ';' ;
forStmt         : 'for' '(' (varDecl | exprStmt | ';') expression? ';' expression? ')' statement ;
ifStmt          : 'if' '(' expression ')' statement ('else' statement)? ;
printStmt       : 'print' expression ';' ;
returnStmt      : 'return' expression? ';' ;
whileStmt       : 'while' '(' expression ')' statement ;
block           : '{' declaration* '}' ;
funAnon         : 'fun' '(' parameters? ')' block;
inputStmt       : input ';' ;

input: inputFloat | inputInt | inputString ;

inputFloat  : 'inputFloat' STRING ;
inputInt    : 'inputInt' STRING ;
inputString : 'inputString' STRING ',' NUMBER ;

expression      : assignment;

assignment      : (call '.')? IDENTIFIER '=' assignment
                | logic_or
                | input ;

logic_or        : logic_and ('or' logic_and)* ;
logic_and       : equality ('and' equality)* ;
equality        : comparison (( '!=' | '==' ) comparison)* ;
comparison      : term (( '>' | '>=' | '<' | '<=' ) term)* ;
term            : factor (( '-' | '+' ) factor)* ;
factor          : unary (( '/' | '*' | '%'  ) unary)* ;
array           : '[' (expression (',' expression)*)? ']';
instantiation   : 'new' IDENTIFIER '(' arguments? ')';

unary           : ( '!' | '-' ) unary
                | call ;

call            : primary ( '(' arguments? ')' | '.' IDENTIFIER | '[' expression ']')* 
                | funAnon;

primary         : 'true' | 'false' | 'nil' | 'this'
                | NUMBER | STRING | IDENTIFIER | '(' expression ')'
                | 'super' '.' IDENTIFIER 
                | array | instantiation
                | funAnon;

function        : IDENTIFIER '(' parameters? ')' block ;
parameters      : IDENTIFIER ( ',' IDENTIFIER )* ;
arguments       : expression ( ',' expression )* ;

NUMBER          : DIGIT+ ( '.' DIGIT+ )? ;
STRING          : '"' (~["\\])* '"' ;
IDENTIFIER      : ALPHA ( ALPHA | DIGIT )* ;
fragment ALPHA  : [a-zA-Z_] ;
fragment DIGIT  : [0-9] ;
WS              : [ \t\r\n]+ -> skip ;
ONE_LINE_COMMENT: '//' (~ '\n')* '\n'? -> skip;