---
title: "演算子オーバーロード (Operator overloads)"
---

スクリプトクラスに対して演算子が使用された際の挙動を定義することができます。必須ではありませんが、適切に使用することでコードの直感性や可読性を高めることができます。

これを **演算子オーバーロード** と呼び、クラス内に特定の名称のメソッドを実装することで実現します。コンパイラは、オーバーロードされた演算子を含む式を解析する際、これらのメソッドを自動的に認識して呼び出しに書き換えます。

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

式 `a == b` は `a.opEquals(b)` または `b.opEquals(a)` に書き換えられ、より一致度の高い方が呼び出されます。`!=` も同様に扱われますが、結果が論理否定されます。`opEquals` メソッドは、コンパイラに認識されるために戻り値の型を `bool` にする必要があります。

比較演算子（`<`, `<=`, `>`, `>=`）は `a.opCmp(b) op 0` または `0 op b.opCmp(a)` に書き換えられます。`opCmp` メソッドは戻り値として `int` を返す必要があります。
- オブジェクト自身より引数の方が **大きい** とみなす場合、負の値を返します。
- **等しい** とみなす場合、0 を返します。
- オブジェクト自身の方が **大きい** とみなす場合、正の値を返します。

等値チェック (`==`) の際、`opEquals` メソッドが見つからない場合、コンパイラは代わりに `opCmp` を探します。そのため、最適化が必要な場合を除き、`opCmp` さえ実装しておけば `opEquals` を個別に実装する必要はありません。

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

代入式 `a op b` は `a.opfunc(b)` に書き換えられます。代入演算子は、次のように連鎖的な代入を可能にするために自身へのハンドルを返すのが一般的です。

```cs
obj &opAssign(const obj &inout other)
{
  // メンバのコピー処理
  ...
  
  // 自分自身を返して連鎖を可能にする
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

式 `type(expr)` がコンパイルされる際、その型が引数一致する [変換コンストラクタ](./doc_script_class#コンストラクタ-class-constructors) を持っていない場合、コンパイラは `expr.opConv()` への書き換えを試みます。戻り値の型が要求される `type` と一致する `opConv` が選択されます。

暗黙的な型変換では、コンパイラはまず対象型の変換コンストラクタ（`explicit` でないもの）を探し、見つからない場合はソース側の `opImplConv` を呼び出そうとします。

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

参照キャストが望ましい場合（つまり同じオブジェクトインスタンスへの異なる型のハンドル）は、代わりに `opCast` メソッドを実装すべきです。コンパイラは `cast<type>(expr)` という式を `expr.opCast()` に書き換え、要求された型のハンドルを返す `opCast` オーバーライドを選択します。暗黙的な参照キャストを許可する場合は、代わりに `opImplCast` を実装することもできます。

```cs
class MyObjA
{
  MyObjB @objB;
  MyObjC @objC;

  // 明示的な参照キャストを可能にします
  MyObjB @opCast() { return objB; }
  const MyObjB @opCast() const { return objB; }

  // 暗黙的な参照キャストを可能にします
  MyObjC @opImplCast() { return objC; }
  const MyObjC @opImplCast() const { return objC; }
}
```

:::note
条件式の中の論理式をコンパイルする際、コンパイラは参照型に対して `bool opImplConv` が実装されていてもそれを使用しません。これは、ハンドル自体を確認しているのか、それとも実際のオブジェクトを確認しているのかが曖昧になるためです。
:::

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
