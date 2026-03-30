---
title: "🚀 JITコンパイラの構築 (How to build a JIT compiler)"
---

AngelScript には標準の JIT コンパイラは組み込まれていませんが、公開されているインターフェースを通じて外部の JIT コンパイラを導入可能です。

JIT コンパイルを利用するには、スクリプトのコンパイル時に専用の命令を挿入する必要があります。これらは JIT コンパイラへのヒントとして機能し、仮想マシン (VM) が JIT コンパイル済み関数へ制御を移す際のエントリポイントとなります。この機能はデフォルトでは無効になっており、エンジンプロパティ `asEP_INCLUDE_JIT_INSTRUCTIONS` を設定することで有効化できます。

JIT コンパイラインターフェースには 2 つのバージョンがあります。デフォルトではバージョン 1 が使用されますが、バージョン 2 を使用する場合は `asEP_JIT_INTERFACE_VERSION` プロパティで明示的に指定する必要があります。

## JIT インターフェース バージョン 1 (The JIT interface version 1)

バージョン 1 では、`SetJITCompiler` で `asIJITCompiler` を設定すると、AngelScript はコンパイルまたは[ロード](./doc_adv_precompile)された各スクリプト関数に対して、自動的に `CompileFunction` を呼び出します。生成された `asJITFunction` は、そのスクリプト関数が有効である限りリンクされます。スクリプト関数が破棄される際、AngelScript はクリーンアップのために `ReleaseJITFunction` を呼び出します。

このインターフェースバージョンでは、JIT コンパイラはグローバルな最適化を行う方法がありません。なぜなら、現在コンパイルされているスクリプト関数の知識のみを持った状態で JIT 関数をコンパイルすることを余儀なくされるため、後から JIT 関数に戻って更新することができないからです。

## JIT インターフェース バージョン 2 (The JIT interface version 2)

バージョン 2 では、アプリケーションが `SetJITCompiler` で `asIJITCompilerV2` を設定した場合、AngelScript はコンパイルされた、あるいは [事前コンパイル済みバイトコードからロードされた](./doc_adv_precompile) 各新しいスクリプト関数に対して自動的に `NewFunction` を呼び出します。

違いは、バージョン 2 ではこのタイミングで JIT 関数を提供することが任意である点です。JIT コンパイラはコンパイルをスクリプト全体がコンパイルされるまたはロードされるまで遅らせることを選択できます。これにより、すべての関数を見た上で、インライン化などのグローバルな最適化を行うことができます。`asJITFunction` がコンパイルされた際、JIT コンパイラは `SetJITFunction` を使用してスクリプト関数にそれをリンクしなければなりません。

JIT コンパイラが `NewFunction` の呼び出しですべてのスクリプト関数のマップを構築したくない場合、`GetLastFunctionId` と `GetFunctionById` で既存のすべてのスクリプト関数をイテレートすることも可能です。

AngelScript は JIT 関数がスクリプト関数上で置き換えられる時、またはスクリプト関数が破棄された時はいつでも `CleanFunction` を呼び出します。

`asJITFunction` は、仮想マシンと正しく連携するために特定のルールに従う必要があります。基本的な動作の流れは、VM が JIT 関数へと実行を渡し、実行をサスペンド（一時停止）する必要が生じた際に JIT 関数から VM へと制御を戻すというものです。この際、VM が後に実行を再開できるよう、JIT 関数は VM の内部状態を正確に更新しておかなければなりません。JIT 関数から VM に制御を戻すたびに、実行されたコードの結果に基づいて `asSVMRegisters` とスタックの内容が同期されている必要があります。

バイトコード内には `JitEntry` という特殊な命令があり、ここが VM から JIT 関数への切り替えポイントとなります。通常、この命令は各スクリプト文の先頭や関数呼び出しの直後に配置されます。そのため、JIT コンパイル済み関数は、`JitEntry` 命令の引数に応じて任意の地点から実行を開始できる設計にする必要があります。この引数の値とその解釈は JIT コンパイラに委ねられますが、引数が 0 の場合は「その地点では JIT 関数へ制御を移さない」ことを意味します。

バイトコード命令の中には、意図的にネイティブコード化せず VM に処理を任せるべきものもあります。例えば、新しいスクリプト関数の呼び出し準備を行う命令や、関数から戻る命令など、VM のグローバルな管理に関わる命令が該当します。これらに遭遇した際、JIT 関数は VM へと制御を戻し、VM 自身にその処理を実行させます。

また、一部の命令を条件付きで実装する場合もあります。例えば除算命令において、除数が 0 でない通常のケースはネイティブコードで高速に処理し、ゼロ除算が発生する特殊なケースでは VM へと処理を戻して適切な例外処理を行わせる、といった使い分けが可能です。

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

バイトコード命令から引数を読み取るには、以下のマクロを使用すべきです。引数のレイアウトは `asBCInfo` 配列から決定されます。

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

各バイトコード命令が何を行うかは別ページで説明されていますが、各バイトコード命令の正確な実装は VM の実装、つまり `asCScriptContext::ExecuteNext` メソッドから最もよく判断できます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_jit.html
