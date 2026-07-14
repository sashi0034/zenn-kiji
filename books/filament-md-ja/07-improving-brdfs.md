---
title: "BRDF の改善"
---

セクション [Energy conservation] で、エネルギー保存則が優れた BRDF の重要な構成要素の 1 つであると述べました。残念ながら、これまでに検討した BRDF は、以下で検討する 2 つの問題に悩まされています。

## Diffuse reflectance におけるエネルギーゲイン

Lambert diffuse BRDF は、サーフェスで反射するため diffuse 散乱イベントに参加できない光を考慮していません。

[TODO: $f_r$ + $f_d$ の問題について記述する]

## Specular reflectance におけるエネルギー損失

先ほど提示した Cook-Torrance BRDF は、マイクロファセットレベルで複数のイベントをモデル化しようとしますが、光の単一バウンスを考慮することでそれを行います。この近似は、高 roughness でエネルギー損失を引き起こす可能性があり、サーフェスはエネルギー保存則に従いません。図 [singleVsMultiBounce] は、このエネルギー損失が発生する理由を示しています。単一バウンス（または単一散乱）モデルでは、サーフェスに当たる光線が別のマイクロファセットに反射され、マスキングとシャドウイング項のために破棄される可能性があります。しかし、複数のバウンス（マルチスキャタリング）を考慮すると、同じ光線がマイクロファセットフィールドから抜け出し、視聴者に向かって反射される可能性があります。

![](/images/filament-md-ja/diagram_single_vs_multi_scatter.png)
*図 [singleVsMultiBounce]: 単一散乱（左）vs マルチスキャタリング*

この簡単な説明に基づいて、サーフェスが粗いほど、複数の散乱イベントを考慮しないためにエネルギーが失われる可能性が高くなることを直感的に推測できます。このエネルギー損失により、粗いマテリアルが暗くなるように見えます。金属サーフェスは、すべての reflectance が specular であるため、特に影響を受けます。この暗化効果は図 [metallicRoughEnergyLoss] に示されています。マルチスキャタリングを使用すると、図 [metallicRoughEnergyPreservation] に示すように、エネルギー保存則を達成できます。

![](/images/filament-md-ja/material_metallic_energy_loss.png)
*図 [metallicRoughEnergyLoss]: 単一散乱により roughness とともに暗化が増加*
![](/images/filament-md-ja/material_metallic_energy_preservation.png)
*図 [metallicRoughEnergyPreservation]: マルチスキャタリングによるエネルギー保存*

ホワイトファーネス（純白に設定された均一なライティング環境）を使用して、BRDF のエネルギー保存特性を検証できます。エネルギー保存が達成されると、純粋に反射する金属サーフェス（$f_{0} = 1$）は、そのサーフェスの roughness に関係なく、背景と区別がつかないはずです。図 [whiteFurnaceLoss] は、前のセクションで提示した specular BRDF を使用した場合のそのようなサーフェスの外観を示しています。roughness が増加するにつれてのエネルギー損失は明らかです。対照的に、図 [whiteFurnacePreservation] は、マルチスキャタリングイベントを考慮することでエネルギー損失に対処できることを示しています。

![](/images/filament-md-ja/material_furnace_energy_loss.png)
*図 [whiteFurnaceLoss]: 単一散乱により roughness とともに暗化が増加*
![](/images/filament-md-ja/material_furnace_energy_preservation.png)
*図 [whiteFurnacePreservation]: マルチスキャタリングによるエネルギー保存*

複数散乱マイクロファセット BRDF は [#Heitz16] で詳しく議論されています。残念ながら、この論文はマルチスキャタリング BRDF の確率的評価のみを提示しています。したがって、この解決策はリアルタイムレンダリングには適していません。Kulla と Conty は [#Kulla17] で別のアプローチを提示しています。彼らのアイデアは、式 `energyCompensationLobe` に示すように、追加の BRDF ローブとしてエネルギー補償項を追加することです。

$$
f_{ms}(l,v) = \frac{(1 - E(l)) (1 - E(v)) F_{avg}^2 E_{avg}}{\pi (1 - E_{avg}) (1 - F_{avg}(1 - E_{avg}))}
$$

ここで、$E$ は specular BRDF $f_r$ の directional albedo であり、$f_{0}$ は 1 に設定されています。

$$
E(l) = \int_{\Omega} f(l,v) (n \cdot v) dv
$$

項 $E_{avg}$ は $E$ のコサイン重み付き平均です。

$$
E_{avg} = 2 \int_0^1 E(\mu) \mu d\mu
$$

同様に、$F_{avg}$ は Fresnel 項のコサイン重み付き平均です。

$$
F_{avg} = 2 \int_0^1 F(\mu) \mu d\mu
$$

項 $E$ と $E_{avg}$ の両方は事前計算してルックアップテーブルに保存できます。一方、$F_{avg}$ は Schlick 近似を使用する場合に大幅に簡略化できます。

$$
F_{avg} = \frac{1 + 20 f_{0}}{21}
$$

この新しいローブは、以前に $f_r$ と表記された元の単一散乱ローブと組み合わされます。

$$
f_{r}(l,v) = f_{ss}(l,v) + f_{ms}(l,v)
$$

[#Lagarde18] で、Lagarde と Golubev は、Emmanuel Turquin の功績として、式 `averageFresnel` を $f_{0}$ に簡略化できることを観察しています。彼らはまた、スケールされた GGX specular ローブを追加することでエネルギー補償を適用することを提案しています。

$$
f_{ms}(l,v) = f_{0} \frac{1 - E(l)}{E(l)} f_{ss}(l,v)
$$

重要な洞察は、$E(l)$ が事前計算できるだけでなく、image-based lighting の事前統合と共有できることです。したがって、マルチスキャタリングエネルギー補償式は次のようになります。

$$
f_r(l,v) = f_{ss}(l,v) + f_{0} \left( \frac{1}{r} - 1 \right) f_{ss}(l,v)
$$

ここで、$r$ は次のように定義されます。

$$
r = \int_{\Omega} D(l,v) V(l,v) \left< n \cdot l \right> dl
$$

セクション [Image based lights] で提示された DFG ルックアップテーブルに $r$ を保存すれば、specular エネルギー補償を無視できるコストで実装できます。リスト [energyCompensationImpl] は、実装が式 `scaledEnergyCompensationLobe` の直接変換であることを示しています。

```glsl
vec3 energyCompensation = 1.0 + f0 * (1.0 / dfg.y - 1.0);
// マルチスキャタリングを考慮して specular ローブをスケール
Fr *= pixel.energyCompensation;
```
*リスト [energyCompensationImpl]: エネルギー補償 specular ローブの実装*

DFG ルックアップテーブルがどのように導出され計算されるかについては、セクション [Image based lights] とセクション [Pre-integration for multiscattering] を参照してください。

---

原文: https://google.github.io/filament/Filament.html
