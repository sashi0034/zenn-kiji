[AGENTS.md]


---

[doc_addon.md]

## アプリケーションモジュール
## スクリプト拡張
## スクリプトビルダー
### C++-パブリックインターフェース
#### インクルードコールバックのシグネチャ
#### pragma-コールバックのシグネチャ
### インクルードディレクティブ
### 条件付きコンパイル
### スクリプト内のメタデータ
## コンテキストマネージャー
### C++-パブリックインターフェース
## デバッガー
### C++-パブリックインターフェース
### 使用例
## シリアライザー
### C++-パブリックインターフェース
### 使用例
## ヘルパー関数
### C++-パブリックインターフェース
## 自動ラッパー関数
### 使用例
## 例外ルーティン
### C++-パブリックインターフェース
## string-オブジェクト
## array-テンプレートオブジェクト
### C++-パブリックインターフェース
### C++-での使用例
## grid-テンプレートオブジェクト
### C++-パブリックインターフェース
### スクリプトインターフェース
### スクリプトでの使用例
## any-オブジェクト
### C++-パブリックインターフェース
### スクリプトインターフェース
### スクリプトでの使用例
## ref-オブジェクト
### C++-パブリックインターフェース
### C++-からの使用例
## weakref-オブジェクト
### C++-パブリックインターフェース
## dictionary-オブジェクト
### C++-パブリックインターフェース
### C++-での使用例
## file-オブジェクト
### C++-パブリックインターフェース
## filesystem-オブジェクト
### C++-パブリックインターフェース
## math-関数
### スクリプトインターフェース
### complex-型
## datetime-オブジェクト
### C++-パブリックインターフェース
## socket-オブジェクト
### C++-パブリックインターフェース

---

[doc_adv_access_mask.md]


---

[doc_adv_class_hierarchy.md]

## 関係の確立-(Establishing-the-relationship)

---

[doc_adv_concurrent.md]


---

[doc_adv_coroutine.md]


---

[doc_adv_custom_options.md]

## 登録可能な型-(Registerable-types)
## 言語の変更-(Language-modifications)
#### asEP_DISALLOW_EMPTY_LIST_ELEMENTS
#### asEP_DISALLOW_VALUE_ASSIGN_FOR_REF_TYPE
#### asEP_ALLOW_UNSAFE_REFERENCES
#### asEP_USE_CHARACTER_LITERALS,-asEP_ALLOW_MULTILINE_STRINGS,-asEP_SCRIPT_SCANNER,-asEP_STRING_ENCODING
#### asEP_HEREDOC_TRIM_MODE
#### asEP_ALLOW_IMPLICIT_HANDLE_TYPES
#### asEP_REQUIRE_ENUM_SCOPE
#### asEP_PROPERTY_ACCESSOR_MODE
#### asEP_DISALLOW_GLOBAL_VARS
#### asEP_ALWAYS_IMPL_DEFAULT_CONSTRUCT
#### asEP_ALWAYS_IMPL_DEFAULT_COPY_CONSTRUCT
#### asEP_ALWAYS_IMPL_DEFAULT_COPY
#### asEP_ALTER_SYNTAX_NAMED_ARGS
#### asEP_DISABLE_INTEGER_DIVISION
#### asEP_PRIVATE_PROP_AS_PROTECTED
#### asEP_ALLOW_UNICODE_IDENTIFIERS
#### asEP_IGNORE_DUPLICATE_SHARED_INTF
#### asEP_BOOL_CONVERSION_MODE
#### asEP_FOREACH_SUPPORT
#### asEP_MEMBER_INIT_MODE
## エンジンの動作-(Engine-behaviours)
#### asEP_MAX_NESTED_CALLS
#### asEP_OPTIMIZE_BYTECODE
#### asEP_COPY_SCRIPT_SECTIONS
#### asEP_MAX_STACK_SIZE,-asEP_INIT_STACK_SIZE,-asEP_MAX_CALL_STACK_SIZE,-asEP_INIT_CALL_STACK_SIZE
#### asEP_BUILD_WITHOUT_LINE_CUES
#### asEP_INIT_GLOBAL_VARS_AFTER_BUILD
#### asEP_INCLUDE_JIT_INSTRUCTIONS
#### asEP_EXPAND_DEF_ARRAY_TO_TMPL
#### asEP_AUTO_GARBAGE_COLLECT
#### asEP_DISABLE_SCRIPT_CLASS_GC
#### asEP_COMPILER_WARNINGS
#### asEP_GENERIC_CALL_MODE
#### asEP_NO_DEBUG_OUTPUT

