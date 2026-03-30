---
title: "🛠️ 関数の登録 (Registering a function)"
---

本稿では、AngelScript におけるアプリケーション関数の登録方法と、アプリケーションのインターフェースを適切に公開するために開発者が留意すべき C++ と AngelScript の相違点について解説します。ここで説明する原則は、`RegisterGlobalFunction`、`RegisterObjectMethod`、`RegisterObjectBehaviour` など、API の各所で使用されます。

## アプリケーション関数またはメソッドのアドレスを取得する方法 (How to get the address of the application function or method)

マクロ `asFUNCTION`、`asFUNCTIONPR`、`asMETHOD`、`asMETHODPR` は、C++ の関数ポインタをエンジンが扱える形式で取得し、受け渡しを簡略化するために用意されています。

`asFUNCTION` ターゲットとなる関数名を引数に取ります。これは、オーバーロードのないグローバル関数であればそのまま利用できます。もしオーバーロード（同名で引数リストが異なる複数の関数）が存在する場合は、代わりに `asFUNCTIONPR` を使用してください。このマクロには、関数名、引数リスト、および戻り値の型を明示的に指定します。これにより、C++ コンパイラが適切なオーバーロード関数を正確に解決できるようになります。

```cpp
// グローバル関数
void globalFunc();
r = engine->RegisterGlobalFunction("void globalFunc()", asFUNCTION(globalFunc), asCALL_CDECL); assert( r >= 0 );

// オーバーロードされたグローバル関数
void globalFunc2(int);
void globalFunc2(float);
r = engine->RegisterGlobalFunction("void globalFunc2(int)", asFUNCTIONPR(globalFunc2, (int), void), asCALL_CDECL); assert( r >= 0 );
```

`asMETHOD` と `asMETHODPR` についても同様です。これらと `asFUNCTION`/`asFUNCTIONPR` との違いは、前者がクラス名もパラメータとして受け取ることです。

```cpp
class Object
{
  // クラスメソッド
  void method();
  
  // オーバーロードされたメソッド
  void method2(int input);
  void method2(int input, int &output);
  
  // const メソッド
  int getAttr(int) const;
};

// クラスメソッドの登録
r = engine->RegisterObjectMethod("object", "void method()", asMETHOD(Object,method), asCALL_THISCALL); assert( r >= 0 );

// オーバーロードされたメソッドの登録
r = engine->RegisterObjectMethod("object", "void method2(int)", asMETHODPR(Object, method2, (int), void), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectMethod("object", "void method2(int, int &out)", asMETHODPR(Object, method2, (int, int&), void), asCALL_THISCALL); assert( r >= 0 );

// const メソッドの登録
r = engine->RegisterObjectMethod("object", "int getAttr(int) const", asMETHODPR(Object, getAttr, (int) const, int), asCALL_THISCALL); assert( r >= 0 );
```

> **Note**: `asMETHOD` は、多重継承を使用しているクラスでは正しく動作しない場合があります。C++ コンパイラの制限により、メソッドポインタが誤った基底クラスを参照してしまうことがあるためです。この問題を回避するには、`asMETHODPR` マクロを使用してください。

クラスメソッドを、スクリプトからグローバル関数のように呼び出せる形式で登録することも可能です。これは、シングルトンのインスタンスをスクリプトに公開する際によく利用されます。シングルトンのメソッドが、スクリプトからは通常のグローバル関数のように見えるようになります。この際、登録時にアプリケーション側にインスタンスの参照（ポインタ）が存在している必要があり、スクリプトから呼び出される可能性がある間は、そのオブジェクトが破棄されないようアプリケーション側で保証しなければなりません。

```cpp
class MySingleton
{
  // スクリプトからグローバル関数のごとく呼び出されるクラスメソッド
  void MyGlobalFunc(int arg1, int arg2);
};

MySingleton single;

// シングルトンのメソッドをまるでグローバル関数のように登録する
r = engine->RegisterGlobalFunction("void MyGlobalFunc(int, int)", asMETHOD(MySingleton, MyGlobalFunc), asCALL_THISCALL_ASGLOBAL, &single); assert( r >= 0 );
```

## 呼び出し規約 (Calling convention)

AngelScript は、C++ で一般的に使用される呼び出し規約（cdecl、stdcall、thiscall）をサポートしています。また、プラットフォームがネイティブの呼び出し規約をサポートしていない場合などに利用できる「ジェネリック」な規約も用意されています。

