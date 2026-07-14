## Subsurface model

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


[TODO]

### Subsurface specular BRDF

[TODO]

### Subsurface parameterization

[TODO]

## Cloth model

All the material models described previously are designed to simulate dense surfaces, both at a macro and at a micro level. Clothes and fabrics are however often made of loosely connected threads that absorb and scatter incident light. The microfacet BRDFs presented earlier do a poor job of recreating the nature of cloth due to their underlying assumption that a surface is made of random grooves that behave as perfect mirrors. When compared to hard surfaces, cloth is characterized by a softer specular lobe with a large falloff and the presence of fuzz lighting, caused by forward/backward scattering. Some fabrics also exhibit two-tone specular colors (velvets for instance).

Figure [materialCloth] shows how a traditional microfacet BRDF fails to capture the appearance of a sample of denim fabric. The surface appears rigid (almost plastic-like), more similar to a tarp than a piece of clothing. This figure also shows how important the softer specular lobe caused by absorption and scattering is to the faithful recreation of the fabric.

![Figure [materialCloth]: Comparison of denim fabric rendered using a traditional microfacet BRDF (left) and our cloth BRDF (right)](/images/filament-md-ja/screenshot_cloth.png)

Velvet is an interesting use case for a cloth material model. As shown in figure [materialVelvet] this type of fabric exhibits strong rim lighting due to forward and backward scattering. These scattering events are caused by fibers standing straight at the surface of the fabric. When the incident light comes from the direction opposite to the view direction, the fibers will forward-scatter the light. Similarly, when the incident light from the same direction as the view direction, the fibers will scatter the light backward.

![Figure [materialVelvet]: Velvet fabric showcasing forward and backward scattering](/images/filament-md-ja/screenshot_cloth_velvet.png)

Since fibers are flexible, we should in theory model the ability to groom the surface. While our model does not replicate this characteristic, it does model a visible front facing specular contribution that can be attributed to the random variance in the direction of the fibers.

It is important to note that there are types of fabrics that are still best modeled by hard surface material models. For instance, leather, silk and satin can be recreated using the standard or anisotropic material models.

### Cloth specular BRDF

