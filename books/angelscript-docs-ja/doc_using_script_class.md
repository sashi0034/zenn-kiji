---
title: "スクリプトクラスの使用 (Using script classes)"
---

同じスクリプトの実装で制御される複数のオブジェクトがある場合、グローバルスクリプト関数よりもスクリプトクラスを使用する方が有利な場合があります。スクリプトクラスを使用することで、各インスタンスはクラス内に独自の変数セットを持つことができます。対照的に、グローバル関数は永続的な情報を格納するためにグローバル変数に頼る必要があります。

もちろん、オブジェクトインスタンスごとに1つのモジュールが存在するようにスクリプトモジュールを複製することも可能ですが、これはアプリケーションにかなり大きなオーバーヘッドを課すことになります。スクリプトクラスはそのようなオーバーヘッドを持ちません。すべてのインスタンスが同じモジュールを共有し、したがって同じバイトコードと関数IDなどを共有するからです。

## スクリプトクラスのインスタンス化 (Instantiating the script class)

スクリプトクラスをインスタンス化する前に、どのクラスをインスタンス化するかを知る必要があります。これをどのように行うかは正確にはアプリケーションに依存しますが、以下にいくつかの提案を示します。

もしアプリケーションがクラスの名前を（ハードコードまたは何らかの設定から）知っている場合、クラスの型はモジュールの [GetTypeIdByDecl](#asIScriptModule::GetTypeIdByDecl) をクラス名と共に呼び出すことで簡単に取得できます。アプリケーションはまた、クラスの何らかのプロパティ（例えばクラスが事前に定義された [インターフェース](#asIScriptEngine::RegisterInterface) を実装している場合など）を通じてクラスを識別することもできます。その場合、アプリケーションは [GetObjectTypeByIndex](#asIScriptModule::GetObjectTypeByIndex) でスクリプトに実装されているクラスの型を列挙し、[asITypeInfo](#asITypeInfo) インターフェースを通じて型を検査することができます。

第三の選択肢として、[スクリプトビルダーのアドオン](./doc_addon_build) を使用しているなら、メタデータを使用してクラスを識別することができます。このオプションを選択する場合は、[asIScriptModule](#asIScriptModule) を使用して宣言された型を列挙し、それらのメタデータについて [CScriptBuilder](./doc_addon_build) にクエリします。

オブジェクト型が判明したら、クラスのファクトリ関数を呼び出してインスタンスを作成します。必要な引数（例えばスクリプトクラスがバインドすべきアプリケーションオブジェクトへのポインタなど）を渡します。ファクトリ関数の ID は [asITypeInfo](#asITypeInfo) をクエリすることで見つかります。

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

// オブジェクトを保存する場合は参照をインクリメントしなければなりません。
// そうしないと、コンテキストが再利用または破棄された時にオブジェクトが破棄されてしまいます。
obj->AddRef();
```

ファクトリ関数は [通常のグローバル関数として呼び出され](./doc_call_script_func)、新しくインスタンス化されたクラスへのハンドルを返します。

## スクリプトクラスのメソッド呼び出し (Calling a method on the script class)

スクリプトクラスのメソッドを呼び出すことは、[グローバル関数の呼び出し](./doc_call_script_func) と似ていますが、[asITypeInfo](#asITypeInfo) から関数IDを取得し、残りの関数引数と合わせてオブジェクトポインタを設定しなければならない点が異なります。

```cpp
// クラスメソッドを表す関数オブジェクトを取得します
asIScriptFunction *func = type->GetMethodByDecl("void method()");

// メソッドを呼び出すためにコンテキストを準備します
ctx->Prepare(func);

// オブジェクトポインタをセットします
ctx->SetObject(obj);

// 呼び出しを実行します
ctx->Execute();
```

## スクリプトクラスの受け取り (Receiving script classes)

スクリプトクラスを受け取る関数をアプリケーションが登録するためには、まずその型を知る必要があります。もちろん、クラスはスクリプト内で宣言されているため、スクリプトがコンパイルされる前に型を知ることはできません。代わりに、アプリケーションはエンジンに [インターフェース](./doc_global_interface) を登録することができます。そうすれば、そのインターフェースへのハンドルを受け取るように関数を登録することができます。

```cpp
// インターフェースを登録します
engine->RegisterInterface("IMyObj");

// スクリプトクラスにそれらを実装することを強制したい場合、インターフェースにメソッドを登録することもできます
engine->RegisterInterfaceMethod("IMyObj", "void RequiredMethod()");

// インターフェースへのハンドルを受け取る関数を登録します
engine->RegisterGlobalFunction("void ReceiveMyObj(IMyObj @obj)", asFUNCTION(ReceiveMyObj), asCALL_CDECL);
```

インターフェースを受け取る関数は、[asIScriptObject](#asIScriptObject) へのポインタを取るように実装されるべきです。

```cpp
asIScriptObject *gObj = 0;
void ReceiveMyObj(asIScriptObject *obj)
{
  // オブジェクトで何かを行います
  if( obj )
  {
    if( doStore )
    {
      // オブジェクトを保存する場合、ハンドルを解放すべきではありません
      gObj = obj;
    }
    else
    {
      // オブジェクトを保存しない場合、返す前にハンドルを解放しなければなりません
      obj->Release();
    }
  }
}
```

このようにインターフェースを使用したくない場合は、[可変引数型](./doc_adv_var_type) や汎用の [スクリプトハンドルのアドオン](./doc_addon_handle) を検討してください。これらは事前に型が分からない値やオブジェクトを受け取るために使用できます。

## スクリプトクラスの返却 (Returning script classes)

登録された関数からスクリプトクラスを返すことは、[それを受け取ること](./doc_use_script_class_3) と多くの点で同じです。関数を登録するには、インターフェースを使用するか、汎用の [スクリプトハンドルのアドオン](./doc_addon_handle) を使用することができます。

```cpp
// グローバル変数は他の場所で初期化されます
asIScriptObject *gObj;

asIScriptObject *ReturnMyObj()
{
  if( gObj == 0 )
    return 0;

  // 返されたハンドルを計上するために参照カウントをインクリメントします
  gObj->AddRef();
  return gObj;
}
```

この関数は次のように登録することができます：

```cpp
// インターフェースを登録します
engine->RegisterInterface("IMyObj");

// インターフェースへのハンドルを返す関数を登録します
engine->RegisterGlobalFunction("IMyObj @ReturnMyObj()", asFUNCTION(ReturnMyObj), asCALL_CDECL);
```
