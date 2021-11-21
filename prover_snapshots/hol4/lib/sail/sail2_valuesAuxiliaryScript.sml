(*Generated by Lem from ../../src/gen_lib/sail_values.lem.*)
open HolKernel Parse boolLib bossLib;
open lem_pervasives_extraTheory lem_machine_wordTheory sail2_valuesTheory;
open intLib;

val _ = numLib.prefer_num();



open lemLib;
(* val _ = lemLib.run_interactive := true; *)
val _ = new_theory "sail2_valuesAuxiliary"


(****************************************************)
(*                                                  *)
(* Termination Proofs                               *)
(*                                                  *)
(****************************************************)

(* val gst = Defn.tgoal_no_defn (shr_int_def, shr_int_ind) *)
val (shr_int_rw, shr_int_ind_rw) =
  Defn.tprove_no_defn ((shr_int_def, shr_int_ind),
    WF_REL_TAC`measure (Num o SND)` \\ COOPER_TAC
  )
val shr_int_rw = save_thm ("shr_int_rw", shr_int_rw);
val shr_int_ind_rw = save_thm ("shr_int_ind_rw", shr_int_ind_rw);
val () = computeLib.add_persistent_funs["shr_int_rw"];


(* val gst = Defn.tgoal_no_defn (shl_int_def, shl_int_ind) *)
val (shl_int_rw, shl_int_ind_rw) =
  Defn.tprove_no_defn ((shl_int_def, shl_int_ind),
    WF_REL_TAC`measure (Num o SND)` \\ COOPER_TAC
  )
val shl_int_rw = save_thm ("shl_int_rw", shl_int_rw);
val shl_int_ind_rw = save_thm ("shl_int_ind_rw", shl_int_ind_rw);
val () = computeLib.add_persistent_funs["shl_int_rw"];


(* val gst = Defn.tgoal_no_defn (repeat_def, repeat_ind) *)
val (repeat_rw, repeat_ind_rw) =
  Defn.tprove_no_defn ((repeat_def, repeat_ind),
    WF_REL_TAC`measure (Num o SND)` \\ COOPER_TAC
  )
val repeat_rw = save_thm ("repeat_rw", repeat_rw);
val repeat_ind_rw = save_thm ("repeat_ind_rw", repeat_ind_rw);
val () = computeLib.add_persistent_funs["repeat_rw"];


(* val gst = Defn.tgoal_no_defn (bools_of_nat_aux_def, bools_of_nat_aux_ind) *)
val (bools_of_nat_aux_rw, bools_of_nat_aux_ind_rw) =
  Defn.tprove_no_defn ((bools_of_nat_aux_def, bools_of_nat_aux_ind),
    WF_REL_TAC`measure (Num o FST)` \\ COOPER_TAC
  )
val bools_of_nat_aux_rw = save_thm ("bools_of_nat_aux_rw", bools_of_nat_aux_rw);
val bools_of_nat_aux_ind_rw = save_thm ("bools_of_nat_aux_ind_rw", bools_of_nat_aux_ind_rw);
val () = computeLib.add_persistent_funs["bools_of_nat_aux_rw"];


(* val gst = Defn.tgoal_no_defn (pad_list_def, pad_list_ind) *)
val (pad_list_rw, pad_list_ind_rw) =
  Defn.tprove_no_defn ((pad_list_def, pad_list_ind),
    WF_REL_TAC`measure (Num o SND o SND)` \\ COOPER_TAC
  )
val pad_list_rw = save_thm ("pad_list_rw", pad_list_rw);
val pad_list_ind_rw = save_thm ("pad_list_ind_rw", pad_list_ind_rw);
val () = computeLib.add_persistent_funs["pad_list_rw"];


(* val gst = Defn.tgoal_no_defn (reverse_endianness_list_def, reverse_endianness_list_ind) *)
val (reverse_endianness_list_rw, reverse_endianness_list_ind_rw) =
  Defn.tprove_no_defn ((reverse_endianness_list_def, reverse_endianness_list_ind),
    WF_REL_TAC`measure LENGTH` \\ rw[drop_list_def,nat_of_int_def]
  )
val reverse_endianness_list_rw = save_thm ("reverse_endianness_list_rw", reverse_endianness_list_rw);
val reverse_endianness_list_ind_rw = save_thm ("reverse_endianness_list_ind_rw", reverse_endianness_list_ind_rw);
val () = computeLib.add_persistent_funs["reverse_endianness_list_rw"];


(* val gst = Defn.tgoal_no_defn (index_list_def, index_list_ind) *)
val (index_list_rw, index_list_ind_rw) =
  Defn.tprove_no_defn ((index_list_def, index_list_ind),
    WF_REL_TAC`measure (λ(x,y,z). Num(1+(if z > 0 then int_max (-1) (y - x) else int_max (-1) (x - y))))`
    \\ rw[integerTheory.INT_MAX]
    \\ intLib.COOPER_TAC
  )
val index_list_rw = save_thm ("index_list_rw", index_list_rw);
val index_list_ind_rw = save_thm ("index_list_ind_rw", index_list_ind_rw);
val () = computeLib.add_persistent_funs["index_list_rw"];


(*
(* val gst = Defn.tgoal_no_defn (while_def, while_ind) *)
val (while_rw, while_ind_rw) =
  Defn.tprove_no_defn ((while_def, while_ind),
    cheat (* the termination proof *)
  )
val while_rw = save_thm ("while_rw", while_rw);
val while_ind_rw = save_thm ("while_ind_rw", while_ind_rw);
*)


(*
(* val gst = Defn.tgoal_no_defn (until_def, until_ind) *)
val (until_rw, until_ind_rw) =
  Defn.tprove_no_defn ((until_def, until_ind),
    cheat (* the termination proof *)
  )
val until_rw = save_thm ("until_rw", until_rw);
val until_ind_rw = save_thm ("until_ind_rw", until_ind_rw);
*)


(****************************************************)
(*                                                  *)
(* Lemmata                                          *)
(*                                                  *)
(****************************************************)

val just_list_spec = store_thm("just_list_spec",
``((! xs. (just_list xs = NONE) <=> MEM NONE xs) /\
   (! xs es. (just_list xs = SOME es) <=> (xs = MAP SOME es)))``,
  (* Theorem: just_list_spec*)
  conj_tac
  \\ ho_match_mp_tac just_list_ind
  \\ Cases \\ rw[]
  \\ srw_tac [boolSimps.NORMEQ_ss] [Once just_list_def]
  >- ( CASE_TAC \\ fs[] \\ CASE_TAC )
  \\ Cases_on`es` \\ fs[]
  \\ CASE_TAC \\ fs[]
  \\ CASE_TAC \\ fs[]
);



val _ = export_theory()
