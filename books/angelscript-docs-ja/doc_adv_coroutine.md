---
title: "コルーチン (Co-routines)"
---

コルーチン (Co-routines) は、複数の実行パスを並行して許可する方法ですが、あるスレッドがいつでもサスペンドされて別のスレッドが再開される可能性のある [マルチスレッド](./doc_adv_multithread) におけるプリエンプティブ (pre-emptive) なスケジューリングの危険性を伴いません。コルーチンは常に次のコルーチンのために自発的に自らをサスペンドするため、アトミック命令やクリティカルセクション (critical sections) について心配する必要はありません。

コルーチンは AngelScript ライブラリにネイティブに組み込まれているわけではありませんが、アプリケーション側から簡単に実装することができます。実際、[Context manager アドオン](./doc_addon_ctxmgr) はすでにこのためのデフォルトの実装を提供しています。

独自のバージョンのコルーチンを実装するには、いくつかの部品が必要になります：

 - コルーチン自体。これは単に [asIScriptContext](#asIScriptContext) オブジェクトのインスタンスです。各コルーチンは、そのコルーチンのコールスタックを保持する独自のコンテキストオブジェクトを持ちます。
 - スクリプトが新しいコルーチンを作成、あるいはスポーン (spawn) するのを許可する関数。この関数は、新しいコルーチンの開始関数を参照できる必要があります。この参照は名前で行うこともできますし、よりエレガントに [関数ポインタ](./doc_datatypes_funcptr) を使うこともできます。呼び出されると、この関数は新しいコンテキストをインスタンス化し、開始関数をそこに準備します。
 - コルーチンが次のコルーチンに制御を譲る (yield) ことを許可する関数。この関数は単に現在のコンテキストをサスペンドし、次のコルーチンが再開できるようにします。
 - コルーチンのための簡単な制御アルゴリズム。これは単にすべてのコルーチンが実行を終えるまで、コルーチン（つまりコンテキスト）の配列をイテレート（反復）するループにすることができます。新しいコルーチンが作成されると、それは単に配列の末尾に追加され、現在のコルーチンが制御を譲った時にピックアップされます。

新しいコルーチンをスポーンする関数の簡単な実装例は次のようになります：

```cpp
void CreateCoRoutine(string &func)
{
  asIScriptContext *ctx = asGetActiveContext();
  if( ctx )
  {
    asIScriptEngine *engine = ctx->GetEngine();
    string mod = ctx->GetFunction()->GetModuleName();

    // コルーチンとして作成される関数を見つける必要があります
    string decl = "void " + func + "()"; 
    asIScriptFunction *funcPtr = engine->GetModule(mod.c_str())->GetFunctionByDecl(decl.c_str());
    if( funcPtr == 0 )
    {
      // 関数が見つからなかった場合、例外を発生させます
      ctx->SetException(("Function '" + decl + "' doesn't exist").c_str());
      return;
    }

    // コルーチンのための新しいコンテキストを作成します
    asIScriptContext *coctx = engine->CreateContext();
    coctx->Prepare(funcPtr);

    // 新しいコルーチンのコンテキストをコルーチンの配列に追加します
    coroutines.push_back(coctx);
  }
}
```

yield 関数の実装はさらに簡単です：

```cpp
void Yield()
{
  asIScriptContext *ctx = asGetActiveContext();
  if( ctx )
  { 
    // 次のコルーチンが再開できるように、コンテキストをサスペンドします
    ctx->Suspend();
  }
}
```

基本的な制御アルゴリズムは次のようになるかもしれません：

```cpp
std::vector<asIScriptContext *> coroutines;
void Execute()
{
  int n = 0;
  while( coroutines.size() > 0 )
  {
    // コルーチンを再開します
    int r = coroutines[n]->Execute();
    if( r == asEXECUTION_SUSPENDED )
    {
      // 次のコルーチンを再開します
      if( ++n == coroutines.size() )
        n = 0;
    }
    else
    {
      // コルーチンが終了したため、取り除きます
      coroutines[n]->Release();
      coroutines.erase(n);
    }
  }
}
```

参照: [Context manager アドオン](./doc_addon_ctxmgr)、[Co-routines サンプル](./doc_samples_corout)、[並行スクリプト](./doc_adv_concurrent)
