---
title: "AngelScriptの仕組みを理解する (Understanding AngelScript)"
---

AngelScript をうまく活用するためには、AngelScript と C++ の間のいくつかの違いについて理解することが重要です。ライブラリは、アプリケーションの関数やクラスの変更を最小限に抑えつつアプリケーションに組み込めるように書かれていますが、AngelScript と C++ の間でオブジェクトを受け渡す場合にはいくつかの注意が必要です。

 - [バージョン (Versions)](./doc_versions)
 - [スクリプトモジュール (Modules)](./doc_module)
 - [AngelScript vs C++ データ型](./doc_as_vs_cpp_types)
 - [オブジェクトハンドル (Object handles)](./doc_obj_handle)
 - [メモリ管理 (Memory management)](./doc_memory)
 - [typeid の構造 (Structure of the typeid)](#typeid-の構造-structure-of-the-typeid)
 - [呼び出し規約 (Calling convention)](#呼び出し規約-calling-convention)

> TODO: サンドボックスに関する記事を追加する

## typeid の構造 (Structure of the typeid)

AngelScript インターフェースのいくつかの関数で使用される typeid は、32ビットの符号付き整数です。負の値は無効な typeid であり、そのため typeid を返す関数は、[エラーを示すため](#asERetCodes) に負の値を返すことがあります。

typeid に含まれる値は2つの部分から構成されています。[asTYPEID_MASK_SEQNBR](#asTYPEID_MASK_SEQNBR) で示される下位ビットは、アプリケーションによって登録されるか、スクリプト内で宣言された新しい型ごとに増加するシーケンス番号です。上位ビットは型のカテゴリを示すビットマスクを形成します。ビットマスクの各ビットは次のような意味を持っています：

 - bit [asTYPEID_APPOBJECT](#asTYPEID_APPOBJECT) : アプリケーションによって登録されたオブジェクトであることを示します。
 - bit [asTYPEID_SCRIPTOBJECT](#asTYPEID_SCRIPTOBJECT) : スクリプトで宣言された型であることを示します（つまり、オブジェクトを [asIScriptObject](#asIScriptObject) にキャストできます）。
 - bit [asTYPEID_TEMPLATE](#asTYPEID_TEMPLATE) : テンプレートであることを示し、インスタンス化することはできません。
 - bit [asTYPEID_HANDLETOCONST](#asTYPEID_HANDLETOCONST) : const オブジェクトに対するハンドルであることを示します（つまり、参照先のオブジェクトは変更してはなりません）。
 - bit [asTYPEID_OBJHANDLE](#asTYPEID_OBJHANDLE) : オブジェクトハンドルであることを示します（つまり、実際のオブジェクトのアドレスを得るためには値をデリファレンスする必要があります）。
 - bit 32 : typeid が無効であることを示し、数値には [asERetCodes](#asERetCodes) からのエラー値が含まれます。

typeid がプリミティブに対するものかどうかを識別するには、[asTYPEID_MASK_OBJECT](#asTYPEID_MASK_OBJECT) のビットがゼロであるかどうかをチェックします。これは、すべての組み込みプリミティブ型および列挙型に対して真になります。

組み込みのプリミティブ型には、列挙型 [asETypeIdFlags](#asETypeIdFlags) で見られるように事前に定義された ID があり、その値と直接比較することができます。例えば、32ビット符号付き整数の typeid は [asTYPEID_INT32](#asTYPEID_INT32) です。

型に関するさらに詳しい情報、例えば正確なオブジェクト型などを得たい場合は、[asIScriptEngine::GetTypeInfoById](#asIScriptEngine::GetTypeInfoById) を使用してください。そうすれば [asITypeInfo](#asITypeInfo) が返され、その型のすべての詳細情報を取得するために使用できます。

## 呼び出し規約 (Calling convention)

仮想マシン内の AngelScript の内部呼び出し規約は非常にシンプルです。

すべての関数の引数は、最後から最初の順にスタックにプッシュされます。すべての引数は4バイト境界に合わせて調整されます。参照は CPU アーキテクチャに応じて 4バイト または 8バイト になります。
値渡しされるプリミティブ型はそのままプッシュされます。値渡しされるオブジェクト型は、オブジェクト自体がヒープ上に保存される一方で、そのオブジェクトへの参照がスタックにプッシュされます。呼び出された関数は、オブジェクトをクリーンアップしメモリを解放する責任を負います。オブジェクトハンドルの場合は、引数が準備されハンドルがスタックにプッシュされる際に、呼び出し元の関数が参照カウントをインクリメントし、ハンドルの所有権は呼び出された関数に譲渡されます。その後、呼び出された側はリターンする前にハンドルを解放しなければなりません。

可変引数型 `?` の場合、実際の引数値の前に typeid がスタックにプッシュされます。

関数が可変長引数 `...`（すなわち任意の数の引数を受け取る）の場合、実際の引数の数は、最初の関数引数の後にスタックにプッシュされます。

関数がオブジェクトを値として返す場合、返されたオブジェクトを初期化しなければならないアドレスを持つ隠し引数がスタックにプッシュされます。
返されるオブジェクトは、制御が呼び出し元に戻るまで呼び出された関数によって所有されます。つまり、オブジェクトが初期化されてから呼び出し元に制御が戻るまでの間に例外が発生した場合、例外ハンドラーは呼び出された関数のコールフレームの一部として、返されたオブジェクトをクリーンアップします。

関数がクラスのメソッドである場合、オブジェクトインスタンスのアドレスが最後の引数としてスタックにプッシュされます。これにより呼び出された関数は、スタックフレームの 0 番目の位置に always `this` ポインタが存在することに依存することができます。
