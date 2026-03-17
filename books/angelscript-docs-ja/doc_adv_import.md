---
title: "関数のインポート (Import functions)"
---

[関数のインポート](./doc_global_import) は、スクリプトモジュール間でコードを [共有](./doc_script_shared) するための一形態です。しかし、`shared` キーワードを使った方法とは異なり、`import` の場合は、スクリプトがコンパイルされた後にインポートされた関数をバインドするための固有のコードがアプリケーション側に必要になります。

これは、アプリケーションが「何をインポートできて何をインポートできないか」を明確に制御したい場合に役立ちます。

特別な処理を一切行わずにインポートされたすべての関数をバインドするには、アプリケーションは [ビルド](./doc_compile_script) が完了した後に、[BindAllImportedFunctions](#asIScriptModule::BindAllImportedFunctions) メソッドを呼び出すだけです。

よりきめ細かな制御を行いたい場合、アプリケーションは [GetImportedFunctionCount](#asIScriptModule::GetImportedFunctionCount)、[GetImportedFunctionDeclaration](#asIScriptModule::GetImportedFunctionDeclaration)、[GetImportedFunctionSourceModule](#asIScriptModule::GetImportedFunctionSourceModule)、[GetFunctionByDecl](#asIScriptModule::GetFunctionByDecl)、および [BindImportedFunction](#asIScriptModule::BindImportedFunction) の各メソッドを使用して、インポートされた関数を1つずつ列挙してバインドし、もしアプリケーションが許可していない関数をスクリプトがインポートしようとした場合にはエラーを発生させるべきです。

関数のインポート機能が共有エンティティ (`shared`) よりも優れているもう1つの利点は、提供元 (sourcing) のモジュールを変更する必要がある場合に、インポートされた関数のバインドを解除し、その後別のスクリプトモジュールに再バインドできることです。バインドされた関数のバインドを解除するには、[UnbindAllImportedFunctions](#asIScriptModule::UnbindAllImportedFunctions) または [UnbindImportedFunction](#asIScriptModule::UnbindImportedFunction) メソッドを使用します。
