import argparse
import sys
import math
import copy
from multiprocessing import Pool


def parse_args(args): #the function adds the necessary argumeent line functions to see if there is an input/output file and necessary processes
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--Input", help = "Show input", required = True, type = str)
    parser.add_argument("-o", "--Output", help= "Show output", required = True, type = str)
    parser.add_argument("-p", "--Processes", help= "# of processes to spawn", type = int, default = 1)
    return parser.parse_args(args)

def transfer(input, matr, rows, cols): #function that directly transfers input file info to matrix for manipulation
    clear = ''
    for line in input:
        clear += line.rstrip('\n') #clears the new line characters to create a a list for turning it into a matrix of numbers 
    for i in range(rows):
       for j in range(cols):
        c = clear[(i*cols)+j]
        if(c == 'O'):
            x = 3
        elif(c == 'o'):
            x = 1
        elif(c == 'X'):
            x = -3
        elif(c == 'x'):
            x = -1
        elif(c == '.'):
            x = 0
        matr[i][j] = x   
    return matr

def matr_mani(old, rowSize, colSize, rowId, colID):
    new = [[0 for i in range(colSize+2)] for j in range(rowSize+2)]
    returnedNew = [[0 for i in range(colSize)] for j in range(rowSize)]
    for j in range(1, rowSize + 1):
        for k in range(1, colSize + 1):
            #first sum up neigbhors
            ul = old[j-1][k-1]
            u = old[j-1][k]
            ur = old[j-1][k+1]
            r = old[j][k+1]
            br = old[j+1][k+1]
            b = old[j+1][k]
            bl = old[j+1][k-1]
            l = old[j][k-1]
            sum_n = ul+u+ur+r+br+b+bl+l
            if(old[j][k] == 3):
                #healthy O cells
                fib = {0,1,2,3,5,8,13,21}
                if(sum_n in fib):
                    new[j][k] = 0
                elif(sum_n <12):
                    new[j][k] = 1
                else:
                    new[j][k] = old[j][k]
            elif(old[j][k] == 1):
                #weakened o cells
                if(sum_n < 0):
                    new[j][k] = 0
                elif(sum_n > 6):
                    new[j][k] = 3
                else:
                    new[j][k] = old[j][k]
            elif(old[j][k] == 0):
                #dead cells
                if(sum_n > 0):
                    if(math.log2(sum_n).is_integer()):
                        new[j][k] = 1
                elif(sum_n < 0):
                    if(math.log2(abs(sum_n)).is_integer()):
                        new[j][k] = -1
                else:
                    new[j][k] = old[j][k]
            elif(old[j][k] == -1):
                #weakened x cells 
                if(sum_n >= 1):
                    new[j][k] = 0
                elif(sum_n < -6):
                    new[j][k] = -3
                else:
                    new[j][k] = old[j][k]
            elif(old[j][k] == -3):
                #healthy X cells
                absSum = abs(sum_n)
                isPrime = False 
                if(absSum == 1):
                    isPrime = False
                if (absSum > 1):
                    isPrime = True
                    for i in range(2, int(math.sqrt(absSum)) + 1):
                        if (absSum % i == 0):
                            isPrime = False
                            break
                if(isPrime):
                        new[j][k] = 0
                elif(sum_n > -12):
                    new[j][k] = -1
                else:
                    new[j][k] = old[j][k]
            returnedNew[j-1][k-1] = new[j][k]
    
    return returnedNew
def write_file(matr, out, rows, cols):
    for i in range(rows):
        for j in range(cols):
            if(matr[i][j] == 3):
                x = 'O'
            elif(matr[i][j] == 1):
                x = 'o'
            elif(matr[i][j] == -3):
                x = 'X'
            elif(matr[i][j] == -1):
                x = 'x'
            elif(matr[i][j] == 0):
                x = '.'
            out.write(x)
        out.write('\n')

def main():
    print("Project :: R11706114")
    line_count = 0
    parser = parse_args(sys.argv[1:])
    if (parser.Processes < 1): # check processes command arg 
        print("Error... processes need to be positive")
        sys.exit(1)
    else:
        processes = parser.Processes
    try: #try except finally clauses to open files
        print("Opening files")
        infile = open(parser.Input, "r")
        for line in infile: # to count the number of lines... since all are square rows will = columns = lines
            line_count += 1
        infile.seek(0) # to reset the file pointer to the beginning before calling the transfer function 
        cols = line_count
        rows = line_count
        o_matr = [[0 for i in range(cols)] for j in range(rows)] # original / later old matrix 
        outfile = open(parser.Output, "w")
        transfer(infile, o_matr, rows, cols)
        blockSize = rows // processes

        for i in range(100):
            allBlocks = [] 
            for row_id in range(0, rows, blockSize):
                for col_id in range(0, cols, blockSize):
                    if ((row_id + blockSize) > rows and (col_id + blockSize) > cols): # if the rows and columns extend over the border of the matrix causing OutOfBounds issues
                        RowDifference = rows - (row_id + blockSize) # remaining rows
                        fixedRowSize = blockSize + RowDifference
                        fixedColDif =  cols - (col_id+ blockSize) # remaining cols
                        fixedColSize = blockSize + fixedColDif 
                        block = [[o_matr[(row_id + i - 1)%rows][(col_id + j - 1)%cols] for j in range(fixedColSize + 2)] for i in range(fixedRowSize +2)]
                    elif((row_id + blockSize) > rows): #if it is just rows that overextend
                        RowDifference = rows - (row_id + blockSize) 
                        fixedRowSize = blockSize + RowDifference
                        fixedColSize = blockSize
                        block = [[o_matr[(row_id + i - 1)%rows][(col_id + j - 1)%cols] for j in range(fixedColSize + 2)] for i in range(fixedRowSize +2)]
                    elif((col_id + blockSize) > cols): # just cols overextend
                        fixedRowSize = blockSize
                        fixedColDif =  cols - (col_id+ blockSize)
                        fixedColSize = blockSize + fixedColDif 
                        block = [[o_matr[(row_id + i - 1)%rows][(col_id + j - 1)%cols] for j in range(fixedColSize + 2)] for i in range(fixedRowSize +2)]
                    else: # no out of bounds issues (1, 2, 4,...all other even cuts)
                        fixedColSize = blockSize
                        fixedRowSize = blockSize
                        block = [[o_matr[(row_id+i-1)%rows][(col_id+j-1)%cols] for j in range(fixedColSize + 2)] for i in range(fixedRowSize + 2)]
                    #creates all the blocks with an extra row and column solely to handle the matrix manipulation
                    allBlocks.append((block, fixedRowSize, fixedColSize, row_id, col_id)) 
                    #list of tuples to hold each individual block and its respective dimension and location, horizontally and vertically

            with Pool(processes = processes) as p: 
                result = p.starmap(matr_mani, [(block, fixedRowSize, fixedColSize, row_id, col_id) for block, fixedRowSize, fixedColSize, row_id, col_id in allBlocks])
                #passes each tuple into matr_mani for multiprocessesing 
            for pos, (block, fixedRowSize, fixedColSize, row_id, col_id) in enumerate(allBlocks):
                n = result[pos]
                for i in range(fixedRowSize):
                        for j in range(fixedColSize):
                         o_matr[row_id + i][col_id + j] = n[i][j]
        write_file(o_matr, outfile, rows, cols) # write rebuilt matrix into output 

    except Exception as e:
        print("error: ", e)
    finally:
        print("Closing Files")
        infile.close()
        outfile.close()
    return 0
if __name__ == "__main__":
    main()
