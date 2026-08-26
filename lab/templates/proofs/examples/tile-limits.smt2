; tile-limits.smt2 — offline sketch for shared-memory tile bounds
; This file is a template example. It does not require z3 on PATH for verify_template.
; Command when z3 is installed:
;   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH z3 -smt2 tile-limits.smt2
;
; Assumptions (must appear in the Z3 report):
;   - per-block shared memory = 228 KiB
;   - smem_bytes(TM,TN) = 4 * TM * TN  (operator-stated static formula)
;   - TM, TN in {8,16,...,128}

(set-logic QF_LIA)

(declare-const TM Int)
(declare-const TN Int)

; Multiples of 8 in [8, 128]
(assert (and (>= TM 8) (<= TM 128) (= (mod TM 8) 0)))
(assert (and (>= TN 8) (<= TN 128) (= (mod TN 8) 0)))

(define-fun smem_bytes ((tm Int) (tn Int)) Int
  (* 4 (* tm tn)))

; Shared-memory capacity: 228 KiB
(assert (<= (smem_bytes TM TN) (* 228 1024)))

; Sanity check: ask for any admissible pair (not the optimize step).
; For maximization, use z3's optimize API or a documented search wrapper.
(check-sat)
(get-model)
