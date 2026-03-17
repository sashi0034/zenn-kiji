---
title: "可変パラメータ型 (The variable parameter type) / 可変長引数 (Variadic arguments)"
---

## 可変パラメータ型 (The variable parameter type)

アプリケーションは、**可変型 (variable type)** への参照を受け取る関数を登録することができます。これは、その関数が任意の型の変数への参照を受け取ることができることを意味します。この機能は、ジェネリックなコンテナを作成する際などに役立ちます。

関数がこの特別なパラメータ型を用いて登録されると、関数は参照と共に、その変数の型の [型ID (type id)](./doc_typeid) を格納した追加の引数を受け取ります。この参照は呼び出し元が送信した「実際の値」を参照します。すなわち、式がオブジェクトハンドルである場合、参照は実際のオブジェクトではなくそのハンドルを参照することになります。

```cpp
// ネイティブ関数での使用例
engine->RegisterGlobalFunction("void func_c(?&in)", asFUNCTION(func_c), asCALL_CDECL);

void func_c(void *ref, int typeId)
{
    // 参照を使って何かを実行する

    // 参照の型は型IDを通じて決定されます
}

// ジェネリック関数での使用例
engine->RegisterGlobalFunction("void func_g(?&in)", asFUNCTION(func_g), asCALL_GENERIC);

void func_g(asIScriptGeneric *gen)
{
    void *ref = gen->GetArgAddress(0);
    int typeId = gen->GetArgTypeId(0);

    func_c(ref, typeId);
}
```

可変型は `out` 参照と組み合わせて使用することもできますが、`inout` 参照とは組み合わせて使用できません。現在、これはグローバル関数、オブジェクトコンストラクタ、およびオブジェクトメソッドでのみ使用可能です。その他の振る舞いや演算子とは組み合わせて使用できません。

可変型はスクリプト内では利用できないため、アプリケーション側の関数の登録にのみ使用することができます。

使用例については [any アドオン](./doc_addon_any) および [辞書アドオン](./doc_addon_dict) を参照してください。型IDの解釈方法に関する情報については [型ID (type id)](./doc_typeid) を参照してください。

### 可変型の変換演算子 (Variable conversion operators)

可変パラメータ型は、[opConv と opCast](./doc_script_class_conv) の演算子オーバーロードの特別バージョンで使用することもできます。これは、任意の型のコンテンツを保持できるようにする必要があるジェネリックなコンテナ型にとって特に有用です。

 - `void opCast(?&out)`
 - `void opConv(?&out)`

例については [ハンドルアドオン](./doc_addon_handle) および [辞書アドオン](./doc_addon_dict) を参照してください。


---

## 可変長引数 (Variadic arguments)

可変長引数（可変個引数）を受け取る関数もエンジンに登録することができますが、その関数は [ジェネリック呼び出し規約](./doc_generic) で実装されていなければなりません。

関数が可変長引数を受け取るように登録されている場合、コンパイラは関数に渡された引数の数を保持する隠し引数をスタックにさらに一つ積みます。これは `asIScriptGeneric` インターフェースが引数の数を知るために使用されます。アプリケーションはこの隠し引数を明示的に読み取る必要はなく、通常通り [GetArgCount](#asIScriptGeneric::GetArgCount) メソッドを使用するだけで構いません。可変長部分に渡されるすべての引数の型は同一となります（アプリケーションが登録した型です）。

この引数の一般的な構成としては、[可変パラメータ型](#可変パラメータ型-the-variable-parameter-type) のリストを入力として受け取るための `const ?&in ...`、または様々な型の引数を出力として受け取るための `?&out ...` があります。しかし単にそれだけが必要なのであれば、特定の単一の型（例：`int ...`）を指定しても完全に問題ありません。

```cpp
    r = engine->RegisterGlobalFunction("string format(const string&in fmt, const ?&in ...)", asFUNCTION(StringFormat), asCALL_GENERIC); assert(r >= 0);
    r = engine->RegisterGlobalFunction("uint scan(const string&in str, ?&out ...)", asFUNCTION(StringScan), asCALL_GENERIC); assert(r >= 0);
```

参照: [文字列アドオン](./doc_addon_std_string) における `format` と `scan` の実装。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_var_type.html
