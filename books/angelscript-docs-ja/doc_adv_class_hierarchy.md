---
title: "クラス階層 (Class hierarchies)"
---

AngelScript は登録されたクラス間の関係を自動的に決定することができないため、スクリプト言語内での使用において階層構造（継承関係）を確立するためには、通常の [オブジェクト型の登録](./doc_register_type) を超えた追加の登録作業が必要になります。

現時点では、階層構造は [参照型](./doc_reg_basicref) に対してのみ登録可能であり、[値型](./doc_register_val_type) に対しては登録できません。

## 関係の確立 (Establishing the relationship)

2つの型が関連していることを AngelScript に知らせるには、参照キャスト演算子である [opCast](./doc_script_class_conv) と [opImplCast](./doc_script_class_conv) を登録する必要があります。`opCast` は、`cast<class>` 演算子を用いた明示的な呼び出しによるキャストのみを許可したい場合に使用されるべきです。`opImplCast` は、コンパイラが暗黙的にキャストを必要に応じて実行することを許可したい場合に使用されるべきです。

通常、派生型から基底型へのキャストには `opImplCast` を使用し、基底型から派生型へのキャストには `opCast` を使用することになるでしょう。

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

プリプロセッサがテンプレート宣言内の `,` をマクロの引数の区切り文字として解釈しないようにするため、`asFUNCTION` マクロに追加の括弧（ペア）を付ける必要があるかもしれないことに注意してください。

## 継承されたメソッドとプロパティ (Inherited methods and properties)

関係（階層）が自動的に決定されないのと同様に、AngelScript に継承されたメソッドやプロパティを派生型へ自動的に追加させる方法もありません。なぜなら、メソッドのポインタやプロパティのオフセットは基底クラスと派生クラスの間で異なる可能性があり、特に多重継承が使用されている場合には自動的にその違いを正確に決定する方法が存在しないからです。

このため、アプリケーションは派生クラス向けに継承されたすべてのメソッドとプロパティを登録する必要がありますが、これによって多少の重複コードが発生する可能性があります。しかし、少し賢い工夫をすればこの重複を避けることができるかもしれません。以下は、基底クラスと派生クラスのメソッドとプロパティを登録する例です（簡潔にするために振る舞いの登録は省略されています）：

派生型が基底型のメンバを隠蔽（シャドーイング）している場合、この方法での実装は不可能であることに注意してください。もしそのような場合は、基底型の隠蔽されたメンバを除外し、派生型で可視の各メンバを明示的に登録するしか方法はありません。

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
