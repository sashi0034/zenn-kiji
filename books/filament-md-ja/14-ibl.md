---
title: "Image based lights（IBL）"
---

現実世界では、光はあらゆる方向から来ます。光源から直接来るか、環境内のオブジェクトに跳ね返った後に間接的に来て、その過程で部分的に吸収されます。ある意味では、オブジェクトを囲む環境全体を光源と見なすことができます。画像、特にキューブマップは、そのような「環境光」をエンコードする優れた方法です。これはImage Based Lighting（IBL）または間接照明と呼ばれます。

![](/images/filament-md-ja/screenshot_ball_ibl.png)
*図 [iblBall]: ここに示されているオブジェクトは、画像エンコードされた環境光のみで照明されています。この技術を使用して適用できる微妙な照明効果に注目してください。*
画像ベース照明には制限があります。明らかに、環境画像は何らかの方法で取得する必要があり、以下で説明するように、照明に使用する前に前処理する必要があります。通常、環境画像は実世界でオフラインで取得されるか、オフラインまたは実行時にエンジンによって生成されます。いずれの場合も、ローカルまたは遠方のプローブが使用されます。

これらのプローブは、遠方またはローカルの環境を取得するために使用できます。このドキュメントでは、光が無限に遠くから来ると仮定される遠方環境プローブに焦点を当てます（これは、オブジェクトの表面上のすべての点が同じ環境マップを使用することを意味します）。

環境全体がオブジェクトの表面上の特定の点に光を寄与します。これは_放射照度_（$E$）と呼ばれます。オブジェクトから跳ね返る結果の光は放射輝度（$L_{out}$）と呼ばれます。入射照明は、BRDFの拡散部分と鏡面部分に一貫して適用する必要があります。

画像ベースライト（IBL）の放射照度とマテリアルモデル（BRDF）$f(\Theta)$[^ibl1] との相互作用から生じる放射輝度 $L_{out}$ は、次のように計算されます。

$$
L_{out}(n, v, \Theta) = \int_\Omega  f(l, v, \Theta) L_{\bot}(l) \left< n \cdot l \right> dl
$$ 

ここでは、表面を**マクロ**レベルで見ていることに注意してください（ミクロレベルの方程式と混同しないでください）。そのため、$\vec n$ と $\vec v$ にのみ依存します。本質的には、IBLにエンコードされたすべての方向から来る「点光源」にBRDFを適用しています。

## IBLのタイプ

現代のレンダリングエンジンで使用される4つの一般的なタイプのIBLがあります。

- **遠方ライトプローブ**：「無限遠」での照明情報をキャプチャするために使用され、視差を無視できます。遠方プローブには通常、空、遠方の景観の特徴、建物などが含まれます。エンジンによってキャプチャされるか、高ダイナミックレンジ画像（HDRI）としてカメラから取得されます。

- **ローカルライトプローブ**：特定の視点から世界の特定のエリアをキャプチャするために使用されます。キャプチャは、周囲のジオメトリに応じて立方体または球に投影されます。ローカルプローブは遠方プローブよりも正確で、マテリアルにローカル反射を追加するのに特に有用です。

- **平面反射**：平面でミラーリングされたシーンをレンダリングすることで反射をキャプチャするために使用されます。この技術は、建物の床、道路、水などの平面にのみ機能します。

- **スクリーン空間反射**：レンダリングされたシーン（たとえば前のフレーム）に基づいて、深度バッファでレイマーチングすることで反射をキャプチャするために使用されます。SSRは優れた結果をもたらしますが、非常に高価になる可能性があります。

さらに、静的IBLと動的IBLを区別する必要があります。完全に動的な昼夜サイクルを実装するには、たとえば遠方ライトプローブを動的に再計算する必要があります[^iblTypes1]。平面反射とスクリーン空間反射は本質的に動的です。

## IBL単位

前述の直接照明セクションで説明したように、すべてのライトは物理単位を使用する必要があります。したがって、IBLは輝度単位 $\frac{cd}{m^2}$ を使用します。これは、すべての直接照明方程式の出力単位でもあります。輝度単位の使用は、エンジンによってキャプチャされたライトプローブ（動的またはオフラインで静的に）に対して簡単です。

しかし、高ダイナミックレンジ画像の処理はもう少し繊細です。カメラは測定された輝度を記録するのではなく、元のシーンの輝度に_関連する_だけのデバイス依存の値を記録します。したがって、アーティストに、元の絶対輝度を回復、または少なくとも密接に近似できる乗数を提供する必要があります。

IBLのHDRIの輝度を適切に再構築するには、アーティストは単に環境の写真を撮るだけでなく、追加情報を記録する必要があります。

