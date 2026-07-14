## Direct lighting

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


We have defined the light units for all the light types supported by the renderer in the section above but we have not defined the light unit for the result of the lighting equations. Choosing physical light units means that we will compute luminance values in our shaders, and therefore that all our light evaluation functions will compute the luminance $L_{out}$ (or outgoing radiance) at any given point. The luminance depends on the illuminance $E$ and the BSDF $f(v,l)$ :

$$\begin{equation}\label{luminanceEquation}
L_{out} = f(v,l)E
\end{equation}$$

### Directional lights

The main purpose of directional lights is to recreate important light sources for outdoor environment, i.e. the sun and/or the moon. While directional lights do not truly exist in the physical world, any light source sufficiently far from the light receptor can be assumed to be directional (i.e. all the incident light rays are parallel, as shown in  figure [directionalLight]).

![Figure [directionalLight]: Interaction between a directional light and a surface. The light source is a virtual construct that can only be represented by a direction](/images/filament-md-ja/diagram_directional_light.png)

This approximation proves to work incredibly well for the diffuse response of a surface but the specular response is incorrect. The Frostbite engine solves this problem by treating the "sun" directional light as a disc area light. However, our tests have shown that the quality increase does not justify the added computational costs.

We earlier stated that we chose an illuminance light unit ($lx$) for directional lights. This is in part due to the fact that we can easily find illuminance values for the sky and the sun (online or with a light meter) but also to simplify the luminance equation described in $\ref{luminanceEquation}$.

$$\begin{equation}\label{directionalLuminanceEquation}
L_{out} = f(v,l) E_{\bot} \left< \NoL \right>
\end{equation}$$

In the simplified luminance equation $\ref{directionalLuminanceEquation}$, $E_{\bot}$ is the illuminance of the light source for a surface perpendicular to said light source. If the directional light source simulates the sun, $E_{\bot}$ is the illuminance of the sun for a surface perpendicular to the sun direction.

Table [sunSkyIlluminance] provides useful reference values for the sun and sky illumination, measured[^illuminanceMeasures] on a clear day in March, in California.

          Light            |   10am   |   12pm   |  5:30pm  
--------------------------:|---------:|---------:|---------:
$Sky_{\bot} + Sun_{\bot}$  | 120,000  | 130,000  | 90,000  
$Sky_{\bot}$               | 20,000   | 25,000   | 9,000   
$Sun_{\bot}$               | 100,000  | 105,000  | 81,000  
*表 [sunSkyIlluminance]: Illuminance values in $lx$ (a full moon has an illuminance of 1 $lx$)*

Dynamic directional lights are particularly cheap to evaluate at runtime, as shown in listing [glslDirectionalLight].

```glsl
vec3 l = normalize(-lightDirection);
float NoL = clamp(dot(n, l), 0.0, 1.0);

// lightIntensity is the illuminance
// at perpendicular incidence in lux
float illuminance = lightIntensity * NoL;
vec3 luminance = BSDF(v, l) * illuminance;
```
*リスト [glslDirectionalLight]: Implementation of directional lights in GLSL*

Figure [directionalLightTest] shows the effect of lighting a simple scene with a directional light setup to approximate a midday Sun (illuminance set to 110,000 $lx$). For illustration purposes, only direct lighting is shown.

![Figure [directionalLightTest]: Series of dielectric materials of varying roughness under a directional light](/images/filament-md-ja/screenshot_directional_light.png)

[^illuminanceMeasures]: Measurements taken with an incident light meter (Sekonic L-478D)

### Punctual lights

Our engine will support two types of punctual lights, commonly found in most if not all rendering engines: point lights and spot lights. These types of lights are traditionally physically inaccurate for two reasons:

1. They are truly punctual and infinitesimally small.
2. They do not follow the [inverse square law](http://en.wikipedia.org/wiki/Inverse-square_law).

The first issue can be addressed with area lights but, given the cheaper nature of punctual lights it is deemed practical to use infinitesimally small punctual lights whenever possible.

The second issue is easy to fix. For a given punctual light, the perceived intensity decreases proportionally to the square of the distance from the viewer (more precisely, the light receptor).

For punctual lights following the inverse square law, the term $E$ of equation $ \ref{luminanceEquation} $ is expressed in equation $\ref{punctualLightEquation}$, where $d$ is the distance from a point at the surface to the light.

$$\begin{equation}\label{punctualLightEquation}
E = L_{in} \left< \NoL \right> = \frac{I}{d^2} \left< \NoL \right>
\end{equation}$$

The difference between point and spot lights lies in how $E$ is computed, and in particular how the luminous intensity $I$ is computed from the luminous power $\Phi$.

#### Point lights

A point light is defined only by a position in space, as shown in figure [pointLight].

![Figure [pointLight]: Interaction between a point light and a surface. The attenuation only depends on the distance to the light](/images/filament-md-ja/diagram_point_light.png)

The luminous power of a point light is calculated by integrating the luminous intensity over the light's solid angle, as show in equation $\ref{pointLightLuminousPower}$. The luminous intensity can then be easily derived from the luminous power.

$$\begin{equation}\label{pointLightLuminousPower}
\Phi = \int_{\Omega} I dl = \int_{0}^{2\pi} \int_{0}^{\pi} I d\theta d\phi = 4 \pi I \\
I = \frac{\Phi}{4 \pi}
\end{equation}$$

By simple substitution of $I$ in $\ref{punctualLightEquation}$ and $E$ in $ \ref{luminanceEquation} $ we can formulate the luminance equation of a point light as a function of the luminous power (see $ \ref{pointLightLuminanceEquation} $).

$$\begin{equation}\label{pointLightLuminanceEquation}
L_{out} = f(v,l) \frac{\Phi}{4 \pi d^2} \left< \NoL \right>
\end{equation}$$

Figure [pointLightTest] shows the effect of lighting a simple scene with a point light subject to distance attenuation. Light falloff is exaggerated for illustration purposes.

![Figure [pointLightTest]: Inverse square law applied to point lights evaluation](/images/filament-md-ja/screenshot_point_light.png)

#### Spot lights

A spot light is defined by a position in space, a direction vector and two cone angles, $ \theta_{inner} $ and $ \theta_{outer} $ (see figure [spotLight]). These two angles are used to define the angular falloff attenuation of the spot light. The light evaluation function of a spot light must therefore take into account both the inverse square law and these two angles to properly evaluate the luminance attenuation.

![Figure [spotLight]: Interaction between a spot light and a surface. The attenuation depends on the distance to the light and the angle between the surface the spot light's direction vector](/images/filament-md-ja/diagram_spot_light.png)

Equation $ \ref{spotLightLuminousPower} $ describes how the luminous power of a spot light can be calculated in a similar fashion to point lights, using $ \theta_{outer} $ the outer angle of the spot light's cone in the range [0..$\pi$].

$$\begin{equation}\label{spotLightLuminousPower}
\Phi = \int_{\Omega} I dl = \int_{0}^{2\pi} \int_{0}^{\theta_{outer}} I d\theta d\phi = 2 \pi (1 - cos\frac{\theta_{outer}}{2})I \\
I = \frac{\Phi}{2 \pi (1 - cos\frac{\theta_{outer}}{2})}
\end{equation}$$

While this formulation is physically correct, it makes spot lights a little difficult to use: changing the outer angle of the cone changes the illumination levels. Figure [spotLightTestFocused] shows the same scene lit by a spot light, with an outer angle of 55 degrees and an outer angle of 15 degrees. Observes how the illumination level increases as the cone aperture decreases.

![Figure [spotLightTestFocused]: Comparison of spot light outer angles, 55 degrees (left) and 15 degrees (right)](/images/filament-md-ja/screenshot_spot_light_focused.png)

The coupling of illumination and the outer cone means that an artist cannot tweak the influence cone of a spot light without also changing the perceived illumination. It therefore makes sense to provide artists with a parameter to disable this coupling. Equations $ \ref{spotLightLuminousPowerB} $ shows how to formulate the luminous power for that purpose.

$$\begin{equation}\label{spotLightLuminousPowerB}
\Phi = \pi I \\
I = \frac{\Phi}{\pi} \\
\end{equation}$$

With this new formulation to compute the luminous intensity, the test scene in figure [spotLightTest] exhibits similar illumination levels with both cone apertures.

![Figure [spotLightTest]: Comparison of spot light outer angles, 55 degrees (left) and 15 degrees (right)](/images/filament-md-ja/screenshot_spot_light.png)

This new formulation can also be considered physically based if the spot's reflector is replaced with a matte, diffuse mask that absorbs light perfectly.

The spot light evaluation function can be expressed in two ways:

- **With a light absorber**
  $$\begin{equation}\label{spotAbsorber}
  L_{out} = f(v,l) \frac{\Phi}{\pi d^2} \left< \NoL \right> \lambda(l)
  \end{equation}$$
- **With a light reflector**
  $$\begin{equation}\label{spotReflector}
  L_{out} = f(v,l) \frac{\Phi}{2 \pi (1 - cos\frac{\theta_{outer}}{2}) d^2} \left< \NoL \right> \lambda(l)
  \end{equation}$$

The term $ \lambda(l) $ in equations $ \ref{spotAbsorber} $ and $ \ref{spotReflector} $ is the spot's angle attenuation factor described in equation
 $ \ref{spotAngleAtt} $ below.

$$\begin{equation}\label{spotAngleAtt}
\lambda(l) = \frac{l \cdot spotDirection - cos\theta_{outer}}{cos\theta_{inner} - cos\theta_{outer}}
\end{equation}$$

#### Attenuation function

A proper evaluation of the inverse square law attenuation factor is mandatory for physically based punctual lights. The simple mathematical formulation is unfortunately impractical for implementation purposes:

1. The division by the squared distance can lead to divides by 0 when objects intersect or "touch" light sources.

2. The influence sphere of each light is infinite ($ \frac{I}{d^2} $ is asymptotic, it never reaches 0) which means that to correctly shade a pixel we need to evaluate every light in the world.

The first issue can be solved easily by setting the assumption that punctual lights are not truly punctual but instead small area lights. To do this we can simply treat punctual lights as spheres of 1 cm radius, as show in equation $\ref{finitePunctualLight}$.

$$\begin{equation}\label{finitePunctualLight}
E = \frac{I}{max(d^2, {0.01}^2)}
\end{equation}$$

We can solve the second issue by introducing an influence radius for each light. There are several advantages to this solution. Tools can quickly show artists what parts of the world will be influenced by every light (the tool just needs to draw a sphere centered on each light). The rendering engine can cull lights more aggressively using this extra piece of information and artists/developers can assist the engine by manually tweaking the influence radius of a light.

Mathematically, the illuminance of a light should smoothly reach zero at the limit defined by the influence radius. [#Karis13b] proposes to window the inverse square function in such a way that the majority of the light's influence remains unaffected. The proposed windowing is described in equation $\ref{attenuationWindowing}$, where $r$ is the light's radius of influence.

$$\begin{equation}\label{attenuationWindowing}
E = \frac{I}{max(d^2, {0.01}^2)} \left< 1 - \frac{d^4}{r^4} \right>^2
\end{equation}$$

Listing [glslPunctualLight] demonstrates how to implement physically based punctual lights in GLSL. Note that the light intensity used in this piece of code is the luminous intensity $I$ in $cd$, converted from the luminous power  CPU-side. This snippet is not optimized and some of the computations can be offloaded to the CPU (for instance the square of the light's inverse falloff radius, or the spot scale and angle).

```glsl
float getSquareFalloffAttenuation(vec3 posToLight, float lightInvRadius) {
    float distanceSquare = dot(posToLight, posToLight);
    float factor = distanceSquare * lightInvRadius * lightInvRadius;
    float smoothFactor = max(1.0 - factor * factor, 0.0);
    return (smoothFactor * smoothFactor) / max(distanceSquare, 1e-4);
}

float getSpotAngleAttenuation(vec3 l, vec3 lightDir,
        float innerAngle, float outerAngle) {
    // the scale and offset computations can be done CPU-side
    float cosOuter = cos(outerAngle);
    float spotScale = 1.0 / max(cos(innerAngle) - cosOuter, 1e-4)
    float spotOffset = -cosOuter * spotScale

    float cd = dot(normalize(-lightDir), l);
    float attenuation = clamp(cd * spotScale + spotOffset, 0.0, 1.0);
    return attenuation * attenuation;
}

vec3 evaluatePunctualLight() {
    vec3 l = normalize(posToLight);
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    vec3 posToLight = lightPosition - worldPosition;

    float attenuation;
    attenuation  = getSquareFalloffAttenuation(posToLight, lightInvRadius);
    attenuation *= getSpotAngleAttenuation(l, lightDir, innerAngle, outerAngle);

    vec3 luminance = (BSDF(v, l) * lightIntensity * attenuation * NoL) * lightColor;
    return luminance;
}
```
*リスト [glslPunctualLight]: Implementation of punctual lights in GLSL*

### Photometric lights

Punctual lights are an extremely practical and efficient way to light a scene but do not give artists enough control over the light distribution. The field of architectural lighting design concerns itself with designing lighting systems to serve humans needs by taking into account:

- The amount of light provided
- The color of the light
- The distribution of light within the space

The lighting system we have described so far can easily address the first two points but we need a way to define the distribution of light within the space. Light distribution is especially important for indoor scenes or for some types of outdoor scenes or even road lighting. Figure [lightDistributionTest] shows scenes where the light distribution is controlled by the artist. This type of distribution control is widely used when putting objects on display (museums, stores or galleries for instance).

![Figure [lightDistributionTest]: Controlling the distribution of a point light](/images/filament-md-ja/screenshot_photometric_lights.png)

Photometric lights use a photometric profile to describe their intensity distribution. There are two commonly used formats, IES (Illuminating Engineering Society) and EULUMDAT (European Lumen Data format) but we will focus on the former. IES profiles are supported by many tools and engines, such as Unreal Engine 4, Frostbite, Renderman, Maya and Killzone. In addition, IES light profiles are commonly made available by bulbs and luminaires manufacturers (Philips offers [an extensive array of IES files](http://www.usa.lighting.philips.com/connect/tools_literature/photometric_data_1.wpd) for download for instance). Photometric profiles are particularly useful when they measure a luminaire or light fixture, in which the light source is partially covered. The luminaire will block the light emitted in certain directions, thus shaping the light distribution.

![Example of a real world luminaires that can be described by photometric profiles](/images/filament-md-ja/photo_photometric_lights.jpg)

An IES profile stores luminous intensity for various angles on a sphere around the measured light source. This spherical coordinate system is usually referred to as the photometric web, which can be visualized using specialized tools such as [IESviewer](http://www.photometricviewer.com/). Figure [xarrow] below shows the photometric web of the XArrow IES profile [provided by Pixar](http://renderman.pixar.com/view/DP25764) for use with Renderman. This picture also shows a rendering in 3D space of the XArrow IES profile by our tool `lightgen`.

![Figure [xarrow]: The XArrow IES profile rendered as a photometric web and as a point light in 3D space](/images/filament-md-ja/screenshot_xarrow.png)

The IES format is poorly documented and it is not uncommon to find syntax variations between files found on the Internet. The best resource to understand IES profile is Ian Ashdown's "Parsing the IESNA LM-63 photometric data file" document [#Ashdown98]. Succinctly, an IES profiles stores luminous intensities in candela at various angles around the light source. For each measured horizontal angle, a series of luminous intensities at different vertical angles is provided. It is however fairly common for measured light sources to be horizontally symmetrical. The XArrow profile shown above is a good example: intensities vary with vertical angles (vertical axis) but are symmetrical on the horizontal axis. The range of vertical angles in an IES profile is 0 to 180 degrees and the range of horizontal angles is 0 to 360 degrees.

Figure [lightenSamples] shows the series of IES profiles provided by Pixar for Renderman, rendered using our `lightgen` tool.

![Figure [lightenSamples]: Series of IES light profiles rendered with lightgen](/images/filament-md-ja/screenshot_lightgen_samples.png)

IES profiles can be applied directly to any punctual light, point or spot. To do so, we must first process the IES profile and generate a photometric profile as a texture. For performance considerations, the photometric profile we generate is a 1D texture that represents the average luminous intensity for all horizontal angles at a specific vertical angle (i.e., each pixel represents a vertical angle). To truly represent a photometric light, we should use a 2D texture but since most lights are fully, or mostly, symmetrical on the horizontal plane, we can accept this approximation. The values stored in the texture are normalized by the inverse maximum intensity defined in the IES profile. This allows us to easily store the texture in any float format or, at the cost of a bit of precision, in a luminance 8-bit texture (grayscale PNG for instance). Storing normalized values also allows us to treat photometric profiles as a mask:

**Photometric profile as a mask**

The luminous intensity is defined by the artist by setting the luminous power of the light, as with any other punctual light. The artist defined intensity is divided by the intensity of the light computed from the IES profile. IES profiles contain a luminous intensity but it is only valid for a bare light bulb whereas the measured intensity values take into account the light fixture. To measure the intensity of the luminaire, instead of the bulb, we perform a Monte-Carlo integration of the unit sphere using the intensities from the profile[^xarrowIntensity].

**Photometric profile**

The luminous intensity comes from the profile itself. All the values sampled from the 1D texture are simply multiplied by the maximum intensity. We also provide a multiplier for convenience.

The photometric profile can be applied at rendering time as a simple attenuation. The luminance equation $ \ref{photometricLightEvaluation} $ describes the photometric point light evaluation function.

$$\begin{equation}\label{photometricLightEvaluation}
L_{out} = f(v,l) \frac{I}{d^2} \left< \NoL \right> \Psi(l)
\end{equation}$$

The term $ \Psi(l) $ is the photometric attenuation function. It depends on the light vector, but also on the direction of the light. Spot lights already possess a direction vector but we need to introduce one for photometric point lights as well.

The photometric attenuation function can be easily implemented in GLSL by adding a new attenuation factor to the implementation of punctual lights (listing [glslPunctualLight]). The modified implementation is show in listing [glslPhotometricPunctualLight].

```glsl
float getPhotometricAttenuation(vec3 posToLight, vec3 lightDir) {
    float cosTheta = dot(-posToLight, lightDir);
    float angle = acos(cosTheta) * (1.0 / PI);
    return texture2DLodEXT(lightProfileMap, vec2(angle, 0.0), 0.0).r;
}

vec3 evaluatePunctualLight() {
    vec3 l = normalize(posToLight);
    float NoL = clamp(dot(n, l), 0.0, 1.0);
    vec3 posToLight = lightPosition - worldPosition;

    float attenuation;
    attenuation  = getSquareFalloffAttenuation(posToLight, lightInvRadius);
    attenuation *= getSpotAngleAttenuation(l, lightDirection, innerAngle, outerAngle);
    attenuation *= getPhotometricAttenuation(l, lightDirection);

    float luminance = (BSDF(v, l) * lightIntensity * attenuation * NoL) * lightColor;
    return luminance;
}
```
*リスト [glslPhotometricPunctualLight]: Implementation of attenuation from photometric profiles in GLSL*

The light intensity is computed CPU-side (listing [photometricLightIntensity]) and depends on whether the photometric profile is used as a mask.

```glsl
float multiplier;
// Photometric profile used as a mask
if (photometricLight.isMasked()) {
    // The desired intensity is set by the artist
    // The integrated intensity comes from a Monte-Carlo
    // integration over the unit sphere around the luminaire
    multiplier = photometricLight.getDesiredIntensity() /
            photometricLight.getIntegratedIntensity();
} else {
    // Multiplier provided for convenience, set to 1.0 by default
    multiplier = photometricLight.getMultiplier();
}

// The max intensity in cd comes from the IES profile
float lightIntensity = photometricLight.getMaxIntensity() * multiplier;
```
*リスト [photometricLightIntensity]: Computing the intensity of a photometric light on the CPU*

[^xarrowIntensity]: The XArrow profile declares a luminous intensity of 1,750 lm but a Monte-Carlo integration shows an intensity of only 350 lm.

### Area lights

[TODO]

### Lights parameterization

Similarly to the parameterization of the standard material model, our goal is to make lights parameterization intuitive and easy to use for artists and developers alike. In that spirit, we decided to separate the light color (or hue) from the light intensity. A light color will therefore be defined as a linear RGB color (or sRGB in the tools UI for convenience).

The full list of light parameters is presented in table [lightParameters].

          Parameter        |      Definition
--------------------------:|:---------------------
**Type**                   | Directional, point, spot or area
**Direction**              | Used for directional lights, spot lights, photometric point lights, and linear and tubular area lights (orientation)
**Color**                  | The color of emitted light, as a linear RGB color. Can be specified as an sRGB color or a color temperature in the tools
**Intensity**              | The light's brightness. The unit depends on the type of light
**Falloff radius**         | Maximum distance of influence
**Inner angle**            | Angle of the inner cone for spot lights, in degrees
**Outer angle**            | Angle of the outer cone for spot lights, in degrees
**Length**                 | Length of the area light, used to create linear or tubular lights
**Radius**                 | Radius of the area light, used to create spherical or tubular lights
**Photometric profile**    | Texture representing a photometric light profile, works only for punctual lights
**Masked profile**         | Boolean indicating whether the IES profile is used as a mask or not. When used as a mask, the light's brightness will be multiplied by the ratio between the user specified intensity and the integrated IES profile intensity. When not used as a mask, the user specified intensity is ignored but the IES multiplier is used instead
**Photometric multiplier** | Brightness multiplier for photometric lights (if IES as mask is turned off)
*表 [lightParameters]: Light types parameters*

**Note**: to simplify the implementation, all luminous powers will converted to luminous intensities ($cd$) before being sent to the shader. The conversion is light dependent and is explained in the previous sections.

**Note**: the light type can be inferred from other parameters (e.g. a point light has a length, radius, inner angle and outer angle of 0).

#### Color temperature

However, real-world artificial lights are often defined by their color temperature, measured in Kelvin (K). The color temperature of a light source is the temperature of an ideal black-body radiator that radiates light of comparable hue to that of the light source. For convenience, the tools should allow the artist to specify the hue of a light source as a color temperature (a meaningful range is 1,000 K to 12,500 K).

To compute RGB values from a temperature, we can use the Planckian locus, shown in figure [planckianLocus]. This locus is the path that the color of an incandescent black body takes in a chromaticity space as the body's temperature changes.

![Figure [planckianLocus]: The Planckian locus visualized on a CIE 1931 chromaticity diagram (source: Wikipedia)](/images/filament-md-ja/diagram_planckian_locus.png)

The easiest way to compute RGB values from this locus is to use the formula described in [#Krystek85]. Krystek's algorithm (equation $\ref{krystek}$) works in the CIE 1960 (UCS) space, using the following formula where $T$ is the desired temperature, and $u$ and $v$ the coordinates in UCS.

$$\begin{equation}\label{krystek}
u(T) = \frac{0.860117757 + 1.54118254 \times 10^{-4}T + 1.28641212 \times 10^{-7}T^2}{1 + 8.42420235 \times 10^{-4}T + 7.08145163 \times 10^{-7}T^2} \\
v(T) = \frac{0.317398726 + 4.22806245
 \times 10^{-5}T + 4.20481691 \times 10^{-8}T^2}{1 - 2.89741816
 \times 10^{-5}T + 1.61456053 \times 10^{-7}T^2}
\end{equation}$$

This approximation is accurate to roughly $ 9 \times 10^{-5} $ in the range 1,000K to 15,000K. From the CIE 1960 space we can compute the coordinates in xyY space (CIES 1931), using the formula from equation $\ref{cieToxyY}$.

$$\begin{equation}\label{cieToxyY}
x = \frac{3u}{2u - 8v + 4} \\
y = \frac{2v}{2u - 8v + 4}
\end{equation}$$

The formulas above are valid for black body color temperatures, and therefore correlated color temperatures of standard illuminants. If we wish to compute the precise chromaticity coordinates of standard CIE illuminants in the D series we can use equation $\ref{seriesDtoxyY}$.

$$\begin{equation}\label{seriesDtoxyY}
x = \begin{cases} 0.244063 + 0.09911 \frac{10^3}{T} + 2.9678 \frac{10^6}{T^2} - 4.6070 \frac{10^9}{T^3} & 4,000K \le T \le 7,000K \\
0.237040 + 0.24748 \frac{10^3}{T} + 1.9018 \frac{10^6}{T^2} - 2.0064 \frac{10^9}{T^3} & 7,000K \le T \le 25,000K \end{cases} \\
y = -3x^2 + 2.87 x - 0.275
\end{equation}$$

From the xyY space, we can then convert to the CIE XYZ space (equation $\ref{xyYtoXYZ}$).

$$\begin{equation}\label{xyYtoXYZ}
X = \frac{xY}{y} \\
Z = \frac{(1 - x - y)Y}{y}
\end{equation}$$

For our needs, we will fix $Y = 1$. This allows us to convert from the XYZ space to linear RGB with a simple 3x3 matrix, as shown in equation $\ref{XYZtoRGB}$.

$$\begin{equation}\label{XYZtoRGB}
\left[ \begin{matrix} R \\ G \\ B \end{matrix} \right] = M^{-1} \left[ \begin{matrix} X \\ Y \\ Z \end{matrix} \right]
\end{equation}$$

The transformation matrix M is calculated from the target RGB color space primaries. Equation $ \ref{XYZtoRGBValues} $ shows the conversion using the inverse matrix for the sRGB color space.

$$\begin{equation}\label{XYZtoRGBValues}
\left[ \begin{matrix} R \\ G \\ B \end{matrix} \right] = \left[ \begin{matrix} 3.2404542 & -1.5371385 & -0.4985314 \\ -0.9692660 & 1.8760108 & 0.0415560 \\ 0.0556434 & -0.2040259 & 1.0572252 \end{matrix} \right] \left[ \begin{matrix} X \\ Y \\ Z \end{matrix} \right]
\end{equation}$$

The result of these operations is a linear RGB triplet in the sRGB color space. Since we care about the chromaticity of the results, we must apply a normalization step to avoid clamping values greater than 1.0 and distort resulting colors:

$$\begin{equation}\label{normalizedRGB}
\hat{C}_{linear} = \frac{C_{linear}}{max(C_{linear})}
\end{equation}$$

We must finally apply the sRGB opto-electronic conversion function (OECF, shown in equation $ \ref{OECFsRGB} $) to obtain a displayable value (the value should remain linear if passed to the renderer for shading).

$$\begin{equation}\label{OECFsRGB}
C_{sRGB} = \begin{cases} 12.92 \times \hat{C}_{linear} & \hat{C}_{linear} \le 0.0031308 \\
1.055 \times \hat{C}_{linear}^{\frac{1}{2.4}} - 0.055 & \hat{C}_{linear} \gt 0.0031308 \end{cases}
\end{equation}$$

For convenience, figure [colorTemperatureScaleCCT] shows the range of correlated color temperatures from 1,000K to 12,500K. All the colors used below assume CIE $ D_{65} $ as the white point (as is the case in the sRGB color space).

![Figure [colorTemperatureScaleCCT]: Scale of correlated color temperatures](/images/filament-md-ja/diagram_color_temperature_cct.png)

Similarly, figure [colorTemperatureScaleCIE] shows the range of CIE standard illuminants series D from 1,000K to 12,500K.

![Figure [colorTemperatureScaleCIE]: Scale of CIE standard illuminants series D](/images/filament-md-ja/diagram_color_temperature_cie.png)

For reference, figure [colorTemperatureScaleCCTClamped] shows the range of correlated color temperatures without the normalization step presented in equation $\ref{normalizedRGB}$.

![Figure [colorTemperatureScaleCCTClamped]: Unnormalized scale of correlated color temperatures](/images/filament-md-ja/diagram_color_temperature_cct_clamped.png)

Table [colorTemperatureSamples] presents the correlated color temperature of various common light sources as sRGB color swatches. These colors are relative to the $ D_{65} $ white point, so their perceived hue might vary based on your display's white point. See [What colour is the Sun?](http://jila.colorado.edu/~ajsh/colour/Tspectrum.html) for more information.

    Temperature (K)  |          Light source        |                 Color
--------------------:|:-----------------------------|-------------------------------------------------------
1,700-1,800          | Match flame                  | 
1,850-1,930          | Candle flame                 | 
2,000-3,000          | Sun at sunrise/sunset        | 
2,500-2,900          | Household tungsten lightbulb | 
3,000                | Tungsten lamp 1K             | 
3,200-3,500          | Quartz lights                | 
3,200-3,700          | Fluorescent lights           | 
3,275                | Tungsten lamp 2K             | 
3,380                | Tungsten lamp 5K, 10K        | 
5,000-5,400          | Sun at noon                  | 
5,500-6,500          | Daylight (sun + sky)         | 
5,500-6,500          | Sun through clouds/haze      | 
6,000-7,500          | Overcast sky                 | 
6,500                | RGB monitor white point      | 
7,000-8,000          | Shaded areas outdoors        | 
8,000-10,000         | Partly cloudy sky            | 
*表 [colorTemperatureSamples]: Normalized correlated color temperatures for common light sources*

### Pre-exposed lights

Physically based rendering and physical light units pose an interesting challenge: how to store and handle the large range of values produced by the lighting code? Assuming computations performed at full precision in the shaders, we still want to be able to store the linear output of the lighting pass in a reasonably sized buffer (`RGB16F` or equivalent). The most obvious and easiest way to achieve this is to simply apply the camera exposure (see the Physically based camera section for more information) before writing out the result of the lighting pass. This simple step is shown in listing [preexposedLighting]:

```glsl
fragColor = luminance * camera.exposure;
```
*リスト [preexposedLighting]: The output of the lighting pass is pre-exposed to fit in half-float buffers*

This solution solves the storage problem but requires intermediate computations to be performed with single precision floats. We would instead prefer to perform all (or at least most) of the lighting work using half precision floats instead. Doing so can greatly improve performance and power usage, particularly on mobile devices. Half precision floats are however ill-suited for this kind of work as common illuminance and luminance values (for the sun for instance) can exceed their range. The solution is to simply pre-expose the lights themselves instead of the result of the lighting pass. This can be done efficiently on the CPU if updating a light's constant buffer is cheap. This can also be done on the GPU, as shown in listing [preexposedLights].

```glsl
// The inputs must be highp/single precision,
// both for range (intensity) and precision (exposure)
// The output is mediump/half precision
float computePreExposedIntensity(highp float intensity, highp float exposure) {
    return intensity * exposure;
}

Light getPointLight(uint index) {
    Light light;
    uint lightIndex = // fetch light index;

    // the intensity must be highp/single precision
    highp vec4 colorIntensity  = lightsUniforms.lights[lightIndex][1];

    // pre-expose the light
    light.colorIntensity.w = computePreExposedIntensity(
            colorIntensity.w, frameUniforms.exposure);

    return light;
}
```
*リスト [preexposedLights]: Pre-exposing lights allows the entire shading pipeline to use half precision floats*

In practice we pre-expose the following lights:
- Punctual lights (point and spot): on the GPU
- Directional light: on the CPU
- IBLs: on the CPU
- Material emissive: on the GPU
