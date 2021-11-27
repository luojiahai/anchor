import sys
import anchor.compile as compile


def read_file(file):
    f = open(file, "r", encoding='utf-8')
    data = f.read()
    f.close()
    return data

def main():
    data = read_file(sys.argv[1])
    return compile.execute(data)

main()
