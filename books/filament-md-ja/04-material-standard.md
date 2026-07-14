---
title: "マテリアルシステム — 標準モデル"
---

以下のセクションでは、異方性やクリアコート層などのさまざまなサーフェス特性の説明を簡略化するために、複数のマテリアルモデルを説明します。しかし実際には、これらのモデルの一部は単一のモデルに統合されています。例えば、標準モデル、クリアコートモデル、異方性モデルは組み合わせることで、単一のより柔軟で強力なモデルを形成できます。Filament で実装されているマテリアルモデルの説明については、[Materials ドキュメント](./Materials.md.html)を参照してください。

## 標準モデル

私たちのモデルの目的は、標準的なマテリアルの外観を表現することです。マテリアルモデルは数学的に BSDF（Bidirectional Scattering Distribution Function：双方向散乱分布関数）で記述され、BSDF 自体は他の 2 つの関数で構成されます。BRDF（Bidirectional Reflectance Distribution Function：双方向反射率分布関数）と BTDF（Bidirectional Transmittance Function：双方向透過関数）です。

私たちは一般的に遭遇するサーフェスをモデル化することを目指しているため、標準マテリアルモデルは BRDF に焦点を当て、BTDF は無視するか、または大幅に近似します。したがって、私たちの標準モデルは、平均自由行程の短い反射性、等方性、誘電体または導電性のサーフェスのみを正しく模倣できます。

BRDF は、標準マテリアルのサーフェス応答を 2 つの項で構成される関数として記述します。
- Diffuse 成分、または $f_d$
- Specular 成分、または $f_r$

サーフェス、サーフェス法線、入射光、およびこれらの項の関係を図 [frFd] に示します（現時点ではサブサーフェススキャタリングは無視します）。

![図 [frFd]: Diffuse 項 $ f_d $ と Specular 項 $ f_r $ を持つ BRDF モデルを使用した、光とサーフェスの相互作用](/images/filament-md-ja/diagram_fr_fd.png)

完全なサーフェス応答は次のように表現できます。

$$
f(v,l)=f_d(v,l)+f_r(v,l)
$$

この方程式は、単一方向からの入射光に対するサーフェス応答を特徴づけます。完全なレンダリング方程式では、$l$ を半球全体にわたって積分する必要があります。

一般的に遭遇するサーフェスは通常、平坦な界面でできていないため、不規則な界面との光の相互作用を特徴づけることができるモデルが必要です。

マイクロファセット BRDF は、その目的のために物理的にもっともらしい BRDF です。このような BRDF は、サーフェスがマイクロレベルでは滑らかではなく、マイクロファセットと呼ばれる多数のランダムに配向された平面サーフェス断片で構成されていると述べています。図 [microfacetVsFlat] は、マイクロレベルでの平坦な界面と不規則な界面の違いを示しています。

![図 [microfacetVsFlat]: マイクロファセットモデルによってモデル化された不規則な界面（左）と平坦な界面（右）](/images/filament-md-ja/diagram_microfacet.png)

法線が光の方向と視線方向の中間を向いているマイクロファセットのみが可視光を反射します。これは図 [microfacets] に示されています。

![図 [microfacets]: マイクロファセット](/images/filament-md-ja/diagram_macrosurface.png)

ただし、適切に配向された法線を持つすべてのマイクロファセットが反射光を寄与するわけではありません。BRDF はマスキングとシャドウイングを考慮に入れます。これは図 [microfacetShadowing] に示されています。

![図 [microfacetShadowing]: マイクロファセットのマスキングとシャドウイング](/images/filament-md-ja/diagram_shadowing_masking.png)

マイクロファセット BRDF は、マイクロレベルでサーフェスがどれだけ滑らか（低 roughness）か、またはどれだけ粗い（高 roughness）かを記述する _roughness_ パラメータに大きく影響されます。サーフェスが滑らかであるほど、より多くのファセットが整列し、反射光はより顕著になります。サーフェスが粗いほど、カメラと入射光に向けられたファセットが少なくなり、反射後に入射光がカメラから散乱されて、スペキュラハイライトにぼやけた外観を与えます。

図 [roughness] は、異なる roughness のサーフェスと、光がそれらとどのように相互作用するかを示しています。

![図 [roughness]: roughness の変化（左から右へ、粗いものから滑らかなものへ）と、結果として生じる BRDF Specular 成分のローブ](/images/filament-md-ja/diagram_roughness.png)

