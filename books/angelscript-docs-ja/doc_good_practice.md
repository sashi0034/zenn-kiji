---
title: "ベストプラクティス (Good practices)"
---

この記事では、問題が発生したときにより早く原因を特定し、より簡単に解決策を見つけるのに役立つ、いくつかのベストプラクティス（良い習慣）について説明します。

## 登録時の戻り値を必ず確認する (Always check return values for registrations)

スクリプトエンジンを設定する際は、少なくともデバッグモードにおいては、常に戻り値を確認するべきです。すべてのエラーコードは負の値であるため、戻り値を `r` とすると、単純な `assert( r >= 0 )` だけで設定が失敗した箇所を特定するのに十分です。

設定中にいずれかの関数が失敗した場合、[Build](#asIScriptModule::Build) メソッドは常に [`asINVALID_CONFIGURATION`](#asINVALID_CONFIGURATION) のエラーコードで失敗します。これまでのすべての設定呼び出しについてエラーコードを検証していなかった場合、何が原因でエラーになったのかを特定することは不可能になります。

```cpp
// assert を使って戻り値を検証するのは簡単で、コードを汚しません
r = engine->RegisterGlobalFunction("void func()", asFUNCTION(func), asCALL_CDECL); assert( r >= 0 );
```

エンジンの登録において `assert()` を使用することは安全です。なぜなら、もし関数が失敗した場合には、エンジンは内部状態を「無効な設定 (invalid configuration)」に変更するからです。そのため、リリースモードであってもスクリプトのビルド時に失敗が発覚します。

## 詳細なエラーメッセージを受け取るためにメッセージコールバックを使用する (Use the message callback to receive detailed error messages)

登録関数や [Build](#asIScriptModule::Build)、そして [CompileFunction](#asIScriptModule::CompileFunction) などからの戻り値は、何かが間違っていることだけを教えてくれますが、それが「何であるか」までは教えてくれません。正確な問題を特定するためには、メッセージコールバックを使用するべきです。そうすることで、スクリプトライブラリはエラーや警告をクリアなテキストとして説明するメッセージを送信してくれます。

メッセージコールバックに関する詳細情報は [メッセージコールバックの詳細](./doc_compile_script_msg) を参照してください。

## スクリプト関数の実行後は必ず戻り値を検証する (Always verify return value after executing script function)

VM（仮想マシン）は、スクリプト内で発生したあらゆる例外に関する詳細情報を提供することができます。例えば、どの関数のコードの何行目で問題が発生したかなどです。必要であれば、コールスタックや、さらにはローカル変数を列挙することも可能です。

詳細は [スクリプト関数の呼び出しについて](./doc_call_script_4) を参照してください。
