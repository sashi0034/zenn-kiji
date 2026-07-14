---
title: "Clear coat モデル"
---

## Clear coat モデル

これまでに説明した[標準マテリアルモデル](./04-material-standard)は、単一レイヤーで構成される等方性サーフェスに適しています。しかし残念ながら、複数レイヤーで構成されるマテリアル、特に標準レイヤーの上に薄い半透明レイヤーが乗っているマテリアルは非常に一般的です。このようなマテリアルの実例としては、車の塗装、ソーダ缶、ラッカー塗装された木材、アクリルなどがあります。

![](/images/filament-md-ja/material_clear_coat.png)
*図 [materialClearCoat]: 標準マテリアルモデル（左）と clear coat モデル（右）での青い金属表面の比較*

clear coat レイヤーは、2 つ目の specular lobe を追加することで標準マテリアルモデルの拡張としてシミュレートできます。これは 2 つ目の specular BRDF を評価することを意味します。実装とパラメータ化を簡素化するため、clear coat レイヤーは常に等方性かつ誘電体とします。ベースレイヤーは標準モデルで許可されているもの（誘電体または導体）であれば何でも構いません。

入射光が clear coat レイヤーを通過するため、図 [clearCoatModel] に示すように、エネルギーの損失も考慮する必要があります。ただし、私たちのモデルでは相互反射と屈折の挙動はシミュレートしません。

![](/images/filament-md-ja/diagram_clear_coat.png)
*図 [clearCoatModel]: Clear coat サーフェスモデル*

### Clear coat specular BRDF

