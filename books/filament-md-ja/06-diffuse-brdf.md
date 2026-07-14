---
title: "Diffuse BRDF"
---

Diffuse 項では、$f_m$ は Lambertian 関数であり、BRDF の diffuse 項は次のようになります。

$$
f_d(v,l) = \frac{\sigma}{\pi} \frac{1}{| n \cdot v | | n \cdot l |}
\int_\Omega D(m,\alpha) G(v,l,m) (v \cdot m) (l \cdot m) dm
$$

私たちの実装では、代わりにマイクロファセット半球にわたって均一な diffuse 応答を仮定する単純な Lambertian BRDF を使用します。

$$
f_d(v,l) = \frac{\sigma}{\pi}
$$

実際には、リスト [diffuseBRDF] に示すように、diffuse reflectance $\sigma$ は後で乗算されます。

```glsl
float Fd_Lambert() {
    return 1.0 / PI;
}

vec3 Fd = diffuseColor * Fd_Lambert();
```
*リスト [diffuseBRDF]: GLSL での Diffuse Lambertian BRDF の実装*

Lambertian BRDF は明らかに非常に効率的で、より複雑なモデルに十分近い結果をもたらします。

ただし、diffuse 部分は理想的には specular 項と一貫性があり、サーフェスの roughness を考慮に入れる必要があります。Disney diffuse BRDF [#Burley12] と Oren-Nayar モデル [#Oren94] の両方が roughness を考慮に入れ、掠角でいくらかの retro-reflection を作成します。私たちの制約を考えると、追加のランタイムコストがわずかな品質向上を正当化しないと判断しました。この洗練された diffuse モデルは、image-based および spherical harmonics の表現と実装もより困難にします。

完全性のため、[#Burley12] で表現された Disney diffuse BRDF は次のとおりです。

$$
f_d(v,l) = \frac{\sigma}{\pi} F_{Schlick}(n,l,1,f_{90}) F_{Schlick}(n,v,1,f_{90})
$$

ここで：

$$
f_{90}=0.5 + 2 \cdot \alpha cos^2(\theta_d)
$$

```glsl
float F_Schlick(float u, float f0, float f90) {
    return f0 + (f90 - f0) * pow(1.0 - u, 5.0);
}

float Fd_Burley(float NoV, float NoL, float LoH, float roughness) {
    float f90 = 0.5 + 2.0 * roughness * LoH * LoH;
    float lightScatter = F_Schlick(NoL, 1.0, f90);
    float viewScatter = F_Schlick(NoV, 1.0, f90);
    return lightScatter * viewScatter * (1.0 / PI);
}
```
*リスト [diffuseBRDF]: GLSL での Diffuse Disney BRDF の実装*

図 [lambert_vs_disney] は、完全に粗い誘電体マテリアルを使用した、単純な Lambertian diffuse BRDF と高品質な Disney diffuse BRDF の比較を示しています。比較のため、右側の球体はミラーリングされています。サーフェス応答は両方の BRDF で非常に似ていますが、Disney のものは掠角で素敵な retro-reflection を示しています（球体の左端を注意深く見てください）。

![](/images/filament-md-ja/diagram_lambert_vs_disney.png)
*図 [lambert_vs_disney]: Lambertian diffuse BRDF（左）と Disney diffuse BRDF（右）の比較*

アーティスト/開発者が望む品質とターゲットデバイスのパフォーマンスに応じて、Disney diffuse BRDF を選択できるようにすることもできます。ただし、ここで表現されているように、Disney diffuse BRDF はエネルギー保存則に従っていないことに注意することが重要です。

## 標準モデルのまとめ

**Specular 項**: GGX 正規分布関数、Smith-GGX 高さ相関 visibility 関数、および Schlick Fresnel 関数を使用した Cook-Torrance specular マイクロファセットモデル。

**Diffuse 項**: Lambertian diffuse モデル。

標準モデルの完全な GLSL 実装はリスト [glslBRDF] に示されています。

```glsl
float D_GGX(float NoH, float a) {
    float a2 = a * a;
    float f = (NoH * a2 - NoH) * NoH + 1.0;
    return a2 / (PI * f * f);
}

vec3 F_Schlick(float u, vec3 f0) {
    return f0 + (vec3(1.0) - f0) * pow(1.0 - u, 5.0);
}

float V_SmithGGXCorrelated(float NoV, float NoL, float a) {
    float a2 = a * a;
    float GGXL = NoV * sqrt((-NoL * a2 + NoL) * NoL + a2);
    float GGXV = NoL * sqrt((-NoV * a2 + NoV) * NoV + a2);
    return 0.5 / (GGXV + GGXL);
}

float Fd_Lambert() {
    return 1.0 / PI;
}

void BRDF(...) {
    vec3 h = normalize(v + l);

    float NoV = abs(dot(n, v)) + 1e-5;
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    float NoH = clamp(dot(n, h), 0.0, 1.0);
    float LoH = clamp(dot(l, h), 0.0, 1.0);

    // perceptually linear roughness to roughness (see parameterization)
    float roughness = perceptualRoughness * perceptualRoughness;

    float D = D_GGX(NoH, roughness);
    vec3  F = F_Schlick(LoH, f0);
    float V = V_SmithGGXCorrelated(NoV, NoL, roughness);

    // specular BRDF
    vec3 Fr = (D * V) * F;

    // diffuse BRDF
    vec3 Fd = diffuseColor * Fd_Lambert();

    // apply lighting...
}
```
*リスト [glslBRDF]: GLSL での BRDF の評価*

---

原文: https://google.github.io/filament/Filament.html
