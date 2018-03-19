'''
Tools to package and deploy the lambda function for Boston Data app
'''

from __future__ import print_function
import argparse
import os
import pip
import shutil
import zipfile

PROJECT_ROOT = os.path.join(os.getcwd(), os.pardir, os.pardir)
TEMP_DIR_PATH = os.path.join(PROJECT_ROOT, 'temp')
LAMBDA_REL_PATH = 'platforms/amazon/lambda/custom/lambda_function.py'
LAMBDA_FUNCTION_PATH = os.path.join(PROJECT_ROOT, LAMBDA_REL_PATH)
MYCITY_PATH = os.path.join(PROJECT_ROOT, 'mycity')


def zip_lambda_function_directory(zip_target_dir):
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


def install_pip_dependencies(requirements_path):
    print('Installing dependencies ... ', end='')
    install_args = ["install", "-r", requirements_path, "-t", TEMP_DIR_PATH]
    pip.main(install_args)
    print('DONE')

#
# def cleanup(keep_files):
#     """
#     Removes everything not contained in keep_files from the
#     lambda_function directory.
#     """
#     print("Cleaning up temporary files/directories...")
#     dir_contents = os.listdir(LAMBDA_FUNCTION_DIR)
#     for item in dir_contents:
#         if os.path.isfile(os.path.join(LAMBDA_FUNCTION_DIR, item)):
#             if item not in keep_files:
#                 os.remove(os.path.join(LAMBDA_FUNCTION_DIR, item))
#         if os.path.isdir(os.path.join(LAMBDA_FUNCTION_DIR, item)):
#             if item not in keep_files:
#                 shutil.rmtree(os.path.join(LAMBDA_FUNCTION_DIR, item))
#     print("Cleanup complete.")


def package_lambda_function():
    print('Creating temporary build directory ... ', end='')
    # create the temporary directory for the zip file's contents
    os.mkdir(TEMP_DIR_PATH)
    # copy the lambda file, mycity files, andrequirements.txt to temp directory
    shutil.copy(LAMBDA_FUNCTION_PATH, TEMP_DIR_PATH)
    shutil.copytree(MYCITY_PATH, os.path.join(TEMP_DIR_PATH, 'mycity'))
    requirements_path = os.path.join(os.getcwd(), 'requirements.txt')
    shutil.copy(requirements_path, TEMP_DIR_PATH)
    print('DONE')
    # install dependencies
    install_pip_dependencies(requirements_path)
    # build zip file in project root
    zip_lambda_function_directory(PROJECT_ROOT)
    # delete temp directory
    print('Cleaning up ... ', end='')
    shutil.rmtree(TEMP_DIR_PATH)
    print('DONE')


def main():
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
