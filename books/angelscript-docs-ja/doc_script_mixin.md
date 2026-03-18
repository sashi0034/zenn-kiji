---
title: "ミックスインクラス (Mixin class)"
---

AngelScript は単一継承のみをサポートしているため、[多重継承](./doc_script_class#継承とポリモーフィズム-inheritance-and-polymorphism) を使って共通機能をまとめることができません。そのため、複数のクラスで同一のコードを記述しなければならない場面があります。このような場合に、コードの重複を避けて再利用性を高めるための仕組みが **ミックスインクラス** です。

ミックスインクラスを使用すると、複数のクラス宣言に挿入可能な「クラスの一部」を定義できます。ミックスインクラス自体は独立した型ではなく、直接インスタンス化することはできません。

ミックスインクラスがクラス宣言にインクルードされると、ミックスインクラスで宣言されたプロパティとメソッドは自動的にクラスに複製されます。

```cs
// ミックスインクラスを宣言します
mixin class MyMixin
{
  void SomeMethod() { property++; }
  int property;
}

// ミックスインクラスをクラスにインクルードして
// メソッドとプロパティを受け取ります
class MyClass : MyMixin
{
  int OtherMethod()
  {  
    SomeMethod();
    return property;
  }
}
```

すでにクラス側で明示的に宣言されているプロパティやメソッドがある場合、それらはミックスインから上書き（再インクルード）されません。これを利用して、ミックスインでデフォルトの実装を提供し、必要に応じてインクルード先のクラスで個別にオーバーライドすることが可能です。

ミックスインクラスから取り込まれたメソッドは、インクルードした側のクラスのコンテキストでコンパイルされます。そのため、ミックスイン側のメソッドから、インクルード先のクラスが提供している（が、ミックスイン自体には宣言されていない）プロパティや他のメソッドを参照することも可能です。

```cs
mixin class MyMixin
{
  void MethodA() { print("Default behaviour"); } 
  void MethodB() { property++; }
}

class MyClass : MyMixin
{
  // MethodA のデフォルト動作をオーバーライドします
  void MethodA() { print("Overridden behaviour"); }

  // MethodB で使用されるプロパティを宣言します
  int property;
}
```

ミックスインクラスのメソッドは、インクルードされたメソッドが派生クラスに直接実装されたかのように、基底クラスから継承されたメソッドをオーバーライドします。一方、ミックスインクラスのプロパティは、プロパティが既に基底クラスから継承されている場合はインクルードされません。

```cs
class MyBase
{
  void MethodA() { print("Base behaviour"); }
  int property;
}

mixin class MyMixin
{
  void MethodA() { print("Mixin behaviour"); }
  float property;
}

// 基底クラスから継承してミックスインをインクルードします
// MyClass は基底クラスのプロパティとミックスインクラスのメソッドを持ちます
class MyClass : MyBase, MyMixin
{
}
```

ミックスインクラスには、それをインクルードするスクリプトクラスが実装すべきインターフェースのリストを指定できます。この場合、インターフェースのメソッドの一部をミックスイン側で実装し、残りをスクリプトクラス側で直接実装させるといった柔軟な構成が可能です。

ミックスインクラスは他のクラスから継承することができません。

```cs
interface I 
{
  void a();
  void b();
}

mixin class M : I
{
  // a() のデフォルト実装を提供します
  void a() { print("hello from a"); }

  // b() の実装はスクリプトクラスに任せます
}

class C : M
{
  // a() はミックスインクラスによって実装されています

  // b() はスクリプトクラスによって明示的に実装されなければなりません
  void b() { print("hello from b"); }
}
```

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_mixin.html
