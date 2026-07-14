## Clear coat model

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


The standard material model described previously is a good fit for isotropic surfaces made of a single layer. Multi-layer materials are unfortunately fairly common, particularly materials with a thin translucent layer over a standard layer. Real world examples of such materials include car paints, soda cans, lacquered wood, acrylic, etc.

![Figure [materialClearCoat]: Comparison of a blue metallic surface under the standard material model (left) and the clear coat model (right)](/images/filament-md-ja/material_clear_coat.png)

A clear coat layer can be simulated as an extension of the standard material model by adding a second specular lobe, which implies evaluating a second specular BRDF. To simplify the implementation and parameterization, the clear coat layer will always be isotropic and dielectric. The base layer can be anything allowed by the standard model (dielectric or conductor).

Since incoming light will traverse the clear coat layer, we must also take the loss of energy into account as shown in figure [clearCoatModel]. Our model will however not simulate inter reflection and refraction behaviors.

![Figure [clearCoatModel]: Clear coat surface model](/images/filament-md-ja/diagram_clear_coat.png)

### Clear coat specular BRDF

The clear coat layer will be modeled using the same Cook-Torrance microfacet BRDF used in the standard model. Since the clear coat layer is always isotropic and dielectric, with low roughness values (see section [Clear coat parameterization]), we can choose cheaper DFG terms without notably sacrificing visual quality.

A survey of the terms listed in [#Karis13a] and [#Burley12] shows that the Fresnel and NDF terms we already use in the standard model are not computationally more expensive than other terms. [#Kelemen01] describes a much simpler term that can replace our Smith-GGX visibility term:

$$\begin{equation}
V(l,h) = \frac{1}{4(\LoH)^2}
\end{equation}$$

This masking-shadowing function is not physically based, as shown in [#Heitz14], but its simplicity makes it desirable for real-time rendering.

In summary, our clear coat BRDF is a Cook-Torrance specular microfacet model, with a GGX normal distribution function, a Kelemen visibility function, and a Schlick Fresnel function. Listing [kelemen] shows how trivial the GLSL implementation is.

```glsl
float V_Kelemen(float LoH) {
    return 0.25 / (LoH * LoH);
}
```
*リスト [kelemen]: Implementation of the Kelemen visibility term in GLSL*

**Note on the Fresnel term**

The Fresnel term of the specular BRDF requires $\fNormal$, the specular reflectance at normal incidence angle. This parameter can be computed from an index of refraction of an interface. We will assume that our clear coat layer is made of polyurethane, a common compound [used in coatings and varnishes](https://en.wikipedia.org/wiki/List_of_polyurethane_applications#Varnish), or similar. An air-polyurethane interface [has an IOR of 1.5](http://www.clearpur.com/transparent-polyurethanes/), from which we can deduce $\fNormal$:

$$\begin{equation}
\fNormal(1.5) = \frac{(1.5 - 1)^2}{(1.5 + 1)^2} = 0.04
\end{equation}$$

This corresponds to a Fresnel reflectance of 4% that we know is associated with common dielectric materials.

### Integration in the surface response

Because we must take into account the loss of energy caused by the addition of the clear coat layer, we can reformulate the BRDF from equation $\ref{brdf}$ thusly:

$$\begin{equation}
f(v,l)=\fDiffuse(v,l) (1 - F_c) + \fSpecular(v,l) (1 - F_c) + f_c(v,l)
\end{equation}$$

Where $F_c$ is the Fresnel term of the clear coat BRDF and $f_c$ the clear coat BRDF 

### Clear coat parameterization

The clear coat material model encompasses all the parameters previously defined for the standard material mode, plus two parameters described in table [clearCoatParameters].

        Parameter      |      Definition
----------------------:|:---------------------
**ClearCoat**          | Strength of the clear coat layer. Scalar between 0 and 1
**ClearCoatRoughness** | Perceived smoothness or roughness of the clear coat layer. Scalar between 0 and 1
*表 [clearCoatParameters]: Clear coat model parameters*

The clear coat roughness parameter is remapped and clamped in a similar way to the roughness parameter of the standard material.

Figure [clearCoat] and figure [clearCoatRoughness] show how the clear coat parameters affect the appearance of a surface.

![Figure [clearCoat]: Clear coat varying from 0.0 (left) to 1.0 (right) with metallic set to 1.0 and roughness to 0.8](/images/filament-md-ja/material_clear_coat1.png)

![Figure [clearCoatRoughness]: Clear coat roughness varying from 0.0 (left) to 1.0 (right) with metallic set to 1.0, roughness to 0.8 and clear coat to 1.0](/images/filament-md-ja/material_clear_coat2.png)

Listing [clearCoatBRDF] shows the GLSL implementation of the clear coat material model after remapping, parameterization and integration in the standard surface response.

```glsl
void BRDF(...) {
    // compute Fd and Fr from standard model

    // remapping and linearization of clear coat roughness
    clearCoatPerceptualRoughness = clamp(clearCoatPerceptualRoughness, 0.089, 1.0);
    clearCoatRoughness = clearCoatPerceptualRoughness * clearCoatPerceptualRoughness;

    // clear coat BRDF
    float  Dc = D_GGX(clearCoatRoughness, NoH);
    float  Vc = V_Kelemen(clearCoatRoughness, LoH);
    float  Fc = F_Schlick(0.04, LoH) * clearCoat; // clear coat strength
    float Frc = (Dc * Vc) * Fc;

    // account for energy loss in the base layer
    return color * ((Fd + Fr) * (1.0 - Fc) + Frc);
}
```
*リスト [clearCoatBRDF]: Implementation of the clear coat BRDF in GLSL*

### Base layer modification

The presence of a clear coat layer means that we should recompute $\fNormal$, since it is normally based on an air-material interface. The base layer thus requires $\fNormal$ to be computed based on a clear coat-material interface instead.

This can be achieved by computing the material's index of refraction (IOR) from $\fNormal$, then computing a new $\fNormal$ based on the newly computed IOR and the IOR of the clear coat layer (1.5).

First, we compute the base layer's IOR:

$$
IOR_{base} = \frac{1 + \sqrt{\fNormal}}{1 - \sqrt{\fNormal}}
$$

Then we compute the new $\fNormal$ from this new index of refraction:

$$
f_{0_{base}} = \left( \frac{IOR_{base} - 1.5}{IOR_{base} + 1.5} \right) ^2
$$

Since the clear coat layer's IOR is fixed, we can combine both steps to simplify:

$$
f_{0_{base}} = \frac{\left( 1 - 5 \sqrt{\fNormal} \right) ^2}{\left( 5 - \sqrt{\fNormal} \right) ^2}
$$

We should also modify the base layer's apparent roughness based on the IOR of the clear coat layer but this is something we have opted to leave out for now.
