## Static lighting

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


[TODO] Spherical-harmonics or spherical-gaussian lightmaps, irradiance volumes, PRT?…

## Transparency and translucency lighting

Transparent and translucent materials are important to add realism and correctness to scenes. Filament must therefore provide lighting models for both types of materials to allow artists to properly recreate realistic scenes. Translucency can also be used effectively in a number of non-realistic settings.

### Transparency

To properly light a transparent surface, we must first understand how the material's opacity is applied. Observe a window and you will see that the diffuse reflectance is transparent. On the other hand, the brighter the specular reflectance, the less opaque the window appears. This effect can be seen in figure [cameraTransparency]: the scene is properly reflected onto the glass surfaces but the specular highlight of the sun is bright enough to appear opaque.

![Figure [cameraTransparency]: Example of a complex object where lit surface transparency plays an important role](/images/filament-md-ja/screenshot_camera_transparency.jpg)

![Figure [litCar]: Example of a complex object where lit surface transparency plays an important role](/images/filament-md-ja/screenshot_car.jpg)

To properly implement opacity, we will use the premultiplied alpha format. Given a desired opacity noted $ \alpha_{opacity} $ and a diffuse color $ \sigma $ (linear, unpremultiplied), we can compute the effective opacity of a fragment.

$$\begin{align*}
color &= \sigma * \alpha_{opacity} \\
opacity &= \alpha_{opacity}
\end{align*}$$

The physical interpretation is that the RGB components of the source color define how much light is emitted by the pixel, whereas the alpha component defines how much of the light behind the pixel is blocked by said pixel. We must therefore use the following blending functions:

$$\begin{align*}
Blend_{src} &= 1 \\
Blend_{dst} &= 1 - src_{\alpha}
\end{align*}$$

The GLSL implementation of these equations is presented in listing [surfaceTransparency].

```glsl
// baseColor has already been premultiplied
vec4 shadeSurface(vec4 baseColor) {
    float alpha = baseColor.a;

    vec3 diffuseColor = evaluateDiffuseLighting();
    vec3 specularColor = evaluateSpecularLighting();    

    return vec4(diffuseColor + specularColor, alpha);
}
```
*リスト [surfaceTransparency]: Implementation of lit surface transparency in GLSL*

### Translucency

Translucent materials can be divided into two categories:
- Surface translucency
-  Volume translucency

Volume translucency is useful to light particle systems, for instance clouds or smoke. Surface translucency can be used to imitate materials with transmitted scattering such as wax, marble, skin, etc.

[TODO] Surface translucency (BRDF+BTDF, BSSRDF)

![Figure [translucency]: Front-lit translucent object (left) and back-lit translucent object (right), using approximated BTDF and BSSRDF. Model: Lucy from the Stanford University Computer Graphics Laboratory](/images/filament-md-ja/screenshot_translucency.png)

## Occlusion

Occlusion is an important darkening factor used to recreate shadowing at various scales:

**Small&nbsp;scale**

Micro-occlusion used to handle creases, cracks and cavities.

**Medium&nbsp;scale**

Macro-occlusion used to handle occlusion by an object's own geometry or by geometry baked in normal maps (bricks, etc.).

**Large&nbsp;scale**

Occlusion coming from contact between objects, or from an object's own geometry.

