---
title: "🛠️ グローバルプロパティの登録 (Registering global properties)"
---

グローバルプロパティ（Global Properties）を登録すると、特別なラッパー関数などを記述することなく、スクリプトからアプリケーション内の変数を直接参照・変更できるようになります。

プロパティを登録するには、宣言文と対象プロパティへのポインタを指定して `RegisterGlobalProperty` メソッドを呼び出します。登録されたプロパティは、その登録がエンジン内で有効である限り、アプリケーション側で生存（存続）し続けなければならない点に注意してください。

AngelScript に渡すポインタが、宣言された型に対応する正しいアドレスであることを確認してください。例えば整数型として登録する場合は `int*`、オブジェクトハンドルとして登録する場合は「オブジェクトポインタへのポインタ（`obj**`）」を渡す必要があります。残念ながら AngelScript 側で渡されたポインタの妥当性を自動的に検証する術はないため、誤ったアドレスを指定すると、実行時に不正なメモリアクセスや予期せぬ挙動を引き起こす原因となります。

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

また、[プロパティアクセサ](./doc_script_class_prop) を通じて仮想的なプロパティを公開することも可能です。これはプロパティ値の取得や設定を行うための関数ペアで、`get_` および `set_` の接頭辞と、関数デコレータ `property` を持つ関数として実装します。これらの関数は `RegisterGlobalFunction` を使用して登録されます。これは、プロパティのメモリ上のオフセットが不定である場合や、プロパティの型がスクリプトに登録されておらず（例：`char*` から `string` への）何らかの変換が必要な場合に特に有用です。

> **Note**: 仮想プロパティの動作は、エンジンプロパティ [asEP_PROPERTY_ACCESSOR_MODE](./doc_adv_custom_options#言語の変更-(language-modifications)) を用いてカスタマイズすることができます。

参照: [型の登録](./doc_register_type)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_register_prop.html
