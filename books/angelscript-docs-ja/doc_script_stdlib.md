---
title: "📜 標準ライブラリ (Standard library)"
---

本ページでは AngelScript SDK が提供する標準ライブラリについて説明します。AngelScript を組み込んだアプリケーションによって、これらのライブラリがスクリプト側に公開されているかどうかが異なります。利用可能な API の詳細については、対象となるアプリケーションのマニュアルを併せて参照してください。

- [string](#string-（文字列）)
- [array - 配列](#array-（配列）)
- [dictionary - 辞書](#dictionary-（辞書）)
- [ref - 汎用ハンドル](#ref-（汎用ハンドル）)
- [weakref - 弱参照](#weakref-（弱参照）)
- [datetime - 日時](#datetime-（日時）)
- [file - ファイル](#file-（ファイル）)
- [filesystem - ファイルシステム](#filesystem-（ファイルシステム）)
- [socket](#socket)
- [例外処理](#例外処理-(exception-handling))
- [コルーチン](#コルーチン-(co-routines))
- [システム関数](#システム関数-(system-functions))

## socket

:::message
ソケットは、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

`socket` オブジェクトを使用すると、TCP によるクライアント・サーバー間の接続を確立できます。内部でキューやバッファを利用して動作するため、シングルスレッドのスクリプトであってもリモートシステムと非同期的に通信することが可能です。

```c++ (as)
// 接続の受け入れを開始します
socket server;
server.listen(39000);

// クライアントの接続を待ちます
socket @client = server.accept(10*1000000); // 10秒のタイムアウト
if( client !is null )
{
  // メッセージを受信します
  string pkg = client.receive(1*1000000); // 1秒のタイムアウト
  
  // クライアントに同じメッセージを返します
  client.send(pkg);
}
```

### socket のメソッド

**`int listen(uint16 port)`**  
要求されたポートで受信接続のリッスンを開始します。アクションが失敗した場合（例えばポートが既に使用中の場合）は負の値を返します。

**`int close()`**  
ソケットが開いている場合はそれを閉じます。アクションが失敗した場合は負の値を返します。

**`socket @accept(int64 timeout = 0)`**  
受信接続をリッスンしているソケットで使用できます。クライアントが接続しようとしている場合、このメソッドは接続が確立された新しいsocketオブジェクトを返します。タイムアウトはマイクロ秒単位です。

**`int connect(uint ipv4address, uint16 port)`**  
指定された IP アドレスとポートのリモートソケットに接続します。IP アドレスは32ビット符号なし整数として表されます（例えば 127.0.0.1 は `0x7F000001`）。

**`int send(const string &in data)`**  
すでに確立された接続でデータを送信します。送信されたバイト数または失敗した場合は負の値を返します。

**`string receive(int64 timeout = 0)`**  
接続で送信されたデータを受信します。タイムアウトはマイクロ秒単位。受信したバイトの文字列を返します。

**`bool isActive() const`**  
ソケットがアクティブな場合（つまりリッスン中または接続済みの場合）に true を返します。

## 例外処理 (Exception handling)

:::message
標準の `throw` と `getExceptionInfo` は、アプリケーションが [それらを登録](./doc_addon) した場合にのみ提供されます。
:::

**`void throw(const string &in exception)`**  
例外を明示的にスローします。文字列はロギングまたは処理のために例外の種類を識別する必要があります。

**`string getExceptionInfo()`**  
最後にスローされた例外の例外文字列を取得します。

## array （配列）

:::message
配列は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

配列変数は、`array` 識別子の後に山括弧の中に要素の型を付けて宣言することができます：

```c++ (as)
array<int> a, b, c;
array<Foo@> d;
```

配列を宣言する際、コンストラクタに引数を渡すことで初期サイズを指定できます。また、初期化リスト（波括弧 `{}`）を使って各要素を具体的に初期化することも可能です。

```c++ (as)
array<int> a;           // 長さゼロの整数配列
array<int> b(3);        // 3つの要素を持つ整数配列
array<int> c(3, 1);     // 3つの要素を持ち、すべてデフォルトで1が設定された整数配列
array<int> d = {5,6,7}; // 特定の値を持つ3つの要素の整数配列
```

多次元配列は配列の配列としてサポートされています：

```c++ (as)
array<array<int>> a;                     // 整数の配列の空の配列
array<array<int>> b = {{1,2},{3,4}}      // 値が初期化された2x2配列
array<array<int>> c(10, array<int>(10)); // 非初期化の値を持つ10x10の整数配列
```

配列の各要素はインデックス演算子でアクセスされます。インデックスはゼロベースです（有効なインデックスの範囲は 0 から length - 1）：

```c++ (as)
a[0] = some_value;
```

配列はコンテナとして `foreach` ループをサポートしています：

```c++ (as)
array<int> arr = {1,2,3,4,5,6};
int sum = 0;

// 値を合計して配列を反転します
foreach( auto value, auto index : arr ) // インデックス変数が不要な場合は省略可
{
  sum += value;
  arr[index] = -value; // インデックスを使って配列の現在の要素を変更します
}
```

### array の演算子

- **`=` 代入**: 内容の浅いコピーを行います
- **`[]` インデックス演算子**: 要素の参照を返します（範囲外の場合は例外が発生）
- **`==, !=` 等値**: 2つの配列の各要素を値比較します

### array のメソッド

| メソッド | 説明 |
|---------|------|
| `uint length() const` | 配列の要素数を返します |
| `void resize(uint)` | 配列のサイズを変更します |
| `void reverse()` | 配列の要素の順序を逆にします |
| `void insertAt(uint index, const T& in value)` | 指定インデックスに新しい要素を挿入します |
| `void insertAt(uint index, const array<T>& arr)` | 指定インデックスに別の配列の要素を挿入します |
| `void insertLast(const T& in)` | 配列の末尾に要素を追加します |
| `void removeAt(uint index)` | 指定インデックスの要素を削除します |
| `void removeLast()` | 配列の最後の要素を削除します |
| `void removeRange(uint start, uint count)` | `start` から `count` 個の要素を削除します |
| `void sortAsc()` | 要素を昇順に並べ替えます |
| `void sortAsc(uint startAt, uint count)` | 指定範囲の要素を昇順に並べ替えます |
| `void sortDesc()` | 要素を降順に並べ替えます |
| `void sortDesc(uint startAt, uint count)` | 指定範囲の要素を降順に並べ替えます |
| `void sort(const less &in compareFunc, ...)` | コールバック関数を使用して並べ替えます |
| `int find(const T& in)` | 指定値と一致する最初の要素のインデックスを返します |
| `int find(uint startAt, const T& in)` | 指定インデックスから検索します |
| `int findByRef(const T& in)` | アドレスが一致する要素のインデックスを返します |
| `int findByRef(uint startAt, const T& in)` | 指定インデックスからアドレス検索します |

コールバックを使用したソートの例：

```c++ (as)
array<int> arr = {3,2,1};
arr.sort(function(a,b) { return a < b; });
```

## dictionary （辞書）

:::message
辞書は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

辞書（ディクショナリ）は「キー」と「値」のペアを保持するコンテナです。キーには文字列を使い、値には任意の型を格納できます。エントリを動的に追加・削除できるため、汎用的なデータ管理に適しています。

```c++ (as)
obj object;
obj @handle;

// リストで初期化します
dictionary dict = {{'one', 1}, {'object', object}, {'handle', @handle}};

// get や set メソッドで値を調べてアクセスします
if( dict.exists('one') )
{
  bool isValid = dict.get('handle', @handle);
  if( isValid )
  {
    dict.delete('object');
    dict.set('value', 1);
  }
}
```

辞書の値はインデックス演算子を使用してアクセスまたは追加することもできます：

```c++ (as)
// 整数値の読み取りと変更
int val = int(dict['value']);
dict['value'] = val + 1;
```

辞書は `foreach` ループをサポートしています：

```c++ (as)
dictionary dict = {{'a',1},{'b',2},{'c',3}};
int sum = 0;

foreach( auto value, auto key : dict ) // キー変数が不要な場合は省略可
{
  sum += int(value);
  dict[key] = 0;
}
```

### dictionary のメソッド

| メソッド | 説明 |
|---------|------|
| `void set(const string &in key, ? &in value)` | キーと値のペアを設定します |
| `bool get(const string &in key, ? &out value) const` | キーに対応する値を取得します |
| `array<string>@ getKeys() const` | すべてのキーの配列を返します |
| `bool exists(const string &in key) const` | キーが存在する場合 true を返します |
| `bool delete(const string &in key)` | キーと対応する値を削除します |
| `void deleteAll()` | すべてのエントリを削除します |
| `bool isEmpty() const` | 辞書が空の場合 true を返します |
| `uint getSize() const` | キーの数を返します |

## string （文字列）

:::message
文字列は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

文字列リテラルの構文については [データ型のページ](./doc_script_datatypes) を参照してください。

### string の演算子

- **`=` 代入**: 右辺の文字列の内容を左辺にコピーします（プリミティブ型の代入も許可されます）
- **`+, +=` 連結**: 右辺の文字列の内容を左辺の末尾に追加します
- **`==, !=` 等値**: 2つの文字列の内容を比較します
- **`<, >, <=, >=` 比較**: バイト値で文字列の内容を比較します
- **`[]` インデックス演算子**: 文字列内の1バイトへのアクセスを提供します

### string のメソッド

| メソッド | 説明 |
|---------|------|
| `uint length() const` | 文字列の長さを返します |
| `void resize(uint)` | 文字列の長さを設定します |
| `bool isEmpty() const` | 文字列が空の場合 true を返します |
| `string substr(uint start = 0, int count = -1) const` | 指定範囲の部分文字列を返します |
| `void insert(uint pos, const string &in other)` | 指定位置に別の文字列を挿入します |
| `void erase(uint pos, int count = -1)` | 指定位置から文字を削除します |
| `int findFirst(const string &in str, uint start = 0) const` | 最初の出現を検索します |
| `int findLast(const string &in str, int start = -1) const` | 最後の出現を検索します |
| `int findFirstOf(const string &in chars, int start = 0) const` | chars 内の任意の文字の最初の出現を見つけます |
| `int findFirstNotOf(const string &in chars, int start = 0) const` | chars にない最初の文字を見つけます |
| `int findLastOf(const string &in chars, int start = -1) const` | chars 内の任意の文字の最後の出現を見つけます |
| `int findLastNotOf(const string &in chars, int start = -1) const` | chars にない最後の文字を見つけます |
| `int regexFind(const string &in regex, uint start = 0, uint &out lengthOfMatch = void) const` | ECMAScript の正規表現構文で検索します |
| `array<string>@ split(const string &in delimiter) const` | 区切り文字で文字列を分割します |

### string のグローバル関数

| 関数 | 説明 |
|------|------|
| `string join(const array<string> &in arr, const string &in delimiter)` | 配列の文字列を大きな文字列に連結します |
| `uint scan(const string &in str, ?&out ...)` | 後続の値を文字列から解析します |
| `int64 parseInt(const string &in str, uint base = 10, uint &out byteCount = 0)` | 文字列から整数値を解析します |
| `uint64 parseUInt(const string &in str, uint base = 10, uint &out byteCount = 0)` | 文字列から符号なし整数値を解析します |
| `double parseFloat(const string &in, uint &out byteCount = 0)` | 文字列から浮動小数点値を解析します |
| `string format(const string &in fmt, const ?&in ...)` | 複数の値で文字列をフォーマットします |
| `string formatInt(int64 val, const string &in options = '', uint width = 0)` | 整数をフォーマットします |
| `string formatUInt(uint64 val, const string &in options = '', uint width = 0)` | 符号なし整数をフォーマットします |
| `string formatFloat(double val, const string &in options = '', uint width = 0, uint precision = 0)` | 浮動小数点値をフォーマットします |

`format` 関数の使用例：

```c++ (as)
string result = format('{} {} {}', 123, true, 'hello');
```

`formatInt`/`formatUInt`/`formatFloat` のオプション文字列：

| 文字 | 説明 |
|------|------|
| `l` | 左揃え |
| `0` | ゼロでパディング |
| `+` | 正の数でも常に符号を含める |
| スペース | 正の数の場合にスペースを追加 |
| `h` | 小文字の16進数整数（formatFloat には無効） |
| `H` | 大文字の16進数整数（formatFloat には無効） |
| `e` | 小文字の e による指数文字（formatFloat のみ有効） |
| `E` | 大文字の E による指数文字（formatFloat のみ有効） |

## ref （汎用ハンドル）

:::message
`ref` は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

通常、オブジェクトハンドルは特定の型（またはその派生型）しか参照できませんが、`ref` はあらゆるオブジェクト型を参照できる「汎用的なハンドル」として機能します。異なる型同士を一つのハンドルで扱いたい場合に非常に便利です。

```c++ (as)
// 2つの関連しない型
class car {}
class banana {}

// ref 型を引数として取る関数は両方の型で動作できます
void func(ref @handle)
{
  car @c = cast<car>(handle);
  banana @b = cast<banana>(handle);
  if( c !is null )
    print('ハンドルは car を参照しています\n');
  else if( b !is null )
    print('ハンドルは banana を参照しています\n');
  else if( handle !is null )
    print('ハンドルは別のオブジェクトを参照しています\n');
  else
    print('ハンドルは null です\n');
}
```

## weakref （弱参照）

:::message
`weakref` は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

通常のオブジェクトハンドルは、ハンドル自体が存在する限り、参照先のオブジェクトを生存させ続けます。これに対し `weakref`（弱参照）は、オブジェクトへの参照は保持したいが、そのハンドルによってオブジェクトの寿命を延ばしたくない（オブジェクトの破棄を妨げたくない）場合に使用します。

```c++ (as)
class MyClass {}
MyClass @obj1 = MyClass();

// オブジェクトへの weakref を保持します
weakref<MyClass> r1(obj1);

// 読み取り専用オブジェクトへの weakref を保持します
const_weakref<MyClass> r2(obj1);

// オブジェクトへの強参照がある限り、
// weakref はオブジェクトへのハンドルを返せます
MyClass @obj2 = r1.get();
assert( obj2 !is null );

// すべての強参照が削除された後、
// weakref は null のみを返します
@obj1 = null;
@obj2 = null;

const MyClass @obj3 = r2.get();
assert( obj3 is null );
```

### weakref のメソッド

**`T@ get() const`**: 弱参照が参照するオブジェクトへの強参照を返します。オブジェクトがすでに破棄されている場合は null を返します。

## datetime （日時）

:::message
datetime は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

datetime 型はカレンダーの日付と時刻を表します。日付の比較、日付間の差の決定、新しい日付を形成するための日付の加減算などの数学演算に使用できます。

現在のシステム時刻の取得にも使用でき、タスクの時間測定が可能ですが、精度は秒のみです。

### datetime のコンストラクタ

- `datetime()` - オブジェクトを現在のシステム時刻（UTC）で初期化します
- `datetime(const datetime &in other)` - 他のオブジェクトの内容をコピーします
- `datetime(uint y, uint m, uint d, uint h = 0, uint mi = 0, uint s = 0)` - 指定した日付と時刻で初期化します

### datetime のメソッドとプロパティ

| メソッド/プロパティ | 説明 |
|---------|------|
| `uint get_year() const property` | 年を返します |
| `uint get_month() const property` | 月を返します（1〜12） |
| `uint get_day() const property` | 月の日を返します |
| `uint get_hour() const property` | 時を返します（0〜23） |
| `uint get_minute() const property` | 分を返します（0〜59） |
| `uint get_second() const property` | 秒を返します（0〜59） |
| `uint get_weekDay() const property` | 曜日を返します（0=日曜日、6=土曜日） |
| `bool setDate(uint year, uint month, uint day)` | 日付を設定します |
| `bool setTime(uint hour, uint minute, uint second)` | 時刻を設定します |

datetime の演算子：`=`（代入）、`-`（差、秒数として）、`+`/`-`（秒の加減算）、`==`/`!=`/`<`/`<=`/`>=`/`>`（比較）

## file （ファイル）

:::message
file は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

```c++ (as)
file f;
// 'read' モードでファイルを開きます
if( f.open("file.txt", "r") >= 0 ) 
{
    // ファイル全体を文字列バッファに読み取ります
    string str = f.readString(f.getSize()); 
    f.close();
}
```

### file のメソッド

| メソッド | 説明 |
|---------|------|
| `int open(const string &in filename, const string &in mode)` | ファイルを開きます（"r"=読み取り、"w"=書き込み、"a"=追記） |
| `int close()` | ファイルを閉じます |
| `int getSize() const` | ファイルのサイズを返します |
| `bool isEndOfFile() const` | 現在位置がファイルの末尾の場合 true を返します |
| `string readString(uint length)` | 指定バイト数を文字列として読み取ります |
| `string readLine()` | 改行またはファイル末尾まで読み取ります |
| `int64 readInt(uint bytes)` | 指定バイト数を符号あり整数として読み取ります |
| `uint64 readUInt(uint bytes)` | 指定バイト数を符号なし整数として読み取ります |
| `float readFloat()` | 4バイトを float として読み取ります |
| `double readDouble()` | 8バイトを double として読み取ります |
| `int writeString(const string &in str)` | 文字列のバイトをファイルに書き込みます |
| `int writeInt(int64 value, uint bytes)` | 符号あり整数値を書き込みます |
| `int writeUInt(uint64 value, uint bytes)` | 符号なし整数値を書き込みます |
| `int writeFloat(float value)` | float 値を書き込みます |
| `int writeDouble(double value)` | double 値を書き込みます |
| `int getPos() const` | ファイル内の現在位置を返します |
| `int setPos(int pos)` | ファイル内の現在位置を設定します |
| `int movePos(int delta)` | 現在位置から相対的に位置を移動します |

プロパティ `mostSignificantByteFirst`（bool）：数値を読み書きするメソッドで最上位バイトを最初に読み書きする場合は true に設定します。デフォルトは false です。

## filesystem （ファイルシステム）

:::message
filesystem は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

### filesystem のメソッド

| メソッド | 説明 |
|---------|------|
| `bool changeCurrentPath(const string &in path)` | filesystem オブジェクトが使用する現在のディレクトリを変更します |
| `string getCurrentPath() const` | filesystem オブジェクトが使用する現在のパスを返します |
| `array<string>@ getDirs()` | 現在のパスにあるすべてのディレクトリ名のリストを返します |
| `array<string>@ getFiles()` | 現在のパスにあるすべてのファイル名のリストを返します |
| `bool isDir(const string &in path)` | 指定パスがディレクトリの場合 true を返します |
| `bool isLink(const string &in path)` | 指定パスがリンクの場合 true を返します |
| `int64 getSize(const string &in) const` | ファイルのサイズを返します |
| `int makeDir(const string &in)` | 新しいディレクトリを作成します（成功時 0） |
| `int removeDir(const string &in)` | ディレクトリを削除します（空の場合のみ）（成功時 0） |
| `int deleteFile(const string &in)` | ファイルを削除します（成功時 0） |
| `int copyFile(const string &in, const string &in)` | ファイルをコピーします（成功時 0） |
| `int move(const string &in, const string &in)` | ファイルまたはディレクトリを移動・名前変更します（成功時 0） |
| `datetime getCreateDateTime(const string &in)` | ファイルの作成日時を UTC で返します |
| `datetime getModifyDateTime(const string &in)` | ファイルの最終変更日時を UTC で返します |

## コルーチン (Co-routines)

:::message
コルーチンのサポートは、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

**`funcdef void coroutine(dictionary@)`**  
コルーチンの関数シグネチャを定義します。

**`void createCoRoutine(coroutine @, dictionary @)`**  
コルーチンを作成します。コルーチンは yield された状態で開始します（現在のスレッドから制御が与えられるまで実行が始まりません）。

複数のコルーチンを作成することができ、それらはラウンドロビン方式で交互に実行されます。

**`void yield()`**  
キュー内の次のコルーチンに実行の制御を引き渡します。コルーチンが制御を受け取ると、最後の `yield` 呼び出しから（またはコルーチンが初めて実行される場合はエントリポイントから）実行を再開します。

## システム関数 (System functions)

:::message
システム関数は、アプリケーションが [そのサポートを登録](./doc_addon) した場合にのみスクリプトで使用可能です。
:::

**`void print(const string &in line)`**  
標準出力に行を印刷します。末尾に改行は追加されないため、必要な場合は呼び出し元が引数に含める必要があります。

**`string getInput()`**  
標準入力から行を取得します。

**`array<string>@ getCommandLineArgs()`**  
コマンドライン引数を配列として取得します。

**`int exec(const string &in cmd)`**  
**`int exec(const string &in cmd, string &out output)`**  
システムコマンドを実行します。エラー時は -1 を返すか例外が発生します。成功時はシステムコマンドの終了コードを返します。2番目のバリアントは stdout を文字列にキャプチャできます。

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_stdlib.html
