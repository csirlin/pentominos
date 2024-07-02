import pickle
import re
from generate_cnf import *

# read in the map and output file
m = pickle.load(open('mapper5x12.pkl', 'rb'))
f = open('test_out.txt', 'r')
result = f.read()

# reduce string to just the result
result_index = result.find('[ result ]')
profiling_index = result.find('[ profiling ]')
start_index = result.find('c', result_index)
end_index = result.rfind('c', None, profiling_index)
result = result[start_index:end_index]

# replace alphanumeric characters with nothing
result = re.sub(r'[a-zA-z]', '', result)
result = re.sub(r'\n', ' ', result)
result = re.sub(r'-[0-9]+', '', result)
result = re.sub(r' +', ' ', result)
# print(result)
# remove leading and trailing whitespace
result = result.strip()
result_list = result.split(' ')
print(result_list)
print("m.G = ", m.G)
print("m.N = ", m.N)

answer_list = [0]*m.G

for i in range(len(result_list)):
    if 1 <= int(result_list[i]) <= m.G * m.N:
        pent, pos = m.get_assignment_from_num(int(result_list[i]))
        print(result_list[i], pent, pos)
        if answer_list[pos] != 0:
            print(f'Error: answer_list[{pos}] already has value {answer_list[pos]}, but trying to assign new value {pent}')
        answer_list[pos] = pent

for i in range(len(answer_list)):
    print(f'{i+1}: {answer_list[i]}')
