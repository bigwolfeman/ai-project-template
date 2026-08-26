/-
  MergePreserves.lean — offline sketch for merge-preserves-sorted
  This file is a template example. It does not require lake/lean on PATH for verify_template.
  Commands when Lean/Lake are installed (from the package that contains this module):
    env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH lake build
    env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH lean MergePreserves.lean

  Assumptions (must appear in the Lean report):
    - le is a linear order
    - inputs are finite lists
    - no concurrent mutation
-/

-- Sketch only. A live package must supply Sorted, merge, and a real proof or sorry policy.
-- namespace MergePreserves where
--
-- def merge {α} (le : α → α → Bool) : List α → List α → List α
--   | [], ys => ys
--   | xs, [] => xs
--   | x :: xs, y :: ys =>
--       if le x y then x :: merge le xs (y :: ys) else y :: merge le (x :: xs) ys
--
-- theorem merge_preserves_sorted
--     {α : Type} (le : α → α → Prop) [LinearOrder α]
--     (xs ys : List α)
--     (hxs : Sorted le xs) (hys : Sorted le ys) :
--     Sorted le (merge (fun a b => decide (le a b)) xs ys) := by
--   sorry -- replace with a real proof in a live campaign artifact
