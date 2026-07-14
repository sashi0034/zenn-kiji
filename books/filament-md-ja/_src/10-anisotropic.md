## Anisotropic model

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


The standard material model described previously can only describe isotropic surfaces, that is, surfaces whose properties are identical in all directions. Many real-world materials, such as brushed metal, can, however, only be replicated using an anisotropic model.

![Figure [anisotropic]: Comparison of isotropic material (left) and anisotropic material (right)](/images/filament-md-ja/material_anisotropic.png)

### Anisotropic specular BRDF

The isotropic specular BRDF described previously can be modified to handle anisotropic materials. Burley achieves this by using an anisotropic GGX NDF:

$$\begin{equation}
D_{aniso}(h,\alpha) = \frac{1}{\pi \alpha_t \alpha_b} \frac{1}{((\frac{t \cdot h}{\alpha_t})^2 + (\frac{b \cdot h}{\alpha_b})^2 + (\NoH)^2)^2}
\end{equation}$$

This NDF unfortunately relies on two supplemental roughness terms noted $\alpha_b$, the roughness along the bitangent direction, and $\alpha_t$, the roughness along the tangent direction. Neubelt and Pettineo [#Neubelt13] propose a way to derive $\alpha_b$ from $\alpha_t$ by using an _anisotropy_ parameter that describes the relationship between the two roughness values for a material:

$$
\begin{align*}
  \alpha_t &= \alpha \\
  \alpha_b &= lerp(0, \alpha, 1 - anisotropy)
\end{align*}
$$

The relationship defined in [#Burley12] is different, offers more pleasant and intuitive results, but is slightly more expensive:

$$
\begin{align*}
  \alpha_t &= \frac{\alpha}{\sqrt{1 - 0.9 \times anisotropy}} \\
  \alpha_b &= \alpha \sqrt{1 - 0.9 \times anisotropy}
\end{align*}
$$

We instead opted to follow the relationship described in [#Kulla17] as it allows creation of sharp highlights:

$$
\begin{align*}
  \alpha_t &= \alpha \times (1 + anisotropy) \\
  \alpha_b &= \alpha \times (1 - anisotropy)
\end{align*}
$$

Note that this NDF requires the tangent and bitangent directions in addition to the normal direction. Since these directions are already needed for normal mapping, providing them may not be an issue.

The resulting implementation is described in listing [anisotropicBRDF].

```glsl
float at = max(roughness * (1.0 + anisotropy), 0.001);
float ab = max(roughness * (1.0 - anisotropy), 0.001);

float D_GGX_Anisotropic(float NoH, const vec3 h,
        const vec3 t, const vec3 b, float at, float ab) {
    float ToH = dot(t, h);
    float BoH = dot(b, h);
    float a2 = at * ab;
    highp vec3 v = vec3(ab * ToH, at * BoH, a2 * NoH);
    highp float v2 = dot(v, v);
    float w2 = a2 / v2;
    return a2 * w2 * w2 * (1.0 / PI);
}
```
*リスト [anisotropicBRDF]: Implementation of Burley's anisotropic NDF in GLSL*

In addition, [#Heitz14] presents an anisotropic masking-shadowing function to match the height-correlated GGX distribution. The masking-shadowing term can be greatly simplified by using the visibility function instead:

$$\begin{equation}
G(v,l,h,\alpha) = \frac{\chi^+(\VoH) \chi^+(\LoH)}{1 + \Lambda(v) + \Lambda(l)}
\end{equation}$$

$$\begin{equation}
\Lambda(m) = \frac{-1 + \sqrt{1 + \alpha_0^2 tan^2(\theta_m)}}{2} = \frac{-1 + \sqrt{1 + \alpha_0^2 \frac{(1 - cos^2(\theta_m))}{cos^2(\theta_m)}}}{2}
\end{equation}$$

Where:

$$\begin{equation}
\alpha_0 = \sqrt{cos^2(\phi_0)\alpha_x^2 + sin^2(\phi_0)\alpha_y^2}
\end{equation}$$

After derivation we obtain:

$$\begin{equation}
V_{aniso}(\NoL,\NoV,\alpha) = \frac{1}{2((\NoL)\hat{\Lambda}_v+(\NoV)\hat{\Lambda}_l)} \\
\hat{\Lambda}_v = \sqrt{\alpha^2_t(t \cdot v)^2+\alpha^2_b(b \cdot v)^2+(\NoV)^2} \\
\hat{\Lambda}_l = \sqrt{\alpha^2_t(t \cdot l)^2+\alpha^2_b(b \cdot l)^2+(\NoL)^2}
\end{equation}$$

The term $ \hat{\Lambda}_v $ is the same for every light and can be computed only once if needed. The resulting implementation is described in listing [anisotropicV].

```glsl
float at = max(roughness * (1.0 + anisotropy), 0.001);
float ab = max(roughness * (1.0 - anisotropy), 0.001);

float V_SmithGGXCorrelated_Anisotropic(float at, float ab, float ToV, float BoV,
        float ToL, float BoL, float NoV, float NoL) {
    float lambdaV = NoL * length(vec3(at * ToV, ab * BoV, NoV));
    float lambdaL = NoV * length(vec3(at * ToL, ab * BoL, NoL));
    float v = 0.5 / (lambdaV + lambdaL);
    return saturateMediump(v);
}
```
*リスト [anisotropicV]: Implementation of the anisotropic visibility function in GLSL*

### Anisotropic parameterization

The anisotropic material model encompasses all the parameters previously defined for the standard material mode, plus an extra parameter described in table [anisotropicParameters].

        Parameter      |      Definition
----------------------:|:---------------------
**Anisotropy**         | Amount of anisotropy. Scalar between -1 and 1
*表 [anisotropicParameters]: Anisotropic model parameters*

No further remapping is required. Note that negative values will align the anisotropy with the bitangent direction instead of the tangent direction. Figure [anisotropyParameter] shows how the anisotropy parameter affect the appearance of a rough metallic surface.

![Figure [anisotropyParameter]: Anisotropy varying from 0.0 (left) to 1.0 (right)](/images/filament-md-ja/materials/anisotropy.png)
