## Parameterization

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


Disney's material model described in [#Burley12] is a good starting point but its numerous parameters makes it impractical for real-time implementations. In addition, we would like our standard material model to be easy to understand and easy to use for both artists and developers.

### Standard parameters

Table [standardParameters] describes the list of parameters that satisfy our constraints.

       Parameter      |      Definition
---------------------:|:---------------------
**BaseColor**         | Diffuse albedo for non-metallic surfaces, and specular color for metallic surfaces
**Metallic**          | Whether a surface appears to be dielectric (0.0) or conductor (1.0). Often used as a binary value (0 or 1)
**Roughness**         | Perceived smoothness (0.0) or roughness (1.0) of a surface. Smooth surfaces exhibit sharp reflections
**Reflectance**       | Fresnel reflectance at normal incidence for dielectric surfaces. This replaces an explicit index of refraction
**Emissive**          | Additional diffuse albedo to simulate emissive surfaces (such as neons, etc.) This parameter is mostly useful in an HDR pipeline with a bloom pass
**Ambient occlusion** | Defines how much of the ambient light is accessible to a surface point. It is a per-pixel shadowing factor between 0.0 and 1.0. This parameter will be discussed in more details in the lighting section
*表 [standardParameters]: Parameters of the standard model*

Figure [material_parameters] shows how the metallic, roughness and reflectance parameters affect the appearance of a surface.

![Figure [material_parameters]: From top to bottom: varying metallic, varying dielectric roughness, varying metallic roughness, varying reflectance](/images/filament-md-ja/material_parameters.png)

### Types and ranges

It is important to understand the type and range of the different parameters of our material model, described in table [standardParametersTypes].

       Parameter      |    Type and range
---------------------:|:---------------------
**BaseColor**         | Linear RGB [0..1]
**Metallic**          | Scalar [0..1]
**Roughness**         | Scalar [0..1]
**Reflectance**       | Scalar [0..1]
**Emissive**          | Linear RGB [0..1] + exposure compensation
**Ambient occlusion** | Scalar [0..1]
*表 [standardParametersTypes]: Range and type of the standard model's parameters*

Note that the types and ranges described here are what the shader will expect. The API and/or tools UI could and should allow to specify the parameters using other types and ranges when they are more intuitive for artists.

For instance, the base color could be expressed in sRGB space and converted to linear space before being sent off to the shader. It can also be useful for artists to express the metallic, roughness and reflectance parameters as gray values between 0 and 255 (black to white).

Another example: the emissive parameter could be expressed as a color temperature and an intensity, to simulate the light emitted by a black body.

### Remapping

To make the standard material model easier and more intuitive to use for artists, we must remap the parameters _baseColor_, _roughness_ and _reflectance_.

#### Base color remapping

The base color of a material is affected by the "metallicness" of said material. Dielectrics have achromatic specular reflectance but retain their base color as the diffuse color. Conductors on the other hand use their base color as the specular color and do not have a diffuse component.

The lighting equations must therefore use the diffuse color and $\fNormal$ instead of the base color. The diffuse color can easily be computed from the base color, as show in listing [baseColorToDiffuse].

```glsl
vec3 diffuseColor = (1.0 - metallic) * baseColor.rgb;
```
*リスト [baseColorToDiffuse]: Conversion of base color to diffuse in GLSL*

#### Reflectance remapping

**Dielectrics**

