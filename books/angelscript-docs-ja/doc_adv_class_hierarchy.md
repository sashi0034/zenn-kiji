---
title: "クラス階層 (Class hierarchies)"
---

AngelScript は登録されたクラス間の継承関係を自動的に判別することはできません。そのため、スクリプト言語内でクラス階層を確立するには、通常の [オブジェクト型の登録](./doc_register_type) に加えて、いくつかの追加の設定が必要になります。

現時点では、クラス階層の登録は [参照型](./doc_register_type#参照型の登録-registering-a-reference-type) に対してのみサポートされており、[値型](./doc_register_type#値型の登録-registering-a-value-type) では利用できません。

## 関係の確立 (Establishing the relationship)

2つの型に継承関係があることを AngelScript に認識させるには、参照キャスト演算子である [opCast](./doc_script_class_ops#型変換演算子-type-conversion-operators) または [opImplCast](./doc_script_class_ops#型変換演算子-type-conversion-operators) を登録します。`opCast` は、`cast<class>` 演算子を用いた明示的な型変換のみを許可する場合に使用します。一方、`opImplCast` は、必要に応じてコンパイラが暗黙的に型変換を行うことを許可する場合に使用します。

一般的には、派生型から基底型への変換には `opImplCast`（暗黙的キャスト）を使い、基底型から派生型への変換には `opCast`（明示的キャスト）を使用します。

```cpp
// opCast の振る舞いの例
template<class A, class B>
B* refCast(A* a)
{
    // ハンドルが既に null ハンドルである場合は、単に null ハンドルを返します
    if( !a ) return 0;

    // ポインタを目的の型へ動的にキャスト(dynamic_cast)しようと試みます
    B* b = dynamic_cast<B*>(a);
    if( b != 0 )
    {
        // キャストが成功したため、返されるハンドルの参照カウンターを増やす必要があります
        b->addref();
    }
    return b;
}

// 振る舞いの登録例
r = engine->RegisterObjectMethod("base", "derived@ opCast()", asFUNCTION((refCast<base,derived>)), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectMethod("derived", "base@ opImplCast()", asFUNCTION((refCast<derived,base>)), asCALL_CDECL_OBJLAST); assert( r >= 0 );

// ハンドルが読み取り専用 (const) の場合でもキャストが機能するように、const のオーバーロードも登録します
r = engine->RegisterObjectMethod("base", "const derived@ opCast() const", asFUNCTION((refCast<base,derived>)), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectMethod("derived", "const base@ opImplCast() const", asFUNCTION((refCast<derived,base>)), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

テンプレート宣言内のコンマ（`,`）がマクロ引数の区切り文字と誤認されるのを防ぐため、`asFUNCTION` マクロには二重の括弧が必要になる場合があることに注意してください。

継承関係を自動判別できないのと同様に、AngelScript が派生型に対して基底型のメソッドやプロパティを自動的に継承させる仕組みもありません。これは、特に多重継承を使用している場合、メソッドポインタやプロパティのオフセットが基底クラスと派生クラスで異なる可能性があり、その差異を自動的に特定する確実な方法がないためです。

そのため、アプリケーション側で派生クラスに対して継承されたすべてのメソッドやプロパティを再登録する必要があります。これにより登録コードにある程度の重複が生じますが、工夫次第でこれを最小限に抑えることが可能です。以下に、基底クラスと派生クラスのメンバを効率的に登録する例を示します（簡潔にするため振る舞いの登録は省略しています）。

なお、派生型が基底型のメンバを隠蔽（シャドーイング）している場合、この一括登録の手法は使えません。その場合は、派生型から見える各メンバを個別に明示的に登録する必要があります。

```cpp
// 基底クラス
class base
{
public:
  virtual void aMethod();
  
  int aProperty;
};

// 派生クラス
class derived : public base
{
public:
  virtual void aNewMethod();
  
  int aNewProperty;
};

// クラスを登録するためのコード
// これは、多重継承をサポートするためにテンプレート関数として実装されています
template <class T>
void RegisterBaseMembers(asIScriptEngine *engine, const char *type)
{
  int r;

  r = engine->RegisterObjectMethod(type, "void aMethod()", asMETHOD(T, aMethod), asCALL_THISCALL); assert( r >= 0 );
  
  r = engine->RegisterObjectProperty(type, "int aProperty", asOFFSET(T, aProperty)); assert( r >= 0 );
}

template <class T>
void RegisterDerivedMembers(asIScriptEngine *engine, const char *type)
{
  int r;

  // 基底メンバの登録関数を呼び出すことで、
  // 継承されたメンバを登録します
  RegisterBaseMembers<T>(engine, type);

  // その後、新しいメンバを登録します
  r = engine->RegisterObjectMethod(type, "void aNewMethod()", asMETHOD(T, aNewMethod), asCALL_THISCALL); assert( r >= 0 );

  r = engine->RegisterObjectProperty(type, "int aNewProperty", asOFFSET(T, aNewProperty)); assert( r >= 0 );
}

void RegisterTypes(asIScriptEngine *engine)
{
  int r;

  // 基底型を登録します
  r = engine->RegisterObjectType("base", 0, asOBJ_REF); assert( r >= 0 );
  RegisterBaseMembers<base>(engine, "base");

  // 派生型を登録します
  r = engine->RegisterObjectType("derived", 0, asOBJ_REF); assert( r >= 0 );
  RegisterDerivedMembers<derived>(engine, "derived");
}
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_class_hierarchy.html
