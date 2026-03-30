---
title: "ライブラリのコンパイル (Compile the library)"
---

`sdk/angelscript/projects` ディレクトリには、主要なコンパイラ向けのプロジェクトファイルが用意されています。ただし、これらは必ずしも最新バージョンのライブラリ構成を反映しているとは限りません。コンパイルエラーやリンクエラーが発生した場合は、プロジェクトに `sdk/angelscript/source` ディレクトリ内のすべてのファイルが含まれていること、およびプロジェクト設定が本記事の内容に従って適切に行われているかを確認してください。

お使いのコンパイラ用のプロジェクトファイルが見つからない場合は、`sdk/angelscript/source` ディレクトリ内の全ファイルをプロジェクトに追加し、適切に構成することで、独自のプロジェクトを容易に作成できます。これまで AngelScript で使用されたことのない新しいコンパイラやターゲット環境を利用する場合は、適切にコンパイルするために `as_config.h` の編集が必要になる可能性があります。

参照: [特定のプラットフォームに関する考慮事項](#特定のプラットフォームに関する考慮事項-(considerations-for-specific-platforms))

## コンパイル時のオプションの設定 (Set compile time options)

コードは、コンパイラ間の差異を最小限に抑えるように設計されています。そのためのヘッダーファイルが `as_config.h` です。このファイルには、様々なコンパイラに対応させるための `#define` 定義が記述されています。通常このファイルを変更する必要はありませんが、未知のコンパイラを使用してコンパイルエラーが発生した場合には、このファイルの内容を確認してみるとよいでしょう。

他にも、コンパイル時の動作をカスタマイズするための `#define` 定義がいくつかあります。ライブラリをコンパイルする際、ライブラリの関数をエクスポートするために `ANGELSCRIPT_EXPORT` を定義したい場合があります。なお、アプリケーションのプロジェクトにライブラリのソースコードを直接含める場合は、このフラグを定義する必要はありません。

`AS_DEPRECATED` を定義すると、一部の下位互換性が維持されます。これにより最新バージョンへの移行をよりスムーズに進めることができます。ただし、下位互換性が永久に保証されているわけではないため、非推奨となった関数はできるだけ早く使用を止めるようにしてください。

## ライブラリとのリンク (Linking with the library)

AngelScript をプロジェクトに組み込むためのコンパイル・リンク方法は主に 4 つあります。その中でも、静的ライブラリ（スタティックライブラリ）としてリンクする方法を推奨します。これら 4 つの方法は、コードのわずかな変更（ヘッダーインクルード前のフラグ定義や、DLL 手動ロード用ルーチンの追加など）だけで相互に切り替え可能です。それ以外のアプリケーションコードについては、どの方法を選んでも全く同じになります。

### 1. プロジェクトにライブラリのソースファイルを含める (Include library source files in project)

AngelScript のソースファイルをそのまま自分のプロジェクトに直接含めることができます。この方法の利点は、ライブラリとホストアプリケーションで全く同じコンパイラオプション（例えば、マルチスレッドやシングルスレッドの CRT 設定など）が使用されることが保証される点です。デメリットは、プロジェクト内にライブラリのファイルが混在し、管理が煩雑になる可能性があることです。

ライブラリを使用する必要があるファイルでは、特別な設定なしに `angelscript.h` ヘッダーをインクルードするだけです。

```cpp
// ライブラリのインターフェースをインクルード
#include "angelscript.h"

// ... ライブラリの使用を開始
```

### 2. スタティックライブラリをコンパイルしてプロジェクトにリンクする (Compile a static library and link into project)

最も推奨される方法は、プロジェクトにリンクするためのスタティックライブラリをコンパイルすることです。スタティックライブラリをコンパイルする際、CRT 関数とのリンクで競合が発生しないように、正しいコンパイラ設定が使用されていることを確認する必要があります。例えば、ライブラリを動的にリンクするマルチスレッド CRT でコンパイルし、アプリケーションを静的にリンクするシングルスレッド CRT でコンパイルした場合に競合が発生します。（Visual C++ の場合、これらの設定は「プロジェクト」->「設定」->「C/C++」->「カテゴリ: コード生成」にあります）

ライブラリを使用するには、`angelscript.h` ヘッダーファイルをインクルードするだけです。

```cpp
// ライブラリのインターフェースをインクルード
#include "angelscript.h"

// ... ライブラリの使用を開始
```

### 3. インポートライブラリとともに動的ロードライブラリをコンパイルする (Compile a dynamically loaded library with an import library)

Microsoft Visual C++ を使用すると、インポートライブラリとともに動的ロードライブラリ（DLL）をコンパイルすることができます。このインポートライブラリは、DLLをロードし、関数をバインドするために必要な処理を行います。この方法の考えられる欠点は、ライブラリのロードに失敗した場合に、ユーザーフレンドリーなエラーメッセージを出力できないことです。

ライブラリを使用するには、`angelscript.h` ヘッダーファイルをインクルードする前に `ANGELSCRIPT_DLL_LIBRARY_IMPORT` を定義する必要があります。

```cpp
// ライブラリのインターフェースをインクルード
#define ANGELSCRIPT_DLL_LIBRARY_IMPORT
#include "angelscript.h"

// ... ライブラリの使用を開始
```

DLL を手動でロードして使用する場合は、`angelscript.h` をインクルードする前に `ANGELSCRIPT_DLL_MANUAL_IMPORT` を定義してください。これにより、ヘッダーファイルによる関数プロトタイプの宣言が無効化されます。これは、アプリケーション側で同じ名前の関数ポインタ変数を定義する際に、シンボルの衝突を避けるためです。

```cpp
// ライブラリのインターフェースをインクルード
#define ANGELSCRIPT_DLL_MANUAL_IMPORT
#include "angelscript.h"

// 関数ポインタを宣言
typedef asIScriptEngine * AS_CALL t_asCreateScriptEngine(int);
t_asCreateScriptEngine *asCreateScriptEngine = 0;

// ... 残りの関数を宣言

// DLLをロードし、関数をバインドする (明確にするためエラーハンドリングは省略しています)
HMODULE dll = LoadLibrary("angelscript.dll");
asCreateScriptEngine = (t_asCreateScriptEngine*)GetProcAddress(dll, "_asCreateScriptEngine");

// ... 他の関数をバインド

// ... ライブラリの使用を開始
```

## 特定のプラットフォームに関する考慮事項 (Considerations for specific platforms)

前述のように、ほとんどのプラットフォームでライブラリのコンパイルは、すべてのソースファイルを含めてそれらをコンパイルするだけという単純な作業です。しかしながら、一部のプラットフォームではライブラリを正しくコンパイルするために特定のアクションを実行する必要があります。

### Windows 64bit

MSVC コンパイラは、x86 64bit CPU ファミリのインラインアセンブラをサポートしていません。このプラットフォームをサポートするために、独立したアセンブラファイル `as_callfunc_x64_msvc_asm.asm` が作成されています。

このファイルをコンパイルするには、次の内容でカスタムビルドコマンドを設定する必要があります：

```
ml64.exe /c  /nologo /Fo$(OutDir)\as_callfunc_x64_msvc_asm.obj /W3 /Zi /Ta $(InputDir)\$(InputFileName)
```

### Microsoft Visual C++

AngelScript は Microsoft 独自の言語拡張を使用していませんが、それでも言語拡張を無効にするとライブラリのコンパイルで問題が発生する場合があります。これは Microsoft 独自の SDK が言語拡張に依存するコードを持っている可能性があるためです。例えば、Platform SDK のバージョン 6.0a では `specstrings.h` ヘッダーのマクロ定義内にある `$` の存在によりコンパイルエラーが発生すことがあります。この特定の問題は Microsoft 製 SDK のバージョン 6.1 で修正されましたが、他の問題があるかもしれないため、言語拡張を有効にしたままにするのが一番簡単かもしれません。

ラッパーを介さずに C++ と適切に統合するため、AngelScript 内では多くのポインタキャストが使用されています。残念ながら、これらが常に厳密な別名規約（strict aliasing）を満たすとは限らないため、GNUC ベースのコンパイラでは、strict aliasing を前提とした最適化を無効にする必要があります。

この最適化を無効化するには、以下のコンパイラオプションを指定します：

```
-fno-strict-aliasing
```

### Pocket PC with ARM CPU

MSVC コンパイラは ARM CPU のインラインアセンブラをサポートしていないため、アセンブリ用のコードを利用する独立したアセンブラファイル `as_callfunc_arm_msvc.asm` を利用します。

このファイルを適切にコンパイルするには、次の内容でカスタムビルドコマンドを設定する必要があります：

```
armasm -g $(InputPath)
```

### Marmalade

Marmalade はモバイルデバイスを念頭に置いて作成されたクロスプラットフォーム SDK です。これは背後の OS 上に独自の C ランタイムライブラリ層（Windows上でのMSVC、LinuxやMac上でのGNUCなどの一般的な C++ コンパイラが利用されますが）を抽象化することで機能します。

iOS および Android 用に Marmalade で AngelScript をコンパイルする場合、ネイティブな ARM アセンブラルーチンを適切にコンパイルするために scons を利用する必要があります。Windows Phone の場合は通常通り MSVC を使用できるはずです。

## ライブラリのサイズ (Size of the library)

ライブラリのサイズは、コンパイラの種類、コンパイラフラグ、AngelScript のどの機能が含まれているかなど、様々な要因によって異なります。しかしながら、ライブラリがディスクとメモリ上でどれだけのスペースを占めるかの目安を示すために、[asrun サンプル (asrun sample)](./doc_samples#command-line-runner（コマンドラインランナー）) をいくつかの異なる方法でコンパイルし、サイズを記録しました。

| オプション | ディスク上のバイナリのサイズ |
| --- | --- |
| 32 bit / multithreaded dll / optimize for speed<br>AngelScript を含まない場合 | 14KB |
| 32 bit / multithreaded dll / optimize for speed<br>AngelScript とアドオンを含めた場合 | 796KB |
| 32 bit / multithreaded dll / optimize for speed<br>AngelScript を含めるがコンパイラなし (AS_NO_COMPILER)、およびアドオンを含めた場合 | 453KB |
| 32 bit / multithreaded static / optimize for speed<br>AngelScript を含めるがアドオンなしの場合 | 867KB |
| 32 bit / multithreaded static / optimize for speed<br>AngelScript とアドオンを含めた場合 | 1015KB |
| 64 bit / multithreaded static / optimize for speed<br>AngelScript とアドオンを含めた場合 | 1336KB |
| 32 bit / multithreaded static / optimize for size<br>AngelScript とアドオンを含めた場合 | 797KB |
| 32 bit / multithreaded dll / optimize for size<br>AngelScript とアドオンを含めた場合 | 582KB |

これに基づくと、実行速度に最適化した場合、エンジンと VM は約 300KB の容量を占め、コンパイラはさらに 350KB、アドオンはさらに 150KB を追加すると結論づけることができます。

> **Note**: これらのテストは、MSVC 2012 およびライブラリのバージョン 2.30.2 で実施されました。

---

訳注: こちらも参考になれば幸いです。

https://zenn.dev/sashi0034/articles/bf06646e0d88ac#5.-c%2B%2B-%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E3%81%AB-angelscript-%E3%82%92%E7%B5%84%E3%81%BF%E8%BE%BC%E3%82%80

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_compile_lib.html
