---
title: "長く実行されるスクリプトのタイムアウト (Timeout long running scripts)"
---

スクリプトの無限ループや長時間の処理によってアプリケーションがフリーズするのを防ぐために、実行時間の制限（タイムアウト）を設ける方法が必要です。本稿では、これを実現するための 2 つの手法を紹介します。

## ラインコールバックを利用する (With the line callback)

ラインコールバック機能を利用すると、スクリプトの実行中に特定の処理を介入させることができます。コールバックはスクリプトのステートメント（文）ごとに呼び出されるため、そこで実行時間をチェックし、制限時間を超えた場合には実行を中断（サスペンド）して、後で再開させることが可能です。

コンテキストの `Execute` メソッドを呼び出す前に、以下のようにコールバック関数を設定します。

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

この動作の詳細については、[Events サンプル](./doc_samples#events（イベント）) を参照してください。

もしスクリプトが `asEP_BUILD_WITHOUT_LINE_CUES` エンジンプロパティを有効にしてコンパイルされている場合、ラインコールバックの呼び出し頻度は低下しますが、少なくともすべてのループ内や関数呼び出しの際には呼び出されることが保証されています。

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
  // 1秒間（タイムアウト時間）スリープします
  Sleep(1000);
  
  // スリープから復帰したら、コンテキストをサスペンド（一時停止）させます
  threadCtx->Suspend();
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

この手法は、AngelScript ライブラリが [マルチスレッドのサポート](./doc_adv_multithread) なしでビルドされている場合でも安全に機能することに注目してください。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_timeout.html
