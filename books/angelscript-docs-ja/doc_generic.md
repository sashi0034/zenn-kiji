---
title: "ジェネリック呼び出し規約 (The generic calling convention)"
---

ジェネリック呼び出し規約 (generic calling convention) は、アプリケーションのネイティブな呼び出し規約が機能しない状況、例えばネイティブの呼び出し規約のサポートがまだ追加されていないプラットフォーム向けに利用可能です。ターゲットプラットフォームでネイティブ呼び出し規約がサポートされているかどうかを検出するには、[asGetLibraryOptions](#asGetLibraryOptions) 関数を呼び出し、返された文字列に "AS_MAX_PORTABILITY" が含まれているかを確認します。この識別子が返された文字列に含まれている場合、ネイティブな呼び出し規約はサポートされていません。

ジェネリック呼び出し規約を実装する関数は、[asIScriptGeneric](#asIScriptGeneric) インターフェースへのポインタをパラメータとして受け取り `void` を返す、常にグローバル関数（または静的クラスメソッド）の形式をとります。

```cpp
// この関数は以下のシグネチャで登録されています：
//  MyIntf @func(int, float, MyIntf @+)
void MyGenericFunction(asIScriptGeneric *gen)
{
  // 引数を抽出する
  int arg0              = gen->GetArgDWord(0);
  float arg1            = gen->GetArgFloat(1);
  asIScriptObject *arg2 = reinterpret_cast<asIScriptObject*>(gen->GetArgObject(2));
  
  // 実際の関数を呼び出す
  asIScriptObject *ret = MyFunction(arg0, arg1, arg2);
  
  // 戻り値を設定する
  gen->SetReturnObject(ret);
}
```

ジェネリック呼び出し規約を使用する関数は、スクリプトエンジンがグローバル関数またはクラスメソッドを期待する場所であればどこでも登録することができます（明示的に別段の指定がある場合を除きます）。

ジェネリック呼び出し規約用の関数を記述するには、AngelScript のスタックから各引数を抽出し、その後手動で戻り値を返す必要があります。そのため、自分自身で関数を記述するよりも、[自動ラッパー関数](./doc_addon_autowrap) を使用する方が望ましい場合があります。

## 関数の引数の抽出 (Extracting function arguments)

ジェネリックなインターフェースから関数の引数を抽出するには、引数の値を返す `GetArg` メソッドのいずれか、または [GetAddressOfArg](#asIScriptGeneric::GetAddressOfArg) メソッドを呼び出します。`GetAddressOfArg` メソッドは実際の値へのポインタを返します。アプリケーションはそのアドレスから値を読み取れるように、このポインタを正しい型のポインタへとキャストする必要があります。

実装している関数がクラスメソッドを表す場合、オブジェクトインスタンスへのポインタは [GetObject](#asIScriptGeneric::GetObject) を呼び出すことによって取得する必要があります。

出力参照（すなわち `&out`）を受け取る引数の場合、`GetAddressOfArg` はその型の有効なインスタンスへのアドレスを提供します。もし関数がこれらの引数に何も返したくない場合は、何もしなくて構いません。

`asIScriptGeneric` インターフェースはネイティブ呼び出し規約の場合と同じ方法で参照カウントを処理します。つまり、（または [関数の引数を @+ 付きで登録する](./doc_obj_handle_4) 場合を除き）ハンドルとして受け取ったハンドルを解放する責任はアプリケーションの関数にあります。

## 戻り値を返す (Returning values)

関数から値を返すには、`SetReturn` メソッドのいずれかを呼び出してジェネリックなインターフェースに値を渡します。プリミティブな値を返すのは簡単ですが、値型の値渡し、参照渡し、またはオブジェクトハンドルとしてオブジェクト型を返す場合は注意が必要です。型や使用される関数によっては、参照カウントをインクリメントしたり、あるいは最初にオブジェクトのコピーを作成したりする必要があるかもしれません。期待通りの結果を得るために何をすべきかを判断するには、[SetReturnAddress](#asIScriptGeneric::SetReturnAddress) と [SetReturnObject](#asIScriptGeneric::SetReturnObject) の説明を注意深く読んでください。

[GetAddressOfReturnLocation](#asIScriptGeneric::GetAddressOfReturnLocation) メソッドを使用して、戻り値が保存されるメモリのアドレスを取得することも可能です。このメモリは初期化されていないため、placement new 演算子を使用してコンストラクタを呼び出し、このメモリを初期化する必要があります。これはプリミティブ型に対しても機能するため、[自動ラッパー関数](./doc_addon_autowrap) などのテンプレート実装において理想的です。

戻り値の型がハンドルである場合、`GetAddressOfReturnLocation` は null ポインタを保持する場所を参照するため、関数が null を返す場合は何もしなくて構いません。プリミティブの場合、それは未定義の値になるため、値が重要であればそれを設定しなければなりません。呼び出し元の関数によってすでに事前割り当てされた場所で返される値型のオブジェクトの場合、[SetException](#asIScriptContext::SetException) で例外が設定されていない限り、関数はその場所で戻り値を初期化しなければなりません。

関数が `@+` を返すように登録されている場合、ネイティブな呼び出し規約のために行われるのと同様に、スクリプトエンジンは [自動的に参照カウントをインクリメント](./doc_obj_handle_4) します。
