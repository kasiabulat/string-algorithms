import math


class four_russians_helpers:
    def __init__(self, delete_cost_function, insert_cost_function, substitute_cost_function):
        self.delete_cost_function = delete_cost_function
        self.insert_cost_function = insert_cost_function
        self.substitute_cost_function = substitute_cost_function

    def prepare_parameters(self, text_1, text_2):
        A = sorted(list(set(list(text_1[1:] + text_2[1:]))))

        def get_parameter(text_1):
            return int(math.log2(len(text_1) - 1))

        def get_step_size_bound():
            I = max([self.insert_cost_function(letter_idx) for letter_idx in A])
            D = max([self.delete_cost_function(letter_idx) for letter_idx in A])
            return max(I, D)

        m = get_parameter(text_1)
        step_size_bound = get_step_size_bound()

        text_1_mod = (len(text_1) - 1) % m
        if text_1_mod != 0: text_1 += '#' * (m - (text_1_mod))

        text_2_mod = (len(text_2) - 1) % m
        if text_2_mod != 0: text_2 += '#' * (m - (text_2_mod))

        return m, A, step_size_bound, text_1, text_2

    def get_all_strings(self, m, A, dumb_letter):
        """ Returns all possible strings of a given length """

        sub_length_results = [[] for _ in range(m + 1)]
        sub_length_results[0] = []
        sub_length_results[1] = [letter for letter in A]

        for size in range(2, m + 1):
            sub_length_results[size] = []
            for left_substring in sub_length_results[1]:
                for right_substring in sub_length_results[size - 1]:
                    sub_length_results[size].append(left_substring + right_substring)

        result = [dumb_letter + word for word in sub_length_results[m]]
        return result

    def store(self, R_new, S_new, C, D, R, S, storage):
        R = tuple(R)
        S = tuple(S)

        if C not in storage: storage[C] = {}
        if D not in storage[C]: storage[C][D] = {}
        if R not in storage[C][D]: storage[C][D][R] = {}

        storage[C][D][R][S] = (R_new, S_new)

    def fetch(self, C, D, R, S, storage):
        return storage[C][D][tuple(R)][tuple(S)]

    def print_2dim_array(self, array):
        for row in array:
            print(row)

    def algorithm_y(self, m, A, step_size_bound):
        """ Preprocesses data by creating helper submatrices """

        A = ['#'] + A
        strings = self.get_all_strings(m, A, '#')

        step_vectors_alphabet = [[cost] for cost in range(-step_size_bound, step_size_bound + 1)]
        step_vectors = self.get_all_strings(m, step_vectors_alphabet, [0])

        storage = {}

        for C in strings:
            for D in strings:
                for R in step_vectors:
                    for S in step_vectors:
                        T = [[0] * (m + 1) for _ in range(m + 1)]
                        U = [[0] * (m + 1) for _ in range(m + 1)]

                        for i in range(1, m + 1):
                            T[i][0] = R[i]
                            U[0][i] = S[i]

                        for i in range(1, m + 1):
                            for j in range(1, m + 1):
                                T[i][j] = min(
                                    self.substitute_cost_function(C[i], D[j]) - U[i - 1][j],
                                    self.delete_cost_function(C[i]),
                                    self.insert_cost_function(D[j]) + T[i][j - 1] - U[i - 1][j])
                                U[i][j] = min(
                                    self.substitute_cost_function(C[i], D[j]) - T[i][j - 1],
                                    self.delete_cost_function(C[i]) + U[i - 1][j] - T[i][j - 1],
                                    self.insert_cost_function(D[j])
                                )

                        R_new = []
                        S_new = []

                        for i in range(1, (m + 1)):
                            R_new.append(T[i][m])
                            S_new.append(U[m][i])

                        self.store(R_new, S_new, C[1:], D[1:], R[1:], S[1:], storage)

        return storage

    def get_text_parts(self, m, text_1):
        return int(len(text_1) / m) + 1

    def algorithm_z(self, m, storage, text_1, text_2):
        """ Returns step vectors needed to calculate the edit distance between A and B using preprocessed submatrices of size mxm """

        text_1_parts = self.get_text_parts(m, text_1)
        text_2_parts = self.get_text_parts(m, text_2)

        P = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

        for i in range(1, text_1_parts):
            P[i][0] = [self.delete_cost_function(text_1[letter_idx]) for letter_idx in
                       range((i - 1) * m + 1, i * m + 1)]

        Q = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

        for j in range(1, text_2_parts):
            Q[0][j] = [self.insert_cost_function(text_2[letter_idx]) for letter_idx in
                       range((j - 1) * m + 1, j * m + 1)]

        for i in range(1, text_1_parts):
            for j in range(1, text_2_parts):
                (P[i][j], Q[i][j]) = self.fetch(self.get_kth_substring(i, m, text_1),
                                                self.get_kth_substring(j, m, text_2), P[i][j - 1], Q[i - 1][j], storage)

        return P, Q

    def restore_matrix(self, C, D, R, S, m):
        M = [[0] * (m + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            M[i][0] = R[i]
            M[0][i] = S[i]
        for i in range(1, m + 1):
            for j in range(1, m + 1):
                M[i][j] = min(
                    self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1],
                    self.delete_cost_function(C[i]) + M[i - 1][j],
                    self.insert_cost_function(D[j]) + M[i][j - 1]
                )
        return M

    def restore_lcs_part(self, C, D, R, S, m, i1, j1):
        M = self.restore_matrix(C, D, R, S, m)

        # print("M:")
        # self.print_2dim_array(M)

        i = i1
        j = j1

        lcs = ""

        while i != 0 and j != 0:
            # print("M["+str(i)+"]["+str(j)+"]")
            # print(M[i][j])
            # print("substitute")
            # print(self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1])
            # print("delete")
            # print(self.delete_cost_function(C[i]) + M[i - 1][j])
            # print("insert")
            # print(self.insert_cost_function(D[j]) + M[i][j - 1])

            if M[i][j] == self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1]:
                if C[i] == D[j]:
                    lcs += C[i]
                i = i - 1
                j = j - 1
            elif M[i][j] == self.delete_cost_function(C[i]) + M[i - 1][j]:
                i = i - 1
            elif M[i][j] == self.insert_cost_function(D[j]) + M[i][j - 1]:
                j = j - 1
            else:
                # print("M[" + str(i) + "][" + str(j) + "]")
                # print(M[i][j])
                # print("substitute")
                # print(self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1])
                # print("delete")
                # print(self.delete_cost_function(C[i]) + M[i - 1][j])
                # print("insert")
                # print(self.insert_cost_function(D[j]) + M[i][j - 1])
                # if i == 1: i = 0
                # if j == 1: j = 0
                pass
        return lcs, i, j

    def get_kth_substring(self, k, m, text_1):
        return text_1[((k - 1) * m + 1):(k * m + 1)]

    def restore_lcs(self, text_1, text_2, P, Q, m):
        lcs = ""

        # indices on the matrix of submatrices
        I = int(len(text_1) / m)
        J = int(len(text_2) / m)

        # indices inside of the submatrices
        i = m
        j = m

        while I != 1 or J != 1:
            print("I", I)
            print("J", J)

            C = '#'+self.get_kth_substring(I, m, text_1)
            D = '#'+self.get_kth_substring(J, m, text_2)

            print("C: ", C)
            print("D: ", D)

            lcs_part, i, j = self.restore_lcs_part(C, D, [0]+P[I][J], [0]+Q[I][J], m, i, j)

            print("lcs_part: ",lcs_part)
            print("i: ",i)
            print("j: ",j)

            if i == 0 and j == 0:
                prev_C = '#'+self.get_kth_substring(I - 1, m, text_1)
                prev_D = '#'+self.get_kth_substring(J - 1, m, text_2)

                upper_left_matrix = self.restore_matrix(prev_C, prev_D, [0]+P[I - 1][J - 1], [0]+Q[I - 1][J - 1], m)

                left_matrix_upper_initial = [upper_left_matrix[k][m - 1] for k in range(0, m)]
                left_matrix = self.restore_matrix(C, prev_D, [0]+P[I][J - 1], [0]+left_matrix_upper_initial, m)

                upper_matrix_left_initial = [upper_left_matrix[m - 1][k] for k in range(0, m)]
                upper_matrix = self.restore_matrix(prev_C, D, [0]+upper_matrix_left_initial, [0]+Q[I - 1][J], m)

                substitute_cost = self.substitute_cost_function(C[1], D[1]) + upper_left_matrix[m - 1][m - 1]
                delete_cost = self.delete_cost_function(C[1]) + upper_matrix[m - 1][0]
                insert_cost = self.insert_cost_function(D[1]) + left_matrix[0][m - 1]

                minimum = min(substitute_cost, delete_cost, insert_cost)

                if minimum == substitute_cost:
                    if C[1] == D[1]:
                        lcs += C[1]
                        print("C[i]:",C[1])
                    I = I - 1
                    J = J - 1
                    i = m
                    j = m
                elif minimum == delete_cost:
                    I = I - 1
                    i = m
                elif minimum == insert_cost:
                    J = J - 1
                    j = m
            elif i == 1:
                I = I - 1
                i = m
            elif j == 1:
                J = J - 1
                j = m

            lcs += lcs_part

        # reverse result:
        return lcs[::-1]

    def get_edit_distance(self, m, text_1, text_2, storage):
        P, Q = self.algorithm_z(m, storage, text_1, text_2)

        cost = 0

        for i in range(1, self.get_text_parts(m, text_1)):
            cost += sum(P[i][0])

        for j in range(1, self.get_text_parts(m, text_2)):
            cost += sum(Q[int(len(text_1) / m)][j])

        return cost

    def get_lcs(self, m, text_1, text_2, storage):
        P, Q = self.algorithm_z(m, storage, text_1, text_2)
        lcs = self.restore_lcs(text_1, text_2, P, Q, m)
        return lcs, len(lcs)
