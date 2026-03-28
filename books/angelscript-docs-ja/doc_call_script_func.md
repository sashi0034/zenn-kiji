---
title: "スクリプト関数の呼び出し (Calling a script function)"
---

## コンテキストの準備と関数の実行 (Preparing context and executing the function)

通常、スクリプト関数の実行は以下の手順で行われます：

1. コンテキストを準備する（Prepare）
2. 関数の引数を設定する（SetArg）
3. 関数を実行する（Execute）
4. 戻り値を取得する（GetReturn）

実装コードは次のようになります：

```cpp
// スクリプトコンテキストを取得します。
// 呼び出しのたびにコンテキストを生成するオーバーヘッドを避けるため、
// 通常は既存のインスタンスを再利用します。
asIScriptContext *ctx = engine->CreateContext();

// モジュールから関数を取得します。
// 同じ関数を繰り返し呼び出す場合は、取得したポインタをキャッシュしておくことが推奨されます。
asIScriptFunction *func = engine->GetModule(module_name)->GetFunctionByDecl(function_declaration);

// Prepare() を呼び出して、コンテキストの実行スタックを準備します。
ctx->Prepare(func);

// 関数の引数を設定します。
ctx->SetArgDWord(0, ...);

int r = ctx->Execute();
if( r == asEXECUTION_FINISHED )
{
  // 戻り値は実行が正常に終了した場合にのみ有効です。
  asDWORD ret = ctx->GetReturnDWord();
}

// 使い終わったらコンテキストを解放（または再利用のためにプールへ返却）します。
ctx->Release();
```

アプリケーションで実行のサスペンド（中断）を許可している場合（コールバック関数の使用や、スクリプトから手動で中断できる関数の登録など）、`Execute()` メソッドは完了前に `asEXECUTION_SUSPENDED` を返して戻ってくることがあります。その場合、後で再度 `Execute()` を呼び出すだけで、中断した箇所から実行を再開できます。

`GetReturn` メソッドで取得できる戻り値は、スクリプト関数が正常に終了した場合（`Execute()` が `asEXECUTION_FINISHED` を返した場合）にのみ有効である点に注意してください。

## プリミティブ型の引数渡しと戻り値の受け取り (Passing and returning primitives)

引数を取るスクリプト関数を呼び出す際、引数の値は `Prepare()` の呼び出し後、かつ `Execute()` の前に設定する必要があります。引数の設定には、一連の `SetArg` メソッドを使用します。

```cpp
int SetArgDWord(int arg, asDWORD value);
int SetArgQWord(int arg, asQWORD value);
int SetArgFloat(int arg, float value);
int SetArgDouble(int arg, double value);
int SetArgByte(int arg, asBYTE value);
int SetArgWord(int arg, asWORD value);
```

`arg` は引数のインデックスで、最初の引数が 0、次が 1 となります。`value` は渡す値です。使用するメソッドはパラメータの型によって決まります。プリミティブ型には上記のいずれかを使用します。パラメータの型がプリミティブ型への参照である場合は、`SetArgAddress()` を使用してポインタを渡すことが推奨されます。非プリミティブ型（オブジェクト型）には、後述する `SetArgObject()` を使用してください。

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

スクリプト関数の実行が終了すると、戻り値は `GetReturn` メソッド群を使用して取得できます。取得方法は引数の設定と同様です。

```cpp
asDWORD GetReturnDWord();
asQWORD GetReturnQWord();
float   GetReturnFloat();
double  GetReturnDouble();
asBYTE  GetReturnByte();
asWORD  GetReturnWord();
```

取得した戻り値が実際に有効であるかを確認することが重要です。例えば、スクリプト関数が例外によって中断された場合、戻り値は有効ではありません。戻り値が有効か確認するには、`Execute()` または `GetState()` の戻り値が `asEXECUTION_FINISHED` であることを確認してください。

## オブジェクトの引数渡しと戻り値の受け取り (Passing and returning objects)

登録されたオブジェクト型をスクリプト関数に渡す手順も、プリミティブ型の場合と同様です。`SetArgObject()` 関数を使用します。

```cpp
int SetArgObject(int arg, void *object);
```

`arg` は引数のインデックスです。`object` は渡したいオブジェクトへのポインタです。

このメソッドは、値渡し（By Value）と参照渡し（By Reference）の両方のパラメータに使用されます。パラメータが値渡しとして定義されている場合、ライブラリは自動的にオブジェクトのコピーを作成します。

```cpp
// スクリプト関数に渡したいオブジェクト
CObject obj;

// オブジェクトを関数に渡します
ctx->SetArgObject(0, &obj);
```

スクリプト関数によって返されたオブジェクトの取得には、`GetReturnObject()` を使用します。

```cpp
void *GetReturnObject();
```

このメソッドは、スクリプト関数が返したオブジェクトへのポインタを返します。ライブラリはオブジェクトへの参照を保持し続け、これはコンテキストが解放（Release）されるまで維持されます。

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

返されたオブジェクトのコピーを作成するか、参照カウントで管理されている場合は参照を追加することが重要です。これを怠ると、`GetReturnObject()` で取得したポインタは、コンテキストが解放されたり、別のスクリプト関数呼び出しのために再利用されたりした際に無効になってしまいます。

## 例外処理 (Exception handling)

スクリプトが不正な操作（例：null ハンドルに対するメソッド呼び出し）を実行すると、スクリプトエンジンはスクリプト例外をスローします。仮想マシンは実行を即座に中断し、`Execute()` メソッドは `asEXECUTION_EXCEPTION` を返します。

このとき、`asIScriptContext` のメソッドを通じて例外情報を取得できます。以下に例を示します。

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

希望する場合は、`SetExceptionCallback` を使用して、例外が発生した瞬間（`Execute` メソッドが戻る前）に呼び出されるコールバック関数を登録することも可能です。例外コールバックはその後、`WillExceptionBeCaught` を使用して、例外が [スクリプト内でキャッチされる](./doc_script_statement#try-catch-ブロック-(try-catch-blocks)) のか、それとも実行を中断させるのかを判断することができます。

参照: コールスタックの調査については [デバッグ](./doc_debug) を、例外情報を取得するためのヘルパー関数については [ヘルパーアドオン](./doc_addon#ヘルパー関数) を参照してください。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_call_script_func.html
