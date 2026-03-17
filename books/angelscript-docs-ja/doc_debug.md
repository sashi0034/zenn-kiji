---
title: "スクリプトのデバッグ (Debugging scripts)"
---

AngelScript は、スクリプトのデバッグをサポートするための豊富なインターフェースを提供しています。ブレークポイントの設定、関数内の変数の検査や操作、コールスタックの視覚化などを行える組み込みデバッガを簡単に構築することができます。

以下の例で使用されている `CDebugMgr` クラスは実際には存在しないことに注意してください。架空のデバッグルーチンを記述する手間を省くための抽象化としてのみ使用されています。

参照: 標準的な実装については [デバッガーアドオン](./doc_addon#デバッガ-debugger) を参照してください。

## ラインブレークポイントの設定 (Setting line breaks)

コード内の特定の行で処理を一時停止（ブレーク）するために、デバッガはスクリプトコンテキストにラインコールバック関数を設定することができます。VM は実行される各ステートメントに対してコールバックを呼び出し、デバッガが次のステートメントに進むべきかどうかを決定できるようにします。

```cpp
// ラインコールバックの例
void DebugLineCallback(asIScriptContext *ctx, CDebugMgr *dbg)
{
  // ブレークポイントに到達したかどうかを判断する
  const char *scriptSection;
  int line = ctx->GetLineNumber(0, 0, &scriptSection);
  asIScriptFunction *function = ctx->GetFunction();

  // デバッガに、ここにブレークポイントが設定されているか確認させる
  if( dbg->IsBreakpoint(scriptSection, line, function) )
  {
    // ブレークポイントに到達したため、スクリプトの実行を一時停止（サスペンド）すべきである
    ctx->Suspend();
  }
}
```

ラインコールバックは、コンテキストに対して次の呼び出しで設定されます：

```cpp
  // パラメータとしてデバッグマネージャのアドレスを渡し、ラインコールバックを設定する
  ctx->SetLineCallback(asFUNCTION(DebugLineCallback), dbg, asCALL_CDECL);
```

ラインコールバックが実行を一時停止すると、コンテキストの `Execute` 関数は `asEXECUTION_SUSPENDED` コードを返します。その後アプリケーションは、[コールスタックの表示](#コールスタックの表示-viewing-the-call-stack) や [変数の検査](#変数の検査-inspecting-variables) などのデバッグルーチンを処理できる特別なメッセージループに入ることができます。実行を続行する準備ができたら、単純にもう一度 `Execute` メソッドを呼び出せば再開されます。

スクリプト実行を一時停止させる代わりに、ラインコールバックの内部から直接メッセージループを開始するという方法もあります。この場合、実行の再開は単にラインコールバック関数からリターン（戻る）することによって行われます。どちらの実装が簡単かは、アプリケーションがどのように実装されているかに依存します。

## コールスタックの表示 (Viewing the call stack)

`asIScriptContext` は内容を表示するためにコールスタックを公開しており、これにより呼び出し元（発生源）を簡単に追跡することができます。また、コールスタックの各階層における [変数の値を表示](#変数の検査-inspecting-variables) することも可能です。

以下は、コールスタック全体を出力する方法の例です：

```cpp
void PrintCallstack(asIScriptContext *ctx)
{
  // コールスタックを表示する
  for( asUINT n = 0; n < ctx->GetCallstackSize(); n++ )
  {
    asIScriptFunction *func;
    const char *scriptSection;
    int line, column;
    func = ctx->GetFunction(n);
    line = ctx->GetLineNumber(n, &column, &scriptSection);
    printf("%s:%s:%d,%d\n", scriptSection,
                            func->GetDeclaration(),
                            line, column);
  }
}
```

## 変数の検査 (Inspecting variables)

コンテキストインターフェースを通じて、スタック上のローカル変数の値を検査したり、さらに変更したりすることが可能です。これは現在実行されている関数だけでなく、コールスタックの各階層に対して行うことができます。

以下は変数を表示する方法の例です：

```cpp
void PrintVariables(asIScriptContext *ctx, asUINT stackLevel)
{
  asIScriptEngine *engine = ctx->GetEngine();

  // 1つ目に、これがクラスメソッドであれば this ポインタを表示する
  int typeId = ctx->GetThisTypeId(stackLevel);
  void *varPointer = ctx->GetThisPointer(stackLevel);
  if( typeId )
  {
    printf(" this = 0x%x\n", varPointer);
  }

  // パラメータを含む各変数の値を表示する
  int numVars = ctx->GetVarCount(stackLevel);
  for( int n = 0; n < numVars; n++ )
  {
    int typeId = ctx->GetVarTypeId(n, stackLevel); 
    void *varPointer = ctx->GetAddressOfVar(n, stackLevel);
    if( typeId == asTYPEID_INT32 )
    {
      printf(" %s = %d\n", ctx->GetVarDeclaration(n, stackLevel), *(int*)varPointer);
    }
    else if( typeId == asTYPEID_FLOAT )
    {
      printf(" %s = %f\n", ctx->GetVarDeclaration(n, stackLevel), *(float*)varPointer);
    }
    else if( typeId & asTYPEID_SCRIPTOBJECT )
    {
      asIScriptObject *obj = (asIScriptObject*)varPointer;
      if( obj )
        printf(" %s = {...}\n", ctx->GetVarDeclaration(n, stackLevel));
      else
        printf(" %s = <null>\n", ctx->GetVarDeclaration(n, stackLevel));
    }
    else if( typeId == engine->GetTypeIdByDecl("string") )
    {
      string *str = (string*)varPointer;
      if( str )
        printf(" %s = '%s'\n", ctx->GetVarDeclaration(n, stackLevel), str->c_str());
      else
        printf(" %s = <null>\n", ctx->GetVarDeclaration(n, stackLevel));
    }
    else
    {
      printf(" %s = {...}\n", ctx->GetVarDeclaration(n, stackLevel));
    }
  }
}
```

上記のコードは、それがどのように可能であるかのアイデアを示すための例にすぎません。これは完全なものではなく、いくつかの型しか認識しません。それを有用なものにするには、すべての型を認識できるように拡張し、さらにオブジェクトを人間が読める文字列に変換して出力するためのジェネリックな方法を追加する必要があるでしょう。

スクリプトオブジェクトの場合、`asIScriptObject` インターフェースを通じてオブジェクトのメンバを列挙することによってその変換を行うことができます。

デバッガでは、関数がアクセスするグローバル変数を検査できるようにする必要もあるかもしれません。グローバル変数はモジュール内に格納されるため、モジュールこそが探すべき場所となります。`asIScriptModule` インターフェースは、関数からモジュール名を問い合わせ、その後エンジンからモジュールポインタを取得することによって得ることができます。モジュールが特定できれば、`asIScriptModule` インターフェースの適切なメソッドを使用する点を除けば、上の例とほぼ同じ方法でグローバル変数を列挙することができます。

## 内部的に実行されたスクリプトのデバッグ (Debugging internally executed scripts)

いくつかのスクリプトの実行はアプリケーションによって明示的に開始されるわけではありません。例えば、ガベージコレクターがオブジェクトを破棄する際に呼び出されるグローバル変数の初期化やスクリプトクラスのデストラクタの呼び出しなどです。もしこれらの実行をデバッグしたい場合は、アプリケーションは `SetContextCallbacks` メソッドの呼び出しでコンテキストのコールバック関数を設定しなければなりません。エンジンは内部でスクリプトを実行するたびにこれらのコールバックを呼び出し、アプリケーションにそのためのコンテキストを要求します。アプリケーションは、エンジンに提供するコンテキストに対してデバッガをアタッチ（接続）することができます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_debug.html
