---
title: "Direct lighting（直接光）"
---

上記のセクションでレンダラーがサポートするすべてのライトタイプの単位を定義しましたが、ライティング方程式の結果のライト単位は定義していません。物理的なライト単位を選択するということは、シェーダー内で輝度値を計算することを意味し、したがってすべてのライト評価関数は、任意の点における輝度 $L_{out}$（または出射放射輝度）を計算することになります。輝度は照度 $E$ と BSDF $f(v,l)$ に依存します。

$$
L_{out} = f(v,l)E
$$

## 指向性ライト

指向性ライトの主な目的は、屋外環境における重要な光源、すなわち太陽や月を再現することです。指向性ライトは物理世界には真には存在しませんが、光受容体から十分に離れた光源は指向性であると仮定できます（つまり、図 [directionalLight] に示すように、すべての入射光線が平行です）。

![](/images/filament-md-ja/diagram_directional_light.png)
*図 [directionalLight]: 指向性ライトと表面の相互作用。光源は方向のみで表現できる仮想的な構造です*

この近似は、表面の拡散応答に対しては非常にうまく機能しますが、鏡面応答は正確ではありません。Frostbite エンジンは、「太陽」の指向性ライトをディスクエリアライトとして扱うことでこの問題を解決しています。しかし、私たちのテストでは、品質の向上が追加の計算コストを正当化しないことが示されています。

前述のとおり、指向性ライトには照度単位（$lx$）を選択しました。これは、空や太陽の照度値を簡単に見つけられる（オンラインまたは照度計を使用）ことに加え、式 `luminanceEquation` で説明した輝度方程式を簡略化するためでもあります。

$$
L_{out} = f(v,l) E_{\bot} \left< n \cdot l \right>
$$

簡略化された輝度方程式 `directionalLuminanceEquation` において、$E_{\bot}$ は光源に垂直な表面に対する光源の照度です。指向性光源が太陽をシミュレートする場合、$E_{\bot}$ は太陽の方向に垂直な表面に対する太陽の照度です。

表 [sunSkyIlluminance] は、カリフォルニアで3月の晴れた日に測定された[^illuminanceMeasures]、太陽と空の照明の有用な参考値を示しています。

| Light | 10am | 12pm | 5:30pm |
| ---: | ---: | ---: | ---: |
| $Sky_{\bot} + Sun_{\bot}$ | 120,000 | 130,000 | 90,000 |
| $Sky_{\bot}$ | 20,000 | 25,000 | 9,000 |
| $Sun_{\bot}$ | 100,000 | 105,000 | 81,000 |
*表 [sunSkyIlluminance]: $lx$ 単位の照度値（満月の照度は 1 $lx$）*

動的な指向性ライトは、リスト [glslDirectionalLight] に示すように、実行時の評価が特に安価です。

```glsl
vec3 l = normalize(-lightDirection);
float NoL = clamp(dot(n, l), 0.0, 1.0);

// lightIntensity is the illuminance
// at perpendicular incidence in lux
float illuminance = lightIntensity * NoL;
vec3 luminance = BSDF(v, l) * illuminance;
```
*リスト [glslDirectionalLight]: GLSL での指向性ライトの実装*

図 [directionalLightTest] は、正午の太陽を近似するように設定した指向性ライト（照度を 110,000 $lx$ に設定）でシンプルなシーンを照明した効果を示しています。説明のため、直接照明のみを表示しています。

![](/images/filament-md-ja/screenshot_directional_light.png)
*図 [directionalLightTest]: 指向性ライト下でのさまざまな粗さの誘電体材料のシリーズ*

[^illuminanceMeasures]: 入射光測定器（Sekonic L-478D）で測定

## 点光源

私たちのエンジンは、ほとんどのレンダリングエンジンで一般的に見られる2種類の点光源をサポートします：ポイントライトとスポットライトです。これらのタイプのライトは、伝統的に次の2つの理由で物理的に不正確です。

