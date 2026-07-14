---
title: "付録 — Importance sampling"
---

## IBLのImportance sampling

離散領域では、積分は式 `iblSampling` で定義されるサンプリングで近似できます。

$$
L_{out}(n,v,\Theta) \equiv \frac{1}{N} \sum_{i}^{N} f(l_{i}^{uniform},v,\Theta) L_{\perp}(l_i) \left< n \cdot l_i^{uniform} \right>
$$

残念ながら、この積分を評価するには非常に多くのサンプルが必要です。一般的に使用される手法は、より「重要」なサンプルをより頻繁に選択することです。これは _importance sampling_ と呼ばれます。私たちの場合、マイクロファセット法線の分布 $D_{ggx}$ を重要なサンプルの分布として使用します。

importance samplingによる $ L_{out}(n,v,\Theta) $ の評価は、式 `annexIblImportanceSampling` に示されています。

$$
L_{out}(n,v,\Theta) \equiv \frac{1}{N} \sum_{i}^{N} \frac{f(l_{i},v,\Theta)}{p(l_i,v,\Theta)} L_{\perp}(l_i) \left< n \cdot l_i \right>
$$

式 `annexIblImportanceSampling` において、$p$ は _重要な方向サンプル_ $l_i$ の分布の確率密度関数（PDF）です。これらのサンプルは $h_i$、$v$、$\alpha$ に依存します。PDFの定義は式 `iblPDF` に示されています。

