from __future__ import print_function
import argparse


def main():
    parser = argparse.ArgumentParser(description='This code is written for practice about argparse')
    parser.add_argument('--project-path', type=str, default='/home/jsb/storage/NodeODM/data', help='The project path')
    parser.add_argument('project_name', type=str, default='85331ed4-5687-41df-a842-eec7f39d0aca', help='The project name')
    args = parser.parse_args()

    project_path = args.project_path
    project_name = args.project_name
    rectify(project_path, project_name)


def rectify(path, name):
    print(path, name)


if __name__ == "__main__":
    main()
