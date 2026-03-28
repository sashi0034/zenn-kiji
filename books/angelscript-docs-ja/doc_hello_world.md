---
title: "はじめてのスクリプト (Your first script)"
---

このチュートリアルでは、エンジンの初期設定からスクリプトのコンパイル、そして実行に至るまでの基礎について解説します。本記事に掲載されているコードは、ライブラリ使用の全体像を理解するための主要な部分に絞られています。完全なソースコードについては、SDK に同梱されている[サンプル](./doc_samples)を参照してください。

このチュートリアルでは、コードを簡潔にするためいくつかのアドオンを使用しています。実際のアプリケーションでこれらを必ずしも使う必要はありませんが、プロジェクトの立ち上げを早めるのに役立つでしょう。後ほど他の[アドオン](./doc_addon)も確認して、自身のプロジェクトに有用なものを探してみてください。

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

AngelScript は組み込み型（エンベデッド）のスクリプトライブラリであるため、スクリプト単体でできることは限られています。そのため、まずアプリケーション側で、スクリプトがホストと対話するための[インターフェースを登録](./doc_register_api)する必要があります。このインターフェースは、関数、変数、さらにはクラスなどで構成されます。

エンジン作成の直後に行われている[メッセージコールバック](./doc_compile_script#メッセージコールバック-(message-callback))の登録に注目してください。このコールバックは、設定ミスやスクリプトのコンパイルエラーなど、予期しない動作が発生した際に、人間が理解できるエラーメッセージを出力するためにエンジンによって呼び出されます。戻り値の確認は依然として不可欠ですが、メッセージコールバックは問題の原因を素早く特定するための非常に有益な情報を提供してくれます。

```cpp
// スクリプトエンジンを作成する
asIScriptEngine *engine = asCreateScriptEngine();

// エラー情報を人間が読める形式で受け取るためにメッセージコールバックを設定する
int r = engine->SetMessageCallback(asFUNCTION(MessageCallback), 0, asCALL_CDECL); assert( r >= 0 );

// C++ アプリケーションにおいて「決定的な標準」といえる文字列型は存在しないため、
// AngelScript にも組み込みの文字列型は用意されていません。開発者は
// 自身の環境に合わせた文字列型を自由に登録できます。ただし、SDK には
// 標準的な文字列アドオンが含まれているため、特にこだわりがなければ
// それを利用するのが最も簡単です。
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

スクリプトファイルを読み込んでコンパイルするためのコードは以下の通りです。AngelScript エンジン自体はファイルシステムへのアクセスを持たないため、ファイルの読み込みはアプリケーション側で行う必要があります。ここでは、スクリプトファイルの読み込みや `#include` ディレクティブの処理などの前処理を行う [スクリプトビルダー](./doc_addon#スクリプトビルダー) アドオンを使用します。

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

上記の例外処理は非常に基本的なものです。アプリケーション側では、必要に応じてエラー発生時の行番号、関数名、コールスタック、さらにはローカル・グローバル変数の値といった詳細な情報を取得することも可能です。

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

参照: [メッセージコールバック](./doc_compile_script#メッセージコールバック-(message-callback))、[スクリプトビルダー](./doc_addon#スクリプトビルダー)、[標準文字列](./doc_addon#string-オブジェクト)、[サンプル](./doc_samples)

---

訳注: こちらも参考になれば幸いです。

https://zenn.dev/sashi0034/articles/bf06646e0d88ac

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_hello_world.html