$h_i$ は選択した分布によって与えられます。詳細については [重要な方向の選択](#重要な方向の選択) セクションを参照してください。

_重要な方向サンプル_ $l_i$ は、$h_i$ の周りの $v$ の反射として計算されるため、$h_i$ と同じPDFを**持ちません**。変換された分布のPDFは次のように与えられます：

$$
p(T_r(x)) = p(x) |J(T_r)|^{-1}
$$

ここで、$|J(T_r)|$ は変換のヤコビアンの行列式です。私たちの場合、$h_i$ から $l_i$ への変換を考慮しており、そのヤコビアンの行列式は `iblPDF` で与えられます。

$$
p(l,v,\Theta) = D(h,\alpha) \left< n \cdot h \right> |J_{h \rightarrow l}|^{-1} \\
|J_{h \rightarrow l}| = 4 \left< v \cdot h \right>
$$

### 重要な方向の選択

詳細については、[BRDFをサンプリングするための重要な方向の選択](#BRDFをサンプリングするための重要な方向の選択) セクションを参照してください。一様分布 $(\zeta_{\phi},\zeta_{\theta})$ が与えられると、重要な方向 $l$ は式 `importantDirection` で定義されます。

$$
\phi = 2 \pi \zeta_{\phi} \\
\theta = cos^{-1} \sqrt{\frac{1 - \zeta_{\theta}}{(\alpha^2 - 1)\zeta_{\theta}+1}} \\
l = \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
$$

通常、$ (\zeta_{\phi},\zeta_{\theta}) $ は、[Hammersley列](#Hammersley列) セクションで説明されているHammersley一様分布アルゴリズムを使用して選択されます。

### Pre-filtered importance sampling

Importance samplingは、重要な方向を生成するためにPDFのみを考慮します。特に、IBLの実際のコンテンツには関係ありません。後者にサンプルが多くない領域で高周波が含まれている場合、積分は正確ではありません。これは、_pre-filtered importance sampling_ と呼ばれる手法を使用することである程度緩和でき、さらに、この手法により、はるかに少ないサンプルで積分を収束させることができます。

Pre-filtered importance samplingは、環境のいくつかの画像を使用し、それぞれを徐々にローパスフィルタリングします。これは通常、ミップマップとボックスフィルターを使用して非常に効率的に実装されます。LODは、サンプルの重要性に基づいて選択されます。つまり、確率の低いサンプルはより高いLODインデックス（よりフィルタリングされた）を使用します。

この手法は、[#Krivanek08] で詳細に説明されています。

キューブマップLODは次のように決定されます：

$$\begin{align*}
lod &= log_4 \left( K\frac{\Omega_s}{\Omega_p} \right) \\
K &= 4.0 \\
\Omega_s &= \frac{1}{N \cdot p(l_i)} \\
\Omega_p &\approx \frac{4\pi}{6 \cdot width \cdot height}
\end{align*}$$

ここで、$K$ は経験的に決定された定数、$p$ はBRDFのPDF、$ \Omega_{s} $ はサンプルに関連付けられた立体角、$\Omega_p$ はキューブマップのテクセルに関連付けられた立体角です。

キューブマップサンプリングは、シームレストリリニアフィルタリングを使用して行われます。OpenGLのシームレスサンプリング機能、またはシームを回避/削減する他の手法を使用して、フェイス間でキューブマップを正しくサンプリングすることは非常に重要です。

表 [importanceSamplingViz] は、図 [importanceSamplingRef] に適用した場合の、importance samplingとpre-filtered importance samplingの比較を示しています。

![図 [importanceSamplingRef]: Importance samplingの画像リファレンス](/images/filament-md-ja/image_is_original.png)

| サンプル数 | Importance sampling | Pre-filtered importance sampling |
| --- | --- | --- |
| 4096 | ![](/images/filament-md-ja/image_is_4096.png) | &nbsp; |
| 1024 | ![](/images/filament-md-ja/image_is_1024.png) | ![](/images/filament-md-ja/image_fis_1024.png) |
| 32 | ![](/images/filament-md-ja/image_is_32.png) | ![](/images/filament-md-ja/image_fis_32.png) |
*表 [importanceSamplingViz]: $\alpha = 0.4$ でのImportance sampling vs pre-filtered importance sampling*

以下の比較で使用されるリファレンスレンダラーは、近似を行いません。特に、$v = n$ を仮定せず、split sum近似も実行しません。pre-filteredレンダラーは、このセクションで説明したすべての手法を使用します：pre-filteredキューブマップ、DFG項の分析的定式化、そしてもちろんsplit sum近似です。

左：リファレンスレンダラー、右：pre-filtered importance sampling。

![](/images/filament-md-ja/image_is_ref_1.png) ![](/images/filament-md-ja/image_filtered_1.png)
![](/images/filament-md-ja/image_is_ref_2.png) ![](/images/filament-md-ja/image_filtered_2.png)
![](/images/filament-md-ja/image_is_ref_3.png) ![](/images/filament-md-ja/image_filtered_3.png)
![](/images/filament-md-ja/image_is_ref_4.png) ![](/images/filament-md-ja/image_filtered_4.png)

## BRDFをサンプリングするための重要な方向の選択

簡単にするために、BRDFの $ D $ 項をPDFとして使用しますが、PDFは半球上の積分が1になるように正規化する必要があります：

$$
\int_{\Omega}p(m)dm = 1 \\
\int_{\Omega}D(m)(n \cdot m)dm = 1 \\
\int_{\phi=0}^{2\pi}\int_{\theta=0}^{\frac{\pi}{2}}D(\theta,\phi) cos \theta sin \theta d\theta d\phi = 1 \\
$$

したがって、BRDFのPDFは式 `importantPDF` のように表現できます：

$$
p(\theta,\phi) = \frac{\alpha^2}{\pi(cos^2\theta (\alpha^2-1) + 1)^2} cos\theta sin\theta
$$

項 $sin\theta$ は、球上で積分するため、微分立体角 $sin\theta d\phi d\theta$ から来ています。$\theta$ と $\phi$ を独立にサンプリングします：

$$\begin{align*}
p(\theta) &= \int_0^{2\pi} p(\theta,\phi) d\phi = \frac{2\alpha^2}{(cos^2\theta (\alpha^2-1) + 1)^2} cos\theta sin\theta \\
p(\phi) &= \frac{p(\theta,\phi)}{p(\phi)} = \frac{1}{2\pi}
\end{align*}$$

$ p(\phi) $ の式は、法線の等方性分布に対して真です。

次に、各変数の累積分布関数（CDF）を計算します：

$$\begin{align*}
P(s_{\phi}) &= \int_{0}^{s_{\phi}} p(\phi) d\phi = \frac{s_{\phi}}{2\pi} \\
P(s_{\theta}) &= \int_{0}^{s_{\theta}} p(\theta) d\theta = 2 \alpha^2 \left( \frac{1}{(2\alpha^4-4\alpha^2+2) cos(s_{\theta})^2 + 2\alpha^2 - 2} - \frac{1}{2\alpha^4-2\alpha^2} \right)
\end{align*}$$

$ P(s_{\phi}) $ と $ P(s_{\theta}) $ を確率変数 $ \zeta_{\phi} $ と $ \zeta_{\theta} $ に設定し、それぞれ $ s_{\phi} $ と $ s_{\theta} $ を求めます：

$$\begin{align*}
P(s_{\phi}) &= \zeta_{\phi} \rightarrow s_{\phi} = 2\pi\zeta_{\phi} \\
P(s_{\theta}) &= \zeta_{\theta} \rightarrow s_{\theta} = cos^{-1} \sqrt{\frac{1-\zeta_{\theta}}{(\alpha^2-1)\zeta_{\theta}+1}}
\end{align*}$$

したがって、一様分布 $ (\zeta_{\phi},\zeta_{\theta}) $ が与えられると、重要な方向 $l$ は次のように定義されます：

$$\begin{align*}
\phi &= 2\pi\zeta_{\phi} \\
\theta &= cos^{-1} \sqrt{\frac{1-\zeta_{\theta}}{(\alpha^2-1)\zeta_{\theta}+1}} \\
l &= \{ cos\phi sin\theta,sin\phi sin\theta,cos\theta \}
\end{align*}$$

## Hammersley列

```glsl
vec2f hammersley(uint i, float numSamples) {
    uint bits = i;
    bits = (bits << 16) | (bits >> 16);
    bits = ((bits & 0x55555555) << 1) | ((bits & 0xAAAAAAAA) >> 1);
    bits = ((bits & 0x33333333) << 2) | ((bits & 0xCCCCCCCC) >> 2);
    bits = ((bits & 0x0F0F0F0F) << 4) | ((bits & 0xF0F0F0F0) >> 4);
    bits = ((bits & 0x00FF00FF) << 8) | ((bits & 0xFF00FF00) >> 8);
    return vec2f(i / numSamples, bits / exp2(32));
}
```
[Hammersley列ジェネレーターのC++実装]

## Image-based lightingのためのLの事前計算

$ L_{DFG} $ 項は $ n \cdot v $ のみに依存します。以下では、法線を任意に $ n=\left[0, 0, 1\right] $ に設定し、$v$ は $ n \cdot v $ を満たすように選択されます。ベクトル $ h_i $ は、$ D_{GGX}(\alpha) $ の重要な方向サンプル $i$ です。

```glsl
float GDFG(float NoV, float NoL, float a) {
    float a2 = a * a;
    float GGXL = NoV * sqrt((-NoL * a2 + NoL) * NoL + a2);
    float GGXV = NoL * sqrt((-NoV * a2 + NoV) * NoV + a2);
    return (2 * NoL) / (GGXV + GGXL);
}

float2 DFG(float NoV, float a) {
    float3 V;
    V.x = sqrt(1.0f - NoV*NoV);
    V.y = 0.0f;
    V.z = NoV;

    float2 r = 0.0f;
    for (uint i = 0; i < sampleCount; i++) {
        float2 Xi = hammersley(i, sampleCount);
        float3 H = importanceSampleGGX(Xi, a, N);
        float3 L = 2.0f * dot(V, H) * H - V;

        float VoH = saturate(dot(V, H));
        float NoL = saturate(L.z);
        float NoH = saturate(H.z);

        if (NoL > 0.0f) {
            float G = GDFG(NoV, NoL, a);
            float Gv = G * VoH / NoH;
            float Fc = pow(1 - VoH, 5.0f);
            r.x += Gv * (1 - Fc);
            r.y += Gv * Fc;
        }
    }
    return r * (1.0f / sampleCount);
}
```
[$ L_{DFG} $ 項のC++実装]

---

原文: https://google.github.io/filament/Filament.html
