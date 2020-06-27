import unittest
from copy import deepcopy

from approximate_string_matching.four_russians_helpers import four_russians_helpers

lcs_delete_cost_function = lambda a: 1
lcs_insert_cost_function = lambda b: 1
lcs_substitute_cost_function = lambda a, b: 0 if (a == b) else 2


class TestPrepareParameters(unittest.TestCase):
    def check_prepare_parameters(self, fr, t_1, t_2, expected_m, expected_A, expected_t_1, expected_t_2):
        m, A, step_size_bound, t_1, t_2 = fr.prepare_parameters(t_1, t_2)
        self.assertEqual(m, expected_m)
        self.assertEqual(A, expected_A)
        self.assertEqual(step_size_bound, 1)
        self.assertEqual(t_1, expected_t_1)
        self.assertEqual(t_2, expected_t_2)

    def test_prepare_parameters(self):
        fr = four_russians_helpers(lcs_delete_cost_function, lcs_insert_cost_function, lcs_substitute_cost_function)
        self.check_prepare_parameters(fr, "#abab", "#abab", 2, ['a', 'b'], "#abab", "#abab")
        self.check_prepare_parameters(fr, "#ababa", "#abc", 2, ['a', 'b', 'c'], "#ababa#", "#abc#")
        self.check_prepare_parameters(fr, "#11111111", "#000", 3, ['0', '1'], "#11111111#", "#000")

class TestGetAllStrings(unittest.TestCase):
    def check_get_all_strings(self, fr, m, A, dumb_letter, expected_strings):
        strings = fr.get_all_strings(m, A, dumb_letter)
        self.assertEqual(len(strings), len(expected_strings))
        self.assertEqual(strings, expected_strings)

    def test_get_all_strings(self):
        fr = four_russians_helpers(lcs_delete_cost_function, lcs_insert_cost_function, lcs_substitute_cost_function)
        self.check_get_all_strings(fr, 2, ['a', 'b'], '#', ["#aa", "#ab", "#ba", "#bb"])
        self.check_get_all_strings(fr, 3, ['z'], '?', ["?zzz"])

class TestStorage(unittest.TestCase):
    def check_storage(self, fr, R_expected_new, S_expected_new, C, D, R, S, storage):
        fr.store(R_expected_new, S_expected_new, C, D, R, S, storage)
        R_new, S_new = fr.fetch(C, D, R, S, storage)
        self.assertEqual(R_expected_new, R_new)
        self.assertEqual(S_expected_new, S_new)

    def test_storage(self):
        fr = four_russians_helpers(lcs_delete_cost_function, lcs_insert_cost_function, lcs_substitute_cost_function)
        storage = {}

        self.check_storage(fr, [0, -1], [1, 0], "ab", "ba", [0, 1], [0, -1], storage)
        self.check_storage(fr, [-10, -100], [1, 11], "ababa", "ba", [1, 1], [1, -1], storage)
        self.check_storage(fr, [0, -1], [1, 11], "ababa", "ba", [1, 1], [1, -1], storage)
        self.check_storage(fr, [0, -1], [1, 0], "ab", "ba", [0, 1], [0, -1], storage)

class TestAlgorithmY(unittest.TestCase):
    def test_algorithm_y(self):
        delete_cost_function2 = lambda a: 1
        insert_cost_function2 = lambda b: 1
        def substitute_cost_function2(c, d):
            if c == 'a' and d == 'a': return 0
            if c == 'b' and d == 'b': return 0
            if c == 'a' and d == 'b': return 1
            return 2

        fr = four_russians_helpers(delete_cost_function2, insert_cost_function2, substitute_cost_function2)
        text_1 = "#baabab"
        text_2 = "#ababaa"
        m, A, step_size_bound, t_1, t_2 = fr.prepare_parameters(text_1, text_2)
        storage = fr.algorithm_y(m, A, step_size_bound)

        whole_matrix = fr.restore_matrix(text_1, text_2, [0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 4, 5, 6], 6)

        diff_between_rows = deepcopy(whole_matrix)
        for i in range(1,7):
            for j in range(0,7):
                diff_between_rows[i][j] = whole_matrix[i][j] - whole_matrix[i-1][j]

        diff_between_columns =  deepcopy(whole_matrix)
        for i in range(0,7):
            for j in range(1,7):
                diff_between_columns[i][j] = whole_matrix[i][j] - whole_matrix[i][j-1]

        for i in range(0,5):
            for j in range(0,5):
                self.assertEqual(storage
                                 [text_1[i+1:i+3]]
                                 [text_2[j+1:j+3]]
                                 [(diff_between_rows[i+1][j],diff_between_rows[i+2][j])]
                                 [(diff_between_columns[i][j+1],diff_between_columns[i][j+2])],
                                 (
                                     [diff_between_rows[i+1][j+2],diff_between_rows[i+2][j+2]],
                                     [diff_between_columns[i+2][j + 1], diff_between_columns[i+2][j + 2]]
                                 ))
