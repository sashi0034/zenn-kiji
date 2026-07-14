# Annex

$$
\newcommand{NoL}{n \cdot l}
\newcommand{NoV}{n \cdot v}
\newcommand{NoH}{n \cdot h}
\newcommand{VoH}{v \cdot h}
\newcommand{LoH}{l \cdot h}
\newcommand{fNormal}{f_{0}}
\newcommand{fDiffuse}{f_d}
\newcommand{fSpecular}{f_r}
\newcommand{fX}{f_x}
\newcommand{aa}{\alpha^2}
\newcommand{fGrazing}{f_{90}}
\newcommand{schlick}{F_{Schlick}}
\newcommand{nior}{n_{ior}}
\newcommand{Ed}{E_d}
\newcommand{Lt}{L_{\bot}}
\newcommand{Lout}{L_{out}}
\newcommand{cosTheta}{\left< \cos \theta \right> }
$$


## Specular color

The specular color of a metallic surface, or $\fNormal$, can be computed directly from measured spectral data. Online databases such as [Refractive Index](https://refractiveindex.info/?shelf=3d&book=metals&page=brass) provide tables of complex IOR measured at different wavelengths for various materials.

Earlier in this document, we presented equation $\ref{fresnelEquation}$ to compute the Fresnel reflectance at normal incidence for a dielectric surface given its IOR. The same equation can be rewritten for conductors by using complex numbers to represent the surface's IOR:

$$\begin{equation}
c_{ior} = n_{ior} + ik
\end{equation}$$

Equation $\ref{fresnelComplexIOR}$ presents the resulting Fresnel formula, where $c^*$ is the conjugate of the complex number $c$:

$$\begin{equation}\label{fresnelComplexIOR}
\fNormal(c_{ior}) = \frac{(c_{ior} - 1)(c_{ior}^* - 1)}{(c_{ior} + 1)(c_{ior}^* + 1)}
\end{equation}$$

To compute the specular color of a material we need to evaluate the complex Fresnel equation at each spectral sample of complex IOR over the visible spectrum. For each spectral sample, we obtain a spectral reflectance sample. To find the RGB color at normal incidence, we must multiply each sample by the CIE XYZ CMFs (color matching functions) and the spectral power distribution of the desired illuminant. We choose the standard illuminant D65 because we want to compute a color in the sRGB color space.

We then sum (integrate) and normalize all the samples to obtain $\fNormal$ in the XYZ color space. From there, a simple color space conversion yields a linear sRGB color or a non-linear sRGB color after applying the opto-electronic transfer function (OETF, commonly known as "gamma" curve). Note that for some materials such as gold the final sRGB color might fall out of gamut. We use a simple normalization step as a cheap form of gamut remapping but it would be interesting to consider computing values in a color space with a wider gamut (for instance BT.2020).

To achieve the desired result we used the ICE 1931 2 degrees CMFs, from 360nm to 830nm at 1nm intervals ([source](http://cvrl.ioo.ucl.ac.uk/cmfs.htm)), and the CIE Standard Illuminant D65 relative spectral power distribution, from 300nm to 830nm, at 5nm intervals ([source](http://files.cie.co.at/204.xls)).

Our implementation is presented in listing [specularColorImpl], with the actual data omitted for brevity.

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
*リスト [specularColorImpl]: C++ implementation to compute the base color of a metallic surface from spectral data*

Special thanks to Naty Hoffman for his valuable help on this topic.
