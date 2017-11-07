'''
Created on Oct 23, 2017

@author: Jacob
'''
import unittest


class Test(unittest.TestCase):

    def step1_matrix_a1(self, resp_data):
        temp_list = resp_data.split("|")
        fact_size_dic = {30:6, 20:5, 12:4, 6:3}
        row_size_dic = {6:15, 5:10, 4:6, 3:3}
        matrix_size = fact_size_dic[len(temp_list)]
        matrix_pair = [0 for i in range(row_size_dic[matrix_size])]
        matrix_pair
        
        temp_list = resp_data.split("|")
        list_idx = 0
        temp_dic = {}
        for idx, tl in enumerate(temp_list):
            pair_data = tl.split(",")
        
            res_id = int(pair_data[0][-1:]) - 1
            res_val = int(pair_data[2])
            temp_dic[res_id] = res_val
        
            # second item
            if idx % 2 != 0:
                matrix_pair[list_idx] = temp_dic
                temp_dic = {} 
                list_idx += 1
            
        return matrix_pair

    def step1_matrix_a2(self, idx0, idx1, idx2, idx3, matrix_pair):
        matrix_size_dic = {15:6, 10:5, 6:4, 3:3}
        pair_size = len(matrix_pair)
        matrix_size = matrix_size_dic[len(matrix_pair)]
        
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)] 
        for idx in range(pair_size):
            temp_pair = matrix_pair[idx]
            print("*"*80)
            for i in temp_pair.keys():
                print("key:" + str(i))
                print("val:" + str(temp_pair[i]))
                # matrix[idx0][idx0]            

    def testName(self):
        str_al = 'CR111,A,40|CR112,B,60|CR114,D,57|CR113,C,43|CR113,C,75|CR111,A,25|CR112,B,38|CR114,D,62|CR111,A,20|CR114,D,80|CR112,B,50|CR113,C,50'
        print(self.step1_matrix_a1(str_al))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
