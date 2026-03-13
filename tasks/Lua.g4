grammar Lua;

prog: (statement)* EOF;

statement: assign
         | expr
         | forStmt
         | whileStmt
         | repeatStmt
         | ifStmt
         | breakStmt
         | continueStmt
         | funStmt
         | printStmt
         | readStmt
         ;

readStmt: 'read' '(' ')';

printStmt: 'print' '(' argList? ')';

argList: atom (',' atom)*;

callFun: NAME '(' args? ')';

args: expr (',' expr)*; 

returnStmt: 'return' expr;

funStmt: 'function' NAME '(' params? ')' block 'end';

params: NAME (',' NAME)*;

block: (statement)* returnStmt?;

table: '{' (tableEl (',' tableEl)*)? '}';

tableEl: key '=' value | value;

key: NUMBER
    | STRING
    | NAME
    | table
    | '[' expr ']';

value: atom | table;

assign: NAME '=' expr | NAME '=' table | NAME '=' readStmt;

breakStmt: 'break';

continueStmt: 'continue';

ifStmt: 'if' expr 'then' (statement)* ('elseif' expr 'then' (statement)*)* ('else' (statement)*)? 'end';

forStmt: 'for' NAME '=' expr ',' expr 'do' (statement)* 'end';

repeatStmt: 'repeat' (statement)* 'until' expr;

whileStmt: 'while' expr 'do' (statement)* 'end';

expr: orExpr | callFun;

orExpr: andExpr ('or' andExpr)*;

andExpr: notExpr ('and' notExpr)*;

notExpr: 'not' notExpr | comparison;

comparison: addExpr (('<' | '>' | '<=' | '>=' | '==' | '~=') addExpr)*;

addExpr: mulExpr (('+' | '-') mulExpr)*;

mulExpr: atom (('*' | '/' | '%' ) atom)*;

atom: NUMBER
    | STRING
    | NAME
    | '(' expr ')'
    | '-' atom
    | 'true'
    | 'false'
    | 'nil'
    | table
    | NAME '[' expr ']'
    | NAME '.' NAME
    ;

NUMBER: [0-9]+;
STRING: '"' .*? '"';
NAME: [a-zA-Z_]+;
WS: [ \t\r\n]+ -> skip;