:::message
**注: roughness について**

ユーザーが設定する roughness パラメータは、本ドキュメント全体のシェーダースニペットでは `perceptualRoughness` と呼ばれます。`roughness` と呼ばれる変数は、セクション [Parameterization] で説明されているリマッピングが適用された `perceptualRoughness` です。
:::

マイクロファセットモデルは次の方程式で記述されます（x は specular または diffuse 成分を表します）。

$$
f_x(v,l) = \frac{1}{| n \cdot v | | n \cdot l |}
\int_\Omega D(m,\alpha) G(v,l,m) f_m(v,l,m) (v \cdot m) (l \cdot m) dm
$$

項 $D$ は、マイクロファセットの分布をモデル化します（この項は NDF または Normal Distribution Function とも呼ばれます）。この項は、図 [roughness] に示されているように、サーフェスの外観において主要な役割を果たします。

項 $G$ は、マイクロファセットの visibility（または occlusion または shadow-masking）をモデル化します。

この方程式は specular と diffuse の両方の成分に対して有効であるため、違いはマイクロファセット BRDF $f_m$ にあります。

この方程式は _マイクロレベル_ で半球にわたって積分するために使用されることに注意することが重要です。

![図 [microLevel]: 単一点でのサーフェス応答をモデル化するには、マイクロレベルでの積分が必要](/images/filament-md-ja/diagram_micro_vs_macro.png)

上の図は、マクロレベルでは、サーフェスが平坦であると見なされることを示しています。これは、単一方向から照らされたシェーディングされたフラグメントがサーフェスの単一点に対応すると仮定することで、方程式を簡略化するのに役立ちます。

ただし、マイクロレベルでは、サーフェスは平坦ではなく、もはや単一の光線を仮定することはできません（ただし、入射光線が平行であると仮定することはできます）。マイクロファセットは平行な入射光線の束が与えられると、光を異なる方向に散乱させるため、半球にわたってサーフェス応答を積分する必要があります。上の図では m と表記されています。

各シェーディングされたフラグメントに対してマイクロファセット半球全体の完全な積分を計算することは明らかに実用的ではありません。したがって、specular と diffuse の両方の成分に対して、積分の近似に依存します。

## 誘電体と導体

以下に示すいくつかの方程式と動作をよりよく理解するために、まず金属（導体）と非金属（誘電体）のサーフェスの違いを明確に理解する必要があります。

BRDF によって支配されるサーフェスに入射光が当たると、光は 2 つの別々の成分として反射されることを前に見ました。Diffuse reflectance と Specular reflectance です。この動作のモデル化は、図 [bsdfBrdf] に示されているように簡単です。

![図 [bsdfBrdf]: BSDF の BRDF 部分のモデル化](/images/filament-md-ja/diagram_fr_fd.png)

このモデル化は、光が実際にサーフェスとどのように相互作用するかの簡略化です。実際には、入射光の一部がサーフェスに侵入し、内部で散乱し、Diffuse reflectance として再びサーフェスから出ます。この現象は図 [diffuseScattering] に示されています。

![図 [diffuseScattering]: Diffuse 光の散乱](/images/filament-md-ja/diagram_scattering.png)

ここに導体と誘電体の違いがあります。純粋に金属性のマテリアルではサブサーフェススキャタリングが発生しません。つまり、Diffuse 成分がありません（そして後で、これが Specular 成分の知覚される色に影響を与えることがわかります）。スキャタリングは誘電体で発生します。つまり、誘電体は Specular と Diffuse の両方の成分を持っています。

BRDF を適切にモデル化するには、図 [dielectricConductor] に示されているように、誘電体と導体を区別する必要があります（明確にするため、スキャタリングは示されていません）。

![図 [dielectricConductor]: 誘電体および導体サーフェスの BRDF モデル化](/images/filament-md-ja/diagram_brdf_dielectric_conductor.png)

## エネルギー保存則

エネルギー保存則は、物理ベースレンダリングのための優れた BRDF の重要な構成要素の 1 つです。エネルギー保存則に従う BRDF は、Specular と Diffuse の reflectance エネルギーの合計が、入射エネルギーの合計よりも少ないことを述べています。エネルギー保存則に従う BRDF がなければ、アーティストは、サーフェスから反射される光が入射光よりも強くならないように手動で確認する必要があります。

---

原文: https://google.github.io/filament/Filament.html
