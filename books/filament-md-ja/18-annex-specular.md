---
title: "付録 — Specular color"
---

## Specular color

金属サーフェスのスペキュラー色、つまり $f_{0}$ は、測定されたスペクトルデータから直接計算できます。[Refractive Index](https://refractiveindex.info/?shelf=3d&book=metals&page=brass) などのオンラインデータベースは、さまざまな材料について異なる波長で測定された複素IORの表を提供しています。

本ドキュメントの前半で、誘電体サーフェスのIORが与えられた場合の正反射時のフレネル反射率を計算するための式 `fresnelEquation` を提示しました。同じ式は、サーフェスのIORを表すために複素数を使用することで、導体用に書き換えることができます：

$$
c_{ior} = n_{ior} + ik
$$

式 `fresnelComplexIOR` は、結果として得られるフレネル式を示しています。ここで、$c^*$ は複素数 $c$ の共役です：

$$
f_{0}(c_{ior}) = \frac{(c_{ior} - 1)(c_{ior}^* - 1)}{(c_{ior} + 1)(c_{ior}^* + 1)}
$$

材料のスペキュラー色を計算するには、可視スペクトル全体にわたって複素IORの各スペクトルサンプルで複素フレネル方程式を評価する必要があります。各スペクトルサンプルについて、スペクトル反射率サンプルを取得します。正反射でのRGB色を見つけるには、各サンプルにCIE XYZ CMF（色マッチング関数）と目的の照明のスペクトルパワー分布を掛ける必要があります。sRGB色空間で色を計算したいので、標準照明D65を選択します。

次に、すべてのサンプルを合計（積分）して正規化し、XYZ色空間で $f_{0}$ を取得します。そこから、単純な色空間変換により、線形sRGB色または光電変換関数（OETF、一般に「ガンマ」曲線として知られる）を適用した後の非線形sRGB色が得られます。金などの一部の材料では、最終的なsRGB色が色域外になる可能性があることに注意してください。安価なガマット再マッピングの形式として単純な正規化ステップを使用していますが、より広い色域を持つ色空間（たとえばBT.2020）で値を計算することを検討するのは興味深いでしょう。

望ましい結果を達成するために、360nmから830nmまでの1nm間隔のICE 1931 2度CMF（[ソース](http://cvrl.ioo.ucl.ac.uk/cmfs.htm)）と、300nmから830nmまでの5nm間隔のCIE標準照明D65相対スペクトルパワー分布（[ソース](http://files.cie.co.at/204.xls)）を使用しました。

実装をリスト [specularColorImpl] に示します。簡潔にするため、実際のデータは省略しています。

```glsl
// CIE 1931 2-deg color matching functions (CMFs), from 360nm to 830nm,
// at 1nm intervals
//
// Data source:
//     http://cvrl.ioo.ucl.ac.uk/cmfs.htm
//     http://cvrl.ioo.ucl.ac.uk/database/text/cmfs/ciexyz31.htm
const size_t CIE_XYZ_START = 360;
const size_t CIE_XYZ_COUNT = 471;
const float3 CIE_XYZ[CIE_XYZ_COUNT] = { ... };

// CIE Standard Illuminant D65 relative spectral power distribution,
// from 300nm to 830, at 5nm intervals
//
// Data source:
//     https://en.wikipedia.org/wiki/Illuminant_D65
//     https://cielab.xyz/pdf/CIE_sel_colorimetric_tables.xls
const size_t CIE_D65_INTERVAL = 5;
const size_t CIE_D65_START = 300;
const size_t CIE_D65_END = 830;
const size_t CIE_D65_COUNT = 107;
const float CIE_D65[CIE_D65_COUNT] = { ... };

struct Sample {
    float w = 0.0f; // wavelength
    std::complex<float> ior; // complex IOR, n + ik
};

static float illuminantD65(float w) {
    auto i0 = size_t((w - CIE_D65_START) / CIE_D65_INTERVAL);
    uint2 indexBounds{i0, std::min(i0 + 1, CIE_D65_END)};

    float2 wavelengthBounds = CIE_D65_START + float2{indexBounds} * CIE_D65_INTERVAL;
    float t = (w - wavelengthBounds.x) / (wavelengthBounds.y - wavelengthBounds.x);
    return lerp(CIE_D65[indexBounds.x], CIE_D65[indexBounds.y], t);
}

// For std::lower_bound
bool operator<(const Sample& lhs, const Sample& rhs) {
    return lhs.w < rhs.w;
}

// The wavelength w must be between 360nm and 830nm
static std::complex<float> findSample(const std::vector<Sample>& samples, float w) {
    auto i1 = std::lower_bound(
	        samples.begin(), samples.end(), Sample{w, 0.0f + 0.0if});
    auto i0 = i1 - 1;

    // Interpolate the complex IORs
    float t = (w - i0->w) / (i1->w - i0->w);
    float n = lerp(i0->ior.real(), i1->ior.real(), t);
    float k = lerp(i0->ior.imag(), i1->ior.imag(), t);
    return { n, k };
}

static float fresnel(const std::complex<float>& sample) {
    return (((sample - (1.0f + 0if)) * (std::conj(sample) - (1.0f + 0if))) /
            ((sample + (1.0f + 0if)) * (std::conj(sample) + (1.0f + 0if)))).real();
}

static float3 XYZ_to_sRGB(const float3& v) {
    const mat3f XYZ_sRGB{
             3.2404542f, -0.9692660f,  0.0556434f,
            -1.5371385f,  1.8760108f, -0.2040259f,
            -0.4985314f,  0.0415560f,  1.0572252f
    };
    return XYZ_sRGB * v;
}

// Outputs a linear sRGB color
static float3 computeColor(const std::vector<Sample>& samples) {
    float3 xyz{0.0f};
    float y = 0.0f;

    for (size_t i = 0; i < CIE_XYZ_COUNT; i++) {
        // Current wavelength
        float w = CIE_XYZ_START + i;

        // Find most appropriate CIE XYZ sample for the wavelength
        auto sample = findSample(samples, w);
        // Compute Fresnel reflectance at normal incidence
        float f0 = fresnel(sample);

        // We need to multiply by the spectral power distribution of the illuminant
        float d65 = illuminantD65(w);

        xyz += f0 * CIE_XYZ[i] * d65;
        y += CIE_XYZ[i].y * d65;
    }

    // Normalize so that 100% reflectance at every wavelength yields Y=1
    xyz /= y;

    float3 linear = XYZ_to_sRGB(xyz);

    // Normalize out-of-gamut values
    if (any(greaterThan(linear, float3{1.0f}))) linear *= 1.0f / max(linear);

    return linear;
}
```
*リスト [specularColorImpl]: スペクトルデータから金属サーフェスのベース色を計算するC++実装*

このトピックに関する貴重な助けをいただいたNaty Hoffmanに特別な感謝を捧げます。

---

原文: https://google.github.io/filament/Filament.html
