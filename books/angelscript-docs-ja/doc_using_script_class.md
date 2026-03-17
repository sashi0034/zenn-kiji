---
title: "スクリプトクラスの使用 (Using script classes)"
---

同じスクリプト実装によって制御される複数のオブジェクトがある場合、グローバルなスクリプト関数ではなくスクリプトクラスを使用するのが望ましい場合があります。スクリプトクラスを使用すると、永続的な情報を保存するためにグローバル変数に頼る必要があるグローバル関数とは異なり、各インスタンスがクラス内に独自の変数のセットを持つことができます。

もちろん、スクリプトモジュールを複製してオブジェクトインスタンスごとに1つのモジュールを持たせることも可能ですが、それはアプリケーションにとってかなり大きなオーバーヘッドになります。スクリプトクラスにはそのようなオーバーヘッドはありません。すべてのインスタンスが同じモジュール、つまり同じバイトコードと関数 ID などを共有するためです。

## スクリプトクラスのインスタンス化

スクリプトクラスをインスタンス化する前に、どのクラスをインスタンス化するかを知る必要があります。これがどのように行われるかはアプリケーションによって異なりますが、いくつかの提案を以下に示します。

アプリケーションがクラス名を知っている場合（ハードコードされているか、何らかの設定から得られる場合）、モジュールの `GetTypeIdByDecl` をクラス名で呼び出すことで、クラス型を簡単に取得できます。アプリケーションは、クラスが定義済みの[インターフェース](./doc_register_api)を実装しているかどうかなど、クラスのいくつかのプロパティを通じてクラスを識別するように選択することもできます。その場合、アプリケーションはスクリプトで実装されているクラス型を `GetObjectTypeByIndex` で列挙し、`asITypeInfo` インターフェースを通じて型を調べることができます。

3番目のオプションは、[スクリプトビルダーアドオン](./doc_addon)を使用している場合に、メタデータを使用してクラスを識別することです。このオプションを選択した場合は、`asIScriptModule` を使用して宣言された型を列挙し、`CScriptBuilder` にそれらのメタデータを問い合わせます。

オブジェクト型が判明したら、クラスのファクトリ関数を呼び出し、必要な引数（例: スクリプトクラスがバインドされるアプリケーションオブジェクトへのポインタ）を渡すことでインスタンスを作成します。ファクトリ関数の ID は `asITypeInfo` に問い合わせることで見つかります。

```cpp
// オブジェクト型を取得します
asIScriptModule *module = engine->GetModule("MyModule");
asITypeInfo *type = module->GetTypeInfoByDecl("MyClass");

// オブジェクト型からファクトリ関数を取得します
asIScriptFunction *factory = type->GetFactoryByDecl("MyClass @MyClass()");

// ファクトリ関数を呼び出すためにコンテキストを準備します
ctx->Prepare(factory);

// 呼び出しを実行します
ctx->Execute();

// 作成されたオブジェクトを取得します
asIScriptObject *obj = *(asIScriptObject**)ctx->GetAddressOfReturnValue();

// オブジェクトを保存する場合は、参照カウントを増やす必要があります。
// そうしないと、コンテキストが再利用または破棄されたときにオブジェクトが破棄されます。
obj->AddRef();
```

ファクトリ関数は[通常のグローバル関数として呼び出され](./doc_call_script_func)、新しくインスタンス化されたクラスへのハンドルを返します。

## スクリプトクラスのメソッドの呼び出し

スクリプトクラスのメソッドの呼び出しは、`asITypeInfo` から関数 ID を取得し、他の関数引数と一緒にオブジェクトポインタを設定する必要がある点を除けば、[グローバル関数の呼び出し](./doc_call_script_func)と同様です。

```cpp
// クラスメソッドを表す関数オブジェクトを取得します
asIScriptFunction *func = type->GetMethodByDecl("void method()");

// メソッドを呼び出すためにコンテキストを準備します
ctx->Prepare(func);

// オブジェクトポインタを設定します
ctx->SetObject(obj);

// 呼び出しを実行します
ctx->Execute();
```

## スクリプトクラスの受け取り

アプリケーションがスクリプトクラスを受け取る関数を登録するためには、まずその型を知る必要があります。もちろん、クラスはスクリプトで宣言されているため、スクリプトがコンパイルされる前に型を知ることは不可能です。代わりに、アプリケーションは[インターフェース](./doc_register_api)をエンジンに登録できます。その後、そのインターフェースへのハンドルを受け取るように関数を登録できます。

```cpp
// インターフェースを登録します
engine->RegisterInterface("IMyObj");

// スクリプトクラスに実装を強制したい場合は、インターフェースメソッドを登録することもできます
engine->RegisterInterfaceMethod("IMyObj", "void RequiredMethod()");

// インターフェースへのハンドルを受け取る関数を登録します
engine->RegisterGlobalFunction("void ReceiveMyObj(IMyObj @obj)", asFUNCTION(ReceiveMyObj), asCALL_CDECL);
```

インターフェースを受け取る関数は、`asIScriptObject` へのポインタを受け取るように実装する必要があります。

```cpp
asIScriptObject *gObj = 0;
void ReceiveMyObj(asIScriptObject *obj)
{
  // オブジェクトを処理します
  if( obj )
  {
    if( doStore )
    {
      // オブジェクトを保存する場合、ハンドルを解放してはいけません
      gObj = obj;
    }
    else
    {
      // オブジェクトを保存しない場合、戻る前にハンドルを解放しなければなりません
      obj->Release();
    }
  }
}
```

このようにインターフェースを使用したくない場合は、事前に型が不明な値やオブジェクトを受け取る方法である[可変引数型](./doc_adv_var_type)または[汎用スクリプトハンドルアドオン](./doc_addon)を検討してください。

## スクリプトクラスの返却

登録された関数からスクリプトクラスを返すことは、[それらを受け取る](#スクリプトクラスの受け取り)のとほぼ同じです。関数を登録するためには、インターフェースを使用するか、[汎用スクリプトハンドルアドオン](./doc_addon)を使用する必要があります。

```cpp
// グローバル変数は他で初期化されます
asIScriptObject *gObj;

asIScriptObject *ReturnMyObj()
{
  if( gObj == 0 )
    return 0;

  // 返されるハンドルを考慮して参照カウントを増やします
  gObj->AddRef();
  return gObj;
}
```

この関数は次のように登録できます：

```cpp
// インターフェースを登録します
engine->RegisterInterface("IMyObj");

// インターフェースへのハンドルを返す関数を登録します
engine->RegisterGlobalFunction("IMyObj @ReturnMyObj()", asFUNCTION(ReturnMyObj), asCALL_CDECL);
```
