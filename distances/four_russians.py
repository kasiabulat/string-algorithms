def get_all_strings(length, alphabet_size):
    """ Returns all possible strings of a given length """

    sub_length_results = []
    sub_length_results[0] = []
    sub_length_results[1] = [[letter] for letter in range(0, alphabet_size)]

    for size in range(2, length + 1):
        sub_length_results[size] = []
        for left_substring in sub_length_results[1]:
            for right_substring in sub_length_results[size - 1]:
                sub_length_results[size].append(left_substring + right_substring)

    return sub_length_results[length]


def store(R_new, S_new, C, D, R, S, storage):
    storage[C][D][R][S] = (R_new, S_new)


def algorithm_y(m, alphabet_size, step_size_bound, delete_cost_function, insert_cost_function, replace_cost_function):
    """ Preprocesses data by creating helper submatrices """

    strings = get_all_strings(m, alphabet_size)
    step_vectors = get_all_strings(m, 2 * step_size_bound + 1)
    step_vectors_mapped = []
    for step_vector in step_vectors:
        step_vectors_mapped.append([letter - step_size_bound for letter in step_vector])

    storage = []

    for C in strings:
        for D in strings:
            for R in step_vectors_mapped:
                for S in step_vectors_mapped:
                    T = []
                    U = []

                    for i in range(1, m):
                        T[i][0] = R[i]
                        U[0][i] = S[i]

                    for i in range(1, m):
                        for j in range(1, m):
                            T[i][j] = min(
                                replace_cost_function(C[i], D[j]) - U[i-1][j],
                                delete_cost_function([C[i]]),
                                insert_cost_function(D[j] + T[i][j-1] - U[i-1][j]))
                            U[i][j] = min(
                                replace_cost_function(C[i],D[j]) - T[i][j-1],
                                delete_cost_function(C[i]) + U[i-1][j] - T[i][j-1],
                                insert_cost_function[D[j]]
                            )

                    R_new = []
                    S_new = []

                    for i in range(1,m):
                        R_new.append(T[i][m])
                        S_new.append(U[m][i])

                    store(R_new, S_new, R, S, C, D, storage)

    return storage
