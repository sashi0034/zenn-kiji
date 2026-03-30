---
title: "🚀 C++例外と longjmp (C++ exceptions and longjmp)"
---

スクリプトエンジンに登録されたアプリケーション関数やクラスメソッドは、C++ 例外をスローすることが許可されています。仮想マシン（VM）はあらゆる C++ 例外を自動的にキャッチし、スクリプトの実行を中断してアプリケーションに制御を戻します。

```cpp
asIScriptContext *ctx = engine->CreateContext();
ctx->Prepare(engine->GetModule("test")->GetFunctionByName("func"));
int r = ctx->Execute();
if( r == asEXECUTION_EXCEPTION )
{
  string err = ctx->GetExceptionString();
  if( err == "Caught an exception from the application" )
  {
    // スクリプトから呼び出されたアプリケーション関数が例外をスローした
    ...
  }
}
```

デフォルトでは、VM は異なる例外の種類を判別する手段を持たず、すべての例外に対して標準的な例外メッセージを返します。必要に応じて、例外の種類をより詳細な文字列に変換するための [コールバックを登録](./doc_addon#ヘルパー関数) することができます。

```cpp
void TranslateException(asIScriptContext *ctx, void* /*userParam*/)
{
  try 
  {
    // 元の例外を再スローして、もう一度キャッチできるようにします
    throw;
  }
  catch( std::exception &e )
  {
    // 発生した例外の種類を VM に伝えます
    ctx->SetException(e.what());
  }
  catch(...)
  {
    // コールバック内ではいかなる例外のスローも許容されませんが、
    // デフォルトの例外文字列で十分な場合は、明示的に例外文字列を設定する必要はありません。
  }
}

// エンジンにコールバックを登録する
engine->SetTranslateAppExceptionCallback(asFUNCTION(TranslateException), 0, asCALL_CDECL);
```

参照: ヘルパー関数 [GetExceptionInfo](./doc_addon#ヘルパー関数)

> [!NOTE]
> 例外をキャッチする機能は、ライブラリを `AS_NO_EXCEPTIONS` を定義してコンパイルすることで無効化できます。その場合、アプリケーションは例外をスローする可能性のある関数を一切登録してはいけません。例外が発生した場合、結果が未定義（Undefined）となるためです。

## longjmp

一部のアプリケーションでは、エラー処理のために `longjmp` を使用します。以前に保存された状態へ `longjmp` を実行する際、コードには保存時以降に発生した出来事に対するクリーンアップを行う機会がありません。そのため、アプリケーションは関数内から `longjmp` を実行するような関数を登録してはなりません。そのようなことをすれば、仮想マシンが未定義（予測不能）な状態に陥る可能性があるためです。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_cpp_exceptions.html