---

[doc_adv_dynamic_build.md]

## オンデマンドビルド-(On-demand-builds)
## インクリメンタルビルド-(Incremental-builds)
## スクリプトのホットリロード-(Hot-reloading-scripts)
### 考慮すべきこと-(Things-to-consider)

---

[doc_adv_dynamic_config.md]


---

[doc_adv_generic_handle.md]


---

[doc_adv_import.md]


---

[doc_adv_inheritappclass.md]


---

[doc_adv_jit.md]

## JIT-インターフェース-バージョン-1-(The-JIT-interface-version-1)
## JIT-インターフェース-バージョン-2-(The-JIT-interface-version-2)
## バイトコードのトラバース-(Traversing-the-byte-code)

---

[doc_adv_multithread.md]

## マルチスレッド環境で考慮すべきこと-(Things-to-think-about-with-a-multithreaded-environment)
## ファイバー-(Fibers)

---

[doc_adv_namespace.md]

## 名前空間を用いたインターフェースの登録-(Registering-the-interface-with-namespaces)
## 名前空間内のエンティティの検索-(Finding-entities-in-namespaces)

---

[doc_adv_precompile.md]

## 覚えておくべきこと-(Things-to-remember)

---

[doc_adv_reflection.md]

## 変数とプロパティの列挙-(Enumerating-variables-and-properties)
## 関数とメソッドの列挙-(Enumerating-functions-and-methods)
## 型の列挙-(Enumerating-types)

---

[doc_adv_scoped_type.md]


---

[doc_adv_single_ref_type.md]


---

[doc_adv_template.md]

#### テンプレートインスタンスのサブタイプ置換について-(On-subtype-replacement-for-template-instances)
### テンプレートの子関数定義-(Child-funcdefs-of-templates)
### コンパイル時のテンプレートインスタンス化の検証-(Validating-template-instantiations-at-compile-time)
## テンプレート関数-(Template-functions)

---

[doc_adv_timeout.md]

## ラインコールバックを利用する-(With-the-line-callback)
## サブスレッドを使用する-(With-a-secondary-thread)

---

[doc_adv_var_type.md]

### 可変型の変換演算子-(Variable-conversion-operators)
## 可変長引数-(Variadic-arguments)

---

[doc_adv_weakref.md]


---

[doc_arrays.md]


---

[doc_as_vs_cpp_types.md]

## プリミティブ型-(Primitives)
## 文字列-(Strings)
## 配列-(Arrays)
## スクリプトクラスとインターフェース-(Script-classes-and-interfaces)
## 関数ポインタ-(Function-pointers)

---

[doc_call_script_func.md]

## コンテキストの準備と関数の実行-(Preparing-context-and-executing-the-function)
## プリミティブ型の引数渡しと戻り値の受け取り-(Passing-and-returning-primitives)
## オブジェクトの引数渡しと戻り値の受け取り-(Passing-and-returning-objects)
## 例外処理-(Exception-handling)

---

[doc_callbacks.md]

## 実装例-(An-example)
## デリゲート-(Delegates)

---

[doc_compile_lib.md]

## コンパイル時のオプションの設定-(Set-compile-time-options)
## ライブラリとのリンク-(Linking-with-the-library)
### 1.-プロジェクトにライブラリのソースファイルを含める-(Include-library-source-files-in-project)
### 2.-スタティックライブラリをコンパイルしてプロジェクトにリンクする-(Compile-a-static-library-and-link-into-project)
### 3.-インポートライブラリとともに動的ロードライブラリをコンパイルする-(Compile-a-dynamically-loaded-library-with-an-import-library)
## 特定のプラットフォームに関する考慮事項-(Considerations-for-specific-platforms)
### Windows-64bit
### Microsoft-Visual-C++
### Pocket-PC-with-ARM-CPU
### Marmalade
## ライブラリのサイズ-(Size-of-the-library)

---

