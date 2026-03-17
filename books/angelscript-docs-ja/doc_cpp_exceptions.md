---
title: "C++例外と longjmp (C++ exceptions and longjmp)"
---

## 例外 (Exceptions)

スクリプトエンジンに登録されたアプリケーションの関数およびクラスメソッドは、C++の例外（exceptions）をスローすることが許可されています。仮想マシン (VM) は自動的にすべての C++ 例外をキャッチし、スクリプトの実行を中止して、制御をアプリケーションに返します。

```cpp
asIScriptContext *ctx = engine->CreateContext();
ctx->Prepare(engine->GetModule("test")->GetFunctionByName("func"));
int r = ctx->Execute();
if( r == asEXECUTION_EXCEPTION )
{
  string err = ctx->GetExceptionString();
  if( err == "Caught an exception from the application" )
  {
    // アプリケーションの関数がスクリプトから呼び出されている間に例外をスローした
    ...
  }
}
```

デフォルトでは、VM は異なる種類の例外を見分ける手段を持たず、それらすべてに対して単なる標準の例外文字列を出力します。もし望むなら、例外の種類からより情報量の多い例外文字列への変換を提供する [コールバックをエンジンに登録](./doc_addon_helpers) ことができます。

```cpp
void TranslateException(asIScriptContext *ctx, void* /*userParam*/)
{
  try 
  {
    // もう一度キャッチできるように、元の例外を再スローします
    throw;
  }
  catch( std::exception &e )
  {
    // 発生した例外の種類を VM に伝えます
    ctx->SetException(e.what());
  }
  catch(...)
  {
    // コールバックはいかなる例外のスローも許容してはいけませんが、
    // デフォルトの例外文字列で十分な場合は明示的に例外文字列を設定する必要はありません
  }
}

// エンジンにコールバックを登録する
engine->SetTranslateAppExceptionCallback(asFUNCTION(TranslateException), 0, asCALL_CDECL);
```

参照: ヘルパー関数 [GetExceptionInfo](./doc_addon_helpers)

> **Note**: 例外をキャッチする機能は、ライブラリを `AS_NO_EXCEPTIONS` を定義してコンパイルすることで無効化させることができます。これを行った場合、アプリケーションは例外をスローする可能性のある関数を一切登録すべきではありません。例外が発生した場合、最終的な結果が未定義（undefined）となってしまうためです。

## longjmp

一部のアプリケーションはエラー処理のために `longjmp` を使用します。以前に保存された状態へと `longjmp` を実行する際、コードには状態が保存された「後」のすべての出来事に対するクリーンアップを実行する機会がありません。そのため、関数の中から `longjmp` を実行し得るような関数をアプリケーションが登録してはなりません。そのようなことをすれば、仮想マシンが未定義の（予測不可能な）状態に陥る可能性があるためです。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_cpp_exceptions.html
