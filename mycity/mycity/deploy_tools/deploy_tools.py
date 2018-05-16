'''
Tools to package and deploy the lambda function for Boston Data app.
'''

from __future__ import print_function
import argparse
import os
import pip
import shutil
import subprocess
import zipfile

# TODO: This needs to be updated to give user some idea of how to run it and where to run it from
PROJECT_ROOT = os.path.join(os.getcwd(), os.pardir, os.pardir)
TEMP_DIR_PATH = os.path.join(PROJECT_ROOT, 'temp')
LAMBDA_REL_PATH = 'platforms/amazon/lambda/custom/lambda_function.py'
LAMBDA_FUNCTION_PATH = os.path.join(PROJECT_ROOT, LAMBDA_REL_PATH)
MYCITY_PATH = os.path.join(PROJECT_ROOT, 'mycity')

INSTALL_REQUIREMENTS_SCRIPT = os.path.join(os.getcwd(), 'install_requirements.sh')


def zip_lambda_function_directory(zip_target_dir):
    """
    Generates a .zip file containing the contents of the temporary directory
    where the project files have been copied. Note that this .zip file
    contains the files with no intermediate directory.

    :param zip_target_dir: destination directory for zip file being created
    :return: none
    """
    # TODO: revise this to avoid changing directory
    os.chdir(zip_target_dir)
    zip_file_name = "lambda_function.zip"
    zip_file = zipfile.ZipFile(zip_file_name, 'w')
    os.chdir(TEMP_DIR_PATH)
    print('Compressing ', end='')
    for root, dirs, files in os.walk('.'):
        for f in files:
            zip_file.write(os.path.join(root, f))
            print('.', end='')
    print('DONE')
    zip_file.close()


def install_pip_dependencies(requirements_path, requirements_path_no_deps):
    """
    Wraps both _install_pip_dependencies. pip version is checked in this
    function so correct install function is called.

    if pip version >= '10.0.0', we should install from script
    else, install using pip.main

    :param requirements_path: path to textfile containing required libraries
    :param requirements_path_no_deps: path to textfile containing required
        libraries (whose dependencies won't be downloaded)
    :return: none
    """
    version = pip.__version__
    if version >= '10.0.0':
        _install_pip_dependencies_from_script()
    else:
        _install_pip_dependencies(requirements_path, requirements_path_no_deps)


def _install_pip_dependencies(requirements_path, requirements_path_no_deps):
    """
    Uses requirements.txt to install all external libraries used by the project
    in the temporary directory the .zip file is created from.

    :param requirements_path: path to textfile containing required libraries
    :param requirements_path_no_deps: path to textfile containing required
        libraries (whose dependencies won't be downloaded)
    :return: none
    """
    print('Installing dependencies ... ', end='')
    install_args = "pip install -r " + requirements_path + " -t " + TEMP_DIR_PATH
    pip.main(install_args)
    print('Installing dependencies from requirements_no_deps.txt ...', end='')
    install_args_no_deps = ("pip install --no-deps -r ",
                            requirements_paths_no_deps,
                            " -t ", 
                            TEMP_DIR_PATH)
    pip.main(install_args_no_deps)
    print('DONE')


def _install_pip_dependencies_from_script():
    """
    pip.main is deprecated in the latest version of pip. If pip is version 10.0.0 
    or later, we can install our dependencies using a shell script

    :return: none
    """
    print('Installing dependencies ... ', end='')
    subprocess.call(INSTALL_REQUIREMENTS_SCRIPT)
    print('DONE')


def package_lambda_function():
    """
    Creates a temporary directory where the lambda file and all of its
    dependencies are copied before being compressed. Removes the temporary
    directory after creating the .zip file.

    :return: none
    """
    print('Creating temporary build directory ... ', end='')
    # create the temporary directory for the zip file's contents
    os.mkdir(TEMP_DIR_PATH)
    # copy the lambda file, mycity files, and requirements.txt to temp directory
    shutil.copy(LAMBDA_FUNCTION_PATH, TEMP_DIR_PATH)
    shutil.copytree(MYCITY_PATH, os.path.join(TEMP_DIR_PATH, 'mycity'))
    requirements_path = os.path.join(os.getcwd(), 'requirements.txt')
    requirements_path_no_deps = os.path.join(os.getcwd(), 'requirements_no_deps.txt')
    shutil.copy(requirements_path, TEMP_DIR_PATH)
    print('DONE')
    # install dependencies
    install_pip_dependencies(requirements_path, requirements_path_no_deps)
    # build zip file in project root
    zip_lambda_function_directory(PROJECT_ROOT)
    # delete temp directory
    print('Cleaning up ... ', end='')
    shutil.rmtree(TEMP_DIR_PATH)
    print('DONE')


def main():
    """
    Defines the command-line option required to initiate building the zipfile.
    Conditionally begins the build process if the required option is present.

    :return: none
    """
    parser = argparse.ArgumentParser(description="Tools to " +
        "package and deploy the lambda function for Boston Data app")

    parser.add_argument('-p', '--package', help="Creates a zip file " +
        "that can be uploaded as an Amazon lambda function",
        action='store_true')

    args = parser.parse_args()

    if args.package:
        package_lambda_function()
    else:
        print("No known option selected")


if __name__ == "__main__":
    main()
