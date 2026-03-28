---
title: "並行スクリプト (Concurrent scripts)"
---

スクリプトエンジンは、複数のスクリプトを並行して実行（並行実行）させることができます。これは、各スレッドが個別のスクリプトコンテキストを実行する[マルチスレッド](./doc_adv_multithread)を利用すれば容易に実現できますが、本稿ではマルチスレッドを使用せずに並行実行を行う方法について解説します。

複数のスクリプトを並行して実行するには、各スクリプトが専用の `asIScriptContext` を持ち、[通常の関数呼び出し](./doc_call_script_func)と同様にセットアップされている必要があります。その上で、アプリケーション側で各コンテキストに実行時間の制限（タイムアウト）を設けます。タイムアウトに達したコンテキストは `Suspend` メソッドで一時停止させ、次のコンテキストに実行権を譲るように構成します。

以下は、この仕組みの非常にシンプルな実装例です：

```cpp
// この関数が呼び出される前に、各コンテキストは準備（Prepare）済みであるとします
void ExecuteScripts(std::vector<asIScriptContext *> contexts)
{
  // この関数はすべてのスクリプトが完了するまで実行されます
  while( contexts.size() > 0 )
  {
    for( asUINT n = 0; n < contexts.size(); n++ )
    {
      // このコンテキストに対して 10 ミリ秒のタイムアウトを設定します
      SetTimeoutForContext(contexts[n], 10);

      // Execute を呼び出して、このコンテキストの実行を再開します
      int r = contexts[n]->Execute();

      // 誤ってトリガーされないように、タイムアウトを解除します
      RemoveTimeoutForContext();

      // スクリプトの実行が完了したか、それともタイムアウトしたかを判断します
      if( r == asEXECUTION_SUSPENDED )
      {
        // タイムアウトしたため、スクリプトの実行は次のループ（イテレーション）で続行されます
      }
      else
      {
        // スクリプトの実行が完了したため、スクリプトのリストから除外します
        contexts[n--] = contexts.back();
        contexts.pop_back();
      }
    }
  }
}
```

アプリケーションは、各スクリプトに均等な実行時間を与える単純なラウンドロビン（Round-robin）方式で実行を管理することもできますし、優先度の高いスクリプトにより多くの実行時間を与えるといった、より高度なスケジューリングアルゴリズムを構築することも可能です。

前述の `SetTimeoutForContext` のようなタイムアウト機能は、主に 2 つの方法で実装できます。

1 つ目は、[ラインコールバック](./doc_debug#ラインブレークポイントの設定-(setting-line-breaks))を使用する方法です。コンテキストはスクリプト内の各ステートメントの実行ごとにコールバックを呼び出します。そこでタイムアウトに達したかどうかを確認し、達していればコンテキストをサスペンドさせます。

2 つ目は、タイムアウト専用のスレッドを使用する方法です。このスレッドはタイムアウト時間に達するまでスリープし、復帰時に（実行中であれば）そのコンテキストをサスペンドさせます。

タイムアウト専用スレッドを使用する方法は実装が比較的容易で、ラインコールバックに比べてパフォーマンスへの影響も少なくなります。ただし、ターゲット OS がマルチスレッドをサポートしていない場合は、ラインコールバックを使用する必要があります。

別のスレッドを用いてタイムアウト関数を実装する簡単な例を以下に示します：

```cpp
static HANDLE            thread_handle = 0;
static asIScriptContext *thread_ctx;

DWORD WINAPI TimeoutThread(void *sleeptime)
{
  Sleep(*reinterpret_cast<int*>(sleeptime));
  if( thread_ctx )
    thread_ctx->Suspend();

  return 0;
}

void SetTimeoutForContext(asIScriptContext *ctx, int milliseconds)
{
  thread_ctx    = ctx;
  thread_handle = CreateThread(0, 50, TimeoutThread, reinterpret_cast<void*>(&milliseconds), 0, 0);
}

void RemoveTimeoutForContext()
{
  // TerminateThread は細心の注意を払って使用されるべきですが、
  // この場合、実行途中で中断されたとしても TimeoutThread は何の害も及ぼしません
  TerminateThread(thread_handle, 0);
  thread_handle = 0;
}
```

マルチスレッドのルーチンはターゲットシステムに大きく依存して異なるのが一般的であることに注意してください。上記のコードは Windows 向けであり、他のシステムで動作させるためには適応が必要になる可能性が高いです。

参照: [Context manager アドオン](./doc_addon#コンテキストマネージャー)、[Concurrent scripts サンプル](./doc_samples#concurrent-scripts（並行スクリプト）)、[コルーチン](./doc_adv_coroutine)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_concurrent.html
