---
title: "アプリケーションへのオブジェクトハンドル (Object handles to the application)"
---

AngelScript においてオブジェクトハンドルは、オブジェクトへの参照カウント付きポインタです。スクリプト内では、オブジェクトを値渡しではなく参照渡しで受け渡しするために使用されます。アプリケーションの型がどのように登録されているかによって、その型がハンドルをサポートするかどうかが決まります。

参照: [型の登録](./doc_register_type)、スクリプト言語における [スクリプトのハンドル](./doc_script_handle)

## 関数内での参照カウンターの管理 (Managing the reference counter in functions)

オブジェクトハンドルがアプリケーションからスクリプトエンジンへ値渡しされる時、その逆の場合も含め、その参照は適切に計上されなければなりません。これは、アプリケーションがそれ以上必要としなくなった時に、パラメータとして受け取ったオブジェクトハンドルを解放しなければならないことを意味します。また、スクリプトエンジンに返されるオブジェクトハンドルの参照カウンターをインクリメントしなければならないことも意味します。これは [ジェネリック呼び出し規約](./doc_generic) にも適用されます。

オブジェクトを作成してスクリプトエンジンに返す関数は次のようになります：

```cpp
// "obj@ CreateObject()" として登録されます
obj *CreateObject()
{
  // コンストラクタはすでに参照カウントを 1 に初期化します
  return new obj();
}
```

スクリプトからオブジェクトハンドルを受け取りグローバル変数に格納する関数は次のようになります：

```cpp
// "void StoreObject(obj@)" として登録されます
obj *o = 0;
void StoreObject(obj *newO)
{
  // 古いオブジェクトハンドルを解放します
  if( o ) o->Release();

  // 新しいオブジェクトハンドルを格納します
  o = newO;
}
```

以前に格納されたオブジェクトハンドルを取得する関数は次のようになります：

```cpp
// "obj@ RetrieveObject()" として登録されます
obj *RetrieveObject()
{
  // 返されるハンドルに対して参照カウンターをインクリメントします
  if( o ) o->AddRef();

  // 以前に格納されたハンドルがない場合は null を返してもかまいません
  return o;
}
```

パラメータにオブジェクトハンドルを受け取るが格納しない関数は次のようになります：

```cpp
// "void DoSomething(obj@)" として登録されます
void DoSomething(obj *o)
{
  // オブジェクトを使い終わったら解放しなければなりません
  if( o ) o->Release();
}
```

## 自動ハンドルで簡略化する (Auto handles can make it easier)

アプリケーションは自動ハンドル (`@+`) を使用して、参照カウンターを管理する手間の一部を軽減することができます。AngelScript に関数やメソッドを登録する際、AngelScript が自動的に管理すべきオブジェクトハンドルにプラス記号を追加します。パラメータに対して AngelScript は関数が返した後に参照を解放し、戻り値に対して AngelScript は返されたポインタの参照をインクリメントします。パラメータが解放される前に戻り値の参照がインクリメントされるため、関数がパラメータの1つを返すことも可能です。

```cpp
// "obj@+ ChooseObj(obj@+, obj@+)" として登録されます
obj *ChooseObj(obj *a, obj *b)
{
  // 自動ハンドルのため AngelScript が自動的に参照カウンターを管理します
  return some_condition ? a : b;
}
```

自動ハンドルは [ジェネリック呼び出し規約](./doc_generic) でも同様に機能します。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_obj_handle.html
