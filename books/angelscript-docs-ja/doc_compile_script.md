---
title: "スクリプトのコンパイル (Compiling scripts)"
---

[アプリケーションインターフェースの登録](./doc_register_api) が完了したら、次は実行されるスクリプトをコンパイルします。

## メッセージコールバック (Message callback)

コンパイルを開始する前に、コンパイルエラーに関してエラーコード以上の詳細な情報を得られるよう、エンジンにメッセージコールバックを設定しておくことを忘れないでください。実際のところ、アプリケーションインターフェースの登録中にもメッセージコールバックが役立つ場合があるため、スクリプトエンジンを作成した直後にメッセージコールバックを設定することが推奨されます。

メッセージコールバックは、エラーや警告がなければ何も出力しないように設計されているため、すべてが正常であれば何も受け取らないはずです。しかし `Build` メソッドがエラーを返した場合、メッセージコールバックは何を修正する必要があるかを示す詳細なエラー情報を受け取ります。

もし希望するなら、アプリケーションは自身のメッセージをエンジンの `WriteMessage` メソッドを通じてコールバックに送ることもできます。

```cpp
// シンプルなメッセージコールバック関数の実装
void MessageCallback(const asSMessageInfo *msg, void *param)
{
  const char *type = "ERR ";
  if( msg->type == asMSGTYPE_WARNING ) 
    type = "WARN";
  else if( msg->type == asMSGTYPE_INFORMATION ) 
    type = "INFO";
  printf("%s (%d, %d) : %s : %s\n", msg->section, msg->row, msg->col, type, msg->message);
}

// エンジンを作成する際にメッセージコールバックを設定します
asIScriptEngine *engine = asCreateScriptEngine();
engine->SetMessageCallback(asFUNCTION(MessageCallback), 0, asCALL_CDECL);
```

## スクリプトのロードとコンパイル (Loading and compiling scripts)

スクリプトモジュールをビルドするには、まずエンジンからモジュールを取得し、次にスクリプトセクションを追加し、最後にそれらをコンパイルします。コンパイルされたスクリプトモジュールは1つ以上のスクリプトセクションで構成することができるため、アプリケーションは各セクションを別々のファイルに保存したり、動的に生成したりすることもできます。コンパイラはスクリプト内のどこで宣言されているかに関わらず、すべての名前を解決できるため、スクリプトセクションをモジュールに追加する順序は関係ありません。

```cpp
// 新しいスクリプトモジュールを作成します
asIScriptModule *mod = engine->GetModule("module", asGM_ALWAYS_CREATE);

// スクリプトセクションをロードしてモジュールに追加します
string script;
LoadScriptFile("script.as", script);
mod->AddScriptSection("script.as", script.c_str());

// モジュールをビルドします
int r = mod->Build();
if( r < 0 )
{
  // ビルドが失敗しました。メッセージストリームには、
  // 何を修正する必要があるかを示すコンパイラエラーが届いています。
}
```

AngelScript はほとんどのアプリケーションが独自のファイルロード方法を持っているため、スクリプトファイルをロードするための組み込み関数を提供していません。しかし、例えば次のように、スクリプトファイルをロードするためのルーティンを自分で書くのは非常に簡単です：

```cpp
// スクリプトファイル全体を文字列バッファに読み込みます
void LoadScriptFile(const char *fileName, string &script)
{
  // バイナリモードでファイルを開きます
  FILE *f = fopen("test.as", "rb");
  
  // ファイルのサイズを確認します
  fseek(f, 0, SEEK_END);
  int len = ftell(f);
  fseek(f, 0, SEEK_SET);
  
  // ファイル全体を1回の呼び出しでロードします
  script.resize(len);
  fread(&script[0], len, 1, f);
  
  fclose(f);
} 
```

AngelScript はファイル自体をロードしないため、スクリプト内から他のファイルをインクルードするための組み込みサポートもありません。しかし、アドオンディレクトリを見ると、このサポートおよびそれ以上の機能を提供する [CScriptBuilder](./doc_addon#スクリプトビルダー-script-builder) クラスがあります。これはファイルのロード、前処理パスの実行、そしてモジュールのビルドを行うためのヘルパークラスです。スクリプトビルダーの使用例は [Hello World](./doc_hello_world) で確認できます。

参照: [事前コンパイル済みバイトコード](./doc_adv_precompile)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_compile_script.html
