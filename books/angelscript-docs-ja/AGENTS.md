
AngelScript のユーザーマニュアル (angelscript-2.38.0-doxygen/source 以下) を日本語に翻訳し、zenn の記事にしたいです。

angelscript-2.38.0-doxygen/source 以下のファイルをそれぞれ分かりやすい日本語に翻訳し、マークダウンファイルを記述してください。もちろんファイル名や変数名などは英語のままで良いです。ファイル名は元の英語ファイル名のままで構いません。angelscript-2.38.0-doxygen/source/doc_main.h から進めていくと良さそうです。

zenn 記法に従って構成する必要があり、それぞれのファイルは config.yaml で記載して管理します。
記載した順にチャプターが並べられるので、それを意識して列挙する必要があります。

各マークダウンの先頭には
```
---
title: "ページタイトル"
---
```
が必要です。

別ページへのリンクについて、例えば my_page.md のリンクは [my_page のマークダウン](./my_page) のように表記出来ます。

画像は ../images/angelscript-docs-ja に保存してください。ただし、記事から参照する時は ![](/images/angelscript-docs-ja/logo.png) のように表記してください。

コードブロックで angelscript を指定しても認識しないので、代わりに cs を指定してください。
