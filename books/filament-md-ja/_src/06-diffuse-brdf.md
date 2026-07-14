## Diffuse BRDF

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


In the diffuse term, $f_m$ is a Lambertian function and the diffuse term of the BRDF becomes:

$$\begin{equation}
\fDiffuse(v,l) = \frac{\sigma}{\pi} \frac{1}{| \NoV | | \NoL |}
\int_\Omega D(m,\alpha) G(v,l,m) (v \cdot m) (l \cdot m) dm
\end{equation}$$

Our implementation will instead use a simple Lambertian BRDF that assumes a uniform diffuse response over the microfacets hemisphere:

$$\begin{equation}
\fDiffuse(v,l) = \frac{\sigma}{\pi}
\end{equation}$$

In practice, the diffuse reflectance $\sigma$ is multiplied later, as shown in listing [diffuseBRDF].

```glsl
float Fd_Lambert() {
    return 1.0 / PI;
}

vec3 Fd = diffuseColor * Fd_Lambert();
```
*リスト [diffuseBRDF]: Implementation of the diffuse Lambertian BRDF in GLSL*

The Lambertian BRDF is obviously extremely efficient and delivers results close enough to more complex models.

However, the diffuse part would ideally be coherent with the specular term and take into account the surface roughness. Both the Disney diffuse BRDF [#Burley12] and Oren-Nayar model [#Oren94] take the roughness into account and create some retro-reflection at grazing angles. Given our constraints we decided that the extra runtime cost does not justify the slight increase in quality. This sophisticated diffuse model also renders image-based and spherical harmonics more difficult to express and implement.

For completeness, the Disney diffuse BRDF expressed in [#Burley12] is the following:

$$\begin{equation}
\fDiffuse(v,l) = \frac{\sigma}{\pi} \schlick(n,l,1,\fGrazing) \schlick(n,v,1,\fGrazing)
\end{equation}$$

Where:

$$\begin{equation}
\fGrazing=0.5 + 2 \cdot \alpha cos^2(\theta_d)
\end{equation}$$

```glsl
float F_Schlick(float u, float f0, float f90) {
    return f0 + (f90 - f0) * pow(1.0 - u, 5.0);
}

float Fd_Burley(float NoV, float NoL, float LoH, float roughness) {
    float f90 = 0.5 + 2.0 * roughness * LoH * LoH;
    float lightScatter = F_Schlick(NoL, 1.0, f90);
    float viewScatter = F_Schlick(NoV, 1.0, f90);
    return lightScatter * viewScatter * (1.0 / PI);
}
```
*リスト [diffuseBRDF]: Implementation of the diffuse Disney BRDF in GLSL*

Figure [lambert_vs_disney] shows a comparison between a simple Lambertian diffuse BRDF and the higher quality Disney diffuse BRDF, using a fully rough dielectric material. For comparison purposes, the right sphere was mirrored. The surface response is very similar with both BRDFs but the Disney one exhibits some nice retro-reflections at grazing angles (look closely at the left edge of the spheres).

![Figure [lambert_vs_disney]: Comparison between the Lambertian diffuse BRDF (left) and the Disney diffuse BRDF (right)](/images/filament-md-ja/diagram_lambert_vs_disney.png)

We could allow artists/developers to choose the Disney diffuse BRDF depending on the quality they desire and the performance of the target device. It is important to note however that the Disney diffuse BRDF is not energy conserving as expressed here.

## Standard model summary

**Specular term**: a Cook-Torrance specular microfacet model, with a GGX normal distribution function, a Smith-GGX height-correlated visibility function, and a Schlick Fresnel function.

**Diffuse term**: a Lambertian diffuse model.

The full GLSL implementation of the standard model is shown in listing [glslBRDF].

```glsl
float D_GGX(float NoH, float a) {
    float a2 = a * a;
    float f = (NoH * a2 - NoH) * NoH + 1.0;
    return a2 / (PI * f * f);
}

vec3 F_Schlick(float u, vec3 f0) {
    return f0 + (vec3(1.0) - f0) * pow(1.0 - u, 5.0);
}

float V_SmithGGXCorrelated(float NoV, float NoL, float a) {
    float a2 = a * a;
    float GGXL = NoV * sqrt((-NoL * a2 + NoL) * NoL + a2);
    float GGXV = NoL * sqrt((-NoV * a2 + NoV) * NoV + a2);
    return 0.5 / (GGXV + GGXL);
}

float Fd_Lambert() {
    return 1.0 / PI;
}

void BRDF(...) {
    vec3 h = normalize(v + l);

    float NoV = abs(dot(n, v)) + 1e-5;
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    float NoH = clamp(dot(n, h), 0.0, 1.0);
    float LoH = clamp(dot(l, h), 0.0, 1.0);

    // perceptually linear roughness to roughness (see parameterization)
    float roughness = perceptualRoughness * perceptualRoughness;

    float D = D_GGX(NoH, roughness);
    vec3  F = F_Schlick(LoH, f0);
    float V = V_SmithGGXCorrelated(NoV, NoL, roughness);

    // specular BRDF
    vec3 Fr = (D * V) * F;

    // diffuse BRDF
    vec3 Fd = diffuseColor * Fd_Lambert();

    // apply lighting...
}
```
*リスト [glslBRDF]: Evaluation of the BRDF in GLSL*