[doc_compile_script.md]

## メッセージコールバック-(Message-callback)
## スクリプトのロードとコンパイル-(Loading-and-compiling-scripts)

---

[doc_cpp_exceptions.md]

## longjmp

---

[doc_debug.md]

## ラインブレークポイントの設定-(Setting-line-breaks)
## 変数の検査-(Inspecting-variables)
## 内部的に実行されたスクリプトのデバッグ-(Debugging-internally-executed-scripts)

---

[doc_finetuning.md]

## 関数と型のキャッシュ-(Cache-the-functions-and-types)
## コンテキストオブジェクトの再利用-(Reuse-the-context-object)
### コンテキストプール-(Context-pool)
### ネストされた呼び出し-(Nested-calls)
## ラインキュー無しのスクリプトコンパイル-(Compile-scripts-without-line-cues)
## スレッドセーフの無効化-(Disable-thread-safety)
## 自動ガベージコレクションの無効化-(Turn-off-automatic-garbage-collection)
## ネイティブ呼び出し規約とジェネリック呼び出し規約の比較-(Compare-native-calling-convention-versus-generic-calling-convention)

---

[doc_gc.md]

## 検出された循環参照用のコールバック-(Callback-for-detected-circular-references)
## ガベージコレクションとマルチスレッド-(Garbage-collection-and-multi-threading)

---

[doc_gc_object.md]

## ガベージコレクション用のファクトリ-(Factory-for-garbage-collection)
## ガベージコレクションに合わせた-Addref-と-Release-(Addref-and-release-for-garbage-collection)
## 値型における-GC-の振る舞い-(GC-behaviours-for-value-types)
## ガベージコレクション対応オブジェクトとマルチスレッド-(Garbage-collected-objects-and-multi-threading)

---

[doc_generic.md]

## 関数の引数の抽出-(Extracting-function-arguments)

---

[doc_good_practice.md]

## 登録時の戻り値を必ず確認する-(Always-check-return-values-for-registrations)
## 詳細なエラーメッセージを受け取るためにメッセージコールバックを使用する-(Use-the-message-callback-to-receive-detailed-error-messages)
## スクリプト関数の実行後は必ず戻り値を検証する-(Always-verify-return-value-after-executing-script-function)

---

[doc_hello_world.md]

## ヘルパー関数-(Helper-functions)

---

[doc_license.md]

# ライセンス-(License)
## AngelCode-Scripting-Library

---

[doc_main.md]

## 開発者マニュアル
## はじめに-(Getting-started)
## アプリケーションインターフェースの登録
### 高度なアプリケーションインターフェース
## 高度なトピック
## スクリプト言語-(The-script-language)

---

[doc_memory.md]

## メモリ管理の概要-(Overview-of-the-memory-management)
## 参照カウントのアルゴリズム-(Reference-counting-algorithm)
## ガベージコレクターのアルゴリズム-(Garbage-collector-algorithm)
## メモリヒープ-(Memory-heap)

---

[doc_module.md]

## シングルモジュールと複数モジュール-(Single-module-versus-multiple-modules)
## モジュール間の情報交換-(Exchanging-information-between-modules)

---

[doc_obj_handle.md]

## 関数内での参照カウンターの管理-(Managing-the-reference-counter-in-functions)
## 自動ハンドルによる管理の簡略化-(Auto-handles-can-make-it-easier)

---

[doc_overview.md]


---

[doc_register_api.md]


---

[doc_register_func.md]

## アプリケーション関数またはメソッドのアドレスを取得する方法-(How-to-get-the-address-of-the-application-function-or-method)
## 呼び出し規約-(Calling-convention)
## 型の違いについて少し-(A-little-on-type-differences)
## 仮想継承はサポートされていません-(Virtual-inheritance-is-not-supported)

---

[doc_register_prop.md]


---

[doc_register_type.md]

