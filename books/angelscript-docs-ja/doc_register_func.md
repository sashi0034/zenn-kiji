---
title: "関数の登録 (Registering a function)"
---

この記事は、AngelScript で関数を登録する方法と、スクリプトが使用するアプリケーションインターフェースを正常に登録するために開発者が把握しておくべき、C++ と AngelScript の間のいくつかの違いについて説明することを目的としています。ここで学ぶ原則は、`RegisterGlobalFunction`、`RegisterObjectMethod`、`RegisterObjectBehaviour` など、いくつかの場所で使用されます。

## アプリケーション関数またはメソッドのアドレスを取得する方法 (How to get the address of the application function or method)

マクロ [asFUNCTION](#asFUNCTION)、[asFUNCTIONPR](#asFUNCTIONPR)、[asMETHOD](#asMETHOD)、および [asMETHODPR](#asMETHODPR) は、関数ポインタを取得してスクリプトエンジンに渡す作業を容易にするために実装されています。

`asFUNCTION` は関数名をパラメータとして受け取ります。これは、オーバーロードを持たないすべてのグローバル関数で機能します。オーバーロード（すなわち、同じ名前でパラメータが異なる複数の関数）を使用する場合は、代わりに `asFUNCTIONPR` を使用する必要があります。このマクロは関数名、パラメータリスト、および戻り値の型をパラメータとして受け取り、C++ コンパイラがどのアドレスのオーバーロード関数を取得すべきかを正確に解決できるようにします。

```cpp
// グローバル関数
void globalFunc();
r = engine->RegisterGlobalFunction("void globalFunc()", asFUNCTION(globalFunc), asCALL_CDECL); assert( r >= 0 );

// オーバーロードされたグローバル関数
void globalFunc2(int);
void globalFunc2(float);
r = engine->RegisterGlobalFunction("void globalFunc2(int)", asFUNCTIONPR(globalFunc2, (int), void), asCALL_CDECL); assert( r >= 0 );
```

`asMETHOD` と `asMETHODPR` についても同様です。これらと `asFUNCTION`/`asFUNCTIONPR` との違いは、前者がクラス名とパラメータの両方を受け取ることです。

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

> **Note**: `asMETHOD` は、多重継承を持つクラスではうまく機能しません。C++ コンパイラの制限により、一部のコンパイラではメソッドポインタが誤ったベースクラスを参照してしまうことになります。その場合の解決策は `asMETHODPR` マクロを使用することです。

スクリプトから呼び出されるクラスメソッドを、まるでグローバル関数であるかのように登録することが可能です。これは、シングルトンをスクリプトインターフェースに公開する際によく行われます。なぜなら、シングルトンのメソッドは通常のグローバル関数のように見えるためです。これを行う場合、アプリケーションは登録時にオブジェクトへの参照を持っていなければならず、また、スクリプトがそのメソッドを呼び出す可能性がなくなるまで、オブジェクトが生存していることをアプリケーション側で保証する必要があります。

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

AngelScript は、C++ が使用する最も一般的な呼び出し規約（cdecl、stdcall、および thiscall）を受け入れます。また、ネイティブ呼び出し規約がターゲットプラットフォームでサポートされていない場合などに使用できるジェネリックな呼び出し規約もあります。

アプリケーション関数がどの呼び出し規約を使用しているかを AngelScript に伝えるために、すべての関数およびビヘイビア（振る舞い）は、[asCALL_CDECL](#asCALL_CDECL)、[asCALL_STDCALL](#asCALL_STDCALL)、[asCALL_THISCALL](#asCALL_THISCALL)、または [asCALL_GENERIC](#asCALL_GENERIC) のフラグを用いて登録する必要があります。クラスメソッドをグローバル関数を通じてシミュレートするために、`asCALL_THISCALL` が受け入れられる場所であればどこでも、特別な規約である [asCALL_CDECL_OBJLAST](#asCALL_CDECL_OBJLAST) と [asCALL_CDECL_OBJFIRST](#asCALL_CDECL_OBJFIRST) を使用することもできます。また、関数オブジェクト (Functor) は、構成 [asCALL_THISCALL_ASGLOBAL](#asCALL_THISCALL_ASGLOBAL) を用いてグローバル関数をエミュレートしたり、構成 [asCALL_THISCALL_OBJFIRST](#asCALL_THISCALL_OBJFIRST) または [asCALL_THISCALL_OBJLAST](#asCALL_THISCALL_OBJLAST) を用いてクラスメソッドをエミュレートすることも可能です。

登録時に誤った呼び出し規約が指定された場合、スクリプトエンジンが関数を呼び出すたびに、アプリケーションがスタック破損でクラッシュする可能性が非常に高くなります。C++ プログラムにおけるすべてのグローバル関数のデフォルト呼び出し規約は cdecl であるため、迷った場合はまず `asCALL_CDECL` で試してみてください。呼び出し規約が cdecl と異なるのは、関数が明示的に別の規約を使用するように宣言されている場合や、コンパイラのオプションでデフォルトを他の規約に設定している場合だけです。

クラスメソッドについては、thiscall 規約しか存在しません（スタティックメソッドは別として、スタティックメソッドは実際にはクラス名前空間内のグローバル関数であるため）。通常のメソッド、仮想メソッド、および多重継承を持つクラスのメソッドはすべて同じ方法（`asCALL_THISCALL`）で登録されます。

仮想継承を持つクラスはネイティブにはサポートされておらず（[後述](#仮想継承はサポートされていません-virtual-inheritance-is-not-supported)）、これらの場合はラッパー関数を作成する必要があります。これらのラッパー関数は手動で実装することもできますし、[アドオン](./doc_addon#自動ラッパー関数-autowrapper) が提供するテンプレートベースの自動ラッパーを使用することもできます。

参照: [ジェネリック関数](./doc_generic)

## 型の違いについて少し (A little on type differences)

AngelScript は C++ が持っている同じ型のほとんどをサポートしていますが、関数、メソッド、またはビヘイビアを登録する際に知っておくべき違いがあります。記事 [AngelScript vs C++ データ型](./doc_as_vs_cpp_types) を読み、理解しておいてください。

参照を取る関数を登録する際は、その参照内のデータの意図を伝えるために正しいキーワードを指定する必要があります。例えば、入力として使用されることを目的とするパラメータ参照の場合、`&` 文字の後に `in` というキーワードを定義し、出力参照の場合には `out` というキーワードを入れるべきです。[参照型](./doc_register_type#参照型の登録-registering-a-reference-type) は入出力両方の参照として渡すことができ、その場合はキーワード `inout` を使用するか、単にキーワードを省略することができます。一方で、[値型 (Value types)](./doc_register_type#値型の登録-registering-a-value-type) は `inout` 参照を使用できません。なぜなら、AngelScript は関数の実行中を通じて該当の参照が有効であることを保証できないからです。

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
