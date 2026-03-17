---
title: "ガベージコレクション対応オブジェクト (Garbage collected objects)"
---

メモリ管理としての参照カウントには、デッドオブジェクト（不要になったオブジェクト）を判定する際に循環参照を検出するのが困難であるという欠点があります。AngelScript では、循環参照を検出するためのガベージコレクションをサポートするために、特別な振る舞い（behaviours）を持つ型をアプリケーションが登録できるようになっています。これらの振る舞いはクラスを少し複雑にしますが、登録する必要があるのはジェネリックなコンテナクラスなど、ごく少数の型に対してのみで済むはずです。

```cpp
// ガベージコレクション対応の参照型を登録する
r = engine->RegisterObjectType("ref_type", 0, asOBJ_REF | asOBJ_GC); assert( r >= 0 );
```

ガベージコレクション対応型と非対応型の違いは、`addref` と `release` の振る舞い、クラスコンストラクタ、そして追加のサポート用の振る舞いにあります。

ガベージコレクション対応オブジェクトの例については、[辞書 (dictionary)](./doc_addon#dictionary-オブジェクト) アドオンを参照してください。

## GC サポート用の振る舞い (GC support behaviours)

GC（ガベージコレクター）は、各オブジェクトから辿ることができる参照の数をカウントすることによって、オブジェクトがいつ破棄されるべきかを決定します。もし GC がオブジェクトを指す「すべての」参照を把握できた場合、そのオブジェクトは循環参照の一部であると判断し得ます。その循環参照に関与しているすべてのオブジェクトが外部からの参照を持たない場合、それはそれらすべてが破棄されるべきであることを意味します。

デッドオブジェクトを判定するプロセスには以下の振る舞いのうち最初の4つが使用され、オブジェクトの破棄は、オブジェクトの持つ参照の解放 (release) を強制することによって行われます。

```cpp
void CGCRef::SetGCFlag()
{
    // 参照カウンターの最上位ビットとして gc フラグを設定する
    refCount |= 0x80000000;
}

bool CGCRef::GetGCFlag()
{
    // gc フラグを返す
    return (refCount & 0x80000000) ? true : false;
}

int CGCRef::GetRefCount()
{
    // gc フラグを除いた参照カウントを返す
    return (refCount & 0x7FFFFFFF);
}

void CGCRef::EnumReferences(asIScriptEngine *engine)
{
    // 保持している他のオブジェクトへのすべての参照に対して engine::GCEnumCallback を呼び出す
    engine->GCEnumCallback(myref);
}

void CGCRef::ReleaseAllReferences(asIScriptEngine *engine)
{
    // この呼び出しを受け取った時、我々は死んだも同然ですが、GCは我々への参照を
    // まだ保持しているため、我々自身を直ちに削除することはまだできません。
    // 単に我々が保持している他のオブジェクトへのすべての参照を解放します。
    if( myref )
    {
        myref->Release();
        myref = 0;
    }
}

// GC サポート用の振る舞いを登録する
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_SETGCFLAG, "void f()", asMETHOD(CGCRef,SetGCFlag), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_GETGCFLAG, "bool f()", asMETHOD(CGCRef,GetGCFlag), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_GETREFCOUNT, "int f()", asMETHOD(CGCRef,GetRefCount), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_ENUMREFS, "void f(int&in)", asMETHOD(CGCRef,EnumReferences), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_RELEASEREFS, "void f(int&in)", asMETHOD(CGCRef,ReleaseAllReferences), asCALL_THISCALL); assert( r >= 0 );
```

## ガベージコレクション用のファクトリ (Factory for garbage collection)

ガベージコレクション対応のクラスが作成されるたびに、ガベージコレクターにその存在を通知しなければなりません。それを行う最も簡単な方法は、クラスの初期化時にファクトリの振る舞い、あるいはクラスコンストラクタが、エンジン上の `NotifyGarbageCollectorOfNewObject()` メソッドを呼び出すことです。

```cpp
CGCRef *GCRef_Factory()
{
    // オブジェクトを作成し、その後 GC にその存在を通知する
    CGCRef *obj = new CGCRef();
    asITypeInfo *type = engine->GetTypeInfoByName("gc");
    engine->NotifyGarbageCollectorOfNewObject(obj, type);
    return obj;
}
```

この型のオブジェクトが作成されるたびに、比較的コストがかかる `GetTypeIdByDecl` の呼び出しを通じて毎回 typeId を検索しなくて済むように、typeId をキャッシュしておくことを検討すると良いでしょう。

なお、アプリケーション側からこの型のオブジェクトを作成する場合も、ガベージコレクターにその存在を通知する必要があります。そのため、すべてのコードがこの型のオブジェクトを作成する際に同じ方法を使用するように保証するのが優れたやり方です。

## ガベージコレクションに合わせた Addref と Release (Addref and release for garbage collection)

ガベージコレクション対応のオブジェクトにおいて、`AddRef` と `Release` の振る舞いが GC フラグをクリアしていることを確認することは重要です。そうしないと、GC が誤ってオブジェクトを破棄すべきだと判定してしまう可能性があります。

```cpp
void CGCRef::AddRef()
{
    // gc フラグをクリアし、参照カウンターを増加させる
    refCount = (refCount&0x7FFFFFFF) + 1;
}

void CGCRef::Release()
{
    // gc フラグをクリアし、参照カウントを減少させ、0に達したら削除する
    refCount &= 0x7FFFFFFF;
    if( --refCount == 0 )
        delete this;
}

// addref/release の振る舞いを登録する
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_ADDREF, "void f()", asMETHOD(CGCRef,AddRef), asCALL_THISCALL); assert( r >= 0 );
r = engine->RegisterObjectBehaviour("ref_type", asBEHAVE_RELEASE, "void f()", asMETHOD(CGCRef,Release), asCALL_THISCALL); assert( r >= 0 );
```

## 値型における GC の振る舞い (GC behaviours for value types)

値型 (value types) はそれ自身が直接参照（ポインタのように複数の箇所から共有される形）されることがないため、通常は循環参照の原因になるとは考えられていません。しかし、もしある「値型」が他の参照型への参照を保持できる場合、そしてその「参照型」がさらに自分のメンバとして先ほどの「値型」を持っている場合、循環参照が成立してしまい、参照型が解放されるのを妨げてしまいます。

これらの状況を解決するために、値型に対してもガベージコレクターの振る舞いをいくつか登録することが可能です。

```cpp
// ガベージコレクションの振る舞いとともに値型を登録する
r = engine->RegisterObjectType("value_type", sizeof(value_type), asOBJ_VALUE | asOBJ_GC | ...); assert( r >= 0 );

// ガベージコレクターの振る舞いを登録する
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_ENUMREFS, "void f(int&in)", asMETHOD(value_type,EnumReferences), asCALL_THISCALL); assert(r >= 0);
r = engine->RegisterObjectBehaviour("ref", asBEHAVE_RELEASEREFS, "void f(int&in)", asMETHOD(value_type, ReleaseReferences), asCALL_THISCALL); assert(r >= 0);
```

値型については、`asBEHAVE_ENUMREFS` と `asBEHAVE_RELEASEREFS` のみを登録する必要があります。これらは参照型の場合と同じように動作します。つまり、`asBEHAVE_ENUMREFS` は保持しているすべての参照についてエンジンの `GCEnumCallback` を呼び出すべきであり、`asBEHAVE_RELEASEREFS` は保持しているすべての参照をクリアするべきです。

GCの振る舞いを持つ値型をメンバとして含む参照型は、自身の `asBEHAVE_ENUMREFS` と `asBEHAVE_RELEASEREFS` の呼び出しを、メンバである値型へ転送（forward）するように適応させる必要があります。この転送は、それぞれエンジンの `ForwardGCEnumReferences` または `ForwardGCReleaseReferences` を呼び出すことによって行われます。

```cpp
void CGCRef2::EnumReferences(asIScriptEngine *engine)
{
    // 列挙の呼び出しをメンバの値型へ転送する
    engine->ForwardGCEnumReferences(valueObj, valueType);
}

void CGCRef2::ReleaseAllReferences(asIScriptEngine *engine)
{
    // この呼び出しを受け取った時、我々は死んだも同然ですが、GCは我々への参照を
    // まだ保持しているため、我々自身を直ちに削除することはまだできません。
    // 単に我々が保持している他のオブジェクトへのすべての参照を解放します。

    // 解放の呼び出しをメンバの値型へ転送する
    engine->ForwardGCReleaseReferences(valueObj, valueType);
}
```

参照: GCの振る舞いを持つ値型の例としての [handle アドオン](./doc_addon#handle-オブジェクト)、およびGCの振る舞いを持つ値型を含むことができる参照型の例としての [dictionary アドオン](./doc_addon#dictionary-オブジェクト)。

## ガベージコレクション対応オブジェクトとマルチスレッド (Garbage collected objects and multi-threading)

もしあなたが [自動ガベージコレクション](./doc_adv_custom_options#エンジンの振る舞い-engine-behaviours) を有効にした状態で複数のスレッドからスクリプトを実行する予定がある場合、またはバックグラウンドスレッドから手動でガベージコレクターを実行する予定がある場合は、ガベージコレクターをサポートするオブジェクト型の振る舞い（behaviours）が**スレッドセーフ**であることを保証しなければなりません。特に ADDREF、RELEASE、そして ENUMREFS の振る舞いは、複数のスレッドから同時に呼び出される確率が高くなります。RELEASEREFS の振る舞いは、ガベージコレクターがそのオブジェクトが既にデッドであると判断した時にのみ呼び出されるため、複数のスレッドによって呼び出されないことが保証されています。その他の GETREFCOUNT、SETGCFLAG、および GETGCFLAG は、ガベージコレクターがその情報を単にヒントとして使用するだけなので、さほど敏感ではありません。

ADDREF と RELEASE の振る舞いをスレッドセーフにするのは、`asAtomicInc` と `asAtomicDec` を使用することで簡単に実現できます。オブジェクトの内容のメモリレイアウトが変更されない（例えば静的なコンテナである）場合、ENUMREFS はすでにスレッドセーフです。しかし、動的配列やハッシュマップのようにメモリレイアウトが変更され得る場合は、ENUMREFS の内容に対する反復処理（イテレーション）の途中でメモリが変更された場合に備えて、壊れないように反復処理を保護しなければなりません。

参照: [ガベージコレクション (Garbage collection)](./doc_gc#ガベージコレクションとマルチスレッド-garbage-collection-and-multi-threading)

---

原文: https://www.angelcode.com/angelscript/sdk/docs/manual/doc_gc_object.html
