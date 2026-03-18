---
title: "スクリプト言語の文法 (Script language grammar)"
---

これは拡張バッカス・ナウア表記法 (EBNF) による言語文法です。

:::tip
[Railroad Diagram Generator](https://github.com/GuntherRademacher/rr) を使用すると、オンラインでナビゲーション可能な鉄道図（構文図）を生成できます。
:::

```ebnf
SCRIPT        ::= (IMPORT | ENUM | TYPEDEF | CLASS | MIXIN | INTERFACE | FUNCDEF | VIRTPROP | VAR | FUNC | NAMESPACE | USING | ';')*
IMPORT        ::= 'import' TYPE '&'? IDENTIFIER PARAMLIST FUNCATTR 'from' STRING ';'
USING         ::= 'using' 'namespace' IDENTIFIER ('::' IDENTIFIER)* ';'
NAMESPACE     ::= 'namespace' IDENTIFIER ('::' IDENTIFIER)* '{' SCRIPT '}'
ENUM          ::= ('shared' | 'external')* 'enum' IDENTIFIER (';' | ('{' IDENTIFIER ('=' EXPR)? (',' IDENTIFIER ('=' EXPR)?)* '}'))
FUNCDEF       ::= ('external' | 'shared')* 'funcdef' TYPE '&'? IDENTIFIER PARAMLIST ';'
FUNC          ::= ('shared' | 'external')* ('private' | 'protected')? (((TYPE '&'?) | '~'))? IDENTIFIER PARAMLIST 'const'? FUNCATTR (';' | STATBLOCK)
VIRTPROP      ::= ('private' | 'protected')? TYPE '&'? IDENTIFIER '{' (('get' | 'set') 'const'? FUNCATTR (STATBLOCK | ';'))* '}'
INTERFACE     ::= ('external' | 'shared')* 'interface' IDENTIFIER (';' | ((':' IDENTIFIER (',' IDENTIFIER)*)? '{' (VIRTPROP | INTFMTHD)* '}'))
MIXIN         ::= 'mixin' CLASS
CLASS         ::= ('shared' | 'abstract' | 'final' | 'external')* 'class' IDENTIFIER (';' | ((':' IDENTIFIER (',' IDENTIFIER)*)? '{' (VIRTPROP | FUNC | VAR | FUNCDEF)* '}'))
VAR           ::= ('private'|'protected')? TYPE IDENTIFIER (( '=' (INITLIST | EXPR)) | ARGLIST)? (',' IDENTIFIER (( '=' (INITLIST | EXPR)) | ARGLIST)?)* ';'
TYPEDEF       ::= 'typedef' PRIMTYPE IDENTIFIER ';'
INTFMTHD      ::= TYPE '&'? IDENTIFIER PARAMLIST 'const'? ';'
STATBLOCK     ::= '{' (VAR | STATEMENT | USING)* '}'
PARAMLIST     ::= '(' ('void' | (TYPE TYPEMOD ('...' | IDENTIFIER? ('=' EXPR)?) (',' TYPE TYPEMOD ('...' | IDENTIFIER? ('=' EXPR)?))*))? ')'
TYPEMOD       ::= ('&' ('in' | 'out' | 'inout')?)?
TYPE          ::= 'const'? SCOPE DATATYPE TEMPLTYPELIST? ( ('[' ']') | ('@' 'const'?) )*
TEMPLTYPELIST ::= '<' TYPE (',' TYPE)* '>'
INITLIST      ::= '{' (ASSIGN | INITLIST)? (',' (ASSIGN | INITLIST)?)* '}'
SCOPE         ::= '::'? (IDENTIFIER '::')* (IDENTIFIER TEMPLTYPELIST? '::')?
DATATYPE      ::= (IDENTIFIER | PRIMTYPE | '?' | 'auto')
PRIMTYPE      ::= 'void' | 'int' | 'int8' | 'int16' | 'int32' | 'int64' | 'uint' | 'uint8' | 'uint16' | 'uint32' | 'uint64' | 'float' | 'double' | 'bool'
FUNCATTR      ::= ('override' | 'final' | 'explicit' | 'property' | 'delete')*
STATEMENT     ::= (IF | FOR | FOREACH | WHILE | RETURN | STATBLOCK | BREAK | CONTINUE | DOWHILE | SWITCH | EXPRSTAT | TRY)
EXPRSTAT      ::= ASSIGN? ';'
SWITCH        ::= 'switch' '(' ASSIGN ')' '{' CASE* '}'
IF            ::= 'if' '(' ASSIGN ')' STATEMENT ('else' STATEMENT)?
TRY           ::= 'try' STATBLOCK 'catch' STATBLOCK
FOR           ::= 'for' '(' (VAR | EXPRSTAT) EXPRSTAT (ASSIGN (',' ASSIGN)*)? ')' STATEMENT
FOREACH       ::= 'foreach' '(' TYPE IDENTIFIER (',' TYPE IDENTIFIER)* ':' ASSIGN ')' STATEMENT
WHILE         ::= 'while' '(' ASSIGN ')' STATEMENT
DOWHILE       ::= 'do' STATEMENT 'while' '(' ASSIGN ')' ';'
RETURN        ::= 'return' ASSIGN? ';'
BREAK         ::= 'break' ';'
CONTINUE      ::= 'continue' ';'
EXPR          ::= EXPRTERM (EXPROP EXPRTERM)*
CASE          ::= (('case' EXPR) | 'default') ':' STATEMENT*
EXPRTERM      ::= ((TYPE '=')? INITLIST) | (EXPRPREOP* EXPRVALUE EXPRPOSTOP*)
EXPRVALUE     ::= 'void' | CONSTRUCTCALL | FUNCCALL | VARACCESS | CAST | LITERAL | '(' ASSIGN ')' | LAMBDA
CONSTRUCTCALL ::= TYPE ARGLIST
EXPRPREOP     ::= '-' | '+' | '!' | '++' | '--' | '~' | '@'
EXPRPOSTOP    ::= ('.' (FUNCCALL | IDENTIFIER)) | ('[' (IDENTIFIER ':')? ASSIGN (',' (IDENTIFIER ':')? ASSIGN)* ']') | ARGLIST | '++' | '--'
CAST          ::= 'cast' '<' TYPE '>' '(' ASSIGN ')'
LITERAL       ::= NUMBER | STRING | BITS | 'true' | 'false' | 'null'
LAMBDA        ::= 'function' '(' ((TYPE TYPEMOD)? IDENTIFIER? (',' (TYPE TYPEMOD)? IDENTIFIER?)*)? ')' STATBLOCK
FUNCCALL      ::= SCOPE IDENTIFIER TEMPLTYPELIST? ARGLIST
VARACCESS     ::= SCOPE IDENTIFIER
ARGLIST       ::= '(' (IDENTIFIER ':')? ASSIGN (',' (IDENTIFIER ':')? ASSIGN)* ')'
ASSIGN        ::= CONDITION ( ASSIGNOP ASSIGN )?
CONDITION     ::= EXPR ('?' ASSIGN ':' ASSIGN)?
EXPROP        ::= MATHOP | COMPOP | LOGICOP | BITOP
MATHOP        ::= '+' | '-' | '*' | '/' | '\%' | '**'
COMPOP        ::= '==' | '!=' | '<' | '<=' | '>' | '>=' | 'is' | '!is'
LOGICOP       ::= '&&' | '||' | '^^' | 'and' | 'or' | 'xor'
BITOP         ::= '&' | '|' | '^' | '<<' | '>>' | '>>>'
ASSIGNOP      ::= '=' | '+=' | '-=' | '*=' | '/=' | '|=' | '&=' | '^=' | '%=' | '**=' | '<<=' | '>>=' | '>>>='
IDENTIFIER    ::= [A-Za-z_][A-Za-z0-9_]*            // 単一トークン: 文字または _ で始まり、任意の文字と数字を含めることができます。C++ と同じです。
NUMBER        ::= [0-9]+("."[0-9]+)?                // 単一トークン: 整数および実数を含みます。C++ と同じです。
STRING        ::= '"' ("\". | [^"\#x0D\#x0A\\])* '"'   // 単一トークン: シングルクォート '、ダブルクォート "、またはヒアドキュメント複数行文字列 """
BITS          ::= '0'[bBoOdDxX][0-9A-Fa-f]+         // 単一トークン: 2進数 0b, 8進数 0o, 10進数 0d, 16進数 0x
COMMENT       ::= ('//'[^\#x0A]*) | ('/*'[^*]*'*/')  // 単一トークン: // で始まって改行で終わるか、/* で始まって */ で終わります
WHITESPACE    ::= [ \#x09\#x0A\#x0D]+                  // 単一トークン: スペース、タブ、キャリッジリターン、ラインフィード、および UTF8 バイトオーダーマーク
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_bnf.html
