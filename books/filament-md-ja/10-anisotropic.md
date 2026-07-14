---
title: "Anisotropic モデル"
---

## Anisotropic モデル

これまでに説明した[標準マテリアルモデル](./04-material-standard)では、等方性サーフェス、つまりすべての方向で特性が同一であるサーフェスしか記述できません。しかし、ブラシをかけた金属など、多くの実世界のマテリアルは、異方性モデルを使用しないと再現できません。

![](/images/filament-md-ja/material_anisotropic.png)
*図 [anisotropic]: 等方性マテリアル（左）と異方性マテリアル（右）の比較*

### Anisotropic specular BRDF

前述した等方性 specular BRDF は、異方性マテリアルを扱うように変更できます。Burley は、異方性 GGX NDF を使用してこれを実現しています：

$$
D_{aniso}(h,\alpha) = \frac{1}{\pi \alpha_t \alpha_b} \frac{1}{((\frac{t \cdot h}{\alpha_t})^2 + (\frac{b \cdot h}{\alpha_b})^2 + (n \cdot h)^2)^2}
$$

残念ながら、この NDF は 2 つの追加の粗さ項に依存しています。$\alpha_b$ は bitangent 方向に沿った粗さで、$\alpha_t$ は tangent 方向に沿った粗さです。Neubelt と Pettineo [#Neubelt13] は、マテリアルの 2 つの粗さ値の関係を表す _anisotropy_ パラメータを使用して、$\alpha_t$ から $\alpha_b$ を導出する方法を提案しています：

$$
\begin{align*}
  \alpha_t &= \alpha \\
  \alpha_b &= lerp(0, \alpha, 1 - anisotropy)
\end{align*}
$$

[#Burley12] で定義されている関係は異なり、より快適で直感的な結果が得られますが、計算コストがわずかに高くなります：

$$
\begin{align*}
  \alpha_t &= \frac{\alpha}{\sqrt{1 - 0.9 \times anisotropy}} \\
  \alpha_b &= \alpha \sqrt{1 - 0.9 \times anisotropy}
\end{align*}
$$

私たちは代わりに [#Kulla17] で説明されている関係に従うことにしました。これにより、シャープなハイライトを作成できます：

$$
\begin{align*}
  \alpha_t &= \alpha \times (1 + anisotropy) \\
  \alpha_b &= \alpha \times (1 - anisotropy)
\end{align*}
$$

この NDF は、法線方向に加えて tangent と bitangent 方向を必要とすることに注意してください。これらの方向は法線マッピングにすでに必要なため、それらを提供することは問題にならないかもしれません。

結果として得られる実装は、リスト [anisotropicBRDF] に記載されています。

```glsl
float at = max(roughness * (1.0 + anisotropy), 0.001);
float ab = max(roughness * (1.0 - anisotropy), 0.001);

float D_GGX_Anisotropic(float NoH, const vec3 h,
        const vec3 t, const vec3 b, float at, float ab) {
    float ToH = dot(t, h);
    float BoH = dot(b, h);
    float a2 = at * ab;
    highp vec3 v = vec3(ab * ToH, at * BoH, a2 * NoH);
    highp float v2 = dot(v, v);
    float w2 = a2 / v2;
    return a2 * w2 * w2 * (1.0 / PI);
}
```
*リスト [anisotropicBRDF]: Burley の異方性 NDF の GLSL 実装*

さらに、[#Heitz14] は、高さ相関 GGX 分布に合わせた異方性 masking-shadowing 関数を提示しています。masking-shadowing 項は、visibility 関数を使用することで大幅に簡素化できます：

$$
G(v,l,h,\alpha) = \frac{\chi^{+}(v \cdot h) \chi^{+}(l \cdot h)}{1 + \Lambda(v) + \Lambda(l)}
$$

$$
\Lambda(m) = \frac{-1 + \sqrt{1 + \alpha_0^2 tan^2(\theta_m)}}{2} = \frac{-1 + \sqrt{1 + \alpha_0^2 \frac{(1 - cos^2(\theta_m))}{cos^2(\theta_m)}}}{2}
$$

ここで：

$$
\alpha_0 = \sqrt{cos^2(\phi_0)\alpha_x^2 + sin^2(\phi_0)\alpha_y^2}
$$

導出後、次を得ます：

$$
V_{aniso}(n \cdot l,n \cdot v,\alpha) = \frac{1}{2((n \cdot l)\hat{\Lambda}_v+(n \cdot v)\hat{\Lambda}_l)} \\
\hat{\Lambda}_v = \sqrt{\alpha^2_t(t \cdot v)^2+\alpha^2_b(b \cdot v)^2+(n \cdot v)^2} \\
\hat{\Lambda}_l = \sqrt{\alpha^2_t(t \cdot l)^2+\alpha^2_b(b \cdot l)^2+(n \cdot l)^2}
$$

$\hat{\Lambda}_v$ 項はすべてのライトで同じであり、必要に応じて一度だけ計算できます。結果として得られる実装は、リスト [anisotropicV] に記載されています。

```glsl
float at = max(roughness * (1.0 + anisotropy), 0.001);
float ab = max(roughness * (1.0 - anisotropy), 0.001);

float V_SmithGGXCorrelated_Anisotropic(float at, float ab, float ToV, float BoV,
        float ToL, float BoL, float NoV, float NoL) {
    float lambdaV = NoL * length(vec3(at * ToV, ab * BoV, NoV));
    float lambdaL = NoV * length(vec3(at * ToL, ab * BoL, NoL));
    float v = 0.5 / (lambdaV + lambdaL);
    return saturateMediump(v);
}
```
*リスト [anisotropicV]: 異方性 visibility 関数の GLSL 実装*

### Anisotropic のパラメータ化

異方性マテリアルモデルは、標準マテリアルモードに対して以前に定義されたすべてのパラメータに加えて、表 [anisotropicParameters] に記載された追加パラメータを含みます。

| パラメータ | 定義 |
| ---: | :--- |
| **Anisotropy** | 異方性の量。-1 から 1 までのスカラー |
*表 [anisotropicParameters]: Anisotropic モデルのパラメータ*

さらなるリマッピングは必要ありません。負の値は、異方性を tangent 方向ではなく bitangent 方向に合わせることに注意してください。図 [anisotropyParameter] は、anisotropy パラメータが粗い金属サーフェスの外観にどのように影響するかを示しています。

![](/images/filament-md-ja/materials/anisotropy.png)
*図 [anisotropyParameter]: Anisotropy を 0.0（左）から 1.0（右）まで変化させた様子*

---

原文: https://google.github.io/filament/Filament.html
