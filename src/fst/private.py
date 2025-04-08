"""This only exists temporarily to audit private function docstrings."""

from .fst import (
    _with_loc,
    _next_src,
    _prev_src,
    _next_find,
    _prev_find,
    _next_pars,
    _prev_pars,
    _fixup_field_body,
    _fixup_slice_index,
    _normalize_code,
    _new_empty_module,
    _new_empty_tuple,
    _new_empty_list,
    _new_empty_dict,
    _new_empty_set_curlies,
    _new_empty_set_call,
    FST
)

__all__ = [
    '_with_loc',
    '_next_src',
    '_prev_src',
    '_next_find',
    '_prev_find',
    '_next_pars',
    '_prev_pars',
    '_fixup_field_body',
    '_fixup_slice_index',
    '_normalize_code',
    '_new_empty_module',
    '_new_empty_tuple',
    '_new_empty_list',
    '_new_empty_dict',
    '_new_empty_set_curlies',
    '_new_empty_set_call',

    '_FST_make_fst_tree',
    '_FST_unmake_fst_tree',
    '_FST_repr_tail',
    '_FST_dump',
    '_FST_prev_ast_bound',
    '_FST_next_ast_bound',
    '_FST_lpars',
    '_FST_rpars',
    '_FST_loc_from_children',
    '_FST_dict_key_or_mock_loc',
    '_FST_floor_start_pos',
    '_FST_set_end_pos',
    '_FST_maybe_add_comma',
    '_FST_maybe_add_singleton_tuple_comma',
    '_FST_maybe_fix_tuple',
    '_FST_maybe_fix_set',
    '_FST_maybe_fix_if',
    '_FST_make_fst_and_dedent',
    '_FST_get_seq_and_dedent',
    '_FST_get_slice_tuple_list_or_set',
    '_FST_get_slice_empty_set_call',
    '_FST_get_slice_dict',
    '_FST_get_slice_stmt',
    '_FST_put_seq_and_indent',
    '_FST_put_slice_tuple_list_or_set',
    '_FST_put_slice_empty_set_call',
    '_FST_put_slice_dict',
]

_FST_make_fst_tree                   = FST._make_fst_tree
_FST_unmake_fst_tree                 = FST._unmake_fst_tree
_FST_repr_tail                       = FST._repr_tail
_FST_dump                            = FST._dump
_FST_prev_ast_bound                  = FST._prev_ast_bound
_FST_next_ast_bound                  = FST._next_ast_bound
_FST_lpars                           = FST._lpars
_FST_rpars                           = FST._rpars
_FST_loc_from_children               = FST._loc_from_children
_FST_dict_key_or_mock_loc            = FST._dict_key_or_mock_loc
_FST_floor_start_pos                 = FST._floor_start_pos
_FST_set_end_pos                     = FST._set_end_pos
_FST_maybe_add_comma                 = FST._maybe_add_comma
_FST_maybe_add_singleton_tuple_comma = FST._maybe_add_singleton_tuple_comma
_FST_maybe_fix_tuple                 = FST._maybe_fix_tuple
_FST_maybe_fix_set                   = FST._maybe_fix_set
_FST_maybe_fix_if                    = FST._maybe_fix_if
_FST_make_fst_and_dedent             = FST._make_fst_and_dedent
_FST_get_seq_and_dedent              = FST._get_seq_and_dedent
_FST_get_slice_tuple_list_or_set     = FST._get_slice_tuple_list_or_set
_FST_get_slice_empty_set_call        = FST._get_slice_empty_set_call
_FST_get_slice_dict                  = FST._get_slice_dict
_FST_get_slice_stmt                  = FST._get_slice_stmt
_FST_put_seq_and_indent              = FST._put_seq_and_indent
_FST_put_slice_tuple_list_or_set     = FST._put_slice_tuple_list_or_set
_FST_put_slice_empty_set_call        = FST._put_slice_empty_set_call
_FST_put_slice_dict                  = FST._put_slice_dict
