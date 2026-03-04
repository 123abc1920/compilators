grammar Lua;

prog: (statement)* EOF;

statement: assign
         | expr
         | forStmt
         | whileStmt
         ;

assign: NAME '=' expr;

forStmt: 'for' NAME '=' expr ',' expr 'do' (statement)* 'end';

whileStmt: 'while' expr 'do' (statement)* 'end';

expr: orExpr;

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
    ;

NUMBER: [0-9]+;
STRING: '"' .*? '"';
NAME: [a-zA-Z_]+;
WS: [ \t\r\n]+ -> skip;