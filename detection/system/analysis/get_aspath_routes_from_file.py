import pandas as pd
from io import StringIO
import re

def load_bgp_table_file(filename):

    flag = False
    file_lines = []

    with open(filename, 'r') as f:
        for line in f:
            #print(line)
            if flag and ('>' in line):
                file_lines.append(line.strip('\n'))

            if 'Network' in line:
                #print(line)
                file_lines.append(line.replace('   Network','').strip('\n'))
                flag = True

    return '\n'.join(file_lines)



def get_aspath_routes(address_prefix, ):
    pass

if __name__ == '__main__':

    #print(os.path.dirname(__file__))
    #print(os.path.relpath(os.getcwd()))
    bgp_file = r"D:\Documents\open university\netSeminar\source\detection\system\sensor\bgp_table.txt"
    data = load_bgp_table_file(bgp_file)
    print(data)

    # Read using whitespace delimiter
    df = pd.read_csv(StringIO(data), delim_whitespace=True)

    print(df)

    #address_prefix: str = '198.18.1.13'
    #get_aspath_routes(address_prefix)