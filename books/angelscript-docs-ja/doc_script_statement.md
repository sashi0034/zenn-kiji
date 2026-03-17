---
title: "ステートメント (Statements)"
---

## 変数宣言 (Variable declarations)

```angelscript
int var = 0, var2 = 10;
object@ handle, handle2;
const float pi = 3.141592f;
object obj(23), obj2 = object(23);
array<int> arr, arr2 = {1,2,3};
```

変数はステートメントブロック内またはサブブロック内で使用される前に宣言しなければなりません。変数が宣言されたステートメントブロックを抜けると、変数は無効になります。

変数は初期式あり、またはなしで宣言できます。初期式ありで宣言する場合、式は変数の型と互換性のある型に評価される必要があります。

任意の数の変数をコンマで区切って同じ行に宣言することができ、すべての変数は同じ型になります。

変数は `const` として宣言できます。その場合、変数の値は初期化後に変更できません。

初期値なしで宣言されたプリミティブ型の変数はランダムな値を持ちます。ハンドルやオブジェクトなどの複合型の変数はデフォルト値で初期化されます。ハンドルの場合は `null`、オブジェクトの場合はオブジェクトのデフォルトコンストラクタで定義されているものです。

参照: [自動型宣言](./doc_script_datatypes)

## 式ステートメント (Expression statement)

```angelscript
a = b;  // 変数代入
func(); // 関数呼び出し
```

任意の [式](./doc_script_expr) を単独でステートメントとして行に配置することができます。これは通常、変数代入や重要な値を返さない関数呼び出しに使用されます。

すべての式ステートメントはセミコロン `;` で終わらなければなりません。

## 条件分岐 (Conditions: if / if-else / switch-case)

```angelscript
if( condition ) 
{
  // 条件が true の時に何かを行います
}

if( value < 10 ) 
{
  // value が 10 未満の時に何かを行います
}
else
{
  // value が 10 以上の時に別のことを行います
}
```

if ステートメントは特定の条件に基づいてロジックの一部を実行するかどうかを決定するために使用されます。条件式は常に `true` または `false` に評価しなければなりません。

複数の `if-else` ステートメントを連鎖させることが可能で、その場合各条件は1つが `true` と判明するまで順次評価されます。

```angelscript
switch( value )
{
case 0:
  // value が 0 の場合に何かを行い、その後抜けます
  break;

case 2:
case constant_value:
  // value が 2 または constant_value と等しい場合に実行されます
  break;

default:
  // value がいずれのケースとも等しくない場合に実行されます
}
```

異なる結果に繋がるべき多くの異なる結果を持つ整数（符号あり、符号なし）式がある場合、switch-case は条件を実装するための最善の選択です。特にすべてのケース値が近い数値の場合、一連の if よりも大幅に高速です。

各 case は次のケースに続けたい場合を除いて、break ステートメントで終了すべきです。

## ループ (Loops: while / do-while / for / foreach)

```angelscript
// ロジックが実行される前に条件がチェックされるループ
int i = 0;
while( i < 10 )
{
  // 何かを行います
  i++;
}

// ロジックが実行された後に条件がチェックされるループ
int j = 0;
do 
{
  // 何かを行います
  j++;
} while( j < 10 );
```

`while` と `do-while` の両方において、ループを続けるかどうかを決定する式は true または false に評価しなければなりません。

```angelscript
// 条件がロジックの実行前にチェックされるよりコンパクトなループ
for( int n = 0; n < 10; n++ ) 
{
  // 何かを行います
}
```

`for` ループは `while` ループのよりコンパクトな形式です。ステートメントの最初の部分（最初の `;` まで）はループが始まる前に1回だけ実行されます。`for` ループ内でのみ可視の変数をここで宣言することも可能です。2番目の部分はループが実行されるために満たされなければならない条件です。ここで空の式は常に true に評価されます。最後の部分はループ内のロジックの後に実行されます。

