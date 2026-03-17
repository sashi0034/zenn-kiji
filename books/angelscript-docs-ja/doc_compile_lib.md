---
title: "ライブラリのコンパイル (Compile the library)"
---

`sdk/angelscript/projects` ディレクトリ内には、多くの主要なコンパイラ用のプロジェクトファイルがあります。しかしながら、これらのプロジェクトファイルは常にライブラリの最新バージョンに更新されているとは限りません。コンパイラやリンカーのエラーが発生した場合は、プロジェクトファイルに `sdk/angelscript/source` ディレクトリ内のすべてのファイルが含まれていること、およびプロジェクトの設定がこの記事に従って適切に行われていることを確認してください。

お使いのコンパイラ用のプロジェクトファイルが見つからない場合は、`sdk/angelscript/source` ディレクトリ内のすべてのファイルを追加し、プロジェクトを適切に構成することで、独自のプロジェクトを簡単に作成できます。AngelScript でこれまで使用されたことのない新しいコンパイラやターゲットを使用している場合は、ライブラリが適切にコンパイルされるように `as_config.h` ファイルを編集する必要があるかもしれません。

参照: [特定のプラットフォームに関する考慮事項](#特定のプラットフォームに関する考慮事項-considerations-for-specific-platforms)

## コンパイル時のオプションの設定 (Set compile time options)

コードは、コンパイラ間の違いをできるだけ少数の箇所に留めるように設計されています。`as_config.h` ヘッダーはその目的のために作成されました。そこには、様々なコンパイラを動作させるための `#define` 定義がいくつか含まれています。おそらくこのファイルを変更する必要はないでしょうが、これまで使用されたことのないコンパイラを使用しており、コンパイラエラーが発生している場合は、このファイルを確認する価値があるかもしれません。

コード内には、コンパイルの挙動を変更するために使用される他の `#define` 定義もいくつか存在します。ライブラリをコンパイルする際、ライブラリの関数をエクスポートするために `ANGELSCRIPT_EXPORT` を定義したい場合があります。アプリケーションのプロジェクトにライブラリのソースコードを直接含める場合は、このフラグを定義する必要はありません。

`AS_DEPRECATED` が定義されている場合、一部の下位互換性が維持されます。これにより最新バージョンへのアップグレードを少しスムーズに行うことができます。ただし、下位互換性が保証されているわけではないため、非推奨となった関数はできるだけ早く使用を中止するようにしてください。

## ライブラリとのリンク (Linking with the library)

AngelScript を使用するためにライブラリをコンパイルおよびリンクする方法には4つあります。その中でもスタティックライブラリとしてリンクする方法を推奨します。なお、これら4つの方法は、コードの小さな変更（例えば、ヘッダーファイルをインクルードする前のフラグの定義や、DLLを手動でロードするルーチンの追加など）だけで相互に置き換え可能です。それ以外のコードについては、どの方法を使用しても全く同じになります。

### 1. プロジェクトにライブラリのソースファイルを含める (Include library source files in project)

AngelScript のソースファイルをそのまま自分のプロジェクトに直接含めることができます。この方法の利点は、ライブラリとホストアプリケーションで全く同じコンパイラオプション（例えば、マルチスレッドやシングルスレッドの CRT など）が使用されることが保証される点です。欠点は、プロジェクトがライブラリのファイルで雑然としてしまうことです。

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

### 4. 動的ロードライブラリを手動でロードする (Load the dynamically loaded library manually)

アプリケーション間でコードを共有するなどの目的で DLL を使用したい場合は、関数のロードやバインドに失敗した時のエラーハンドリングを丁寧に行うことができるため、ライブラリを手動でロードすることをお勧めします。

手動でロードする DLL を使用する場合は、`angelscript.h` ヘッダーファイルをインクルードする前に `ANGELSCRIPT_DLL_MANUAL_IMPORT` を定義する必要があります。これにより、ヘッダーファイルが関数のプロトタイプを宣言しないようになります。なぜなら、その関数名と同名の関数ポインタを使用する必要がある可能性が高いからです。

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

### GNUC ベースのコンパイラ

ラッパーを必要とせずに C++ と適切に統合するために、AngelScript は大量のポインタキャストを使用しています。残念ながら、これによって常に strict aliasing（厳密なエイリアス）を保証できるわけではないため、GNUC ベースのコンパイラでは、strict aliasing を前提とするコンパイラ最適化を無効にする必要があります。

これを無効にするには、次のコンパイラ引数を使用します：

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

ライブラリのサイズは、コンパイラの種類、コンパイラフラグ、AngelScript のどの機能が含まれているかなど、様々な要因によって異なります。しかしながら、ライブラリがディスクとメモリ上でどれだけのスペースを占めるかの目安を示すために、[asrun サンプル (asrun sample)](./doc_samples_asrun) をいくつかの異なる方法でコンパイルし、サイズを記録しました。

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
