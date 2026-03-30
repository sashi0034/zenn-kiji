---
title: "🏠 はじめに (Introduction)"
---

![](/images/angelscript-docs-ja/aslogo.png)

`Version 2.38.0`

AngelScript は、アプリケーションへの組み込みを目的とした、[無料かつオープンソース](./doc_license)で柔軟な、クロスプラットフォーム・スクリプティングライブラリです。強力な機能を備えつつも、稀にしか使われない機能による肥大化を避け、使いやすさを最優先に設計されています。

AngelScript の開発は 2003 年 2 月に始まり、同年 3 月 28 日に基本機能を搭載した最初の公開リリースが行われました。それ以来、今日に至るまで新機能の追加や改善を伴う頻繁なアップデートが続いています。作者（Andreas Jönsson）は現在も、このライブラリの継続的な改善と発展に力を注いでいます。

ライブラリの公式サイトは [http://www.angelcode.com/angelscript](http://www.angelcode.com/angelscript) です。

https://github.com/anjo76/angelscript

# 特徴 (Features)

## スクリプト言語 (Script language)

- **馴染みのある構文 (Familiar syntax)** - スクリプトの構文は C や C++ に似ており、わずかな違いしかありません。
- **静的型付け (Statically typed)** - 動的型付けの多くのスクリプト言語とは異なり、AngelScript は C++ と同じ静的型付けを使用します。また、アプリケーションから追加の型を登録できます。
- **オブジェクト指向 (Object oriented)** - スクリプト言語ではクラスの宣言が可能で、単一継承やインターフェースを介したポリモーフィズムをサポートしています。
- **オブジェクトハンドル (Object handles)** - スクリプト環境ではポインタは安全ではないため、AngelScript では代わりにオブジェクトハンドルを使用します。オブジェクトハンドルはスマートポインタとほぼ同じ機能で、保持しているオブジェクトのライフタイム（有効期間）を管理します。
- **サンドボックス化 (Sandboxing)** - ライブラリはスクリプトに対して安全な環境を提供します。つまり、スクリプトはアプリケーションが明示的に公開したものにのみアクセスでき、組み込みのスクリプトオブジェクトは完全に安全です。
- **国際化サポート (International support)** - スクリプトファイルは ASCII または UTF-8 でエンコードできます。文字列定数には UTF-8 エンコードされた文字を直接含めることができるほか、エスケープシーケンスを使用して特定の Unicode コードポイントを追加することも可能です。UTF-16 エンコードされた文字列リテラルもサポートされています。

## エンジン (Engine)

- **実行時コンパイル (Run-time compiled)** - ライブラリはスクリプトをバイトコードにコンパイルし、仮想マシン上でそのバイトコードを実行します。
- **ステップ実行 (Step by step execution)** - スクリプトは、細かな制御やデバッグのために 1 行ずつ実行できます。
- **詳細な例外 (Detailed exceptions)** - 例外が発生した際、その原因や発生場所に関する情報を簡単に取得できます。
- **1行ごとの解釈 (Line interpretation)** - エンジンは現在コンパイルされているスクリプトを使用して個別のスクリプト行を解釈できます。ゲーム内コンソールなどに便利です。
- **バイトコードの保存と読み込み (Saving/loading byte code)** - コンパイルされたバイトコードは保存し、後でリロードすることができます。バイトコードはプラットフォームに依存しません。
- **モジュール性 (Modular)** - スクリプトは、相互に動的にリンク可能なモジュールとしてコンパイルできます。
- **並行スクリプト (Concurrent scripts)** - スクリプトを一つずつ一時停止・再開させることで、複数のスクリプトを並行して実行できます。これにより、マルチタスク構成やコルーチン（協調的マルチタスク）を簡単に実装できます。
- **デバッグサポート (Debugging support)** - アプリケーションはスクリプトの実行中にコールスタックやローカル変数の値を検査できます。行単位のコールバック機能を使えば、ブレークポイントの使用やプロファイリングなどが可能です。
- **リアルタイム対応 (Real-time capable)** - 実行時間は決定論的であり、変動しません。

## 統合 (Integration)

- **直接アクセス (Direct access)** - スクリプトエンジンは、登録された関数、オブジェクト、またオブジェクトのメンバーに対して直接アクセスし使用できるため、プロキシ関数を記述する必要がありません（ネイティブの呼び出し規約がサポートされている場合）。
- **C++インターフェース (C++ interface)** - 標準的なアプリケーションインターフェースは C++ ですが、C++ インターフェースとうまく連携できない言語からでも使用できるように、C 言語インターフェースを容易に記述できます。例えば、Delphi プロジェクトで成功裡に使用された実績があります。
- **マルチスレッド (Multithreading)** - ライブラリはマルチスレッド環境で使用できます。
- **メモリ管理 (Memory management)** - スクリプトとアプリケーション間で渡されるオブジェクトの管理を容易にするため、オブジェクトは参照カウント形式で管理されます。循環参照が発生する可能性のある箇所では、反復型のガベージコレクタが使用されます。アプリケーションがライブラリのメモリ使用量を完全に制御することも可能です。

## 移植性 (Portability)

- **クロスプラットフォーム (Cross platform)** - Windows, Linux, MacOS X, XBox, XBox 360, XBox One, PS2, PSP, PS3, PS4, PS Vita, Dreamcast, Nintendo DS, Windows Mobile, iPhone, BSD, Android で動作することが確認されています。
- **CPU非依存 (CPU independent)** - 32bit と 64bit の両方のプラットフォームがサポートされています。また、ビッグエンディアンとリトルエンディアンの両方の CPU もサポートされています。動作が確認されている CPU: x86, amd64, sh4, mips, ppc, ppc64, arm, s390x。
- **コンパイラのサポート (Compiler support)** - MSVC++, GNUC, MinGW, DJGPP, Borland C++ Builder で動作します。その他のコンパイラは公式にはテストされていませんが、同様に動作する可能性が高いです。
- **ネイティブ呼び出し規約 (Native calling conventions)** - ライブラリは、以下の構成や他の互換性のある構成において、ラッパーを必要とせずにネイティブの呼び出し規約をサポートしています。
  - Win32 - MSVC - x86
  - Win32 - MinGW - x86
  - Win32 CE - MSVC - arm
  - Win64 - MSVC - x86/64
  - Win64 - MinGW - x86/64
  - Linux - GNUC - x86/64
  - Linux - GNUC - arm/arm64
  - Linux - GNUC - mips
  - Linux - GNUC - risc-v 64
  - MacOS X - GNUC - x86
  - MacOS X - GNUC - x86/64
  - MacOS X - GNUC - ppc
  - iOS - GNUC - arm
  - iOS - GNUC/Clang - arm/arm64
  - BSD - GNUC - x86
  - BSD - GNUC - x86/64
  - Dreamcast - GNUC - sh4
  - PSP - GNUC - mips
  - PS2 - GNUC - mips
  - PS3 - GNUC - ppc/64
  - PS4 - GNUC - x86/64
  - PS Vita - GNUC - arm
  - XBox - MSVC - x86
  - XBox 360 - MSVC - ppc/64
  - XBox One - MSVC - x86/64
  - Android - GNUC - arm/arm64
  - Android - GNUC - mips
  - Haiku - GNUC - x86
  - Nintendo Switch - GNUC - arm64
- **最大互換モード (Maximum portability mode)** - このモードでコンパイルされた場合、標準に準拠した C++ コードをコンパイルできるほぼすべてのコンパイラ・プラットフォームで機能するはずです。ただし、ネイティブの呼び出し規約などの一部の機能はこのモードでは利用できません。
- **クロス言語 (Cross language)** - フラットな C 言語インターフェースを使用することで、Delphi などの他の言語からもライブラリを利用できます。また、C++ インターフェースを通じて .NET ベースのアプリケーションにライブラリを統合した実績もあります。さらに、emscripten と Chrome PNaCl を用いてコンパイルすることで、Web アプリケーションでも使用されています。

## その他 (Other)

- **無料 (No costs)** - スクリプトライブラリはすべての用途において完全に無料で利用できますが、寄付は歓迎しています。
- **充実したドキュメント (Well documented)** - スクリプト言語とライブラリの両方について、完全に文書化されたドキュメントが提供されています。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/index.html
原文: https://www.angelcode.com/angelscript/features.html
注: ページをツリー状に出来ないため、分かりやすさのため原文のページ順番を入れ替えてあるところがあります。
