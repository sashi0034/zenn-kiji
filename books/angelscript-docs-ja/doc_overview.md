---
title: "🔰 概要 (Overview)"
---

AngelScript は、アプリケーションがスクリプトに公開する[関数](./doc_register_func)、[プロパティ](./doc_register_prop)、さらには[型](./doc_register_type)を[登録](./doc_register_api)するためのエンジンを中心に構成されています。スクリプトは[モジュール (modules)](./doc_module) 単位にコンパイルされ、アプリケーションの用途に応じて 1 つ以上のモジュールを保持できます。また、[アクセスマスク (access profiles)](./doc_adv_access_mask) を使用することで、モジュールごとに異なるインターフェースを公開することも可能です。これは、GUI 制御用や AI 制御用など、役割の異なるスクリプトを共存させる場合に非常に有効です。

スクリプトはバイトコードにコンパイルされ、AngelScript はそのバイトコードを[実行](./doc_call_script_func)するための仮想マシンである「スクリプトコンテキスト (script context)」を提供します。アプリケーションは同時に任意の数のコンテキストを持つことができますが、多くの場合は 1 つで十分でしょう。コンテキストは実行の「中断（Suspend）」と「再開（Resume）」をサポートしているため、[並行実行 (concurrent scripts)](./doc_adv_concurrent) や[コルーチン (co-routines)](./doc_adv_coroutine) といった機能を容易に実装できます。また、スクリプトコンテキストは実行時の詳細な情報を抽出するインターフェースも備えており、スクリプトの[デバッグ](./doc_debug)に役立ちます。

[スクリプト言語](./doc_main#スクリプト言語-(script-language))の文法は、C++ をはじめ Java、C#、D といったモダンな言語の構文に基づいています。これらの言語や、JavaScript・ActionScript のような類似の構文を持つ言語の経験があれば、AngelScript にはすぐに馴染めるはずです。大半のスクリプト言語とは異なり、AngelScript は強力な「静的型付け」を採用しています。これにより実行時の型評価コストが抑えられ、高速な実行とホストアプリケーションとのスムーズな連携を実現しています。

AngelScript の[メモリ管理](./doc_memory)は参照カウント方式に基づいています。これに加えて、循環参照を検出し段階的に解放するための[ガベージコレクター (garbage collector)](./doc_gc)も搭載しています。これにより、GC 動作によるアプリケーションの一時的なフリーズ（停止）を防ぎつつ、制御された安全なメモリ管理環境を提供します。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_overview.html