## 参照型の登録-(Registering-a-reference-type)
### ファクトリ関数-(Factory-function)
#### 補助オブジェクト-(Auxiliary-object)-を使用したファクトリ関数
#### リストファクトリ関数-(List-factory-function)
### Addref-および-Release-の振る舞い
### 参照カウントを行わない参照型-(Reference-types-without-reference-counting)
### インスタンス化できない参照型の登録-(Registering-an-uninstantiable-reference-type)
## 値型の登録-(Registering-a-value-type)
### コンストラクタとデストラクタ-(Constructor-and-destructor)
### リストコンストラクタ-(List-constructor)
### 値型とネイティブ呼び出し規約-(Value-types-and-native-calling-conventions)
### C++11-未満のコンパイラを使用する場合
## 演算子の振る舞いの登録-(Registering-operator-behaviours)
### 演算子のオーバーロード-(Operator-overloads)
## オブジェクトメソッドの登録-(Registering-object-methods)
### コンポジットメンバ-(Composite-members)
## オブジェクトプロパティの登録-(Registering-object-properties)
### コンポジットメンバ-(Composite-members)
### プロパティアクセサ-(Property-accessors)

---

[doc_samples.md]

## Tutorial（チュートリアル）
## Concurrent-scripts（並行スクリプト）
## Console（コンソール）
## Co-routines（コルーティン）
## Events（イベント）
## Include-directive（インクルードディレクティブ）
## Generic-compiler（汎用コンパイラ）
## Command-line-runner（コマンドラインランナー）
### asrun-の使い方-(Usage)
### スクリプト-(Scripts)
### スクリプトのデバッグ方法-(How-to-debug-scripts)
## Game（ゲーム）

---

[doc_script_bnf.md]


---

[doc_script_class.md]

## クラスの概要-(Script-class-overview)
## コンストラクタ-(Class-constructors)
### 自動生成されるコンストラクタ-(Auto-generated-constructors)
## デストラクタ-(Class-destructor)
## クラスのメソッド-(Class-methods)
### const-メソッド-(Const-methods)
## 継承とポリモーフィズム-(Inheritance-and-polymorphism)
### final,-abstract,-override
## プロテクトとプライベートなクラスメンバー-(Protected-and-private-class-members)
## クラスメンバーの初期化-(Initialization-of-class-members)

---

[doc_script_class_ops.md]

## 前置単項演算子-(Prefixed-unary-operators)
## 後置単項演算子-(Postfixed-unary-operators)
## 比較演算子-(Comparison-operators)
## 代入演算子-(Assignment-operators)
### 自動生成される代入演算子
## 二項演算子-(Binary-operators)
## インデックス演算子-(Index-operators)
## 関数呼び出し演算子-(Functor-operator)
## 型変換演算子-(Type-conversion-operators)
## foreach-ループ演算子-(Foreach-loop-operators)

---

[doc_script_class_prop.md]

## インデックス付きプロパティアクセサー-(Indexed-property-accessors)

---

[doc_script_datatypes.md]

## プリミティブ型-(Primitives)
### void
### bool
### 整数型-(Integer-numbers)
### 実数型-(Real-numbers)
## オブジェクトとハンドル-(Objects-and-handles)
### オブジェクト-(Objects)
### オブジェクトハンドル-(Object-handles)
## 関数ハンドル-(Function-handles)
### デリゲート-(Delegates)
## 文字列-(Strings)
## 自動型宣言-(Auto-declarations)

---

[doc_script_expr.md]

## 代入-(Assignments)
## 関数呼び出し-(Function-call)
## 算術演算子-(Math-operators)
## ビット演算子-(Bitwise-operators)
## 複合代入-(Compound-assignments)
## 論理演算子-(Logic-operators)
## 等値比較演算子-(Equality-comparison-operators)
## 関係比較演算子-(Relational-comparison-operators)
## 同一性比較演算子-(Identity-comparison-operators)
## インクリメント演算子-(Increment-operators)
## インデックス演算子-(Indexing-operator)
## 条件式-(Conditional-expression)
## メンバーアクセス-(Member-access)
## ハンドル-(Handle-of)
## 括弧-(Parenthesis)
## スコープ解決-(Scope-resolution)
## 型変換-(Type-conversions)
## 匿名オブジェクト-(Anonymous-objects)

---

[doc_script_function.md]

## グローバル関数の宣言
## パラメータの参照-(Parameter-references)
## 参照の返却-(Return-references)
## 関数オーバーロード-(Function-overloading)
## デフォルト引数-(Default-arguments)
## 無名関数-(Anonymous-functions)

---

