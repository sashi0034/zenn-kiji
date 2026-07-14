---
title: "Imaging pipeline — ポストプロセス / ライトパス / 検証"
---

## 光学ポストプロセス

### 色収差

[TODO]

![図 [fringing]: 色収差の例：左の耳や下の顎を見てください](/images/filament-md-ja/screenshot_fringing.jpg)

### レンズフレア

[TODO] 注記：レンズのオプティカルアセンブリを通してレイをトレースすることで、レンズフレアを生成する物理ベースのアプローチがありますが、ここでは画像ベースのアプローチを使用します。このアプローチはより安価で、無料のエミッター遮蔽や無制限の光源サポートなど、いくつかの歓迎すべき利点があります。

## フィルミックポストプロセス

[TODO] 可能な限りシーン参照データ（線形空間、トーンマッピング前）でポストプロセスを実行します。

最終画像に対してより大きな芸術的コントロールをアーティストに提供するために、カラーコレクションツールを提供することが重要です。これらのツールは、Adobe PhotoshopやAdobe After Effectsなど、すべての写真またはビデオ処理アプリケーションに見られます。

### コントラスト

### カーブ

### レベル

### カラーグレーディング

## ライトパス

エンジンが使用するライトパス、つまりレンダリング方法は、パフォーマンスに深刻な影響を与える可能性があり、シーンで使用できるライトの数に強い制限を課す可能性があります。3Dエンジンで伝統的に使用される2つの異なるレンダリング方法は、フォワードレンダリングとディファードレンダリングです。

私たちの目標は、以下の制約に従うレンダリング方法を使用することです：

- 低帯域幅要件
- ピクセルごとの複数の動的ライト

さらに、以下を簡単にサポートしたいと考えています：

- MSAA
- 透明度
- 複数のマテリアルモデル

ディファードレンダリングは、多くの最新の3Dレンダリングエンジンで、数十、数百、さらには数千の光源を簡単にサポートするために使用されています（その他の利点もあります）。ただし、この方法は帯域幅の面で非常に高価です。デフォルトのPBRマテリアルモデルでは、Gバッファーはピクセルあたり160〜192ビットを使用し、これは直接的にかなり高い帯域幅要件に変換されます。

一方、フォワードレンダリング方法は、歴史的に複数のライトの処理が苦手でした。一般的な実装は、可視ライトごとにシーンを複数回レンダリングし、結果をブレンド（加算）することです。別の手法は、シーン内の各オブジェクトに固定の最大ライト数を割り当てることです。ただし、これは世界で広大なスペースを占めるオブジェクト（建物、道路など）には実用的ではありません。

タイルドシェーディングは、フォワードとディファードの両方のレンダリング方法に適用できます。アイデアは、画面をタイルのグリッドに分割し、各タイルについて、そのタイル内のピクセルに影響を与えるライトのリストを見つけることです。これにより、オーバードロー（ディファードレンダリング）と大きなオブジェクトのシェーディング計算（フォワードレンダリング）を削減できるという利点があります。ただし、この手法は深度の不連続性の問題に悩まされ、大量の余分な作業につながる可能性があります。

図 [sponza] に表示されるシーンは、クラスタードフォワードレンダリングを使用してレンダリングされました。

![図 [sponza]: 数十の動的ライトとMSAAを使用したクラスタードフォワードレンダリング](/images/filament-md-ja/screenshot_sponza.jpg)

図 [sponzaTiles] は、同じシーンをタイルに分割したもの（この場合、1280x720のレンダーターゲットで80x80pxタイル）を示しています。

![図 [sponzaTiles]: タイルドシェーディング（16x9タイル）](/images/filament-md-ja/screenshot_sponza_tiles.jpg)

### クラスタードフォワードレンダリング

クラスタードシェーディングと呼ばれる別の方法を、そのフォワードバリアントで探求することにしました。クラスタードシェーディングは、タイルドレンダリングのアイデアを拡張しますが、3番目の軸にセグメンテーションを追加します。「クラスタリング」は、ビュー空間で、フラスタムを3Dグリッドに分割することで行われます。

フラスタムは、図 [sponzaSlices] に示すように、最初に深度軸でスライスされます。

![図 [sponzaSlices]: 深度スライス（16スライス）](/images/filament-md-ja/screenshot_sponza_slices.jpg)

