---
title: "Specular BRDF"
---

Specular 項については、$f_r$ は Fresnel の法則でモデル化できる鏡面 BRDF であり、Cook-Torrance によるマイクロファセットモデル積分の近似では $F$ と表記されます。

$$
f_r(v,l) = \frac{D(h, \alpha) G(v, l, \alpha) F(v, h, f0)}{4(n \cdot v)(n \cdot l)}
$$

リアルタイム制約を考えると、3 つの項 $D$、$G$、$F$ に対して近似を使用する必要があります。[#Karis13a] は、Cook-Torrance Specular BRDF で使用できるこれら 3 つの項の優れた定式化リストをまとめています。以下のセクションでは、これらの項に対して選択した方程式について説明します。

## Normal distribution function (specular D)

[#Burley12] は、ロングテール型の Normal distribution function（NDF）が現実世界のサーフェスに適していることを観察しました。[#Walter07] で説明されている GGX 分布は、ロングテールのフォールオフと短いピークをハイライトに持つ分布であり、リアルタイム実装に適したシンプルな定式化を持っています。また、現代の物理ベースレンダラーにおける Trowbridge-Reitz 分布と同等の人気のあるモデルでもあります。

$$
D_{GGX}(h,\alpha) = \frac{\alpha^2}{\pi ( (n \cdot h)^2 (\alpha^2 - 1) + 1)^2}
$$

リスト [specularD] に示す NDF の GLSL 実装はシンプルで効率的です。

```glsl
float D_GGX(float NoH, float roughness) {
    float a = NoH * roughness;
    float k = roughness / (1.0 - NoH * NoH + a * a);
    return k * k * (1.0 / PI);
}
```
*リスト [specularD]: GLSL での Specular D 項の実装*

この実装は半精度浮動小数点数を使用することで改善できます。この最適化には元の方程式への変更が必要です。半精度浮動小数点数で $1 - (n \cdot h)^2$ を計算する際に 2 つの問題があるためです。第一に、$(n \cdot h)^2$ が 1 に近い場合（ハイライト）、この計算は浮動小数点の桁落ちに悩まされます。第二に、$n \cdot h$ は 1 周辺で十分な精度を持っていません。

解決策には Lagrange の恒等式を使用します。

$$
| a \times b |^2 = |a|^2 |b|^2 - (a \cdot b)^2
$$

$n$ と $h$ はどちらも単位ベクトルであるため、$|n \times h|^2 = 1 - (n \cdot h)^2$ です。これにより、単純な外積を使用して半精度浮動小数点数で直接 $1 - (n \cdot h)^2$ を計算できます。リスト [specularDfp16] は、最終的な最適化された実装を示しています。

```glsl
#define MEDIUMP_FLT_MAX    65504.0
#define saturateMediump(x) min(x, MEDIUMP_FLT_MAX)

float D_GGX(float roughness, float NoH, const vec3 n, const vec3 h) {
    vec3 NxH = cross(n, h);
    float a = NoH * roughness;
    float k = roughness / (dot(NxH, NxH) + a * a);
    float d = k * k * (1.0 / PI);
    return saturateMediump(d);
}
```
*リスト [specularDfp16]: fp16 用に最適化された GLSL での Specular D 項の実装*

## Geometric shadowing (specular G)

Eric Heitz は [#Heitz14] で、Smith の geometric shadowing 関数が使用すべき正しく正確な $G$ 項であることを示しました。Smith の定式化は次のとおりです。

$$
G(v,l,\alpha) = G_1(l,\alpha) G_1(v,\alpha)
$$

$G_1$ は複数のモデルに従うことができ、一般的には GGX の定式化に設定されます。

$$
G_1(v,\alpha) = G_{GGX}(v,\alpha) = \frac{2 (n \cdot v)}{n \cdot v + \sqrt{\alpha^2 + (1 - \alpha^2) (n \cdot v)^2}}
$$

したがって、完全な Smith-GGX の定式化は次のようになります。

$$
G(v,l,\alpha) = \frac{2 (n \cdot l)}{n \cdot l + \sqrt{\alpha^2 + (1 - \alpha^2) (n \cdot l)^2}} \frac{2 (n \cdot v)}{n \cdot v + \sqrt{\alpha^2 + (1 - \alpha^2) (n \cdot v)^2}}
$$

被除数 $2 (n \cdot l)$ と $2 (n \cdot v)$ により、visibility 関数 $V$ を導入することで元の関数 $f_r$ を簡略化できることがわかります。

$$
f_r(v,l) = D(h, \alpha) V(v, l, \alpha) F(v, h, f_0)
$$

ここで：

$$
V(v,l,\alpha) = \frac{G(v, l, \alpha)}{4 (n \cdot v) (n \cdot l)} = V_1(l,\alpha) V_1(v,\alpha)
$$

そして：

$$
V_1(v,\alpha) = \frac{1}{n \cdot v + \sqrt{\alpha^2 + (1 - \alpha^2) (n \cdot v)^2}}
$$

ただし、Heitz は、マスキングとシャドウイングを相関させるためにマイクロファセットの高さを考慮すると、より正確な結果が得られると述べています。彼は高さ相関 Smith 関数を次のように定義しています。

$$
G(v,l,h,\alpha) = \frac{\chi^{+}(v \cdot h) \chi^{+}(l \cdot h)}{1 + \Lambda(v) + \Lambda(l)}
$$

$$
\Lambda(m) = \frac{-1 + \sqrt{1 + \alpha^2 tan^2(\theta_m)}}{2} = \frac{-1 + \sqrt{1 + \alpha^2 \frac{(1 - cos^2(\theta_m))}{cos^2(\theta_m)}}}{2}
$$

$cos(\theta_m)$ を $n \cdot v$ で置き換えると、次が得られます。

$$
\Lambda(v) = \frac{1}{2} \left( \frac{\sqrt{\alpha^2 + (1 - \alpha^2)(n \cdot v)^2}}{n \cdot v} - 1 \right)
$$

ここから visibility 関数を導出できます。

$$
V(v,l,\alpha) = \frac{0.5}{n \cdot l \sqrt{(n \cdot v)^2 (1 - \alpha^2) + \alpha^2} + n \cdot v \sqrt{(n \cdot l)^2 (1 - \alpha^2) + \alpha^2}}
$$

リスト [specularV] に示す visibility 項の GLSL 実装は、2 つの `sqrt` 演算が必要なため、期待するよりも少し高コストです。

```glsl
float V_SmithGGXCorrelated(float NoV, float NoL, float roughness) {
    float a2 = roughness * roughness;
    float GGXV = NoL * sqrt(NoV * NoV * (1.0 - a2) + a2);
    float GGXL = NoV * sqrt(NoL * NoL * (1.0 - a2) + a2);
    return 0.5 / (GGXV + GGXL);
}
```
*リスト [specularV]: GLSL での Specular V 項の実装*

平方根の下のすべての項が 2 乗であり、すべての項が $[0..1]$ 範囲にあることに気付いた後、近似を使用してこの visibility 関数を最適化できます。

$$
V(v,l,\alpha) = \frac{0.5}{n \cdot l (n \cdot v (1 - \alpha) + \alpha) + n \cdot v (n \cdot l (1 - \alpha) + \alpha)}
$$

この近似は数学的には間違っていますが、2 つの平方根演算を節約し、リスト [approximatedSpecularV] に示すように、リアルタイムモバイルアプリケーションには十分です。

```glsl
float V_SmithGGXCorrelatedFast(float NoV, float NoL, float roughness) {
    float a = roughness;
    float GGXV = NoL * (NoV * (1.0 - a) + a);
    float GGXL = NoV * (NoL * (1.0 - a) + a);
    return 0.5 / (GGXV + GGXL);
}
```
*リスト [approximatedSpecularV]: GLSL での近似 Specular V 項の実装*

[#Hammon17] は、平方根を削除できるという同じ観察に基づいて同じ近似を提案しています。式を _lerp_ として書き直すことでそれを行います。

$$
V(v,l,\alpha) = \frac{0.5}{lerp(2 (n \cdot l) (n \cdot v), n \cdot l + n \cdot v, \alpha)}
$$

## Fresnel (specular F)

Fresnel 効果は、物理ベースマテリアルの外観において重要な役割を果たします。この効果は、視聴者がサーフェスから反射されて見える光の量が視聴角度に依存するという事実をモデル化します。大きな水域は、図 [fresnelLake] に示されているように、この現象を体験する完璧な方法です。水をまっすぐ下に見ると（垂直入射で）、水を透かして見ることができます。しかし、遠くを見ると（掠角で、知覚される光線がサーフェスに平行になる場所）、水面の specular 反射がより強くなるのがわかります。

反射される光の量は、視聴角度だけでなく、マテリアルの屈折率（IOR）にも依存します。垂直入射（サーフェスに垂直、または 0 度の角度）では、反射される光の量は $f_{0}$ と表記され、セクション [Reflectance remapping] で見るように IOR から導出できます。掠角で反射される光の量は $f_{90}$ と表記され、滑らかなマテリアルでは 100% に近づきます。

![](/images/filament-md-ja/photo_fresnel_lake.jpg)
*図 [fresnelLake]: Fresnel 効果は大きな水域で特に顕著*

より正式には、Fresnel 項は、2 つの異なる媒体間の界面で光がどのように反射および屈折するか、または反射および透過エネルギーの比率を定義します。[#Schlick94] は、Cook-Torrance Specular BRDF の Fresnel 項の安価な近似を説明しています。

$$
F_{Schlick}(v,h,f_{0},f_{90}) = f_{0} + (f_{90} - f_{0})(1 - v \cdot h)^5
$$

定数 $f_{0}$ は垂直入射での specular reflectance を表し、誘電体では無彩色、金属では有彩色です。実際の値は界面の屈折率に依存します。リスト [specularF] に示すように、この項の GLSL 実装では `pow` の使用が必要ですが、いくつかの乗算で置き換えることができます。

```glsl
vec3 F_Schlick(float u, vec3 f0, float f90) {
    return f0 + (vec3(f90) - f0) * pow(1.0 - u, 5.0);
}
```
*リスト [specularF]: GLSL での Specular F 項の実装*

この Fresnel 関数は、入射 specular reflectance と掠角での reflectance（ここでは $f_{90}$ で表される）の間を補間するものと見なすことができます。現実世界のマテリアルの観察によると、誘電体と導体の両方が掠角で無彩色の specular reflectance を示し、Fresnel reflectance は 90 度で 1.0 であることがわかります。より正確な $f_{90}$ については、セクション [Specular occlusion] で説明します。

$f_{90}$ を 1 に設定すると、Fresnel 項の Schlick 近似は、コードを少しリファクタリングすることでスカラー演算用に最適化できます。結果はリスト [scalarSpecularF] に示されています。

```glsl
vec3 F_Schlick(float u, vec3 f0) {
    float f = pow(1.0 - u, 5.0);
    return f + f0 * (1.0 - f);
}
```
*リスト [scalarSpecularF]: GLSL での Specular F 項のスカラー最適化*

---

原文: https://google.github.io/filament/Filament.html
