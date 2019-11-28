from __future__ import print_function
import argparse


def main():
    parser = argparse.ArgumentParser(description='This code is written for practice about argparse')
    parser.add_argument('path', type=str,
                        help='The project path')
    args = parser.parse_args()

    path = args.path
    rectify(path)


def rectify(path):
    print(path)


if __name__ == "__main__":
    main()
