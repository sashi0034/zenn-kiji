---
title: "パラメータ化"
---

[#Burley12] で説明されている Disney のマテリアルモデルは良い出発点ですが、パラメータが多数あるためリアルタイム実装には実用的ではありません。さらに、標準マテリアルモデルは、アーティストと開発者の両方にとって理解しやすく、使いやすいものにしたいと考えています。

## 標準パラメータ

表 [standardParameters] は、私たちの制約を満たすパラメータのリストを説明しています。

| パラメータ | 定義 |
| ---: | :--- |
| **BaseColor** | 非金属サーフェスの Diffuse albedo、および金属サーフェスの Specular 色 |
| **Metallic** | サーフェスが誘電体（0.0）または導体（1.0）に見えるかどうか。多くの場合、バイナリ値（0 または 1）として使用される |
| **Roughness** | サーフェスの知覚される滑らかさ（0.0）または粗さ（1.0）。滑らかなサーフェスは鋭い反射を示す |
| **Reflectance** | 誘電体サーフェスの垂直入射での Fresnel reflectance。これは明示的な屈折率を置き換える |
| **Emissive** | 発光サーフェス（ネオンなど）をシミュレートするための追加の Diffuse albedo。このパラメータは、ブルームパスを持つ HDR パイプラインで最も有用 |
| **Ambient occlusion** | サーフェスポイントにアンビエントライトがどれだけアクセスできるかを定義します。0.0 から 1.0 の間のピクセルごとのシャドウイング係数。このパラメータについては、ライティングセクションで詳しく説明します |
*表 [standardParameters]: 標準モデルのパラメータ*

図 [material_parameters] は、metallic、roughness、reflectance パラメータがサーフェスの外観にどのように影響するかを示しています。

![](/images/filament-md-ja/material_parameters.png)
*図 [material_parameters]: 上から下へ: metallic の変化、誘電体 roughness の変化、金属 roughness の変化、reflectance の変化*

## 型と範囲

表 [standardParametersTypes] に記述されているように、マテリアルモデルの異なるパラメータの型と範囲を理解することが重要です。

| パラメータ | 型と範囲 |
| ---: | :--- |
| **BaseColor** | Linear RGB [0..1] |
| **Metallic** | Scalar [0..1] |
| **Roughness** | Scalar [0..1] |
| **Reflectance** | Scalar [0..1] |
| **Emissive** | Linear RGB [0..1] + 露出補正 |
| **Ambient occlusion** | Scalar [0..1] |
*表 [standardParametersTypes]: 標準モデルのパラメータの範囲と型*

ここで説明されている型と範囲は、シェーダーが期待するものであることに注意してください。API やツール UI は、アーティストにとってより直感的な他の型と範囲を使用してパラメータを指定できる、またそうすべきです。

例えば、base color は sRGB 空間で表現し、シェーダーに送る前に線形空間に変換できます。また、アーティストが metallic、roughness、reflectance パラメータを 0 から 255（黒から白）のグレー値として表現できると便利です。

別の例：emissive パラメータは、黒体が放出する光をシミュレートするために、色温度と強度として表現できます。

## リマッピング

標準マテリアルモデルをアーティストにとって使いやすく、より直感的にするために、パラメータ _baseColor_、_roughness_、_reflectance_ をリマップする必要があります。

### Base color のリマッピング

マテリアルの base color は、そのマテリアルの「metallicness（金属性）」の影響を受けます。誘電体は無彩色の specular reflectance を持ちますが、diffuse 色として base color を保持します。一方、導体は base color を specular 色として使用し、diffuse 成分を持ちません。

したがって、ライティング方程式は base color の代わりに diffuse 色と $f_{0}$ を使用する必要があります。リスト [baseColorToDiffuse] に示すように、diffuse 色は base color から簡単に計算できます。

```glsl
vec3 diffuseColor = (1.0 - metallic) * baseColor.rgb;
```
*リスト [baseColorToDiffuse]: GLSL での base color から diffuse への変換*

### Reflectance のリマッピング

**誘電体**

Fresnel 項は、垂直入射角での specular reflectance である $f_{0}$ に依存し、誘電体では無彩色です。[#Lagarde14] で説明されている誘電体サーフェスのリマッピングを使用します。

$$
f_{0} = 0.16 \cdot reflectance^2
$$

目標は、一般的な誘電体サーフェス（4% reflectance）と宝石（8% から 16%）の両方の Fresnel 値を表現できる範囲に $f_{0}$ をマップすることです。マッピング関数は、入力 reflectance が 0.5（または線形 RGB グレースケールで 128）の場合に 4% の Fresnel reflectance 値を生成するように選択されています。図 [reflectance] は、これらの一般的な値と、それらがマッピング関数にどのように関連しているかを示しています。

![](/images/filament-md-ja/diagram_reflectance.png)
*図 [reflectance]: 一般的な reflectance 値*

屈折率がわかっている場合（例えば、空気と水の界面の IOR は 1.33）、Fresnel reflectance は次のように計算できます。

$$
f_{0}(n_{ior}) = \frac{(n_{ior} - 1)^2}{(n_{ior} + 1)^2}
$$

reflectance 値がわかっている場合、対応する IOR を計算できます。

$$
n_{ior} = \frac{2}{1 - \sqrt{f_{0}}} - 1
$$

表 [commonMatReflectance] は、さまざまなタイプのマテリアルに対する許容可能な Fresnel reflectance 値を説明しています（現実世界のマテリアルは 2% 未満の値を持ちません）。

| マテリアル | Reflectance | IOR | Linear 値 |
| ---: | :--- | :--- | :--- |
| 水 | 2% | 1.33 | 0.35 |
| 布地 | 4% to 5.6% | 1.5 to 1.62 | 0.5 to 0.59 |
| 一般的な液体 | 2% to 4% | 1.33 to 1.5 | 0.35 to 0.5 |
| 一般的な宝石 | 5% to 16% | 1.58 to 2.33 | 0.56 to 1.0 |
| プラスチック、ガラス | 4% to 5% | 1.5 to 1.58 | 0.5 to 0.56 |
| その他の誘電体マテリアル | 2% to 5% | 1.33 to 1.58 | 0.35 to 0.56 |
| 目 | 2.5% | 1.38 | 0.39 |
| 肌 | 2.8% | 1.4 | 0.42 |
| 髪 | 4.6% | 1.55 | 0.54 |
| 歯 | 5.8% | 1.63 | 0.6 |
| デフォルト値 | 4% | 1.5 | 0.5 |
*表 [commonMatReflectance]: 一般的なマテリアルの Reflectance（出典: Real-Time Rendering 4th Edition）*

表 [fNormalMetals] は、いくつかの金属の $f_{0}$ 値をリストしています。値は sRGB で示されており、マテリアルモデルで base color として使用する必要があります。測定データからこれらの sRGB 色がどのように計算されるかの説明については、付録のセクション [Specular color] を参照してください。

| 金属 | $f_{0}$ in sRGB | 16進数 | 色 |
| ---: | :---: | :---: | --- |
| 銀 | 0.97, 0.96, 0.91 | #f7f4e8 |
| アルミニウム | 0.91, 0.92, 0.92 | #e8eaea |
| チタン | 0.76, 0.73, 0.69 | #c1baaf |
| 鉄 | 0.77, 0.78, 0.78 | #c4c6c6 |
| プラチナ | 0.83, 0.81, 0.78 | #d3cec6 |
| 金 | 1.00, 0.85, 0.57 | #ffd891 |
| 真鍮 | 0.98, 0.90, 0.59 | #f9e596 |
| 銅 | 0.97, 0.74, 0.62 | #f7bc9e |
*表 [fNormalMetals]: 一般的な金属の $f_{0}$*

すべてのマテリアルは掠角で 100% の Fresnel reflectance を持つため、specular BRDF $f_r$ を評価する際に次のように $f_{90}$ を設定します。

$$
f_{90} = 1.0
$$

図 [grazing_reflectance] は赤いプラスチックのボールを示しています。球体の端を注意深く見ると、掠角での無彩色の specular reflectance に気付くことができるでしょう。

![](/images/filament-md-ja/material_grazing_reflectance.png)
*図 [grazing_reflectance]: specular reflectance は掠角で無彩色になる*

**導体**

金属サーフェスの specular reflectance は有彩色です。

$$
f_{0} = baseColor \cdot metallic
$$

リスト [fNormal] は、誘電体と金属マテリアルの両方に対して $f_{0}$ がどのように計算されるかを示しています。金属の場合、specular reflectance の色が base color から導出されることを示しています。

```glsl
vec3 f0 = 0.16 * reflectance * reflectance * (1.0 - metallic) + baseColor * metallic;
```
*リスト [fNormal]: GLSL での誘電体および金属マテリアルの $f_{0}$ の計算*

### Roughness のリマッピングとクランプ

ユーザーが設定する roughness（ここでは `perceptualRoughness` と呼ばれる）は、次の定式化を使用して知覚的に線形な範囲にリマップされます。

$$
\alpha = perceptualRoughness^2
$$

図 [roughness_remap] は、変更されていない roughness 値（下）とリマップされた値（上）を使用して、roughness を増加させた（0.0 から 1.0 まで）銀の金属サーフェスを示しています。

![](/images/filament-md-ja/material_roughness_remap.png)
*図 [roughness_remap]: Roughness リマッピングの比較: 知覚的に線形な roughness（上）と roughness（下）*

この視覚的比較を使用すると、リマップされた roughness がアーティストと開発者にとって理解しやすいことは明らかです。このリマッピングがないと、光沢のある金属サーフェスは 0.0 から 0.05 の間の非常に小さな範囲に限定されなければなりません。

Brent Burley は彼のプレゼンテーション [#Burley12] で同様の観察を行いました。他のリマッピング（例えば、3 次および 2 次マッピング）を実験した後、この単純な 2 乗リマッピングが、リアルタイムアプリケーションにとって安価でありながら、視覚的に美しく直感的な結果をもたらすという結論に達しました。

最後に重要なこととして、roughness パラメータは、限られた浮動小数点精度が問題になる可能性があるランタイムでのさまざまな計算で使用されることに注意することが重要です。例えば、_mediump_ 精度の浮動小数点数は、モバイル GPU では半精度浮動小数点数（fp16）として実装されることがよくあります。

これは、ライティング方程式で $\frac{1}{perceptualRoughness^4}$ のような小さな値を計算するときに問題を引き起こします（GGX 計算での roughness の 2 乗）。半精度浮動小数点数として表現できる最小値は $2^{-14}$ または $6.1 \times 10^{-5}$ です。非正規化数をサポートしないデバイスでの 0 による除算を回避するために、$\frac{1}{roughness^4}$ の結果は $6.1 \times 10^{-5}$ より低くなってはなりません。そのためには、roughness を 0.089 にクランプする必要があります。これにより $6.274 \times 10^{-5}$ が得られます。

パフォーマンス低下を防ぐために、非正規化数も回避する必要があります。明らかな 0 による除算を回避するために、roughness も 0 に設定することはできません。

また、specular ハイライトに最小サイズを持たせたい（0 に近い roughness はほとんど見えないハイライトを作成します）ため、シェーダーで roughness を安全な範囲にクランプする必要があります。このクランプには、低い roughness 値で現れる可能性がある specular エイリアシング[^frostbiteRoughnessClamp]を修正するという追加の利点があります。

[^frostbiteRoughnessClamp]: Frostbite エンジンは、specular エイリアシングを減らすために、解析的ライトの roughness を 0.045 にクランプします。これは、単精度浮動小数点数（fp32）を使用する場合に可能です。

## ブレンディングとレイヤリング

[#Burley12] と [#Neubelt13] で述べられているように、このモデルは、異なるパラメータを単に補間することで、異なるマテリアル間の堅牢なブレンディングを可能にします。特に、これにより単純なマスクを使用して異なるマテリアルをレイヤー化できます。

例えば、図 [materialBlending] は、スタジオ Ready at Dawn が _The Order: 1886_ でマテリアルブレンディングとレイヤリングを使用して、単純なマテリアル（金、銅、木、錆など）のライブラリから複雑な外観を作成した方法を示しています。

![](/images/filament-md-ja/material_blending.png)
*図 [materialBlending]: マテリアルブレンディングとレイヤリング。出典: Ready at Dawn Studios*

マテリアルのブレンディングとレイヤリングは、実質的にマテリアルモデルのさまざまなパラメータの補間です。図 [material_interpolation] は、光沢のある金属クロームと粗い赤いプラスチックの間の補間を示しています。中間のブレンドされたマテリアルは物理的にはあまり意味がありませんが、もっともらしく見えます。

![](/images/filament-md-ja/material_interpolation.png)
*図 [material_interpolation]: 光沢のあるクロム（左）から粗い赤いプラスチック（右）への補間*

## 物理ベースマテリアルの作成

物理ベースマテリアルの設計は、4 つの主要なパラメータの性質を理解すれば、かなり簡単です。base color、metallic、roughness、reflectance です。

アーティストと開発者が独自の物理ベースマテリアルを作成するのに役立つ[便利なチャート/リファレンスガイド](./Material%20Properties.pdf)を提供しています。

![](/images/filament-md-ja/material_chart.jpg)
*物理ベースマテリアルの作成*

さらに、マテリアルモデルの使用方法の簡単な要約を以下に示します。

**すべてのマテリアル**

**Base color** は、マイクロオクルージョンを除いて、ライティング情報を含んではいけません。

**Metallic** はほぼバイナリ値です。純粋な導体は metallic 値が 1 で、純粋な誘電体は metallic 値が 0 です。0 または 1 に近い、または一致する値を使用するようにしてください。中間値は、サーフェスタイプ間の遷移（例えば、金属から錆への遷移）を意図しています。

**非金属マテリアル**

**Base color** は反射色を表し、50-240（厳密な範囲）または 30-240（許容範囲）の範囲の sRGB 値である必要があります。

**Metallic** は 0 または 0 に近い値である必要があります。

**Reflectance** は、適切な値が見つからない場合は 127 sRGB（0.5 linear、4% reflectance）に設定する必要があります。90 sRGB（0.35 linear、2% reflectance）未満の値は使用しないでください。

**金属マテリアル**

**Base color** は specular 色と reflectance の両方を表します。67% から 100% の輝度を持つ値（170-255 sRGB）を使用してください。酸化または汚れた金属は、非金属成分を考慮に入れるため、きれいな金属よりも低い輝度を使用する必要があります。

**Metallic** は 1 または 1 に近い値である必要があります。

**Reflectance** は無視されます（base color から計算されます）。

---

原文: https://google.github.io/filament/Filament.html
