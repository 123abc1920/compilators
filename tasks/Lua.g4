grammar Lua;

prog: (statement)* EOF;

statement: assign
         | expr
         | forStmt
         ;

assign: NAME '=' expr;

forStmt: 'for' NAME '=' expr ',' expr 'do' (statement)* 'end';

whileStmt: 'while' expr 'do' (statement)* 'end';

expr: notExpr;

notExpr: 'not' notExpr | andExpr;

andExpr: comparison ('and' comparison)*;

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