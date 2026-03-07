grammar Lua;

prog: (statement)* EOF;

statement: assign
         | expr
         | forStmt
         | whileStmt
         | repeatStmt
         | ifStmt
         | breakStmt
         ;

assign: NAME '=' expr;

breakStmt: 'break';

ifStmt: 'if' expr 'then' (statement)* ('elseif' expr 'then' (statement)*)* ('else' (statement)*)? 'end';

forStmt: 'for' NAME '=' expr ',' expr 'do' (statement)* 'end';

repeatStmt: 'repeat' (statement)* 'until' expr;

whileStmt: 'while' expr 'do' (statement)* 'end';

expr: orExpr
    | 'true'
    | 'false'
    | 'nil';

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
    ;

NUMBER: [0-9]+;
STRING: '"' .*? '"';
NAME: [a-zA-Z_]+;
WS: [ \t\r\n]+ -> skip;