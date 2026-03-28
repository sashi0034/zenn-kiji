---
title: "テンプレート型 (Template types) / テンプレート関数 (Template functions)"
---

AngelScript のテンプレート型は、C++ のテンプレートと同様に機能します。スクリプト内では、サブタイプを指定することでテンプレート型の様々なバリエーションをインスタンス化できます。インスタンス化されたメソッドは、指定されたサブタイプに合わせて適応し、引数や戻り値の型が正しく処理されます。

AngelScript におけるテンプレート型の実装は、必ずしも C++ のテンプレートである必要はありません。代わりに、実行時にサブタイプに基づいて動的に処理を決定する汎用クラスとして実装できます。各型ごとに専用の実装を持つ C++ テンプレートに比べると効率は低下しますが、その分、柔軟性が得られます。パフォーマンスが必要な特定の型については、アプリケーション側で **テンプレートの特殊化 (Template Specialization)** を登録することで、最適化された実装を提供することも可能です。

これにより、未知の型に対する汎用的なサポートと、特定の既知の型に対する高いパフォーマンスを両立させることができます。

テンプレート型は [参照型](./doc_register_type#参照型の登録-(registering-a-reference-type)) または [値型](./doc_register_type#値型の登録-(registering-a-value-type)) のいずれとしても登録できます。手順は通常の型とほぼ同じですが、いくつか独自のルールがあります。

型名は、テンプレート名に続けてサブタイプ名を山括弧（`< >`）で囲んで宣言します。サブタイプが複数ある場合はコンマ（`,`）で区切ります。また、登録時には `asOBJ_TEMPLATE` フラグを指定して、これがテンプレート型であることを AngelScript に伝えます。

```cpp
// テンプレート型を GC 対応の参照型として登録
r = engine->RegisterObjectType("myTemplate<class T>", 0, asOBJ_REF | asOBJ_GC | asOBJ_TEMPLATE); assert( r >= 0 );

// 別のテンプレート型を値型として登録
r = engine->RegisterObjectType("myValueTemplate<class T>", sizeof(MyValueTempl), asOBJ_VALUE | asOBJ_TEMPLATE | asGetTypeTraits<MyValueTempl>()); assert( r >= 0 );
```

テンプレート型は必ずしもガベージコレクション (GC) に対応させる必要はありませんが、どのようなサブタイプで利用されるか予測できないため、基本的には GC サポートを実装しておくのが最善です。

メソッドやプロパティの登録時、型名は `myTemplate<T>` のように山括弧を含んだ形式で指定されますが、`class` キーワードは含めません。サブタイプ名は `RegisterObjectType` で宣言したものと同じ名前を使用します。

テンプレート型のファクトリやコンストラクタの振る舞いも特殊です。どのサブタイプでインスタンス化されているかを実装側が知るため、ファクトリやコンストラクタは隠しパラメータとして最初の引数にテンプレートインスタンスの `asITypeInfo` を受け取ります。ファクトリやコンストラクタを登録する際、この隠しパラメータは宣言に反映され、例えば `int &in` のように記述されます。

```cpp
// ファクトリの振る舞いを登録する
r = engine->RegisterObjectBehaviour("myTemplate<T>", asBEHAVE_FACTORY, "myTemplate<T>@ f(int&in)", asFUNCTIONPR(myTemplateFactory, (asITypeInfo*), myTemplate*), asCALL_CDECL); assert( r >= 0 );

// コンストラクタの振る舞いを登録する
r = engine->RegisterObjectBehaviour("myValueTemplate<T>", asBEHAVE_CONSTRUCT, "void f(int&in)", asFUNCTIONPR(myValueTemplConstructor, (asITypeInfo*, void*), void), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

初期化リストによってオブジェクトをインスタンス化するために使用されるリストファクトリやリストコンストラクタも同様の方法で登録します。

```cpp
// リストファクトリの振る舞いを登録する
r = engine->RegisterObjectBehaviour("myTemplate<T>", asBEHAVE_LIST_FACTORY, "myTemplate<T>@ f(int&in, uint)", asFUNCTIONPR(myTemplateListFactory, (asITypeInfo*, unsigned int), myTemplate*), asCALL_CDECL); assert( r >= 0 );

// リストコンストラクタの振る舞いを登録する
r = engine->RegisterObjectBehaviour("myValueTemplate<T>", asBEHAVE_LIST_CONSTRUCT, "void f(int&in, uint)", asFUNCTIONPR(myValueTemplListConstruct, (asITypeInfo*, unsigned int, void*), void), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

サブタイプは実行時に動的に決定される必要があるため、サブタイプを値渡しで受け取る関数や、値で返す関数を宣言することはできない点に注意してください。代わりに、メソッドや振る舞いがその型を**参照**で受け取るように設計する必要があります。オブジェクトハンドルを使用することは可能ですが、その場合、スクリプトエンジンはプリミティブや他の値型についてそのテンプレート型をインスタンス化できなくなります。

オブジェクトプロパティについても同様です。テンプレートは他のクラスと同様にプロパティを持つことができますが、登録時にはサブタイプのサイズが判明していないため、プロパティ自体の型をテンプレートのサブタイプに指定することはできません。

参照: [配列アドオン](./doc_addon#array-テンプレートオブジェクト)

#### テンプレートインスタンスのサブタイプ置換について (On subtype replacement for template instances)

テンプレート型が宣言（例えば変数の宣言）でインスタンス化されると、コンパイラはテンプレート型のすべてのメンバを列挙し、置換が必要なサブタイプが使用されているかを確認します。ほとんどのケースでは一対一の直接置換ですが、サブタイプが const 参照のパラメータとして使用されている場合は、期待する動作を得るために追加の指示が必要になる場合があります。

以下は、サブタイプ `T` を const ref として受け取るように登録されたメソッドの例です。

```cpp
r = engine->RegisterObjectMethod("array<T>", "int find(const T&in value) const", ...); 
```

もしこのテンプレートが、サブタイプとしてハンドルを指定してインスタンス化された場合（例：`array<Obj@>`）、このメソッドは次のようになります：

```cpp
  int find(Obj @const &in value) const
```

これは、パラメータが非読み取り専用（non-read only）の `Obj` へのハンドルを受け取ることを意味します。ハンドル自体を変更することはできませんが、ハンドルが参照するオブジェクトは依然としてメソッドによって変更される可能性があります。これは結果として、スクリプトが持っているハンドルが読み取り専用（const）である場合、そのメソッドを呼び出すことができなくなることを意味します。

メソッドが「読み取り専用のオブジェクトへのハンドルを許可すべきである」とアプリケーション開発者が宣言できるようにするために、特別なキーワード `if_handle_then_const` が用意されています。

```cpp
r = engine->RegisterObjectMethod("array<T>", "int find(const T&in if_handle_then_const value) const", ...); 
```

すると、メソッドは次のようになります：

```cpp
  int find(const Obj @const &in value) const
```

これは、パラメータが読み取り専用の `Obj` への const ハンドルを受け取ることを意味します。すなわち、ハンドル自体も、それが参照するオブジェクトインスタンスも、メソッドによって変更することはできません。これにより、スクリプトは読み取り専用ハンドルと非読み取り専用ハンドルのどちらでもこのメソッドを呼び出せるようになります。

### テンプレートの子関数定義 (Child funcdefs of templates)

funcdef（関数定義）を受け取るコールバックメソッドをテンプレート型に実装したい場合、その funcdef 自体がテンプレートのサブタイプに依存しているなら、その funcdef をテンプレート型の子 (child) として登録しなければなりません。

```cpp
// スコープとしてテンプレートを指定し、子 funcdef を登録する
r = engine->RegisterFuncdef("bool myTemplate<T>::callback(const T &in)"); assert( r >= 0 );

// コールバックのために定義された funcdef を参照またはハンドルとして受け取るメソッドを登録する
r = engine->RegisterObjectMethod("myTemplate<T>", "void doCallback(const callback &in)", asFUNCTION(...), asCALL_GENERIC); assert(r >= 0);
```

コールバック自体は、[コールバック (Callbacks)](./doc_callbacks) の項で説明されている通り、通常通り使用されます。

参照: [配列アドオン](./doc_addon#array-テンプレートオブジェクト) の `sort` メソッド

### コンパイル時のテンプレートインスタンス化の検証 (Validating template instantiations at compile time)

無効なテンプレートのインスタンス化に対する不要な実行時の検証を避けるため、アプリケーションは優先的に `asBEHAVE_TEMPLATE_CALLBACK` の振る舞いを登録すべきです。これは、スクリプトエンジンが新しいテンプレートインスタンスの型を生成するたびに呼び出される特別な振る舞いの関数です。コールバック関数は必要な検証を実行し、その型が処理可能であるかどうかを確認し、処理できない場合はエンジンにそのインスタンス機能がサポートされていないことを伝えることができます。

コールバック関数は `asITypeInfo` のポインタを受け取り、真偽値（boolean）を返すグローバル関数でなければなりません。テンプレートインスタンスが有効である場合、戻り値は `true` であるべきです。

この関数はまた、boolean の出力参照を第2パラメータとして受け取る必要があります。そのテンプレートインスタンスがガベージコレクションされるべきではない場合は、関数によってこのパラメータが `true` に設定されるべきです。これにより AngelScript はそのオブジェクト型について `asOBJ_GC` フラグをクリアします。テンプレートインスタンスが循環参照を形成し得ない場合、ガベージコレクションの必要はありません。これを行うことでガベージコレクターによる作業負担を軽減できます。

```cpp
// テンプレートのコールバックを登録する
// asITypeInfo ポインタの引数は int の参照として表現されることに注目してください
r = engine->RegisterObjectBehaviour("myTemplate<T>", asBEHAVE_TEMPLATE_CALLBACK, "bool f(int &in, bool&out)", asFUNCTION(myTemplateCallback), asCALL_CDECL); assert( r >= 0 );
```

以下はコールバック関数の例です：

```cpp
bool myTemplateCallback(asITypeInfo *ot, bool &dontGarbageCollect)
{
  // このテンプレートはプリミティブ型のみをサポートします
  int typeId = ot->GetSubTypeId();
  if( typeId & asTYPEID_MASK_OBJECT )
  {
    // スクリプトがオブジェクト型でテンプレートをインスタンス化しようとしていますが、
    // これは許可されません。
    return false;
  }
  
  // このインスタンスではガベージコレクションが不要であることを AngelScript に伝えます
  dontGarbageCollect = true;
    
  // プリミティブ型なので許可します
  return true;
}
```

## テンプレートの特殊化 (Template Specialization)

テンプレートの特殊化（Template Specialization）を登録すると、スクリプトがテンプレート型を含む宣言をコンパイルする際に通常行われる、AngelScript 側のインスタンス化処理がオーバーライドされます。これにより、アプリケーションは特定のサブタイプに対して、独自の実装を持つ全く異なるオブジェクトを登録できるようになります。当然ながら、スクリプト開発者に対して透過的（意識させない状態）であるように特殊化を登録することが推奨されます。つまり、テンプレート型とその特殊化との間で、メソッド名や振る舞いが異なるような設計は避けるべきです。

型名を除けば、テンプレートの特殊化は[通常の型](./doc_register_type)と全く同じように登録されます。テンプレートの特殊化は、ベースとなるテンプレートと同じネームスペース（名前空間）に登録されなければなりません。

```cpp
// float サブタイプに対するテンプレートの特殊化を登録する
r = engine->RegisterObjectType("myTemplate<float>", 0, asOBJ_REF); assert( r >= 0 );
  
// ファクトリを登録する（特殊化の場合、隠しパラメータはありません）
r = engine->RegisterObjectBehaviour("myTemplate<float>", asBEHAVE_FACTORY, "myTemplate<float>@ f()", asFUNCTIONPR(myTemplateFloatFactory, (), myTemplateFloat*), asCALL_CDECL); assert( r >= 0 );
```

---

## テンプレート関数 (Template functions)

テンプレート関数は [ジェネリック呼び出し規約](./doc_generic) を用いて実装することができ、エンジンに対して [グローバル関数](./doc_register_func) または [オブジェクトメソッド](./doc_register_type#オブジェクトメソッドの登録-(registering-object-methods)) として登録できます。

テンプレート関数が呼び出されると、関数は `GetArgTypeId`、もしくは `GetSubTypeId` を使用して引数の型を決定することができます。

```cpp
// グローバルなテンプレート関数を登録する
r = engine->RegisterGlobalFunction("T Test<T, U>(T t, U u)", asFUNCTION(ScriptTestGen), asCALL_GENERIC); assert( r >= 0 );
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_template.html
