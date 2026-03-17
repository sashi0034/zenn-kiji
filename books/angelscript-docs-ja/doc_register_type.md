---
title: "オブジェクト型の登録 (Registering an object type)"
---

新しい型を登録する際に取るべき主要な道は2つあります。1つは、動的メモリ（ヒープ）に配置される参照型 (reference type) であり、もう1つはスタック上や他のオブジェクトのメンバとしてローカルに配置される値型 (value type) です。参照型は（アプリケーションによって制限されていない限り）オブジェクトハンドルをサポートしますが、アプリケーションに登録された関数へ値渡しすることはできません。一方、値型はハンドルをサポートしませんが、アプリケーションに登録された関数へ値渡しまたは参照渡しをすることができます。

どちらを使用すべきかという明確なルールはありませんが、一般的には、型が作成されたスコープを超えて存続できなければならない場合には参照型を使用し、短い計算を実行した後に不要になるような用途がメインの場合には値型を使用します。もし型が巨大であったり複雑であったりする場合は、参照型を選択する可能性が高いでしょう。

 - [参照型の登録 (Registering a reference type)](#参照型の登録-registering-a-reference-type)
 - [値型の登録 (Registering a value type)](#値型の登録-registering-a-value-type)
 - [演算子の振る舞いの登録 (Registering operator behaviours)](#演算子の振る舞いの登録-registering-operator-behaviours)
 - [オブジェクトメソッドの登録 (Registering object methods)](#オブジェクトメソッドの登録-registering-object-methods)
 - [オブジェクトプロパティの登録 (Registering object properties)](#オブジェクトプロパティの登録-registering-object-properties)

---

## 参照型の登録 (Registering a reference type)

基本的な参照型は、`asBEHAVE_FACTORY`、`asBEHAVE_ADDREF`、および `asBEHAVE_RELEASE` の振る舞い (behaviours) とともに登録する必要があります。

```cpp
// 参照型の登録
r = engine->RegisterObjectType("ref", 0, asOBJ_REF); assert( r >= 0 );
```

参照型の例については [any](./doc_addon#any-オブジェクト) アドオンを参照してください。

より高度な型については、[ガベージコレクション対応オブジェクト](./doc_gc_object)、[クラス階層](./doc_adv_class_hierarchy)、[スコープ付きの型](./doc_adv_scoped_type)、そして [単一参照の型](./doc_adv_single_ref_type) を参照してください。

### ファクトリ関数 (Factory function)

ファクトリ関数は、変数が宣言されたときに AngelScript がこの型のオブジェクトをインスタンス化するために使用する関数です。これはオブジェクトのメモリの割り当てと初期化を行う責任があります。

デフォルトのファクトリ関数はパラメータを受け取らず、新しいオブジェクトのオブジェクトハンドルを返す必要があります。オブジェクトへのすべての参照が削除されたときにオブジェクトが適切に解放されるよう、オブジェクトの参照カウンターがファクトリ関数によって返される参照を正しくカウントしていることを確認してください。

```cpp
CRef::CRef()
{
    // コンストラクタで参照カウンターを 1 に初期化する
    refCount = 1;
}

CRef *Ref_Factory()
{
    // クラスのコンストラクタ内で参照カウンターが 1 に初期化される
    return new CRef();
}

// ファクトリの振る舞いを登録する
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_FACTORY, "ref@ f()", asFUNCTION(Ref_Factory), asCALL_CDECL); assert( r >= 0 );
```

パラメータを受け取るファクトリ関数を登録することもでき、これらはオブジェクトの初期化時に使用されます。

ファクトリ関数はグローバル関数として登録されなければなりませんが、静的なクラスメソッド、一般的なグローバル関数、またはジェネリック呼び出し規約に従うグローバル関数として実装することが可能です。

ファクトリ関数がオブジェクトハンドルを返す場合であっても、（オブジェクトのインスタンス化に失敗したことを示す例外を設定した場合を除き）null ハンドルを返してはなりません。

例外を設定せずに null を返すファクトリ関数の動作は未定義です。

#### 補助オブジェクトを伴うファクトリ関数 (Factory function with auxiliary object)

ファクトリ関数はグローバル関数であることが想定されていますが、オブジェクトの構築を補助するために補助オブジェクト（例：ファクトリシングルトン）を使用することも可能です。これを行うには、アプリケーションは呼び出し規約 `asCALL_CDECL_OBJFIRST` または `asCALL_CDECL_OBJLAST` を使用し、ファクトリ関数の登録時に補助オブジェクトのアドレスを通知する必要があります。

その後、ファクトリ関数は、指定された呼び出し規約に応じて最初または最後のパラメータとして補助オブジェクトのアドレスを受け取ります。

```cpp
// ファクトリ関数によって使用されるヘルパーオブジェクト
class HelperObject {...} aux;

// ファクトリ関数は最後の引数としてヘルパーオブジェクトのアドレスを受け取る
CRef *Ref_Factory(int arg, HelperObject *aux) {...}

// 補助オブジェクトを伴ってファクトリの振る舞いを登録する。ヘルパーオブジェクトは関数のシグネチャには含まれません。
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_FACTORY, "ref@ f(int)", asFUNCTION(Ref_Factory), asCALL_CDECL_OBJLAST, &aux); assert( r >= 0 );
```

#### リストファクトリ関数 (List factory function)

リストファクトリ関数は、初期化リスト（initialization list）から型を作成できるように登録される特別な[ファクトリ関数](#ファクトリ関数-factory-function)です。リストファクトリ関数は、単一のポインタのみを引数として受け取ります。AngelScript は、その引数に初期化リストのバッファへのポインタを渡します。このバッファには、オブジェクトの作成と初期化に必要なすべての値が含まれます。

スクリプトエンジンがバッファに配置すべき情報を把握できるようにするため、アプリケーションはリストファクトリを登録する際に**リストパターン (list pattern)**を提供する必要があります。リストパターンは、データ型と次のトークンから構成される特別な構文で宣言されます：`{`、`}`、`?`、`repeat`、および `repeat_same`。

`{ }` トークンは、リストパターンが値のリストまたはサブリストを期待することを宣言するために使用されます。`repeat` トークンは、次の型またはサブリストが0回以上繰り返される可能性があることを示します。`repeat_same` トークンは `repeat` と似ていますが、リストが繰り返されるたびに同じ長さでなければならないこともコンパイラに伝えます。リストパターンには、値渡し可能なデータ型であれば任意のデータ型を使用できます。可変型が要求される場合には `?` トークンを使用できます。

リストパターンを使ったリストファクトリの登録の例は以下の通りです：

```cpp
// 配列型は例えば次のように初期化できます： intarray a = {1,2,3};
engine->RegisterObjectBehaviour("intarray", asBEHAVE_LIST_FACTORY, 
  "intarray@ f(int &in) {repeat int}", ...);

// 辞書型は次のように初期化できます： dictionary d = {{'a',1}, {'b',2}, {'c',3}};
engine->RegisterObjectBehaviour("dictionary", asBEHAVE_LIST_FACTORY, 
  "dictionary @f(int &in) {repeat {string, ?}}", ...);
  
// グリッド型は次のように初期化できます： grid a = {{1,2},{3,4}};
engine->RegisterObjectBehaviour("grid", asBEHAVE_LIST_FACTORY,
  "grid @f(int &in) {repeat {repeat_same int}}", ...);
```

ファクトリ関数に渡されるリストバッファは、次のルールに従って値が格納されます：

- パターンが `repeat` を期待する場合、バッファにはこの後に続く繰り返し値の数を示す32ビット整数が含まれます。
- パターンが `?` を期待する場合、バッファにはこの後に続く値の typeId を表す32ビット整数が含まれます。
- パターンが参照型を期待する場合、バッファにはオブジェクトへのポインタが含まれます。
- パターンが値型を期待する場合、バッファにはオブジェクトそのものが含まれます。
- バッファ内のすべての値は、バッファに配置される値のサイズが32ビット未満でない限り、32ビット境界にアライメントされます。

リストファクトリの実装例については [配列アドオン](./doc_addon#array-テンプレートオブジェクト) と [辞書アドオン](./doc_addon#dictionary-オブジェクト) を参照してください。

### Addref と Release の振る舞い (Addref and release behaviours)

```cpp
void CRef::Addref()
{
    // 参照カウンターを増加させる
    refCount++;
}

void CRef::Release()
{
    // 参照カウンターを減らし、0に達したら削除する
    if( --refCount == 0 )
        delete this;
}

// addref/release の振る舞いを登録する
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_ADDREF, "void f()", asMETHOD(CRef,AddRef), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_RELEASE, "void f()", asMETHOD(CRef,Release), asCALL_THISCALL); assert( r >= 0 );
```

もしこのオブジェクトのインスタンスが複数のスレッド間で共有される場合、アトミック命令を使用してインクリメントとデクリメントを行い、参照カウンターがスレッドセーフであることを保証するのを忘れないでください。

参照: [マルチスレッド](./doc_adv_multithread)

### 参照カウントなしの参照型 (Reference types without reference counting)

アプリケーションが参照カウントに基づかない独自のメモリ管理を提供する場合、RegisterObjectType の呼び出し時にフラグ `asOBJ_NOCOUNT` を指定することで、addref と release の振る舞いなしで型を登録することが可能です。

```cpp
// 参照型の登録
r = engine->RegisterObjectType("ref", 0, asOBJ_REF | asOBJ_NOCOUNT); assert( r >= 0 );
```

addref と release の振る舞いがない場合、アプリケーションは、グローバル変数などの場所でスクリプトエンジンから依然として参照されている可能性のあるオブジェクトを誤って破壊しないように注意しなければなりません。

オブジェクトがスクリプトエンジンの存在期間と同じ長さだけ確実に存続し続けない限り、エンジンプロパティ [asEP_DISALLOW_GLOBAL_VARS](./doc_adv_custom_options#言語の変更-language-modifications) を用いてグローバル変数を無効にすることを検討した方が良い場合があります。これにより、アプリケーションがオブジェクトへの参照がどこに保持されているかを知るのが非常に容易になります。すべてのグローバル変数を無効にする代替案として、オブジェクト型への参照を保存する可能性のあるグローバル変数のみを選択的に不許可にすることもできます。これは、スクリプトのビルド後にコンパイルされたグローバル変数を列挙（`GetGlobalVarCount` など）し、ユーザーが含めるべきでない変数を含めていた場合にエラーを出すことによって行うことができます。

### インスタンス化不可能な参照型の登録 (Registering an uninstantiable reference type)

スクリプトによるインスタンス化はできないが、スクリプトから対話できるような型を登録することが有用な場合があります。これを行うには、型を通常の参照型として登録しますが、ファクトリの振る舞いの登録は省略します。その後、アプリケーションによって作成されたオブジェクトにスクリプトがオブジェクトハンドルを介してアクセスできるようにするグローバルプロパティや関数を登録することができます。

これは、アプリケーションが利用可能なオブジェクトの数が限られており、新しいオブジェクトを作成させたくない場合（シングルトンやプールされたオブジェクトなど）に使用されます。

---

## 値型の登録 (Registering a value type)

値型を登録する際には、AngelScript がその型にどの程度のスペースが必要かを知るために、型のサイズを指定する必要があります。
型に特別な処理が必要ない場合、すなわち維持する必要があるポインタやその他のリソース参照が含まれていない場合、型はフラグ `asOBJ_POD` で登録することができます。この場合、AngelScript はデフォルトコンストラクタ、代入の振る舞い、またはデストラクタを必要とせず、組み込みのプリミティブ型と同様にこれらのケースを自動的に処理することができます。

この型を、ネイティブの呼び出し規約を使用する登録済み関数に対して値渡しや値の戻り値として使用する予定がある場合は、アプリケーションにおける [実際の型の実装方法](#値型とネイティブ呼び出し規約-value-types-and-native-calling-conventions) を AngelScript に通知する必要があります。ただし、ジェネリック呼び出し規約のみを使用する計画がある場合、またはこれらの型を値渡ししない場合は、それについて心配する必要はありません。

```cpp
// コンテンツの特別な管理を必要としないプリミティブ型を登録する
r = engine->RegisterObjectType("pod", sizeof(pod), asOBJ_VALUE | asOBJ_POD); assert( r >= 0 );

// 適切に初期化および非初期化されなければならないクラスを登録する
r = engine->RegisterObjectType("val", sizeof(val), asOBJ_VALUE); assert( r >= 0 );
```

値型の例については、[標準文字列](./doc_addon#string-オブジェクト) や、[数学アドオン](./doc_addon#math-関数) を参照してください。
値型のより具体的な例については、[ジェネリックなハンドル型](./doc_adv_generic_handle) を参照してください。
型が他の型のメンバである時に循環参照を形成する可能性がある場合の対応については、[ガベージコレクション対応オブジェクト](./doc_gc_object) を参照してください。

### コンストラクタとデストラクタ (Constructor and destructor)

コンストラクタまたはデストラクタが必要な場合は、次のように登録する必要があります：

```cpp
void Constructor(void *memory)
{
  // placement-new 演算子を用いてオブジェクトコンストラクタを呼び出し、
  // 事前割り当てされたメモリを初期化する
  new(memory) Object();
}

void Destructor(void *memory)
{
  // オブジェクトのデストラクタを呼び出してメモリを非初期化する
  ((Object*)memory)->~Object();
}

// 振る舞いを登録する
r = engine->RegisterObjectBehaviour("val", asBEHAVE_CONSTRUCT, "void f()", asFUNCTION(Constructor), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("val", asBEHAVE_DESTRUCT, "void f()", asFUNCTION(Destructor), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

テンプレートの実装を作成する場合であっても、ラッパー関数には必ず一意の名前か名前空間を使用するように注意してください。そうしないと、AngelScript にラッパーを登録する際にリンカーが誤った関数のアドレスを取得してしまい、予期しない動作が発生する原因となります。

事前割り当てされたメモリブロックを初期化するために使用される placement new 演算子を宣言するために、`<new>` ヘッダーをインクルードする必要があるかもしれないことに注意してください。

#### リストコンストラクタ (List constructor)

リストコンストラクタは、参照型用の[リストファクトリ関数](#リストファクトリ関数-list-factory-function)と似ています。コンストラクタは全く同じ方法で初期化リストのバッファへのポインタを受け取り、期待されるリストパターンも同じ方法で登録されるべきです。違いは、リストコンストラクタは他の通常の[コンストラクタ](#コンストラクタとデストラクタ-constructor-and-destructor)と同様に、メソッドのように登録される必要がある点です。

リストコンストラクタの登録例：

```cpp
engine->RegisterObjectBehaviour("vector3", asBEHAVE_LIST_CONSTRUCT, "void f(int &in) {float, float, float}", ...);
```

リストコンストラクタを備えた値型の例については [complex math アドオン](./doc_addon_math) を参照してください。

### 値型とネイティブ呼び出し規約 (Value types and native calling conventions)

ネイティブの呼び出し規約を用いて、ある型がアプリケーションとの間で値渡しされる場合、C++ におけるその本当の型を AngelScript に通知することが重要です。そうしないと、AngelScript は、C++ がパラメータや戻り値においてその型をどのように正確に処理しているかを判断できなくなります。

実際の型についての情報を伝えるフラグが提供されておらず、プラットフォーム上で AngelScript がそれを必要とする場合、「Don't support passing/returning type 'MyType' by value to application in native calling convention on this platform (このプラットフォームでのネイティブ呼び出し規約では、型 'MyType' のアプリケーションへの値渡し/値戻しをサポートしていません)」というエラーメッセージが表示されます。

C++ における実際の型を AngelScript に通知するには、テンプレート関数 [asGetTypeTraits](#asGetTypeTraits) を優先して使用すべきです。これは [RegisterObjectType](#asIScriptEngine::RegisterObjectType) に `asOBJ_VALUE` と共に渡すべきフラグのほとんどを自動的に決定してくれるからです。

```cpp
// C++11 の場合、型は GetTypeTraits を使用して登録できます
r = engine->RegisterObjectType("complex", sizeof(complex), asOBJ_VALUE | asGetTypeTraits<complex>()); assert( r >= 0 );
```

以下のフラグが `asGetTypeTraits` によってカバーされています：

| フラグ | 説明 |
| --- | --- |
| `asOBJ_APP_CLASS` | C++の型はクラス、構造体、または共用体である |
| `asOBJ_APP_CLASS_CONSTRUCTOR` | C++の型はデフォルトコンストラクタを持つ |
| `asOBJ_APP_CLASS_DESTRUCTOR` | C++の型はデストラクタを持つ |
| `asOBJ_APP_CLASS_ASSIGNMENT` | C++の型はコピー代入演算子を持つ |
| `asOBJ_APP_CLASS_COPY_CONSTRUCTOR` | C++の型はコピーコンストラクタを持つ |
| `asOBJ_APP_PRIMITIVE` | C++の型はC++プリミティブだが、floatやdoubleではない |
| `asOBJ_APP_FLOAT` | C++の型はfloatまたはdoubleである |
| `asOBJ_APP_ARRAY` | C++の型は配列である |

C++ クラス内で `= default` として宣言されている場合は、コンストラクタ、デストラクタ、代入演算子、またはコピーコンストラクタに対するフラグを含めないでください。

一部のプラットフォームでは、ネイティブ呼び出し規約が正常に機能するために、クラスやそのメンバについて `asGetTypeTraits` だけでは決定できないさらなる知識を必要とする場合があります。フラグが必要かどうかはコンパイラとターゲットプラットフォームに依存しますが、フラグが不要な場合、AngelScript は単にそれらを無視するため、情報を提供して害になることはありません。

誤ったフラグが使用されると、これらの型を値で渡したり返したりする登録済みオブジェクトを呼び出す際に予期しない動作が発生する可能性があるため、正しいフラグを通知するように注意してください。一般的な問題は、スタックの破損や不正なメモリアクセスです。場合によっては、関数が期待される値を返さないなど、より静かなエラーに直面することもあり、これは検出が難しくなることがあります。

AngelScript では、最も一般的なバリアント（変種）をカバーする情報をアプリケーションに提供させることができます。例えば、クラス全体をすべてのメンバが整数（または非浮動小数点のプリミティブ）であるかのように扱うよう指示したり、すべてのメンバが float であるかのように扱うよう指示したりすることができます。また、クラスが従来のデフォルトコンストラクタやコピーコンストラクタ以外により多くのコンストラクタを持つかどうかを通知することも可能です。この最後の事項は通常、デフォルトおよびコピーコンストラクタが `= default` 化されている場合にのみ重要性を持ちます。

| フラグ | 説明 |
| --- | --- |
| [asOBJ_APP_CLASS_MORE_CONSTRUCTORS](#asOBJ_APP_CLASS_MORE_CONSTRUCTORS) | C++クラスはデフォルトやコピーコンストラクタ以外にパラメータを持つコンストラクタを持つ |
| [asOBJ_APP_CLASS_ALLINTS](#asOBJ_APP_CLASS_ALLINTS) | C++クラスのメンバはすべてが整数であるかのように扱うことができる |
| [asOBJ_APP_CLASS_ALLFLOATS](#asOBJ_APP_CLASS_ALLFLOATS) | C++クラスのメンバはすべてがfloatまたはdoubleであるかのように扱うことができる |
| [asOBJ_APP_CLASS_ALIGN8](#asOBJ_APP_CLASS_ALIGN8) | C++クラスは8バイトアライメントを必要とするメンバ（例：double）を含んでいる |
| [asOBJ_APP_CLASS_UNION](#asOBJ_APP_CLASS_UNION) | C++クラスは共用体をメンバとして含んでいる |

以下は、フラグの使用法を分かりやすく示すためのいくつかの例です：

```cpp
// パラメータ付きコンストラクタが存在するため、フラグ asOBJ_APP_CLASS_MORE_CONSTRUCTORS が使用されるべきです
struct A
{
	A() = default;
	A(const A& o) = default;
	A(float x, float y) { this->x = x; this->y = y; }
};

// 構造体は非浮動小数点プリミティブのみを含むため、asOBJ_APP_CLASS_ALLINTS が使用されるべきです
struct B
{
	int a;
	void *b;
};

// 構造体はfloatのみを含むため、asOBJ_APP_CLASS_ALLFLOATS が使用されるべきです
struct C
{
	float x,y,z;
};

// 構造体はdoubleのみを含むため、フラグ asOBJ_APP_CLASS_ALLFLOATS および asOBJ_APP_CLASS_ALIGN8 が使用されるべきです
struct D
{
	double x,y;
};

// 構造体はfloatの共用体を含むため、フラグ asOBJ_APP_CLASS_ALLFLOATS および asOBJ_APP_CLASS_UNION が使用されるべきです
struct E
{
	union {
		float x, s;
	};
	union {
		float y, t;
	};
};
```

各システムの ABI に対する深い知識が必要となるため、どのフラグがいつ使用されるべきかを正確に説明することは困難です。そのため、これらのフラグを本当に使用する必要がある場合は、スクリプトエンジンによって関数が正しく呼び出されていることを保証するための十分なテストを必ず実行してください。もしこれらのフラグのいずれも機能せず、フラグなしで動作するようにクラス設計も変更できないのであれば、残された唯一の選択肢は、（好ましくは [自動ラッパーアドオン](./doc_addon_autowrap) を伴う）ジェネリック呼び出し規約を使用することです。

#### C++11 および asGetTypeTraits をサポートしないコンパイラ向けの設定 (For compilers that don't support C++11 and asGetTypeTraits)

もしあなたのコンパイラが C++11 の機能に対応していない場合、`asGetTypeTraits` 関数は使用できません。この場合、正しいフラグを手動で追加する以外の選択肢はありません。

なお、これらのフラグは、型がスクリプト言語内でどのように振る舞うかを表すものではなく、ホストアプリケーションにおける実際の型が何であるかを表すものであることに注意してください。したがって、スクリプト言語内ではプリミティブ型として振る舞わせたい C++ クラスを登録したい場合であっても、依然として `asOBJ_APP_CLASS` フラグを使用すべきです。クラスがコンストラクタ、デストラクタ、代入演算子、またはコピーコンストラクタを持つことを識別するフラグについても同様です。これらのフラグは、クラスに対応する機能が存在することを AngelScript に伝えるものであり、スクリプト言語内の型がそれらの振る舞いを持つべきであると伝えるものではありません。

クラスのメンバの1つが対象の処理を必要とする型である場合、C++ コンパイラがいくつかの関数を自動的に提供することがあるという点に注意してください。そのため、登録したい型そのものには明示的に宣言されたデフォルトコンストラクタがない場合でも、`asOBJ_APP_CLASS_CONSTRUCTOR` フラグと共に型を登録する必要性が出てくる場合があります。他の関数（デストラクタなど）についても同様です。

クラス型のために、5つのフラグの組み合わせそれぞれに対応するより短い形式のフラグも用意されています。これらは `asOBJ_APP_CLASS_CDAK` のような形式であり、末尾の文字の有無によって、コンストラクタ、デストラクタ、および/または代入の振る舞いなどが利用可能かどうかが決まります。例えば、[asOBJ_APP_CLASS_CDAK](#asOBJ_APP_CLASS_CDAK) は `asOBJ_APP_CLASS | asOBJ_APP_CLASS_CONSTRUCTOR | asOBJ_APP_CLASS_DESTRUCTOR | asOBJ_APP_CLASS_ASSIGNMENT | asOBJ_APP_CLASS_COPY_CONSTRUCTOR` として定義されています。

```cpp
// アプリケーションへ値として渡される complex 型を登録する
r = engine->RegisterObjectType("complex", sizeof(complex), asOBJ_VALUE | asOBJ_APP_CLASS_CDAK); assert( r >= 0 );
```

---

## 演算子の振る舞いの登録 (Registering operator behaviours)

AngelScript がアプリケーション登録済みの型をどのように処理すべきかを知るためには、いくつか特定の振る舞い（例えばメモリ管理に関するもの）を登録する必要があります。

メモリ管理の振る舞いについては、[参照型の登録](#参照型の登録-registering-a-reference-type) および [値型の登録](#値型の登録-registering-a-value-type) に記述されています。

その他の高度な振る舞いについては [高度なアプリケーションインターフェース (Advanced application interface)](./doc_advanced_api) で説明されています。

ほとんどの振る舞いは通常のクラスメソッドとして実装されますが、コンパイラが理解できるように特定（事前定義済み）の名前が付けられている必要があります。

### 演算子のオーバーロード (Operator overloads)

AngelScript では、すべての演算子オーバーロードは [事前定義された名前を持つクラスメソッド](./doc_script_class_ops) として実装されます。これは、クラスメソッドとグローバル関数の両方が使用可能な C++ とは異なります。特に、二項演算子（2つのオペランドを受け取るもの）は、通常は一方がクラスメソッドとして実装され、オペランドの順序が逆になったパターン向けにはグローバル関数として実装されます。

C++ での演算子オーバーロードを登録するには、[関数の登録](./doc_register_func) で説明した方法を使用します。

演算子オーバーロードを登録する方法の例：

```cpp
class MyClass
{
  ...

  // 演算子 'MyClass - int' はメソッドとして実装されている
  MyClass operator-(int) const;

  // 演算子 'int - MyClass' はグローバル関数として実装されている
  static MyClass operator-(int, const MyClass &);
}

void RegisterMyClass(asIScriptEngine *engine)
{
  // 演算子 'MyClass - int' の登録
  engine->RegisterObjectMethod("MyClass", "MyClass opSub(int) const", asMETHODPR(MyClass, operator-, (int) const, MyClass), asCALL_THISCALL); 

  // 演算子 'int - MyClass' の登録
  engine->RegisterObjectMethod("MyClass", "MyClass opSub_r(int) const", asFUNCTIONPR(operator-, (int, const MyClass &), MyClass), asCALL_CDECL_OBJLAST);
}
```

---

## オブジェクトメソッドの登録 (Registering object methods)

クラスメソッドは `RegisterObjectMethod` の呼び出しによって登録されます。非仮想メソッドと仮想メソッドは両方とも同じ方法で登録されます。

静的 (Static) なクラスメソッドは実際にはグローバル関数であるため、オブジェクトメソッドとしてではなく [グローバル関数として登録](./doc_register_func) されるべきです。

```cpp
// クラスメソッドの登録
void MyClass::ClassMethod()
{
  // 何かを行う
}

r = engine->RegisterObjectMethod("mytype", "void ClassMethod()", asMETHOD(MyClass,ClassMethod), asCALL_THISCALL); assert( r >= 0 );
```

また、オブジェクトへのポインタを受け取るグローバル関数を、クラスメソッドであるかのように登録することも可能です。これを利用すると、C++ クラス自体の実装を変更することなく、AngelScript 経由でアクセスされた時のクラスの機能を拡張することができます。

```cpp
// グローバル関数をオブジェクトメソッドとして登録する
void MyClass_MethodWrapper(MyClass *obj)
{
  // オブジェクトにアクセス
  obj->DoSomething();
}

r = engine->RegisterObjectMethod("mytype", "void MethodWrapper()", asFUNCTION(MyClass_MethodWrapper), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

マクロの仕組みの詳細は [関数の登録 (Registering a function)](./doc_register_func) を参照してください。

### コンポジットメンバ (Composite members)

登録されるアプリケーションクラスがコンポジション（合成）を使用している場合、次のようにコンポジットメンバ（複合された包含オブジェクト等のメンバ）のメソッドを登録することが可能です：

```cpp
struct Component
{
  int DoSomething();
};

struct Object
{
  Component *comp;
};

r = engine->RegisterObjectMethod("object", "int DoSomething()", asMETHOD(Component, DoSomething), asCALL_THISCALL, 0, asOFFSET(Object, comp), true); assert( r >= 0 );
```

最後のパラメータは、コンポジットメンバに到達するためにポインタのデリファレンスが必要であることを示しています。コンポジットメンバがポインタではなく直接構造体にインライン展開されている場合は、このパラメータは `false` に設定されるべきです。

---

## オブジェクトプロパティの登録 (Registering object properties)

クラスのメンバ変数は、メソッドを呼び出すことなくスクリプトから直接アクセスできるようにするために、[RegisterObjectProperty](#asIScriptEngine::RegisterObjectProperty) を使用して登録することができます。

```cpp
struct MyStruct
{
  int a;
};

r = engine->RegisterObjectProperty("mytype", "int a", asOFFSET(MyStruct,a)); assert( r >= 0 );
```

クラスのメンバが間接的である場合（すなわち、ヒープ上に割り当てられたメンバへのポインタをクラスが保持している場合）、スクリプトエンジンに対してメンバにアクセスするためのデリファレンスが必要であることを伝えるため、`&` を使用してプロパティを登録することが可能です。

```cpp
struct MyStruct
{
  OtherStruct *a;
};

r = engine->RegisterObjectProperty("mytype", "othertype &a", asOFFSET(MyStruct,a)); assert( r >= 0 );
```

もちろん、アプリケーションは、スクリプトからアクセスされる可能性のある期間中、そのポインタがずっと有効であることを保証しなければなりません。

C++ においては、参照として宣言されたクラスメンバのアドレスを取得することはできないということに留意してください。なぜなら、この場合の `&` 演算子は、そのメンバが参照している実際のオブジェクトを対象にするからです。この理由から、参照として宣言されたメンバのオフセットを決定するために `asOFFSET` を使用することはできません。その代わり、隣接するメンバからの相対的なオフセットを手動で計算することは可能です。その際は、コンパイラによって追加されるバイトアライメントやパディングの可能性の検証を忘れないでください。

### コンポジットメンバのプロパティ (Composite members)

登録されるアプリケーションクラスがコンポジションを使用している場合、次のようにコンポジットメンバのプロパティを登録することが可能です：

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

最後のパラメータは、コンポジットメンバのプロパティに到達するためにポインタのデリファレンスが必要であることを示しています。コンポジットメンバがインラインで保持されている場合は、そのパラメータを `false` に設定するべきです。

### プロパティアクセサ (Property accessors)

[プロパティアクセサ](./doc_script_class_prop)を通じてプロパティを公開することも可能です。これはプロパティ値の取得や設定を行うためのもので、`get_` と `set_` のプレフィックスと、関数デコレータ `property` を持つクラスメソッドのペアです。これらのメソッドは [RegisterObjectMethod](./doc_register_func) で登録されるべきです。これは、プロパティのオフセットが決定できない場合や、プロパティの型がスクリプトに登録されておらず（例：`char*` から `string` への）何らかの変換が発生しなければならない場合に特に有用です。

アプリケーションクラスが C++ の配列をメンバとして含んでいる場合、登録された型を AngelScript に合わせて複雑なマッチングを試みるよりも、[インデックス付きプロパティアクセサ](./doc_script_class_prop) を通じて配列を公開する方が有利な場合があります。これを行うには、配列へのアクセスを中継する簡単なプロキシ関数をいくつか作成することができます。

> **Note**: 仮想プロパティの動作は、エンジンプロパティ [asEP_PROPERTY_ACCESSOR_MODE](./doc_adv_custom_options_lang_mod) を用いてカスタマイズできます。

```cpp
struct MyStruct
{
  int array[16];
};

// 中継するためのプロキシをいくつか記述します
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

// メンバメソッドとしてプロキシ関数を登録する
r = engine->RegisterObjectMethod("mytype", "int get_array(uint) property", asFUNCTION(MyStruct_get_array), asCALL_CDECL_OBJLAST); assert( r >= 0 );
r = engine->RegisterObjectMethod("mytype", "void set_array(uint, int) property", asFUNCTION(MyStruct_set_array), asCALL_CDECL_OBJLAST); assert( r >= 0 );
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_register_type.html