1. それらは真に点状で無限小です。
2. [逆二乗則](http://en.wikipedia.org/wiki/Inverse-square_law)に従いません。

最初の問題はエリアライトで対処できますが、点光源の安価な性質を考えると、可能な限り無限小の点光源を使用することが実用的とみなされます。

2番目の問題は簡単に修正できます。与えられた点光源について、知覚される強度は視点（より正確には光受容体）からの距離の二乗に反比例して減少します。

逆二乗則に従う点光源の場合、式 `luminanceEquation` の項 $E$ は式 `punctualLightEquation` で表され、ここで $d$ は表面上の点から光源までの距離です。

$$
E = L_{in} \left< n \cdot l \right> = \frac{I}{d^2} \left< n \cdot l \right>
$$

ポイントライトとスポットライトの違いは、$E$ の計算方法、特に光束 $\Phi$ から光度 $I$ を計算する方法にあります。

### ポイントライト

ポイントライトは、図 [pointLight] に示すように、空間内の位置のみで定義されます。

![](/images/filament-md-ja/diagram_point_light.png)
*図 [pointLight]: ポイントライトと表面の相互作用。減衰は光源までの距離にのみ依存します*

ポイントライトの光束は、式 `pointLightLuminousPower` に示すように、光の立体角で光度を積分することによって計算されます。光度は光束から簡単に導出できます。

$$
\Phi = \int_{\Omega} I dl = \int_{0}^{2\pi} \int_{0}^{\pi} I d\theta d\phi = 4 \pi I \\
I = \frac{\Phi}{4 \pi}
$$

`punctualLightEquation` の $I$ と `luminanceEquation` の $E$ を単純に代入することで、ポイントライトの輝度方程式を光束の関数として定式化できます（`pointLightLuminanceEquation` 参照）。

$$
L_{out} = f(v,l) \frac{\Phi}{4 \pi d^2} \left< n \cdot l \right>
$$

図 [pointLightTest] は、距離減衰の影響を受けるポイントライトでシンプルなシーンを照明した効果を示しています。説明のため、光の減衰が誇張されています。

![](/images/filament-md-ja/screenshot_point_light.png)
*図 [pointLightTest]: ポイントライト評価に適用された逆二乗則*

### スポットライト

スポットライトは、空間内の位置、方向ベクトル、2つの円錐角 $\theta_{inner}$ と $\theta_{outer}$ で定義されます（図 [spotLight] 参照）。これら2つの角度は、スポットライトの角度減衰を定義するために使用されます。したがって、スポットライトのライト評価関数は、輝度減衰を適切に評価するために、逆二乗則とこれら2つの角度の両方を考慮する必要があります。

![](/images/filament-md-ja/diagram_spot_light.png)
*図 [spotLight]: スポットライトと表面の相互作用。減衰は光源までの距離と、表面とスポットライトの方向ベクトル間の角度に依存します*

式 `spotLightLuminousPower` は、ポイントライトと同様の方法でスポットライトの光束を計算する方法を説明しており、スポットライトの円錐の外角 $\theta_{outer}$ を [0..$\pi$] の範囲で使用します。

$$
\Phi = \int_{\Omega} I dl = \int_{0}^{2\pi} \int_{0}^{\theta_{outer}} I d\theta d\phi = 2 \pi (1 - cos\frac{\theta_{outer}}{2})I \\
I = \frac{\Phi}{2 \pi (1 - cos\frac{\theta_{outer}}{2})}
$$

この定式化は物理的に正しいものの、スポットライトを少し使いにくくします：円錐の外角を変更すると照明レベルが変化します。図 [spotLightTestFocused] は、外角が55度と15度のスポットライトで照明された同じシーンを示しています。円錐の開口が減少するにつれて照明レベルが増加することに注目してください。

![](/images/filament-md-ja/screenshot_spot_light_focused.png)
*図 [spotLightTestFocused]: スポットライトの外角の比較、55度（左）と15度（右）*

照明と外円錐の結合は、アーティストがスポットライトの影響範囲を調整する際に、知覚される照明も変更してしまうことを意味します。したがって、この結合を無効にするパラメータをアーティストに提供することが理にかなっています。式 `spotLightLuminousPowerB` は、その目的のために光束を定式化する方法を示しています。

$$
\Phi = \pi I \\
I = \frac{\Phi}{\pi} \\
$$

この新しい定式化で光度を計算すると、図 [spotLightTest] のテストシーンは、両方の円錐開口で同様の照明レベルを示します。

![](/images/filament-md-ja/screenshot_spot_light.png)
*図 [spotLightTest]: スポットライトの外角の比較、55度（左）と15度（右）*

この新しい定式化は、スポットの反射板を完全に光を吸収するマットな拡散マスクに置き換えた場合にも、物理ベースと見なすことができます。

スポットライト評価関数は、2つの方法で表現できます。

- **光吸収体を使用**
  $$
L_{out} = f(v,l) \frac{\Phi}{\pi d^2} \left< n \cdot l \right> \lambda(l)
$$
- **光反射板を使用**
  $$
L_{out} = f(v,l) \frac{\Phi}{2 \pi (1 - cos\frac{\theta_{outer}}{2}) d^2} \left< n \cdot l \right> \lambda(l)
$$

式 `spotAbsorber` と `spotReflector` の項 $\lambda(l)$ は、以下の式 `spotAngleAtt` で説明されるスポットの角度減衰係数です。

$$
\lambda(l) = \frac{l \cdot spotDirection - cos\theta_{outer}}{cos\theta_{inner} - cos\theta_{outer}}
$$

### 減衰関数

物理ベースの点光源には、逆二乗則減衰係数の適切な評価が必須です。しかし、単純な数学的定式化は実装目的には実用的ではありません。

1. 距離の二乗による除算は、オブジェクトが光源と交差または「接触」するときにゼロ除算につながる可能性があります。

2. 各ライトの影響球は無限です（$\frac{I}{d^2}$ は漸近的で、決してゼロに達しません）。これは、ピクセルを正しくシェーディングするために、世界のすべてのライトを評価する必要があることを意味します。

最初の問題は、点光源が真に点状ではなく、代わりに小さなエリアライトであるという仮定を設定することで簡単に解決できます。これを行うには、式 `finitePunctualLight` に示すように、点光源を半径1cmの球として扱うだけです。

$$
E = \frac{I}{max(d^2, {0.01}^2)}
$$

2番目の問題は、各ライトに影響半径を導入することで解決できます。このソリューションにはいくつかの利点があります。ツールは、世界のどの部分が各ライトに影響されるかをアーティストに素早く示すことができます（ツールは各ライトを中心とした球を描画するだけです）。レンダリングエンジンは、この追加情報を使用してライトをより積極的にカリングでき、アーティスト/開発者はライトの影響半径を手動で調整することでエンジンを支援できます。

数学的には、ライトの照度は、影響半径によって定義される限界で滑らかにゼロに達する必要があります。[#Karis13b] は、ライトの影響の大部分が影響を受けないように、逆二乗関数をウィンドウ化することを提案しています。提案されたウィンドウ化は式 `attenuationWindowing` で説明されており、ここで $r$ はライトの影響半径です。

$$
E = \frac{I}{max(d^2, {0.01}^2)} \left< 1 - \frac{d^4}{r^4} \right>^2
$$

リスト [glslPunctualLight] は、GLSL で物理ベースの点光源を実装する方法を示しています。このコードで使用されるライト強度は、CPU側で光束から変換された $cd$ 単位の光度 $I$ であることに注意してください。このスニペットは最適化されておらず、一部の計算はCPUにオフロードできます（たとえば、ライトの逆減衰半径の二乗、またはスポットスケールと角度）。

```glsl
float getSquareFalloffAttenuation(vec3 posToLight, float lightInvRadius) {
    float distanceSquare = dot(posToLight, posToLight);
    float factor = distanceSquare * lightInvRadius * lightInvRadius;
    float smoothFactor = max(1.0 - factor * factor, 0.0);
    return (smoothFactor * smoothFactor) / max(distanceSquare, 1e-4);
}

float getSpotAngleAttenuation(vec3 l, vec3 lightDir,
        float innerAngle, float outerAngle) {
    // the scale and offset computations can be done CPU-side
    float cosOuter = cos(outerAngle);
    float spotScale = 1.0 / max(cos(innerAngle) - cosOuter, 1e-4)
    float spotOffset = -cosOuter * spotScale

    float cd = dot(normalize(-lightDir), l);
    float attenuation = clamp(cd * spotScale + spotOffset, 0.0, 1.0);
    return attenuation * attenuation;
}

vec3 evaluatePunctualLight() {
    vec3 l = normalize(posToLight);
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    vec3 posToLight = lightPosition - worldPosition;

    float attenuation;
    attenuation  = getSquareFalloffAttenuation(posToLight, lightInvRadius);
    attenuation *= getSpotAngleAttenuation(l, lightDir, innerAngle, outerAngle);

    vec3 luminance = (BSDF(v, l) * lightIntensity * attenuation * NoL) * lightColor;
    return luminance;
}
```
*リスト [glslPunctualLight]: GLSL での点光源の実装*

## 測光ライト

点光源は、シーンを照明する非常に実用的で効率的な方法ですが、アーティストに光の分布に対する十分な制御を与えません。建築照明デザインの分野は、次の点を考慮して人間のニーズに応える照明システムの設計に関心があります。

- 提供される光の量
- 光の色
- 空間内の光の分布

これまでに説明した照明システムは、最初の2点に簡単に対処できますが、空間内の光の分布を定義する方法が必要です。光の分布は、屋内シーンや一部の屋外シーン、さらには道路照明にとって特に重要です。図 [lightDistributionTest] は、アーティストが光の分布を制御するシーンを示しています。このタイプの分布制御は、オブジェクトを展示する際（例えば、博物館、店舗、ギャラリー）に広く使用されています。

![](/images/filament-md-ja/screenshot_photometric_lights.png)
*図 [lightDistributionTest]: ポイントライトの分布の制御*

測光ライトは、測光プロファイルを使用して強度分布を記述します。一般的に使用される形式は2つあり、IES（Illuminating Engineering Society）とEULUMDAT（European Lumen Data format）ですが、ここでは前者に焦点を当てます。IESプロファイルは、Unreal Engine 4、Frostbite、Renderman、Maya、Killzoneなど、多くのツールやエンジンでサポートされています。さらに、IESライトプロファイルは、電球や照明器具メーカーによって一般的に提供されています（例えば、Philipsは[豊富なIESファイル](http://www.usa.lighting.philips.com/connect/tools_literature/photometric_data_1.wpd)をダウンロード用に提供しています）。測光プロファイルは、光源が部分的に覆われている照明器具やライトフィクスチャを測定する場合に特に有用です。照明器具は特定の方向に放射される光を遮断し、光の分布を形作ります。

![](/images/filament-md-ja/photo_photometric_lights.jpg)
*実世界の照明器具の例。測光プロファイルで記述できます*

IESプロファイルは、測定された光源を囲む球上のさまざまな角度の光度を格納します。この球面座標系は通常、測光ウェブと呼ばれ、[IESviewer](http://www.photometricviewer.com/)などの専用ツールを使用して視覚化できます。図 [xarrow] は、[Pixarが提供する](http://renderman.pixar.com/view/DP25764)XArrow IESプロファイルの測光ウェブと、私たちのツール `lightgen` による3D空間でのレンダリングを示しています。

![](/images/filament-md-ja/screenshot_xarrow.png)
*図 [xarrow]: 測光ウェブとして、および3D空間のポイントライトとしてレンダリングされたXArrow IESプロファイル*

IES形式は文書化が不十分で、インターネット上で見つかるファイル間で構文のバリエーションが見られることは珍しくありません。IESプロファイルを理解するための最良のリソースは、Ian Ashdownの「Parsing the IESNA LM-63 photometric data file」ドキュメント [#Ashdown98] です。簡潔に言えば、IESプロファイルは、光源周りのさまざまな角度でのカンデラ単位の光度を格納します。測定された各水平角度について、異なる垂直角度での一連の光度が提供されます。ただし、測定された光源が水平方向に対称であることは一般的です。上記のXArrowプロファイルは良い例です：強度は垂直角度（垂直軸）によって変化しますが、水平軸上では対称です。IESプロファイルの垂直角度の範囲は0〜180度で、水平角度の範囲は0〜360度です。

図 [lightenSamples] は、私たちの `lightgen` ツールを使用してレンダリングされた、PixarがRenderman用に提供する一連のIESプロファイルを示しています。

![](/images/filament-md-ja/screenshot_lightgen_samples.png)
*図 [lightenSamples]: lightgenでレンダリングされた一連のIESライトプロファイル*

IESプロファイルは、ポイントライトまたはスポットライトの任意の点光源に直接適用できます。これを行うには、まずIESプロファイルを処理し、測光プロファイルをテクスチャとして生成する必要があります。パフォーマンス上の考慮事項から、私たちが生成する測光プロファイルは、特定の垂直角度でのすべての水平角度の平均光度を表す1Dテクスチャです（つまり、各ピクセルは垂直角度を表します）。測光ライトを真に表現するには2Dテクスチャを使用する必要がありますが、ほとんどのライトが水平面上で完全にまたはほぼ対称であるため、この近似を受け入れることができます。テクスチャに格納される値は、IESプロファイルで定義された最大強度の逆数で正規化されます。これにより、任意の浮動小数点形式、または精度を犠牲にして輝度8ビットテクスチャ（グレースケールPNGなど）にテクスチャを簡単に格納できます。正規化された値を格納することで、測光プロファイルをマスクとして扱うこともできます。

**マスクとしての測光プロファイル**

光度は、他の点光源と同様に、ライトの光束を設定することでアーティストによって定義されます。アーティストが定義した強度は、IESプロファイルから計算されたライトの強度で除算されます。IESプロファイルには光度が含まれていますが、それは裸の電球に対してのみ有効であり、測定された強度値はライトフィクスチャを考慮しています。電球ではなく照明器具の強度を測定するために、プロファイルからの強度を使用して単位球のモンテカルロ積分を実行します[^xarrowIntensity]。

**測光プロファイル**

光度はプロファイル自体から来ます。1Dテクスチャからサンプリングされたすべての値は、単に最大強度で乗算されます。便宜上、乗数も提供します。

測光プロファイルは、レンダリング時に単純な減衰として適用できます。輝度方程式 `photometricLightEvaluation` は、測光ポイントライト評価関数を説明しています。

$$
L_{out} = f(v,l) \frac{I}{d^2} \left< n \cdot l \right> \Psi(l)
$$

項 $\Psi(l)$ は測光減衰関数です。これは光ベクトルに依存するだけでなく、ライトの方向にも依存します。スポットライトはすでに方向ベクトルを持っていますが、測光ポイントライトにも方向ベクトルを導入する必要があります。

測光減衰関数は、点光源の実装（リスト [glslPunctualLight]）に新しい減衰係数を追加することで、GLSLで簡単に実装できます。変更された実装は、リスト [glslPhotometricPunctualLight] に示されています。

```glsl
float getPhotometricAttenuation(vec3 posToLight, vec3 lightDir) {
    float cosTheta = dot(-posToLight, lightDir);
    float angle = acos(cosTheta) * (1.0 / PI);
    return texture2DLodEXT(lightProfileMap, vec2(angle, 0.0), 0.0).r;
}

vec3 evaluatePunctualLight() {
    vec3 l = normalize(posToLight);
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    vec3 posToLight = lightPosition - worldPosition;

    float attenuation;
    attenuation  = getSquareFalloffAttenuation(posToLight, lightInvRadius);
    attenuation *= getSpotAngleAttenuation(l, lightDirection, innerAngle, outerAngle);
    attenuation *= getPhotometricAttenuation(l, lightDirection);

    float luminance = (BSDF(v, l) * lightIntensity * attenuation * NoL) * lightColor;
    return luminance;
}
```
*リスト [glslPhotometricPunctualLight]: GLSL での測光プロファイルからの減衰の実装*

ライト強度はCPU側で計算され（リスト [photometricLightIntensity]）、測光プロファイルがマスクとして使用されているかどうかに依存します。

```glsl
float multiplier;
// Photometric profile used as a mask
if (photometricLight.isMasked()) {
    // The desired intensity is set by the artist
    // The integrated intensity comes from a Monte-Carlo
    // integration over the unit sphere around the luminaire
    multiplier = photometricLight.getDesiredIntensity() /
            photometricLight.getIntegratedIntensity();
} else {
    // Multiplier provided for convenience, set to 1.0 by default
    multiplier = photometricLight.getMultiplier();
}

// The max intensity in cd comes from the IES profile
float lightIntensity = photometricLight.getMaxIntensity() * multiplier;
```
*リスト [photometricLightIntensity]: CPU上での測光ライトの強度の計算*

[^xarrowIntensity]: XArrowプロファイルは1,750 lmの光度を宣言していますが、モンテカルロ積分では350 lmの強度のみを示しています。

## エリアライト

[TODO]

## ライトのパラメータ化

標準マテリアルモデルのパラメータ化と同様に、私たちの目標は、アーティストと開発者の両方にとって直感的で使いやすいライトのパラメータ化を行うことです。その精神で、ライトの色（または色相）をライト強度から分離することにしました。したがって、ライトの色は線形RGB色（またはUIの便宜上sRGB）として定義されます。

ライトパラメータの完全なリストは、表 [lightParameters] に示されています。

| Parameter | Definition |
| ---: | :--- |
| **Type** | Directional、point、spot、area |
| **Direction** | 指向性ライト、スポットライト、測光ポイントライト、線形および管状エリアライトに使用（方向） |
| **Color** | 放射される光の色、線形RGB色として。ツールではsRGB色または色温度として指定可能 |
| **Intensity** | ライトの明るさ。単位はライトタイプに依存 |
| **Falloff radius** | 最大影響距離 |
| **Inner angle** | スポットライトの内側円錐の角度（度） |
| **Outer angle** | スポットライトの外側円錐の角度（度） |
| **Length** | エリアライトの長さ、線形または管状ライトの作成に使用 |
| **Radius** | エリアライトの半径、球状または管状ライトの作成に使用 |
| **Photometric profile** | 測光ライトプロファイルを表すテクスチャ、点光源にのみ機能 |
| **Masked profile** | IESプロファイルがマスクとして使用されるかどうかを示すブール値。マスクとして使用される場合、ライトの明るさは、ユーザー指定の強度と統合されたIESプロファイル強度の比で乗算されます。マスクとして使用されない場合、ユーザー指定の強度は無視されますが、IES乗数が代わりに使用されます |
| **Photometric multiplier** | 測光ライトの明るさ乗数（IESをマスクとして使用しない場合） |
*表 [lightParameters]: ライトタイプのパラメータ*

**注意**: 実装を簡略化するため、すべての光束はシェーダーに送信される前に光度（$cd$）に変換されます。変換はライトに依存し、前のセクションで説明されています。

**注意**: ライトタイプは他のパラメータから推測できます（例：ポイントライトは長さ、半径、内角、外角が0）。

### 色温度

しかし、実世界の人工光源は、ケルビン（K）で測定される色温度で定義されることがよくあります。光源の色温度は、光源の色相と類似した色相の光を放射する理想的な黒体放射体の温度です。便宜上、ツールはアーティストが光源の色相を色温度として指定できるようにする必要があります（意味のある範囲は1,000 K〜12,500 K）。

温度からRGB値を計算するには、図 [planckianLocus] に示されるプランクの軌跡を使用できます。この軌跡は、黒体の温度が変化するにつれて、白熱黒体の色が色度空間で辿る経路です。

![](/images/filament-md-ja/diagram_planckian_locus.png)
*図 [planckianLocus]: CIE 1931色度図上に視覚化されたプランクの軌跡（出典：Wikipedia）*

この軌跡からRGB値を計算する最も簡単な方法は、[#Krystek85] で説明されている式を使用することです。Krystekのアルゴリズム（式 `krystek`）はCIE 1960（UCS）空間で機能し、次の式を使用します。ここで $T$ は目的の温度、$u$ と $v$ はUCS内の座標です。

$$
u(T) = \frac{0.860117757 + 1.54118254 \times 10^{-4}T + 1.28641212 \times 10^{-7}T^2}{1 + 8.42420235 \times 10^{-4}T + 7.08145163 \times 10^{-7}T^2} \\
v(T) = \frac{0.317398726 + 4.22806245
 \times 10^{-5}T + 4.20481691 \times 10^{-8}T^2}{1 - 2.89741816
 \times 10^{-5}T + 1.61456053 \times 10^{-7}T^2}
$$

この近似は、1,000K〜15,000Kの範囲で約 $9 \times 10^{-5}$ まで正確です。CIE 1960空間から、式 `cieToxyY` を使用してxyY空間（CIES 1931）の座標を計算できます。

$$
x = \frac{3u}{2u - 8v + 4} \\
y = \frac{2v}{2u - 8v + 4}
$$

上記の式は、黒体色温度、したがって標準光源の相関色温度に有効です。Dシリーズの標準CIE光源の正確な色度座標を計算したい場合は、式 `seriesDtoxyY` を使用できます。

$$
x = \begin{cases} 0.244063 + 0.09911 \frac{10^3}{T} + 2.9678 \frac{10^6}{T^2} - 4.6070 \frac{10^9}{T^3} & 4,000K \le T \le 7,000K \\
0.237040 + 0.24748 \frac{10^3}{T} + 1.9018 \frac{10^6}{T^2} - 2.0064 \frac{10^9}{T^3} & 7,000K \le T \le 25,000K \end{cases} \\
y = -3x^2 + 2.87 x - 0.275
$$

xyY空間から、式 `xyYtoXYZ` を使用してCIE XYZ空間に変換できます。

$$
X = \frac{xY}{y} \\
Z = \frac{(1 - x - y)Y}{y}
$$

私たちの目的のため、$Y = 1$ に固定します。これにより、式 `XYZtoRGB` に示すように、単純な3x3行列でXYZ空間から線形RGBに変換できます。

$$
\left[ \begin{matrix} R \\ G \\ B \end{matrix} \right] = M^{-1} \left[ \begin{matrix} X \\ Y \\ Z \end{matrix} \right]
$$

変換行列Mは、ターゲットRGB色空間の原色から計算されます。式 `XYZtoRGBValues` は、sRGB色空間の逆行列を使用した変換を示しています。

$$
\left[ \begin{matrix} R \\ G \\ B \end{matrix} \right] = \left[ \begin{matrix} 3.2404542 & -1.5371385 & -0.4985314 \\ -0.9692660 & 1.8760108 & 0.0415560 \\ 0.0556434 & -0.2040259 & 1.0572252 \end{matrix} \right] \left[ \begin{matrix} X \\ Y \\ Z \end{matrix} \right]
$$

これらの操作の結果は、sRGB色空間の線形RGB三つ組です。結果の色度に関心があるため、1.0より大きい値をクランプして結果の色を歪めることを避けるために、正規化ステップを適用する必要があります。

$$
\hat{C}_{linear} = \frac{C_{linear}}{max(C_{linear})}
$$

最後に、表示可能な値を取得するために、sRGB光電子変換関数（OECF、式 `OECFsRGB` に示す）を適用する必要があります（シェーディングのためにレンダラーに渡す場合は、値は線形のままにする必要があります）。

$$
C_{sRGB} = \begin{cases} 12.92 \times \hat{C}_{linear} & \hat{C}_{linear} \le 0.0031308 \\
1.055 \times \hat{C}_{linear}^{\frac{1}{2.4}} - 0.055 & \hat{C}_{linear} \gt 0.0031308 \end{cases}
$$

便宜上、図 [colorTemperatureScaleCCT] は、1,000K〜12,500Kの相関色温度の範囲を示しています。以下で使用されるすべての色は、白色点としてCIE $D_{65}$ を想定しています（sRGB色空間の場合と同様）。

![](/images/filament-md-ja/diagram_color_temperature_cct.png)
*図 [colorTemperatureScaleCCT]: 相関色温度のスケール*

同様に、図 [colorTemperatureScaleCIE] は、1,000K〜12,500KのCIE標準光源シリーズDの範囲を示しています。

![](/images/filament-md-ja/diagram_color_temperature_cie.png)
*図 [colorTemperatureScaleCIE]: CIE標準光源シリーズDのスケール*

参考のため、図 [colorTemperatureScaleCCTClamped] は、式 `normalizedRGB` で示した正規化ステップなしの相関色温度の範囲を示しています。

![](/images/filament-md-ja/diagram_color_temperature_cct_clamped.png)
*図 [colorTemperatureScaleCCTClamped]: 正規化されていない相関色温度のスケール*

表 [colorTemperatureSamples] は、さまざまな一般的な光源の相関色温度をsRGB色見本として示しています。これらの色は $D_{65}$ 白色点に対する相対的なものであるため、ディスプレイの白色点によって知覚される色相が異なる場合があります。詳細については、[What colour is the Sun?](http://jila.colorado.edu/~ajsh/colour/Tspectrum.html) を参照してください。

| Temperature (K) | Light source | Color |
| ---: | :--- | --- |
| 1,700-1,800 | マッチの炎 |
| 1,850-1,930 | ろうそくの炎 |
| 2,000-3,000 | 日の出/日の入りの太陽 |
| 2,500-2,900 | 家庭用タングステン電球 |
| 3,000 | タングステンランプ 1K |
| 3,200-3,500 | クォーツライト |
| 3,200-3,700 | 蛍光灯 |
| 3,275 | タングステンランプ 2K |
| 3,380 | タングステンランプ 5K、10K |
| 5,000-5,400 | 正午の太陽 |
| 5,500-6,500 | 昼光（太陽 + 空） |
| 5,500-6,500 | 雲/霞を通した太陽 |
| 6,000-7,500 | 曇り空 |
| 6,500 | RGBモニター白色点 |
| 7,000-8,000 | 屋外の日陰エリア |
| 8,000-10,000 | 部分的に曇った空 |
*表 [colorTemperatureSamples]: 一般的な光源の正規化された相関色温度*

## プリ露光ライト

物理ベースレンダリングと物理的なライト単位は、興味深い課題を提起します：照明コードによって生成される広範囲の値をどのように保存および処理するか？シェーダー内で完全な精度で計算が実行されると仮定すると、照明パスの線形出力を適切なサイズのバッファ（`RGB16F` または同等）に保存できるようにしたいと考えています。これを実現する最も明白で簡単な方法は、照明パスの結果を書き出す前にカメラの露光（詳細については物理ベースカメラセクションを参照）を単純に適用することです。この単純なステップは、リスト [preexposedLighting] に示されています。

```glsl
fragColor = luminance * camera.exposure;
```
*リスト [preexposedLighting]: 照明パスの出力は、半精度浮動小数点バッファに収まるようにプリ露光されます*

このソリューションは保存の問題を解決しますが、中間計算を単精度浮動小数点で実行する必要があります。代わりに、すべて（または少なくともほとんど）の照明作業を半精度浮動小数点で実行することを好みます。そうすることで、特にモバイルデバイスでのパフォーマンスと電力使用量を大幅に改善できます。しかし、半精度浮動小数点は、一般的な照度と輝度の値（例えば太陽）がその範囲を超える可能性があるため、この種の作業には適していません。解決策は、照明パスの結果ではなく、ライト自体をプリ露光することです。これは、ライトの定数バッファの更新が安価である場合、CPUで効率的に実行できます。これは、リスト [preexposedLights] に示すように、GPUでも実行できます。

```glsl
// The inputs must be highp/single precision,
// both for range (intensity) and precision (exposure)
// The output is mediump/half precision
float computePreExposedIntensity(highp float intensity, highp float exposure) {
    return intensity * exposure;
}

Light getPointLight(uint index) {
    Light light;
    uint lightIndex = // fetch light index;

    // the intensity must be highp/single precision
    highp vec4 colorIntensity  = lightsUniforms.lights[lightIndex][1];

    // pre-expose the light
    light.colorIntensity.w = computePreExposedIntensity(
            colorIntensity.w, frameUniforms.exposure);

    return light;
}
```
*リスト [preexposedLights]: ライトをプリ露光することで、シェーディングパイプライン全体で半精度浮動小数点を使用できます*

実際には、次のライトをプリ露光します：
- 点光源（ポイントとスポット）：GPU上で
- 指向性ライト：CPU上で
- IBL：CPU上で
- マテリアル発光：GPU上で

---

原文: https://google.github.io/filament/Filament.html
