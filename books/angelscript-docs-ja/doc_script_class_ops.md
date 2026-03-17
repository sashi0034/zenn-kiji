---
title: "演算子オーバーロード (Operator overloads)"
---

スクリプトクラスで演算子が使用された時の動作を定義することができます。ほとんどのスクリプトで必須ではありませんが、コードの可読性を向上させるのに役立ちます。

これを演算子オーバーロードと呼び、特定のクラスメソッドを実装することによって行われます。コンパイラは、オーバーロードされた演算子とスクリプトクラスを含む式をコンパイルする時に、これらのメソッドを認識して使用します。

## 前置単項演算子 (Prefixed unary operators)

| op | opfunc     |
|----|------------|
| `-` | opNeg     |
| `~` | opCom     |
| `++` | opPreInc |
| `--` | opPreDec |

式 `op a` がコンパイルされる時、コンパイラは代わりにそれを `a.opfunc()` として書き換えてコンパイルします。

## 後置単項演算子 (Postfixed unary operators)

| op | opfunc      |
|----|-------------|
| `++` | opPostInc |
| `--` | opPostDec |

式 `a op` がコンパイルされる時、コンパイラは代わりにそれを `a.opfunc()` として書き換えてコンパイルします。

## 比較演算子 (Comparison operators)

| op | opfunc   |
|----|----------|
| `==` | opEquals |
| `!=` | opEquals |
| `<`  | opCmp    |
| `<=` | opCmp    |
| `>`  | opCmp    |
| `>=` | opCmp    |
| `is` | opEquals |
| `!is` | opEquals |

式 `a == b` は `a.opEquals(b)` と `b.opEquals(a)` として書き換えられ、最良の一致が使用されます。`!=` も同様に扱われますが、結果が否定されます。`opEquals` メソッドはコンパイラに認識されるために `bool` を返すよう実装しなければなりません。

比較演算子は `a.opCmp(b) op 0` と `0 op b.opCmp(a)` として書き換えられ、最良の一致が使用されます。`opCmp` メソッドはコンパイラに認識されるために `int` を返すよう実装しなければなりません。メソッドの引数がオブジェクトより大きいとみなされる場合、メソッドは負の値を返す必要があります。等しいとみなされる場合、戻り値は 0 であるべきです。

等値チェックが行われ `opEquals` メソッドが利用できない場合、コンパイラは代わりに `opCmp` メソッドを探します。したがって `opCmp` メソッドが利用可能であれば、最適化の理由を除いて `opEquals` メソッドを実装する必要は実際には必要ありません。

同一性演算子 `is` は、`opEquals` がハンドル `@` を引数として取ることを期待します。これにより、アドレスを比較して、同じ値を持つ2つの異なるオブジェクトではなく同じオブジェクトかどうかを返すことができます。

## 代入演算子 (Assignment operators)

| op | opfunc       |
|----|--------------|
| `=`   | opAssign    |
| `+=`  | opAddAssign |
| `-=`  | opSubAssign |
| `*=`  | opMulAssign |
| `/=`  | opDivAssign |
| `%=`  | opModAssign |
| `**=` | opPowAssign |
| `&=`  | opAndAssign |
| `\|=` | opOrAssign  |
| `^=`  | opXorAssign |
| `<<=` | opShlAssign |
| `>>=` | opShrAssign |
| `>>>=`| opUShrAssign|

代入式 `a op b` は `a.opfunc(b)` として書き換えられ、最良の一致となるメソッドが使用されます。代入演算子は例えば次のように実装できます：

```cs
obj &opAssign(const obj &inout other)
{
  // 適切な代入を行います
  ...
  
  // 複数の代入を連鎖できるよう self へのハンドルを返します
  return this;
}
```

### 自動生成される代入演算子

単一のパラメータを持つ明示的な `opAssign` メソッドが宣言されていない場合、コンパイラは自動的に同じ型のインスタンスの内容をコピーする `opAssign` を生成します。

自動生成された `opAssign` が望ましくない場合は、削除済みとしてフラグを立てることで明示的に除外できます：

```cs
class MyClass
{
  MyClass &opAssign(const MyClass &inout) delete;
}
```

## 二項演算子 (Binary operators)

