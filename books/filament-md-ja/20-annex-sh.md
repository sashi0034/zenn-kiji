---
title: "付録 — Spherical Harmonics"
---

## Spherical Harmonics

| 記号 | 定義 |
| :---: | :--- |
| $K^m_l$ | 正規化係数 |
| $P^m_l(x)$ | 陪ルジャンドル多項式 |
| $y^m_l$ | 球面調和関数基底、またはSH基底 |
| $L^m_l$ | 単位球上で定義される $L(s)$ 関数のSH係数 |
*表 [shSymbols]: Spherical harmonics記号の定義*

### 基底関数

単位球の表面上の点の球面パラメータ化：

$$
\{ x, y, z \} = \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
$$

複素球面調和関数基底は次のように与えられます：

$$
Y^m_l(\theta, \phi) = K^m_l e^{im\theta} P^{|m|}_l(cos \theta), l \in N, -l <= m <= l
$$

ただし、実数基底のみが必要です：

$$\begin{align*}
y^{m > 0}_l &= \sqrt{2} K^m_l cos(m \phi) P^m_l(cos \theta) \\
y^{m < 0}_l &= \sqrt{2} K^m_l sin(|m| \phi) P^{|m|}_l(cos \theta) \\
y^0_l &= K^0_l P^0_l(cos \theta)
\end{align*}$$

正規化係数は次のように与えられます：

$$
K^m_l = \sqrt{\frac{(2l + 1)(l - |m|)!}{4 \pi (l + |m|)!}}
$$

陪ルジャンドル多項式 $P^{|m|}_l$ は、以下の再帰式から計算できます：

$$
P^0_0(x) = 1 \\
P^0_1(x) = x \\
P^l_l(x) = (-1)^l (2l - 1)!! (1 - x^2)^{\frac{l}{2}} \\
P^m_l(x) = \frac{((2l - 1) x P^m_{l - 1} - (l + m - 1) P^m_{l - 2})}{l - m} \\
$$

$y^{|m|}_l$ を計算するには、まず $P^{|m|}_l(z)$ を計算する必要があります。これは、式 `shRecursions` の再帰式を使用することで、かなり簡単に実現できます。3番目の再帰式は、表 [basisFunctions] で「対角線上を移動する」ために使用できます。つまり、$y^0_0$、$y^1_1$、$y^2_2$ などを計算します。次に、4番目の再帰式を使用して垂直に移動できます。

| バンドインデックス | 基底関数 $-l <= m <= l$ |
| :---: | :---: |
| $l = 0$ | $y^0_0$ |
| $l = 1$ | $y^{-1}_1$ $y^0_1$ $y^1_1$ |
| $l = 2$ | $y^{-2}_2$ $y^{-1}_2$ $y^0_2$ $y^1_2$ $y^2_2$ |
*表 [basisFunctions]: バンドごとの基底関数*

三角関数の項も再帰的に計算することが非常に簡単です：

$$\begin{align*}
C_m &\equiv cos(m \phi)sin(\theta)^m \\
S_m &\equiv sin(m \phi)sin(\theta)^m \\
\{ x, y, z \} &= \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
\end{align*}$$

角度和の三角関数恒等式を使用します：

$$\begin{align*}
cos(m \phi + \phi) &= cos(m \phi) cos(\phi) - sin(m \phi) sin(\phi) \Leftrightarrow C_{m + 1} = x C_m - y S_m \\
sin(m \phi + \phi) &= sin(m \phi) cos(\phi) + cos(m \phi) sin(\phi) \Leftrightarrow S_{m + 1} = x S_m - y C_m
\end{align*}$$

リスト [nonNormalizedSHBasis] は、非正規化SH基底 $\frac{y^m_l(s)}{\sqrt{2} K^m_l}$ を計算するC++コードを示しています：

```glsl
static inline size_t SHindex(ssize_t m, size_t l) {
    return l * (l + 1) + m;
}

void computeShBasis(
        double* const SHb,
        size_t numBands,
        const vec3& s)
{
    // handle m=0 separately, since it produces only one coefficient
    double Pml_2 = 0;
    double Pml_1 = 1;
    SHb[0] =  Pml_1;
    for (ssize_t l = 1; l < numBands; l++) {
        double Pml = ((2 * l - 1) * Pml_1 * s.z - (l - 1) * Pml_2) / l;
        Pml_2 = Pml_1;
        Pml_1 = Pml;
        SHb[SHindex(0, l)] = Pml;
    }
    double Pmm = 1;
    for (ssize_t m = 1; m < numBands ; m++) {
        Pmm = (1 - 2 * m) * Pmm;
        double Pml_2 = Pmm;
        double Pml_1 = (2 * m + 1)*Pmm*s.z;
        // l == m
        SHb[SHindex(-m, m)] = Pml_2;
        SHb[SHindex( m, m)] = Pml_2;
        if (m + 1 < numBands) {
            // l == m+1
            SHb[SHindex(-m, m + 1)] = Pml_1;
            SHb[SHindex( m, m + 1)] = Pml_1;
            for (ssize_t l = m + 2; l < numBands; l++) {
                double Pml = ((2 * l - 1) * Pml_1 * s.z - (l + m - 1) * Pml_2)
                        / (l - m);
                Pml_2 = Pml_1;
                Pml_1 = Pml;
                SHb[SHindex(-m, l)] = Pml;
                SHb[SHindex( m, l)] = Pml;
            }
        }
    }
    double Cm = s.x;
    double Sm = s.y;
    for (ssize_t m = 1; m <= numBands ; m++) {
        for (ssize_t l = m; l < numBands ; l++) {
            SHb[SHindex(-m, l)] *= Sm;
            SHb[SHindex( m, l)] *= Cm;
        }
        double Cm1 = Cm * s.x - Sm * s.y;
        double Sm1 = Sm * s.x + Cm * s.y;
        Cm = Cm1;
        Sm = Sm1;
    }
}
```
*リスト [nonNormalizedSHBasis]: 非正規化SH基底を計算するC++実装*

