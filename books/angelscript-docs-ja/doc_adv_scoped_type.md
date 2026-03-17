---
title: "スコープ付き参照型の登録 (Registering a scoped reference type)"
---

一部の C++ の値型 (value type) は、それが配置されるメモリに対して、例えば特定のアライメント要件やメモリプーリングなど特別な要件を持っています。AngelScript は値型がどこにどのように割り当てられるかについてそこまでの制御を提供していないため、これらの型は参照型として登録する必要があります。この場合、その型を**スコープ付き参照型 (scoped reference type)** として登録することになります。

スコープ付き参照型の寿命は、それをインスタンス化する変数のスコープによって制御されます。すなわち、変数がスコープ外に出た瞬間にインスタンスは破棄されます。これは、その型に対してハンドルを取得することが許可されていないことを意味します。

スコープ付き参照型には release の振る舞いの登録のみが必要です。addref の振る舞いは許可されていません。もしファクトリの振る舞いが登録されていなければ、スクリプトはこの型のオブジェクトをインスタンス化することはできませんが、それでもアプリケーションからパラメータとして受け取ることは可能です。

このオブジェクト型に対してハンドルを取得することはできないため、オブジェクトへ保持されている参照の数を追跡する必要はありません。これは、release の振る舞いが呼び出され次第、ただちにオブジェクトを破棄してメモリ割り当てを解除すればよいことを意味します。

```cpp
scoped *Scoped_Factory()
{
  return new scoped;
}

void Scoped_Release(scoped *s)
{
  if( s ) delete s;
}

// スコープ付き参照型を登録する
r = engine->RegisterObjectType("scoped", 0, asOBJ_REF | asOBJ_SCOPED); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("scoped", asBEHAVE_FACTORY, "scoped @f()", asFUNCTION(Scoped_Factory), asCALL_CDECL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("scoped", asBEHAVE_RELEASE, "void f()", asFUNCTION(Scoped_Release), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

残念ながら、C++ 側でこの型を値によって受け取ったり返したりするすべての関数は、AngelScript がその値の寿命を管理できるようにするためにラップされなければなりません。

以下は、ある値を受け取り別の値を返す関数と、それに対応するラッパーの例です。

```cpp
scoped Foo(scoped a)
{
  scoped b;
  return b;
}

scoped *Foo_wrapper(const scoped &a)
{
  return new scoped(Foo(a));
}

// 関数を登録する
r = engine->RegisterGlobalFunction("scoped @Foo(const scoped &in)", asFUNCTION(Foo_wrapper), asCALL_CDECL); assert( r >= 0 );
```

スコープ付きの型は実際にはハンドルをサポートしていませんが、この関数がハンドルによってスコープ付きの値を返すように登録されている点に注目してください。これは、AngelScript が受け取った値の処理を終えた後に、返されたインスタンスに対して Release を呼び出すようにするために行われます。

参照: [参照型の登録](./doc_reg_basicref)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_scoped_type.html
