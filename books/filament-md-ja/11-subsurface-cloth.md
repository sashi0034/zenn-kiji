---
title: "Subsurface / Cloth モデル"
---

## Subsurface モデル

[TODO]

### Subsurface specular BRDF

[TODO]

### Subsurface のパラメータ化

[TODO]

## Cloth モデル

これまでに説明したすべてのマテリアルモデルは、マクロレベルとミクロレベルの両方で密なサーフェスをシミュレートするように設計されています。しかし、衣服や布地は、入射光を吸収および散乱する、緩く接続された糸で作られていることがよくあります。前述したマイクロファセット BRDF は、サーフェスが完全な鏡として振る舞うランダムな溝で構成されているという根本的な仮定があるため、布地の性質を再現するには不十分です。硬いサーフェスと比較すると、布地は大きなフォールオフを持つ柔らかい specular lobe と、前方/後方散乱によって引き起こされるファズライティングの存在が特徴です。一部の布地（例えばベルベット）は、2 トーンの specular カラーも示します。

図 [materialCloth] は、伝統的なマイクロファセット BRDF がデニム布地のサンプルの外観を捉えることに失敗する様子を示しています。サーフェスは硬く（ほぼプラスチックのように）見え、衣服の一部というよりもタープに近い印象です。この図は、吸収と散乱によって引き起こされる柔らかい specular lobe が、布地の忠実な再現にとっていかに重要であるかも示しています。

![](/images/filament-md-ja/screenshot_cloth.png)
*図 [materialCloth]: 伝統的なマイクロファセット BRDF（左）と私たちの cloth BRDF（右）を使用してレンダリングされたデニム布地の比較*

ベルベットは、cloth マテリアルモデルにとって興味深いユースケースです。図 [materialVelvet] に示すように、このタイプの布地は、前方および後方散乱による強いリムライティングを示します。これらの散乱イベントは、布地の表面で垂直に立っている繊維によって引き起こされます。入射光がビュー方向と反対の方向から来る場合、繊維は光を前方散乱します。同様に、入射光がビュー方向と同じ方向から来る場合、繊維は光を後方散乱します。

![](/images/filament-md-ja/screenshot_cloth_velvet.png)
*図 [materialVelvet]: 前方および後方散乱を示すベルベット布地*

繊維は柔軟であるため、理論的にはサーフェスをグルーミングする能力をモデル化する必要があります。私たちのモデルはこの特性を再現しませんが、繊維の方向のランダムな分散に起因する、可視的な正面の specular 寄与をモデル化しています。

硬いサーフェスマテリアルモデルで最もよくモデル化される布地のタイプがあることに注意することが重要です。例えば、革、シルク、サテンは、[標準](./04-material-standard)または[異方性](./10-anisotropic)マテリアルモデルを使用して再現できます。

### Cloth specular BRDF

