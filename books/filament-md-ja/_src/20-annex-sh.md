## Spherical Harmonics

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


          Symbol             |           Definition
:---------------------------:|:---------------------------|
$K^m_l$                      | Normalization factors
$P^m_l(x)$                   | Associated Legendre polynomials
$y^m_l$                      | Spherical harmonics bases, or SH bases
$L^m_l$                      | SH coefficients of the $L(s)$ function defined on the unit sphere
*表 [shSymbols]: Spherical harmonics symbols definitions*

### Basis functions

Spherical parameterization of points on the surface of the unit sphere:

$$\begin{equation}
\{ x, y, z \} = \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
\end{equation}$$

The complex spherical harmonics bases are given by:

$$\begin{equation}
Y^m_l(\theta, \phi) = K^m_l e^{im\theta} P^{|m|}_l(cos \theta), l \in N, -l <= m <= l
\end{equation}$$

However we only need the real bases:

$$\begin{align*}
y^{m > 0}_l &= \sqrt{2} K^m_l cos(m \phi) P^m_l(cos \theta) \\
y^{m < 0}_l &= \sqrt{2} K^m_l sin(|m| \phi) P^{|m|}_l(cos \theta) \\
y^0_l &= K^0_l P^0_l(cos \theta)
\end{align*}$$

The normalization factors are given by:

$$\begin{equation}
K^m_l = \sqrt{\frac{(2l + 1)(l - |m|)!}{4 \pi (l + |m|)!}}
\end{equation}$$

The associated Legendre polynomials $P^{|m|}_l$ can be calculated from the following recursions:

$$\begin{equation}\label{shRecursions}
P^0_0(x) = 1 \\
P^0_1(x) = x \\
P^l_l(x) = (-1)^l (2l - 1)!! (1 - x^2)^{\frac{l}{2}} \\
P^m_l(x) = \frac{((2l - 1) x P^m_{l - 1} - (l + m - 1) P^m_{l - 2})}{l - m} \\
\end{equation}$$

Computing $y^{|m|}_l$ requires to compute $P^{|m|}_l(z)$ first.
This can be accomplished fairly easily using the recursions in equation $\ref{shRecursions}$.
The third recursion can be used to "move diagonally" in table [basisFunctions], i.e. calculating $y^0_0$, $y^1_1$, $y^2_2$ etc.
Then, the fourth recursion can be used to move vertically.

  Band index |  Basis functions $-l <= m <= l$
:-----------:|:---------------------------------:|
$l = 0$      | $y^0_0$
$l = 1$      | $y^{-1}_1$ $y^0_1$ $y^1_1$
$l = 2$      | $y^{-2}_2$ $y^{-1}_2$ $y^0_2$ $y^1_2$ $y^2_2$
*表 [basisFunctions]: Basis functions per band*

It’s also fairly easy to compute the trigonometric terms recursively:

$$\begin{align*}
C_m &\equiv cos(m \phi)sin(\theta)^m \\
S_m &\equiv sin(m \phi)sin(\theta)^m \\
\{ x, y, z \} &= \{ cos \phi sin \theta, sin \phi sin \theta, cos \theta \}
\end{align*}$$

Using the angle sum trigonometric identities:

$$\begin{align*}
cos(m \phi + \phi) &= cos(m \phi) cos(\phi) - sin(m \phi) sin(\phi) \Leftrightarrow C_{m + 1} = x C_m - y S_m \\
sin(m \phi + \phi) &= sin(m \phi) cos(\phi) + cos(m \phi) sin(\phi) \Leftrightarrow S_{m + 1} = x S_m - y C_m
\end{align*}$$

Listing [nonNormalizedSHBasis] shows the C++ code to compute the non-normalized SH basis $\frac{y^m_l(s)}{\sqrt{2} K^m_l}$:

```glsl
static inline size_t SHindex(ssize_t m, size_t l) {
    return l * (l + 1) + m;
}

void computeShBasis(
        double* const SHb,
        size_t numBands,
        const vec3& s)
{
    // handle m=0 separately, since it produces only one coefficient
    double Pml_2 = 0;
    double Pml_1 = 1;
    SHb[0] =  Pml_1;
    for (ssize_t l = 1; l < numBands; l++) {
        double Pml = ((2 * l - 1) * Pml_1 * s.z - (l - 1) * Pml_2) / l;
        Pml_2 = Pml_1;
        Pml_1 = Pml;
        SHb[SHindex(0, l)] = Pml;
    }
    double Pmm = 1;
    for (ssize_t m = 1; m < numBands ; m++) {
        Pmm = (1 - 2 * m) * Pmm;
        double Pml_2 = Pmm;
        double Pml_1 = (2 * m + 1)*Pmm*s.z;
        // l == m
        SHb[SHindex(-m, m)] = Pml_2;
        SHb[SHindex( m, m)] = Pml_2;
        if (m + 1 < numBands) {
            // l == m+1
            SHb[SHindex(-m, m + 1)] = Pml_1;
            SHb[SHindex( m, m + 1)] = Pml_1;
            for (ssize_t l = m + 2; l < numBands; l++) {
                double Pml = ((2 * l - 1) * Pml_1 * s.z - (l + m - 1) * Pml_2)
                        / (l - m);
                Pml_2 = Pml_1;
                Pml_1 = Pml;
                SHb[SHindex(-m, l)] = Pml;
                SHb[SHindex( m, l)] = Pml;
            }
        }
    }
    double Cm = s.x;
    double Sm = s.y;
    for (ssize_t m = 1; m <= numBands ; m++) {
        for (ssize_t l = m; l < numBands ; l++) {
            SHb[SHindex(-m, l)] *= Sm;
            SHb[SHindex( m, l)] *= Cm;
        }
        double Cm1 = Cm * s.x - Sm * s.y;
        double Sm1 = Sm * s.x + Cm * s.y;
        Cm = Cm1;
        Sm = Sm1;
    }
}
```
*リスト [nonNormalizedSHBasis]: C++ implementation to compute a non-normalized SH basis*

Normalized SH basis functions $y^m_l(s)$ for the first 3 bands:

   Band  |               $m = -2$               |                $m = -1$               |                      $m = 0$                        |                $m = 1$                |                    $m = 2$                    |
:-------:|:------------------------------------:|:-------------------------------------:|:---------------------------------------------------:|:-------------------------------------:|:---------------------------------------------:|
$l = 0$  |                                      |                                       | $\frac{1}{2}\sqrt{\frac{1}{\pi}}$                   |                                       |                                               |
$l = 1$  |                                      | $-\frac{1}{2}\sqrt{\frac{3}{\pi}}y$   | $\frac{1}{2}\sqrt{\frac{3}{\pi}}z$                  | $-\frac{1}{2}\sqrt{\frac{3}{\pi}}x$   |                                               |
$l = 2$  | $\frac{1}{2}\sqrt{\frac{15}{\pi}}xy$ | $-\frac{1}{2}\sqrt{\frac{15}{\pi}}yz$ | $\frac{1}{4}\sqrt{\frac{5}{\pi}}(2z^2 - x^2 - y^2)$ | $-\frac{1}{2}\sqrt{\frac{15}{\pi}}xz$ | $\frac{1}{4}\sqrt{\frac{15}{\pi}}(x^2 - y^2)$ |
*表 [basisFunctions]: Normalized basis functions per band*

### Decomposition and reconstruction

A function $L(s)$ defined on a sphere is projected to the SH basis as follows:

$$\begin{equation}
L^m_l = \int_\Omega L(s) y^m_l(s) ds \\
L^m_l = \int_{\theta = 0}^{\pi} \int_{\phi = 0}^{2\pi} L(\theta, \phi) y^m_l(\theta, \phi) sin \theta d\theta d\phi
\end{equation}$$

