import sys
from interfaces.cli import cli


def main():
    from utils.dependencies import check_dependencies
    if not check_dependencies():
        sys.exit(1)
    
    cli()


if __name__ == '__main__':
    main()
