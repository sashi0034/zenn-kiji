---
title: "コルーチン (Co-routines)"
---

コルーチン (Co-routines) は、複数の実行パスを並行して実行させる手法の一つです。[並行スクリプト](./doc_adv_concurrent)で触れたマルチスレッドのような、スレッドが任意のタイミングで中断され別のスレッドに切り替わる「プリエンプティブ（強制割り込み型）」なスケジューリングに伴う危険性がありません。コルーチンは常に自発的に実行権を次のルーチンに譲る（サスペンドする）ため、アトミック操作やクリティカルセクションによる排他制御について心配する必要がありません。

コルーチンは AngelScript ライブラリの標準機能として組み込まれているわけではありませんが、アプリケーション側で容易に実装できます。実際、[コンテキストマネージャアドオン](./doc_addon#コンテキストマネージャー)には標準的な実装が含まれています。

独自のコルーチン機能を実装する場合、以下の要素が必要になります。

1. **コルーチンの実体**: 各コルーチンは `asIScriptContext` オブジェクトのインスタンスです。各コルーチンはそれぞれ独自のコンテキストを持ち、そこにコールスタックが保持されます。
2. **生成（スポーン）関数**: スクリプトから新しいコルーチンを作成（スポーン）するための関数です。この関数は、新しいコルーチンの開始関数を参照できる必要があります。参照には関数名を使用するか、より洗練された方法として [関数ハンドル](./doc_script_datatypes#関数ハンドル-(function-handles)) を使用することもできます。呼び出されると、新しいコンテキストを作成し、開始関数を準備（Prepare）します。
3. **譲渡（イールド）関数**: 現在のコルーチンが次のルーチンに実行権を譲るための関数です。単に現在のコンテキストをサスペンドし、次のコルーチンが再開できるようにします。
4. **制御ロジック（スケジューラ）**: すべてのコルーチンが終了するまで、コンテキストの配列を順次実行するシンプルなループ処理です。新しいコルーチンが生成されたら配列に追加され、現在のルーチンがイールドした際に次のルーチンが実行されます。

新しいコルーチンをスポーンする関数の簡単な実装例は次のようになります：

```cpp
void CreateCoRoutine(string &func)
{
  asIScriptContext *ctx = asGetActiveContext();
  if( ctx )
  {
    asIScriptEngine *engine = ctx->GetEngine();
    string mod = ctx->GetFunction()->GetModuleName();

    // コルーチンとして実行する関数を見つける必要があります
    string decl = "void " + func + "()"; 
    asIScriptFunction *funcPtr = engine->GetModule(mod.c_str())->GetFunctionByDecl(decl.c_str());
    if( funcPtr == 0 )
    {
      // 関数が見つからなかった場合、例外をスローします
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

参照: [Context manager アドオン](./doc_addon#コンテキストマネージャー)、[Co-routines サンプル](./doc_samples#co-routines（コルーティン）)、[並行スクリプト](./doc_adv_concurrent)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_coroutine.html