そして、深度スライスは画面タイルと組み合わされて、フラスタムを「ボクセル化」します。各クラスターをfroxelと呼びます。これは、それらが何を表すか（フラスタム空間のボクセル）を明確にするためです。「フロクセル化」パスの結果は、図 [froxel1] と図 [froxel2] に示されています。

![図 [froxel1]: フラスタムのボクセル化（5x3タイル、8深度スライス）](/images/filament-md-ja/screenshot_sponza_froxels1.jpg)

![図 [froxel2]: フラスタムのボクセル化（5x3タイル、8深度スライス）](/images/filament-md-ja/screenshot_sponza_froxels2.jpg)

フレームをレンダリングする前に、シーン内の各ライトは、それが交差するfroxelに割り当てられます。ライト割り当てパスの結果は、各froxelのライトのリストです。レンダリングパス中に、フラグメントが属するfroxelのIDを計算でき、したがってそのフラグメントに影響を与える可能性のあるライトのリストを計算できます。

深度スライシングは線形ではなく、指数的です。典型的なシーンでは、近平面に近いピクセルが遠平面に近いピクセルよりも多くなります。したがって、froxelの指数グリッドは、最も重要な場所でライトの割り当てを改善します。

図 [froxelDistribution] は、指数スライシングを使用した場合、各深度スライスが使用するワールド空間単位の量を示しています。

![図 [froxelDistribution]: 近：0.1m、遠：100m、16スライス](/images/filament-md-ja/diagram_froxels1.png)

ただし、単純な指数ボクセル化だけでは十分ではありません。上のグラフはワールド空間がスライス全体にどのように分布しているかを明確に示していますが、近平面の近くで何が起こるかを示していません。同じ分布をより小さな範囲（0.1mから7m）で調べると、図 [froxelDistributionClose] に示すように、興味深い問題が現れます。

![図 [froxelDistributionClose]: 0.1〜7m範囲での深度分布](/images/filament-md-ja/diagram_froxels2.png)

このグラフは、単純な指数分布がカメラに非常に近い場所でスライスの半分を使い果たすことを示しています。この特定のケースでは、最初の5メートルで16スライスのうち8スライスを使用しています。動的ワールドライトはポイントライト（球）またはスポットライト（円錐）のいずれかであるため、近平面の近くではこのような細かい解像度は完全に不要です。

私たちの解決策は、シーンと近平面および遠平面に応じて、最初のfroxelのサイズを手動で調整することです。そうすることで、残りのfroxelをフラスタム全体により適切に分散できます。図 [froxelDistributionExp] は、たとえば0.1mから5mの間に特別なfroxelを使用した場合に何が起こるかを示しています。

![図 [froxelDistributionExp]: 近：0.1、遠：100m、16スライス、特別なfroxel：0.1〜5m](/images/filament-md-ja/diagram_froxels3.png)

この新しい分布ははるかに効率的で、フラスタム全体を通してライトをより適切に割り当てることができます。

### 実装ノート

ライト割り当ては、GPUまたはCPUの2つの異なる方法で実行できます。

#### GPUライト割り当て

この実装には、OpenGL ES 3.1とコンピュートシェーダーのサポートが必要です。ライトはShader Storage Buffer Objects（SSBO）に格納され、各ライトを対応するfroxelに割り当てるコンピュートシェーダーに渡されます。

フラスタムのボクセル化は、最初のコンピュートシェーダーによって1回だけ実行でき（投影行列が変更されない限り）、ライト割り当ては別のコンピュートシェーダーによって各フレーム実行できます。

コンピュートシェーダーのスレッディングモデルは、このタスクに特に適しています。単純に、froxelの数だけワークグループを呼び出します（ワークグループのX、Y、Zカウントをfroxelグリッドの解像度に直接マッピングできます）。各ワークグループは順番にスレッド化され、割り当てるすべてのライトをトラバースします。

交差テストは、単純な球/フラスタムまたは円錐/フラスタムテストを意味します。

GPU実装（ポイントライトのみ）のソースコードについては、付録を参照してください。

#### CPUライト割り当て

OpenGL ES 3.1以外のデバイスでは、ライト割り当てをCPUで効率的に実行できます。アルゴリズムはGPU実装とは異なります。各froxelのすべてのライトを反復する代わりに、エンジンは各ライトをfroxelとして「ラスタライズ」します。たとえば、ポイントライトの中心と半径が与えられれば、それが交差するfroxelのリストを計算することは簡単です。