最初の3バンドの正規化SH基底関数 $y^m_l(s)$：

| バンド | $m = -2$ | $m = -1$ | $m = 0$ | $m = 1$ | $m = 2$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $l = 0$ |  |  | $\frac{1}{2}\sqrt{\frac{1}{\pi}}$ |
| $l = 1$ |  | $-\frac{1}{2}\sqrt{\frac{3}{\pi}}y$ | $\frac{1}{2}\sqrt{\frac{3}{\pi}}z$ | $-\frac{1}{2}\sqrt{\frac{3}{\pi}}x$ |
| $l = 2$ | $\frac{1}{2}\sqrt{\frac{15}{\pi}}xy$ | $-\frac{1}{2}\sqrt{\frac{15}{\pi}}yz$ | $\frac{1}{4}\sqrt{\frac{5}{\pi}}(2z^2 - x^2 - y^2)$ | $-\frac{1}{2}\sqrt{\frac{15}{\pi}}xz$ | $\frac{1}{4}\sqrt{\frac{15}{\pi}}(x^2 - y^2)$ |
*表 [basisFunctions]: バンドごとの正規化基底関数*

### 分解と再構成

球上で定義される関数 $L(s)$ は、次のようにSH基底に投影されます：

$$
L^m_l = \int_\Omega L(s) y^m_l(s) ds \\
L^m_l = \int_{\theta = 0}^{\pi} \int_{\phi = 0}^{2\pi} L(\theta, \phi) y^m_l(\theta, \phi) sin \theta d\theta d\phi
$$

各 $L^m_l$ は、RGB色チャネルごとに1つずつ、3つの値のベクトルであることに注意してください。

SH係数からの逆変換、つまり再構成またはレンダリングは、次のように与えられます：

$$
\hat{L}(s) = \sum_l \sum_{m = -l}^l L^m_l y^m_l(s)
$$

### $\left< cos \theta \right>$ の分解

$\left< cos \theta \right>$ は $\phi$ に依存しない（方位独立）ため、積分は次のように簡略化されます：

$$\begin{align*}
C^0_l &= 2\pi \int_0^{\pi} \left< cos \theta \right> y^0_l(\theta) sin \theta d\theta \\
C^0_l &= 2\pi K^m_l \int_0^{\frac{\pi}{2}} P^0_l(cos \theta) cos \theta sin \theta d\theta \\
C^m_l &= 0, m != 0
\end{align*}$$

[#Ramamoorthi01] では、積分の解析解が説明されています：

$$\begin{align*}
C_1 &= \sqrt{\frac{\pi}{3}} \\
C_{odd} &= 0 \\
C_{l, even} &= 2\pi \sqrt{\frac{2l + 1}{4\pi}} \frac{(-1)^{\frac{l}{2} - 1}}{(l + 2)(l - 1)} \frac{l!}{2^l (\frac{l!}{2})^2}
\end{align*}$$

最初のいくつかの係数は次のとおりです：

$$\begin{align*}
C_0 &= +0.88623 \\
C_1 &= +1.02333 \\
C_2 &= +0.49542 \\
C_3 &= +0.00000 \\
C_4 &= -0.11078
\end{align*}$$

図 [shCosThetaApprox] に示すように、$\left< cos \theta \right>$ を合理的に近似するには、非常に少ない係数が必要です。

![図 [shCosThetaApprox]: SH係数による $cos \theta$ の近似](/images/filament-md-ja/chart_sh_cos_thera_approx.png)

### 畳み込み

円形対称性を持つカーネル $h$ による畳み込みは、SH空間で直接簡単に適用できます：

$$
(h * f)^m_l = \sqrt{\frac{4\pi}{2l + 1}} h^0_l(s) f^m_l(s)
$$

都合よく、$\sqrt{\frac{4\pi}{2l + 1}} = \frac{1}{K^0_l}$ なので、実際には $C_l$ を $\frac{1}{K^0_l}$ で事前に乗算し、よりシンプルな式を得ることができます：

$$
\hat{C}_{l, even} = 2\pi \frac{(-1)^{\frac{l}{2} - 1}}{(l + 2)(l - 1)} \frac{l!}{2^l (\frac{l!}{2})^2} \\
\hat{C}_1 = \frac{2\pi}{3}
$$

$\hat{C}_l$ を計算するC++コードは次のとおりです：

```glsl
static double factorial(size_t n, size_t d = 1);

// < cos(theta) > SH coefficients pre-multiplied by 1 / K(0,l)
double computeTruncatedCosSh(size_t l) {
    if (l == 0) {
        return M_PI;
    } else if (l == 1) {
        return 2 * M_PI / 3;
    } else if (l & 1) {
        return 0;
    }
    const size_t l_2 = l / 2;
    double A0 = ((l_2 & 1) ? 1.0 : -1.0) / ((l + 2) * (l - 1));
    double A1 = factorial(l, l_2) / (factorial(l_2) * (1 << l));
    return 2 * M_PI * A0 * A1;
}

// returns n! / d!
double factorial(size_t n, size_t d ) {
   d = std::max(size_t(1), d);
   n = std::max(size_t(1), n);
   double r = 1.0;
   if (n == d) {
       // intentionally left blank
   } else if (n > d) {
       for ( ; n>d ; n--) {
           r *= n;
       }
   } else {
       for ( ; d>n ; d--) {
           r *= d;
       }
       r = 1.0 / r;
   }
   return r;
}
```

---

原文: https://google.github.io/filament/Filament.html
