class four_russians:
    def __init__(self, delete_cost_function, insert_cost_function, substitute_cost_function):
        self.delete_cost_function = delete_cost_function
        self.insert_cost_function= insert_cost_function
        self.substitute_cost_function = substitute_cost_function

    def get_all_strings(self, m, A, dumb_letter):
        """ Returns all possible strings of a given length """

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


    def algorithm_y(self, m, A, step_size_bound):
        """ Preprocesses data by creating helper submatrices """

        A.add('#')
        strings = self.get_all_strings(m, A, '#')

        step_vectors_alphabet = [[cost] for cost in range(-step_size_bound,step_size_bound+1)]
        step_vectors = self.get_all_strings(m, step_vectors_alphabet, [0])

        print("strings: " + str(strings))
        print("step_vectors: " + str(step_vectors))

        storage = {}

        def store(R_new, S_new, C, D, R, S, storage):
            C = C[1:]
            D = D[1:]

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

                        for i in range(1, m+1):
                            T[i][0] = R[i]
                            U[0][i] = S[i]

                        for i in range(1, m+1):
                            for j in range(1, m+1):
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

                        for i in range(1, (m+1)):
                            R_new.append(T[i][m])
                            S_new.append(U[m][i])

                        store(R_new, S_new, C, D, R, S, storage)

        return storage


    def restore_lcs_part(self, R, S, C, D, m, i1, j1):
        # Restore submatrix

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

        i = i1
        j = j1

        lcs = ""

        while i != 0 or j != 0:
            if M[i][j] == self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1]:
                if C[i] == D[j]:
                    lcs += C[i]
                i = i-1
                j = j-1
            elif M[i][j] == self.delete_cost_function(C[i]) + M[i - 1][j]:
                i = i - 1
            elif M[i][j] == self.insert_cost_function(D[j]) + M[i][j - 1]:
                j = j - 1

        return lcs, i, j


    def restore_lcs(self, text_1, text_2):
        pass


    def algorithm_z(self, m, text_1, text_2, storage):
        """ Calculates the edit distance between A and B using preprocessed submatrices of size mxm """

        text_1_parts = int(len(text_1) / m) + 1
        text_2_parts = int(len(text_2) / m) + 1

        P = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

        for i in range(1, text_1_parts):
            P[i][0] = [self.delete_cost_function(text_1[letter_idx]) for letter_idx in range((i - 1) * m + 1, i * m + 1)]

        Q = [[[] for _ in range(text_2_parts)] for _ in range(text_1_parts)]

        for j in range(1, text_2_parts):
            Q[0][j] = [self.insert_cost_function(text_2[letter_idx]) for letter_idx in range((j - 1) * m + 1, j * m + 1)]

        def fetch(R, S, C, D, storage):
            return storage[C][D][tuple(R)][tuple(S)]

        for i in range(1, text_1_parts):
            for j in range(1, text_2_parts):
                (P[i][j], Q[i][j]) = fetch(P[i][j - 1], Q[i - 1][j], text_1[((i - 1) * m + 1):(i * m+1)],
                                           text_2[((j - 1) * m + 1):(j * m+1)], storage)

        # P, Q - matrices with step vectors

        cost = 0

        for i in range(1, text_1_parts):
            cost += sum(P[i][0])

        for j in range(1, text_2_parts):
            cost += sum(Q[int(len(text_1) / m)][j])

        return cost