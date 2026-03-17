---
title: "スクリプト関数の呼び出し (Calling a script function)"
---

## コンテキストの準備と関数の実行 (Preparing context and executing the function)

通常、スクリプト関数はいくつかのステップで実行されます：

1. コンテキストを準備する
2. 関数の引数をセットする
3. 関数を実行する
4. 戻り値を取得する

これらのコードは次のようになります：

```cpp
// スクリプトコンテキストのインスタンスを取得します。
// 呼び出しごとにインスタンスを割り当てるオーバーヘッドを避けるために、
// 通常は以前に作成したインスタンスを再利用することを望むでしょう。
asIScriptContext *ctx = engine->CreateContext();

// モジュールから関数を取得します。
// 同じ関数が複数回呼び出される場合はキャッシュしておくことが推奨されます。
asIScriptFunction *func = engine->GetModule(module_name)->GetFunctionByDecl(function_declaration);

// Prepare() を呼び出し、コンテキストにスタックの準備をさせます
ctx->Prepare(func);

// 関数の引数をセットします
ctx->SetArgDWord(...);

int r = ctx->Execute();
if( r == asEXECUTION_FINISHED )
{
  // 戻り値は実行が正常に終了した場合にのみ有効です
  asDWORD ret = ctx->GetReturnDWord();
}

// 使い終わったらコンテキストを解放します
ctx->Release();
```

もしアプリケーションがコールバック関数を使用したり、スクリプトが手動で実行を一時停止できる関数を登録したりすることで実行のサスペンドを許可している場合、実行関数はリターンコード `asEXECUTION_SUSPENDED` で終了前に戻ってくる可能性があります。その場合、単に実行関数を再度呼び出すことで後で実行を再開することができます。

`GetReturnValue()` で取得された戻り値は、スクリプト関数が正常に戻った場合、つまり `Execute()` が `asEXECUTION_FINISHED` を返した場合にのみ有効であることに注意してください。

## プリミティブ型の引数渡しと戻り値の受け取り (Passing and returning primitives)

引数を取るスクリプト関数を呼び出す際、これらの引数の値は `Prepare()` の呼び出し後、`Execute()` の前にセットされなければなりません。引数は `SetArg` メソッドのグループを使ってセットされます：

```cpp
int SetArgDWord(int arg, asDWORD value);
int SetArgQWord(int arg, asQWORD value);
int SetArgFloat(int arg, float value);
int SetArgDouble(int arg, double value);
int SetArgByte(int arg, asBYTE value);
int SetArgWord(int arg, asWORD value);
```

`arg` は引数の番号で、最初の引数は 0、次は 1、というようになります。`value` は引数の値です。どのメソッドを使うかはパラメータの型によって決まります。プリミティブ型にはこれらのいずれも使用できます。パラメータ型がプリミティブ型への参照の場合は、`SetArgAddress()` メソッドを使用してポインタを値として渡すことが推奨されます。非プリミティブ型には `SetArgObject()` メソッドを使用すべきで、これについては次のセクションで説明します。

```cpp
// このコンテキストは以下のシグネチャを持つスクリプト関数のために準備済みです：
// int function(int, double, bool, int &out)

// 最初の引数から始めて、コンテキストのスタックに引数を積みます
ctx->SetArgDWord(0, 1);
ctx->SetArgDouble(1, 3.141592);
ctx->SetArgByte(2, true);
int val;
ctx->SetArgAddress(3, &val);
```

スクリプト関数が実行されると、戻り値は `GetReturn` メソッドのグループを使って同様の方法で取得されます：

```cpp
asDWORD GetReturnDWord();
asQWORD GetReturnQWord();
float   GetReturnFloat();
double  GetReturnDouble();
asBYTE  GetReturnByte();
asWORD  GetReturnWord();
```

返された値が実際に有効であることを確認する必要があることに注意してください。例えば、スクリプト関数がスクリプト例外によって中断された場合、値は有効ではありません。これを行うには、`Execute()` または `GetState()` からのリターンコードを確認し、リターンコードが `asEXECUTION_FINISHED` であることを確認します。

## オブジェクトの引数渡しと戻り値の受け取り (Passing and returning objects)

登録されたオブジェクト型をスクリプト関数に渡すのは、プリミティブ型の渡し方と似ています。使用する関数は `SetArgObject()` です：

```cpp
int SetArgObject(int arg, void *object);
```

`arg` は他の `SetArg` メソッドと同様に引数の番号です。`object` は渡したいオブジェクトへのポインタです。

この同じメソッドは、値で渡されるパラメータと参照で渡されるパラメータの両方に使用されます。ライブラリは、パラメータが値で渡されるように定義されている場合、自動的にオブジェクトのコピーを作成します。

```cpp
// スクリプト関数に渡したい複雑なオブジェクト
CObject obj;

// オブジェクトを関数に渡します
ctx->SetArgObject(0, &obj);
```

スクリプト関数によって返されたオブジェクトの取得は、`GetReturnObject()` を使って同様の方法で行われます：

```cpp
void *GetReturnObject();
```

このメソッドはスクリプト関数が返したオブジェクトへのポインタを返します。ライブラリはオブジェクトへの参照を保持し続け、これはコンテキストが解放される際にのみ解放されます。

```cpp
// 戻り値を格納したいオブジェクト
CObject obj;

// 関数を実行します
int r = ctx->Execute();
if( r == asEXECUTION_FINISHED )
{
  // 返されたオブジェクトへのポインタを取得し、私たちのオブジェクトにコピーします
  obj = *(CObject*)ctx->GetReturnObject();
}
```

返されたオブジェクトのコピーを作成するか、それが参照カウントによって管理されている場合は参照を追加することが重要です。これをしないと、`GetReturnObject()` で取得したポインタはコンテキストが解放されたり、別のスクリプト関数呼び出しのために再利用されたりした際に無効になってしまいます。

## 例外処理 (Exception handling)

スクリプトが不正な操作（例えば null ハンドルに対するメソッド呼び出し）を実行した場合、スクリプトエンジンはスクリプト例外を投げます。仮想マシンはその後実行を中断し、[Execute](#asIScriptContext::Execute) メソッドは [asEXECUTION_EXCEPTION](#asEXECUTION_EXCEPTION) の値を返します。

この時、`asIScriptContext` のメソッドを通じて例外に関する情報を取得することが可能です。例：

```cpp
void PrintExceptionInfo(asIScriptContext *ctx)
{
  asIScriptEngine *engine = ctx->GetEngine();

  // 発生した例外を特定します
  printf("desc: %s\n", ctx->GetExceptionString());

  // 例外が発生した関数を特定します
  const asIScriptFunction *function = ctx->GetExceptionFunction();
  printf("func: %s\n", function->GetDeclaration());
  printf("modl: %s\n", function->GetModuleName());
  printf("sect: %s\n", function->GetScriptSectionName());

  // 例外が発生した行番号を特定します
  printf("line: %d\n", ctx->GetExceptionLineNumber());
}
```

希望する場合は、`SetExceptionCallback` を使用して、例外が発生した瞬間（`Execute` メソッドが戻る前）に呼び出されるコールバック関数を登録することも可能です。例外コールバックはその後、`WillExceptionBeCaught` を使用して、例外が [スクリプト内でキャッチされる](./doc_script_statement#try-catch-ブロック-try-catch-blocks) のか、それとも実行を中断させるのかを判断することができます。

参照: コールスタックの調査については [デバッグ](./doc_debug) を、例外情報を取得するためのヘルパー関数については [ヘルパーアドオン](./doc_addon#ヘルパー関数-scripthelper) を参照してください。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_call_script_func.html
