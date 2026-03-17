---
title: "弱参照 (Weak references)"
---

AngelScript は循環参照を解決するために [ガベージコレクター](./doc_gc) を使用しますが、それでも弱参照 (weak reference) が役立つ場合があります。弱参照は特に、あるオブジェクトが他のオブジェクトにアクセスできる状態を保ちたいが、必要以上にそれらを延命させたくないというシナリオで有用です。

AngelScript は、共有真偽値 (shared boolean) を用いて弱参照をサポートしています。オブジェクトへの弱参照を保持したいコードは、そのオブジェクトから共有真偽値である weakref フラグを取得し、オブジェクトへのポインタを使用する前に、オブジェクトがもはや生存していないことを示すためにこのフラグが設定されていないかを確認する必要があります。

スクリプトクラスは、スクリプトライターが何も行わなくても自動的に弱参照をサポートします。一方で、アプリケーションから登録された型の場合は、振る舞い [asBEHAVE_GET_WEAKREF_FLAG](#asBEHAVE_GET_WEAKREF_FLAG) を登録し、オブジェクトの破棄時にフラグを設定するロジックを実装する必要があります。

以下のコードは、スレッドセーフな実装を行う方法を示しています：

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

スクリプト言語自体には、弱参照用の組み込みの構文はありません。その代わりに、スクリプト内でこのサポートを提供したいアプリケーションのために、これを提供する標準の [weakref アドオン](./doc_addon_weakref) が実装されています。
