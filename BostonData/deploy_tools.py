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
    requirements_path = os.path.join("lambda_function", "requirements.txt")
    install_args = ["install", "-r", requirements_path, "-t" "lambda_function"]
    pip.main(install_args)

def cleanup():
    """
    Removes everything except lambda_function.py and requirements.txt
    from the lambda_function directory.
    """
    keep_files = ['requirements.txt', 'lambda_function.py']
    for root, dirs, files in os.walk(LAMBDA_FUNCTION_DIR):
        for name in files:
            if name not in keep_files:
                os.remove(os.path.join(root, name))
        for name in dirs:
            shutil.rmtree(os.path.join(root, name))


def package_lambda_function():
    print("Packaging lambda_function into a deployable zip file...\n")
    install_pip_dependencies()
    zip_lambda_function_directory()
    cleanup()


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