Note that each $L^m_l$ is a vector of 3 values, one for each RGB color channel.

The inverse transformation, or reconstruction, or rendering, from the SH coefficients is given by:

$$\begin{equation}
\hat{L}(s) = \sum_l \sum_{m = -l}^l L^m_l y^m_l(s)
\end{equation}$$

### Decomposition of $\left< cos \theta \right>$

Since $\left< cos \theta \right>$ does not depend on $\phi$ (azimuthal independence), the integral simplifies to:

$$\begin{align*}
C^0_l &= 2\pi \int_0^{\pi} \left< cos \theta \right> y^0_l(\theta) sin \theta d\theta \\
C^0_l &= 2\pi K^m_l \int_0^{\frac{\pi}{2}} P^0_l(cos \theta) cos \theta sin \theta d\theta \\
C^m_l &= 0, m != 0
\end{align*}$$

In [#Ramamoorthi01] an analytical solution to the integral is described:

$$\begin{align*}
C_1 &= \sqrt{\frac{\pi}{3}} \\
C_{odd} &= 0 \\
C_{l, even} &= 2\pi \sqrt{\frac{2l + 1}{4\pi}} \frac{(-1)^{\frac{l}{2} - 1}}{(l + 2)(l - 1)} \frac{l!}{2^l (\frac{l!}{2})^2}
\end{align*}$$

The first few coefficients are:

$$\begin{align*}
C_0 &= +0.88623 \\
C_1 &= +1.02333 \\
C_2 &= +0.49542 \\
C_3 &= +0.00000 \\
C_4 &= -0.11078
\end{align*}$$

Very few coefficients are needed to reasonably approximate $\left< cos \theta \right>$, as shown in figure [shCosThetaApprox].

![Figure [shCosThetaApprox]: Approximation of $cos \theta$ with SH coefficients](/images/filament-md-ja/chart_sh_cos_thera_approx.png)

### Convolution

Convolutions by a kernel $h$ that has a circular symmetry can be applied directly and easily in SH space:

$$\begin{equation}
(h * f)^m_l = \sqrt{\frac{4\pi}{2l + 1}} h^0_l(s) f^m_l(s)
\end{equation}$$

Conveniently, $\sqrt{\frac{4\pi}{2l + 1}} = \frac{1}{K^0_l}$, so in practice we pre-multiply $C_l$ by $\frac{1}{K^0_l}$ and we get a simpler expression:

$$\begin{equation}
\hat{C}_{l, even} = 2\pi \frac{(-1)^{\frac{l}{2} - 1}}{(l + 2)(l - 1)} \frac{l!}{2^l (\frac{l!}{2})^2} \\
\hat{C}_1 = \frac{2\pi}{3}
\end{equation}$$

Here is the C++ code to compute $\hat{C}_l$:

```glsl
static double factorial(size_t n, size_t d = 1);

// < cos(theta) > SH coefficients pre-multiplied by 1 / K(0,l)
double computeTruncatedCosSh(size_t l) {
    if (l == 0) {
        return M_PI;
    } else if (l == 1) {
        return 2 * M_PI / 3;
    } else if (l & 1) {
        return 0;
    }
    const size_t l_2 = l / 2;
    double A0 = ((l_2 & 1) ? 1.0 : -1.0) / ((l + 2) * (l - 1));
    double A1 = factorial(l, l_2) / (factorial(l_2) * (1 << l));
    return 2 * M_PI * A0 * A1;
}

// returns n! / d!
double factorial(size_t n, size_t d ) {
   d = std::max(size_t(1), d);
   n = std::max(size_t(1), n);
   double r = 1.0;
   if (n == d) {
       // intentionally left blank
   } else if (n > d) {
       for ( ; n>d ; n--) {
           r *= n;
       }
   } else {
       for ( ; d>n ; d--) {
           r *= d;
       }
       r = 1.0 / r;
   }
   return r;
}
```