The Fresnel term relies on $\fNormal$, the specular reflectance at normal incidence angle, and is achromatic for dielectrics. We will use the remapping for dielectric surfaces described in [#Lagarde14] :

$$\begin{equation}
\fNormal = 0.16 \cdot reflectance^2
\end{equation}$$

The goal is to map $\fNormal$ onto a range that can represent the Fresnel values of both common dielectric surfaces (4% reflectance) and gemstones (8% to 16%). The mapping function is chosen to yield a 4% Fresnel reflectance value for an input reflectance of 0.5 (or 128 on a linear RGB gray scale). Figure [reflectance] show those common values and how they relate to the mapping function.

![Figure [reflectance]: Common reflectance values](/images/filament-md-ja/diagram_reflectance.png)

If the index of refraction is known (for instance, an air-water interface has an IOR of 1.33), the Fresnel reflectance can be calculated as follows:

$$\begin{equation}\label{fresnelEquation}
\fNormal(n_{ior}) = \frac{(\nior - 1)^2}{(\nior + 1)^2}
\end{equation}$$

And if the reflectance value is known, we can compute the corresponding IOR:

$$\begin{equation}
n_{ior} = \frac{2}{1 - \sqrt{\fNormal}} - 1 
\end{equation}$$

Table [commonMatReflectance] describes acceptable Fresnel reflectance values for various types of materials (no real world material has a value under 2%).

          Material         |    Reflectance   |        IOR       |   Linear value
--------------------------:|:-----------------|:-----------------|:----------------
Water                      | 2%               | 1.33             | 0.35
Fabric                     | 4% to 5.6%       | 1.5 to 1.62      | 0.5 to 0.59
Common liquids             | 2% to 4%         | 1.33 to 1.5      | 0.35 to 0.5
Common gemstones           | 5% to 16%        | 1.58 to 2.33     | 0.56 to 1.0
Plastics, glass            | 4% to 5%         | 1.5 to 1.58      | 0.5 to 0.56
Other dielectric materials | 2% to 5%         | 1.33 to 1.58     | 0.35 to 0.56
Eyes                       | 2.5%             | 1.38             | 0.39
Skin                       | 2.8%             | 1.4              | 0.42
Hair                       | 4.6%             | 1.55             | 0.54
Teeth                      | 5.8%             | 1.63             | 0.6
Default value              | 4%               | 1.5              | 0.5
*表 [commonMatReflectance]: Reflectance of common materials (source: Real-Time Rendering 4th Edition)*

Table [fNormalMetals] lists the $\fNormal$ values for a few metals. The values are given in sRGB and must be used as the base color in our material model. Please refer to the annex, section [Specular color], for an explanation of how these sRGB colors are computed from measured data.

    Metal  | $\fNormal$ in sRGB  |  Hexadecimal |               Color
----------:|:-------------------:|:------------:|-------------------------------------------------------
Silver     | 0.97, 0.96, 0.91    | #f7f4e8     | 
Aluminum   | 0.91, 0.92, 0.92    | #e8eaea     | 
Titanium   | 0.76, 0.73, 0.69    | #c1baaf     | 
Iron       | 0.77, 0.78, 0.78    | #c4c6c6     | 
Platinum   | 0.83, 0.81, 0.78    | #d3cec6     | 
Gold       | 1.00, 0.85, 0.57    | #ffd891     | 
Brass      | 0.98, 0.90, 0.59    | #f9e596     | 
Copper     | 0.97, 0.74, 0.62    | #f7bc9e     | 
*表 [fNormalMetals]: $\fNormal$ for common metals*

All materials have a Fresnel reflectance of 100% at grazing angles so we will set $\fGrazing$ in the following way when evaluating the specular BRDF $\fSpecular$:

$$\begin{equation}
\fGrazing = 1.0
\end{equation}$$

Figure [grazing_reflectance] shows a red plastic ball. If you look closely at the edges of the sphere, you will be able to notice the achromatic specular reflectance at grazing angles.

![Figure [grazing_reflectance]: The specular reflectance becomes achromatic at grazing angles](/images/filament-md-ja/material_grazing_reflectance.png)

**Conductors**

The specular reflectance of metallic surfaces is chromatic:

$$\begin{equation}
\fNormal = baseColor \cdot metallic
\end{equation}$$

Listing [fNormal] shows how $\fNormal$ is computed for both dielectric and metallic materials. It shows that the color of the specular reflectance is derived from the base color in the metallic case.

```glsl
vec3 f0 = 0.16 * reflectance * reflectance * (1.0 - metallic) + baseColor * metallic;
```
*リスト [fNormal]: Computing $\fNormal$ for dielectric and metallic materials in GLSL*

#### Roughness remapping and clamping

The roughness set by the user, called `perceptualRoughness` here, is remapped to a perceptually linear range using the following formulation:

$$\begin{equation}
\alpha = perceptualRoughness^2
\end{equation}$$

Figure [roughness_remap] shows a silver metallic surface with increasing roughness (from 0.0 to 1.0), using the unmodified roughness value (bottom) and the remapped value (top).

![Figure [roughness_remap]: Roughness remapping comparison: perceptually linear roughness (top) and roughness (bottom)](/images/filament-md-ja/material_roughness_remap.png)

Using this visual comparison, it is obvious that the remapped roughness is easier to understand by artists and developers. Without this remapping, shiny metallic surfaces would have to be confined to a very small range between 0.0 and 0.05.

Brent Burley made similar observations in his presentation [#Burley12]. After experimenting with other remappings (cubic and quadratic mappings for instance), we have reached the conclusion that this simple square remapping delivers visually pleasing and intuitive results while being cheap for real-time applications.

Last but not least, it is important to note that the roughness parameters is used in various computations at runtime where limited floating point precision can become an issue. For instance, _mediump_ precision floats are often implemented as half-floats (fp16) on mobile GPUs.

This cause problems when computing small values like $\frac{1}{perceptualRoughness^4}$ in our lighting equations (roughness squared in the GGX computation). The smallest value that can be represented as a half-float is $2^{-14}$ or $6.1 \times 10^{-5}$. To avoid divisions by 0 on devices that do not support denormals, the result of $\frac{1}{roughness^4}$ must therefore not be lower than $6.1 \times 10^{-5}$. To do so, we must clamp the roughness to 0.089, which gives us $6.274 \times 10^{-5}$. 

Denormals should also be avoided to prevent performance drops. The roughness can also not be set to 0 to avoid obvious divisions by 0.

Since we also want specular highlights to have a minimum size (a roughness close to 0 creates almost invisible highlights), we should clamp the roughness to a safe range in the shader. This clamping has the added benefit of correcting specular aliasing[^frostbiteRoughnessClamp] that can appear for low roughness values.

[^frostbiteRoughnessClamp]: The Frostbite engine clamps the roughness of analytical lights to 0.045 to reduce specular aliasing. This is possible when using single precision floats (fp32).

### Blending and layering

As noted in [#Burley12] and [#Neubelt13], this model allows for robust blending between different materials by simply interpolating the different parameters. In particular, this allows to layer different materials using simple masks.

For instance, figure [materialBlending] shows how the studio Ready at Dawn used material blending and layering in _The Order: 1886_ to create complex appearances from a library of simple materials (gold, copper, wood, rust, etc.).

![Figure [materialBlending]: Material blending and layering. Source: Ready at Dawn Studios](/images/filament-md-ja/material_blending.png)

The blending and layering of materials is effectively an interpolation of the various parameters of the material model. Figure [material_interpolation] show an interpolation between shiny metallic chrome and rough red plastic. While the intermediate blended materials make little physical sense, they look plausible.

![Figure [material_interpolation]: Interpolation from shiny chrome (left) to rough red plastic (right)](/images/filament-md-ja/material_interpolation.png)

### Crafting physically based materials

Designing physically based materials is fairly easy once you understand the nature of the four main parameters: base color, metallic, roughness and reflectance.

We provide a [useful chart/reference guide](./Material%20Properties.pdf) to help artists and developers craft their own physically based materials.

![Crafting physically based materials](/images/filament-md-ja/material_chart.jpg)

In addition, here is a quick summary of how to use our material model:

**All materials**

**Base color** should be devoid of lighting information, except for micro-occlusion.

    **Metallic** is almost a binary value. Pure conductors have a metallic value of 1 and pure dielectrics have a metallic value of 0. You should try to use values close at or close to 0 and 1. Intermediate values are meant for transitions between surface types (metal to rust for instance).

**Non-metallic materials**

**Base color** represents the reflected color and should be an sRGB value in the range 50-240 (strict range) or 30-240 (tolerant range).

    **Metallic** should be 0 or close to 0.

    **Reflectance** should be set to 127 sRGB (0.5 linear, 4% reflectance) if you cannot find a proper value. Do not use values under 90 sRGB (0.35 linear, 2% reflectance).

**Metallic materials**

**Base color** represents both the specular color and reflectance. Use values with a luminosity of 67% to 100% (170-255 sRGB). Oxidized or dirty metals should use a lower luminosity than clean metals to take into account the non-metallic components.

    **Metallic** should be 1 or close to 1.

    **Reflectance** is ignored (calculated from the base color).
