---
title: "AngelScript Introduction"
---

![](/images/angelscript-docs-ja/aslogo.png)

<center>Version 2.38.0</center>

[AngelScript](./doc_overview) は、アプリケーションへの組み込みを目的とした、[フリーでオープンソース](./doc_license)の、柔軟かつクロスプラットフォームなスクリプトライブラリです。その目的は、強力でありながら、めったに使われない多数の機能による重さがない、使いやすいライブラリを提供することです。

AngelScript の開発は 2003年2月 に始まり、最も基本的な機能のみを備えた最初の公開リリースは 2003年3月28日に行われました。その日以来、新しい機能や改善を含むリリースが頻繁に行われています。著者は現在も、このライブラリの継続的な改善と成長に専念しています。

ライブラリの公式サイトは <a href="http://www.angelcode.com/angelscript" target="_blank">http://www.angelcode.com/angelscript</a> です。

## 開発者マニュアル (Developer manual)

 - [ライセンス](./doc_license)
 - [はじめに](./doc_start)
 - [AngelScriptの仕組みを理解する](./doc_understanding_as)
 - [アプリケーションインターフェースの登録](./doc_register_api_topic)
 - [スクリプトのコンパイル](./doc_compile_script)
 - [スクリプト関数の呼び出し](./doc_call_script_func)
 - [スクリプトクラスの使用](./doc_use_script_class)
 - [コールバック](./doc_callbacks)
 - [高度なトピック](./doc_advanced)
 - [サンプル](./doc_samples)
 - [アドオン](./doc_addon)

## はじめに (Getting started)

 - [概要](./doc_overview)
 - [ライブラリのコンパイル](./doc_compile_lib)
 - [Hello World](./doc_hello_world)
 - [ベストプラクティス (Good practice)](./doc_good_practice)

## アプリケーションインターフェースの登録 (Registering the application interface)

 - [アプリケーションAPIの登録](./doc_register_api)
 - [関数の登録](./doc_register_func)
 - [プロパティの登録](./doc_register_prop)
 - [型の登録](./doc_register_type)
 - [高度なアプリケーションインターフェース](./doc_advanced_api)

## 高度なアプリケーションインターフェース (Advanced application interface)

 - [文字列 (Strings)](./doc_strings)
 - [配列 (Arrays)](./doc_arrays)
 - [ガベージコレクション対応オブジェクト](./doc_gc_object)
 - [ジェネリック関数 (Generic functions)](./doc_generic)
 - [ジェネリックなハンドル型](./doc_adv_generic_handle)
 - [スコープ付きの型](./doc_adv_scoped_type)
 - [単一参照の型](./doc_adv_single_ref_type)
 - [クラス階層](./doc_adv_class_hierarchy)
 - [可変型 (The variable type)](./doc_adv_var_type)
 - [可変長引数 (Variadic functions)](./doc_adv_variadic)
 - [テンプレート型](./doc_adv_template)
 - [テンプレート関数](./doc_adv_template_func)
 - [弱参照 (Weak references)](./doc_adv_weakref)
 - [C++ 例外](./doc_cpp_exceptions)

## 高度なトピック (Advanced topics)

 - [デバッグ](./doc_debug)
 - [スクリプト実行のタイムアウト](./doc_adv_timeout)
 - [ガベージコレクション](./doc_gc)
 - [マルチスレッド](./doc_adv_multithread)
 - [並行スクリプト (Concurrent scripts)](./doc_adv_concurrent)
 - [コルーチン](./doc_adv_coroutine)
 - [動的なスクリプトモジュールのインポート](./doc_adv_import)
 - [動的なビルド](./doc_adv_dynamic_build)
 - [スクリプトの事前コンパイル](./doc_adv_precompile)
 - [パフォーマンスの微調整](./doc_finetuning)
 - [アクセス制御マスク](./doc_adv_access_mask)
 - [スクリプトの名前空間](./doc_adv_namespace)
 - [動的なエンジン設定](./doc_adv_dynamic_config)
 - [カスタムビルドオプション](./doc_adv_custom_options)
 - [リフレクション](./doc_adv_reflection)
 - [シリアライゼーション](./doc_serialization)
 - [スクリプトクラスからのアプリケーションクラスの継承](./doc_adv_inheritappclass)
 - [JIT コンパイル](./doc_adv_jit_topic)

