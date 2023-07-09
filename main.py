from core import Core 

# Main functions 
if __name__ == '__main__':
    core = Core(len(sys.argv) >= 2 and sys.argv[1] == 'dog')
    core.start()