clear coat レイヤーは、標準モデルで使用しているものと同じ Cook-Torrance マイクロファセット BRDF を使ってモデル化されます。clear coat レイヤーは常に等方性かつ誘電体であり、粗さの値が低い（セクション [Clear coat のパラメータ化](#clear-coat-のパラメータ化)を参照）ため、視覚的な品質を著しく損なうことなく、より安価な DFG 項を選択できます。

[#Karis13a] と [#Burley12] にリストされている項を調査すると、標準モデルですでに使用している Fresnel と NDF の項は、他の項と比べて計算コストが高くないことがわかります。[#Kelemen01] では、Smith-GGX visibility 項を置き換えることができる、より単純な項が説明されています：

$$
V(l,h) = \frac{1}{4(l \cdot h)^2}
$$

この masking-shadowing 関数は、[#Heitz14] で示されているように物理ベースではありませんが、その単純さがリアルタイムレンダリングにおいて望ましいものとなっています。

まとめると、私たちの clear coat BRDF は Cook-Torrance specular マイクロファセットモデルであり、GGX 法線分布関数、Kelemen visibility 関数、Schlick Fresnel 関数を使用します。リスト [kelemen] は、GLSL 実装がいかに簡単であるかを示しています。

```glsl
float V_Kelemen(float LoH) {
    return 0.25 / (LoH * LoH);
}
```
*リスト [kelemen]: Kelemen visibility 項の GLSL 実装*

**Fresnel 項に関する注意**

specular BRDF の Fresnel 項には、法線入射角での specular reflectance である $f_{0}$ が必要です。このパラメータは界面の屈折率から計算できます。clear coat レイヤーはポリウレタン、または[コーティングやワニスに使用される](https://en.wikipedia.org/wiki/List_of_polyurethane_applications#Varnish)一般的な化合物、あるいは類似のもので作られていると仮定します。空気とポリウレタンの界面は [IOR が 1.5](http://www.clearpur.com/transparent-polyurethanes/) であり、ここから $f_{0}$ を導き出すことができます：

$$
f_{0}(1.5) = \frac{(1.5 - 1)^2}{(1.5 + 1)^2} = 0.04
$$

これは、一般的な誘電体材料に関連付けられている 4% の Fresnel reflectance に相当します。

### サーフェスレスポンスへの統合

clear coat レイヤーの追加によって引き起こされるエネルギーの損失を考慮する必要があるため、式 `brdf` の BRDF を次のように再定式化できます：

$$
f(v,l)=f_d(v,l) (1 - F_c) + f_r(v,l) (1 - F_c) + f_c(v,l)
$$

ここで、$F_c$ は clear coat BRDF の Fresnel 項で、$f_c$ は clear coat BRDF です。

### Clear coat のパラメータ化

clear coat マテリアルモデルは、標準マテリアルモードに対して以前に定義されたすべてのパラメータに加えて、表 [clearCoatParameters] に記載された 2 つのパラメータを含みます。

| パラメータ | 定義 |
| ---: | :--- |
| **ClearCoat** | clear coat レイヤーの強度。0 から 1 までのスカラー |
| **ClearCoatRoughness** | clear coat レイヤーの知覚的な滑らかさまたは粗さ。0 から 1 までのスカラー |
*表 [clearCoatParameters]: Clear coat モデルのパラメータ*

clear coat の粗さパラメータは、標準マテリアルの粗さパラメータと同様の方法でリマップおよびクランプされます。

図 [clearCoat] と図 [clearCoatRoughness] は、clear coat パラメータがサーフェスの外観にどのように影響するかを示しています。

![](/images/filament-md-ja/material_clear_coat1.png)
*図 [clearCoat]: Clear coat を 0.0（左）から 1.0（右）まで変化させた様子（metallic を 1.0、roughness を 0.8 に設定）*
![](/images/filament-md-ja/material_clear_coat2.png)
*図 [clearCoatRoughness]: Clear coat roughness を 0.0（左）から 1.0（右）まで変化させた様子（metallic を 1.0、roughness を 0.8、clear coat を 1.0 に設定）*

リスト [clearCoatBRDF] は、リマップ、パラメータ化、および標準サーフェスレスポンスへの統合後の clear coat マテリアルモデルの GLSL 実装を示しています。

```glsl
void BRDF(...) {
    // 標準モデルから Fd と Fr を計算

    // clear coat roughness のリマップと線形化
    clearCoatPerceptualRoughness = clamp(clearCoatPerceptualRoughness, 0.089, 1.0);
    clearCoatRoughness = clearCoatPerceptualRoughness * clearCoatPerceptualRoughness;

    // clear coat BRDF
    float  Dc = D_GGX(clearCoatRoughness, NoH);
    float  Vc = V_Kelemen(clearCoatRoughness, LoH);
    float  Fc = F_Schlick(0.04, LoH) * clearCoat; // clear coat 強度
    float Frc = (Dc * Vc) * Fc;

    // ベースレイヤーのエネルギー損失を考慮
    return color * ((Fd + Fr) * (1.0 - Fc) + Frc);
}
```
*リスト [clearCoatBRDF]: clear coat BRDF の GLSL 実装*

### ベースレイヤーの変更

clear coat レイヤーの存在は、$f_{0}$ を再計算する必要があることを意味します。通常、$f_{0}$ は空気とマテリアルの界面に基づいているためです。したがって、ベースレイヤーでは、$f_{0}$ を clear coat とマテリアルの界面に基づいて計算する必要があります。

これは、マテリアルの屈折率（IOR）を $f_{0}$ から計算し、次に新しく計算された IOR と clear coat レイヤーの IOR（1.5）に基づいて新しい $f_{0}$ を計算することで実現できます。

まず、ベースレイヤーの IOR を計算します：

$$
IOR_{base} = \frac{1 + \sqrt{f_{0}}}{1 - \sqrt{f_{0}}}
$$

次に、この新しい屈折率から新しい $f_{0}$ を計算します：

$$
f_{0_{base}} = \left( \frac{IOR_{base} - 1.5}{IOR_{base} + 1.5} \right) ^2
$$

clear coat レイヤーの IOR は固定されているため、両方のステップを組み合わせて簡素化できます：

$$
f_{0_{base}} = \frac{\left( 1 - 5 \sqrt{f_{0}} \right) ^2}{\left( 5 - \sqrt{f_{0}} \right) ^2}
$$

また、clear coat レイヤーの IOR に基づいてベースレイヤーの見かけの粗さも変更する必要がありますが、これは現時点では省略することにしました。

---

原文: https://google.github.io/filament/Filament.html