この手法には、GPUバリアントよりも厳密なカリングを提供するという追加の利点があります。CPU実装は、圧縮されたライトのリストをより簡単に生成することもできます。

#### シェーディング

froxelごとのライトのリストは、SSBO（OpenGL ES 3.1）またはテクスチャとしてフラグメントシェーダーに渡すことができます。

#### 深度からfroxelへ

近平面 $n$、遠平面 $f$、深度スライスの最大数 $m$、範囲 [0..1] の線形深度値 $z$ が与えられると、式 `zToCluster` を使用して、特定の位置のクラスターのインデックスを計算できます。

$$
zToCluster(z,n,f,m)=floor \left( max \left( log2(z) \frac{m}{-log2(\frac{n}{f})} + m, 0 \right) \right)
$$

ただし、この式は前述の解像度の問題に悩まされます。特別な近値 $sn$ を導入することで修正できます。これは最初のfroxelの範囲を定義します（最初のfroxelは範囲 [n..sn] を占め、残りのfroxelは [sn..f] を占めます）。

$$
zToCluster(z,n,sn,f,m)=floor \left( max \left( log2(z) \frac{m-1}{-log2(\frac{sn}{f})} + m, 0 \right) \right)
$$

式 `linearZ` は、`gl_FragCoord.z` から線形深度値を計算するために使用できます（標準的なOpenGL投影行列を想定）。

$$
linearZ(z)=\frac{n}{f+z(n-f)}
$$

この式は、式 `linearZFix` に示すように、2つの項 $c0$ と $c1$ を事前計算することで簡略化できます。

$$
c1 = \frac{f}{n} \\
c0 = 1 - c1 \\
linearZ(z)=\frac{1}{z \cdot c0 + c1}
$$

この簡略化は重要です。なぜなら、線形z値を `zToClusterFix` の `log2` に渡すからです。除算は対数の下で否定になるため、代わりに $-log2(z \cdot c0 + c1)$ を使用することで除算を回避できます。

すべてをまとめると、リスト [fragCoordToFroxel] に示すように、特定のフラグメントのfroxelインデックスの計算は非常に簡単に実装できます。

```glsl
#define MAX_LIGHT_COUNT 16 // max number of lights per froxel

uniform uvec4 froxels; // res x, res y, count y, count y
uniform vec4 zParams;  // c0, c1, index scale, index bias

uint getDepthSlice() {
    return uint(max(0.0, log2(zParams.x * gl_FragCoord.z + zParams.y) *
            zParams.z + zParams.w));
}

uint getFroxelOffset(uint depthSlice) {
    uvec2 froxelCoord = uvec2(gl_FragCoord.xy) / froxels.xy;
    froxelCoord.y = (froxels.w - 1u) - froxelCoord.y;

    uint index = froxelCoord.x + froxelCoord.y * froxels.z +
            depthSlice * froxels.z * froxels.w;
    return index * MAX_FROXEL_LIGHT_COUNT;
}

uint slice = getDepthSlice();
uint offset = getFroxelOffset(slice);

// Compute lighting...
```
*リスト [fragCoordToFroxel]: フラグメントの画面座標からfroxelインデックスを計算するGLSL実装*

インデックス評価を効率的に実行するために、いくつかのユニフォームを事前計算する必要があります。これらのユニフォームを事前計算するために使用されるコードは、リスト [froxelIndexPrecomputation] にあります。

```glsl
froxels[0] = TILE_RESOLUTION_IN_PX;
froxels[1] = TILE_RESOLUTION_IN_PX;
froxels[2] = numberOfTilesInX;
froxels[3] = numberOfTilesInY;

zParams[0] = 1.0f - Z_FAR / Z_NEAR;
zParams[1] = Z_FAR / Z_NEAR;
zParams[2] = (MAX_DEPTH_SLICES - 1) / log2(Z_SPECIAL_NEAR / Z_FAR);
zParams[3] = MAX_DEPTH_SLICES;
```
[リスト [froxelIndexPrecomputation]]

#### froxelから深度へ

froxelインデックス $i$、特別な近平面 $sn$、遠平面 $f$、深度スライスの最大数 $m$ が与えられると、式 `clusterToZ` は特定のfroxelの最小深度を計算します。

