## Specular BRDF

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


For the specular term, $f_r$ is a mirror BRDF that can be modeled with the Fresnel law, noted $F$ in the Cook-Torrance approximation of the microfacet model integration:

$$\begin{equation}
f_r(v,l) = \frac{D(h, \alpha) G(v, l, \alpha) F(v, h, f0)}{4(\NoV)(\NoL)}
\end{equation}$$

Given our real-time constraints, we must use an approximation for the three terms $D$, $G$ and $F$. [#Karis13a] has compiled a great list of formulations for these three terms that can be used with the Cook-Torrance specular BRDF. The sections that follow describe the equations we picked for these terms.

### Normal distribution function (specular D)

[#Burley12] observed that long-tailed normal distribution functions (NDF) are a good fit for real-world surfaces. The GGX distribution described in [#Walter07] is a distribution with long-tailed falloff and short peak in the highlights, with a simple formulation suitable for real-time implementations. It is also a popular model, equivalent to the Trowbridge-Reitz distribution, in modern physically based renderers.

$$\begin{equation}
D_{GGX}(h,\alpha) = \frac{\aa}{\pi ( (\NoH)^2 (\aa - 1) + 1)^2}
\end{equation}$$

The GLSL implementation of the NDF, shown in listing [specularD], is simple and efficient.

```glsl
float D_GGX(float NoH, float roughness) {
    float a = NoH * roughness;
    float k = roughness / (1.0 - NoH * NoH + a * a);
    return k * k * (1.0 / PI);
}
```
*リスト [specularD]: Implementation of the specular D term in GLSL*

We can improve this implementation by using half precision floats. This optimization requires changes to the original equation as there are two problems when computing $1 - (\NoH)^2$ in half-floats. First, this computation suffers from floating point cancellation when $(\NoH)^2$ is close to 1 (highlights). Secondly $\NoH$ does not have enough precision around 1.

The solution involves Lagrange's identity:

$$\begin{equation}
| a \times b |^2 = |a|^2 |b|^2 - (a \cdot b)^2
\end{equation}$$

Since both $n$ and $h$ are unit vectors, $|n \times h|^2 = 1 - (\NoH)^2$. This allows us to compute $1 - (\NoH)^2$ directly with half precision floats by using a simple cross product. Listing [specularDfp16] shows the final optimized implementation.

```glsl
#define MEDIUMP_FLT_MAX    65504.0
#define saturateMediump(x) min(x, MEDIUMP_FLT_MAX)

float D_GGX(float roughness, float NoH, const vec3 n, const vec3 h) {
    vec3 NxH = cross(n, h);
    float a = NoH * roughness;
    float k = roughness / (dot(NxH, NxH) + a * a);
    float d = k * k * (1.0 / PI);
    return saturateMediump(d);
}
```
*リスト [specularDfp16]: Implementation of the specular D term in GLSL optimized for fp16*

### Geometric shadowing (specular G)

Eric Heitz showed in [#Heitz14] that the Smith geometric shadowing function is the correct and exact $G$ term to use. The Smith formulation is the following:

$$\begin{equation}
G(v,l,\alpha) = G_1(l,\alpha) G_1(v,\alpha)
\end{equation}$$

$G_1$ can in turn follow several models, and is commonly set to the GGX formulation:

$$\begin{equation}
G_1(v,\alpha) = G_{GGX}(v,\alpha) = \frac{2 (\NoV)}{\NoV + \sqrt{\aa + (1 - \aa) (\NoV)^2}}
\end{equation}$$

The full Smith-GGX formulation thus becomes:

$$\begin{equation}
G(v,l,\alpha) = \frac{2 (\NoL)}{\NoL + \sqrt{\aa + (1 - \aa) (\NoL)^2}} \frac{2 (\NoV)}{\NoV + \sqrt{\aa + (1 - \aa) (\NoV)^2}}
\end{equation}$$

We can observe that the dividends $2 (\NoL)$ and $2 (n \cdot v)$ allow us to simplify the original function $f_r$ by introducing a visibility function $V$:

$$\begin{equation}
f_r(v,l) = D(h, \alpha) V(v, l, \alpha) F(v, h, f_0)
\end{equation}$$

Where:

$$\begin{equation}
V(v,l,\alpha) = \frac{G(v, l, \alpha)}{4 (\NoV) (\NoL)} = V_1(l,\alpha) V_1(v,\alpha)
\end{equation}$$

And:

$$\begin{equation}
V_1(v,\alpha) = \frac{1}{\NoV + \sqrt{\aa + (1 - \aa) (\NoV)^2}}
\end{equation}$$

Heitz notes however that taking the height of the microfacets into account to correlate masking and shadowing leads to more accurate results. He defines the height-correlated Smith function thusly:

$$\begin{equation}
G(v,l,h,\alpha) = \frac{\chi^+(\VoH) \chi^+(\LoH)}{1 + \Lambda(v) + \Lambda(l)}
\end{equation}$$

$$\begin{equation}
\Lambda(m) = \frac{-1 + \sqrt{1 + \aa tan^2(\theta_m)}}{2} = \frac{-1 + \sqrt{1 + \aa \frac{(1 - cos^2(\theta_m))}{cos^2(\theta_m)}}}{2}
\end{equation}$$

Replacing $cos(\theta_m)$ by $\NoV$, we obtain:

$$\begin{equation}
\Lambda(v) = \frac{1}{2} \left( \frac{\sqrt{\aa + (1 - \aa)(\NoV)^2}}{\NoV} - 1 \right)
\end{equation}$$

From which we can derive the visibility function:

$$\begin{equation}
V(v,l,\alpha) = \frac{0.5}{\NoL \sqrt{(\NoV)^2 (1 - \aa) + \aa} + \NoV \sqrt{(\NoL)^2 (1 - \aa) + \aa}}
\end{equation}$$

The GLSL implementation of the visibility term, shown in listing [specularV], is a bit more expensive than we would like since it requires two `sqrt` operations.

```glsl
float V_SmithGGXCorrelated(float NoV, float NoL, float roughness) {
    float a2 = roughness * roughness;
    float GGXV = NoL * sqrt(NoV * NoV * (1.0 - a2) + a2);
    float GGXL = NoV * sqrt(NoL * NoL * (1.0 - a2) + a2);
    return 0.5 / (GGXV + GGXL);
}
```
*リスト [specularV]: Implementation of the specular V term in GLSL*

We can optimize this visibility function by using an approximation after noticing that all the terms under the square roots are squares and that all the terms are in the $[0..1]$ range:

$$\begin{equation}
V(v,l,\alpha) = \frac{0.5}{\NoL (\NoV (1 - \alpha) + \alpha) + \NoV (\NoL (1 - \alpha) + \alpha)}
\end{equation}$$

This approximation is mathematically wrong but saves two square root operations and is good enough for real-time mobile applications, as shown in listing [approximatedSpecularV].

```glsl
float V_SmithGGXCorrelatedFast(float NoV, float NoL, float roughness) {
    float a = roughness;
    float GGXV = NoL * (NoV * (1.0 - a) + a);
    float GGXL = NoV * (NoL * (1.0 - a) + a);
    return 0.5 / (GGXV + GGXL);
}
```
*リスト [approximatedSpecularV]: Implementation of the approximated specular V term in GLSL*

[#Hammon17] proposes the same approximation based on the same observation that the square root can be removed. It does so by rewriting the expressions as _lerps_:

$$\begin{equation}
V(v,l,\alpha) = \frac{0.5}{lerp(2 (\NoL) (\NoV), \NoL + \NoV, \alpha)}
\end{equation}$$

### Fresnel (specular F)

The Fresnel effect plays an important role in the appearance of physically based materials. This effect models the fact that the amount of light the viewer sees reflected from a surface depends on the viewing angle. Large bodies of water are a perfect way to experience this phenomenon, as shown in figure [fresnelLake]. When looking at the water straight down (at normal incidence) you can see through the water. However, when looking further out in the distance (at grazing angle, where perceived light rays are getting parallel to the surface), you will see the specular reflections on the water become more intense.

The amount of light reflected depends not only on the viewing angle, but also on the index of refraction (IOR) of the material. At normal incidence (perpendicular to the surface, or 0 degree angle), the amount of light reflected back is noted $\fNormal$ and can be derived from the IOR as we will see in section [Reflectance remapping]. The amount of light reflected back at grazing angle is noted $\fGrazing$ and approaches 100% for smooth materials.

![Figure [fresnelLake]: The Fresnel effect is particularly evident on large bodies of water](/images/filament-md-ja/photo_fresnel_lake.jpg)

More formally, the Fresnel term defines how light reflects and refracts at the interface between two different media, or the ratio of reflected and transmitted energy. [#Schlick94] describes an inexpensive approximation of the Fresnel term for the Cook-Torrance specular BRDF:

$$\begin{equation}
F_{Schlick}(v,h,\fNormal,\fGrazing) = \fNormal + (\fGrazing - \fNormal)(1 - \VoH)^5
\end{equation}$$

The constant $\fNormal$ represents the specular reflectance at normal incidence and is achromatic for dielectrics, and chromatic for metals. The actual value depends on the index of refraction of the interface. The GLSL implementation of this term requires the use of a `pow`, as shown in listing [specularF], which can be replaced by a few multiplications.

```glsl
vec3 F_Schlick(float u, vec3 f0, float f90) {
    return f0 + (vec3(f90) - f0) * pow(1.0 - u, 5.0);
}
```
*リスト [specularF]: Implementation of the specular F term in GLSL*

This Fresnel function can be seen as interpolating between the incident specular reflectance and the reflectance at grazing angles, represented here by $\fGrazing$. Observation of real world materials show that both dielectrics and conductors exhibit achromatic specular reflectance at grazing angles and that the Fresnel reflectance is 1.0 at 90 degrees. A more correct $\fGrazing$ is discussed in section [Specular occlusion].

Using $\fGrazing$ set to 1, the Schlick approximation for the Fresnel term can be optimized for scalar operations by refactoring the code slightly. The result is shown in listing [scalarSpecularF].

```glsl
vec3 F_Schlick(float u, vec3 f0) {
    float f = pow(1.0 - u, 5.0);
    return f + f0 * (1.0 - f);
}
```
*リスト [scalarSpecularF]: Scalar optimization of the specular F term in GLSL*
