def get_all_strings(m, A, dumb_letter):
    """ Returns all possible strings of a given length """

    # print("m: "+str(m))
    # print("A: "+str(A))

    sub_length_results = [[] for _ in range(m+1)]
    sub_length_results[0] = []
    sub_length_results[1] = [letter for letter in A]

    for size in range(2, m + 1):
        sub_length_results[size] = []
        for left_substring in sub_length_results[1]:
            for right_substring in sub_length_results[size - 1]:
                sub_length_results[size].append(left_substring + right_substring)

    result = [dumb_letter + word for word in sub_length_results[m]]
    return result


def algorithm_y(m, A, step_size_bound, delete_cost_function, insert_cost_function, substitute_cost_function):
    """ Preprocesses data by creating helper submatrices """

    A.add('#')
    strings = get_all_strings(m, A, '#')

    step_vectors_alphabet = [[cost] for cost in range(-step_size_bound,step_size_bound+1)]
    step_vectors = get_all_strings(m, step_vectors_alphabet, [0])

    print("strings: " + str(strings))
    print("step_vectors: " + str(step_vectors))

    storage = {}

    def store(R_new, S_new, C, D, R, S, storage):
        C = C[1:]
        D = D[1:]

        # print("C: " + str(C))
        # print("D: " + str(D))
        # print("R: " + str(R))
        # print("S: " + str(S))
        # print("R_new: " + str(S))
        # print("S_new: " + str(S))

        R = tuple(R[1:])
        S = tuple(S[1:])

        if C not in storage: storage[C] = {}
        if D not in storage[C]: storage[C][D] = {}
        if R not in storage[C][D]: storage[C][D][R] = {}

        storage[C][D][R][S] = (R_new, S_new)

    for C in strings:
        for D in strings:
            for R in step_vectors:
                for S in step_vectors:
                    T = [[0]*(m+1) for _ in range(m+1)]
                    U = [[0]*(m+1) for _ in range(m+1)]

                    # print("T: " + str(T))
                    # print("U: " + str(U))

                    for i in range(1, m+1):
                        T[i][0] = R[i]
                        U[0][i] = S[i]

                    for i in range(1, m+1):
                        for j in range(1, m+1):
                            T[i][j] = min(
                                substitute_cost_function(C[i], D[j]) - U[i - 1][j],
                                delete_cost_function(C[i]),
                                insert_cost_function(D[j]) + T[i][j - 1] - U[i - 1][j])
                            U[i][j] = min(
                                substitute_cost_function(C[i], D[j]) - T[i][j - 1],
                                delete_cost_function(C[i]) + U[i - 1][j] - T[i][j - 1],
                                insert_cost_function(D[j])
                            )

                    R_new = []
                    S_new = []

                    for i in range(1, (m+1)):
                        R_new.append(T[i][m])
                        S_new.append(U[m][i])

                    store(R_new, S_new, C, D, R, S, storage)

    return storage


def algorithm_z(m, text_1, text_2, delete_cost_function, insert_cost_function, storage):
    """ Calculates the edit distance between A and B using preprocessed submatrices of size mxm """

    text_1_parts = int(len(text_1) / m) + 1
    text_2_parts = int(len(text_2) / m) + 1

    P = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

    for i in range(1, text_1_parts):
        P[i][0] = [delete_cost_function(text_1[letter_idx]) for letter_idx in range((i - 1) * m + 1, i * m + 1)]

    Q = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

    for j in range(1, text_2_parts):
        Q[0][j] = [insert_cost_function(text_2[letter_idx]) for letter_idx in range((j - 1) * m + 1, j * m + 1)]

    def fetch(R, S, C, D, storage):
        return storage[C][D][tuple(R)][tuple(S)]

    for i in range(1, text_1_parts):
        for j in range(1, text_2_parts):
            (P[i][j], Q[i][j]) = fetch(P[i][j - 1], Q[i - 1][j], text_1[((i - 1) * m + 1):(i * m+1)],
                                       text_2[((j - 1) * m + 1):(j * m+1)], storage)

    cost = 0

    for i in range(1, text_1_parts):
        cost += sum(P[i][0])

    for j in range(1, text_2_parts):
        cost += sum(Q[int(len(text_1) / m)][j])

    return cost