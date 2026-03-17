---
title: "JITコンパイラの構築 (How to build a JIT compiler)"
---

AngelScript は組み込みの JIT コンパイラを提供していません。代わりに、外部の JIT コンパイラをパブリックインターフェースを通じて実装することを許可しています。

JIT コンパイルを使用するには、スクリプトを JIT コンパイラにヒントを提供し、VM がいつ制御を JIT コンパイル済み関数に渡すべきかを知るためのエントリポイントとなる、いくつかの追加命令と共にコンパイルしなければなりません。デフォルトではこれはオフになっており、エンジンプロパティ [asEP_INCLUDE_JIT_INSTRUCTIONS](#asEP_INCLUDE_JIT_INSTRUCTIONS) を設定することによってオンにする必要があります。

JIT コンパイラインターフェースには2つの異なるバージョンがサポートされています。デフォルトではバージョン 1 が使用されますが、バージョン 2 が必要な場合は [asEP_JIT_INTERFACE_VERSION](#asEP_JIT_INTERFACE_VERSION) を使用して [asIScriptEngine::SetEngineProperty](#asIScriptEngine::SetEngineProperty) で明示的に設定する必要があります。

## JIT インターフェース バージョン 1 (The JIT interface version 1)

バージョン 1 では、アプリケーションが [SetJITCompiler](#asIScriptEngine::SetJITCompiler) で [asIJITCompiler](#asIJITCompiler) を設定した場合、AngelScript はコンパイルされた、あるいは [事前コンパイル済みバイトコードからロードされた](./doc_adv_precompile) 各新しいスクリプト関数に対して自動的に [asIJITCompiler::CompileFunction](#asIJITCompiler::CompileFunction) を呼び出します。生成された [asJITFunction](#asJITFunction) はスクリプト関数が有効である間スクリプト関数とリンクされます。スクリプト関数が破棄された時、AngelScript はクリーンアップのために [asIJITCompiler::ReleaseJITFunction](#asIJITCompiler::ReleaseJITFunction) を呼び出します。

このインターフェースバージョンでは、JIT コンパイラはグローバルな最適化を行う方法がありません。なぜなら、現在コンパイルされているスクリプト関数の知識のみを持った状態で JIT 関数をコンパイルすることを余儀なくされるため、後から JIT 関数に戻って更新することができないからです。

## JIT インターフェース バージョン 2 (The JIT interface version 2)

バージョン 2 では、アプリケーションが [SetJITCompiler](#asIScriptEngine::SetJITCompiler) で [asIJITCompilerV2](#asIJITCompilerV2) を設定した場合、AngelScript はコンパイルされた、あるいは [事前コンパイル済みバイトコードからロードされた](./doc_adv_precompile) 各新しいスクリプト関数に対して自動的に [asIJITCompilerV2::NewFunction](#asIJITCompilerV2::NewFunction) を呼び出します。

違いは、バージョン 2 ではこのタイミングで JIT 関数を提供することが任意である点です。JIT コンパイラはコンパイルをスクリプト全体がコンパイルされるまたはロードされるまで遅らせることを選択できます。これにより、すべての関数を見た上で、インライン化などのグローバルな最適化を行うことができます。[asJITFunction](#asJITFunction) がコンパイルされた際、JIT コンパイラは [asIScriptFunction::SetJITFunction](#asIScriptFunction::SetJITFunction) を使用してスクリプト関数にそれをリンクしなければなりません。

JIT コンパイラが `NewFunction` の呼び出しですべてのスクリプト関数のマップを構築したくない場合、[asIScriptEngine::GetLastFunctionId](#asIScriptEngine::GetLastFunctionId) と [GetFunctionById](#asIScriptEngine::GetFunctionById) で既存のすべてのスクリプト関数をイテレートすることも可能です。

AngelScript は JIT 関数がスクリプト関数上で置き換えられる時、またはスクリプト関数が破棄された時はいつでも [asIJITCompilerV2::CleanFunction](#asIJITCompilerV2::CleanFunction) を呼び出します。

## JIT 関数の構造 (The structure of the JIT function)

[JIT コンパイル済み関数](#asJITFunction) は仮想マシンとうまく連動するために、いくつかのルールに従わなければなりません。その意図は、VM が JIT 関数に制御を渡し、実行をサスペンドする必要がある時は JIT 関数が VM に制御を返しながら、VM が後で再開が要求された時に実行を再開できるように VM の内部状態を更新するというものです。JIT 関数が VM に制御を返すたびに、実行されたコードに従って [VM レジスタ](#asSVMRegisters) とスタックの値が更新されていることを確認しなければなりません。

バイトコードには `JitEntry` という特別な命令があり、これは VM が JIT 関数に制御を渡せる位置を定義します。これらは通常すべてのスクリプトステートメントに対して、および別の関数を呼び出す各命令の後に配置されます。このことから、JIT コンパイル済み関数は `JitEntry` 命令の引数に基づいて異なるポイントから実行を開始できる必要があります。引数の値は JIT コンパイラによって定義され、その解釈方法も JIT コンパイラ次第です。ただし、0 は JIT 関数に制御を渡すべきではないことを意味するという例外があります。

バイトコード命令の中には、ネイティブコードに変換されることを意図していないものもあります。これらは通常 VM に対してより広範な影響を与えるもので、例えば新しいスクリプト関数の呼び出しをセットアップする命令や、前の命令から戻る命令などです。これらの関数に遭遇した時、JIT 関数は VM に制御を返すべきであり、その後 VM がその命令を実行します。

他のバイトコード命令は JIT 関数によって部分的に実装される場合があります。例えば、特定の条件に基づいて例外を投げる可能性があるものなどです。そのような例の1つが除算命令です。除数が 0 の場合、VM は例外をセットして実行を中断します。これらの命令では、JIT コンパイラは例外を投げない条件を優先的に実装し、例外が投げられる場合には JIT 関数が代わりに VM へとブレークアウトします。

以下は JIT コンパイル済み関数のあり得る構造を示しています：

```
void jitCompiledFunc(asSVMRegisters *regs, asPWORD jitArg)
{
  求められる VM レジスタを CPU レジスタに読み込む。
  'jitArg' 引数に基づいて関数の現在の位置にジャンプする。
1:
  ブロック1のコードを実行する。
  不正な操作（例：ゼロ除算）が行われた場合は exit にジャンプする。
  ブロックが JIT 関数で実行すべきでない命令で終わる場合は exit にジャンプする。
2:
  ...
3:
  ...
exit:
  VM に制御を返す前に VM レジスタを更新する。
  必要に応じて、regs で通知されたコンテキストのメソッドを呼び出すことができる。
  例：実行のサスペンド、またはスクリプト例外のセットなど。
}
```

## バイトコードのトラバース (Traversing the byte code)

```cpp
int CJITCompiler::CompileFunction(asIScriptFunction *func, asJITFunction *output)
{
  bool success = StartNewCompilation();

  // スクリプトのバイトコードを取得します
  asUINT   length;
  asDWORD *byteCode = func->GetByteCode(&length);
  asDWORD *end = byteCode + length;
  
  while( byteCode < end )
  {
    // 命令を特定します
    asEBCInstr op = asEBCInstr(*(asBYTE*)byteCode);
    switch( op )
    {
    // 各バイトコード命令をネイティブコードに変換します。
    // 変換できない命令については VM に制御を戻し、
    // VM が次の JitEntry 命令に遭遇した時に
    // JIT 関数に制御が戻るようにします。
    ...
    
    case asBC_JitEntry:
      // JitEntry 命令の引数を、JIT 関数に送られるべき
      // 引数で更新します。
      // 0 は VM が JIT 関数に制御を渡すべきでないことを意味します。
      asBC_PTRARG(byteCode) = DetermineJitEntryArg();
      break;
    }
    
    // 次の命令に移動します
    byteCode += asBCTypeSize[asBCInfo[op].type];
  }
  
  if( success )
  {
    *output = GetCompiledFunction();
    return 0;
  }
  
  return -1;
}
```

バイトコード命令から引数を読み取るには、以下のマクロを使用すべきです。引数のレイアウトは [asBCInfo](#asBCInfo) 配列から決定されます。

 - `asBC_DWORDARG`
 - `asBC_INTARG`
 - `asBC_QWORDARG`
 - `asBC_FLOATARG`
 - `asBC_PTRARG`
 - `asBC_WORDARG0`
 - `asBC_WORDARG1`
 - `asBC_SWORDARG0`
 - `asBC_SWORDARG1`
 - `asBC_SWORDARG2`

各 [バイトコード命令](./doc_adv_jit_1) が何を行うかは別ページで説明されていますが、各バイトコード命令の正確な実装は VM の実装、つまり `asCScriptContext::ExecuteNext` メソッドから最もよく判断できます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_jit.html
