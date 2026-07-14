---
title: "記法"
---

本ドキュメント全体で使用される方程式では、表 [symbols] で説明されている記号を使用します。

| 記号 | 定義 |
| :---: | :--- |
| $v$ | View（視線）の単位ベクトル |
| $l$ | 入射光の単位ベクトル |
| $n$ | サーフェス法線の単位ベクトル |
| $h$ | $l$ と $v$ の間のハーフ単位ベクトル |
| $f$ | BRDF |
| $f_d$ | BRDF の Diffuse 成分 |
| $f_r$ | BRDF の Specular 成分 |
| $\alpha$ | Roughness、入力 `perceptualRoughness` からリマップされたもの |
| $\sigma$ | Diffuse reflectance |
| $\Omega$ | 球面領域 |
| $f_{0}$ | 垂直入射での反射率 |
| $f_{90}$ | 掠角での反射率 |
| $\chi^{+}(a)$ | Heaviside 関数（$a > 0$ なら 1、それ以外は 0） |
| $n_{ior}$ | 界面の屈折率（IOR） |
| $\left< n \cdot l \right>$ | [0..1] にクランプされた内積 |
| $\left< a \right>$ | 飽和値（[0..1] にクランプ） |
*表 [symbols]: 記号の定義*

---

原文: https://google.github.io/filament/Filament.html
