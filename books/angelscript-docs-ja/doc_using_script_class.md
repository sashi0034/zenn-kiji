---
title: "スクリプトクラスの使用 (Using script classes)"
---

同一のスクリプト実装によって制御されるオブジェクトが複数存在する場合、グローバル関数ではなくスクリプトクラスを使用するのが適しています。クラスを使用することで、各インスタンスが独自の変数セットを持つことができ、永続的な情報の保存にグローバル変数を利用せざるを得ないグローバル関数とは対照的です。

もちろん、オブジェクトのインスタンスごとにスクリプトモジュールを複製することも可能ですが、それではアプリケーションにとって非常に大きなオーバーヘッドとなります。スクリプトクラスにはそのようなオーバーヘッドはありません。すべてのインスタンスが同じモジュールを共有するため、バイトコードや関数 ID などを共有できるからです。

## スクリプトクラスのインスタンス化

スクリプトクラスをインスタンス化する前に、どのクラスをインスタンス化すべきかを特定する必要があります。その方法はアプリケーションの設計によりますが、いくつか代表的な方法を紹介します。

1. **名前による特定**: アプリケーションがクラス名を把握している場合（プログラム内にハードコードされている、または設定ファイルなどから取得できる場合）、モジュールの `GetTypeIdByDecl` にクラス名を渡すことで、簡単に型情報を取得できます。
2. **インターフェースによる特定**: 特定の[インターフェース](./doc_register_api)を実装しているクラスを探す方法です。アプリケーションはスクリプトモジュール内の型を `GetObjectTypeByIndex` で列挙し、`asITypeInfo` インターフェースを介して目的のインターフェースを実装しているか確認できます。
3. **メタデータによる特定**: [スクリプトビルダーアドオン](./doc_addon#スクリプトビルダー-script-builder)を使用している場合、メタデータを利用してクラスを特定できます。`asIScriptModule` で型を列挙し、`CScriptBuilder` を通じて付随するメタデータを問い合わせます。

オブジェクト型が判明したら、そのクラスのファクトリ関数（C++ でいうコンストラクタに相当する部分）を呼び出してインスタンスを作成します。ファクトリ関数の ID は `asITypeInfo` から取得できます。

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

// 作成されたオブジェクトを取得します。
// GetAddressOfReturnValue() は戻り値（ここではオブジェクトハンドル）へのポインタを返します。
asIScriptObject *obj = *(asIScriptObject**)ctx->GetAddressOfReturnValue();

// オブジェクトを外部で保持し続ける場合は、参照カウントを増やす必要があります。
// 増やさない場合、コンテキストが解放されたり再利用されたりした時点でオブジェクトが破棄されます。
obj->AddRef();
```

ファクトリ関数は、[通常のグローバル関数を呼び出す手順](./doc_call_script_func)と同様に実行でき、新しくインスタンス化されたクラスへのハンドル（ポインタ）を返します。

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

## スクリプトクラスの受け取り (Receiving script classes)

アプリケーションがスクリプトクラス（のインスタンス）を引数として受け取る関数を登録したい場合、まずそのクラスの「型」を知る必要があります。しかし、クラスはスクリプト内で定義されるため、スクリプトがコンパイルされるまでその型を確定させることはできません。

この問題を解決するために、アプリケーションはあらかじめ[インターフェース](./doc_register_api)をエンジンに登録しておきます。そして、そのインターフェースへのハンドルを受け取るように引数を定義して関数を登録します。

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

このようにインターフェースを使用したくない場合は、事前に型が不明な値やオブジェクトを扱う手段として、[可変パラメータ型](./doc_adv_var_type)や [Handle アドオン](./doc_addon#handle-オブジェクト) の利用を検討してください。

## スクリプトクラスの返却 (Returning script classes)

登録された関数からスクリプトクラスのインスタンスを返す手順は、[受け取る場合](#スクリプトクラスの受け取り-receiving-script-classes)とほぼ同じです。関数の戻り値を登録するには、インターフェースを使用するか、汎用的な [Handle アドオン](./doc_addon#handle-オブジェクト) を利用する必要があります。

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

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_using_script_class.html
