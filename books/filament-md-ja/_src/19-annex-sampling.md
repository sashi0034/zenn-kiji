## Importance sampling for the IBL

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


In the discrete domain, the integral can be approximated with sampling as defined in equation $\ref{iblSampling}$.

$$\begin{equation}\label{iblSampling}
\Lout(n,v,\Theta) \equiv \frac{1}{N} \sum_{i}^{N} f(l_{i}^{uniform},v,\Theta) L_{\perp}(l_i) \left< n \cdot l_i^{uniform} \right>
\end{equation}$$

Unfortunately, we would need too many samples to evaluate this integral. A technique commonly used
is to choose samples that are more "important" more often, this is called _importance sampling_.
In our case we'll use the distribution of micro-facets normals, $D_{ggx}$, as the distribution of
important samples.

The evaluation of $ \Lout(n,v,\Theta) $ with importance sampling is presented in equation $\ref{annexIblImportanceSampling}$.

$$\begin{equation}\label{annexIblImportanceSampling}
\Lout(n,v,\Theta) \equiv \frac{1}{N} \sum_{i}^{N} \frac{f(l_{i},v,\Theta)}{p(l_i,v,\Theta)} L_{\perp}(l_i) \left< n \cdot l_i \right>
\end{equation}$$

In equation $\ref{annexIblImportanceSampling}$, $p$ is the probability density function (PDF) of the
distribution of _important direction samples_ $l_i$. These samples depend on $h_i$, $v$ and $\alpha$.
The definition of the PDF is shown in equation $\ref{iblPDF}$.

$h_i$ is given by the distribution we chose, see section [Choosing important directions] for more details.

The _important direction samples_ $l_i$ are calculated as the reflection of $v$ around $h_i$, and therefore
**do not** have the same PDF as $h_i$. The PDF of a transformed distribution is given by:

$$\begin{equation}
p(T_r(x)) = p(x) |J(T_r)|^{-1}
\end{equation}$$

Where $|J(T_r)|$ is the determinant of the Jacobian of the transform. In our case we're considering
the transform from $h_i$ to $l_i$ and the determinant of its Jacobian is given in \ref{iblPDF}.

$$\begin{equation}\label{iblPDF}
p(l,v,\Theta) = D(h,\alpha) \left< \NoH \right> |J_{h \rightarrow l}|^{-1} \\
|J_{h \rightarrow l}| = 4 \left< \VoH \right>
\end{equation}$$

### Choosing important directions

Refer to section [Choosing important directions for sampling the BRDF] for more details. Given a uniform distribution $(\zeta_{\phi},\zeta_{\theta})$ the important direction $l$ is defined by equation $\ref{importantDirection}$.

$$\begin{equation}\label{importantDirection}
\phi = 2 \pi \zeta_{\phi} \\
\theta = cos^{-1} \sqrt{\frac{1 - \zeta_{\theta}}{(\alpha^2 - 1)\zeta_{\theta}+1}} \\
l = \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
\end{equation}$$

Typically, $ (\zeta_{\phi},\zeta_{\theta}) $ are chosen using the Hammersley uniform distribution algorithm described in section [Hammersley sequence].

### Pre-filtered importance sampling

Importance sampling considers only the PDF to generate important directions; in particular, it is oblivious to the actual content of the IBL. If the latter contains high frequencies in areas without a lot of samples, the integration won’t be accurate. This can be somewhat mitigated by using a technique called _pre-filtered importance sampling_, in addition this allows the integral to converge with many fewer samples.

Pre-filtered importance sampling uses several images of the environment increasingly low-pass filtered. This is typically implemented very efficiently with mipmaps and a box filter. The LOD is selected based on the sample importance, that is, low probability samples use a higher LOD index (more filtered).