`for` ループでは `,` で区切って複数の変数を宣言することができます。同様に、最後の部分で `,` で区切ることで複数のインクリメント式を使用することができます。

```angelscript
// foreach ループはコンテナオブジェクトの各要素を反復処理します
dictionary dict = {...};
int count = 0;
int sum = 0;
foreach( auto val, auto key : dict )
{
   count++;
   sum += int(val);
   dict[key] = 0;
}
double average = double(sum)/count;
```

`foreach` はコンテナオブジェクト用の特別なループで、コンテナの各要素を反復処理します。コンテナで使用できる値の型と数はコンテナの型によって異なります。`foreach` ループをサポートする各コンテナ型には、コンパイラが要素の反復処理のロジックを構築できるようにするためのメソッドのセットがあります。

`foreach` ループ内でコンテナが変更された場合（例えば要素が削除または追加された場合）、動作は未定義です。

参照: [foreach ループ演算子](./doc_script_class_ops)

## ループ制御 (Loop control: break / continue)

```angelscript
for(;;) // 無限ループ
{
  // 何かを行います

  // 条件が true の時ループを終了します
  if( condition )
    break;
}
```

`break` は最も内側のループ文または switch 文を終了します。

```angelscript
for(int n = 0; n < 10; n++ )
{
  if( n == 5 )
    continue;

  // 0 から 9 までのすべての値に対して何かを行いますが、値 5 を除きます
}
```

`continue` は最も内側のループ文の次のイテレーションにジャンプします。

## return ステートメント (Return statement)

```angelscript
float valueOfPI()
{
  return 3.141592f; // 値を返します
}
```

`void` 以外の戻り値の型を持つすべての関数は、式が関数の戻り値の型と同じデータ型に評価される `return` ステートメントで終了しなければなりません。`void` として宣言された関数は式なしの `return` ステートメントを持つことができます（早期終了のため）。

## ステートメントブロック (Statement blocks)

```angelscript
{
  int a; 
  float b;

  {
    float a; // 外の変数の宣言をオーバーライドしますが、
             // このブロックのスコープ内でのみです

    // 外のブロックの変数は依然として可視です
    b = a;
  }

  // a は再び整数変数を参照します
}
```

ステートメントブロックはステートメントの集合です。各ステートメントブロックは独自の可視スコープを持つため、ステートメントブロック内で宣言された変数はブロックの外から見えません。

## try-catch ブロック (Try-catch blocks)

```angelscript
{
  try
  {
    DoSomethingThatMightThrowException();

    // 例外がスローされた場合、これは実行されません
  }
  catch
  {
    // 例外がスローされた場合、これが実行されます
  }
}
```

例外をスローする可能性のあるコードを実行していて、その例外をキャッチしてスクリプトを単に中断するのではなく例外とともに続行したい場合は、try-catch ブロックを使用することができます。

例外はさまざまな理由で発生します。例えば、初期化されていないハンドルの null ポインタへのアクセス、ゼロ除算、またはアプリケーション登録関数からスローされた例外などです。一部のケースでは、スクリプトが意図的に例外を発生させて一部の実行を中断します。

参照: [例外の標準ライブラリ](./doc_script_stdlib)

## using namespace ステートメント (Using namespace)

ステートメントブロック内で `using namespace` を宣言することができます。これを行うと、そのブロック内の後続のすべてのステートメントは指定された名前空間でもシンボルを検索します。

```angelscript
namespace test
{
  void func() {}
}
void main()
{
  test::func(); // この呼び出しは名前空間を明示的に指定しなければなりません
  {
    using namespace test;
    func(); // この呼び出しは名前空間を暗黙的に検索します
  }
  test::func(); // ここはステートメントブロックの後で、再び名前空間を明示的に指定しなければなりません
}
```

参照: [グローバルの 'using namespace'](./doc_script_global)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_statements.html
