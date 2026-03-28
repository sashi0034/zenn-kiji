---
title: "アクセスマスクと別のインターフェースの公開 (Access masks and exposing different interfaces)"
---

アプリケーションによっては、スクリプトの種類に応じて異なるインターフェースを公開したい場合があります。例えば、ゲーム内の各エンティティには特定の関数セットのみを許可し、GUI スクリプトには全く別の関数セットを許可するといった使い分けです。

これを実現するために、アプリケーションはインターフェースを登録する際に「アクセスマスク (Bitmask)」を設定できます。スクリプトをビルドする際、このビットマスクによって、そのスクリプトがアクセス可能な範囲が決定されます。

```cpp
void ConfigureEngine(asIScriptEngine *engine)
{
  // スクリプト型 1 で利用可能なインターフェースを登録します
  engine->SetDefaultAccessMask(0x1); 
  r = engine->RegisterGlobalFunction("void func1()", asFUNCTION(func1), asCALL_CDECL); assert( r >= 0 );

  // スクリプト型 2 で利用可能なインターフェースを登録します
  engine->SetDefaultAccessMask(0x2); 
  r = engine->RegisterGlobalFunction("void func2()", asFUNCTION(func2), asCALL_CDECL); assert( r >= 0 );

  // 両方のスクリプト型で利用可能なインターフェースを登録します
  engine->SetDefaultAccessMask(0x3);
  r = engine->RegisterGlobalFunction("void func3()", asFUNCTION(func3), asCALL_CDECL); assert( r >= 0 );
}

int CompileScript(asIScriptEngine *engine, const char *script, int type)
{
  int r;
  CScriptBuilder builder;
  r = builder.StartNewModule(engine, script);
  if( r < 0 ) return r;

  // モジュールに対してアクセスマスクを設定します。
  // これにより、アプリケーションインターフェースの中から呼び出し可能な関数が決定されます
  asIScriptModule *mod = builder.GetModule();
  mod->SetAccessMask(type); 

  // スクリプトセクションを追加し、スクリプトをビルドします
  r = builder.AddSectionFromFile(script);
  if( r < 0 ) return r;

  return builder.BuildModule();
}
```

アクセスマスクは、アプリケーションインターフェース内の以下のエンティティに対して定義することができます：

 - [グローバル関数](./doc_register_func)
 - [グローバルプロパティ](./doc_register_prop)
 - [オブジェクト型](./doc_register_type)
 - [型の個々のメソッド](./doc_register_type#オブジェクトメソッドの登録-(registering-object-methods))
 - [型の個々のプロパティ](./doc_register_type#オブジェクトプロパティの登録-(registering-object-properties))
 - [個々のオブジェクトの振る舞い (behaviours)](./doc_register_type#参照型の登録-(registering-a-reference-type))

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_access_mask.html
