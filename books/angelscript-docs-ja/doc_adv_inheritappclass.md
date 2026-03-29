---
title: "アプリケーションが登録したクラスからの継承 (Inheriting from application registered class)"
---

スクリプトクラスは C++ クラスのようにネイティブな機械語にコンパイルされるわけではないため、アプリケーション側で登録したクラスから直接継承することはできません。

しかし、抽象化レイヤーを用いて実装の差異を隠蔽する「プロキシクラス (Proxy Class)」を使用することで、継承をエミュレート（模倣）することは可能です。プロキシクラスは2つの部分から構成されます。1つはアプリケーションが扱う C++ 側であり、もう 1つはスクリプトから継承可能なスクリプト側です。

以下は、そのようなプロキシクラスの実装例です。

```cpp
// C++ 側
class FooScripted
{
public:
  // スクリプトがオーバーライドできるようにしたい公開（パブリック）インターフェース 
  void CallMe()
  {
    // スクリプト側がまだ生存していれば、スクリプト化された関数を呼び出します
    if( !m_isDead->Get() )
    {
      // 呼び出しを行っているのがスクリプトクラスのインスタンス自身ではないことを確認します
      // そうである場合は、無限再帰を避けるためにスクリプトへのコールバックを行いません
      asIScriptContext* ctx = asGetActiveContext();
      asIScriptFunction* func = ctx ? ctx->GetFunction(0) : 0;
      if (!func || strcmp(func->GetName(), "CallMe") != 0 || !ctx || ctx->GetThisPointer(0) != m_obj)
      {
        // スクリプト関数 CallMe を呼び出し、スクリプトがオーバーロードされた振る舞いを提供できるようにします
        asIScriptEngine* engine = m_obj->GetEngine();
        ctx = engine->RequestContext();

        // GetMethodByDecl はスクリプトクラスの仮想関数を返します。
        // これによって、それを呼び出した際に VM は派生したメソッドを実行します
        ctx->Prepare(m_obj->GetObjectType()->GetMethodByDecl("void CallMe()"));
        ctx->SetObject(m_obj);
        ctx->Execute();

        engine->ReturnContext(ctx);
      }
    }
  }

  int m_value;

  // スクリプト側で作成するために使用できるファクトリ関数
  static FooScripted *Factory()
  {
    asIScriptContext *ctx = asGetActiveContext();

    // ファクトリを呼び出している関数を取得し、それが FooScript スクリプトクラスであることを確実にします
    asIScriptFunction *func = ctx->GetFunction(0);
    if( func->GetObjectType() == 0 || std::string(func->GetObjectType()->GetName()) != "FooScripted" )
    {
      ctx->SetException("Invalid attempt to manually instantiate FooScript_t");
      return 0;
    }

    // FooScript C++ クラスが FooScript スクリプトクラスとリンクされるように、
    // 呼び出し元の関数から this ポインタを取得します
    asIScriptObject *obj = reinterpret_cast<asIScriptObject*>(ctx->GetThisPointer(0));

    return new FooScripted(obj);
  }

  // 参照カウント
  void AddRef()
  {
    m_refCount++;

    // スクリプト側への参照カウンターもインクリメントし、
    // C++側より先にスクリプト側が誤って破棄されないようにします
    if( !m_isDead->Get() )
      m_obj->AddRef();
  }
  void Release()
  { 
    // スクリプトインスタンスも解放します
    if( !m_isDead->Get() )
      m_obj->Release();

    if( --m_refCount == 0 ) delete this;
  }

  // 代入演算子
  FooScripted &operator=(const FooScripted &o)
  {
    // コンテンツのみをコピーし、スクリプトプロキシクラスはコピーしません
    m_value = o.m_value;
    return *this;
  }

protected:

  // コンストラクタとデストラクタは間接的に呼び出されます
  FooScripted(asIScriptObject *obj) : m_obj(0), m_isDead(0), m_value(0), m_refCount(1)
  {
    // スクリプトオブジェクトの弱参照 (weak ref) フラグを取得し、
    // スクリプトクラスへの強い参照を保持することを避けます
    m_isDead = obj->GetWeakRefFlag();
    m_isDead->AddRef();

    m_obj = obj;
  }

  ~FooScripted()
  {
    // 弱参照フラグを解放します
    m_isDead->Release();
  }

  // 参照カウント
  int m_refCount;

  // C++ 側とスクリプト側との間の循環参照を避けるために、
  // C++ 側はスクリプト側への弱いリンクを保持します
  asILockableSharedBool *m_isDead;
  asIScriptObject *m_obj;
};
```

この型は次のようにエンジンに登録されます：

