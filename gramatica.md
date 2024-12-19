<prog> -> <funcao> <RestoFuncoes>
<RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
<funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
<tipoResultado> -> LAMBDA | -> <tipo>
<params> -> <tipo> ident <restoParams> | LAMBDA
<restoParams> -> LAMBDA | , <tipo> ident <restoParams> 
<corpo> -> begin <declaracoes> <calculo> end
<declaracoes> -> <declara> <declaracoes> | LAMBDA
<declara> -> <tipo> <idents> ;
<idents> -> ident <restoIdents> 
<restoIdents> -> , ident <restoIdents> | LAMBDA 
<tipo> -> string <opcLista> | int <opcLista> | float <opcLista> 
<opcLista> -> [ list ] | LAMBDA
<calculo> -> LAMBDA | <com> <calculo>
<com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna> | <call> 
<retorna> -> return <expOpc> ;
<expOpc> -> LAMBDA | <exp>
<while> -> while ( <exp> ) <com>
<for> -> for ident in <range> do <com>
<range> -> <lista> | range ( <exp> , <exp> <opcRange> )
<lista> -> ident <opcIndice> | [ <elemLista> ]
<elemLista> -> LAMBDA | <elem> <restoElemLista>
<restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
<elem> -> intVal | floatVal | strVal | ident 
<opcRange> -> , <exp> | LAMBDA
<atrib> -> ident <opcIndice> = <exp> ;
<if> -> if ( <exp> ) then <com> <else_opc>
<else_opc> -> LAMBDA | else <com> 
<leitura> -> read ( strVal , ident ) ;
<escrita> -> write ( <lista_out> ) ;
<lista_outs> -> <out> <restoLista_outs>
<restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
<out> -> <exp>
<bloco> -> { <calculo> }
<exp> -> <disj>
<disj> -> <conj> <restoDisj>
<restoDisj> -> LAMBDA | or <conj> <restoDisj>
<conj> -> <nao> <restoConj>
<restoConj> -> LAMBDA | and <nao> <restoConj>
<nao> -> not <nao> | <rel>
<rel> -> <soma> <restoRel>
<restoRel> -> LAMBDA | oprel <soma>
<soma> -> <mult> <restoSoma>
<restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
<mult> -> <uno> <restoMult>
<restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
<uno> -> + <uno> | - <uno> | <folha>
<folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
<call> -> ident ( <lista_outs_opc> )
<lista_outs_opc> -> <lista_outs> | LAMBDA
<opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
<restoElem> -> LAMBDA | : <exp>

