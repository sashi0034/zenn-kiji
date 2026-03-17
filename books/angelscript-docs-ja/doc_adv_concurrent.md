---
title: "並行スクリプト (Concurrent scripts)"
---

スクリプトエンジンは複数のスクリプトを並行して実行すること、すなわち並行スクリプト (concurrent scripts) を実行することができます。これは各スレッドが独自のスクリプトコンテキストを実行する [マルチスレッド](./doc_adv_multithread) を使用すれば簡単に行うことができますが、この記事ではマルチスレッドを使用せずに並行実行を行う方法について説明します。

複数のスクリプトを並行して実行するためには、各スクリプトが独自の [asIScriptContext](#asIScriptContext) を持っていなければならず、[通常の関数呼び出し](./doc_call_script_func) と同じようにコンテキストがセットアップされます。その後、アプリケーションは各コンテキストに対してタイムアウトを設定する必要があります。タイムアウトに達した場合、コンテキストは [サスペンド（一時停止）](#asIScriptContext::Suspend) され、次のコンテキストがしばらくの間実行できるようにすべきです。

以下は、これをどのように行えるかを示す非常に簡単な例です：

```cpp
// この関数が呼び出される前に、コンテキストは準備済みであるとします
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

      // スクリプトが完了したか、それともタイムアウトしたかを判断します
      if( r == asEXECUTION_SUSPENDED )
      {
        // スクリプトは次のイテレーションで続行されます
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

アプリケーションは、各スクリプトに均等な実行時間を与える単純なラウンドロビン (round-robin) 方式でスクリプトの実行を管理することもできますし、優先度の高いスクリプトにより多くの実行時間を与えるような、より複雑な管理アルゴリズムを構築することもできます。

上記の例の `SetTimeoutForContext` のようなタイムアウト関数は、2つの異なる方法で実装することができます。1つは [ラインコールバック](#asIScriptContext::SetLineCallback) を使用する方法で、コンテキストはスクリプト内の各ステートメントに対してコールバックを呼び出します。そこでコールバックがタイムアウトリミットに達したかどうかを確認し、コンテキストをサスペンドさせることができます。

もう1つの方法はタイムアウト用スレッドを使用することです。このスレッドはタイムアウトリミットに達するまで単にスリープし、スレッドが復帰した時にコンテキスト（がまだ実行中の場合）をサスペンドします。

タイムアウトスレッドを使用する方法が恐らく実装が最も簡単であり、またラインコールバックほどにはパフォーマンスに影響を与えません。ただし、ターゲット OS がマルチスレッドをサポートしていない場合は、依然としてラインコールバックを使用しなければならない可能性があります。

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

参照: [Context manager アドオン](./doc_addon_ctxmgr)、[Concurrent scripts サンプル](./doc_samples_concurrent)、[コルーチン](./doc_adv_coroutine)
