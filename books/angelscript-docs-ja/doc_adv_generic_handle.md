---
title: "ジェネリック・ハンドル型の登録 (Registering a generic handle type)"
---

特定のクラスの実装に依存せず、あらゆるオブジェクトへの参照を保持できる「汎用的なストレージ」や「メッセージングシステム」を提供したい場合があります。

AngelScript には、すべてのオブジェクト型に共通する基底クラス（Common Denominator）は存在しません。その理由は、スクリプト内で定義されたクラスと、アプリケーション側で登録されたクラスは内部的な実装が根本的に異なり、単一のスーパークラスの下に一般化することができないためです。

その解決策として、AngelScript は「ジェネリック・ハンドル型」の登録をサポートしています。この型はアプリケーションの要件に合わせて実装されますが、スクリプトからは任意の参照型を保持できる [汎用ハンドル](./doc_script_handle) であるかのように振る舞います。これにより、オブジェクト、[関数ハンドル](./doc_script_datatypes#関数ハンドル-function-handles)、および [配列](./doc_addon#array-テンプレートオブジェクト) を一律に保持できるようになります。

ジェネリック・ハンドル型の登録は、いくつかの詳細を除き、基本的には [値型](./doc_register_type#値型の登録-registering-a-value-type) の登録手順と同じです。以下にその詳細を説明します。

 - この型は、追加のフラグ `asOBJ_ASHANDLE` を伴って登録されなければなりません。これが AngelScript に対して、この型がジェネリックなハンドルをシミュレートしていることを伝えるフラグです。

 - 任意のハンドルをこの型に代入できるようにするためには、[opHndlAssign](./doc_script_class_ops) メソッドが [可変パラメータ型](./doc_adv_var_type) で登録されなければなりません（例：`ref &opHndlAssign(const ?&in)`）。
 
 - `is` と `!is` の演算子がハンドルの期待通りに動作できるようにするため、[opEquals](./doc_script_class_ops) メソッドも [可変パラメータ型](./doc_adv_var_type) で登録されなければなりません（例：`bool opEquals(const ?&in)`）。
 
 - 最後に、他の任意の型への動的キャストを可能にするため、[opCast](./doc_script_class_ops) を `void opCast(?&out)` というシグネチャで登録しなければなりません。

これが非常に便利な型でありながらカスタマイズの必要性がほとんどないため、この実装を備えた標準アドオンが SDK に同梱されています。

参照: [ref オブジェクト](./doc_addon#ref-オブジェクト)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_generic_handle.html
