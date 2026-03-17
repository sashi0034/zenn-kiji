---
title: "概要 (Overview)"
---

AngelScript は、アプリケーションがスクリプトから利用可能にするための [関数](./doc_register_func)、[プロパティ](./doc_register_prop)、そして [型](./doc_register_type) を [登録](./doc_register_api) するための [エンジン (engine)](#asIScriptEngine) を中心に構成されています。その後、スクリプトは [モジュール (modules)](./doc_module) にコンパイルされます。アプリケーションは必要に応じて1つ以上のモジュールを持つことができます。また、アプリケーションは [アクセスプロファイル (access profiles)](./doc_adv_access_mask) を使用して、各モジュールに対して異なるインターフェースを公開することも可能です。これは、アプリケーションが GUI や AI 制御など、複数の種類のスクリプトを扱う場合に特に有用です。

スクリプトはバイトコードにコンパイルされるため、AngelScript はバイトコードを [実行](./doc_call_script_func) するための仮想マシンを提供します。これは [スクリプトコンテキスト (script context)](#asIScriptContext) とも呼ばれます。アプリケーションは同時に任意の数のスクリプトコンテキストを持つことができますが、ほとんどのアプリケーションではおそらく1つだけで十分です。コンテキストは実行の [一時停止](#asIScriptContext::Suspend) と再開をサポートしているため、アプリケーションは [並行スクリプト (concurrent scripts)](./doc_adv_concurrent) や [コルーチン (co-routines)](./doc_adv_coroutine) のような機能を簡単に実装することができます。スクリプトコンテキストは、スクリプトの [デバッグ](./doc_debug) に役立つランタイム情報を抽出するためのインターフェースも提供します。

[スクリプト言語](./doc_script) は、C++ や、Java、C#、D といったよりモダンな言語のよく知られた構文に基づいています。これらの言語、あるいは Javascript や ActionScript のような似た構文を持つ他のスクリプト言語の知識がある人なら、AngelScript にすぐに馴染むことができるでしょう。大半のスクリプト言語とは対照的に、AngelScript は強い型付け（静的型付け）の言語です。これにより、実行時の型評価のオーバーヘッドが減少し、コードの高速な実行とホストアプリケーションとの橋渡しのオーバーヘッドが少ないという特徴があります。

AngelScript の [メモリ管理](./doc_memory) は、参照カウントに基づいています。さらに、循環参照を含むオブジェクトを検出しプログレッシブに解放するための [ガベージコレクター (garbage collector)](./doc_gc) も備わっています。これにより、ガベージコレクターがメモリ解放を行う際にもアプリケーションのフリーズが発生せず、制御された環境が提供されます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_overview.html
