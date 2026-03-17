---
title: "シリアライゼーション (Serialization)"
---

スクリプトをシリアライズ (保存/直列化) するためには、アプリケーションはスクリプトに関連するすべての変数とオブジェクトをイテレート (反復/巡回) し、後で復元できるようにそれらのコンテンツを保存できなければなりません。単純な値についてはこれは簡単ですが、オブジェクトやハンドルにおいては、オブジェクト間の参照や、スクリプトで定義されたクラスおよびアプリケーションで登録された型の内部構造を追跡する必要があるため、より複雑になります。

変数とオブジェクトメンバーのイテレートについては [リフレクション (reflection)](./doc_adv_reflection) に関する記事ですでに説明されているため、この記事では値の保存と復元に焦点を当てます。

シリアライゼーションの実装例としては、[Serializer アドオン](./doc_addon_serializer) のソースコードを参照してください。

参照: [ホットリロードスクリプト](./doc_adv_dynamic_build_hot)

## モジュールのシリアライゼーション (Serialization of modules)

スクリプトモジュールをシリアライズするには、すべてのグローバル変数を列挙し、[それぞれをシリアライズ](./doc_serialization_vars) する必要があります。

モジュールをデシリアライズ (復元/逆直列化) する時は、[ソーススクリプト](./doc_compile_script) から、または [事前コンパイル済みバイトコードのロード](./doc_adv_precompile) によって通常通りコンパイルを行いますが、その前に [エンジンプロパティ asEP_INIT_GLOBAL_VARS_AFTER_BUILD をオフにする](#asIScriptEngine::SetEngineProperty) ことでグローバル変数の初期化をオフにしておく必要があります。

## グローバル変数のシリアライゼーション (Serialization of global variables)

グローバル変数をシリアライズするには、その変数のキーとして使用するための名前と名前空間が必要で、次にその変数の型 ID とアドレスが必要になります。これらは [asIScriptModule::GetGlobalVar](#asIScriptModule::GetGlobalVar) と [asIScriptModule::GetAddressOfGlobalVar](#asIScriptModule::GetAddressOfGlobalVar) メソッドで取得できます。もし型 ID がプリミティブ型のものなら、値はそのまま保存できます。もしそれがハンドルや参照の場合は、参照自体とそれが指す対象のオブジェクトをシリアライズする必要があります。もし型 ID がオブジェクト型の場合、[オブジェクトをシリアライズ](./doc_serialization_objects) してそのコンテンツを保存します。

グローバル変数をデシリアライズするには、名前と名前空間を使用してそれを検索し、次に `GetAddressOfGlobalVar` を使用して、シリアライズされたコンテンツで復元する必要があるメモリのアドレスを取得します。

## オブジェクトのシリアライゼーション (Serialization of objects)

スクリプトオブジェクトをシリアライズするには、[asIScriptObject](#asIScriptObject) インターフェースを使用してメンバーをイテレートし、コンテンツを保存します。オブジェクトは他のオブジェクトへの参照や、時には自分自身への参照を保持する可能性があることを忘れないでください。そのため、すでにシリアライズされたオブジェクトインスタンスを追跡し、同じオブジェクトが再び現れた場合には単に参照を保存することが重要です。

スクリプトオブジェクトをデシリアライズする際は、コンストラクタが実行されないように [asIScriptEngine::CreateUninitializedScriptObject](#asIScriptEngine::CreateUninitializedScriptObject) を使用して最初にメモリを割り当て、その後メンバーをイテレートしてコンテンツを復元すべきです。

アプリケーションで登録された型については、スクリプトエンジンはその型の完全なコンテンツを知らず、それゆえにシリアライゼーションのためのインターフェースを提供できないため、あなた自身の実装を提供する必要があります。

## コンテキストのシリアライゼーション (Serialization of contexts)

スクリプトコンテキストのシリアライゼーションには、すべての関数呼び出し、ローカル変数、レジスタなどを含む完全なコールスタックの保存が含まれます。これを行うには [asIScriptContext](#asIScriptContext) インターフェースを使用します。

 - コールスタックのサイズを取得するには [GetCallstackSize](#asIScriptContext::GetCallstackSize) を使用します
 - コールスタックの各エントリについて、以下を行います：
   - レジスタ（プログラムポインタ、スタックポインタなど）を保存するために [GetCallStateRegisters](#asIScriptContext::GetCallStateRegisters) を使用します
   - 名前のない一時変数を含むすべてのローカル変数を保存するために [GetVarCount](#asIScriptContext::GetVarCount)、[GetVar](#asIScriptContext::GetVar)、および [GetAddressOfVar](#asIScriptContext::GetAddressOfVar) を使用します
   - その後の関数呼び出しのためにスタックにプッシュされた値を保存するために [GetArgsOnStackCount](#asIScriptContext::GetArgsOnStackCount) と [GetArgOnStack](#asIScriptContext::GetArgOnStack) を使用します
 - 追加のコンテキストレジスタを保存するために [GetStateRegisters](#asIScriptContext::GetStateRegisters) を使用します
 
コンテキストをデシリアライズするには、以下の手順に従います：

 - デシリアライゼーションが実行されることをコンテキストに伝えるために [StartDeserialization](#asIScriptContext::StartDeserialization) を呼び出します
 - 事前に保存されたコールスタックの各エントリについて、以下を行います：
   - コールスタック・エントリのための領域を予約するために [PushFunction](#asIScriptContext::PushFunction) を呼び出します
   - レジスタを復元するために [SetCallStateRegisters](#asIScriptContext::SetCallStateRegisters) を呼び出します
   - すべてのローカル変数を復元するために [GetVar](#asIScriptContext::GetVar) と [GetAddressOfVar](#asIScriptContext::GetAddressOfVar) を使用します
   - スタックにプッシュされた値を復元するために [GetArgOnStack](#asIScriptContext::GetArgOnStack) を使用します
 - 追加のコンテキストレジスタを復元するために [SetStateRegisters](#asIScriptContext::SetStateRegisters) を呼び出します
 - シリアライゼーションを完了させ、実行の再開を許可するために [FinishDeserialization](#asIScriptContext::FinishDeserialization) を呼び出します

### 制限事項 (Limitations)

以下は、コンテキストのシリアライゼーションに関するいくつかの制限事項です：

 - シリアライゼーションはプラットフォーム依存です。つまり、32ビットプラットフォームでコンテキストをシリアライズし、それを64ビットプラットフォームでデシリアライズすることはできません。逆もまた同様です
 - 変更されたスクリプトの [ホットリロード](./doc_adv_dynamic_build_hot) 後にコンテキストをデシリアライズしようとすると動作が未定義となり、ほぼ確実にクラッシュを引き起こします
