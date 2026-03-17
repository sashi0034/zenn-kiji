---
title: "登録可能な要素 (What can be registered)"
---

AngelScript では、スクリプト自身以外のものとやり取りするために、アプリケーション開発者がスクリプト用のインターフェースを登録する必要があります。

スクリプトから直接使用できる [グローバル関数](./doc_register_func) や [グローバルプロパティ](./doc_register_prop) を登録することが可能です。

より複雑なスクリプトの場合は、組み込みのデータ型を補完するために [新しいオブジェクト型](./doc_register_type) を登録すると便利です。

C++ における文字列型にはデファクトスタンダードがないため、AngelScript には [組み込みの文字列型](./doc_strings) が存在しません。その代わり、AngelScript ではアプリケーションが好みの文字列型を登録し、スクリプトエンジンが文字列のインスタンス化に使用する [文字列ファクトリ (string factory)](#asIScriptEngine::RegisterStringFactory) を登録できるようになっています。

また、デフォルトの [組み込み配列型](./doc_arrays) もありません。これも多くの開発者が自分自身のバージョンを持ちたいと考える要素だからです。配列型は [テンプレート](./doc_adv_template) として登録されたのち、[デフォルトの配列型](#asIScriptEngine::RegisterDefaultArrayType) として設定されます。独自の配列型を実装したくない開発者のために、標準の [配列アドオン](./doc_addon_array) が提供されています。

スクリプトクラスが特定のクラスメソッドのセットを実装することを保証したい場合は、[クラスインターフェース (Class interfaces)](#asIScriptEngine::RegisterInterface) を登録できます。アプリケーションからスクリプトクラスを扱う際にインターフェースは便利ですが、インターフェースなしでもアプリケーション側から利用可能なメソッドとプロパティを簡単に列挙できるため、必須ではありません。

コールバックルーチンの実装など、スクリプトからアプリケーションへ関数ポインタを渡すことを許可したい場合は、[関数定義 (Function definitions)](#asIScriptEngine::RegisterFuncdef) を登録できます。

スクリプトの可読性を向上させるために、[列挙型 (Enumeration types)](#asIScriptEngine::RegisterEnum) や [型定義 (typedefs)](#asIScriptEngine::RegisterTypedef) を登録することも可能です。
