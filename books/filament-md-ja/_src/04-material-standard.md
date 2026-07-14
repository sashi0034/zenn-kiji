# Material system

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


The sections below describe multiple material models to simplify the description of various surface features such as anisotropy or the clear coat layer. In practice however some of these models are condensed into a single one. For instance, the standard model, the clear coat model and the anisotropic model can be combined to form a single, more flexible and powerful model. Please refer to the [Materials documentation](./Materials.md.html) to get a description of the material models as implemented in Filament.

## Standard model

The goal of our model is to represent standard material appearances. A material model is described mathematically by a BSDF (Bidirectional Scattering Distribution Function), which is itself composed of two other functions: the BRDF (Bidirectional Reflectance Distribution Function) and the BTDF (Bidirectional Transmittance Function).

Since we aim to model commonly encountered surfaces, our standard material model will focus on the BRDF and ignore the BTDF, or approximate it greatly. Our standard model will therefore only be able to correctly mimic reflective, isotropic, dielectric or conductive surfaces with short mean free paths.

The BRDF describes the surface response of a standard material as a function made of two terms:
- A diffuse component, or $f_d$
- A specular component, or $f_r$

The relationship between a surface, the surface normal, incident light and these terms is shown in figure [frFd] (we ignore subsurface scattering for now):

![Figure [frFd]: Interaction of the light with a surface using BRDF model with a diffuse term $ f_d $ and a specular term $ f_r $](/images/filament-md-ja/diagram_fr_fd.png)

The complete surface response can be expressed as such:

$$\begin{equation}\label{brdf}
f(v,l)=f_d(v,l)+f_r(v,l)
\end{equation}$$

This equation characterizes the surface response for incident light from a single direction. The full rendering equation would require to integrate $l$ over the entire hemisphere.

Commonly encountered surfaces are usually not made of a flat interface so we need a model that can characterize the interaction of light with an irregular interface.

A microfacet BRDF is a good physically plausible BRDF for that purpose. Such BRDF states that surfaces are not smooth at a micro level, but made of a large number of randomly aligned planar surface fragments, called microfacets. Figure [microfacetVsFlat] shows the difference between a flat interface and an irregular interface at a micro level:

![Figure [microfacetVsFlat]: Irregular interface as modeled by a microfacet model (left) and flat interface (right)](/images/filament-md-ja/diagram_microfacet.png)

Only the microfacets whose normal is oriented halfway between the light direction and the view direction will reflect visible light, as shown in figure [microfacets].

![Figure [microfacets]: Microfacets](/images/filament-md-ja/diagram_macrosurface.png)

However, not all microfacets with a properly oriented normal will contribute reflected light as the BRDF takes into account masking and shadowing. This is illustrated in figure [microfacetShadowing].

![Figure [microfacetShadowing]: Masking and shadowing of microfacets](/images/filament-md-ja/diagram_shadowing_masking.png)

A microfacet BRDF is heavily influenced by a _roughness_ parameter which describes how smooth (low roughness) or how rough (high roughness) a surface is at a micro level. The smoother the surface, the more facets are aligned and the more pronounced the reflected light is. The rougher the surface, the fewer facets are oriented towards the camera and incoming light is scattered away from the camera after reflection, giving a blurry aspect to the specular highlights.

Figure [roughness] shows surfaces of different roughness and how light interacts with them.

![Figure [roughness]: Varying roughness (from left to right, rough to smooth) and the resulting BRDF specular component lobe](/images/filament-md-ja/diagram_roughness.png)

:::message
**Note: About roughness**

The roughness parameter as set by the user is called `perceptualRoughness` in the shader snippets throughout this document. The variable called `roughness` is the `perceptualRoughness` with a remapping explained in section [Parameterization].
:::
A microfacet model is described by the following equation (where x stands for the specular or diffuse component):

$$\begin{equation}
\fX(v,l) = \frac{1}{| \NoV | | \NoL |}
\int_\Omega D(m,\alpha) G(v,l,m) f_m(v,l,m) (v \cdot m) (l \cdot m) dm
\end{equation}$$

The term $D$ models the distribution of the microfacets (this term is also referred to as the NDF or Normal Distribution Function). This term plays a primordial role in the appearance of surfaces as shown in figure [roughness].

The term $G$ models the visibility (or occlusion or shadow-masking) of the microfacets.

Since this equation is valid for both the specular and diffuse components, the difference lies in the microfacet BRDF $f_m$.

It is important to note that this equation is used to integrate over the hemisphere at a _micro level_:

![Figure [microLevel]: Modeling the surface response at a single point requires an integration at the micro level](/images/filament-md-ja/diagram_micro_vs_macro.png)

The diagram above shows that at a macro level, the surfaces is considered flat. This helps simplify our equations by assuming that a shaded fragment lit from a single direction corresponds to a single point at the surface.

At a micro level however, the surface is not flat and we cannot assume a single ray of light anymore (we can however assume that the incident rays are parallel). Since the micro facets will scatter the light in different directions given a bundle of parallel incident rays, we must integrate the surface response over a hemisphere, noted m in the above diagram.

It is obviously not practical to compute the full integration over the microfacets hemisphere for each shaded fragment. We will therefore rely on approximations of the integration for both the specular and diffuse components.

## Dielectrics and conductors

To better understand some of the equations and behaviors shown below, we must first clearly understand the difference between metallic (conductor) and non-metallic (dielectric) surfaces.

We saw earlier that when incident light hits a surface governed by a BRDF, the light is reflected as two separate components: the diffuse reflectance and the specular reflectance. The modelization of this behavior is straightforward as shown in figure [bsdfBrdf].

![Figure [bsdfBrdf]: Modelization of the BRDF part of a BSDF](/images/filament-md-ja/diagram_fr_fd.png)

This modelization is a simplification of how the light actually interacts with the surface. In reality, part of the incident light will penetrate the surface, scatter inside, and exit the surface again as diffuse reflectance. This phenomenon is illustrated in figure [diffuseScattering].

![Figure [diffuseScattering]: Scattering of diffuse light](/images/filament-md-ja/diagram_scattering.png)

Here lies the difference between conductors and dielectrics. There is no subsurface scattering occurring with purely metallic materials, which means there is no diffuse component (and we will see later that this has an influence on the perceived color of the specular component). Scattering happens in dielectrics, which means they have both specular and diffuse components.

To properly modelize the BRDF we must therefore distinguish between dielectrics and conductors (scattering not shown for clarity), as shown in figure [dielectricConductor].

![Figure [dielectricConductor]: BRDF modelization for dielectric and conductor surfaces](/images/filament-md-ja/diagram_brdf_dielectric_conductor.png)

## Energy conservation

Energy conservation is one of the key components of a good BRDF for physically based rendering. An energy conservative BRDF states that the total amount of specular and diffuse reflectance energy is less than the total amount of incident energy. Without an energy conservative BRDF, artists must manually ensure that the light reflected off a surface is never more intense than the incident light.
