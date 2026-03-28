---
title: "関数のインポート (Import functions)"
---

[関数のインポート](./doc_script_global#インポート-imports) は、スクリプトモジュール間でコードを [共有](./doc_script_shared) するための手法の一つです。ただし、`shared` キーワードによる共有とは異なり、`import` を使用する場合は、スクリプトのコンパイル後にインポートされた関数をバインドするための専用の処理をアプリケーション側に実装する必要があります。

これは、アプリケーション側で「どの関数をインポート可能とするか、あるいはさせないか」を厳密に制御したい場合に有用です。

特別な処理を必要とせず、すべてのインポート関数を一括でバインドするには、アプリケーションは [ビルド](./doc_compile_script) 完了後にモジュールの `BindAllImportedFunctions` メソッドを呼び出すだけです。

よりきめ細かな制御を行いたい場合は、`GetImportedFunctionCount`、`GetImportedFunctionDeclaration`、`GetImportedFunctionSourceModule`、`GetFunctionByDecl`、および `BindImportedFunction` メソッドを使用して、インポートされた関数を 1 つずつ列挙してバインドします。これにより、アプリケーションが許可していない関数のインポートをスクリプトが試みた際に、エラーを発生させるといった制御が可能になります。

共有エンティティ (`shared`) に対するインポート機能のもう一つの利点は、必要に応じてバインドを解除し、別のスクリプトモジュールに再バインドできる柔軟性です。これにより、関数の提供元 (Source) となるモジュールを動的に変更することが可能です。バインドの解除には、`UnbindAllImportedFunctions` または `UnbindImportedFunction` メソッドを使用します。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_import.html
