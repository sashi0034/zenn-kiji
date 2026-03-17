---
title: "はじめてのスクリプト (Your first script)"
---

このチュートリアルでは、エンジンの設定、スクリプトのコンパイル、そしてその実行方法についての基礎を説明します。この記事内のコードは完全なものではなく、スクリプトライブラリを使用するための基本的な構造を説明する関連部分だけが含まれています。完全なソースコードについては、SDK に付属している [サンプル](./doc_samples) を参照してください。

このチュートリアルでは、コードをより簡単にするためにいくつかのアドオンが使用されています。自分のアプリケーションでこれらを必ずしも使用する必要はありませんが、これらを使用することでプロジェクトをより早く立ち上げ、実行することができるでしょう。後で他の [アドオン](./doc_addon) も確認して、自分にとって役立ちそうなものをチェックしてみてください。

```cpp
// スクリプトライブラリと、使用するアドオンの定義をインクルードします。
// コンパイラがこれらのヘッダーを見つけられるように、プロジェクト設定の
// 構成が必要になる場合があります。アプリケーションの一部としてコンパイル
// されるように、アドオンのソースモジュールをプロジェクトに追加することも
// 忘れないでください。
#include <angelscript.h>
#include <scriptstdstring/scriptstdstring.h>
#include <scriptbuilder/scriptbuilder.h>
```

組み込み用スクリプトライブラリである AngelScript は、スクリプト単体でできることはあまり多くないため、機能を持たせるためにはアプリケーションで最初にスクリプトがアプリケーションと対話するための [インターフェースを登録](./doc_register_api) する必要があります。インターフェースは関数、変数、さらには完全なクラス構成などで構成される場合があります。

エンジンが作成された直後に [メッセージコールバック](./doc_compile_script_msg) がどのように登録されているかに特に注意してください。メッセージコールバックは、例えば登録が正しく行われなかった場合や、スクリプトにコンパイル失敗のエラーがある場合など、何か想定外の動作をしたときに、人間が読めるエラーメッセージを出力するためにエンジンによって使用されます。引き続き戻り値の検証は行う必要がありますが、メッセージコールバックは少ない労力で何が問題かを突き止めるために価値のある情報を提供してくれます。

```cpp
// スクリプトエンジンを作成する
asIScriptEngine *engine = asCreateScriptEngine();

// エラー情報を人間が読める形式で受け取るためにメッセージコールバックを設定する
int r = engine->SetMessageCallback(asFUNCTION(MessageCallback), 0, asCALL_CDECL); assert( r >= 0 );

// C++ アプリケーションのための明確な標準文字列型が存在しないため、AngelScript 
// にも組み込みの文字列型はありません。各開発者は独自の文字列型を自由に登録
// できます。ただし、SDK には文字列型を登録するための標準アドオンが用意されて
// いるため、自身で実装したくない場合は登録処理を自作する必要はありません。
RegisterStdString(engine);

// スクリプトから呼び出せるようにしたい関数を登録する
r = engine->RegisterGlobalFunction("void print(const string &in)", asFUNCTION(print), asCALL_CDECL); assert( r >= 0 );
```

エンジンの設定が完了した後の次の手順は、実行すべきスクリプトをコンパイルすることです。

以下は、登録された `print` 関数を呼び出して標準出力ストリームに `Hello world` を書き込むスクリプトです。これが `test.as` というファイルに保存されていると想定しましょう。

```cpp
  void main()
  {
    print("Hello world\n");
  }
```

スクリプトファイルを読み込んでコンパイルするためのコードは以下の通りです。AngelScript エンジン自体はファイルシステムへのアクセスを持たないため、ファイルの読み込みはアプリケーション側で行う必要があります。ここでは、スクリプトファイルの読み込みや `#include` ディレクティブの処理などの前処理を行う [スクリプトビルダー](./doc_addon_build) アドオンを使用します。

```cpp
// CScriptBuilder ヘルパーはファイルを読み込み、必要に応じてプリプロセッシングの
// パスを実行し、その後エンジンにスクリプトモジュールをビルドするよう指示するアドオンです。
CScriptBuilder builder;
int r = builder.StartNewModule(engine, "MyModule"); 
if( r < 0 ) 
{
  // ここでコードが失敗する場合、通常はモジュールを割り当てるためのメモリが
  // マシンの上限に達していることが原因です。
  printf("Unrecoverable error while starting a new module.\n");
  return;
}
r = builder.AddSectionFromFile("test.as");
if( r < 0 )
{
  // ビルダーがファイルを読み込めませんでした。ファイルが削除されたか、
  // 間違った名前が指定されたか、あるいはいくつかのプリプロセスコマンドが
  // 正しく記述されていない可能性があります。
  printf("Please correct the errors in the script and try again.\n");
  return;
}
r = builder.BuildModule();
if( r < 0 )
{
  // エラーが発生しました。出力ストリームにリストされたコンパイルエラーを
  // 修正するようスクリプトライターに指示してください。
  printf("Please correct the errors in the script and try again.\n");
  return;
}
```

最後のステップは、呼び出されるべき関数を特定し、それを実行するためのコンテキストを設定することです。

```cpp
// 呼び出すべき関数を見つける 
asIScriptModule *mod = engine->GetModule("MyModule");
asIScriptFunction *func = mod->GetFunctionByDecl("void main()");
if( func == 0 )
{
  // 関数が見つかりませんでした。スクリプトに期待される関数を
  // 含めるようスクリプトライターに指示してください。
  printf("The script must have the function 'void main()'. Please add it and try again.\n");
  return;
}

// コンテキストを作成し、準備し、そして実行する
asIScriptContext *ctx = engine->CreateContext();
ctx->Prepare(func);
int r = ctx->Execute();
if( r != asEXECUTION_FINISHED )
{
  // 実行が期待通りに完了しませんでした。何が起こったかを判定します。
  if( r == asEXECUTION_EXCEPTION )
  {
    // 例外が発生しました。修正できるように、スクリプトライターに何が起こったかを知らせます。
    printf("An exception '%s' occurred. Please correct the code and try again.\n", ctx->GetExceptionString());
  }
}
```

上記の例外処理は非常に基本的なものです。アプリケーションは必要に応じて、行番号、関数、コールスタック、さらにはローカルおよびグローバル変数の値に関する情報を取得することもできます。

エンジンの使用が完了した後のクリーンアップを忘れないでください。

```cpp
// クリーンアップ
ctx->Release();
engine->ShutDownAndRelease();
```

## ヘルパー関数 (Helper functions)

print 関数は、printf 関数の非常にシンプルなラッパーとして実装されています。

```cpp
// スクリプトの文字列を標準出力ストリームに表示する
void print(string &msg)
{
  printf("%s", msg.c_str());
}
```

参照: [メッセージコールバック](./doc_compile_script_msg)、[スクリプトビルダー](./doc_addon_build)、[標準文字列](./doc_addon_std_string)、[サンプル](./doc_samples)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_hello_world.html
