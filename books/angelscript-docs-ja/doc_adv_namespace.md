---
title: "名前空間の使用 (Using namespaces)"
---

名前空間 (Namespaces) は、関連する関数やエンティティをグループ化するための仕組みです。名前空間を利用することで、同じ名前を持つ無関係なエンティティとの衝突を回避できます。

名前空間は、アプリケーション側で登録するインターフェースのほか、[スクリプト内](./doc_script_global#名前空間-(namespaces))でも定義・利用できます。

## 名前空間を用いたインターフェースの登録 (Registering the interface with namespaces)

特定の名前空間に関数や型を登録するには、まず `SetDefaultNamespace` メソッドを呼び出して対象の名前空間を指定します。その後の登録は、[API の登録](./doc_register_api)で説明されている通常の手順に従います。

```cpp
void RegisterInNamespace(asIScriptEngine *engine)
{
  int r;

  // 名前空間 "myspace" に型と関数を登録
  r = engine->SetDefaultNamespace("myspace"); assert( r >= 0 );
  r = engine->RegisterObjectType("mytype", 0, asOBJ_REF); assert( r >= 0 );
  r = engine->RegisterGlobalFunction("void myfunc()", asFUNCTION(myfunc), asCALL_CDECL); assert( r >= 0 );
}
```

名前空間は、スコープ解決演算子 (`::`) を使って `SetDefaultNamespace("outer::inner");` のようにネスト（入れ子）にすることも可能です。

## 名前空間内のエンティティの検索 (Finding entities in namespaces)

名前空間では同じシグネチャを持つ複数の宣言が可能なため、エンティティを検索する際には対象の名前空間を指定する必要があります。これも `SetDefaultNamespace` メソッドで行い、エンジンの `SetDefaultNamespace` とモジュールの `SetDefaultNamespace` の両方のインターフェースに適用されます。

```cpp
void FindFuncInNamespace(asIScriptModule *module)
{
  int r;

  // 名前空間内で関数を探します（つまり myspace::myfunc）
  r = module->SetDefaultNamespace("myspace"); assert( r >= 0 );
  asIScriptFunction *func1 = module->GetFunctionByName("myfunc");

  // 一致する宣言を検索する際、宣言自体に明示的な名前空間が与えられていない限りは
  // デフォルトの名前空間も使用されます。
  asIScriptFunction *funcA = module->GetFunctionByDecl("void myfunc()");
  asIScriptFunction *funcB = module->GetFunctionByDecl("void myspace::myfunc()");

  assert( funcA == funcB );
}
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_namespace.html
