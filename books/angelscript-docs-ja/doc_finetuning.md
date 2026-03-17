---
title: "パフォーマンスの微調整 (Fine tuning)"
---

AngelScript から最大限のパフォーマンスを引き出すためのいくつかの推奨事項を以下に示します。

## 関数と型のキャッシュ (Cache the functions and types)

関数の宣言や名前による検索はかなり時間がかかるため、呼び出される関数ごとに1回以上行うべきではありません。使用する可能性のある型についても同様です。

また、可能な限り、ID の代わりに実際の [asIScriptFunction](#asIScriptFunction) や [asITypeInfo](#asITypeInfo) のポインタを使用するようにしてください。これにより、エンジンが ID を実際のオブジェクトに変換する手間を省くことができます。

キャッシュされた情報を保存するために、様々なエンジンインターフェースのユーザーデータ (user data) を利用することができます。例えば、よく使用されるクラスメソッドを含む構造体を、[asITypeInfo](#asITypeInfo) インターフェースの [ユーザーデータ](#asITypeInfo::SetUserData) として保存します。このようにすれば、関数を呼び出す必要がある時に素早くアクセスすることができます。

## コンテキストオブジェクトの再利用 (Reuse the context object)

コンテキストオブジェクトは軽量なオブジェクトではないため、呼び出しのたびに新しいインスタンスを割り当てるのは避けるべきです。このオブジェクトは、複数の呼び出しで再利用できるように設計されています。

### コンテキストプール (Context pool)

理想的には、アプリケーションは割り当てられたコンテキストオブジェクトのシンプルなメモリプールを保持し、プール内に空きオブジェクトがない場合にのみ新しいオブジェクトが割り当てられるようにします。

エンジンの [コンテキストコールバック](#asIScriptEngine::SetContextCallbacks) を使用することで、このコンテキストプールはエンジンの内部呼び出しやアドオンからの使用のためにも自動的に利用可能になります。

プールからコンテキストを使用したいコードは、[CreateContext](#asIScriptEngine::CreateContext) メソッドの代わりに、[RequestContext](#asIScriptEngine::RequestContext) と [ReturnContext](#asIScriptEngine::ReturnContext) メソッドを使用するべきです。

以下は、コンテキストプールの簡単な実装例です。

```cpp
std::vector<asIScriptContext *> pool;
asIScriptContext *RequestContextCallback(asIScriptEngine *engine, void *param)
{
  // プールからコンテキストを取得するか、新しく作成します
  asIScriptContext *ctx = 0;
  if( pool.size() )
  {
    ctx = *pool.rbegin();
    pool.pop_back();
  }
  else
    ctx = engine->CreateContext();

  return ctx;
}

void ReturnContextToPool(asIScriptEngine *engine, asIScriptContext *ctx, void *param)
{
  pool.push_back(ctx);
  
  // 再利用できないリソースを解放するために、コンテキストを Unprepare() します
  ctx->Unprepare();
}
```

### ネストされた呼び出し (Nested calls)

コンテキストを再利用するもう1つの形態は、ネストされた呼び出し (nested calls) を使用することです。

スクリプトから呼び出されたアプリケーションの登録済み関数が別のスクリプトを実行する必要がある場合、すでにアクティブなコンテキストをネストされた呼び出しのために再利用することができます。このようにすれば、この呼び出しだけのためにプールから空きコンテキストを探したり、新しいコンテキストを割り当てたりする必要はありません。

```cpp
void Func()
{
  // アクティブなコンテキストを取得します
  asIScriptContext *ctx = asGetActiveContext();

  // 後で復元できるように、現在のコンテキストの状態を保存 (Push) します
  if( ctx && ctx->PushState() > 0 )
  {
    // 通常通りコンテキストを使用します
    //  ctx->Prepare(...);
    //  ctx->Execute(...);

    // 終了したら、以前の状態を復元 (Pop) します
    ctx->PopState();
  }
}
```

## ラインキュー無しのスクリプトコンパイル (Compile scripts without line cues)

ラインキュー (line cues) は通常、各スクリプト・ステートメント間のバイトコード内に配置されます。これらは、VM が実行のサスペンド（一時停止）を許可する場所であり、またラインコールバックが呼び出される場所でもあります。

もしスクリプト内で実行されるすべてのステートメントでコールバックを受け取る必要がない場合は、ラインキューを無しにしてコンパイルすることで、スクリプトから少しでも多くのパフォーマンスを引き出すことができるかもしれません。

ラインコールバックは依然として機能し、無限ループや無限再帰呼び出しをアプリケーションが中断できるように、スクリプト内の各ループおよび各関数呼び出しごとに少なくとも1回は呼び出されることが保証されています。

```cpp
engine->SetEngineProperty(asEP_BUILD_WITHOUT_LINE_CUES, true);
```

## スレッドセーフの無効化 (Disable thread safety)

もしアプリケーションがスクリプトエンジンを呼び出すために1つのスレッドしか使用しない場合、スレッドセーフ (thread safety) なしでライブラリをコンパイルすることで、わずかながらパフォーマンスを向上させる価値があるかもしれません。

これを行うには、ライブラリをコンパイルする際に `as_config.h` ヘッダーまたはプロジェクト設定で `AS_NO_THREADS` フラグを定義します。

## 自動ガベージコレクションの無効化 (Turn off automatic garbage collection)

ガベージコレクションは長時間実行されるアプリケーションにおいて重要ですが、自動ガベージコレクションをオフにし、その後制御された方法で手動でガベージコレクターを実行させることに関心があるかもしれません。ガベージコレクターはインクリメンタル（段階的）であるため実行中に長時間の停止は見られないはずですが、他のことのために必要かもしれない CPU サイクルを消費します。

自動ガベージコレクターをオフにするには、エンジンプロパティ [asEP_AUTO_GARBAGE_COLLECT](#asEP_AUTO_GARBAGE_COLLECT) を `false` に設定します。

```cpp
engine->SetEngineProperty(asEP_AUTO_GARBAGE_COLLECT, false);
```

参照: [ガベージコレクション](./doc_gc)

## ネイティブ呼び出し規約とジェネリック呼び出し規約の比較 (Compare native calling convention versus generic calling convention)

もし非常に頻繁に呼び出される特定の関数がある場合、ネイティブ呼び出し規約 (native calling convention) で関数をバインドする場合と、ジェネリック呼び出し規約 (generic calling convention) の場合のパフォーマンスを比較する価値があるかもしれません。どちらが常に速いと一般化して言うことはできず、関数のシグネチャやプラットフォームの ABI の複雑さに依存して変化します。

参照: [ジェネリック関数](./doc_generic)、[関数の登録 - 呼び出し規約](./doc_register_func_2)
