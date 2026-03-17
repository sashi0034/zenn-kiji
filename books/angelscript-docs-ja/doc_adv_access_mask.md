---
title: "アクセスマスクと異なるインターフェースの公開 (Access masks and exposing different interfaces)"
---

アプリケーションは、例えばゲームの各エンティティが特定の関数のセットにのみアクセスできる一方で、GUI スクリプトが全く異なる関数のセットにアクセスできるようにするなど、スクリプトの種類によって異なるインターフェースを公開する必要がある場合があります。

これを達成するために、アプリケーションはインターフェースを登録する際にビットマスク (bitmask) を設定することができ、その後スクリプトをビルドする際にそのビットマスクを使用して、スクリプトが何にアクセスでき何にアクセスできないかを決定します。

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

 - [グローバル関数](#asIScriptEngine::RegisterGlobalFunction)
 - [グローバルプロパティ](#asIScriptEngine::RegisterGlobalProperty)
 - [オブジェクト型](#asIScriptEngine::RegisterObjectType)
 - [型の個々のメソッド](#asIScriptEngine::RegisterObjectMethod)
 - [型の個々のプロパティ](#asIScriptEngine::RegisterObjectProperty)
 - [個々のオブジェクトの振る舞い (behaviours)](#asIScriptEngine::RegisterObjectBehaviour)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_access_mask.html