## JIT コンパイル (JIT compilation)

 - [JITコンパイラの使い方](./doc_adv_jit)
 - [JITコンパイラの仕組み](./doc_adv_jit_1)

## スクリプト言語 (The script language)

これは AngelScript スクリプト言語のリファレンスドキュメントです。

 - [グローバルエンティティ](./doc_script_global)
 - [ステートメント (Statements)](./doc_script_statements)
 - [式 (Expressions)](./doc_expressions)
 - [データ型](./doc_datatypes)
 - [関数](./doc_script_func)
 - [スクリプトクラス](./doc_script_class)
 - [オブジェクトハンドル](./doc_script_handle)
 - [共有エンティティ (Shared entities)](./doc_script_shared)
 - [演算子の優先順位](./doc_operator_precedence)
 - [予約語](./doc_reserved_keywords)
 - [スクリプトのBNF文法](./doc_script_bnf)
 - [組み込みライブラリ](./doc_script_stdlib)

## グローバルエンティティ (Global entities)

すべてのグローバル宣言は同じ名前空間を共有するため、名前に競合があってはなりません。これには、ホストアプリケーションによって登録された拡張データ型や組み込み関数も含まれます。また、すべての宣言はどこからでも可視性があります。例えば、呼び出される関数を、それを呼び出す関数の前に宣言する必要はありません。

 - [関数](./doc_global_func)
 - [変数](./doc_global_variable)
 - [仮想プロパティ](./doc_global_virtprop)
 - [クラス](./doc_global_class)
 - [インターフェース](./doc_global_interface)
 - [ミックスインクラス](./doc_script_mixin)
 - [列挙型 (Enums)](./doc_global_enums)
 - [関数定義 (Funcdefs)](./doc_global_funcdef)
 - [型定義 (Typedefs)](./doc_global_typedef)
 - [名前空間 (Namespaces)](./doc_global_namespace)
 - [インポート (Imports)](./doc_global_import)

## 関数 (Global functions)

[グローバル関数](./doc_script_func) は、何らかの入力を操作し、結果を生成するためのルーチンを実装する手段を提供します。

```cpp
  void foo()
  {
    // 何かを行う
  }
```

## 関数 (Functions)

関数はグローバルに宣言され、引数の型と戻り値が定義されるシグネチャと、実装が定義される本体から構成されます。

- [宣言](./doc_script_func_decl)
- [参照渡しでの引数](./doc_script_func_ref)
- [参照返し](./doc_script_func_retref)
- [関数のオーバーロード](./doc_script_func_overload)
- [デフォルトの引数](./doc_script_func_defarg)
- [無名関数 (Anonymous functions)](./doc_script_anonfunc)

## スクリプトクラス (Script classes)

[スクリプトクラス](./doc_script_class) は通常、値とその値を操作する関数をグループ化するために使用されます。クラスのインスタンスは複数存在することができ、各インスタンスは異なる値を持ちます。

```cpp
  class Foo
  {
    void bar() { value++; }
    int value;
  }
```

## スクリプトクラスの詳細 (Script classes syntax)

スクリプトクラスはグローバルに宣言され、プロパティとメソッドを論理的な単位にグループ化する簡単な方法を提供します。クラスの構文は C++ や Java に似ています。

 - [クラスの概要](./doc_script_class_desc)
 - [コンストラクタ](./doc_script_class_construct)
 - [メンバーの初期化](./doc_script_class_memberinit)
 - [デストラクタ](./doc_script_class_destruct)
 - [メソッド](./doc_script_class_methods)
 - [継承](./doc_script_class_inheritance)
 - [非公開 (Private) クラスメンバー](./doc_script_class_private)
 - [演算子のオーバーロード](./doc_script_class_ops)
 - [プロパティ](./doc_script_class_prop)
