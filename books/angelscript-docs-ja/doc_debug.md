---
title: "スクリプトのデバッグ (Debugging scripts)"
---

AngelScript は、スクリプトのデバッグをサポートする強力なインターフェースを提供しています。ブレークポイントの設定、関数内の変数の検査・操作、コールスタックの表示などが可能な組み込みデバッガを容易に構築できます。

以下の例で使用されている `CDebugMgr` クラスは、架空のデバッグ用管理クラスです。説明を簡略化するための抽象化として使用しています。

参照: 標準的な実装については [デバッガーアドオン](./doc_addon#デバッガー) を参照してください。

## ラインブレークポイントの設定 (Setting line breaks)

コードの特定の行で実行を一時停止（ブレーク）させるために、デバッガはスクリプトコンテキストに「ラインコールバック関数」を設定できます。VM（仮想マシン）は各ステートメントを実行するたびにこのコールバックを呼び出し、デバッガはそこで実行を続行するか停止するかを判断できます。

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

ラインコールバックによって実行が中断されると、コンテキストの `Execute` メソッドは `asEXECUTION_SUSPENDED` を返します。その後、アプリケーションは [コールスタックの表示](#コールスタックの表示-viewing-the-call-stack) や [変数の検査](#変数の検査-inspecting-variables) などのデバッグ機能を処理するための、専用のメッセージループに入ることができます。実行を再開するには、再度 `Execute` を呼び出すだけです。

スクリプトの実行をサスペンド（一時停止）させる代わりに、ラインコールバックの中から直接メッセージループを開始するという実装方法もあります。この場合、実行の再開はラインコールバック関数からリターン（戻る）することによって行われます。どちらの方法が実装しやすいかは、アプリケーションの設計に依存します。

`asIScriptContext` は、実行の経緯を追跡するためにコールスタックを公開しています。これにより、各スタック階層で [変数の値を表示](#変数の検査-inspecting-variables) することも可能です。

## コールスタックの表示 (Viewing the call stack)
 
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

コンテキストのインターフェースを通じて、スタック上のローカル変数の値を検査したり、さらに変更したりすることが可能です。これは現在実行中の関数だけでなく、コールスタックのすべての階層に対して行うことができます。

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

いくつかのスクリプトの実行は、アプリケーションによって明示的に開始されるものではありません。例えば、グローバル変数の初期化や、ガベージコレクターがオブジェクトを破棄する際に呼び出されるデストラクタなどです。これらの実行をデバッグしたい場合、アプリケーションは `SetContextCallbacks` メソッドを使用してコンテキストコールバックを登録する必要があります。エンジンは内部でスクリプトを実行する際、これらのコールバックを介してアプリケーションにコンテキストを要求します。アプリケーションは、エンジンに提供するコンテキストに対してデバッガをアタッチ（接続）することができます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_debug.html