- **色較正**：グレーカードまたは[MacBeth ColorChecker](http://en.wikipedia.org/wiki/ColorChecker)を使用

- **カメラ設定**：絞り、シャッター、ISO

- **輝度サンプル**：スポット/輝度計を使用

[TODO] 一般的な輝度値（晴天、屋内など）を測定してリスト化

## ライトプローブの処理

前述のとおり、IBLの放射輝度は表面の半球上で積分することによって計算されます。これは明らかにリアルタイムで行うには高価すぎるため、まずライトプローブを前処理して、リアルタイム相互作用により適した形式に変換する必要があります。

以下のセクションでは、ライトプローブの評価を高速化するために使用される技術について説明します。

- **鏡面反射率**：事前フィルタリングされた重点サンプリングと分割和近似

- **拡散反射率**：放射照度マップと球面調和関数

## 遠方ライトプローブ

### 拡散BRDFの積分

ランベルトBRDF[^iblDiffuse1]を使用すると、放射輝度が得られます。

$$
\begin{align*}
   f_d(\sigma) &= \frac{\sigma}{\pi} \\
L_d(n, \sigma) &= \int_{\Omega} f_d(\sigma) L_{\bot}(l) \left< n \cdot l \right> dl \\
               &= \frac{\sigma}{\pi} \int_{\Omega} L_{\bot}(l) \left< n \cdot l \right> dl \\
               &= \frac{\sigma}{\pi} E_d(n) \quad \text{放射照度} \; 
        E_d(n) = \int_{\Omega} L_{\bot}(l) \left< n \cdot l \right> dl
\end{align*}
$$

または離散領域では：

$$ E_d(n) \equiv \sum_{\forall \, i \in image} L_{\bot}(s_i) \left< n \cdot s_i \right> \Omega_s $$

$\Omega_s$ はサンプル $i$ に関連する立体角[^iblDiffuse2]です。

放射照度積分 $E_d$ は、自明ではありますが、ゆっくりと[^iblDiffuse3]事前計算でき、実行時の効率的なアクセスのためにキューブマップに格納できます。通常、_image_ はキューブマップまたは正距円筒図です。項 $\frac{\sigma}{\pi}$ はIBLとは独立しており、実行時に追加されて_放射輝度_を取得します。

![](/images/filament-md-ja/ibl/ibl_river_roughness_m0.png)
*図 [iblOriginal]: 画像ベースの環境*
![](/images/filament-md-ja/ibl/ibl_irradiance.png)
*図 [iblIrradiance]: ランベルトBRDFを使用した画像ベースの放射照度マップ*
[^ibl1]: $\Theta$ はマテリアルモデル $f$ のパラメータを表します。つまり：_粗さ_、アルベドなど

[^iblTypes1]: これは、静的プローブのブレンディングまたは時間経過によるワークロードの分散によって実行できます

[^iblDiffuse1]: ランベルトBRDFは $\vec l$、$\vec v$、$\theta$ に依存しないため、$L_d(n,v,\theta) \equiv L_d(n,\sigma)$

[^iblDiffuse2]: $\Omega_s$ はキューブマップの場合、$\frac{2\pi}{6 \cdot width \cdot height}$ で近似できます

[^iblDiffuse3]: $O(12\,n^2\,m^2)$、$n$ と $m$ はそれぞれ環境と事前計算されたキューブマップの寸法

しかし、放射照度は球面調和関数（SH、球面調和関数セクションで詳しく説明）への分解によって非常に密接に近似でき、実行時に安価に計算できます。通常、モバイルでテクスチャフェッチを避け、テクスチャユニットを解放するのが最善です。キューブマップに格納されている場合でも、SH分解を使用した積分の事前計算とそれに続くレンダリングの方が桁違いに高速です。

SH分解は概念的にフーリエ変換に似ており、周波数領域で正規直交基底上の信号を表現します。私たちが最も関心を持つ特性は次のとおりです。

- $\left< \cos \theta \right>$ をエンコードするために必要な係数は非常に少ない

- _円形対称性_を持つカーネルによる畳み込みは非常に安価で、SH空間での積になります

実際には、$\left< \cos \theta \right>$ には4または9係数（つまり：2または3バンド）で十分です。つまり、$L_{\bot}$ にもこれ以上必要ありません。

![](/images/filament-md-ja/ibl/ibl_irradiance_sh3.png)
*図 [iblSH3]: 3バンド（9係数）*
![](/images/filament-md-ja/ibl/ibl_irradiance_sh2.png)
*図 [iblSH2]: 2バンド（4係数）*
実際には、$L_{\bot}$ を $\left< \cos \theta \right>$ で事前畳み込みし、これらの係数を基底スケーリング係数 $K_l^m$ で事前スケーリングして、シェーダーでの再構築コードを可能な限り単純にします。

```glsl
vec3 irradianceSH(vec3 n) {
    // uniform vec3 sphericalHarmonics[9]
    // We can use only the first 2 bands for better performance
    return
          sphericalHarmonics[0]
        + sphericalHarmonics[1] * (n.y)
        + sphericalHarmonics[2] * (n.z)
        + sphericalHarmonics[3] * (n.x)
        + sphericalHarmonics[4] * (n.y * n.x)
        + sphericalHarmonics[5] * (n.y * n.z)
        + sphericalHarmonics[6] * (3.0 * n.z * n.z - 1.0)
        + sphericalHarmonics[7] * (n.z * n.x)
        + sphericalHarmonics[8] * (n.x * n.x - n.y * n.y);
}
```
*リスト [irradianceSH]: 事前スケーリングされたSHから放射照度を再構築するGLSLコード*

2バンドの場合、上記の計算は単一の $4 \times 4$ 行列とベクトルの乗算になることに注意してください。

さらに、$K_l^m$ による事前スケーリングのため、SH係数は色と見なすことができます。特に `sphericalHarmonics[0]` は平均放射照度に直接対応します。

### 鏡面BRDFの積分

上記で見たように、IBLの放射照度とBRDFの相互作用から生じる放射輝度 $L_{out}$ は次のとおりです。

$$
L_{out}(n, v, \Theta) = \int_\Omega f(l, v, \Theta) L_{\bot}(l) \left< n \cdot l \right> \partial l
$$ 

これは、$f(l, v, \Theta) \left< n \cdot l \right>$ による $L_{\bot}$ の畳み込みと認識されます。つまり：環境はBRDFをカーネルとして*フィルタリング*されます。実際、粗さが高いほど、鏡面反射は*ぼやけて*見えます。

式 `specularBRDFIntegration` に $f$ の式を代入すると、次のようになります。

$$
L_{out}(n,v,\Theta) = \int_\Omega D(l, v, \alpha) F(l, v, f_0, f_{90}) V(l, v, \alpha) \left< n \cdot l \right> L_{\bot}(l) \partial l
$$ 

この式は、積分内の $v$、$\alpha$、$f_0$、$f_{90}$ に依存するため、その評価は非常にコストがかかり、モバイルでのリアルタイムには適していません（事前フィルタリングされた重点サンプリングを使用しても）。

#### BRDFの積分の簡略化

$L_{out}$ 積分の閉形式解や簡単に計算する方法がないため、代わりに簡略化された方程式 $\hat{I}$ を使用します。ここで、$v = n$、つまりビュー方向 $v$ が常に表面法線 $n$ に等しいと仮定します。明らかに、この仮定は、ビューアに近い反射のぼやけの増加（いわゆる伸縮反射）など、畳み込みのすべてのビュー依存効果を壊します。

このような簡略化は、白いファーネスなどの定数環境にも深刻な影響を与えます。なぜなら、結果の定数（つまりDC）項の大きさに影響するからです。少なくとも、適切に選択されたときに平均放射照度が正しく保たれることを確認するスケール係数 $K$ を使用して、簡略化された積分でこれを修正できます。

- $I$ は元の積分です。つまり：$I(g) = \int_\Omega g(l) \left< n \cdot l \right> \partial l$
- $\hat{I}$ は $v = n$ の簡略化された積分です
- $K$ は、平均放射照度が $\hat{I}$ によって変更されないことを保証するスケール係数です
- $\tilde{I}$ は $I$ の最終的な近似です。$\tilde{I} = \hat{I} \times K$ 

$I$ は積分であるため、乗算をその上に分配できます。つまり：$I(g()f()) = I(g())I(f())$。

これを踏まえると、

$$
I( f(\Theta) L_{\bot} ) \approx \tilde{I}( f(\Theta) L_{\bot} )                       \\
\tilde{I}( f(\Theta) L_{\bot} ) = K \times \hat{I}( f(\Theta) L_{\bot} )              \\
K = \frac{I(f(\Theta))}{\hat{I}(f(\Theta))}
$$ 

上記の方程式から、$\tilde{I}$ は $L_{\bot}$ が定数の場合に $I$ と等価であり、正しい結果が得られることがわかります。

$$\begin{align*}
\tilde{I}(f(\Theta)L_{\bot}^{constant}) &= L_{\bot}^{constant} \hat{I}(f(\Theta)) \frac{I(f(\Theta))}{\hat{I}(f(\Theta))} \\
                                   &= L_{\bot}^{constant} I(f(\Theta))                                               \\
                                   &= I(f(\Theta)L_{\bot}^{constant})
\end{align*}$$

同様に、$v = n$ の場合に結果が正しいことも示すことができます。この場合、$I = \hat{I}$ です。

$$\begin{align*}
\tilde{I}(f(\Theta)L_{\bot}) &= I(f(\Theta)L_{\bot}) \frac{I(f(\Theta))}{I(f(\Theta))}    \\
                        &= I(f(\Theta)L_{\bot})
\end{align*}$$

最後に、$L_{\bot} = \bar{L_{\bot}} + (L_{\bot} - \bar{L_{\bot}}) = \bar{L_{\bot}} + \Delta L_{\bot}$ を $\tilde{I}$ に代入することで、スケール係数 $K$ が平均放射照度（$\bar{L_{\bot}}$）要件を満たすことを示すことができます。

$$\begin{align*}
\tilde{I}(f(\Theta)L_{\bot}) &= \tilde{I}\left[f\left(\Theta\right) \left(\bar{L_{\bot}} + \Delta L_{\bot}\right)\right] \\
                        &= K \times \hat{I}\left[f\left(\Theta\right) \left(\bar{L_{\bot}} + \Delta L_{\bot}\right)\right] \\
                        &= K \times \left[\hat{I}\left(f\left(\Theta\right)\bar{L_{\bot}}\right) + \hat{I}\left(f\left(\Theta\right)\Delta L_{\bot}\right)\right] \\ 
                        &= K \times \hat{I}\left(f\left(\Theta\right)\bar{L_{\bot}}\right) + K \times \hat{I}\left(f\left(\Theta\right) \Delta L_{\bot}\right) \\
                        &= \tilde{I}\left(f\left(\Theta\right)\bar{L_{\bot}}\right) + \tilde{I}\left(f\left(\Theta\right) \Delta L_{\bot}\right) \\
                        &= I\left(f\left(\Theta\right)\bar{L_{\bot}}\right) + \tilde{I}\left(f\left(\Theta\right) \Delta L_{\bot}\right)
\end{align*}$$

上記の結果は、平均放射照度が正しく計算されること、つまり $I(f(\Theta)\bar{L_{\bot}})$ を示しています。

この近似について考える方法は、放射輝度 $L_{\bot}$ を2つの部分、平均 $\bar{L_{\bot}}$ と平均からのデルタ $\Delta L_{\bot}$ に分割し、平均部分の正しい積分を計算してから、デルタ部分の簡略化された積分を追加することです。

$$
approximation(L_{\bot}) = correct(\bar{L_{\bot}}) + simplified(L_{\bot} - \bar{L_{\bot}})
$$ 

それでは、各項を見てみましょう。

$$
\hat{I}(f(n, \alpha) L_{\bot}) = \int_\Omega f(l, n, \alpha) L_{\bot}(l) \left< n \cdot l \right> \partial l   \\
\hat{I}(f(n, \alpha))     = \int_\Omega f(l, n, \alpha)        \left< n \cdot l \right> \partial l   \\
I(f(n, v, \alpha))        = \int_\Omega f(l, n, v, \alpha)     \left< n \cdot l \right> \partial l
$$

これら3つの方程式はすべて、以下で説明するように、簡単に事前計算してルックアップテーブルに格納できます。

#### 離散領域

離散領域では、`iblPartialEquations` の方程式は次のようになります。

$$
\hat{I}(f(n, \alpha) L_{\bot}) \equiv \frac{1}{N}\sum_{\forall \, i \in image} f(l_i, n, \alpha) L_{\bot}(l_i) \left<n \cdot l\right>  \\
\hat{I}(f(n, \alpha))     \equiv \frac{1}{N}\sum_{\forall \, i \in image} f(l_i, n, \alpha)          \left<n \cdot l\right>  \\
I(f(n, v, \alpha))        \equiv \frac{1}{N}\sum_{\forall \, i \in image} f(l_i, n, v, \alpha)       \left<n \cdot l\right>
$$

しかし、実際には_重点サンプリング_を使用しており、分布の $pdf$ を考慮する必要があり、項 $\frac{4\left<v \cdot h\right>}{D(h_i, \alpha)\left<n \cdot h\right>}$ が追加されます。
IBLの重点サンプリングのセクションを参照してください。

$$
\hat{I}(f(n, \alpha) L_{\bot}) \equiv \frac{4}{N}\sum_i^N f(l_i, n, \alpha)    \frac{\left<v \cdot h\right>}{D(h_i, \alpha)\left<n \cdot h\right>} L_{\bot}(l_i) \left<n \cdot l\right>  \\
\hat{I}(f(n, \alpha))     \equiv \frac{4}{N}\sum_i^N f(l_i, n, \alpha)    \frac{\left<v \cdot h\right>}{D(h_i, \alpha)\left<n \cdot h\right>}          \left<n \cdot l\right>  \\
I(f(n, v, \alpha))        \equiv \frac{4}{N}\sum_i^N f(l_i, n, v, \alpha) \frac{\left<v \cdot h\right>}{D(h_i, \alpha)\left<n \cdot h\right>}          \left<n \cdot l\right>
$$

$\hat{I}$ については、$v = n$ を仮定することを思い出してください。方程式 `iblImportanceSampling` は次のように簡略化されます。

$$
\hat{I}(f(n, \alpha) L_{\bot}) \equiv \frac{4}{N}\sum_i^N \frac{f(l_i, n,    \alpha)}{D(h_i, \alpha)} L_{\bot}(l_i) \left<n \cdot l\right>  \\
\hat{I}(f(n, \alpha))     \equiv \frac{4}{N}\sum_i^N \frac{f(l_i, n,    \alpha)}{D(h_i, \alpha)}          \left<n \cdot l\right>  \\
I(f(n, v, \alpha))        \equiv \frac{4}{N}\sum_i^N \frac{f(l_i, n, v, \alpha)}{D(h_i, \alpha)} \frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right>
$$

その後、最初の2つの方程式を統合して、$LD(n, \alpha) = \frac{\hat{I}(f(n, \alpha) L_{\bot})}{\hat{I}(f(n, \alpha))}$ にできます。

$$
LD(n, \alpha)       \equiv \frac{\sum_i^N \frac{f(l_i, n, \alpha)}{D(h_i, \alpha)} L_{\bot}(l_i) \left<n \cdot l\right>}{\sum_i^N \frac{f(l_i, n, \alpha)}{D(h_i, \alpha)}\left<n \cdot l\right>}
$$
$$
I(f(n, v, \alpha))  \equiv \frac{4}{N}\sum_i^N \frac{f(l_i, n, v, \alpha)}{D(h_i, \alpha)} \frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right>
$$

この時点で、両方の残りの方程式をほぼオフラインで計算できることに注意してください。唯一の難しさは、これらの積分を事前計算するときに $f_0$ も $f_{90}$ もわからないことです。以下で、式 `iblDFV` については実行時にこれらの項を組み込むことができることがわかりますが、残念ながら、これは式 `iblLD` には不可能であり、$f_0 = f_{90} = 1$ を仮定する必要があります（つまり：フレネル項は常に1と評価されます）。

また、brdfの可視性項も処理する必要があります。実際にはそれを保持すると、グラウンドトゥルースと比較してわずかに悪い結果が得られるため、$V = 1$ も設定します。

式 `iblLD` と `iblDFV` で $f$ を置き換えましょう。

$$
f(l_i, n, \alpha) = D(h_i, \alpha)F(f_0, f_{90}, \left<v \cdot h\right>)V(l_i, v, \alpha)
$$

最初の簡略化は、brdfの項 $D(h_i, \alpha)$ が分母（重点サンプリングによる $pdf$ からの）と相殺され、FとVは値が1であると仮定するため消えることです。

$$
LD(n, \alpha)       \equiv \frac{\sum_i^N V(l_i, v, \alpha)\left<n \cdot l\right>L_{\bot}(l_i) }{\sum_i^N \left<n \cdot l\right>}
$$
$$
I(f(n, v, \alpha))  \equiv \frac{4}{N}\sum_i^N \color{green}{F(f_0, f_{90}, \left<v \cdot h\right>)} V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right>
$$

それでは、式 `iblFV` にフレネル項を代入しましょう。

$$
F(f_0, f_{90}, \left<v \cdot h\right>) = f_0 (1 - F_c(\left<v \cdot h\right>)) + f_{90} F_c(\left<v \cdot h\right>) \\
F_c(\left<v \cdot h\right>) = (1 - \left<v \cdot h\right>)^5
$$

$$
I(f(n, v, \alpha))  \equiv \frac{4}{N}\sum_i^N \left[\color{green}{f_0 (1 - F_c(\left<v \cdot h\right>)) + f_{90} F_c(\left<v \cdot h\right>)}\right] V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
$$

$$
\begin{align*}
I(f(n, v, \alpha))  \equiv & \color{green}{f_0   } \frac{4}{N}\sum_i^N  \color{green}{(1 - F_c(\left<v \cdot h\right>))} V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
+      & \color{green}{f_{90}} \frac{4}{N}\sum_i^N  \color{green}{     F_c(\left<v \cdot h\right>) } V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right>
\end{align*}
$$

最後に、オフラインで計算できる方程式（つまり、実行時パラメータ $f_0$ と $f_{90}$ に依存しない部分）を抽出します。

$$
DFG_1(\alpha, \left<n \cdot v\right>) = \frac{4}{N}\sum_i^N  \color{green}{(1 - F_c(\left<v \cdot h\right>))} V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
DFG_2(\alpha, \left<n \cdot v\right>) = \frac{4}{N}\sum_i^N  \color{green}{     F_c(\left<v \cdot h\right>) } V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
I(f(n, v, \alpha))  \equiv   \color{green}{f_0} \color{red}{DFG_1(\alpha, \left<n \cdot v\right>)} + \color{green}{f_{90}} \color{red}{DFG_2(\alpha, \left<n \cdot v\right>)}
$$

$DFG_1$ と $DFG_2$ は $n \cdot v$、つまり法線 $n$ とビュー方向 $v$ の間の角度にのみ依存することに注意してください。これは、積分が $n$ に関して対称であるため真です。積分する際に、$n \cdot v$ を満たす限り、任意の $v$ を選択できます（たとえば：$v \cdot h$ を計算する場合）。

すべてをまとめると：

$$
\begin{align*}
L_{out}(n,v,\alpha,f_0,f_{90})     &\simeq \big[ f_0 \color{red}{DFG_1(n \cdot v, \alpha)} + f_{90} \color{red}{DFG_2(n \cdot v, \alpha)} \big] \times LD(n, \alpha) \\
DFG_1(\alpha, \left<n \cdot v\right>) &=      \frac{4}{N}\sum_i^N  \color{green}{(1 - F_c(\left<v \cdot h\right>))} V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
DFG_2(\alpha, \left<n \cdot v\right>) &=      \frac{4}{N}\sum_i^N  \color{green}{     F_c(\left<v \cdot h\right>) } V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
LD(n, \alpha)                    &=      \frac{\sum_i^N V(l_i, n, \alpha)\left<n \cdot l\right>L_{\bot}(l_i) }{\sum_i^N \left<n \cdot l\right>}
\end{align*}     
$$

### $DFG_1$ と $DFG_2$ 項の視覚化

$DFG_1$ と $DFG_2$ の両方は、$(n \cdot v, \alpha)$ でインデックス付けされた通常の2Dテクスチャで事前計算してバイリニアサンプリングするか、表面の分析近似を使用して実行時に計算できます。付録のサンプルコードを参照してください。事前計算されたテクスチャは、表 [textureDFG] に示されています。事前計算のC++実装は、[画像ベース照明のためのLの事前計算]セクションにあります。

![](/images/filament-md-ja/ibl/dfg1.png)
*$DFG_1$*
![](/images/filament-md-ja/ibl/dfg2.png)
*$DFG_2$*
![](/images/filament-md-ja/ibl/dfg.png)
*表 [textureDFG]: Y軸：$\alpha$。X軸：$\cos\theta$*
$DFG_1$ と $DFG_2$ は便利なことに $[0, 1]$ の範囲内にありますが、8ビットテクスチャには十分な精度がなく、問題を引き起こします。残念ながら、モバイルでは16ビットまたは浮動小数点テクスチャは普遍的ではなく、サンプラーの数が限られています。テクスチャを使用するシェーダーコードの魅力的な単純さにもかかわらず、分析近似を使用する方が良いかもしれません。ただし、2つの項のみを格納する必要があるため、OpenGL ES 3.0のRG16Fテクスチャ形式が良い候補です。

このような分析近似は [#Karis14] で説明されており、それ自体は [#Lazarov13] に基づいています。[#Narkowicz14] も別の興味深い近似です。これら2つの近似は、[マルチスキャタリングの事前積分]セクションで提示されるエネルギー補償項と互換性がないことに注意してください。表 [textureApproxDFG] は、これらの近似の視覚的表現を示しています。

![](/images/filament-md-ja/ibl/dfg1_approx.png)
*$DFG_1$（近似）*
![](/images/filament-md-ja/ibl/dfg2_approx.png)
*$DFG_2$（近似）*
![](/images/filament-md-ja/ibl/dfg_approx.png)
*表 [textureApproxDFG]: Y軸：$\alpha$。X軸：$\cos\theta$*
### $LD$ 項の視覚化

$LD$ は、$\alpha$ パラメータ（それ自体は粗さに関連、[粗さの再マッピングとクランピング]セクションを参照）にのみ依存する関数による環境の畳み込みです。$LD$ は、LODの増加が粗さの増加で事前フィルタリングされた環境を受け取るミップマップキューブマップに便利に格納できます。この畳み込みは強力なローパスフィルタであるため、これはうまく機能します。各ミップマップレベルを有効に活用するには、$\alpha$ を再マップする必要があります。私たちは、$\gamma = 2$ のべき乗再マッピングを使用するとうまく機能し、便利であることを発見しました。

$$
\begin{align*}
    \alpha       &= perceptualRoughness^2                        \\
    lod_{\alpha} &= \alpha^{\frac{1}{2}} = perceptualRoughness   \\
\end{align*}
$$

以下の例を参照してください。

![](/images/filament-md-ja/ibl/ibl_river_roughness_m0.png)
*$\alpha=0.0$*
![](/images/filament-md-ja/ibl/ibl_river_roughness_m1.png)
*$\alpha=0.2$*
![](/images/filament-md-ja/ibl/ibl_river_roughness_m2.png)
*$\alpha=0.4$*
![](/images/filament-md-ja/ibl/ibl_river_roughness_m3.png)
*$\alpha=0.6$*
![](/images/filament-md-ja/ibl/ibl_river_roughness_m4.png)
*$\alpha=0.8$*
### 間接鏡面と間接拡散コンポーネントの視覚化

図 [iblVisualized] は、間接照明が誘電体と導体とどのように相互作用するかを示しています。説明のため、直接照明は削除されました。

![](/images/filament-md-ja/ibl/ibl_visualization.jpg)
*図 [iblVisualized]: 間接拡散と鏡面の分解*
### IBL評価の実装

リスト [iblEvaluation] は、前のセクションで説明したさまざまなテクスチャを使用してIBLを評価するGLSL実装を示しています。

```glsl
vec3 ibl(vec3 n, vec3 v, vec3 diffuseColor, vec3 f0, vec3 f90,
        float perceptualRoughness) {
    vec3 r = reflect(n);
    vec3 Ld = textureCube(irradianceEnvMap, r) * diffuseColor;
    float lod = computeLODFromRoughness(perceptualRoughness);
    vec3 Lld = textureCube(prefilteredEnvMap, r, lod);
    vec2 Ldfg = textureLod(dfgLut, vec2(dot(n, v), perceptualRoughness), 0.0).xy;
    vec3 Lr =  (f0 * Ldfg.x + f90 * Ldfg.y) * Lld;
    return Ld + Lr;
}
```
*リスト [iblEvaluation]: 画像ベース照明評価のGLSL実装*

ただし、放射照度キューブマップの代わりに球面調和関数を使用し、$DFG$ LUTの分析近似を使用することで、いくつかのテクスチャルックアップを節約できます。これはリスト [optimizedIblEvaluation] に示されています。

```glsl
vec3 irradianceSH(vec3 n) {
    // uniform vec3 sphericalHarmonics[9]
    // We can use only the first 2 bands for better performance
    return
          sphericalHarmonics[0]
        + sphericalHarmonics[1] * (n.y)
        + sphericalHarmonics[2] * (n.z)
        + sphericalHarmonics[3] * (n.x)
        + sphericalHarmonics[4] * (n.y * n.x)
        + sphericalHarmonics[5] * (n.y * n.z)
        + sphericalHarmonics[6] * (3.0 * n.z * n.z - 1.0)
        + sphericalHarmonics[7] * (n.z * n.x)
        + sphericalHarmonics[8] * (n.x * n.x - n.y * n.y);
}

// NOTE: this is the DFG LUT implementation of the function above
vec2 prefilteredDFG_LUT(float coord, float NoV) {
    // coord = sqrt(roughness), which is the mapping used by the
    // IBL prefiltering code when computing the mipmaps
    return textureLod(dfgLut, vec2(NoV, coord), 0.0).rg;
}

vec3 evaluateSpecularIBL(vec3 r, float perceptualRoughness) {
    // This assumes a 256x256 cubemap, with 9 mip levels
    float lod = 8.0 * perceptualRoughness;
    // decodeEnvironmentMap() either decodes RGBM or is a no-op if the
    // cubemap is stored in a float texture
    return decodeEnvironmentMap(textureCubeLodEXT(environmentMap, r, lod));
}

vec3 evaluateIBL(vec3 n, vec3 v, vec3 diffuseColor, vec3 f0, vec3 f90, float perceptualRoughness) {
    float NoV = max(dot(n, v), 0.0);
    vec3 r = reflect(-v, n);

    // Specular indirect
    vec3 indirectSpecular = evaluateSpecularIBL(r, perceptualRoughness);
    vec2 env = prefilteredDFG_LUT(perceptualRoughness, NoV);
    vec3 specularColor = f0 * env.x + f90 * env.y;

    // Diffuse indirect
    // We multiply by the Lambertian BRDF to compute radiance from irradiance
    // With the Disney BRDF we would have to remove the Fresnel term that
    // depends on NoL (it would be rolled into the SH). The Lambertian BRDF
    // can be baked directly in the SH to save a multiplication here
    vec3 indirectDiffuse = max(irradianceSH(n), 0.0) * Fd_Lambert();

    // Indirect contribution
    return diffuseColor * indirectDiffuse + indirectSpecular * specularColor;
}
```
*リスト [optimizedIblEvaluation]: 画像ベース照明評価のGLSL実装*

### マルチスキャタリングの事前積分

[鏡面反射率のエネルギー損失]セクションで、BRDFで単一の散乱イベントのみを考慮することによるエネルギー損失を補償するために、第2のスケーリングされた鏡面ローブを使用する方法について説明しました。このエネルギー補償ローブは、次の方法で定義される $r$ に依存する項でスケーリングされます。

$$
r = \int_{\Omega} D(l,v) V(l,v) \left< n \cdot l \right> \partial l
$$

または、重点サンプリングで評価されます（IBLの重点サンプリングのセクションを参照）。

$$
r \equiv  \frac{4}{N}\sum_i^N  V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right>
$$

この等式は、式 `iblAllEquations` で見た項 $DFG_1$ と $DFG_2$ に非常に似ています。実際、フレネル項がないことを除いて同じです。

$f_{90} = 1$ とさらに仮定することで、$DFG_1$ と $DFG_2$ および $L_{out}$ 再構築を書き直すことができます。

$$
\begin{align*}
L_{out}(n,v,\alpha,f_0)                           &\simeq \big[ (1 - f_0) \color{red}{DFG_1^{multiscatter}(n \cdot v, \alpha)} + f_0 \color{red}{DFG_2^{multiscatter}(n \cdot v, \alpha)} \big] \times LD(n, \alpha) \\
DFG_1^{multiscatter}(\alpha, \left<n \cdot v\right>) &=      \frac{4}{N}\sum_i^N  \color{green}{F_c(\left<v \cdot h\right>)} V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
DFG_2^{multiscatter}(\alpha, \left<n \cdot v\right>) &=      \frac{4}{N}\sum_i^N                                        V(l_i, v, \alpha)\frac{\left<v \cdot h\right>}{\left<n \cdot h\right>} \left<n \cdot l\right> \\
LD(n, \alpha)                                   &=      \frac{\sum_i^N V(l_i, n, \alpha)\left<n \cdot l\right>L_{\bot}(l_i) }{\sum_i^N V(l_i, n, \alpha)\left<n \cdot l\right>}
\end{align*}     
$$

これら2つの新しい $DFG$ 項は、[画像ベース照明のためのLの事前計算]セクションで示した実装で使用されるものと単純に置き換える必要があります。

```glsl
float Fc = pow(1 - VoH, 5.0f);
r.x += Gv * Fc;
r.y += Gv;
```
*リスト [multiscatterIBLPreintegration]: マルチスキャタリング用の $L_{DFG}$ 項のC++実装*

再構築を実行するには、リスト [multiscatterIBLEvaluation] をわずかに変更する必要があります。

```glsl
vec2 dfg = textureLod(dfgLut, vec2(dot(n, v), perceptualRoughness), 0.0).xy;
// (1 - f0) * dfg.x + f0 * dfg.y
vec3 specularColor = mix(dfg.xxx, dfg.yyy, f0);
```
*リスト [multiscatterIBLEvaluation]: マルチスキャタリングLUTを使用した画像ベース照明評価のGLSL実装*

### まとめ

遠方の画像ベースライトの鏡面寄与を計算するために、いくつかの近似と妥協を行う必要がありました。

- $v = n$、IBLの非定数部分を積分する際に最大の誤差をもたらす仮定です。これにより、視点に対する粗さの異方性が完全に失われます。

- IBLの非定数部分の粗さ寄与は量子化され、三線形フィルタリングがこれらのレベル間を補間するために使用されます。これは低粗さで最も顕著です（たとえば、9 LODのキューブマップの場合、約0.0625付近）。

- ミップマップレベルは事前統合された環境を格納するために使用されるため、本来そうあるべきテクスチャ縮小には使用できません。これにより、低粗さおよび/または遠方または小さなオブジェクトでの環境の高周波領域でエイリアシングまたはモアレアーティファクトが発生する可能性があります。これにより、結果として生じる貧弱なキャッシュアクセスパターンのためにパフォーマンスにも影響する可能性があります。

- IBLの非定数部分にフレネルなし。

- IBLの非定数部分に可視性 = 1。

- シュリックのフレネル

- マルチスキャタリングの場合は $f_{90} = 1$。

![](/images/filament-md-ja/ibl/ibl_prefilter_vs_reference.png)
*図 [iblPrefilterVsImportanceSampling]: 重点サンプリング参照（上）と事前フィルタリングされたIBL（中央）の比較。*
![](/images/filament-md-ja/ibl/ibl_stretchy_reflections_error.png)
*図 [iblStretchyReflectionLoss]: $v = n$ を仮定することによる反射の誤差（下） — 「伸縮反射」の喪失。*
![](/images/filament-md-ja/ibl/ibl_trilinear_0.png)
*図 [iblRoughnessInLods0]: 粗さ = 0.0625でキューブマップLODに粗さを格納することによる誤差（つまり、レベル間で正確にサンプリング）。 ぼやけの代わりに、2つのぼやけ間の「クロスフェード」が表示されることに注意してください。*
![](/images/filament-md-ja/ibl/ibl_trilinear_1.png)
*図 [iblRoughnessInLods1]: 粗さ = 0.125でキューブマップLODに粗さを格納することによる誤差（つまり、レベル1を正確にサンプリング）。 粗さがLODと密接に一致する場合、キューブマップの三線形フィルタリングによる誤差が減少します。掠角での $v = n$ による誤差に注意してください。*
![](/images/filament-md-ja/ibl/ibl_no_mipmaping.png)
*図 [iblMoirePattern]: 色付き垂直ストライプで作られた環境を使用した $\alpha = 0$ の金属球でのテクスチャ縮小によるモアレパターン（スカイボックスは非表示）。*

## クリアコート

IBLをサンプリングする際、クリアコート層は第2の鏡面ローブとして計算されます。この鏡面ローブは、半球上で積分することは合理的にできないため、ビュー方向に沿って配向されます。リスト [clearCoatIBL] は、この近似を実際に示しています。エネルギー保存ステップも示しています。この第2の鏡面ローブは、同じDFG近似を使用して、メイン鏡面ローブとまったく同じ方法で計算されることに注意することが重要です。

```glsl
// clearCoat_NoV == shading_NoV if the clear coat layer doesn't have its own normal map
float Fc = F_Schlick(0.04, 1.0, clearCoat_NoV) * clearCoat;
// base layer attenuation for energy compensation
iblDiffuse  *= 1.0 - Fc;
iblSpecular *= sq(1.0 - Fc);
iblSpecular += specularIBL(r, clearCoatPerceptualRoughness) * Fc;
```
*リスト [clearCoatIBL]: 画像ベース照明のクリアコート鏡面ローブのGLSL実装*

## 異方性

[#McAuley15] は、[#Revie12] に基づく「曲がった反射ベクトル」と呼ばれる技術について説明しています。曲がった反射ベクトルは異方性照明の大まかな近似ですが、代替手段は重点サンプリングを使用することです。この近似は計算が十分に安価で、図 [anisotropicIBL1] と図 [anisotropicIBL2] に示すように良好な結果を提供します。

![](/images/filament-md-ja/screenshot_anisotropic_ibl1.jpg)
*図 [anisotropicIBL1]: 曲がった法線を使用した異方性間接鏡面反射（左：粗さ0.3、右：粗さ：0.0；両方：異方性1.0）*
![](/images/filament-md-ja/screenshot_anisotropic_ibl2.jpg)
*図 [anisotropicIBL2]: さまざまな粗さ、金属性などを持つ異方性反射*
この技術の実装は、リスト [bentReflectionVector] で示されるように簡単です。

```glsl
vec3 anisotropicTangent = cross(bitangent, v);
vec3 anisotropicNormal = cross(anisotropicTangent, bitangent);
vec3 bentNormal = normalize(mix(n, anisotropicNormal, anisotropy));
vec3 r = reflect(-v, bentNormal);
```
*リスト [bentReflectionVector]: 曲がった反射ベクトルのGLSL実装*

この技術は、リスト [bentReflectionVectorDirection] に示すように、負の `anisotropy` 値を受け入れることでより有用にすることができます。異方性が負の場合、ハイライトはタンジェントの方向ではなく、代わりにバイタンジェントの方向になります。

```glsl
vec3 anisotropicDirection = anisotropy >= 0.0 ? bitangent : tangent;
vec3 anisotropicTangent = cross(anisotropicDirection, v);
vec3 anisotropicNormal = cross(anisotropicTangent, anisotropicDirection);
vec3 bentNormal = normalize(mix(n, anisotropicNormal, anisotropy));
vec3 r = reflect(-v, bentNormal);
```
*リスト [bentReflectionVectorDirection]: 曲がった反射ベクトルのGLSL実装*

図 [anisotropicDirection] は、この変更された実装を実際に示しています。

![](/images/filament-md-ja/screenshot_anisotropy_direction.png)
*図 [anisotropicDirection]: 正（左）と負（右）の値を使用した異方性方向の制御*
## サブサーフェス

[TODO] サブサーフェスとIBLの説明

## クロス

クロスマテリアルモデルのIBL実装は、他のマテリアルモデルよりも複雑です。主な違いは、異なるNDF（「Charlie」対高さ相関スミスGGX）の使用に由来します。このセクションで説明したように、IBLを計算する際にBRDFのDFG項を計算するために分割和近似を使用します。このDFG項は異なるBRDF用に設計されており、クロスBRDFには使用できません。クロスBRDFがフレネル項を必要としないように設計したため、DFG LUTの第3チャンネルに単一のDG項を生成できます。結果は図 [dfgClothLUT] に示されています。

DG項は、[#Estevez17] で推奨されているように一様サンプリングを使用して生成されます。一様サンプリングでは、$pdf$ は単に $\frac{1}{2\pi}$ であり、ヤコビアン $\frac{1}{4\left< v \cdot h \right>}$ を使用する必要があります。

![](/images/filament-md-ja/ibl/dfg_cloth.png)
*図 [dfgClothLUT]: クロスBRDFのDG項をエンコードする第3チャンネルを持つDFG LUT*
画像ベース照明実装の残りの部分は、オプションのサブサーフェススキャタリング項とそのラップディフューズコンポーネントを含め、通常のライトの実装と同じステップに従います。クリアコートIBL実装と同様に、半球上で積分できず、ラップディフューズコンポーネントを計算するための支配的な光の方向としてビュー方向を使用します。

```glsl
float diffuse = Fd_Lambert() * ambientOcclusion;
#if defined(SHADING_MODEL_CLOTH)
#if defined(MATERIAL_HAS_SUBSURFACE_COLOR)
diffuse *= saturate((NoV + 0.5) / 2.25);
#endif
#endif

vec3 indirectDiffuse = irradianceIBL(n) * diffuse;
#if defined(SHADING_MODEL_CLOTH) && defined(MATERIAL_HAS_SUBSURFACE_COLOR)
indirectDiffuse *= saturate(subsurfaceColor + NoV);
#endif

vec3 ibl = diffuseColor * indirectDiffuse + indirectSpecular * specularColor;
```
*リスト [clothApprox]: クロスNDF用のDFG近似のGLSL実装*

これはIBL問題の一部にのみ対処していることに注意することが重要です。前述の事前フィルタリングされた鏡面環境マップは、標準シェーディングモデルのBRDFで畳み込まれており、クロスBRDFとは異なります。正確な結果を得るには、理論的にはエンジンで使用される各BRDFごとに1セットのIBLを提供する必要があります。しかし、第2セットのIBLを提供することは私たちのユースケースでは実用的ではないため、代わりに既存のIBLに依存することにしました。

---

原文: https://google.github.io/filament/Filament.html
