---
title: "グローバルプロパティの登録 (Registering global properties)"
---

スクリプトエンジンにグローバルプロパティを登録することで、特別な関数を書かなくてもスクリプトから直接アプリケーション内の変数を検査したり、変更したりできるようになります。

プロパティを登録するには、プロパティの宣言とそのプロパティへのポインタを渡して [RegisterGlobalProperty](#asIScriptEngine::RegisterGlobalProperty) メソッドを呼び出すだけです。登録されたプロパティは、エンジン内でその登録が有効である限り、存続（アライブ）し続けなければならないことに注意してください。

AngelScript に正しいポインタを渡していることを確認してください。ポインタは宣言が参照している値へのポインタでなければなりません。つまり、宣言が整数であればポインタは整数値へのポインタであり、宣言がオブジェクトハンドルであればポインタはオブジェクトへのポインタへのポインタであるべきです。残念ながら、AngelScript 側でポインタが正しいかどうかを検証する方法はないため、もし誤ったポインタが渡された場合、アプリケーションが予期せぬ動作を示すことによって実行時に初めてそれに気づくことになります。

```cpp
// スクリプトからアクセスできるようにすべき変数
int      g_number       = 0;
CObject *g_object       = 0;
Vector3  g_vector       = {0,0,0};
bool     g_readOnlyFlag = false;

// グローバルプロパティを登録するための関数
void RegisterProperties(asIScriptEngine *engine)
{
    int r;
    
    // スクリプトから読み書き可能なプリミティブプロパティを登録する
    r = engine->RegisterGlobalProperty("int g_number", &g_number); assert( r >= 0 );
    
    // スクリプトが CObject 型へのハンドルを保存できる変数を登録する。
    // CObject 型がすでに参照型としてエンジンに登録されていることを前提としています。
    r = engine->RegisterGlobalProperty("CObject @g_object", &g_object); assert( r >= 0 );
    
    // 3Dベクター変数を登録する。
    // Vector3 型がすでに値型として登録されていることを前提としています。
    r = engine->RegisterGlobalProperty("Vector3 g_vector", &g_vector); assert( r >= 0 );
    
    // スクリプトから読み取ることはできるが、変更はできない論理値フラグを登録する。
    r = engine->RegisterGlobalProperty("const bool g_readOnlyFlag", &g_readOnlyFlag); assert( r >= 0 );
}
```

また、[プロパティアクセサ](./doc_script_class_prop) を通じてプロパティを公開することも可能です。これはプロパティ値の取得や設定を行うためのもので、`get_` および `set_` のプレフィックスと、関数デコレータ `property` を持つ関数のペアです。これらの関数は [RegisterGlobalFunction](./doc_register_func) を使用して登録されるべきです。これは、プロパティのオフセットが決定できない場合や、プロパティの型がスクリプトに登録されておらず（例：`char*` から `string` への）何らかの変換が必要な場合に特に有用です。

> **Note**: 仮想プロパティの動作は、プロパティ設定 [asEP_PROPERTY_ACCESSOR_MODE](./doc_adv_custom_options_lang_mod) を用いてカスタマイズすることができます。

参照: [型の登録](./doc_register_type)