私たちが使用する cloth specular BRDF は、[#Ashikhmin07] で Ashikhmin と Premoze によって説明されているように、変更されたマイクロファセット BRDF です。彼らの研究において、Ashikhmin と Premoze は、分布項が BRDF に最も寄与し、shadowing/masking 項は彼らのベルベット分布には必要ないと指摘しています。分布項自体は、反転ガウス分布です。これにより、ファズライティング（前方および後方散乱）を実現しながら、正面の specular 寄与をシミュレートするためにオフセットが追加されます。いわゆるベルベット NDF は次のように定義されます：

$$
D_{velvet}(v,h,\alpha) = c_{norm}(1 + 4 exp\left(\frac{-{cot}^2\theta_{h}}{\alpha^2}\right))
$$

この NDF は、同じ著者が [#Ashikhmin00] で説明している NDF のバリアントであり、特にオフセット（ここでは 1 に設定）と振幅（4）を含むように変更されています。[#Neubelt13] で、Neubelt と Pettineo は、この NDF の正規化バージョンを提案しています：

$$
D_{velvet}(v,h,\alpha) = \frac{1}{\pi(1 + 4\alpha^2)} (1 + 4 \frac{exp\left(\frac{-{cot}^2\theta_{h}}{\alpha^2}\right)}{{sin}^4\theta_{h}})
$$

完全な specular BRDF については、[#Neubelt13] にも従い、伝統的な分母をより滑らかなバリアントで置き換えます：

$$
f_{r}(v,h,\alpha) = \frac{D_{velvet}(v,h,\alpha)}{4(n \cdot l + n \cdot v - (n \cdot l)(n \cdot v))}
$$

ベルベット NDF の実装は、リスト [clothBRDF] に示されており、half float フォーマットに適切に収まるように最適化され、高価なコタンジェントの計算を避けて三角関数の恒等式に依存しています。この BRDF から Fresnel 成分を削除したことに注意してください。

```glsl
float D_Ashikhmin(float roughness, float NoH) {
    // Ashikhmin 2007, "Distribution-based BRDFs"
	float a2 = roughness * roughness;
	float cos2h = NoH * NoH;
	float sin2h = max(1.0 - cos2h, 0.0078125); // 2^(-14/2), so sin2h^2 > 0 in fp16
	float sin4h = sin2h * sin2h;
	float cot2 = -cos2h / (a2 * sin2h);
	return 1.0 / (PI * (4.0 * a2 + 1.0) * sin4h) * (4.0 * exp(cot2) + sin4h);
}
```
*リスト [clothBRDF]: Ashikhmin のベルベット NDF の GLSL 実装*

[#Estevez17] で、Estevez と Kulla は、反転ガウスではなく累乗正弦に基づく異なる NDF（「Charlie」シーンと呼ばれる）を提案しています。この NDF は、いくつかの理由で魅力的です：そのパラメータ化がより自然で直感的に感じられ、より柔らかい外観を提供し、式 `charlieNDF` に示すように、その実装がより単純です：

$$
D(m) = \frac{(2 + \frac{1}{\alpha}) sin(\theta)^{\frac{1}{\alpha}}}{2 \pi}
$$

[#Estevez17] は、そのコストのためにここでは省略する新しいシャドウイング項も提示しています。代わりに、[#Neubelt13] の visibility 項（上記の式 `clothSpecularBRDF` に示されています）に依存しています。
この NDF の実装は、リスト [clothCharlieBRDF] に示されており、half float フォーマットに適切に収まるように最適化されています。

```glsl
float D_Charlie(float roughness, float NoH) {
    // Estevez and Kulla 2017, "Production Friendly Microfacet Sheen BRDF"
    float invAlpha  = 1.0 / roughness;
    float cos2h = NoH * NoH;
    float sin2h = max(1.0 - cos2h, 0.0078125); // 2^(-14/2), so sin2h^2 > 0 in fp16
    return (2.0 + invAlpha) * pow(sin2h, invAlpha * 0.5) / (2.0 * PI);
}
```
*リスト [clothCharlieBRDF]: 「Charlie」NDF の GLSL 実装*

#### Sheen color

布地の外観をより良く制御し、ユーザーに 2 トーンの specular マテリアルを再現する能力を与えるために、specular reflectance を直接変更する機能を導入します。図 [materialClothSheen] は、私たちが「sheen color」と呼ぶパラメータを使用した例を示しています。

![](/images/filament-md-ja/screenshot_cloth_sheen.png)
*図 [materialClothSheen]: sheen なし（左）と sheen あり（右）の青い布地*

### Cloth diffuse BRDF

私たちの cloth マテリアルモデルは、依然として Lambertian diffuse BRDF に依存しています。ただし、エネルギー保存を実現するようにわずかに変更されており（clear coat マテリアルモデルのエネルギー保存に類似）、オプションの subsurface scattering 項を提供します。この追加項は物理ベースではなく、特定のタイプの布地における光の散乱、部分的な吸収、および再放出をシミュレートするために使用できます。

まず、オプションの subsurface scattering なしの diffuse 項を示します：

$$
f_{d}(v,h) = \frac{c_{diff}}{\pi}(1 - F(v,h))
$$

ここで、$F(v,h)$ は式 `clothSpecularBRDF` の cloth specular BRDF の Fresnel 項です。実際には、diffuse 成分で $1 - F(v, h)$ 項を省略することにしました。効果はかなり微妙で、追加コストに見合う価値はないと判断しました。

Subsurface scattering は、エネルギー保存形式のラップド diffuse ライティング技術を使用して実装されています：

$$
f_{d}(v,h) = \frac{c_{diff}}{\pi}(1 - F(v,h)) \left< \frac{n \cdot l + w}{(1 + w)^2} \right> \left< c_{subsurface} + n \cdot l \right>
$$

ここで、$w$ は 0 から 1 の間の値で、diffuse light がターミネーターの周りでどの程度ラップするかを定義します。別のパラメータを導入しないように、$w = 0.5$ に固定します。ラップ diffuse ライティングでは、diffuse 項に $n \cdot l$ を掛けてはいけないことに注意してください。この安価な subsurface scattering 近似の効果は、図 [materialClothSubsurface] で見ることができます。

![](/images/filament-md-ja/screenshot_cloth_subsurface.png)
*図 [materialClothSubsurface]: 白い布地（左列）と茶色の subsurface scattering を持つ白い布地（右）*

sheen color とオプションの subsurface scattering を含む、私たちの cloth BRDF の完全な実装は、リスト [clothFullBRDF] にあります。

```glsl
// specular BRDF
float D = distributionCloth(roughness, NoH);
float V = visibilityCloth(NoV, NoL);
vec3  F = sheenColor;
vec3 Fr = (D * V) * F;

// diffuse BRDF
float diffuse = diffuse(roughness, NoV, NoL, LoH);
#if defined(MATERIAL_HAS_SUBSURFACE_COLOR)
// エネルギー保存的なラップ diffuse
diffuse *= saturate((dot(n, light.l) + 0.5) / 2.25);
#endif
vec3 Fd = diffuse * pixel.diffuseColor;

#if defined(MATERIAL_HAS_SUBSURFACE_COLOR)
// 安価な subsurface scatter
Fd *= saturate(subsurfaceColor + NoL);
vec3 color = Fd + Fr * NoL;
color *= (lightIntensity * lightAttenuation) * lightColor;
#else
vec3 color = Fd + Fr;
color *= (lightIntensity * lightAttenuation * NoL) * lightColor;
#endif
```
*リスト [clothFullBRDF]: 私たちの cloth BRDF の GLSL 実装*

### Cloth のパラメータ化

cloth マテリアルモデルは、標準マテリアルモードに対して以前に定義されたすべてのパラメータを含みますが、_metallic_ と _reflectance_ は除外されます。表 [clothParameters] に記載された 2 つの追加パラメータも利用可能です。

| パラメータ | 定義 |
| ---: | :--- |
| **SheenColor** | 2 トーンの specular 布地を作成するための specular ティント（デフォルトは標準の reflectance に合わせて 0.04） |
| **SubsurfaceColor** | マテリアルを通過して散乱および吸収された後の diffuse color のティント |
*表 [clothParameters]: Cloth モデルのパラメータ*

ベルベットのようなマテリアルを作成するには、ベースカラーを黒（または暗い色）に設定できます。色度情報は代わりに sheen color に設定する必要があります。デニム、コットンなどのより一般的な布地を作成するには、色度にベースカラーを使用し、デフォルトの sheen color を使用するか、sheen color をベースカラーの輝度に設定します。

---

原文: https://google.github.io/filament/Filament.html
