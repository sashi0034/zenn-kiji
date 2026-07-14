## Improving the BRDFs

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


We mentioned in section [Energy conservation] that energy conservation is one of the key components of a good BRDF. Unfortunately the BRDFs explored previously suffer from two problems that we will examine below.

### Energy gain in diffuse reflectance

The Lambert diffuse BRDF does not account for the light that reflects at the surface and that is therefore not able to participate in the diffuse scattering event.

[TODO: talk about the issue with fr+fd]

### Energy loss in specular reflectance

The Cook-Torrance BRDF we presented earlier attempts to model several events at the microfacet level but does so by accounting for a single bounce of light. This approximation can cause a loss of energy at high roughness, the surface is not energy preserving. Figure [singleVsMultiBounce] shows why this loss of energy occurs. In the single bounce (or single scattering) model, a ray of light hitting the surface can be reflected back onto another microfacet and thus be discarded because of the masking and shadowing term. If we however account for multiple bounces (multiscattering), the same ray of light might escape the microfacet field and be reflected back towards the viewer.

![Figure [singleVsMultiBounce]: Single scattering (left) vs multiscattering](/images/filament-md-ja/diagram_single_vs_multi_scatter.png)

Based on this simple explanation, we can intuitively deduce that the rougher a surface is, the higher the chances are that energy gets lost because of the failure to account for multiple scattering events. This loss of energy appears to darken rough materials. Metallic surfaces are particularly affected because all of their reflectance is specular. This darkening effect is illustrated in figure [metallicRoughEnergyLoss]. With multiscattering, energy preservation can be achieved, as shown in figure [metallicRoughEnergyPreservation].

![Figure [metallicRoughEnergyLoss]: Darkening increases with roughness due to single scattering](/images/filament-md-ja/material_metallic_energy_loss.png)

![Figure [metallicRoughEnergyPreservation]: Energy preservation with multiscattering](/images/filament-md-ja/material_metallic_energy_preservation.png)

We can use a white furnace, a uniform lighting environment set to pure white, to validate the energy preservation property of a BRDF. When energy preservation is achieved, a purely reflective metallic surface ($\fNormal = 1$) should be indistinguishable from the background, no matter the roughness of said surface. Figure [whiteFurnaceLoss] shows what such a surface looks like with the specular BRDF presented in the previous sections. The loss of energy as the roughness increases is obvious. In contrast, figure [whiteFurnacePreservation] shows that accounting for multiscattering events addresses the energy loss.

![Figure [whiteFurnaceLoss]: Darkening increases with roughness due to single scattering](/images/filament-md-ja/material_furnace_energy_loss.png)

![Figure [whiteFurnacePreservation]: Energy preservation with multiscattering](/images/filament-md-ja/material_furnace_energy_preservation.png)

Multiple-scattering microfacet BRDFs are discussed in depth in [#Heitz16]. Unfortunately this paper only presents a stochastic evaluation of the multiscattering BRDF. This solution is therefore not suitable for real-time rendering. Kulla and Conty present a different approach in [#Kulla17]. Their idea is to add an energy compensation term as an additional BRDF lobe shown in equation $\ref{energyCompensationLobe}$:

$$\begin{equation}\label{energyCompensationLobe}
f_{ms}(l,v) = \frac{(1 - E(l)) (1 - E(v)) F_{avg}^2 E_{avg}}{\pi (1 - E_{avg}) (1 - F_{avg}(1 - E_{avg}))}
\end{equation}$$

Where $E$ is the directional albedo of the specular BRDF $f_r$, with $\fNormal$ set to 1:

$$\begin{equation}
E(l) = \int_{\Omega} f(l,v) (\NoV) dv
\end{equation}$$

The term $E_{avg}$ is the cosine-weighted average of $E$:

$$\begin{equation}
E_{avg} = 2 \int_0^1 E(\mu) \mu d\mu
\end{equation}$$

Similarly, $F_{avg}$ is the cosine-weighted average of the Fresnel term:

$$\begin{equation}
F_{avg} = 2 \int_0^1 F(\mu) \mu d\mu
\end{equation}$$

Both terms $E$ and $E_{avg}$ can be precomputed and stored in lookup tables. while $F_{avg}$ can be greatly simplified when the Schlick approximation is used:

$$\begin{equation}\label{averageFresnel}
F_{avg} = \frac{1 + 20 \fNormal}{21}
\end{equation}$$

This new lobe is combined with the original single scattering lobe, previously noted $f_r$:

$$\begin{equation}
f_{r}(l,v) = f_{ss}(l,v) + f_{ms}(l,v)
\end{equation}$$

In [#Lagarde18], with credit to Emmanuel Turquin, Lagarde and Golubev make the observation that equation $\ref{averageFresnel}$ can be simplified to $\fNormal$. They also propose to apply energy compensation by adding a scaled GGX specular lobe:

$$\begin{equation}\label{energyCompensation}
f_{ms}(l,v) = \fNormal \frac{1 - E(l)}{E(l)} f_{ss}(l,v)
\end{equation}$$

The key insight is that $E(l)$ can not only be precomputed but also shared with image-based lighting pre-integration. The multiscattering energy compensation formula thus becomes:

$$\begin{equation}\label{scaledEnergyCompensationLobe}
f_r(l,v) = f_{ss}(l,v) + \fNormal \left( \frac{1}{r} - 1 \right) f_{ss}(l,v)
\end{equation}$$

Where $r$ is defined as:

$$\begin{equation}
r = \int_{\Omega} D(l,v) V(l,v) \left< \NoL \right> dl
\end{equation}$$

We can implement specular energy compensation at a negligible cost if we store $r$ in the DFG lookup table presented in section [Image based lights]. Listing [energyCompensationImpl] shows that the implementation is a direct conversion of equation $\ref{scaledEnergyCompensationLobe}$.

```glsl
vec3 energyCompensation = 1.0 + f0 * (1.0 / dfg.y - 1.0);
// Scale the specular lobe to account for multiscattering
Fr *= pixel.energyCompensation;
```
*リスト [energyCompensationImpl]: Implementation of the energy compensation specular lobe*

Please refer to section [Image based lights] and section [Pre-integration for multiscattering] to learn how the DFG lookup table is derived and computed.
