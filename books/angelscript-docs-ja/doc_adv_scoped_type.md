---
title: "スコープ付き参照型の登録 (Registering a scoped reference type)"
---

一部の C++ 値型には、メモリ上の配置に関する特別な要件（特定のアライメントやメモリプーリングなど）があります。AngelScript は値型がどこにどのように割り当てられるかを細かく制御できないため、こうした型は参照型として登録する必要があります。この際、その型を**スコープ付き参照型 (scoped reference type)** として定義するのが適切です。

スコープ付き参照型の寿命は、そのインスタンスを生成した変数のスコープ（生存範囲）によって管理されます。変数がスコープを外れると、インスタンスは即座に破棄されます。そのため、この型に対するオブジェクトハンドルを取得することはできません。

スコープ付き参照型では、`release` の振る舞いのみを登録する必要があります。`addref` の登録は許可されていません。ファクトリの振る舞いを登録しなければ、スクリプト内で直接インスタンスを生成することはできませんが、アプリケーション側からパラメータとして受け取ることは可能です。

この型はハンドル（共有参照）を持つことができないため、参照カウントを追跡する必要はありません。つまり、`release` が呼び出された時点で、即座にオブジェクトを破棄（メモリ解放）して構いません。

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

スコープ付きの型は実際にはハンドルをサポートしていませんが、この関数がハンドル（`@`）を介してスコープ付きの値を返すように登録されている点に注目してください。これは、AngelScript が返されたインスタンスの処理を終えた後に、確実に `release` を呼び出して破棄が行われるようにするためです。

参照: [参照型の登録](./doc_register_type#参照型の登録-registering-a-reference-type)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_scoped_type.html
