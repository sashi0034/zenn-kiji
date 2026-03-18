---
title: "可変パラメータ型 (The variable parameter type) / 可変長引数 (Variadic arguments)"
---

アプリケーション側では、**可変パラメータ型（Variable Parameter Type）**への参照を受け取る関数を登録できます。これは、関数が任意の型の変数への参照を受け取れることを意味しており、汎用コンテナの作成に役立ちます。

関数をこの特殊なパラメータ型で登録すると、その関数には参照と追加の引数としてその変数の [型ID（Type ID）](./doc_typeid) が渡されます。この参照は、呼び出し元が渡した「実体」を指します。例えば、渡された式がオブジェクトハンドルである場合、参照はオブジェクトそのものではなく、ハンドル自体を指すことになります。

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

可変パラメータ型は `out` 参照と組み合わせて使用できますが、`inout` 参照には対応していません。現時点では、グローバル関数、オブジェクトのコンストラクタ、およびオブジェクトメソッドでのみ使用可能です。その他の振る舞いや演算子には使用できません。

また、可変型はスクリプト内では直接使用できず、あくまでアプリケーション側での関数登録専用です。

使用例については [any アドオン](./doc_addon#any-オブジェクト) および [辞書アドオン](./doc_addon#dictionary-オブジェクト) を参照してください。型IDの解釈方法に関する情報については [AngelScript の理解](./doc_understanding_as#typeid-の構造) を参照してください。

### 可変型の変換演算子 (Variable conversion operators)

可変パラメータ型は、[演算子オーバーロード](./doc_script_class_ops#型変換演算子-type-conversion-operators) の特別バージョンで使用することもできます。これは、任意の型のコンテンツを保持できるようにする必要があるジェネリックなコンテナ型にとって特に有用です。

 - `void opCast(?&out)`
 - `void opConv(?&out)`

例については [ハンドルアドオン](./doc_addon#handle-オブジェクト) および [辞書アドオン](./doc_addon#dictionary-オブジェクト) を参照してください。


---

## 可変長引数 (Variadic arguments)

可変長引数（Variadic Arguments）を受け取る関数もエンジンに登録できますが、その関数は [ジェネリック呼び出し規約](./doc_generic) で実装されている必要があります。

関数が可変長引数を受け取るように登録されている場合、コンパイラは関数に渡された引数の数を保持する隠し引数をスタックにさらに一つ積みます。これは `asIScriptGeneric` インターフェースが引数の数を知るために使用されます。アプリケーションはこの隠し引数を明示的に読み取る必要はなく、通常通り `GetArgCount` メソッドを使用するだけで構いません。可変長部分に渡されるすべての引数の型は（アプリケーションが登録した型と）同一になります。

この引数の一般的な構成としては、[可変パラメータ型](#可変パラメータ型-the-variable-parameter-type) のリストを入力として受け取るための `const ?&in ...`、または様々な型の引数を出力として受け取るための `?&out ...` があります。しかし単にそれだけが必要なのであれば、特定の単一の型（例：`int ...`）を指定しても完全に問題ありません。

```cpp
    r = engine->RegisterGlobalFunction("string format(const string&in fmt, const ?&in ...)", asFUNCTION(StringFormat), asCALL_GENERIC); assert(r >= 0);
    r = engine->RegisterGlobalFunction("uint scan(const string&in str, ?&out ...)", asFUNCTION(StringScan), asCALL_GENERIC); assert(r >= 0);
```

参照: [文字列アドオン](./doc_addon#string-オブジェクト) における `format` と `scan` の実装。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_adv_var_type.html
