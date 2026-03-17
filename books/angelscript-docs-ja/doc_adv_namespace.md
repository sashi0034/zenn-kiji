---
title: "名前空間の使用 (Using namespaces)"
---

名前空間 (Namespaces) は、関連する関数やその他のエンティティをまとめてグループ化するために使用されます。そうすることで、たまたま同じ名前を使用しているが他には無関係な他のエンティティとの潜在的な衝突（コンフリクト）を避けることができます。

名前空間はアプリケーションが登録するインターフェースだけでなく、[スクリプト](./doc_global_namespace) でも使用することができます。

## 名前空間を用いたインターフェースの登録 (Registering the interface with namespaces)

特定の名前空間に関数やその他のエンティティを登録するには、アプリケーションはまず [SetDefaultNamespace](#asIScriptEngine::SetDefaultNamespace) メソッドを呼び出して希望する名前空間を定義すべきです。その後は、[インターフェースの登録に関する章](./doc_register_api_topic) で説明されている通常の手順に従って登録を行います。

```cpp
void RegisterInNamespace(asIScriptEngine *engine)
{
  int r;

  // 名前空間に型と関数を登録します
  r = engine->SetDefaultNamespace("myspace"); assert( r >= 0 );
  r = engine->RegisterObjectType("mytype", 0, asOBJ_REF); assert( r >= 0 );
  r = engine->RegisterGlobalFunction("void myfunc()", asFUNCTION(myfunc), asCALL_CDECL); assert( r >= 0 );
}
```

もし希望するのであれば、スコープトークン (`::`) で区切ることでネストされた（入れ子にされた）名前空間を使用することもできます。例：
`SetDefaultNamespace("outer::inner");`

## 名前空間内のエンティティの検索 (Finding entities in namespaces)

名前空間は同じシグネチャを持つ複数の宣言を許可するため、エンティティの検索をどの名前空間で行うかを指定する必要があります。これも `SetDefaultNamespace` メソッドを用いて行われます。これは、[エンジン](#asIScriptEngine::SetDefaultNamespace) と [モジュール](#asIScriptModule::SetDefaultNamespace) の両方のインターフェースに適用されます。

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
