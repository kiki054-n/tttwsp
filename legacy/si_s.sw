# Stillinger-Weber potential for Si-S system
# TriTetra Water Splitting Project v3.1.4
#
# Si-Si parameters: original Stillinger & Weber (1985)
# Si-S  parameters: approximated from Si-Si with S corrections
#                   (valence: S=6 vs Si=4 → larger epsilon, smaller sigma)
# S-S   parameters: approximated
#
# Format:
# element1 element2 element3  epsilon  sigma  a  lambda  gamma  costheta0  A  B  p  q  tol

# ── 2体項 (Two-body) ────────────────────────────────────────
# Si-Si-Si (標準 Stillinger-Weber 1985)
Si  Si  Si  2.1683  2.0951  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# Si-S-Si  (Si格子中のS: σを小さく, εを大きく → 歪み導入)
Si  S   Si  2.8000  1.9500  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# S-Si-Si
S   Si  Si  2.8000  1.9500  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# S-S-Si
S   S   Si  3.2000  1.8800  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# S-Si-S
S   Si  S   3.2000  1.8800  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# Si-Si-S
Si  Si  S   2.8000  1.9500  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0

# S-S-S
S   S   S   3.5000  1.8000  1.80  21.0  1.20  -0.333333  7.049556277  0.6022245584  4  0  0.0
