# Lighting

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


The correctness and coherence of the lighting environment is paramount to achieving plausible visuals. After surveying existing rendering engines (such as Unity or Unreal Engine 4) as well as the traditional real-time rendering literature, it is obvious that coherency is rarely achieved.

The Unreal Engine, for instance, lets artists specify the "brightness" of a point light in lumens, a unit of luminous power. The brightness of directional lights is however expressed using an arbitrary unnamed unit. To match the brightness of a point light with a luminous power of 5,000 lumens, the artist must use a directional light of brightness 10. This kind of mismatch makes it difficult for artists to maintain the visual integrity of a scene when adding, removing or modifying lights.
Using solely arbitrary units is a coherent solution but it makes reusing lighting rigs a difficult task. For instance, an outdoor scene will use a directional light of brightness 10 as the sun and all other lights will be defined relative to that value. Moving these lights to an indoor environment would make them too bright.

Our goal is therefore to make all lighting correct by default, while giving artists enough freedom to achieve the desired look. We will support a number of lights, split in two categories, direct and indirect lighting:

**Direct lighting**: punctual lights, photometric lights, area lights.

**Indirect lighting**: image based lights (IBLs), for both local[^localProbesMobile] and distant light probes.

[^localProbesMobile]: Local light probes might be too expensive to support on mobile, we will first focus our efforts on distant light probes set at infinity

## Units

The following sections will discuss how to implement various types of lights and the proposed equations make use of different symbols and units summarized in table [lightUnits].

    Photometric term    |      Notation      |        Unit
-----------------------:|:------------------:|:-----------------
Luminous power          | $\Phi$             | Lumen ($lm$)
Luminous intensity      | $I$                | Candela ($cd$) or $\frac{lm}{sr}$
Illuminance             | $E$                | Lux ($lx$) or $\frac{lm}{m^2}$
Luminance               | $L$                | Nit ($nt$) or $\frac{cd}{m^2}$
Radiant power           | $\Phi_e$           | Watt ($W$)
Luminous efficacy       | $\eta$             | Lumens per watt ($\frac{lm}{W}$)
Luminous efficiency     | $V$                | Percentage (%)
*表 [lightUnits]: Photometric units*

To get properly coherent lighting, we must use light units that respect the ratio between various light intensities found in real-world scenes. These intensities can vary greatly, from around 800 $lm$ for a household light bulb to 120,000 $lx$ for a daylight sky and sun illumination.

The easiest way to achieve lighting coherency is to adopt physical light units. This will in turn enable full reusability of lighting rigs. Using physical light units also allows us to use a physically based camera.

Table [lightTypesUnits] shows the light unit associated with each type of light we intend to support.

        Light type       |        Unit
------------------------:|:---------------------
Directional light        | Illuminance ($lx$ or $\frac{lm}{m^2}$)
Point light              | Luminous power ($lm$)
Spot light               | Luminous power ($lm$)
Photometric light        | Luminous intensity ($cd$)
Masked photometric light | Luminous power ($lm$)
Area light               | Luminous power ($lm$)
Image based light        | Luminance ($\frac{cd}{m^2}$)
*表 [lightTypesUnits]: Intensity unity for each light type*

**Notes about the radiant power unit**

Even though commercially available light bulbs often display their brightness in lumens on the packaging, it is common to refer to the brightness of a light bulb by using its required energy in watts. The number of watts only indicates how much energy a bulb uses, not how bright it is. It is even more important to understand this difference now that more energy efficient bulbs are readily available (halogens, LEDs, etc.).

However, since artists might be accustomed to gauging a light's brightness by its power, we should allow users to use the power unit to define the brightness of a light. The conversion is presented in equation $\ref{radiantPowerToLuminousPower}$.

$$\begin{equation}\label{radiantPowerToLuminousPower}
\Phi = \Phi_e \eta
\end{equation}$$

In equation $\ref{radiantPowerToLuminousPower}$, $\eta$ is the luminous efficacy of the light, expressed in lumens per watt. Knowing that the [maximum possible luminous efficacy](http://en.wikipedia.org/wiki/Luminous_efficacy) is 683 $\frac{lm}{W}$ we can also use luminous efficiency $V$ (also called luminous coefficient), as shown in equation $\ref{radiantPowerLuminousEfficiency}$.

$$\begin{equation}\label{radiantPowerLuminousEfficiency}
\Phi = \Phi_e 683 \times V
\end{equation}$$

Table [lightTypesEfficacy] can be used as a reference to convert watts to lumens using either the luminous efficacy or the luminous efficiency of various types of lights. More specific values are available on Wikipedia's [luminous efficacy](http://en.wikipedia.org/wiki/Luminous_efficacy) page.

       Light type       |  Efficacy $\eta$   |  Efficiency $V$
-----------------------:|:------------------:|:-----------------
Incandescent            | 14-35              | 2-5%
LED                     | 28-100             | 4-15%
Fluorescent             | 60-100             | 9-15%
*表 [lightTypesEfficacy]: Efficacy and efficiency of various light types*

### Light units validation

One of the big advantages of using physical light units is the ability to physically validate our equations. We can use specialized devices to measure three light units.

#### Illuminance

The illuminance reaching a surface can be measured using an incident light meter. For our tests, we use a [Sekonic L-478D](http://www.sekonic.com/products/l-478d/overview.aspx), shown in figure [sekonic].

The incident light meter uses a white diffuse dome to capture the illuminance reaching a surface. It is important to orient the dome properly depending on the desired measurement. For instance, orienting the dome perpendicular to the sun on a bright clear day will give very different results than orienting the dome horizontally.

![Figure [sekonic]: Sekonic L-478D incident light meter](/images/filament-md-ja/photo_light_meter.jpg)

#### Luminance

The luminance at a surface, or the product of the incident light and the surface, can be measured using a luminance meter, also often called a spot meter. While incident light meters use a diffuse hemisphere to capture light from all directions, a spot meter uses a shield to measure incident light from a single direction. For our tests, we use a [Sekonic 5 degree Viewfinder](http://www.sekonic.com/products/l-478dr/accessories/np-finder-5-degree-for-l-478.aspx) that can replace the diffuser on the L-478D to measure luminance in a 5 degree cone.

![Sekonic L-478D working as a luminance meter using a special viewfinder](/images/filament-md-ja/photo_incident_light_meter.jpg)

#### Luminous intensity

The luminous intensity of a light source cannot be measured directly but can be derived from the measured illuminance if we know the distance between the measuring device and the light source. Equation $\ref{derivedLuminousIntensity}$ is a simple application of the inverse square law discussed in section [Punctual lights].

$$\begin{equation}\label{derivedLuminousIntensity}
I = E \cdot d^2
\end{equation}$$