[doc_script_global.md]

## グローバル変数-(Variables)
## 仮想プロパティ-(Virtual-properties)
## インターフェース-(Interfaces)
## インポート-(Imports)
## 列挙型-(Enums)
## typedef-(型定義)
## funcdef-(関数定義)
## 名前空間-(Namespaces)
### using-namespace

---

[doc_script_handle.md]

## 基本的な使用法-(General-usage)
## オブジェクトのライフタイム-(Object-life-times)
## オブジェクトの関係とポリモーフィズム-(Object-relations-and-polymorphing)
## const-ハンドル-(Const-handles)

---

[doc_script_mixin.md]


---

[doc_script_precedence.md]

## 単項演算子-(Unary-operators)
## 二項・三項演算子-(Binary-and-ternary-operators)

---

[doc_script_reserved.md]


---

[doc_script_shared.md]

## 共有エンティティの宣言方法-(How-to-declare-shared-entities)
## 外部共有エンティティ-(External-shared-entities)
## 共有できるもの-(What-can-be-shared)

---

[doc_script_statement.md]

## 変数宣言-(Variable-declarations)
## 式ステートメント-(Expression-statement)
## 条件分岐-(Conditions:-if-/-if-else-/-switch-case)
## ループ-(Loops:-while-/-do-while-/-for-/-foreach)
## ループ制御-(Loop-control:-break-/-continue)
## return-ステートメント-(Return-statement)
## ステートメントブロック-(Statement-blocks)
## try-catch-ブロック-(Try-catch-blocks)
## using-namespace-ステートメント-(Using-namespace)

---

[doc_script_stdlib.md]

## socket
### socket-のメソッド
## 例外処理-(Exception-handling)
## array-（配列）
### array-の演算子
### array-のメソッド
## dictionary-（辞書）
### dictionary-のメソッド
## string-（文字列）
### string-の演算子
### string-のメソッド
### string-のグローバル関数
## ref-（汎用ハンドル）
## weakref-（弱参照）
### weakref-のメソッド
## datetime-（日時）
### datetime-のコンストラクタ
### datetime-のメソッドとプロパティ
## file-（ファイル）
### file-のメソッド
## filesystem-（ファイルシステム）
### filesystem-のメソッド
## コルーチン-(Co-routines)
## システム関数-(System-functions)

---

[doc_serialization.md]

## モジュールのシリアライゼーション
## グローバル変数のシリアライゼーション-(Serialization-of-global-variables)
## オブジェクトのシリアライゼーション-(Serialization-of-objects)
## コンテキストのシリアライゼーション-(Serialization-of-contexts)
### 制限事項

---

[doc_strings.md]

## カスタム文字列型の登録-(Registering-the-custom-string-type)
## Unicode-vs-ASCII
## 文字リテラル

---

[doc_understanding_as.md]

## typeid-の構造
## 呼び出し規約

---

[doc_using_script_class.md]

## スクリプトクラスのインスタンス化
## スクリプトクラスのメソッドの呼び出し
## スクリプトクラスの受け取り-(Receiving-script-classes)
## スクリプトクラスの返却-(Returning-script-classes)

---

[doc_versions.md]

## 歴史-(History)
### 2003年---誕生と最初の公開リリース
### 2005年---バージョン-2、サンドボックス、オブジェクトハンドル、スクリプトクラス、およびガベージコレクション
### 2006年---スクリプトインターフェース
### 2009年---継承、テンプレート型、演算子オーバーロード、および-JIT-コンパイル
### 2010年---関数ポインタ
### 2011年---自動ガベージコレクションとデバッグ
### 2012年---名前空間とミキシン
### 2013年---改良されたテンプレート型、デリゲート、弱参照、および初期化リスト
### 2014年---名前付き引数と-auto
### 2015年---匿名関数
### 2016年---子-funcdef
### 2017年---external-キーワードと匿名初期化リスト
### 2018年---try-catch-ステートメントと明示的コンストラクタ
### 2019年---明示的プロパティキーワード
### 2022年---コンテキストスタックのシリアライゼーション
### 2024年---改良された-JIT-コンパイラインターフェースと自動生成されたコピーコンストラクタ
### 2025年---foreach、可変長引数、およびテンプレート関数

---