$$
clusterToZ(i \ge 1,sn,f,m)=2^{(i-m) \frac{-log2(\frac{sn}{f})}{m-1}}
$$

$i=0$ の場合、z値は0です。この式の結果は [0..1] 範囲にあり、ワールド単位で距離を取得するには $f$ を掛ける必要があります。

コンピュートシェーダー実装では、`pow` の代わりに `exp2` を使用する必要があります。除算は事前計算してユニフォームとして渡すことができます。

## 検証

ライティングシステムの複雑さを考えると、実装を検証することが重要です。参照レンダリング、光測定、データ視覚化など、いくつかの方法で検証します。

[TODO] 光測定検証の説明（レンダーターゲットからEVを読み取り、露出計/カメラで測定した値と比較するなど）

### シーン参照視覚化

シーンのライティングを検証する迅速で簡単な方法は、関連データへの直感的なマッピングを提供する色を出力するようにシェーダーを変更することです。これは、偽色を出力するカスタムデバッグトーンマッピングオペレーターを使用することで簡単に実行できます。

#### 輝度ストップ

発光マテリアルとIBLを使用すると、トーンマッピングと量子化後は観察が困難ですが、シーン参照空間ではかなり明白な、スペキュラーハイライトが見かけ上のキャスターよりも明るいシーンを簡単に取得できます。図 [luminanceViz] は、リスト [tonemapLuminanceViz] で説明されているカスタムオペレーターがシーンの露出輝度を表示するためにどのように使用されるかを示しています。

![図 [luminanceViz]: 輝度を色でコード化してストップを視覚化：シアンはミドルグレー、青は1ストップ暗く、緑は1ストップ明るいなど](/images/filament-md-ja/screenshot_luminance_debug.png)

```glsl
vec3 Tonemap_DisplayRange(const vec3 x) {
    // The 5th color in the array (cyan) represents middle gray (18%)
    // Every stop above or below middle gray causes a color shift
    float v = log2(luminance(x) / 0.18);
    v = clamp(v + 5.0, 0.0, 15.0);
    int index = int(floor(v));
    return mix(debugColors[index], debugColors[min(15, index + 1)], fract(v));
}

const vec3 debugColors[16] = vec3[](
     vec3(0.0, 0.0, 0.0),         // black
     vec3(0.0, 0.0, 0.1647),      // darkest blue
     vec3(0.0, 0.0, 0.3647),      // darker blue
     vec3(0.0, 0.0, 0.6647),      // dark blue
     vec3(0.0, 0.0, 0.9647),      // blue
     vec3(0.0, 0.9255, 0.9255),   // cyan
     vec3(0.0, 0.5647, 0.0),      // dark green
     vec3(0.0, 0.7843, 0.0),      // green
     vec3(1.0, 1.0, 0.0),         // yellow
     vec3(0.90588, 0.75294, 0.0), // yellow-orange
     vec3(1.0, 0.5647, 0.0),      // orange
     vec3(1.0, 0.0, 0.0),         // bright red
     vec3(0.8392, 0.0, 0.0),      // red
     vec3(1.0, 0.0, 1.0),         // magenta
     vec3(0.6, 0.3333, 0.7882),   // purple
     vec3(1.0, 1.0, 1.0)          // white
);
```
*リスト [tonemapLuminanceViz]: 輝度視覚化のためのカスタムデバッグトーンマッピングオペレーターのGLSL実装*

### 参照レンダリング

参照レンダリングに対して実装を検証するために、Mitsubaと呼ばれる商用グレードのオープンソース物理ベースオフラインパストレーサーを使用します。Mitsubaは多くの異なるインテグレーター、サンプラー、マテリアルモデルを提供しており、リアルタイムレンダラーとの公平な比較を提供できるはずです。このパストレーサーは、独自のシーン記述から自動生成しやすいシンプルなXMLシーン記述形式にも依存しています。

図 [mitsubaReference] と図 [filamentReference] は、完全に滑らかな誘電体球である単純なシーンを、それぞれMitsubaとFilamentでレンダリングしたものを示しています。

![図 [mitsubaReference]: 12コア2013 MacProで2048x1440を1分42秒でレンダリング](/images/filament-md-ja/screenshot_ref_mitsuba.jpg)

![図 [filamentReference]: Nexus 9デバイス（Tegra K1 GPU）で2048x1440をMSAA 4xで60 fpsでレンダリング](/images/filament-md-ja/screenshot_ref_filament.jpg)