We currently ignore micro-occlusion, which is often exposed in tools and engines under the form of a "cavity map". Sébastien Lagarde offers an interesting discussion in [#Lagarde14] on how micro-occlusion is handled in Frostbite: diffuse micro-occlusion is pre-baked in diffuse maps and specular micro-occlusion is pre-baked in reflectance textures.
In our system, micro-occlusion can simply be baked in the base color map. This must be done knowing that the specular light will not be affected by micro-occlusion.

Medium scale ambient occlusion is pre-baked in ambient occlusion maps, exposed as a material parameter, as seen in the material parameterization section earlier.

Large scale ambient occlusion is often computed using screen-space techniques such as *SSAO* (screen-space ambient occlusion), *HBAO* (horizon based ambient occlusion), etc. Note that these techniques can also contribute to medium scale ambient occlusion when the camera is close enough to surfaces.

**Note**: to prevent over darkening when using both medium and large scale occlusion, Lagarde recommends to use $min({AO}_{medium}, {AO}_{large})$.

### Diffuse occlusion

Morgan McGuire formalizes ambient occlusion in the context of physically based rendering in [#McGuire10]. In his formulation, McGuire defines an ambient illumination function $ L_a $, which in our case is encoded with spherical harmonics. He also defines a visibility function $V$, with $V(l)=1$ if there is an unoccluded line of sight from the surface in direction $l$, and 0 otherwise.

With these two functions, the ambient term of the rendering equation can be expressed as shown in equation $\ref{diffuseAO}$.

$$\begin{equation}\label{diffuseAO}
L(l,v) = \int_{\Omega} f(l,v) L_a(l) V(l) \left< \NoL \right> dl
\end{equation}$$

This expression can be approximated by separating the visibility term from the illumination function, as shown in equation $\ref{diffuseAOApprox}$.

$$\begin{equation}\label{diffuseAOApprox}
L(l,v) \approx \left( \pi \int_{\Omega} f(l,v) L_a(l) dl \right) \left( \frac{1}{\pi} \int_{\Omega} V(l) \left< \NoL \right> dl \right)
\end{equation}$$

This approximation is only exact when the distant light $ L_a $ is constant and $f$ is a Lambertian term. McGuire states however that this approximation is reasonable if both functions are relatively smooth over most of the sphere. This happens to be the case with a distant light probe (IBL).

The left term of this approximation is the pre-computed diffuse component of our IBL. The right term is a scalar factor between 0 and 1 that indicates the fractional accessibility of a point. Its opposite is the diffuse ambient occlusion term, show in equation $\ref{diffuseAOTerm}$.

$$\begin{equation}\label{diffuseAOTerm}
{AO} = 1 - \frac{1}{\pi} \int_{\Omega} V(l) \left< \NoL \right> dl
\end{equation}$$

Since we use a pre-computed diffuse term, we cannot compute the exact accessibility of shaded points at runtime. To compensate for this lack of information in our precomputed term, we partially reconstruct incident lighting by applying an ambient occlusion factor specific to the surface's material at the shaded point.

In practice, baked ambient occlusion is stored as a grayscale texture which can often be lower resolution than other textures (base color or normals for instance). It is important to note that the ambient occlusion property of our material model intends to recreate macro-level diffuse ambient occlusion. While this approximation is not physically correct, it constitutes an acceptable tradeoff of quality vs performance.

Figure [aoComparison] shows two different materials without and with diffuse ambient occlusion. Notice how the material ambient occlusion is used to recreate the natural shadowing that occurs between the different tiles. Without ambient occlusion, both materials appear too flat.

![Figure [aoComparison]: Comparison of materials without diffuse ambient occlusion (left) and with (right)](/images/filament-md-ja/screenshot_ao.jpg)

Applying baked diffuse ambient occlusion in a GLSL shader is straightforward, as shown in listing [bakedDiffuseAO].

```glsl
// diffuse indirect
vec3 indirectDiffuse = max(irradianceSH(n), 0.0) * Fd_Lambert();
// ambient occlusion
indirectDiffuse *= texture2D(aoMap, outUV).r;
```
*リスト [bakedDiffuseAO]: Implementation of baked diffuse ambient occlusion in GLSL*

Note how the ambient occlusion term is only applied to indirect lighting.

### Specular occlusion

Specular micro-occlusion can be derived from $\fNormal$, itself derived from the diffuse color. The derivation is based on the knowledge that no real-world material has a reflectance lower than 2%. Values in the 0-2% range can therefore be treated as pre-baked specular occlusion used to smoothly extinguish the Fresnel term.

```glsl
float f90 = clamp(dot(f0, 50.0 * 0.33), 0.0, 1.0);
// cheap luminance approximation
float f90 = clamp(50.0 * f0.g, 0.0, 1.0);
```
*リスト [specularMicroOcclusion]: Pre-baked specular occlusion in GLSL*

The derivations mentioned earlier for ambient occlusion assume Lambertian surfaces and are only valid for indirect diffuse lighting. The lack of information about surface accessibility is particularly harmful to the reconstruction of indirect specular lighting. It usually manifests itself as light leaks.

Sébastien Lagarde proposes an empirical approach to derive the specular occlusion term from the diffuse occlusion term in [#Lagarde14]. The result does not have any physical basis but produces visually pleasant results. The goal of his formulation is return the diffuse occlusion term unmodified for rough surfaces. For smooth surfaces, the formulation, implemented in listing [specularOcclusion], reduces the influence of occlusion at normal incidence and increases it at grazing angles.

```glsl
float computeSpecularAO(float NoV, float ao, float roughness) {
    return clamp(pow(NoV + ao, exp2(-16.0 * roughness - 1.0)) - 1.0 + ao, 0.0, 1.0);
}

// specular indirect
vec3 indirectSpecular = evaluateSpecularIBL(r, perceptualRoughness);
// ambient occlusion
float ao = texture2D(aoMap, outUV).r;
indirectSpecular *= computeSpecularAO(NoV, ao, roughness);
```
*リスト [specularOcclusion]: Implementation of Lagarde's specular occlusion factor in GLSL*

Note how the specular occlusion factor is only applied to indirect lighting.

#### Horizon specular occlusion

When computing the specular IBL contribution for a surface that uses a normal map, it is possible to end up with a reflection vector pointing towards the surface. If this reflection vector is used for shading directly, the surface will be lit in places where it should not be lit (assuming opaque surfaces). This is another occurrence of light leaking that can easily be minimized using a simple technique described by Jeff Russell [#Russell15].

The key idea is to occlude light coming from behind the surface. This can easily be achieved since a negative dot product between the reflected vector and the surface's normal indicates a reflection vector pointing towards the surface. Our implementation shown in listing [horizonOcclusion] is similar to Russell's, albeit without the artist controlled horizon fading factor.

```glsl
// specular indirect
vec3 indirectSpecular = evaluateSpecularIBL(r, perceptualRoughness);

// horizon occlusion with falloff, should be computed for direct specular too
float horizon = min(1.0 + dot(r, n), 1.0);
indirectSpecular *= horizon * horizon;
```
*リスト [horizonOcclusion]: Implementation of horizon specular occlusion in GLSL*

Horizon specular occlusion fading is cheap but can easily be omitted to improve performance as needed.

## Normal mapping

There are two common use cases of normal maps: replacing high-poly meshes with low-poly meshes (using a base map) and adding surface details (using a detail map).

Let's imagine that we want to render a piece of furniture covered in tufted leather. Modeling the geometry to accurately represent the tufted pattern would require too many triangles so we instead bake a high-poly mesh into a normal map. Once the base map is applied to a simplified mesh (in this case, a quad), we get the result in figure [normalMapped]. The base map used to create this effect is shown in figure [baseNormalMap].

![Figure [normalMapped]: Low-poly mesh without normal mapping (left) and with (right)](/images/filament-md-ja/screenshot_normal_mapping.jpg)

![Figure [baseNormalMap]: Normal map used as a base map](/images/filament-md-ja/screenshot_normal_map.jpg)

A simple problem arises if we now want to combine this base map with a second normal map. For instance, let's use the detail map shown in figure [detailNormalMap] to add cracks in the leather.

![Figure [detailNormalMap]: Normal map used as a detail map](/images/filament-md-ja/screenshot_normal_map_detail.jpg)

Given the nature of normal maps (XYZ components stored in tangent space), it is fairly obvious that naive approaches such as linear or overlay blending cannot work. We will use two more advanced techniques: a mathematically correct one and an approximation suitable for real-time shading.

### Reoriented normal mapping

Colin Barré-Brisebois and Stephen Hill propose in [#Hill12] a mathematically sound solution called *Reoriented Normal Mapping*, which consists in rotating the basis of the detail map onto the normal from the base map. This technique relies on the shortest arc quaternion to apply the rotation, which greatly simplifies thanks to the properties of the tangent space.

Following the simplifications described in [#Hill12], we can produce the GLSL implementation shown in listing [reorientedNormalMapping].

```glsl
vec3 t = texture(baseMap,   uv).xyz * vec3( 2.0,  2.0, 2.0) + vec3(-1.0, -1.0,  0.0);
vec3 u = texture(detailMap, uv).xyz * vec3(-2.0, -2.0, 2.0) + vec3( 1.0,  1.0, -1.0);
vec3 r = normalize(t * dot(t, u) - u * t.z);
return r;
```
*リスト [reorientedNormalMapping]: Implementation of reoriented normal mapping in GLSL*

Note that this implementation assumes that the normals are stored uncompressed and in the [0..1] range in the source textures.

The normalization step is not strictly necessary and can be skipped if the technique is used at runtime. If so, the computation of `r` becomes `t * dot(t, u) / t.z - u`.

Since this technique is slightly more expensive than the one described below, we will mostly use it offline. We therefore provide a simple offline tool to combine two normal maps. Figure [blendedNormalMaps] presents the output of the tool with the base map and the detail map shown previously.

![Figure [blendedNormalMaps]: Blended normal and detail map (left) and resulting render when combined with a diffuse map (right)](/images/filament-md-ja/screenshot_normal_map_blended.jpg)

### UDN blending

The technique called UDN blending, described in [#Hill12], is a variant of the partial derivative blending technique. Its main advantage is the low number of shader instructions it requires (see listing [udnBlending]). While it leads to a reduction in details over flat areas, UDN blending is interesting if blending must be performed at runtime.

```glsl
vec3 t = texture(baseMap,   uv).xyz * 2.0 - 1.0;
vec3 u = texture(detailMap, uv).xyz * 2.0 - 1.0;
vec3 r = normalize(t.xy + u.xy, t.z);
return r;
```
*リスト [udnBlending]: Implementation of UDN blending in GLSL*

The results are visually close to Reoriented Normal Mapping but a careful comparison of the data shows that UDN is indeed less correct. Figure [blendedNormalMapsUDN] presents the result of the UDN blending approach using the same source data as in the previous examples.

![Figure [blendedNormalMapsUDN]: Blended normal and detail map using the UDN blending technique](/images/filament-md-ja/screenshot_normal_map_blended_udn.jpg)

# Volumetric effects

## Exponential height fog

![Figure [exponentialHeightFog1]: Example of directional in-scattering with exponential height fog](/images/filament-md-ja/screenshot_fog1.jpg)

![Figure [exponentialHeightFog2]: Example of directional in-scattering with exponential height fog](/images/filament-md-ja/screenshot_fog2.jpg)

# Anti-aliasing

[TODO] MSAA, geometric AA (normals and roughness), shader anti-aliasing (object-space shading?)
