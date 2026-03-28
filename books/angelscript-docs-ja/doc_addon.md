---
title: "アドオン (Add-ons)"
---

このページでは `/sdk/add_on/` フォルダにあるアドオンの概要を説明します。

- [アプリケーションモジュール](#アプリケーションモジュール)
- [スクリプト拡張](#スクリプト拡張)

## アプリケーションモジュール

- [スクリプトビルダー (scriptbuilder)](#スクリプトビルダー)
- [コンテキストマネージャー (contextmgr)](#コンテキストマネージャー)
- [デバッガー (debugger)](#デバッガー)
- [シリアライザー (serializer)](#シリアライザー)
- [ヘルパー関数 (scripthelper)](#ヘルパー関数)
- [自動ラッパー関数 (autowrapper)](#自動ラッパー関数)

## スクリプト拡張

- [string](#string-オブジェクト)
- [array テンプレートオブジェクト](#array-テンプレートオブジェクト)
- [any オブジェクト](#any-オブジェクト)
- [ref オブジェクト](#ref-オブジェクト)
- [weakref オブジェクト](#weakref-オブジェクト)
- [dictionary オブジェクト](#dictionary-オブジェクト)
- [file オブジェクト](#file-オブジェクト)
- [filesystem オブジェクト](#filesystem-オブジェクト)
- [math 関数](#math-関数)
- [grid テンプレートオブジェクト](#grid-テンプレートオブジェクト)
- [datetime オブジェクト](#datetime-オブジェクト)
- [socket オブジェクト](#socket-オブジェクト)
- [例外ルーティン](#例外ルーティン)

---

## スクリプトビルダー

**パス:** `/sdk/add_on/scriptbuilder/`

`CScriptBuilder` は、スクリプトの読み込み（ロード）とビルドを簡素化するためのヘルパークラスです。条件付きコンパイル、インクルード（`#include`）、プラグラ（`#pragma`）、メタデータ宣言などをサポートする簡易的なプリプロセッサ機能を備えています。

デフォルトでは、スクリプトビルダーは、インクルード元のファイルがあるディレクトリを基準とした相対パスによってインクルード・ディレクティブを解決します。これとは別の方法でインクルードを処理したい場合は、独自のインクルード・コールバックを実装してください。

アプリケーションでプラグラ（`#pragma`）ディレクティブをサポートする場合は、プラグラ・コールバックを登録する必要があります。コールバックが登録されていない状態でプラグラ・ディレクティブに遭遇すると、スクリプトビルダーはエラーを報告します。

また、スクリプトビルダーは `#!` で始まる行をコメントとして破棄します。これは Linux や UNIX ベースのシステムで一般的に使用される「シバン（shebang）」インタープリタ・ディレクティブをサポートするためです。

### C++ パブリックインターフェース

```cpp
class CScriptBuilder
{
public:
  // 新しいモジュールを開始します
  int StartNewModule(asIScriptEngine *engine, const char *moduleName);

  // ディスク上のファイルからスクリプトセクションをロードします
  // 戻り値: 1=ファイルがインクルードされた, 0=すでにインクルード済み, <0=エラー
  int AddSectionFromFile(const char *filename);

  // メモリからスクリプトセクションをロードします
  // 戻り値: 1=セクションがインクルードされた, 0=同名のセクションがすでにインクルード済み, <0=エラー
  int AddSectionFromMemory(const char *sectionName,
                           const char *scriptCode, 
                           unsigned int scriptLength = 0,
                           int lineOffset = 0);

  // 追加したスクリプトセクションをビルドします
  int BuildModule();

  // スクリプトエンジンを返します
  asIScriptEngine *GetEngine();

  // 現在のモジュールを返します
  asIScriptModule *GetModule();

  // インクルードディレクティブを解決するコールバックを登録します
  void SetIncludeCallback(INCLUDECALLBACK_t callback, void *userParam);

  // pragma ディレクティブを解決するコールバックを登録します
  void SetPragmaCallback(PRAGMACALLBACK_t callback, void *userParam);

  // 条件付きコンパイルのためのプリプロセッサ定義を追加します
  void DefineWord(const char *word);

  // インクルードされたスクリプトセクションを列挙します
  unsigned int GetSectionCount() const;
  string       GetSectionName(unsigned int idx) const;
  
  // クラス、インターフェース、列挙型に宣言されたメタデータを取得します
  std::vector<std::string> GetMetadataStringForType(int typeId);

  // 関数に宣言されたメタデータを取得します
  std::vector<std::string> GetMetadataStringForFunc(asIScriptFunction *func);

  // グローバル変数に宣言されたメタデータを取得します
  std::vector<std::string> GetMetadataStringForVar(int varIdx);

  // クラスのメソッドに宣言されたメタデータを取得します
  std::vector<std::string> GetMetadataStringForTypeMethod(int typeId, asIScriptFunction *method);

  // クラスのプロパティに宣言されたメタデータを取得します
  std::vector<std::string> GetMetadataStringForTypeProperty(int typeId, int varIdx);
};
```

#### インクルードコールバックのシグネチャ

```cpp
// このコールバックはビルダーによって遭遇した各 #include ディレクティブに対して呼び出されます。
// コールバックはインクルードされたセクションをスクリプトに追加するために
// AddSectionFromFile または AddSectionFromMemory を呼び出す必要があります。
// インクルードが解決できない場合、コンパイルを中断するために負の値を返す必要があります。
typedef int (*INCLUDECALLBACK_t)(const char *include, const char *from, CScriptBuilder *builder, void *userParam);
```

#### pragma コールバックのシグネチャ

```cpp
// このコールバックはビルダーによって遭遇した各 #pragma ディレクティブに対して呼び出されます。
// アプリケーションは pragmaText を解釈してそれに基づいて何をするかを決定できます。
// コールバックが負の値を返した場合、ビルダーはエラーを報告してコンパイルを中断します。
typedef int(*PRAGMACALLBACK_t)(const std::string &pragmaText, CScriptBuilder &builder, void *userParam);
```

### インクルードディレクティブ

```cs
#include "commonfuncs.as"

void main()
{
  // インクルードされたファイルの関数を呼び出します
  CommonFunc();
}
```

### 条件付きコンパイル

ビルダーは `#if` / `#endif` プリプロセッサ・ディレクティブによる条件付きコンパイルをサポートしています。アプリケーションは `DefineWord()` を呼び出して任意の単語を定義でき、スクリプト内でその定義の有無をチェックすることで、コードの一部をコンパイル対象に含めたり除外したりできます。

これは、例えばクライアント／サーバー型のアプリケーションにおいて、同じスクリプトファイルを異なるバイナリ（役割）間で共有する場合などに非常に便利です。

```cs
class CObject
{
  void Process()
  {
#if SERVER
    // サーバー固有の処理を行います
#endif

#if CLIENT
    // クライアント固有の処理を行います
#endif

    // 共通の処理を行います
  }
}
```

### スクリプト内のメタデータ

メタデータは、スクリプト内のクラス、インターフェース、関数、およびグローバル変数の宣言の直前に付与できる情報です。メタデータはビルド時にスクリプトビルダーによって抽出され（コードからは削除されます）、ビルド完了後に型 ID、関数 ID、または変数インデックスを用いて検索できるように保存されます。

```cs
[factory func = CreateOgre]
class COgre
{
  [editable] 
  vector3 myPosition;
  
  [editable]
  [range [10, 100]]
  int     myStrength;
}

[factory]
COgre @CreateOgre()
{
  return @COgre();
}
```

---

## コンテキストマネージャー

**パス:** `/sdk/add_on/contextmgr/`

`CContextMgr` は、並列（並行）に実行される複数のスクリプトを効率的に管理するためのクラスです。並列スクリプトスレッドとコルーチンの両方をサポートしています。

アプリケーションが複数のコンテキストを必要としない場合（つまり、同時に実行されるスクリプトが 1 つだけで、完了してから次のスクリプトが実行される場合）、このクラスを使用する必要はありません。

コンテキストマネージャーは、エンジンに登録されたコンテキスト・コールバックを利用し、パッチ作業やプーリングのために `asIScriptEngine::RequestContext` を内部で使用します。

1 つのアプリケーションで複数のコンテキストマネージャーを使い分けることも可能です。例えば、ゲーム内のオブジェクトを制御するスクリプト群と、GUI 要素を制御するスクリプト群を、それぞれ別のコンテキストマネージャーで管理するといった運用が考えられます。

なお、コンテキストマネージャークラス自体はスレッドセーフ（マルチスレッド対応）に設計されていないため、複数のホストスレッドから同時にスクリプトを実行する場合には適切な同期処理が必要です。

参照: サンプルの [Concurrent scripts](./doc_samples#concurrent-scripts（並行スクリプト）) および [Co-routines](./doc_samples#co-routines（コルーティン）)
(※これらは [サンプル](./doc_samples) ページに記載されています)

### C++ パブリックインターフェース

```cpp
class CContextMgr
{
public:
  CContextMgr();
  ~CContextMgr();

  // マネージャーがミリ秒単位で時刻を取得するために使用する関数を設定します
  void SetGetTimeCallback(TIMEFUNC_t func);

  // 以下を登録します:
  //   void sleep(uint milliseconds)
  // これが機能するにはアプリケーションが GetTime コールバックを設定する必要があります
  void RegisterThreadSupport(asIScriptEngine *engine);

  // 以下を登録します:
  //   funcdef void coroutine(dictionary@)
  //   void createCoRoutine(coroutine @func, dictionary @args)
  //   void yield()
  void RegisterCoRoutineSupport(asIScriptEngine *engine);

  // 新しいコンテキストを作成し、関数でそれを準備してから返します（引数値を渡せるよう）
  // 実行が完了した後、コンテキストはマネージャーによって解放されます
  asIScriptContext *AddContext(asIScriptEngine *engine, asIScriptContext *func, bool keepCtxAfterExecution = false);

  // コンテキストが実行後も保持されていた場合、アプリケーションがコンテキストを
  // 使い終わったらこのメソッドを呼び出してプールに返す必要があります
  void DoneWithContext(asIScriptContext *ctx);
  
  // 新しいコンテキストを作成し、関数でそれを準備してから返します
  // コンテキストは currCtx と同じスレッドのコルーチンとして追加されます
  asIScriptContext *AddContextForCoRoutine(asIScriptContext *currCtx, asIScriptContext *func);

  // 現在スリープ中でない各スクリプトを実行します。
  // 各スクリプトが1回実行された後に関数が返ります。
  // アプリケーションはメッセージポンプまたはゲームループの各イテレーションでこれを呼び出すべきです。
  // まだ実行中のスクリプトの数を返します。
  int ExecuteScripts();

  // スクリプトをしばらくスリープ状態にします
  void SetSleeping(asIScriptContext *ctx, asUINT milliSeconds);

  // グループ内の次のコルーチンに実行を切り替えます
  void NextCoRoutine();

  // すべてのスクリプトを中断します
  void AbortAll();
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib#コルーチン-(co-routines)) を参照してください。

---

## デバッガー

**パス:** `/sdk/add_on/debugger/`

`CDebugger` は、スクリプトのデバッグ（ブレークポイントの設定、ステップ実行、変数値の検査など）において標準的な機能を提供します。

デバッガーを使用するには、コンテキストにライン・コールバック（Line Callback）を設定する必要があります。これにより、ブレークポイントに到達した際にデバッガーが制御を引き継ぎ、対話的なデバッグが可能になります。

デフォルトでは標準入出力（stdin/stdout）を使用してユーザーと対話しますが、`CDebugger` クラスを継承し、`TakeCommands` および `Output` メソッドをオーバーライドすることで、独自のインターフェースを実装できます。これにより、GUI デバッガーやリモートデバッグ機能を構築することも可能です。

アプリケーション開発者は、`RegisterToStringCallback` の呼び出しで登録された型の文字列変換コールバックを登録することもできます。

参照: デバッガーの使用方法の完全な例については [asrun サンプル](./doc_samples) を参照

### C++ パブリックインターフェース

```cpp
class CDebugger
{
public:
  CDebugger();
  virtual ~CDebugger();

  // アプリケーション型の文字列変換を処理するコールバックを登録します
  typedef std::string (*ToStringCallback)(void *obj, int expandMembersLevel, CDebugger *dbg);
  virtual void RegisterToStringCallback(const asITypeInfo *type, ToStringCallback callback);
  
  // ユーザーとの対話
  virtual void TakeCommands(asIScriptContext *ctx);
  virtual void Output(const std::string &str);

  // コンテキストによって呼び出されるラインコールバック
  virtual void LineCallback(asIScriptContext *ctx);

  // コマンド
  virtual void PrintHelp();
  virtual void AddFileBreakPoint(const std::string &file, int lineNbr);
  virtual void AddFuncBreakPoint(const std::string &func);
  virtual void ListBreakPoints();
  virtual void ListLocalVariables(asIScriptContext *ctx);
  virtual void ListGlobalVariables(asIScriptContext *ctx);
  virtual void ListMemberProperties(asIScriptContext *ctx);
  virtual void ListStatistics(asIScriptContext *ctx);
  virtual void PrintCallstack(asIScriptContext *ctx);
  virtual void PrintValue(const std::string &expr, asIScriptContext *ctx);

  // ヘルパー
  virtual bool InterpretCommand(const std::string &cmd, asIScriptContext *ctx);
  virtual bool CheckBreakPoint(asIScriptContext *ctx);
  virtual std::string ToString(void *value, asUINT typeId, int expandMembersLevel, asIScriptEngine *engine);
  
  virtual void SetEngine(asIScriptEngine *engine);
  virtual asIScriptEngine *GetEngine();
};
```

### 使用例

```cpp
CDebugger dbg;
int ExecuteWithDebug(asIScriptContext *ctx)
{
  // コンテキストにデバッガーのラインコールバックを呼び出すよう指示します
  ctx->SetLineCallback(asMETHOD(CDebugger, LineCallback), &dbg, asCALL_THISCALL);

  // デバッグを開始する前にユーザーがデバッグを初期化できるようにします
  dbg.TakeCommands(ctx);

  // スクリプトを通常通り実行します。ブレークポイントに達した場合、
  // デバッガーが制御ループを引き継ぎます。
  return ctx->Execute();
}
```

---

## シリアライザー

**パス:** `/sdk/add_on/serializer/`

`CSerializer` を使用すると、モジュール内のグローバル変数の値をシリアライズ（保存・復元）できます。これは、アプリケーションを終了したり初期化し直したりせずに、微修正したスクリプトをリロードして実行を継続したい場合などに役立ちます。プリミティブ型やスクリプトクラス（参照やハンドルを含む）は自動的に処理されます。

アプリケーションで独自に登録した型については、どのようにシリアライズするかを定義するコールバック・オブジェクトを実装する必要があります。ただし POD（Plain Old Data）型は例外で、シリアライザーは単にメモリをバイナリコピーして保持します。ファクトリを持たない登録済みの参照型はシリアライズ対象外となります。

**現在の制限事項:**
- メモリへのシリアライズのみサポートされています（ファイルへの直接保存機能はありません）。
- 復元時に変数の型が変更されている場合、シリアライザーはその値を復元できません。
- シリアライザーはすべてのオブジェクトの状態をまるごと保存しようとしますが、状況によっては「オブジェクトそのもの」ではなく「その参照」だけを保存したい場合があります（例：スクリプトから参照されているアプリケーション内部のシングルトン・オブジェクトなど）。現在のところ、これを個別に指定する機能はありません。
- モジュールが別のモジュールのオブジェクトに依存（参照）している場合、復元に失敗することがあります。

### C++ パブリックインターフェース

```cpp
class CSerializer
{
public:
  CSerializer();
  ~CSerializer();

  // 内部で保持している参照を解放するためにシリアライザーをクリアします
  void Clear();

  // ユーザー型のシリアライズ実装を追加します
  void AddUserType(CUserType *ref, const std::string &name);

  // モジュール内のすべてのグローバル変数を保存します
  int Store(asIScriptModule *mod);

  // スクリプトのリロード後にすべてのグローバル変数を復元します
  int Restore(asIScriptModule *mod);

  // モジュールのグローバル変数から参照されない追加のオブジェクトを保存します
  void AddExtraObjectToStore(asIScriptObject *object);

  // 復元されたオブジェクトへの新しいポインタを返します
  void *GetPointerToRestoredObject(void *originalObject);
};
```

### 使用例

```cpp
void RecompileModule(asIScriptEngine *engine, asIScriptModule *mod)
{
  string modName = mod->GetName();

  // シリアライザーにユーザー型のシリアライズ方法を伝えます
  CSerializer backup;
  backup.AddUserType(new CStringType(), "string");
  backup.AddUserType(new CArrayType(), "array");

  // グローバル変数の値をバックアップします
  backup.Store(mod);
  
  // アプリケーションはモジュールを再コンパイルできます
  CompileModule(modName);

  // 新しいモジュールのグローバル変数の値を復元します
  mod = engine->GetModule(modName.c_str(), asGM_ONLY_IF_EXISTS);
  backup.Restore(mod);
}
```

---

## ヘルパー関数

**パス:** `/sdk/add_on/scripthelper/`

これらのヘルパー関数は一般的なタスクの実装を簡素化します。そのまま使用するか、独自のフレームワークの出発点として使用できます。

### C++ パブリックインターフェース

```cpp
// 同じ型の2つのオブジェクト間の関係を比較します。
// オブジェクトの opCmp メソッドを使用して比較を実行します。
// 比較が実行できなかった場合は負の値を返します。
int CompareRelation(asIScriptEngine *engine, void *leftObj, void *rightObj, int typeId, int &result);

// 同じ型の2つのオブジェクト間の等値を比較します。
// オブジェクトの opEquals メソッドを使用し、それがない場合は opCmp を使用します。
// 比較が実行できなかった場合は負の値を返します。
int CompareEquality(asIScriptEngine *engine, void *leftObj, void *rightObj, int typeId, bool &result);

// 簡単なステートメントをコンパイルして実行します。
// モジュールはオプションです。指定した場合、ステートメントはモジュールでコンパイルされたエンティティにアクセスできます。
int ExecuteString(asIScriptEngine *engine, const char *code, asIScriptModule *mod = 0, asIScriptContext *ctx = 0);

// 戻り値のオプションを含む簡単なステートメントをコンパイルして実行します。
int ExecuteString(asIScriptEngine *engine, const char *code, void *ret, int retTypeId, asIScriptModule *mod = 0, asIScriptContext *ctx = 0);

// スクリプト例外の詳細を人間が読めるテキストにフォーマットします。
// asIScriptContext::Execute が asEXECUTION_EXCEPTION を返すたびに、アプリケーションは
// この関数を呼び出してその例外に関する詳細情報を人間が読める形式で取得できます。
std::string GetExceptionInfo(asIScriptContext *ctx, bool showStack = false);

// 登録されたアプリケーションインターフェースをファイルに書き込みます。
// この関数はサンプルのオフラインコンパイラー asbuild の設定を含むファイルを作成します。
int WriteConfigToFile(asIScriptEngine *engine, const char *filename);

// 登録されたアプリケーションインターフェースをテキストストリームに書き込みます。
int WriteConfigToStream(asIScriptEngine *engine, std::ostream &strm); 

// テキストストリームからインターフェースをロードし、それでエンジンを設定します。
// 正しい関数ポインタを設定しないため、このエンジンでスクリプトを実行することはできませんが、
// スクリプトをコンパイルしてバイトコードを保存するために使用できます。
int ConfigEngineFromStream(asIScriptEngine *engine, std::istream &strm, const char *nameOfStream = "config", asIStringFactory *stringFactory = 0);
```

---

## 自動ラッパー関数

**パス:** `/sdk/add_on/autowrapper/aswrappedcall.h`

このヘッダーファイルには、アプリケーション開発者がプリプロセッサ・マクロを呼び出すだけで、「汎用呼び出し規約（generic calling convention）」を用いたラッパー関数を自動生成できるテンプレート関数およびマクロが定義されています。これは、ネイティブ呼び出し規約がまだサポートされていない新しいプラットフォームなどで非常に有用です。

```cpp
// 暗黙的または明示的なシグネチャを持つグローバル関数をラップします
#define WRAP_FN(name)
#define WRAP_FN_PR(name, Parameters, ReturnType)

// 暗黙的または明示的なシグネチャを持つクラスメソッドをラップします
#define WRAP_MFN(ClassType, name)
#define WRAP_MFN_PR(ClassType, name, Parameters, ReturnType)

// グローバル関数をエミュレートするクラスメソッドをラップします
#define WRAP_MFN_GLOBAL(ClassType, name)
#define WRAP_MFN_GLOBAL_PR(ClassType, name, Parameters, ReturnType)

// クラスメソッドをエミュレートし 'this' ポインタを最初の引数として受け取るグローバル関数をラップします
#define WRAP_OBJ_FIRST(name)
#define WRAP_OBJ_FIRST_PR(name, Parameters, ReturnType)

// クラスメソッドをエミュレートし 'this' ポインタを最後の引数として受け取るグローバル関数をラップします
#define WRAP_OBJ_LAST(name)
#define WRAP_OBJ_LAST_PR(name, Parameters, ReturnType)

// 明示的なシグネチャを持つコンストラクタをラップします
#define WRAP_CON(ClassType, Parameters)

// デストラクタをラップします
#define WRAP_DES(ClassType)
```

### 使用例

```cpp
#include "aswrappedcall.h"

// 登録したいアプリケーション関数
void DoSomething(std::string param1, int param2);

// AngelScript へのラッパーの登録
void RegisterWrapper(asIScriptEngine *engine)
{
  int r;

  // WRAP_FN マクロは汎用ラッパー関数の関数ポインタを自動的に実装して返します。
  // 呼び出し規約は asCALL_GENERIC に設定する必要があることに注意してください。
  r = engine->RegisterGlobalFunction("void DoSomething(string, int)", WRAP_FN(DoSomething), asCALL_GENERIC);
  assert(r >= 0);
}
```

`aswrappedcall.h` ヘッダーファイルはデフォルトで最大4つの引数を持つ関数をサポートするように準備されています。それ以上の引数が必要な場合は、サブディレクトリに含まれるジェネレーターを使用して新しいヘッダーファイルを準備できます。

---

## 例外ルーティン

**パス:** `/sdk/add_on/scripthelper/`

例外処理ルーティンは `RegisterExceptionRoutines` の呼び出しによってアプリケーションに登録されます。

### C++ パブリックインターフェース

```cpp
// 例外ルーティンを登録します:
//   'void throw(const string &msg)'
//   'string getExceptionInfo()'
void RegisterExceptionRoutines(asIScriptEngine *engine);
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib#例外処理-(exception-handling)) を参照してください。

---

## string オブジェクト

**パス:** `/sdk/add_on/scriptstdstring/`

このアドオンは、C++ の `std::string` 型を AngelScript に直接登録します。これにより、パラメータや戻り値に `std::string` を使用する C++ 関数との完全な互換性が得られます。

`std::string` は値型であるため、スクリプト内で文字列が受け渡しされるたびにコピーが発生し、パフォーマンスに影響を与える可能性があります。しかし、これが問題になるのは極端に重い文字列操作を行うスクリプトに限られます。

`RegisterStdString(asIScriptEngine*)` で型を登録します。オプションの `split` メソッドとグローバルの `join` 関数は `RegisterStdStringUtils(asIScriptEngine*)` で登録します（事前に array アドオンを登録する必要があります）。

プリプロセッサ定義 `AS_USE_STLNAMES=1` でコンパイルすると、C++ STL と同じ名前でメソッドが登録されます。

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## array テンプレートオブジェクト

**パス:** `/sdk/add_on/scriptarray/`

`array` 型は、任意の型の配列を宣言できるようにする[テンプレートオブジェクト](./doc_adv_template)です。汎用的なクラスであるため、実行時に型の特性を判断する必要があり、パフォーマンス面では最適ではありません。そのため、頻繁に使用される特定の型については、[テンプレートの特殊化](./doc_adv_template)（Template Specialization）を登録することをお勧めします。

`RegisterScriptArray(asIScriptEngine *engine, bool defaultArrayType)` で型を登録します。`type[]` 構文で配列を宣言できるようにしたい場合は、2番目のパラメータを true に設定してください。

### C++ パブリックインターフェース

```cpp
class CScriptArray
{
public:
  static void SetMemoryFunctions(asALLOCFUNC_t allocFunc, asFREEFUNC_t freeFunc);

  // ファクトリ関数
  static CScriptArray *Create(asITypeInfo *arrayType);
  static CScriptArray *Create(asITypeInfo *arrayType, asUINT length);
  static CScriptArray *Create(asITypeInfo *arrayType, asUINT length, void *defaultValue);
  static CScriptArray *Create(asITypeInfo *arrayType, void *listBuffer);

  // メモリ管理
  void AddRef() const;
  void Release() const;

  // 型情報
  asITypeInfo   *GetArrayObjectType() const;
  int            GetArrayTypeId() const;
  int            GetElementTypeId() const;

  asUINT GetSize() const;
  bool IsEmpty() const;
  void Reserve(asUINT numElements);
  void Resize(asUINT numElements);
  
  void       *At(asUINT index);
  const void *At(asUINT index) const;
  void  SetValue(asUINT index, void *value);

  CScriptArray &operator=(const CScriptArray&);
  bool operator==(const CScriptArray &) const;

  void InsertAt(asUINT index, void *value);
  void RemoveAt(asUINT index);
  void InsertLast(void *value);
  void RemoveLast();
  void SortAsc();
  void SortAsc(asUINT startAt, asUINT count);
  void SortDesc();
  void SortDesc(asUINT startAt, asUINT count);
  void Sort(asUINT startAt, asUINT count, bool asc);
  void Sort(asIScriptFunction *less, asUINT startAt, asUINT count);
  void Reverse();
  int  Find(void *value) const;
  int  Find(asUINT startAt, void *value) const;
  int  FindByRef(void *ref) const;
  int  FindByRef(asUINT startAt, void *ref) const;
  
  void *GetBuffer();
};
```

### C++ での使用例

```cpp
// AngelScript に 'array<string> @CreateArrayOfString()' として登録
CScriptArray *CreateArrayOfStrings()
{
  asIScriptContext *ctx = asGetActiveContext();
  if( ctx )
  {
    asIScriptEngine* engine = ctx->GetEngine();

    // 型情報を取得します（パフォーマンスのためにキャッシュしてください）
    asITypeInfo* t = engine->GetTypeInfoByDecl("array<string>");

    // 初期サイズ3の配列を作成します
    CScriptArray* arr = CScriptArray::Create(t, 3);
    for( asUINT i = 0; i < arr->GetSize(); i++ )
    {
      string val("test");
      arr->SetValue(i, &val);
    }
    return arr;
  }
  return 0;
}
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## grid テンプレートオブジェクト

**パス:** `/sdk/add_on/scriptgrid/`

`grid` 型は、任意の型の 2 次元グリッド（格子状のデータ構造）を宣言できるようにする[テンプレートオブジェクト](./doc_adv_template)です。多くの点で `array` と似ていますが、 2 次元の範囲やマップなどの管理に特化しています。

`RegisterScriptGrid(asIScriptEngine *engine)` で型を登録します。

### C++ パブリックインターフェース

```cpp
class CScriptGrid
{
public:
  static void SetMemoryFunctions(asALLOCFUNC_t allocFunc, asFREEFUNC_t freeFunc);

  static CScriptGrid *Create(asITypeInfo *gridType);
  static CScriptGrid *Create(asITypeInfo *gridType, asUINT width, asUINT height);
  static CScriptGrid *Create(asITypeInfo *gridType, asUINT width, asUINT height, void *defaultValue);
  static CScriptGrid *Create(asITypeInfo *gridType, void *listBuffer);

  void AddRef() const;
  void Release() const;

  asITypeInfo   *GetGridObjectType() const;
  int            GetGridTypeId() const;
  int            GetElementTypeId() const;

  asUINT GetWidth() const;
  asUINT GetHeight() const;
  void   Resize(asUINT width, asUINT height);
  
  void       *At(asUINT x, asUINT y);
  const void *At(asUINT x, asUINT y) const;
  void  SetValue(asUINT x, asUINT y, void *value);
};
```

### スクリプトインターフェース

```cs
class grid<T>
{
  grid();
  grid(uint width, uint height);
  grid(uint width, uint height, const T &in fillValue);

  uint width() const;
  uint height() const;
  void resize(uint w, uint h);
  
  T &opIndex(uint x, uint y);
  const T &opIndex(uint x, uint y) const;
}
```

**`grid()`, `grid(uint width, uint height)`, `grid(uint width, height, const T &in fillValue)`**  
コンストラクタはグリッドオブジェクトを初期化します。デフォルトコンストラクタはサイズゼロのグリッドを作成します。

**`uint width() const`, `uint height() const`**  
グリッドの幅と高さを返します。

**`void resize(uint w, uint h)`**  
グリッドを新しいサイズに変更します。グリッドに収まる要素は値を保持します。

**`T &opIndex(uint x, uint y)`**  
インデックス演算子は要素の1つへの参照を返します。インデックスが境界外の場合、スクリプト例外が発生します。

### スクリプトでの使用例

```cs
// 5x5 のマップを初期化します
grid<int> map = {{1,0,1,1,1},
                 {0,0,1,0,0},
                 {0,1,1,0,1},
                 {0,1,1,0,1},
                 {0,0,0,0,1}};
 
// 次のエリアが歩行可能かを確認する関数
bool canWalk(uint x, uint y)
{
  // マップの目的地がクリアであれば、そこに移動できます
  return map[x,y] == 0;
}
```

---

## any オブジェクト

**パス:** `/sdk/add_on/scriptany/`

`any` 型は、任意の値を保持できる汎用コンテナです。オブジェクトハンドル（参照型）として扱われます。

`RegisterScriptAny(asIScriptEngine*)` で型を登録します。

### C++ パブリックインターフェース

```cpp
class CScriptAny
{
public:
  CScriptAny(asIScriptEngine *engine);
  CScriptAny(void *ref, int refTypeId, asIScriptEngine *engine);

  int AddRef() const;
  int Release() const;

  CScriptAny &operator=(const CScriptAny&);
  int CopyFrom(const CScriptAny *other);

  void Store(void *ref, int refTypeId);
  void Store(asINT64 &value);
  void Store(double &value);

  bool Retrieve(void *ref, int refTypeId) const;
  bool Retrieve(asINT64 &value) const;
  bool Retrieve(double &value) const;

  int GetTypeId() const;
};
```

### スクリプトインターフェース

```cs
class any
{
  any();
  any(? &in value);
  any(int64 &in value);
  any(double &in value);

  any &opAssign(const any &in other);
  
  void store(? &in value);
  void store(int64 &in value);
  void store(double &in value);
  
  bool retrieve(? &out value) const;
  bool retrieve(int64 &out value) const;
  bool retrieve(double &out value) const;
}
```

**`any()`, `any(? &in value)`, `any(int64 &in value)`, `any(double &in value)`**  
デフォルトコンストラクタは空のオブジェクトを作成し、2番目は提供された値でオブジェクトを初期化します。

**`any &opAssign(const any &in other)`**  
代入演算子は他のオブジェクトから含まれる値をコピーします。

**`void store(? &in value)`, `void store(int64 &in value)`, `void store(double &in value)`**  
これらのメソッドはオブジェクト内の値を設定します。

**`bool retrieve(? &out value) const`, `bool retrieve(int64 &out value) const)`, `bool retrieve(double &out value) const`**  
これらのメソッドはオブジェクトに格納された値を取得します。格納された値が要求された型と互換性がある場合に true を返します。

### スクリプトでの使用例

```cs
int value;
obj object;
obj @handle;
any a, b, c;
a.store(value);      // 値を格納します
b.store(@handle);    // オブジェクトハンドルを格納します
c.store(object);     // オブジェクトのコピーを格納します

a.retrieve(value);   // 値を取得します
b.retrieve(@handle); // オブジェクトハンドルを取得します
c.retrieve(object);  // オブジェクトのコピーを取得します
```

---

## ref オブジェクト

**パス:** `/sdk/add_on/scripthandle/`

`ref` 型は、任意のオブジェクトへのハンドルを保持できる汎用コンテナです。実行形式上は値型ですが、その挙動はオブジェクトハンドルに非常に近いです。

`RegisterScriptHandle(asIScriptEngine*)` で型を登録します。

参照: [汎用ハンドル](./doc_adv_generic_handle)

### C++ パブリックインターフェース

```cpp
class CScriptHandle 
{
public:
  CScriptHandle();
  CScriptHandle(const CScriptHandle &other);
  CScriptHandle(void *ref, int typeId);
  ~CScriptHandle();

  CScriptHandle &operator=(const CScriptHandle &other);
  
  void Set(void *ref, asITypeInfo *type);

  bool operator==(const CScriptHandle &o) const;
  bool operator!=(const CScriptHandle &o) const;
  bool opEquals(void *ref, int typeId) const;

  void Cast(void **outRef, int typeId);

  asITypeInfo   *GetType() const;
  int            GetTypeId() const;
  
  void *GetRef();
};
```

### C++ からの使用例

`CScriptHandle` は値型ですが、その型のプロパティを登録する場合は、ハンドルとして登録する必要があります。関数の引数と戻り値の型についても同様です。

```cpp
CScriptHandle g_handle;

void Register(asIScriptEngine *engine)
{
  int r;
  r = engine->RegisterGlobalProperty("ref @g_handle", &g_handle); assert( r >= 0 );
  r = engine->RegisterGlobalFunction("void Function(ref @)", asFUNCTION(Function), asCALL_CDECL); assert( r >= 0 );
}
```

アプリケーションからハンドルにオブジェクトポインタを設定するには、オブジェクトへのポインタとオブジェクトの型を渡して `Set()` メソッドを使用します。アプリケーションからオブジェクトポインタを取得するには、ポインタへのポインタと必要な型IDを渡して `Cast()` メソッドを使用します。

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## weakref オブジェクト

**パス:** `/sdk/add_on/weakref/`

`weakref` 型は、オブジェクトへの弱参照（対象となるオブジェクトの参照カウントを増やさず、その寿命を延ばさない参照）を保持するためのテンプレート型です。

`RegisterScriptWeakRef(asIScriptEngine*)` で型を登録します。

参照: [弱参照](./doc_adv_weakref)

### C++ パブリックインターフェース

```cpp
class CScriptWeakRef 
{
public:
  CScriptWeakRef(asITypeInfo *type);
  CScriptWeakRef(const CScriptWeakRef &other);
  CScriptWeakRef(void *ref, asITypeInfo *type);
  ~CScriptWeakRef();

  CScriptWeakRef &operator=(const CScriptWeakRef &other);

  bool operator==(const CScriptWeakRef &o) const;
  bool operator!=(const CScriptWeakRef &o) const;

  CScriptWeakRef &Set(void *newRef);

  // オブジェクトがまだ生きている場合に返します（返されたオブジェクトの参照カウントをインクリメントします）
  void *Get() const;

  bool Equals(void *ref) const;
  
  asITypeInfo *GetRefType() const;
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## dictionary オブジェクト

**パス:** `/sdk/add_on/scriptdictionary/`

`dictionary`（辞書）オブジェクトは、文字列値をキーとして、任意の型の値またはオブジェクトをマッピング（関連付け）するデータ構造です。

`RegisterScriptDictionary(asIScriptEngine*)` で登録します。

### C++ パブリックインターフェース

```cpp
class CScriptDictionary
{
public:
  static CScriptDictionary *Create(asIScriptEngine *engine);

  void AddRef() const;
  void Release() const;

  CScriptDictionary &operator=(const CScriptDictionary &other);

  void Set(const dictKey &key, void *value, int typeId);
  void Set(const dictKey &key, asINT64 &value);
  void Set(const dictKey &key, double &value);

  bool Get(const dictKey &key, void *value, int typeId) const;
  bool Get(const dictKey &key, asINT64 &value) const;
  bool Get(const dictKey &key, double &value) const;

  CScriptDictValue *operator[](const dictKey &key);
  const CScriptDictValue *operator[](const dictKey &key) const;
  
  int  GetTypeId(const dictKey &key) const;
  bool Exists(const dictKey &key) const;
  bool IsEmpty() const;
  asUINT GetSize() const;
  bool Delete(const dictKey &key);
  void DeleteAll();
  CScriptArray *GetKeys() const;

  // STL スタイルのイテレータ
  class CIterator
  {
  public:
    void operator++();
    void operator++(int);
    bool operator==(const CIterator &other) const;
    bool operator!=(const CIterator &other) const;
    const dictKey &GetKey() const;
    int            GetTypeId() const;
    bool           GetValue(asINT64 &value) const;
    bool           GetValue(double &value) const;
    bool           GetValue(void *value, int typeId) const;
    const void *   GetAddressOfValue() const;
  };
  
  CIterator begin() const;
  CIterator end() const;
  CIterator find(const dictKey &key) const;
};
```

### C++ での使用例

```cpp
void iterateDictionary(CScriptDictionary *dict)
{
  for (auto it : *dict)
  {
    std::string keyName = it.GetKey();
    int typeId = it.GetTypeId();
    const void *addressOfValue = it.GetAddressOfValue();
    // typeId に従って値を正しい C++ 型にキャストして処理します
  }
}
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## file オブジェクト

**パス:** `/sdk/add_on/scriptfile/`

このオブジェクトはファイルの読み書きのサポートを提供します。

`RegisterScriptFile(asIScriptEngine*)` で登録します。

スクリプトに書き込みアクセスを提供したくない場合は、`AS_WRITE_OPS 0` の定義でアドオンをコンパイルすることで書き込みのサポートを無効にできます。

### C++ パブリックインターフェース

```cpp
class CScriptFile
{
public:
  CScriptFile();
  void AddRef() const;
  void Release() const;

  // mode = "r" -> 読み取り用ファイルを開きます
  // mode = "w" -> 書き込み用ファイルを開きます（既存ファイルを上書き）
  // mode = "a" -> 追記用ファイルを開きます
  int Open(const std::string &filename, const std::string &mode);
  int Close();
  
  int GetSize() const;
  bool IsEOF() const;

  std::string ReadString(unsigned int length);
  std::string ReadLine();
  asINT64     ReadInt(asUINT bytes);
  asQWORD     ReadUInt(asUINT bytes);
  float       ReadFloat();
  double      ReadDouble();
    
  int WriteString(const std::string &str);
  int WriteInt(asINT64 v, asUINT bytes);
  int WriteUInt(asQWORD v, asUINT bytes);
  int WriteFloat(float v);
  int WriteDouble(double v);

  int GetPos() const;
  int SetPos(int pos);
  int MovePos(int delta);

  // バイナリ値の読み書きメソッドでビッグエンディアン（最上位バイト優先）を使用するかどうか（デフォルト: false）
  bool mostSignificantByteFirst;
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## filesystem オブジェクト

**パス:** `/sdk/add_on/scriptfile/`

このオブジェクトは、ファイルシステム上のディレクトリ構造を検査し、操作するための機能を提供します。

`RegisterScriptFileSystem(asIScriptEngine*)` で登録します。

### C++ パブリックインターフェース

```cpp
class CScriptFileSystem
{
public:
  CScriptFileSystem();
  void AddRef() const;
  void Release() const;

  bool ChangeCurrentPath(const std::string &path);
  std::string GetCurrentPath() const;

  bool IsDir(const std::string &path) const;
  bool IsLink(const std::string &path) const;
  asINT64 GetSize(const std::string &path) const;
  
  CScriptArray *GetFiles() const;
  CScriptArray *GetDirs() const;
  
  int MakeDir(const std::string &path);
  int RemoveDir(const std::string &path);
  int DeleteFile(const std::string &path);
  int CopyFile(const std::string &source, const std::string &target);
  int Move(const std::string &source, const std::string &target);
  
  CDateTime GetCreateDateTime(const std::string &path) const;
  CDateTime GetModifyDateTime(const std::string &path) const; 
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## math 関数

**パス:** `/sdk/add_on/scriptmath/`

このアドオンは、標準 C ランタイムライブラリ（CRT）の数学関数を AngelScript に登録します。`RegisterScriptMath(asIScriptEngine*)` を呼び出して登録を行います。

プリプロセッサ定義 `AS_USE_FLOAT=0` を定義することで、関数は float の代わりに double を取って返すように登録されます。

関数 `RegisterScriptMathComplex(asIScriptEngine*)` は複素数（実部と虚部を持つ数）を表す `complex` 型を登録します。

### スクリプトインターフェース

```cs
// 三角関数
float cos(float rad);   // コサイン（ラジアン入力）
float sin(float rad);   // サイン（ラジアン入力）
float tan(float rad);   // タンジェント（ラジアン入力）

// 逆三角関数
float acos(float val);           // アークコサイン（ラジアン返却）
float asin(float val);           // アークサイン（ラジアン返却）
float atan(float val);           // アークタンジェント（ラジアン返却）
float atan2(float y, float x);   // アークタンジェント2（ラジアン返却）

// 双曲線関数
float cosh(float rad);  // 双曲コサイン
float sinh(float rad);  // 双曲サイン
float tanh(float rad);  // 双曲タンジェント

// 対数関数
float log(float val);    // 自然対数
float log10(float val);  // 常用対数（底10）

// べき乗
float pow(float val, float exp);  // base の exp 乗

// 平方根
float sqrt(float val);

// 絶対値
float abs(float val);

// 切り上げと切り捨て
float ceil(float val);   // 以上の最近接整数
float floor(float val);  // 以下の最近接整数

// 小数部分の返却
float fraction(float val);

// 浮動小数点の近似比較（数値誤差への対処のため）
bool closeTo(float a, float b, float epsilon = 0.00001f);
bool closeTo(double a, double b, double epsilon = 0.0000000001);

// 浮動小数点と IEEE 754 表現の間の変換
float  fpFromIEEE(uint raw); 
double fpFromIEEE(uint64 raw);
uint   fpToIEEE(float fp);
uint64 fpToIEEE(double fp);
```

**`closeTo`**  
実数の2進表現による数値誤差のため、2つの float 値を直接比較することはしばしば困難です。`closeTo` 関数は2つの値がほぼ等しい場合に true を返し、epsilon 値の大きさまでの小さな差を許容します。

**`fpFromIEEE, fpToIEEE`**  
float を IEEE 754 表現へまたは表現から変換します。2進表現で浮動小数点値を直接検査または操作したい場合に使用できます。

### complex 型

```cs
// この型は実部と虚部を持つ複素数を表します
class complex
{
  // コンストラクタ
  complex();
  complex(const complex &in);
  complex(float r);
  complex(float r, float i);

  // 等値演算子
  bool opEquals(const complex &in) const;

  // 複合代入演算子
  complex &opAddAssign(const complex &in);
  complex &opSubAssign(const complex &in);
  complex &opMulAssign(const complex &in);
  complex &opDivAssign(const complex &in);
  
  // 算術演算子
  complex opAdd(const complex &in) const;
  complex opSub(const complex &in) const;
  complex opMul(const complex &in) const;
  complex opDiv(const complex &in) const;
  
  // 絶対値（大きさ）を返します
  float abs() const;

  // スウィズル演算子
  complex get_ri() const;
  void set_ri(const complex &in);
  complex get_ir() const;
  void set_ir(const complex &in);
  
  // 実部と虚部
  float r;
  float i;
}
```

---

## datetime オブジェクト

**パス:** `/sdk/add_on/datetime/`

`CDateTime` クラスはスクリプトがシステムの日時を取得する方法を提供します。

`RegisterScriptDateTime(asIScriptEngine*)` で型を登録します。

:::message
このクラスは C++11 以降でコンパイルする必要があります。
:::

### C++ パブリックインターフェース

```cpp
class CDateTime
{
public:
  CDateTime();
  CDateTime(const CDateTime &other);
  CDateTime(asUINT year, asUINT month, asUINT day, asUINT hour, asUINT minute, asUINT second);

  CDateTime &operator=(const CDateTime &other);

  asUINT getYear() const;
  asUINT getMonth() const;
  asUINT getDay() const;
  asUINT getHour() const;
  asUINT getMinute() const;
  asUINT getSecond() const;
  asUINT getWeekDay() const;
  
  bool setDate(asUINT year, asUINT month, asUINT day);
  bool setTime(asUINT hour, asUINT minute, asUINT second);
  
  // 2つの datetime の差を秒単位で返します
  asINT64          operator-(const CDateTime &other) const;
  CDateTime        operator+(asINT64 seconds) const;
  friend CDateTime operator+(asINT64 seconds, const CDateTime &other);
  CDateTime &      operator+=(asINT64 seconds);
  CDateTime        operator-(asINT64 seconds) const;
  friend CDateTime operator-(asINT64 seconds, const CDateTime &other);
  CDateTime &      operator-=(asINT64 seconds);
  bool             operator==(const CDateTime &other) const;
  bool             operator<(const CDateTime &other) const;
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

## socket オブジェクト

**パス:** `/sdk/add_on/scriptsocket/`

`CScriptSocket` はスクリプトに使いやすい TCP ソケットを提供します。

:::message
現在このアドオンは Windows のみで動作します。
:::

### C++ パブリックインターフェース

```cpp
class CScriptSocket
{
public:
  CScriptSocket();

  void AddRef() const;
  void Release() const;

  int            Listen(asWORD port);
  int            Close();
  CScriptSocket* Accept(asINT64 timeoutMicrosec = 0);
  int            Connect(asUINT ipv4Address, asWORD port);
  int            Send(const std::string& data);
  std::string    Receive(asINT64 timeoutMicrosec = 0);
  bool           IsActive() const;
};
```

スクリプトインターフェースについては [標準ライブラリ](./doc_script_stdlib) を参照してください。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_addon.html
