#!/usr/bin/env python3.9
import os


def build_cmake_file(project_name: str, file_and_dependencies: dict[str:list]) -> None:
    with open("CMakeLists.txt", 'w') as f:

        f.write("cmake_minimum_required(VERSION 3.5)\n")
        f.write(f"project({project_name})\n")
        f.write("\nif(NOT CMAKE_CXX_STANDARD)\n")
        f.write("\tset(CMAKE_CXX_STANDARD 14)\n")
        f.write("endif()\n")
        f.write(
            "\nif(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES \"Clang\")\n")
        f.write("\tadd_compile_options(-Wall -Wextra -Wpedantic)\n")
        f.write("endif()\n")
        f.write("\nfind_package(ament_cmake REQUIRED)\n")

        """
        There is a more efficient way of writing this - not calling find twice in the same line - but
        the increased cost of using append instead of list comprehension may not only not give a speed up,
        but it might even make it slower for small lists.
        """

        unique_dependencies = set([(item[:item.find("/") if item.find('/') != -1 else len(item)]) for file in
                                   file_and_dependencies.values() for item in file])

        for dependency in unique_dependencies:
            f.write(f"find_package({dependency} REQUIRED)\n")

        f.write("\n")

        for file in file_and_dependencies:
            f.write(f"add_executable({file[:file.index('.')]} src/{file})\n")

        f.write("\n")

        # Can't use f strings here because of the use of the'\'. Have to use "format" instead.
        for file, dependencies in file_and_dependencies.items():
            f.write("ament_target_dependencies({} {})\n".format(file[: file.index('.')], ' '.join(
                [dependency[:dependency.find('/') if dependency.find('/') != -1 else len(dependency)] for dependency in dependencies])))

        f.write("\n")

        for file in file_and_dependencies:
            f.write(
                f"install(TARGETS {file[:file.index('.')]} DESTINATION lib/${{PROJECT_NAME}})\n")

        f.write("\nament_package()")


def main() -> None:
    cwd = os.getcwd().replace('\\', '/')
    # Gets the last index of the '\' character and just sets project_name to everything after the last forwardslash in the directory
    project_name = cwd[len(cwd) - cwd[::-1].index('/'):]
    src_dir = cwd + "/src/"
    file_and_dependencies = {}

    # Loop through the files in the src directory
    for src_file in os.listdir(src_dir):
        # Add an entry to a dictionary
        file_and_dependencies[src_file] = []
        # Open the files to check for dependencies
        with open(src_dir + src_file, 'r') as f:
            for line in f.readlines():
                # Get the lines that include things
                if "#include" in line:
                    file_and_dependencies[src_file].append(
                        line[1 + line.index('<'):-2])

    build_cmake_file(project_name, file_and_dependencies)


if __name__ == "__main__":
    main()