```cpp
void RegisterFooScripted(asIScriptEngine *engine)
{
  engine->RegisterObjectType("FooScripted_t", 0, asOBJ_REF);
  engine->RegisterObjectBehaviour("FooScripted_t", asBEHAVE_FACTORY, "FooScripted_t @f()", asFUNCTION(FooScripted::Factory), asCALL_CDECL);
  engine->RegisterObjectBehaviour("FooScripted_t", asBEHAVE_ADDREF, "void f()", asMETHOD(FooScripted, AddRef), asCALL_THISCALL);
  engine->RegisterObjectBehaviour("FooScripted_t", asBEHAVE_RELEASE, "void f()", asMETHOD(FooScripted, Release), asCALL_THISCALL);
  engine->RegisterObjectMethod("FooScripted_t", "FooScripted_t &opAssign(const FooScripted_t &in)", asMETHOD(FooScripted, operator=), asCALL_THISCALL);
  engine->RegisterObjectMethod("FooScripted_t", "void CallMe()", asMETHOD(FooScripted, CallMe), asCALL_THISCALL);
  engine->RegisterObjectProperty("FooScripted_t", "int m_value", asOFFSET(FooScripted, m_value));
}
```

スクリプト側はすべてのスクリプトモジュールで使用できるように [共有 (shared)](./doc_script_shared) として宣言されます。
また、[抽象 (abstract)](./doc_script_class#final,-abstract,-override) としても宣言されるため、単独でインスタンス化することはできず、他のスクリプトクラスの親クラスとしてのみインスタンス化できます。

このスクリプトセクションは、`FooScripted` クラスから派生できる必要のあるすべてのモジュールにおいて、アプリケーションによって自動的にインクルードされるのが望ましいです。

```c++ (as)
  // スクリプト側
  shared abstract class FooScripted
  {
    // スクリプトがインスタンスを作成できるようにします
    FooScripted()
    {
      // プロキシの C++ 側を作成します
      @m_obj = FooScripted_t();  
    }

    // コピーコンストラクタはディープコピーを実行します
    FooScripted(const FooScripted &in o)
    {
      // 新しい C++ インスタンスを作成し、コンテンツをコピーします
      @m_obj = FooScripted_t();
      m_obj = o.m_obj;
    }

    // C++ オブジェクトのディープコピーを行います
    FooScripted &opAssign(const FooScripted &in o)
    {
      // C++ インスタンスのコンテンツをコピーします
      m_obj = o.m_obj;
      return this;
    }

    // スクリプト側は C++ 側に呼び出しを転送します
    void CallMe() { m_obj.CallMe(); }

    // C++ 側のプロパティはアクセサを通じてスクリプトに公開されます
    int m_value 
    {
      get { return m_obj.m_value; }
      set { m_obj.m_value = value; }
    }

    // スクリプトクラスは opImplCast メソッドを通じて C++ の型に暗黙的にキャストできます
    FooScripted_t @opImplCast() { return m_obj; }
    
    // プロキシの C++ 側への参照を保持します
    private FooScripted_t @m_obj;
  }
```

これで、スクリプトクラスは `FooScripted` クラスから派生し、通常通り親クラスのプロパティやメソッドにアクセスできるようになります。

```c++ (as)
  // アプリケーションクラスから派生したスクリプトクラスを実装します
  class FooDerived : FooScripted
  {
    void CallMe()
    {
       m_value += 1;
    }
  }

  void main()
  {
    // 新しく作成された時、m_value は 0 です
    FooDerived d;
    assert( d.m_value == 0 );

    // メソッドを呼び出すと m_value は 1 増加します
    d.CallMe();
    assert( d.m_value == 1 );
  }
```

もちろん、アプリケーションから「スクリプト化されたクラス（継承クラス）」のインスタンスを生成し、`FooScripted` C++ プロキシを介してアクセスすることも可能です。これにより、アプリケーションの他の部分に対して、実際の実装がスクリプト内で行われているという事実を透過的（意識させない状態）にできます。

```cpp
FooScripted *CreateFooDerived(asIScriptEngine *engine)
{
  // FooScripted C++ クラスを継承する FooDerived スクリプトクラスのインスタンスを作成します
  asIScriptObject *obj = reinterpret_cast<asIScriptObject*>(engine->CreateScriptObject(mod->GetTypeInfoByName("FooDerived")));

  // FooScripted クラスの C++ 側へのポインタを取得します
  FooScripted *obj2 = *reinterpret_cast<FooScripted**>(obj->GetAddressOfProperty(0));

  // これがアプリケーション側からオブジェクトのライフタイムを制御するために使用されるため、
  // C++ オブジェクトの参照カウントを増やします 
  obj2->AddRef();

  // スクリプト側への参照を解放します
  obj->Release();

  return obj2;
}

void Foo(asIScriptEngine *engine)
{
  FooScripted *obj = CreateFooDerived(engine);

  // オブジェクトが作成されると、アプリケーションは実装が実際にはスクリプトで行われていることを
  // 知らなくても、通常通り FooScripted ポインタを通じてオブジェクトにアクセスできます。

  // 新しく作成された時、m_value は 0 です
  assert( obj->m_value == 0 );

  // メソッドを呼び出すと、スクリプトによって m_value が 1 増加します
  obj->CallMe();
  assert( obj->m_value == 1 );

  // オブジェクトを解放してインスタンスを破棄します（これによってスクリプト側も破棄されます）
  obj->Release();
}
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_inheritappclass.html