| op | opfunc | opfunc_r |
|----|--------|----------|
| `+` | opAdd | opAdd_r |
| `-` | opSub | opSub_r |
| `*` | opMul | opMul_r |
| `/` | opDiv | opDiv_r |
| `%` | opMod | opMod_r |
| `**` | opPow | opPow_r |
| `&` | opAnd | opAnd_r |
| `\|` | opOr | opOr_r |
| `^` | opXor | opXor_r |
| `<<` | opShl | opShl_r |
| `>>` | opShr | opShr_r |
| `>>>` | opUShr | opUShr_r |

二項演算子を含む式 `a op b` は `a.opfunc(b)` と `b.opfunc_r(a)` として書き換えられ、最良の一致が使用されます。

## インデックス演算子 (Index operators)

| op | opfunc  |
|----|---------|
| `[]` | opIndex |

式 `a[i]` がコンパイルされる時、コンパイラは代わりにそれを `a.opIndex(i)` として書き換えてコンパイルします。括弧内の複数の引数もサポートされています。

インデックス演算子は [プロパティアクセサー](./doc_script_class_prop) と同様の形式でも実装できます。get アクセサーは `get_opIndex` という名前で、インデックスのための1つのパラメータを持ちます。set アクセサーは `set_opIndex` という名前で、インデックス用の最初のパラメータと新しい値のための2番目のパラメータを持ちます。

```cs
class MyObj
{
  float get_opIndex(int idx) const property { return 0; }
  void set_opIndex(int idx, float value) property { }
}
```

## 関数呼び出し演算子 (Functor operator)

| op | opfunc |
|----|--------|
| `()` | opCall |

式 `expr(arglist)` がコンパイルされ expr がオブジェクトに評価される場合、コンパイラは代わりにそれを `expr.opCall(arglist)` として書き換えてコンパイルします。

## 型変換演算子 (Type conversion operators)

| op | opfunc |
|----|--------|
| `type(expr)` | コンストラクタ、opConv、opImplConv |
| `cast<type>(expr)` | opCast、opImplCast |

式 `type(expr)` がコンパイルされ、型が式の型の引数を取る [変換コンストラクタ](./doc_script_class#コンストラクタ-class-constructors) を持っていない場合、コンパイラは `expr.opConv()` として書き換えようとします。コンパイラは望む型を返す `opConv` を選択します。

暗黙の変換では、コンパイラは一致する引数を取る対象型の変換コンストラクタを探し（`explicit` としてフラグが立っていないものを）、見つからなければ対象型を返すソース型の `opImplConv` を呼び出そうとします。

```cs
class MyObj
{
  double myValue;

  // MyObj を double から暗黙的に作成できるようにします
  MyObj(double v)            { myValue = v; }

  // MyObj を double に暗黙的に変換できるようにします
  double opImplConv() const  { return myValue; }

  // MyObj を int から明示的にのみ作成できるようにします
  MyObj(int v) explicit      { myValue = v; }

  // MyObj を int に明示的にのみ変換できるようにします
  int opConv() const         { return int(myValue); }
}
```

参照キャストが望ましい場合（つまり同じオブジェクトインスタンスへの異なる型のハンドル）は、代わりに `opCast` メソッドを実装すべきです。

参照: [型変換](./doc_script_expr#型変換-type-conversions)、[アプリケーションクラスの継承](./doc_adv_inheritappclass)

## foreach ループ演算子 (Foreach loop operators)

| op | opfunc |
|----|--------|
| foreach の開始 | opForBegin |
| foreach の終了 | opForEnd |
| foreach の次のイテレーション | opForNext |
| foreach の値 | opForValue、opForValue0、opForValue1... |

コンパイラが `foreach` ループをコンパイルしようとする時、コンテナ型に対してメソッドのセットを使用します：

```cs
foreach( auto val, auto key : expr )
{
  ...
}
```

上記は次のように書かれたかのようにコンパイルされます：

```cs
for( auto @container = expr, auto @it = container.opForBegin(); !container.opForEnd(it); @it = container.opForNext(it) )
{
  auto val = container.opForValue0(it);
  auto key = container.opForValue1(it);
  ...
}
```

`opForBegin` が返すイテレータの型は、インデックス付けのための単純な整数でも、イテレーションの追跡のためにより複雑な操作が必要な場合はイテレータクラスでも構いません。

コンテナが単一の値のみをサポートする場合は `opForValue` 演算子を使用できますが、そうでない場合は複数の番号付き `opForValue#` 演算子を使用しなければなりません。

参照: [ステートメント](./doc_script_statement#ループ-loops-while-do-while-for-foreach)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_class_ops.html
