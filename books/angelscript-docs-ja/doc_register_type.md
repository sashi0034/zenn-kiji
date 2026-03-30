---
title: "🛠️ オブジェクト型の登録 (Registering an object type)"
---

新しいオブジェクト型を登録する場合、大きく分けて 2 つのアプローチがあります。一つは、ヒープ領域などの動的メモリに確保される **参照型 (Reference Type)**、もう一つは、スタック上や他のオブジェクトのメンバとして直接配置される **値型 (Value Type)** です。参照型は（アプリケーションによる制限がない限り）オブジェクトハンドルをサポートしますが、値渡しでやり取りすることはできません。一方、値型はハンドルをサポートしませんが、値渡し（Pass-by-value）や参照渡しが可能です。

どちらを選択すべきかという厳格なルールはありませんが、一般的には、生成されたスコープを越えて生存し続ける必要があるものは参照型、一時的な計算結果の保持など、すぐに破棄して構わないものは値型として定義します。データサイズが大きかったり、内部構造が複雑な場合は、参照型を選択するのが一般的です。

  - [参照型の登録](#参照型の登録-(registering-a-reference-type))
  - [値型の登録](#値型の登録-(registering-a-value-type))
  - [演算子の振る舞いの登録](#演算子の振る舞いの登録-(registering-operator-behaviours))
  - [オブジェクトメソッドの登録](#オブジェクトメソッドの登録-(registering-object-methods))
  - [オブジェクトプロパティの登録](#オブジェクトプロパティの登録-(registering-object-properties))

## 参照型の登録 (Registering a reference type)

参照型は、動的メモリ、すなわちヒープ上に割り当てられます。スクリプトからは常にオブジェクトハンドルを介して操作され、値渡しでやり取りすることはできません。参照型を登録するには、まず `asOBJ_REF` フラグを使用して型を登録します。

基本的な参照型には、`asBEHAVE_FACTORY`、`asBEHAVE_ADDREF`、および `asBEHAVE_RELEASE` の振る舞い（behaviours）を登録する必要があります。

```cpp
// 参照型の登録
r = engine->RegisterObjectType("ref", 0, asOBJ_REF); assert( r >= 0 );
```

参照: [any](./doc_addon#any-オブジェクト) アドオン（参照型の実装例として）

参照: [ガベージコレクション対応オブジェクト](./doc_gc_object)、[クラス継承](./doc_adv_class_hierarchy)、[スコープ制限付き型](./doc_adv_scoped_type)、[単一参照型](./doc_adv_single_ref_type)（より高度な型の登録について）

### ファクトリ関数 (Factory function)

ファクトリ関数は、変数が宣言された際に AngelScript がその型のインスタンスを生成するために使用する関数です。オブジェクトのメモリ確保と初期化を担当します。

デフォルトのファクトリ関数は引数を取らず、新しいオブジェクトへのハンドルを返す必要があります。この際、オブジェクトの参照カウンターを、返却されるハンドル分だけインクリメントしておくことが重要です。これにより、すべての参照がなくなった時にオブジェクトが適切に解放されるようになります。

```cpp
CRef::CRef()
{
    // コンストラクタで参照カウンターを 1 に初期化します
    refCount = 1;
}

CRef *Ref_Factory()
{
    // クラスコンストラクタで参照カウンターが 1 に設定されます
    return new CRef();
}

// ファクトリの振る舞いを登録
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_FACTORY, "ref@ f()", asFUNCTION(Ref_Factory), asCALL_CDECL); assert( r >= 0 );
```

引数を取るファクトリ関数を登録することも可能で、これを利用してオブジェクトの初期化をカスタマイズできます。

ファクトリ関数はグローバル関数として登録する必要がありますが、静的クラスメソッドや通常のグローバル関数、あるいはジェネリック呼び出し規約に従った関数として実装できます。

ファクトリ関数は、オブジェクトの生成に失敗して例外を発生させる場合を除き、null ハンドルを返してはいけません。例外を投げずに null を返した場合の挙動は未定義です。

#### 補助オブジェクト (Auxiliary object) を使用したファクトリ関数

ファクトリ関数は通常、グローバル関数である必要がありますが、オブジェクトの構築を支援するために「ファクトリ・シングルトン」などの補助オブジェクトを使用することも可能です。これを行うには、呼び出し規約として `asCALL_CDECL_OBJFIRST` または `asCALL_CDECL_OBJLAST` を指定し、登録時に補助オブジェクトのアドレスを渡します。

ファクトリ関数は、指定された呼び出し規約に応じて、最初または最後の引数として補助オブジェクトのアドレスを受け取ります。

```cpp
// ファクトリ関数で使用されるヘルパーオブジェクト
class HelperObject {...} aux;

// ヘルパーオブジェクトのアドレスを最後の引数として受け取るファクトリ関数
CRef *Ref_Factory(int arg, HelperObject *aux) {...}

// 補助オブジェクトを使用してファクトリ関数を登録。ヘルパーオブジェクトはシグネチャに含まれません。
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_FACTORY, "ref@ f(int)", asFUNCTION(Ref_Factory), asCALL_CDECL_OBJLAST, &aux); assert( r >= 0 );
```

#### リストファクトリ関数 (List factory function)

リストファクトリ関数は、型を「初期化リスト（{}）」から作成できるようにするための特殊なファクトリ関数です。引数としてポインタを一つだけ受け取ります。AngelScript は、この引数を通じて初期化リストのバッファへのポインタを渡します。バッファには、オブジェクトの作成と初期化に必要なすべての値が含まれています。

スクリプトエンジンがバッファにどのような情報を配置すべきかを知るために、登録時に「リストパターン」を提供する必要があります。リストパターンは、データ型と以下のトークン：`{`, `}`, `?`, `repeat`, `repeat_same` を用いた特殊な構文で宣言されます。

- `{ }`: リストまたはサブリストを期待することを示します。
- `repeat`: 次の型またはサブリストが 0 回以上繰り返される可能性があることを示します。
- `repeat_same`: `repeat` と同様ですが、繰り返されるすべてのリストが同じ長さであることをコンパイラに伝えます。
- `?`: 任意の型（可変型）を受け入れる場合に使用します。

リストファクトリの登録例：

```cpp
// 配列型: intarray a = {1,2,3}; のように初期化可能
engine->RegisterObjectBehaviour("intarray", asBEHAVE_LIST_FACTORY, 
  "intarray@ f(int &in) {repeat int}", ...);

// 辞書型: dictionary d = {{'a',1}, {'b',2}, {'c',3}}; のように初期化可能
engine->RegisterObjectBehaviour("dictionary", asBEHAVE_LIST_FACTORY, 
  "dictionary @f(int &in) {repeat {string, ?}}", ...);
  
// グリッド型: grid a = {{1,2},{3,4}}; のように初期化可能
engine->RegisterObjectBehaviour("grid", asBEHAVE_LIST_FACTORY,
  "grid @f(int &in) {repeat {repeat_same int}}", ...);
```

ファクトリ関数に渡されるリストバッファは、以下のルールに従って構築されます：

- `repeat` がある場合、バッファにはその後の繰り返し回数を示す 32bit 整数が格納されます。
- `?` がある場合、バッファにはその直後の値の `typeId` を示す 32bit 整数が格納されます。
- 参照型を期待する場合、バッファにはオブジェクトへのポインタが格納されます。
- 値型を期待する場合、バッファにはオブジェクトそのものが格納されます。
- バッファ内のすべての値は、サイズが 32bit 未満である場合を除き、32bit 境界にアラインされます。

参照: [array アドオン](./doc_addon#array-テンプレートオブジェクト)、[dictionary アドオン](./doc_addon#dictionary-オブジェクト)（リストファクトリの実装例）

### Addref および Release の振る舞い

```cpp
void CRef::Addref()
{
    // 参照カウンターを増加
    refCount++;
}

void CRef::Release()
{
    // 参照カウントを減少させ、0に達したら削除
    if( --refCount == 0 )
        delete this;
}

// Addref/Release の振る舞いを登録
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_ADDREF, "void f()", asMETHOD(CRef,AddRef), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_RELEASE, "void f()", asMETHOD(CRef,Release), asCALL_THISCALL); assert( r >= 0 );
```

マルチスレッド環境でオブジェクトを共有する場合は、参照カウンターの操作をアトミック命令を使用してスレッドセーフにする必要があります。

参照: [マルチスレッド](./doc_adv_multithread)

### 参照カウントを行わない参照型 (Reference types without reference counting)

アプリケーション側で参照カウントに基づかない独自のメモリ管理を行っている場合、`asOBJ_NOCOUNT` フラグを指定することで、Addref/Release を登録せずに型を公開できます。

```cpp
// 参照型を登録
r = engine->RegisterObjectType("ref", 0, asOBJ_REF | asOBJ_NOCOUNT); assert( r >= 0 );
```

この場合、スクリプトエンジン（グローバル変数など）によってまだ参照されている可能性があるオブジェクトを、アプリケーション側で破棄しないよう細心の注意を払う必要があります。

オブジェクトがエンジンの生存期間中ずっと存続することが保証されていない場合は、エンジンプロパティ `asEP_DISALLOW_GLOBAL_VARS` を使用してグローバル変数を禁止することを検討してください。これにより、オブジェクトへの参照がどこに保持されているかを把握しやすくなります。あるいは、特定の型を含む可能性のあるグローバル変数のみをプログラムでチェックしてエラーにする方法もあります。

### インスタンス化できない参照型の登録 (Registering an uninstantiable reference type)

スクリプトからは直接作成できないが、操作自体は可能な型を登録したい場合があります。このケースでは、通常の参照型として登録しつつ、ファクトリ関数の登録を省略します。その後、アプリケーション側で事前に生成したオブジェクトへのハンドルを、グローバルプロパティや関数を介してスクリプトに渡すことができます。

これは、オブジェクトの数が限られている場合（シングルトンやオブジェクトプールなど）に有効です。

## 値型の登録 (Registering a value type)

値型を登録する際は、AngelScript が正確なメモリサイズを把握できるように、型のサイズ（sizeof）を指定する必要があります。ポインタなどの管理すべきリソースを一切含まない純粋なデータ型（POD: Plain Old Data）であれば、`asOBJ_POD` フラグを指定できます。この場合、デフォルトコンストラクタ、代入演算子、デストラクタを個別に登録する必要はなく、AngelScript が組み込み型と同様に自動的に処理（ビットコピー等）を行います。

ネイティブ呼び出し規約を使用して型を値渡し（または値で返却）させたい場合は、[C++側での実装の詳細](#値型とネイティブ呼び出し規約-(value-types-and-native-calling-conventions))をさらに AngelScript に伝える必要があります。ジェネリック呼び出し規約のみを使用する場合や、値渡しを一切行わない場合は、これらを気にする必要はありません。

```cpp
// 特別な管理が不要なプリミティブ型を登録
r = engine->RegisterObjectType("pod", sizeof(pod), asOBJ_VALUE | asOBJ_POD); assert( r >= 0 );

// 適切な初期化・破棄が必要なクラスを登録
r = engine->RegisterObjectType("val", sizeof(val), asOBJ_VALUE); assert( r >= 0 );
```

参照: [std::string アドオン](./doc_addon#string-オブジェクト)や [math アドオン](./doc_addon#math-関数) の complex 型（値型の実装例として）

参照: [ガベージコレクション対応オブジェクト](./doc_gc_object)（値型が他の型のメンバとして循環参照を形成する場合）

### コンストラクタとデストラクタ (Constructor and destructor)

コンストラクタやデストラクタが必要な場合は、以下のように登録します：

```cpp
void Constructor(void *memory)
{
  // 配置 new (Placement new) 演算子を使用して、
  // 確保済みのメモリ上でコンストラクタを呼び出す
  new(memory) Object();
}

void Destructor(void *memory)
{
  // オブジェクトのデストラクタを直接呼び出す
  ((Object*)memory)->~Object();
}

// 振る舞いを登録
r = engine->RegisterObjectBehaviour("val", asBEHAVE_CONSTRUCT, "void f()", asFUNCTION(Constructor), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("val", asBEHAVE_DESTRUCT, "void f()", asFUNCTION(Destructor), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

ラッパー関数には、テンプレート実装であってもユニークな名前や名前空間を使用するようにしてください。そうしないと、リンカが誤った関数のアドレスを解決し、予期せぬ動作を引き起こす可能性があります。

また、配置 new 演算子を使用するために `<new>` ヘッダのインクルードが必要になる場合があります。

### リストコンストラクタ (List constructor)

リストコンストラクタは、参照型の[リストファクトリ関数](#リストファクトリ関数-(list-factory-function))と同様の役割を果たします。コンストラクタは初期化リストのバッファへのポインタを受け取り、期待される形式をリストパターンとして登録します。違いは、他の[コンストラクタ](#コンストラクタとデストラクタ-(constructor-and-destructor))と同様にメソッドの形式で登録される点です。

リストコンストラクタの登録例：

```cpp
engine->RegisterObjectBehaviour("vector3", asBEHAVE_LIST_CONSTRUCT, "void f(int &in) {float, float, float}", ...);
```

参照: [math アドオン](./doc_addon#math-関数)（リストコンストラクタを持つ値型の例として）

### 値型とネイティブ呼び出し規約 (Value types and native calling conventions)

値をネイティブ呼び出し規約で受け渡しする場合、AngelScript が C++ 側でその型がどのように扱われているか（レジスタ渡しができるか等）を正確に判断できるよう、詳細なフラグを指定する必要があります。

必要なフラグが提供されていない場合、プラットフォームによっては「Don't support passing/returning type 'MyType' by value...」というエラーが発生します。

C++11 以降を使用している場合、`asGetTypeTraits` テンプレート関数を使用するのが最も簡単で確実です。これは `RegisterObjectType` に渡すべき適切なフラグを自動的に導出します。

```cpp
// C++11 以降: GetTypeTraits を使用して登録
r = engine->RegisterObjectType("complex", sizeof(complex), asOBJ_VALUE | asGetTypeTraits<complex>()); assert( r >= 0 );
```

`asGetTypeTraits` は以下のフラグをカバーします：

| フラグ | 意味 |
| :--- | :--- |
| `asOBJ_APP_CLASS` | C++ の型が class, struct, または union である |
| `asOBJ_APP_CLASS_CONSTRUCTOR` | デフォルトコンストラクタを持つ |
| `asOBJ_APP_CLASS_DESTRUCTOR` | デストラクタを持つ |
| `asOBJ_APP_CLASS_ASSIGNMENT` | コピー代入演算子を持つ |
| `asOBJ_APP_CLASS_COPY_CONSTRUCTOR` | コピーコンストラクタを持つ |
| `asOBJ_APP_PRIMITIVE` | C++ のプリミティブ型（float や double 以外）である |
| `asOBJ_APP_FLOAT` | float または double 型である |
| `asOBJ_APP_ARRAY` | 配列型である |

C++ クラスで `= default` として宣言されている場合は、コンストラクタ等のフラグを含めないでください。

プラットフォームによっては、`asGetTypeTraits` では判断できないさらに詳細な情報が必要な場合があります。これらはコンパイラやターゲット環境に依存しますが、不要な場合に指定しても無視されるだけなので、念のため指定しておいても害はありません。

誤ったフラグを指定すると、スタック破損、不正なメモリアクセス、あるいは戻り値が正しく返ってこないといった検出しにくい不具合の原因となります。AngelScript には、一般的なケースをカバーするためのフラグが用意されています。

| フラグ | 意味 |
| :--- | :--- |
| `asOBJ_APP_CLASS_MORE_CONSTRUCTORS` | デフォルト/コピーコンストラクタ以外のコンストラクタを持つ |
| `asOBJ_APP_CLASS_ALLINTS` | メンバがすべて整数（または非浮動小数点プリミティブ）として扱える |
| `asOBJ_APP_CLASS_ALLFLOATS` | メンバがすべて float または double として扱える |
| `asOBJ_APP_CLASS_ALIGN8` | double など、8バイトアライメントが必要なメンバを含む |
| `asOBJ_APP_CLASS_UNION` | メンバに union を含む |

フラグの使用例：

```cpp
// 引数付きコンストラクタがあるため asOBJ_APP_CLASS_MORE_CONSTRUCTORS が必要
struct A
{
	A() = default;
	A(const A& o) = default;
	A(float x, float y) { this->x = x; this->y = y; }
};

// 浮動小数点以外のプリミティブのみなので asOBJ_APP_CLASS_ALLINTS
struct B
{
	int a;
	void *b;
};

// float のみなので asOBJ_APP_CLASS_ALLFLOATS
struct C
{
	float x,y,z;
};

// double を含むため asOBJ_APP_CLASS_ALIGN8 も併せて指定
struct D
{
	double x,y;
};
```

これらはシステムの ABI に関する専門知識を必要とするため、使用する場合は十分にテストを行ってください。どうしても解決できない場合は、ジェネリック呼び出し規約や[自動ラッパー (auto wrappers)](./doc_addon#自動ラッパー関数) の使用を検討してください。

### C++11 未満のコンパイラを使用する場合

C++11 以降をサポートしていない環境では `asGetTypeTraits` が利用できないため、すべてのフラグを手動で指定する必要があります。

これらのフラグは「スクリプト上での振る舞い」ではなく、あくまで「アプリケーション（C++）側での型」を表すものであることに注意してください。たとえば、C++ クラスをスクリプト上のプリミティブのように扱いたい場合でも `asOBJ_APP_CLASS` を指定する必要があります。

また、クラス自体にコンストラクタが明示的に書かれていなくても、メンバ変数の型によってはコンパイラが自動的にコンストラクタを生成することがあります。その場合も `asOBJ_APP_CLASS_CONSTRUCTOR` などの指定が必要になります。

クラス型には、5種類のフラグの組み合わせを短縮した記法も用意されています。例えば `asOBJ_APP_CLASS_CDAK` は、Constructor（コンストラクタ）、Destructor（デストラクタ）、Assignment（代入演算子）、copy-Konstructor（コピーコンストラクタ）のすべてが存在することを意味します。

```cpp
// 値渡しされる複雑な型を登録する例
r = engine->RegisterObjectType("complex", sizeof(complex), asOBJ_VALUE | asOBJ_APP_CLASS_CDAK); assert( r >= 0 );
```

## 演算子の振る舞いの登録 (Registering operator behaviours)

AngelScript がアプリ側の型と連携するためには、メモリ管理などの基本的な振る舞いを登録する必要があります。

メモリ管理に関する振る舞いは、上記の[参照型の登録](#参照型の登録-(registering-a-reference-type))および[値型の登録](#値型の登録-(registering-a-value-type))で解説されています。

その他の高度な振る舞については、[登録可能な要素](./doc_register_api) で扱います。

多くの振る舞いは通常のクラスメソッドとして実装されますが、コンパイラが理解できるようにあらかじめ定義された名前を使用します。

### 演算子のオーバーロード (Operator overloads)

AngelScript の演算子オーバーロードは、すべて[あらかじめ定義された名前を持つクラスメソッド](./doc_script_class_ops)として実装されます。これは、クラスメソッドとグローバル関数の両方が使用できる C++ とは異なる点です。特に、2つのオペランドを取る二項演算子では、一方がクラスメソッド、もう一方が引数の順序を逆にしたグローバル関数として実装されるのが一般的です。

C++ の演算子オーバーロードを登録する方法は、[関数の登録](./doc_register_func)と同様です。

演算子オーバーロードの登録例：

```cpp
class MyClass
{
  ...

  // 'MyClass - int' 演算子（メソッドとして実装）
  MyClass operator-(int) const;

  // 'int - MyClass' 演算子（グローバル関数として実装）
  static MyClass operator-(int, const MyClass &);
}

void RegisterMyClass(asIScriptEngine *engine)
{
  // 'MyClass - int' 演算子を登録
  engine->RegisterObjectMethod("MyClass", "MyClass opSub(int) const", asMETHODPR(MyClass, operator-, (int) const, MyClass), asCALL_THISCALL); 

  // 'int - MyClass' 演算子を登録（opSub_r は逆順の演算子）
  engine->RegisterObjectMethod("MyClass", "MyClass opSub_r(int) const", asFUNCTIONPR(operator-, (int, const MyClass &), MyClass), asCALL_CDECL_OBJLAST);
}
```

## オブジェクトメソッドの登録 (Registering object methods)

クラスメソッドは `RegisterObjectMethod` で登録します。通常メソッドも仮想メソッドも同様に登録可能です。

なお、静的クラスメソッドは実質的にグローバル関数であるため、オブジェクトメソッドではなく[グローバル関数](./doc_register_func)として登録する必要があります。

```cpp
// クラスメソッドの登録
void MyClass::ClassMethod()
{
  // 処理
}

r = engine->RegisterObjectMethod("mytype", "void ClassMethod()", asMETHOD(MyClass,ClassMethod), asCALL_THISCALL); assert( r >= 0 );
```

また、オブジェクトへのポインタを引数に取るグローバル関数を、あたかもクラスメソッドであるかのように登録することもできます。これにより、C++ 側の実装を変更することなく、スクリプトから見たクラスの機能を拡張できます。

```cpp
// グローバル関数をクラスメソッドとして登録
void MyClass_MethodWrapper(MyClass *obj)
{
  obj->DoSomething();
}

r = engine->RegisterObjectMethod("mytype", "void MethodWrapper()", asFUNCTION(MyClass_MethodWrapper), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

マクロの仕組みに関する詳細は、[関数の登録](./doc_register_func)を参照してください。

### コンポジットメンバ (Composite members)

アプリケーション側でコンポジション（あるクラスが別のクラスをメンバとして持つ）を使用している場合、以下のようにメンバのメソッドを直接登録できます：

```cpp
struct Component
{
  int DoSomething();
};

struct Object
{
  Component *comp;
};

// 最後の引数を true にすると、ポインタをデリファレンスしてメンバにアクセスします。
// インラインメンバの場合は false にします。
r = engine->RegisterObjectMethod("object", "int DoSomething()", asMETHOD(Component, DoSomething), asCALL_THISCALL, 0, asOFFSET(Object, comp), true); assert( r >= 0 );
```

## オブジェクトプロパティの登録 (Registering object properties)

クラスのメンバ変数は `RegisterObjectProperty` を使用して登録できます。これにより、メソッド呼び出しを介さずにスクリプトから直接変数にアクセスできるようになります。

```cpp
struct MyStruct
{
  int a;
};

r = engine->RegisterObjectProperty("mytype", "int a", asOFFSET(MyStruct,a)); assert( r >= 0 );
```

メンバが間接的（ポインタ経由）である場合は、登録時に `&` を付加することで、スクリプトエンジンにデリファレンスが必要であることを伝えられます。

```cpp
struct MyStruct
{
  OtherStruct *a;
};

r = engine->RegisterObjectProperty("mytype", "othertype &a", asOFFSET(MyStruct,a)); assert( r >= 0 );
```

もちろん、そのポインタがスクリプトからアクセスされる間ずっと有効であることをアプリケーション側で保証する必要があります。

注意点として、C++ では参照として宣言されたメンバ変数のアドレスを取得することはできません（`&` 演算子が参照先の値を返してしまうため）。そのため、参照メンバのオフセットを `asOFFSET` で求めることはできません。その場合は、隣接するメンバからのオフセットを手動で計算する必要があります。その際はアライメントやパディングに注意してください。

### コンポジットメンバ (Composite members)

コンポジションを使用している場合、メンバ変数のプロパティも登録可能です：

```cpp
struct Component
{
  int a;
};

struct Object
{
  Component *comp;
};

r = engine->RegisterObjectProperty("object", "comp_a", asOFFSET(Component, a), asOFFSET(Object, comp), true); assert( r >= 0 );
```

### プロパティアクセサ (Property accessors)

メンバ変数を[プロパティアクセサ](./doc_script_class_prop)として公開することも可能です。これは `get_` や `set_` プレフィックスを持ち、`property` デコレータが付与されたメソッドのペアです。

アクセサは `RegisterObjectMethod` で登録します。これは、変数のオフセットが特定できない場合や、内部の型（例：`char*`）とスクリプト側の型（例：`string`）の間で変換が必要な場合に特に有効です。

また、C++ の配列メンバを公開する場合、対応する配列型を登録するよりも、インデックス付きアクセサ（proxy 関数）を作成して公開する方が簡単な場合があります。

仮想プロパティの挙動は、エンジンプロパティ `asEP_PROPERTY_ACCESSOR_MODE` でカスタマイズ可能です。

```cpp
struct MyStruct
{
  int array[16];
};

// Proxy 関数の作成
int MyStruct_get_array(unsigned int idx, MyStruct *o)
{
  if( idx >= 16 ) return 0;
  return o->array[idx];
}

void MyStruct_set_array(unsigned int idx, int value, MyStruct *o)
{
  if( idx >= 16 ) return;
  o->array[idx] = value;
}

// Proxy 関数をメンバメソッドとして登録
r = engine->RegisterObjectMethod("mytype", "int get_array(uint) property", asFUNCTION(MyStruct_get_array), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectMethod("mytype", "void set_array(uint, int) property", asFUNCTION(MyStruct_set_array), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_register_type.html
