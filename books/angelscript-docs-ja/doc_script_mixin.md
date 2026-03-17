---
title: "ミックスインクラス (Mixin class)"
---

[多重継承](./doc_script_class) が利用できないため、複数のクラスに同一のコードを実装しなければならないことがあります。これが必要な場合は、同じコードを複数の場所に書くことを避けるためにミックスインクラスの使用が推奨されます。

ミックスインクラスはスクリプトが複数の異なるクラス宣言にインクルードされる部分的なクラス構造を宣言できるようにします。ミックスインクラス自体は本物の型ではなく、インスタンス化することができません。

ミックスインクラスがクラス宣言にインクルードされると、ミックスインクラスで宣言されたプロパティとメソッドは自動的にクラスに複製されます。

```angelscript
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

クラスに既に明示的に宣言されているプロパティとメソッドは再度インクルードされません。このようにしてミックスインクラスはデフォルトの実装を提供し、ミックスインをインクルードするクラスでオーバーライドすることができます。

ミックスインクラスからインクルードされたクラスのメソッドは、それをインクルードしたクラスのコンテキストでコンパイルされます。そのため、ミックスインクラスをインクルードするクラスがそれらを提供する場合、ミックスインクラスのメソッドハはミックスインクラス内で宣言されていないプロパティや他のメソッドを参照することが可能です。

```angelscript
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

```angelscript
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

ミックスインクラスは、ミックスインクラスをインクルードするスクリプトクラスによって実装しなければならないインターフェースのリストを指定することができます。この場合、インターフェースのメソッドはオプションでミックスインクラス自体によって提供されることも、スクリプトクラスが直接実装するために省略されることもあります。

ミックスインクラスは他のクラスから継承することができません。

```angelscript
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