関数の登録時には、それがどの呼び出し規約を使用するかを `asCALL_CDECL`、`asCALL_STDCALL`、`asCALL_THISCALL`、あるいは `asCALL_GENERIC` フラグで指定する必要があります。また、グローバル関数でクラスメソッドをシミュレートするための `asCALL_CDECL_OBJLAST` や `asCALL_CDECL_OBJFIRST`、さらにファンクタ（関数オブジェクト）を登録するための `asCALL_THISCALL_ASGLOBAL` といった特殊な指定も可能です。

登録時に誤った呼び出し規約を指定すると、スクリプトからの呼び出し時にスタックが破損（Stack Corruption）し、アプリケーションがほぼ確実にクラッシュします。C++ のグローバル関数は通常 `cdecl` ですが、ビルド設定やプラットフォームによって異なる場合があるため、確信が持てない場合はまず `asCALL_CDECL` を試してください。明示的に別の規約を指定している場合や、コンパイルオプションでデフォルトの規約を変更している場合を除き、通常は `cdecl` となります。

クラスメソッド（非静的メンバ関数）には `thiscall` 規約が使用されます。ただし、静的メソッド（static）は事実上クラスの名前空間内にあるグローバル関数と同じであるため、扱いに注意してください。通常のメソッド、仮想メソッド、および多重継承クラスのメソッドは、すべて同じように `asCALL_THISCALL` で登録します。

仮想継承（Virtual Inheritance）を含むクラスはネイティブにはサポートされておらず（[後述](#仮想継承はサポートされていません-(virtual-inheritance-is-not-supported))）、それらの場合はラッパー関数を作成する必要があります。これらのラッパー関数は手動で実装することもできますし、[アドオン](./doc_addon#自動ラッパー関数) が提供するテンプレートベースの自動ラッパーを使用することもできます。

参照: [ジェネリック関数](./doc_generic)

## 型の違いについて少し (A little on type differences)

AngelScript は C++ が持っている同じ型のほとんどをサポートしていますが、関数、メソッド、またはビヘイビアを登録する際に知っておくべき違いがあります。記事 [AngelScript vs C++ データ型](./doc_as_vs_cpp_types) を読み、理解しておいてください。

参照を取る関数を登録する際は、その参照内のデータの意図を伝えるために正しいキーワードを指定する必要があります。例えば、入力として使用されることを目的とするパラメータ参照の場合、`&` 文字の後に `in` というキーワードを定義し、出力参照の場合には `out` というキーワードを入れるべきです。[参照型](./doc_register_type#参照型の登録-(registering-a-reference-type)) は入出力両方の参照として渡すことができ、その場合はキーワード `inout` を使用するか、単にキーワードを省略することができます。一方で、[値型 (Value types)](./doc_register_type#値型の登録-(registering-a-value-type)) は `inout` 参照を使用できません。なぜなら、AngelScript は関数の実行中を通じて該当の参照が有効であることを保証できないからです。

ポインタを受け取る関数を登録する場合は、そのポインタが何を表しているかを判断する必要があります。それが値型へのポインタである場合は、参照としてのみ登録できます。もしポインタが参照型へのポインタである場合は、[オブジェクトハンドル](./doc_obj_handle) として、あるいは単なる参照として登録することができます。オブジェクトハンドルを使用することを選択した場合は、オブジェクトが早すぎる段階で破棄されることによるメモリリークやクラッシュの問題を避けるために、型の中にある参照カウンターに注意を払う必要があります。

## 仮想継承はサポートされていません (Virtual inheritance is not supported)

仮想継承を持つクラスのクラスメソッドの登録は、それらが伴う高い複雑性のためにサポートされていません。各コンパイラはこれらのクラスのメソッドポインタを異なる方法で実装しており、コードのポータビリティを維持することは非常に困難です。しかし、仮想継承を持つクラスは比較的まれであり、また存在する場合でもシンプルなプロキシ関数を記述して対応することが容易であるため、これは大きな痛手ではありません。

```cpp
class A { void SomeMethodA(); };
class B : virtual A {};
class C : virtual A {};
class D : public B, public C {};

// クラス D 用に SomeMethodA を登録するためのプロキシ関数が必要
void D_SomeMethodA_proxy(D *d)
{
  // C++ コンパイラが仮想メソッドの呼び出しを解決してくれます
  d->SomeMethodA();
}

// クラスメソッドであるかのようにグローバル関数を登録するが、
// 呼び出し規約は asCALL_CDECL_OBJLAST とする
engine->RegisterObjectMethod("D", "void SomeMethodA()", asFUNCTION(D_SomeMethodA_proxy), asCALL_CDECL_OBJLAST);
```

仮想継承を持つクラスが多数ある場合は、すべてのプロキシ関数を手動で記述しなくても済むように、テンプレートのプロキシ関数を書くことを検討すると良いでしょう。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_register_func.html