The cloth specular BRDF we use is a modified microfacet BRDF as described by Ashikhmin and Premoze in [#Ashikhmin07]. In their work, Ashikhmin and Premoze note that the distribution term is what contributes most to a BRDF and that the shadowing/masking term is not necessary for their velvet distribution. The distribution term itself is an inverted Gaussian distribution. This helps achieve fuzz lighting (forward and backward scattering) while an offset is added to simulate the front facing specular contribution. The so-called velvet NDF is defined as follows:

$$\begin{equation}
D_{velvet}(v,h,\alpha) = c_{norm}(1 + 4 exp\left(\frac{-{cot}^2\theta_{h}}{\alpha^2}\right))
\end{equation}$$

This NDF is a variant of the NDF the same authors describe in [#Ashikhmin00], notably modified to include an offset (set to 1 here) and an amplitude (4). In [#Neubelt13], Neubelt and Pettineo propose a normalized version of this NDF:

$$\begin{equation}
D_{velvet}(v,h,\alpha) = \frac{1}{\pi(1 + 4\alpha^2)} (1 + 4 \frac{exp\left(\frac{-{cot}^2\theta_{h}}{\alpha^2}\right)}{{sin}^4\theta_{h}})
\end{equation}$$

For the full specular BRDF, we also follow [#Neubelt13] and replace the traditional denominator with a smoother variant:

$$\begin{equation}\label{clothSpecularBRDF}
f_{r}(v,h,\alpha) = \frac{D_{velvet}(v,h,\alpha)}{4(\NoL + \NoV - (\NoL)(\NoV))}
\end{equation}$$

The implementation of the velvet NDF is presented in listing [clothBRDF], optimized to properly fit in half float formats and to avoid computing a costly cotangent, relying instead on trigonometric identities. Note that we removed the Fresnel component from this BRDF.

```glsl
float D_Ashikhmin(float roughness, float NoH) {
    // Ashikhmin 2007, "Distribution-based BRDFs"
	float a2 = roughness * roughness;
	float cos2h = NoH * NoH;
	float sin2h = max(1.0 - cos2h, 0.0078125); // 2^(-14/2), so sin2h^2 > 0 in fp16
	float sin4h = sin2h * sin2h;
	float cot2 = -cos2h / (a2 * sin2h);
	return 1.0 / (PI * (4.0 * a2 + 1.0) * sin4h) * (4.0 * exp(cot2) + sin4h);
}
```
*リスト [clothBRDF]: Implementation of Ashikhmin's velvet NDF in GLSL*

In [#Estevez17] Estevez and Kulla propose a different NDF (called the "Charlie" sheen) that is based on an exponentiated sinusoidal instead of an inverted Gaussian. This NDF is appealing for several reasons: its parameterization feels more natural and intuitive, it provides a softer appearance and, as shown in equation $\ref{charlieNDF}$, its implementation is simpler:

$$\begin{equation}\label{charlieNDF}
D(m) = \frac{(2 + \frac{1}{\alpha}) sin(\theta)^{\frac{1}{\alpha}}}{2 \pi}
\end{equation}$$

[#Estevez17] also presents a new shadowing term that we omit here because of its cost. We instead rely on the visibility term from [#Neubelt13] (shown in equation $\ref{clothSpecularBRDF}$ above).
The implementation of this NDF is presented in listing [clothCharlieBRDF], optimized to properly fit in half float formats.

```glsl
float D_Charlie(float roughness, float NoH) {
    // Estevez and Kulla 2017, "Production Friendly Microfacet Sheen BRDF"
    float invAlpha  = 1.0 / roughness;
    float cos2h = NoH * NoH;
    float sin2h = max(1.0 - cos2h, 0.0078125); // 2^(-14/2), so sin2h^2 > 0 in fp16
    return (2.0 + invAlpha) * pow(sin2h, invAlpha * 0.5) / (2.0 * PI);
}
```
*リスト [clothCharlieBRDF]: Implementation of the "Charlie" NDF in GLSL*

#### Sheen color

To offer better control over the appearance of cloth and to give users the ability to recreate two-tone specular materials, we introduce the ability to directly modify the specular reflectance. Figure [materialClothSheen] shows an example of using the parameter we call "sheen color".

![Figure [materialClothSheen]: Blue fabric without (left) and with (right) sheen](/images/filament-md-ja/screenshot_cloth_sheen.png)

### Cloth diffuse BRDF

Our cloth material model still relies on a Lambertian diffuse BRDF. It is however slightly modified to be energy conservative (akin to the energy conservation of our clear coat material model) and offers an optional subsurface scattering term. This extra term is not physically based and can be used to simulate the scattering, partial absorption and re-emission of light in certain types of fabrics.

First, here is the diffuse term without the optional subsurface scattering:

$$\begin{equation}
f_{d}(v,h) = \frac{c_{diff}}{\pi}(1 - F(v,h))
\end{equation}$$

Where $F(v,h)$ is the Fresnel term of the cloth specular BRDF in equation $\ref{clothSpecularBRDF}$. In practice we've opted to leave out the $1 - F(v, h)$ term in the diffuse component. The effect is a bit subtle and we deemed it wasn't worth the added cost.

Subsurface scattering is implemented using the wrapped diffuse lighting technique, in its energy conservative form:

$$\begin{equation}
f_{d}(v,h) = \frac{c_{diff}}{\pi}(1 - F(v,h)) \left< \frac{\NoL + w}{(1 + w)^2} \right> \left< c_{subsurface} + \NoL \right>
\end{equation}$$

Where $w$ is a value between 0 and 1 defining by how much the diffuse light should wrap around the terminator. To avoid introducing another parameter, we fix $w = 0.5$. Note that with wrap diffuse lighting, the diffuse term must not be multiplied by $\NoL$. The effect of this cheap
subsurface scattering approximation can be seen in figure [materialClothSubsurface].

![Figure [materialClothSubsurface]: White cloth (left column) vs white cloth with brown subsurface scattering (right)](/images/filament-md-ja/screenshot_cloth_subsurface.png)

The complete implementation of our cloth BRDF, including sheen color and optional subsurface scattering, can be found in listing [clothFullBRDF].

```glsl
// specular BRDF
float D = distributionCloth(roughness, NoH);
float V = visibilityCloth(NoV, NoL);
vec3  F = sheenColor;
vec3 Fr = (D * V) * F;

// diffuse BRDF
float diffuse = diffuse(roughness, NoV, NoL, LoH);
#if defined(MATERIAL_HAS_SUBSURFACE_COLOR)
// energy conservative wrap diffuse
diffuse *= saturate((dot(n, light.l) + 0.5) / 2.25);
#endif
vec3 Fd = diffuse * pixel.diffuseColor;

#if defined(MATERIAL_HAS_SUBSURFACE_COLOR)
// cheap subsurface scatter
Fd *= saturate(subsurfaceColor + NoL);
vec3 color = Fd + Fr * NoL;
color *= (lightIntensity * lightAttenuation) * lightColor;
#else
vec3 color = Fd + Fr;
color *= (lightIntensity * lightAttenuation * NoL) * lightColor;
#endif
```
*リスト [clothFullBRDF]: Implementation of our cloth BRDF in GLSL*

### Cloth parameterization

The cloth material model encompasses all the parameters previously defined for the standard material mode except for _metallic_ and _reflectance_. Two extra parameters described in table [clothParameters] are also available.

       Parameter      |      Definition
---------------------:|:---------------------
**SheenColor**        | Specular tint to create two-tone specular fabrics (defaults to 0.04 to match the standard reflectance)
**SubsurfaceColor**   | Tint for the diffuse color after scattering and absorption through the material
*表 [clothParameters]: Cloth model parameters*

To create a velvet-like material, the base color can be set to black (or a dark color). Chromaticity information should instead be set on the sheen color. To create more common fabrics such as denim, cotton, etc. use the base color for chromaticity and use the default sheen color or set the sheen color to the luminance of the base color.
