class HdmInconsistency:
    def tround(self, num, place):
        num += pow(0.1, place+4)
        return round(num, place)
    
    def make_matrix_a(self, resp_data):
        temp_list = resp_data.split("|")
        n_fact = {20:5, 12:4, 6:3}
        matrix_size = n_fact[len(temp_list)]
        
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)]
        for idx, tl in enumerate(temp_list):
            pair_data = tl.split(",")
    
            # first item
            if idx % 2 == 0:
                col_1st = int(pair_data[0][-1:]) - 1
                pair_1st_val = int(pair_data[2])
                
            # second item
            else:
                col_2nd = int(pair_data[0][-1:]) - 1
                row_2nd = col_1st
                row_1st = col_2nd
                pair_2nd_val = pair_data[2]
                matrix[row_1st][col_1st] = int(pair_1st_val)
                matrix[row_2nd][col_2nd] = int(pair_2nd_val)
            
        return matrix
    
    
    def make_matrix_b(self, matrix_a, matrix_size):
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)]
        
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = self.tround(matrix_a[i][j]/matrix_a[j][i], 2)
        return matrix
    
    
    def make_matrix_c(self, matrix_b, matrix_size):
        matrix = [[0 for col in range(matrix_size-1)] for row in range(matrix_size)]
        
        for i in range(matrix_size):
            for j in range(matrix_size-1):
                matrix[i][j] = self.tround(matrix_b[i][j]/matrix_b[i][j+1], 2)
        return matrix
    
    
    def step5_normalize(self, matrix_mean, matrix_size):
        norm_val = [0 for i in range(matrix_size)]
        norm_val[3] = 1
        norm_val[2] = self.tround(matrix_mean[2], 2)
        norm_val[1] = self.tround(norm_val[2] * matrix_mean[1], 2)
        norm_val[0] = self.tround(norm_val[1] * matrix_mean[0], 2)
        
        sum_val = 0.0
        for val in norm_val:
            sum_val += val
            
        for idx, val in enumerate(norm_val):
            norm_val[idx] = self.tround(val / sum_val, 2)
        
        return norm_val    

def main():
    str_al = 'CR111,A,40|CR112,B,60|CR114,D,57|CR113,C,43|CR113,C,75|CR111,A,25|CR112,B,38|CR114,D,62|CR111,A,20|CR114,D,80|CR112,B,50|CR113,C,50'
    n_fact = {20:5, 12:4, 6:3, 2:2}
    matrix_size = n_fact[len(str_al.split("|"))]
    
    hdm_inc = HdmInconsistency()
    
    matrix_a = hdm_inc.make_matrix_a(str_al)
    matrix_b = hdm_inc.make_matrix_b(matrix_a, matrix_size)
    matrix_c = hdm_inc.make_matrix_c(matrix_b, matrix_size)
    matrix_mean = hdm_inc.make_mean_list(matrix_c, matrix_size)
    
    print(matrix_mean)

if __name__ == "__main__":
    main()