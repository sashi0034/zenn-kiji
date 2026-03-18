---
title: "弱参照 (Weak references)"
---

AngelScript は [ガベージコレクター (GC)](./doc_gc) を用いて循環参照を解決しますが、それとは別に「弱参照 (Weak Reference)」が役立つ場面もあります。弱参照は、特定のオブジェクトへのアクセス手段は保持しておきたいが、そのオブジェクトを必要以上に生存させたくない（参照カウントによる寿命の延長を避けたい）場合に特に有効です。

AngelScript は、共有真偽値（Shared Boolean）を用いることで弱参照をサポートしています。オブジェクトへの弱参照を保持したいコードは、そのオブジェクトから共有真偽値である「弱参照フラグ (Weakref Flag)」を取得します。そして、オブジェクトのポインタを利用する前に、オブジェクトがまだ生存しているかどうかをこのフラグで確認します。

スクリプトクラスは、開発者が何もしなくても自動的に弱参照をサポートします。対照的に、アプリケーションで登録する型で弱参照をサポートするには、`asBEHAVE_GET_WEAKREF_FLAG` の振る舞いを登録し、オブジェクト破棄時にフラグをセットするロジックを自前で実装する必要があります。

以下は、スレッドセーフな実装例です：

```cpp
class MyClass
{
public:
  MyClass() { refCount = 1; weakRefFlag = 0; }
  void AddRef() { asAtomicInc(refCount); }
  void Release() 
  {
    // weak ref フラグが存在する場合、それは誰かが弱参照を保持したためであり、
    // またその誰かがいつでもオブジェクトへの参照を追加する可能性があります。
    // ここでロックを行わずに weakRefFlag の存在を確認しても大丈夫です。
    // なぜなら、もし refCount が 1 であれば、現在他のスレッドが 
    // weakRefFlag を作成していることはあり得ないからです。
    if( refCount == 1 && weakRefFlag )
    {
      // オブジェクトがもはや生存していないことを他者に伝えるためにフラグを設定します
      // このスレッドがオブジェクトを破棄しようとする処理と、他のスレッドが
      // 弱参照から一時的に強参照を追加しようとする処理との間で競合状態 (race condition)
      // が発生しないように、refCount を 0 に減らす前にこれを実行しなければなりません。
      weakRefFlag->Set(true);
    }

    if( asAtomicDec(refCount) == 0 ) 
      delete this; 
  }
  asILockableSharedBool *GetWeakRefFlag()
  {
    if( !weakRefFlag )
    {
      // 他のどのスレッドも同時に共有 boolean の作成を試みることができないように、
      // グローバルにロックをかけます
      asAcquireExclusiveLock();

      // ロックを待っている間に他のスレッドがフラグを作成していないことを確認します
      if( !weakRefFlag )
        weakRefFlag = asCreateLockableSharedBool();

      asReleaseExclusiveLock();
    }

    return weakRefFlag;
  }

  static MyClass *Factory() { return new MyClass(); }

protected:
  ~MyClass()
  {
    // 弱参照を保持しているコードによってまだアクセスされる可能性のある、
    // 弱参照フラグを解放します
    if( weakRefFlag )
      weakRefFlag->Release();
  }

  int refCount;
  asILockableSharedBool *weakRefFlag;
};
```

このクラスに対する `asBEHAVE_GET_WEAKREF_FLAG` の振る舞いは、次のように登録されます：

```cpp
engine->RegisterObjectType("MyClass", 0, asOBJ_REF);
engine->RegisterObjectBehaviour("MyClass", asBEHAVE_ADDREF, "void f()", asMETHOD(MyClass, AddRef), asCALL_THISCALL);
engine->RegisterObjectBehaviour("MyClass", asBEHAVE_RELEASE, "void f()", asMETHOD(MyClass, Release), asCALL_THISCALL);
engine->RegisterObjectBehaviour("MyClass", asBEHAVE_GET_WEAKREF_FLAG, "int &f()", asMETHOD(MyClass, GetWeakRefFlag), asCALL_THISCALL);
```

スクリプト言語自体には、弱参照用の組み込み構文はありません。その代わりに、スクリプト内でこの機能を提供したいアプリケーションのために、標準の [Weakref アドオン](./doc_addon#weakref-オブジェクト) が用意されています。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_weakref.html
