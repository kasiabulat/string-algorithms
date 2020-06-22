from collections import namedtuple
import math

from approximate_string_matching.four_russians import algorithm_y, algorithm_z

ScoreMatrix = namedtuple(
    'ScoreMatrix', ['insert', 'delete', 'substitute', 'match'])

def hamming_distance(text_1, text_2, n_1, n_2):
  if n_1 != n_2:
    raise ValueError('Hamming distance is defined only for equal strings')
  return sum(ci != cj for ci, cj in zip(text_1[1:], text_2[1:]))

def distance_row(text_1, text_2, _, n_2, S):
  previous_row, current_row = None, range(n_2 + 1)
  for i, ci in enumerate(text_1[1:]):
    previous_row, current_row = current_row, [i + 1] + [None] * n_2
    for j, cj in enumerate(text_2[1:]):
      insertion = previous_row[j + 1] + S.insert(ci)
      deletion = current_row[j] + S.delete(cj)
      if ci != cj:
        substitution = previous_row[j] + S.substitute(ci, cj)
      else:
        substitution = previous_row[j] + S.match(ci)
      current_row[j + 1] = min(insertion, deletion, substitution)
  return current_row

def edit_distance(text_1, text_2, n_1, n_2):
  S = ScoreMatrix(
      insert = lambda ci: 1, delete = lambda ci: 1,
      substitute = lambda ci, cj: 1, match = lambda ci: 0)
  if n_1 >= n_2:
    return distance_row(text_1, text_2, n_1, n_2, S)[-1]
  return distance_row(text_2, text_1, n_2, n_1, S)[-1]

def indel_distance_row(text_1, text_2, n_1, n_2):
  S = ScoreMatrix(
      insert = lambda ci: 1, delete = lambda ci: 1,
      substitute = lambda ci, cj: math.inf, match = lambda ci: 0)
  return distance_row(text_1, text_2, n_1, n_2, S)

def indel_distance(text_1, text_2, n_1, n_2):
  return indel_distance_row(text_1, text_2, n_1, n_2)[-1]

def edit_distance_four_russians(text_1, text_2, alphabet_size, delete_cost_function, insert_cost_function, replace_cost_function):
    """ Algorithm proposed by William J. Masek and Michael S. Paterson, using the method of "Four Russians """

    def get_parameter(A):
      return int(math.log2(len(A)))

    def get_step_size_bound():
      I = max([insert_cost_function(letter_idx) for letter_idx in range(0, alphabet_size)])
      D = max([delete_cost_function(letter_idx) for letter_idx in range(0, alphabet_size)])
      return max(I, D)

    m = get_parameter(text_1)
    step_size_bound = get_step_size_bound()

    storage = algorithm_y(m, alphabet_size, step_size_bound,
                          delete_cost_function, insert_cost_function, replace_cost_function)

    cost = algorithm_z(m, text_1, text_2, delete_cost_function, insert_cost_function, storage)

    return cost