This technique is described in details in [#Krivanek08].

The cubemap LOD is determined in the following way:

$$\begin{align*}
lod &= log_4 \left( K\frac{\Omega_s}{\Omega_p} \right) \\
K &= 4.0 \\
\Omega_s &= \frac{1}{N \cdot p(l_i)} \\
\Omega_p &\approx \frac{4\pi}{6 \cdot width \cdot height}
\end{align*}$$

Where $K$ is a constant determined empirically, $p$ the PDF of the BRDF, $ \Omega_{s} $ the solid angle associated to the sample and $\Omega_p$ the solid angle associated with the texel in the cubemap.

Cubemap sampling is done using seamless trilinear filtering. It is extremely important to sample the cubemap correctly across faces using OpenGL's seamless sampling feature or any other technique that avoids/reduces seams.

Table [importanceSamplingViz] shows a comparison between importance sampling and pre-filtered importance sampling when applied to figure [importanceSamplingRef].

![Figure [importanceSamplingRef]: Importance sampling image reference](/images/filament-md-ja/image_is_original.png)

 Samples |      Importance sampling      |    Pre-filtered importance sampling
---------|-------------------------------|---------------------------------------
  4096   | ![](/images/filament-md-ja/image_is_4096.png) | &nbsp;
  1024   | ![](/images/filament-md-ja/image_is_1024.png) | ![](/images/filament-md-ja/image_fis_1024.png)
  32     | ![](/images/filament-md-ja/image_is_32.png)   | ![](/images/filament-md-ja/image_fis_32.png)
*表 [importanceSamplingViz]: Importance sampling vs pre-filtered importance sampling with $\alpha = 0.4$*

The reference renderer used in the comparison below performs no approximation. In particular, it does not assume $v = n$ and does not perform the split sum approximation.  The pre-filtered renderer uses all the techniques discussed in this section: pre-filtered cubemaps, the analytic formulation of the DFG term, and of course the split sum approximation.

Left: reference renderer, right: pre-filtered importance sampling.

![](/images/filament-md-ja/image_is_ref_1.png) ![](/images/filament-md-ja/image_filtered_1.png)
![](/images/filament-md-ja/image_is_ref_2.png) ![](/images/filament-md-ja/image_filtered_2.png)
![](/images/filament-md-ja/image_is_ref_3.png) ![](/images/filament-md-ja/image_filtered_3.png)
![](/images/filament-md-ja/image_is_ref_4.png) ![](/images/filament-md-ja/image_filtered_4.png)

## Choosing important directions for sampling the BRDF

For simplicity we use the $ D $ term of the BRDF as the PDF, however the PDF must be normalized such that the integral over the hemisphere is 1:

$$\begin{equation}
\int_{\Omega}p(m)dm = 1 \\
\int_{\Omega}D(m)(n \cdot m)dm = 1 \\
\int_{\phi=0}^{2\pi}\int_{\theta=0}^{\frac{\pi}{2}}D(\theta,\phi) cos \theta sin \theta d\theta d\phi = 1 \\
\end{equation}$$

The PDF of the BRDF can therefore be expressed as in equation $\ref{importantPDF}$:

$$\begin{equation}\label{importantPDF}
p(\theta,\phi) = \frac{\alpha^2}{\pi(cos^2\theta (\alpha^2-1) + 1)^2} cos\theta sin\theta
\end{equation}$$

The term $sin\theta$ comes from the differential solid angle $sin\theta d\phi d\theta$ since we integrate over a sphere. We sample $\theta$ and $\phi$ independently:

$$\begin{align*}
p(\theta) &= \int_0^{2\pi} p(\theta,\phi) d\phi = \frac{2\alpha^2}{(cos^2\theta (\alpha^2-1) + 1)^2} cos\theta sin\theta \\
p(\phi) &= \frac{p(\theta,\phi)}{p(\phi)} = \frac{1}{2\pi}
\end{align*}$$

The expression of $ p(\phi) $ is true for an isotropic distribution of normals.

We then calculate the cumulative distribution function (CDF) for each variable:

$$\begin{align*}
P(s_{\phi}) &= \int_{0}^{s_{\phi}} p(\phi) d\phi = \frac{s_{\phi}}{2\pi} \\
P(s_{\theta}) &= \int_{0}^{s_{\theta}} p(\theta) d\theta = 2 \alpha^2 \left( \frac{1}{(2\alpha^4-4\alpha^2+2) cos(s_{\theta})^2 + 2\alpha^2 - 2} - \frac{1}{2\alpha^4-2\alpha^2} \right)
\end{align*}$$

We set $ P(s_{\phi}) $ and $ P(s_{\theta}) $ to random variables $ \zeta_{\phi} $ and $ \zeta_{\theta} $ and solve for $ s_{\phi} $ and $ s_{\theta} $ respectively:

$$\begin{align*}
P(s_{\phi}) &= \zeta_{\phi} \rightarrow s_{\phi} = 2\pi\zeta_{\phi} \\
P(s_{\theta}) &= \zeta_{\theta} \rightarrow s_{\theta} = cos^{-1} \sqrt{\frac{1-\zeta_{\theta}}{(\alpha^2-1)\zeta_{\theta}+1}}
\end{align*}$$

So given a uniform distribution $ (\zeta_{\phi},\zeta_{\theta}) $, our important direction $l$ is defined as:

$$\begin{align*}
\phi &= 2\pi\zeta_{\phi} \\
\theta &= cos^{-1} \sqrt{\frac{1-\zeta_{\theta}}{(\alpha^2-1)\zeta_{\theta}+1}} \\
l &= \{ cos\phi sin\theta,sin\phi sin\theta,cos\theta \}
\end{align*}$$

## Hammersley sequence

```glsl
vec2f hammersley(uint i, float numSamples) {
    uint bits = i;
    bits = (bits << 16) | (bits >> 16);
    bits = ((bits & 0x55555555) << 1) | ((bits & 0xAAAAAAAA) >> 1);
    bits = ((bits & 0x33333333) << 2) | ((bits & 0xCCCCCCCC) >> 2);
    bits = ((bits & 0x0F0F0F0F) << 4) | ((bits & 0xF0F0F0F0) >> 4);
    bits = ((bits & 0x00FF00FF) << 8) | ((bits & 0xFF00FF00) >> 8);
    return vec2f(i / numSamples, bits / exp2(32));
}
```
[C++ implementation of a Hammersley sequence generator]

## Precomputing L for image-based lighting

The term $ L_{DFG} $ is only dependent on $ \NoV $. Below, the normal is arbitrarily set to $ n=\left[0, 0, 1\right] $ and $v$ is chosen to satisfy $ \NoV $. The vector $ h_i $ is the $ D_{GGX}(\alpha) $ important direction sample $i$.

```glsl
float GDFG(float NoV, float NoL, float a) {
    float a2 = a * a;
    float GGXL = NoV * sqrt((-NoL * a2 + NoL) * NoL + a2);
    float GGXV = NoL * sqrt((-NoV * a2 + NoV) * NoV + a2);
    return (2 * NoL) / (GGXV + GGXL);
}

float2 DFG(float NoV, float a) {
    float3 V;
    V.x = sqrt(1.0f - NoV*NoV);
    V.y = 0.0f;
    V.z = NoV;

    float2 r = 0.0f;
    for (uint i = 0; i < sampleCount; i++) {
        float2 Xi = hammersley(i, sampleCount);
        float3 H = importanceSampleGGX(Xi, a, N);
        float3 L = 2.0f * dot(V, H) * H - V;

        float VoH = saturate(dot(V, H));
        float NoL = saturate(L.z);
        float NoH = saturate(H.z);

        if (NoL > 0.0f) {
            float G = GDFG(NoV, NoL, a);
            float Gv = G * VoH / NoH;
            float Fc = pow(1 - VoH, 5.0f);
            r.x += Gv * (1 - Fc);
            r.y += Gv * Fc;
        }
    }
    return r * (1.0f / sampleCount);
}
```
[C++ implementation of the $ L_{DFG} $ term]
