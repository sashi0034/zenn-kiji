---
title: "リフレクション (Reflection)"
---

スクリプト言語はリフレクション (reflection) のための組み込み機能を提供していませんが、アプリケーションインターフェースはスクリプト内のすべてのものを列挙するために必要なすべてのメソッドを提供しています。

[デバッグ](./doc_debug) に関する記事で、リフレクションよりデバッグに焦点を当てたこれらのインターフェースの一部を紹介しています。[動的なビルド](./doc_adv_dynamic_build) の記事では、スクリプトが実行時に動的に変更される可能性のある別の側面を示しています。

以下は、スクリプト内のさまざまなエンティティを列挙するために利用可能なメソッドの概要です。

## 変数とプロパティの列挙 (Enumerating variables and properties)

スクリプトモジュール内のグローバル変数は、`asIScriptModule` インターフェースを使用して列挙されます。具体的には、`GetGlobalVarCount` および `GetGlobalVar` メソッドを使用します。`GetGlobalVarIndexByName` および `GetGlobalVarIndexByDecl` は、目的の変数の名前や宣言が事前にわかっている場合に使用できます。グローバル変数の値を検査 (inspect) したり変更したりするには、`GetAddressOfGlobalVar` メソッドを使用すべきです。

エンジンインターフェース `asIScriptEngine` にも、アプリケーションが登録したグローバルプロパティを列挙するための同様のメソッド群があります。つまり、`GetGlobalPropertyCount`、`GetGlobalPropertyByIndex`、`GetGlobalPropertyIndexByName`、および `GetGlobalPropertyIndexByDecl` です。

クラスのメンバープロパティには、生存しているオブジェクトのインスタンスからは `asIScriptObject` インターフェースを通してアクセスされ、生存しているオブジェクトのインスタンスがない状態でのクラス宣言の検査には `asITypeInfo` インターフェースを通してアクセスされます。

関数内のローカル変数も、スクリプトがデバッグ情報付きでコンパイルされていれば列挙することができます。これらは、宣言を検査する場合は `asIScriptFunction` インターフェースを通じて列挙され、スタック上でそれらを検査および/または変更する場合は直接 `asIScriptContext` を通じて列挙されます。

## 関数とメソッドの列挙 (Enumerating functions and methods)

スクリプト内のグローバル関数は、`asIScriptModule` インターフェースを使用して列挙され、`GetFunctionCount`、`GetFunctionByIndex`、`GetFunctionByName`、および `GetFunctionByDecl` の各メソッドを使用します。

エンジンインターフェース `asIScriptEngine` も、同じような方法でアプリケーションが登録した関数を列挙するためのメソッドを公開しています。

クラスのメソッドを列挙するには、`asITypeInfo` インターフェースを使用すべきです。

## 型の列挙 (Enumerating types)

もちろん、`asIScriptModule` はスクリプトに宣言された型を列挙するのにも使われます。`GetObjectTypeCount`、`GetObjectTypeByIndex`、および `GetTypeInfoByName` はクラスとインターフェースを列挙するためのメソッドです。`GetEnumCount` および `GetEnumByIndex` メソッドは列挙型 (enum) を列挙するためのものです。

`asIScriptEngine` インターフェースには、アプリケーションが登録した型を列挙するためのほぼ同一のメソッドがあります。

上記のメソッドの多くは、それぞれの変数、プロパティ、または関数の引数の型を記述する、型ID (type id) と呼ばれる戻り値を返します。多くの場合、型IDは直接ビットフィールドとして検査され、その型が何であるかに関する必要な情報を取得できます。下位ビットは単なるシーケンス番号であり、最初の12個の番号が組み込みのプリミティブ型を表し、それ以上のものはアプリケーションが登録した型またはスクリプトが宣言した型のいずれかを表します。上位ビットは、その型がプリミティブ、オブジェクト、またはハンドルのいずれを表すかを示します。型IDに必要な検証を行うには `asETypeIdFlags` のフラグを使用してください。

オブジェクト型を表す型IDの場合、その型が何であるかのさらに詳しい情報を得るために、`asITypeInfo` インスタンスを取得する必要があるかもしれません。型ID から `asITypeInfo` へ変換するには、`GetTypeInfoById` メソッドが使用されます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_reflection.html
