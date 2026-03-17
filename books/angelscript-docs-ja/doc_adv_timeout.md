---
title: "長く実行されるスクリプトのタイムアウト (Timeout long running scripts)"
---

実行時間の長いスクリプトがアプリケーションをフリーズさせるのを防ぐために、実行をタイムアウトさせる方法を追加する必要がある場合があります。この記事では、これを実現するための2つの異なる方法を紹介します。

## ラインコールバックを使用する (With the line callback)

ラインコールバック機能を使用すると、スクリプトの実行中に特別な処理を実行させることができます。コールバックはスクリプトのステートメントごとに呼び出されるため、スクリプトが長時間実行され過ぎていないかを検証し、もしそうであれば実行を一時停止（サスペンド）して後で再開できるようにすることができます。

コンテキストの `Execute` メソッドを呼び出す前に、次のようにコールバック関数を設定します：

```cpp
int ExecuteScriptWithTimeOut(asIScriptContext *ctx)
{
  // タイムアウト時間を1秒後に設定する
  DWORD timeOut = timeGetTime() + 1000;

  // スクリプトをタイムアウトさせるラインコールバックを設定する
  ctx->SetLineCallback(asFUNCTION(LineCallback), &timeOut, asCALL_CDECL);

  // スクリプトを実行する
  int status = ctx->Execute();

  // もしステータスが asEXECUTION_SUSPENDED であった場合、
  // この関数を再度呼び出すことでスクリプトを再開できます。
  return status;
}

// ラインコールバック関数は、実行されるステートメントごとに VM によって呼び出されます
void LineCallback(asIScriptContext *ctx, DWORD *timeOut)
{
  // タイムアウト時間に達した場合、スクリプトを一時停止します
  if( *timeOut < timeGetTime() )
    ctx->Suspend();
}
```

タイムアウトした後の挙動については、[Events サンプル](./doc_samples#events) を参照してください。

スクリプトが `asEP_BUILD_WITHOUT_LINE_CUES` を指定してコンパイルされている場合、ラインコールバックが呼び出される頻度は下がりますが、少なくともすべてのループまたは関数呼び出しのたびに呼び出されることは保証されている点に注意してください。

## サブスレッドを使用する (With a secondary thread)

タイムアウト後に実行を一時停止させるために、2つ目のスレッド（サブスレッド）を立てることができます。このスレッドは、実行中のパフォーマンスに影響を与えないようにスリープ状態にさせることができます。スレッドがスリープから復帰したとき、コンテキストの `Suspend` メソッドを呼び出します。

以下は、これを行うためのコードの例です。スレッドをセットアップするためのコードはターゲットの OS ごとに異なるため、ここでは架空のものが使われていることに注意してください。

```cpp
// スレッド間で共有される変数
asIScriptContext *threadCtx;
int threadId;

// この関数はサブスレッドで実行されます
void SuspendThread()
{
  // タイムアウト（1秒）までスレッドをスリープ状態にする
  Sleep(1000);
  
  // スリープから復帰したら、コンテキストの Suspend メソッドを呼び出します
  ctx->Suspend();
}

// この関数はタイムアウトスレッドをセットアップし、スクリプトを実行します
int ExecuteScriptWithTimeOut(asIScriptContext *ctx)
{
  // スレッドを作成する前に、共有するコンテキストのポインタを設定します
  threadCtx = ctx;

  // ただちにスリープ状態に入るスレッドを作成します
  threadId = CreateThread(SuspendThread);
  
  // スクリプトを実行します
  int status = ctx->Execute();
  
  // コンテキストを解放する前にサブスレッドを破棄します
  DestroyThread(threadId);
  
  // グローバル変数をクリアします
  threadId = 0;
  threadCtx = 0;
  
  // もしステータスが asEXECUTION_SUSPENDED であった場合、
  // この関数を再度呼び出すことでスクリプトを再開できます。
  
  return status;
}
```

この方法によるアプローチは、AngelScript ライブラリが [マルチスレッドのサポート](./doc_adv_multithread) なしでビルドされている場合でも安全に機能することに注目してください。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_timeout.html