両方のシーンをレンダリングするために使用されたパラメータは次のとおりです：

**Filament**

- Material
  - Base color: sRGB 0.81, 0, 0
  - Metallic: 0
  - Roughness: 0
  - Reflectance: 0.5
- Indirect light: IBL
  - office.exrからcmgenによって生成された256x256キューブマップ
  - Multiplier: 35,000
- Direct light: directional light
  - Linear color: 1.0, 0.96, 0.95
  - Intensity: 120,000 lux
- Exposure
  - Aperture: f/16
  - Shutter speed: 1/125s
  - ISO: 100

**Mitsuba**

- BSDF: roughplastic
  - Distribution: GGX
  - Alpha: 0
  - Diffuse reflectance: sRGB 0.81, 0, 0
- Emitter: environment map
  - Source: office.exr
  - Scale: 35,000
- Emitter: directional
  - Irradiance: linear RGB 120,000 115,200 114,000
- Film: LDR
  - Exposure: -15.23、log2(filamentExposure)から計算
- Integrator: path
- Sampler: ldsampler
  - Sample count: 256

完全なMitsubaシーンは付録にあります。両方のシーンは同じ解像度（2048x1440）でレンダリングされました。

#### 比較

2つのレンダリング間のわずかな違いは、Filamentが使用するさまざまな近似から生じます：RGBM 256x256リフレクションプローブ、RGBM 1024x1024背景マップ、Lambert diffuse、split-sum近似、DFG項の分析的近似など。

図 [referenceComparison] は、両方のエンジンによって生成された画像の輝度グラデーションを示しています。比較はLDR画像で実行されました。

![図 [referenceComparison]: Mitsuba（左）とFilament（右）の輝度グラデーション](/images/filament-md-ja/screenshot_ref_comparison.png)

最大の違いは放射角で見られます。これはおそらく、FilamentがLambertian diffuse項を使用していることで説明されます。Disney diffuse項とそのgrazing retro-reflectionsにより、FilamentはMitsubaに近づくでしょう。

## 座標系

### ワールド座標系

FilamentはY軸上向き、右手座標系を使用します。

![図 [coordinates]: 赤 +X、緑 +Y、青 +Z（Marmoset Toolbagでレンダリング）](/images/filament-md-ja/screenshot_coordinates.jpg)

### カメラ座標系

FilamentのカメラはローカルのZ軸に向かって見ます。つまり、変換が適用されていない状態でカメラをワールドに配置すると、カメラはワールドの-Z軸を見下ろします。

### キューブマップ座標系

Filamentで使用されるすべてのキューブマップは、図 [cubemapCoordinates] に示すように、フェイスアライメントのOpenGL規約に従います。

![図 [cubemapCoordinates]: OpenGLフェイスアライメント規約に従ったキューブマップの水平クロス表現](/images/filament-md-ja/screenshot_cubemap_coordinates.png)

環境背景とリフレクションプローブはミラーリングされていることに注意してください（[ミラーリング](#ミラーリング) セクションを参照）。

#### ミラーリング

リフレクションのレンダリングを簡略化するために、IBLキューブマップはX軸でミラーリングされて保存されます。これは `cmgen` ツールのデフォルトの動作です。これは、環境背景として使用されるIBLキューブマップを実行時に再度ミラーリングする必要があることを意味します。スカイボックスでこれを実現する簡単な方法は、テクスチャ付きの背面を使用することです。Filamentはデフォルトでこれを行います。

#### 正距円筒図環境マップ

正距円筒図環境マップを水平/垂直クロスキューブマップに変換するために、ソースの正方形環境マップの中央に+Zフェイスを配置します。

#### 環境マップとスカイボックスのワールド空間方向

Filamentでスカイボックスまたは IBL を指定する場合、指定されたキューブマップは、-Zフェイスがワールドの+Z軸を指すように方向付けられます（これは、Filamentがミラーリングされたキューブマップを想定しているためです。[ミラーリング](#ミラーリング) セクションを参照）。ただし、環境とスカイボックスは事前にミラーリングされていることが期待されているため、それらの-Z（背面）フェイスは期待どおりにワールドの-Z軸を指します（そして、カメラはデフォルトでその方向を見ます。[カメラ座標系](#カメラ座標系) セクションを参照）。

---

原文: https://google.github.io/filament/Filament.html
