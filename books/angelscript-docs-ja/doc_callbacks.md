---
title: "関数定義とスクリプトのコールバック関数 (Funcdefs and script callback functions)"
---

[Funcdef（関数定義）](./doc_script_global#funcdef-(関数定義)) は、コールバックに使用される関数シグネチャを定義するために使用されます。定義された funcdef は、そのシグネチャに一致する関数へのハンドルを保持できる変数や関数パラメータを宣言する際に利用されます。

アプリケーション側でも、インターフェースの一部として `RegisterFuncdef` を使用して [Funcdef](./doc_script_global#funcdef-(関数定義)) を登録できます。これは、スクリプト側で設定されたコールバックをアプリケーションから呼び出したい場合に有効です。登録後は、アプリケーションは関数ハンドルを `asIScriptFunction` ポインタとして受け取ることができ、通常の [スクリプト関数の呼び出し](./doc_call_script_func) 手順に従って実行できるようになります。

## 実装例 (An example)

アプリケーションで特定のイベントが発生した際に、スクリプト側で設定されたコールバックを呼び出せるようにしたい場合を考えます。まず、アプリケーション側でコールバックのシグネチャを定義する Funcdef を登録します。次に、スクリプトからコールバックを設定するための関数を登録します。

```cpp
  // コールバックのためのシンプルな funcdef を登録します
  engine->RegisterFuncdef("void CallbackFunc()"); 
  
  // コールバックを設定するための関数を登録します
  engine->RegisterGlobalFunction("void SetCallback(CallbackFunc @cb)", asFUNCTION(SetCallback), asCALL_CDECL);  
```

このインターフェースにより、スクリプトは次のようにコールバックを設定できるようになります：

```c++ (as)
  void main()
  {
    // アプリケーションに呼び出すスクリプト関数を伝えます
    SetCallback(MyCallback);
  }
  
  // シグネチャは登録された CallbackFunc funcdef と一致します
  void MyCallback()
  {
    ...
  }
```

`SetCallback` 関数の実装は次のようになるかもしれません：

```cpp
  // コールバックはスクリプト関数です。
  // エンジンをクリーンアップする前にこれを解放することを忘れないでください。
  asIScriptFunction *callback = 0;
  
  void SetCallback(asIScriptFunction *cb)
  {
    // 以前のコールバックがあれば解放します
    if( callback )
      callback->Release();

    // 後で使用するために受け取ったハンドルを保存します
    callback = cb;

    // もう使用されなくなるまで受け取ったスクリプト関数を解放しないでください
  }
```

実際のコールバックを呼び出す際、アプリケーションは他の [スクリプト関数の呼び出し](./doc_call_script_func) と同様にスクリプトコンテキストを使用します。

## デリゲート (Delegates)

もちろん、コールバックは [デリゲート](./doc_script_datatypes#デリゲート-(delegates)) と組み合わせて使用することも可能です。デリゲートは、オブジェクトへの参照とそのオブジェクトに対して呼び出すべきメソッドをペアで保持する、特殊な関数オブジェクトです。アプリケーションでデリゲートをそのまま扱う場合は、上記の例と全く同様に機能し、アプリケーション側がコールバックの実体がグローバル関数なのかデリゲートなのかを意識する必要はありません。

しかし、状況によってはデリゲートを分解し、アプリケーション側で実際のオブジェクトとメソッドを別々に保存した方が都合が良い場合があります。例えば、オブジェクトを必要以上に長く生存させないために、[弱参照 (Weak Reference)](./doc_adv_weakref) を利用してオブジェクトを保持したい場合などです。以下のコードは、デリゲートの内部情報を取り出す方法を示しています。

```cpp
  // コールバックと、コールバックがクラスメソッドの場合は対応するオブジェクト
  asIScriptFunction *callback           = 0;
  void              *callbackObject     = 0;
  asITypeInfo       *callbackObjectType = 0;
  
  void SetCallback(asIScriptFunction *cb)
  {
    // 以前のコールバックがあれば解放します
    if( callback )
      callback->Release();
    if( callbackObject )
      engine->ReleaseScriptObject(callbackObject, callbackObjectType);
    callback           = 0;
    callbackObject     = 0;
    callbackObjectType = 0;
    
    if( cb && cb->GetFuncType() == asFUNC_DELEGATE )
    {
      callbackObject     = cb->GetDelegateObject();
      callbackObjectType = cb->GetDelegateObjectType();
      callback           = cb->GetDelegateFunction();
 
      // オブジェクトとメソッドを保持します
      engine->AddRefScriptObject(callbackObject, callbackObjectType);
      callback->AddRef();
  
      // デリゲートはもう使用されないため、解放します
      cb->Release();
    }
    else
    {
      // 後で使用するために受け取ったハンドルを保存します
      callback = cb;

      // もう使用されなくなるまで受け取ったスクリプト関数を解放しないでください
    }
  }
```

:::message
デリゲートは `asIScriptFunction` インターフェースを使用しますが、実体は通常の関数ではありません。このため、デリゲートはどのモジュールにも所属しません（`GetModule` は常に null を返します）。同様に、特定の関数 ID も持ちません（`GetId` は常に 0 を返します）。
:::

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_callbacks.html
