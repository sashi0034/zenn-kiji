---
title: "リフレクション (Reflection)"
---

スクリプト言語自体には、実行中に自身の構造を調べる「リフレクション (Reflection)」の組み込み機能はありませんが、アプリケーションインターフェース (C++ API) にはスクリプト内のあらゆる要素を列挙するためのメソッドが完備されています。

[デバッグ](./doc_debug) の記事では、これらのインターフェースの一部をデバッグの観点から紹介しています。また、[動的なビルド](./doc_adv_dynamic_build) では、実行時にスクリプトを部分的に変更する側面について説明しています。

以下に、スクリプト内の様々なエンティティを列挙するために利用可能なメソッドの概要を示します。

## 変数とプロパティの列挙 (Enumerating variables and properties)

スクリプトモジュール内のグローバル変数は、`asIScriptModule` インターフェースを使用して列挙します。具体的には、`GetGlobalVarCount` および `GetGlobalVar` メソッドを使用します。対象の変数名や宣言が既知である場合は、`GetGlobalVarIndexByName` や `GetGlobalVarIndexByDecl` を使用してインデックスを取得できます。グローバル変数の値を検査・変更するには、`GetAddressOfGlobalVar` メソッドを使用してそのアドレスを取得します。

エンジンインターフェース `asIScriptEngine` にも、アプリケーション側で登録されたグローバルプロパティを列挙するための同様のメソッド群（`GetGlobalPropertyCount`、`GetGlobalPropertyByIndex`、`GetGlobalPropertyIndexByName`、`GetGlobalPropertyIndexByDecl`）が用意されています。

クラスのメンバープロパティには、生存しているオブジェクトインスタンスがある場合は `asIScriptObject` インターフェースを通してアクセスし、インスタンスがない状態でクラス宣言を検査する場合は `asITypeInfo` インターフェースを通してアクセスします。

関数内のローカル変数も、スクリプトがデバッグ情報付きでコンパイルされていれば列挙可能です。これらは、宣言を検査する場合は `asIScriptFunction` インターフェースを、スタック上の値を検査・変更する場合は `asIScriptContext` インターフェースを直接使用します。

## 関数とメソッドの列挙 (Enumerating functions and methods)

スクリプト内のグローバル関数は、`asIScriptModule` インターフェースの `GetFunctionCount`、`GetFunctionByIndex`、`GetFunctionByName`、および `GetFunctionByDecl` メソッドを使用して列挙できます。

エンジンインターフェース `asIScriptEngine` も、アプリケーションが登録した関数を列挙するための同様のメソッドを公開しています。

クラスのメソッドを列挙するには、`asITypeInfo` インターフェースを使用します。

## 型の列挙 (Enumerating types)

`asIScriptModule` は、スクリプト内で宣言された型を列挙するためにも使用されます。`GetObjectTypeCount`、`GetObjectTypeByIndex`、および `GetTypeInfoByName` はクラスやインターフェースを列挙するためのメソッドです。列挙型 (enum) を列挙するには、`GetEnumCount` および `GetEnumByIndex` を使用します。

`asIScriptEngine` インターフェースにも、アプリケーション側で登録された型を列挙するためのほぼ同一のメソッド群が用意されています。

上記のメソッドの多くは、各変数、プロパティ、または関数の引数の型を記述する **型 ID (Type ID)** を返します。多くの場合、型 ID はビットフィールドとして直接検査でき、その型に関する基本的な情報を取得できます。下位ビットはシーケンス番号であり、最初の 12 個は組み込みのプリミティブ型を表し、それ以上の番号はアプリケーション登録型またはスクリプト宣言型を表します。上位ビットは、その型がプリミティブ、オブジェクト、またはハンドルのいずれであるかを示します。型 ID の詳細な検証には、`asETypeIdFlags` のフラグを使用してください。

オブジェクト型を表す型 ID の場合、その型の詳細を知るために `asITypeInfo` インスタンスを取得する必要があります。型 ID から `asITypeInfo` を取得するには、`asIScriptEngine::GetTypeInfoById` メソッドを使用します。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_reflection.html
