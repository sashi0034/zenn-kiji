---
title: "関数定義とスクリプトのコールバック関数 (Funcdefs and script callback functions)"
---

[Funcdef（関数定義）](./doc_script_global#funcdef-関数定義) はコールバックのための関数シグネチャを定義するために使用されます。この funcdef はその後、一致するシグネチャを持つ関数へのハンドルを保持できる変数または関数パラメータを宣言するために使用されます。

アプリケーションがスクリプトから呼び出されるコールバックをスクリプトに設定させる意図がある場合、アプリケーションはアプリケーションインターフェースの一部として `RegisterFuncdef` も登録することができます。これが完了すると、アプリケーションは関数ハンドルを `asIScriptFunction` ポインタとして受け取り、通常の [スクリプト関数の呼び出し](./doc_call_script_func) と同様に実行することができます。

## 例 (An example)

アプリケーションが何らかのイベントで呼び出されるコールバックをスクリプトに設定させる必要があるとします。これを行うにあたり、アプリケーションはまずコールバックのシグネチャを定義する funcdef を登録します。次に、スクリプトからコールバックを設定するために使用される関数を登録する必要があります。

```cpp
  // コールバックのためのシンプルな funcdef を登録します
  engine->RegisterFuncdef("void CallbackFunc()"); 
  
  // コールバックを設定するための関数を登録します
  engine->RegisterGlobalFunction("void SetCallback(CallbackFunc @cb)", asFUNCTION(SetCallback), asCALL_CDECL);  
```

このインターフェースにより、スクリプトは次のようにコールバックを設定できるようになります：

```angelscript
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

実際のコールバックを呼び出す時が来たら、アプリケーションは他の [スクリプト関数の呼び出し](./doc_call_script_func) と同様にスクリプトコンテキストを使用します。

もちろん、コールバックは [デリゲート](./doc_script_datatypes#デリゲート-delegates) と合わせて使用することもできます。デリゲートはオブジェクトへの参照と、そのオブジェクトに対して呼び出すべきメソッドを保持する特殊な関数オブジェクトです。もしアプリケーションがそれらを扱う方法がまさにこれなら、上記の例はまったく同じように機能し、コールバックが実際にグローバル関数であるかデリゲートオブジェクトであるかについてアプリケーションが意識する必要はありません。

しかし場合によっては、デリゲートを分解し、アプリケーションが実際のオブジェクトとメソッドを別々に保存することが有益な場合があります。例えば、アプリケーションがオブジェクトを必要以上に長く生存させないようにするために [弱い参照 (weak reference)](./doc_adv_weakref) を使用すべき場合などです。以下はデリゲートの内部情報を取得する方法を示しています：

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
デリゲートは `asIScriptFunction` インターフェースを使用しますが、実際の関数ではありません。このため、デリゲートはどのモジュールにも所有されません（つまり `GetModule` は常に null を返します）。同様に、特定の関数 ID も持ちません（つまり `GetId` は 0 を返します）。
:::

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_callbacks.html
