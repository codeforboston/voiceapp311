'''
Tools to package and deploy the lambda function for Boston Data app
'''

from __future__ import print_function
import argparse
import os
import pip
import shutil
import zipfile

LAMBDA_FUNCTION_DIR = os.path.join(os.getcwd(), 'lambda_function')

def zip_lambda_function_directory():
    zip_file_name = "lambda_function.zip"
    zip_file = zipfile.ZipFile(zip_file_name, 'w')
    os.chdir(LAMBDA_FUNCTION_DIR)
    for root, dirs, files in os.walk('.'):
        for f in files:
            zip_file.write(os.path.join(root, f))
    zip_file.close()


def install_pip_dependencies():
    requirements_path = os.path.join(LAMBDA_FUNCTION_DIR, "requirements.txt")
    requirements_no_deps_path = os.path.join(LAMBDA_FUNCTION_DIR, "requirements_no_deps.txt")
    install_args = ["install", "-r", requirements_path, "-t" "lambda_function"]
    install_args_no_deps = ["install", "-r", requirements_no_deps_path, "--no-deps", "-t" "lambda_function"]
    pip.main(install_args)
    pip.main(install_args_no_deps)

def cleanup(keep_files):
    """
    Removes everything not contained in keep_files from the
    lambda_function directory.
    """
    print("Cleaning up temporary files/directories...")
    dir_contents = os.listdir(LAMBDA_FUNCTION_DIR)
    for item in dir_contents:
        if os.path.isfile(os.path.join(LAMBDA_FUNCTION_DIR, item)):
            if item not in keep_files:
                os.remove(os.path.join(LAMBDA_FUNCTION_DIR, item))
        if os.path.isdir(os.path.join(LAMBDA_FUNCTION_DIR, item)):
            if item not in keep_files:
                shutil.rmtree(os.path.join(LAMBDA_FUNCTION_DIR, item))
    print("Cleanup complete.")

def package_lambda_function():
    keep_files = os.listdir(LAMBDA_FUNCTION_DIR)
    print("Packaging lambda_function into a deployable zip file...")
    install_pip_dependencies()
    zip_lambda_function_directory()
    cleanup(keep_files)
    print("Packaging complete.")


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
