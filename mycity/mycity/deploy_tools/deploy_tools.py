"""
Tools to package and deploy the lambda function for the mycity voice app.
"""

from __future__ import print_function
from subprocess import run, PIPE
import argparse
import os
import shutil
import zipfile
import stat
import errno
import time
import re
import json

# path constants
PROJECT_ROOT = os.path.join(os.getcwd(), os.path.pardir, os.path.pardir)
TEMP_DIR_PATH = os.path.join(PROJECT_ROOT, 'temp')
LAMBDA_REL_PATH = 'platforms/amazon/lambda/custom/lambda_function.py'
LAMBDA_FUNCTION_PATH = os.path.join(PROJECT_ROOT, LAMBDA_REL_PATH)
INTERACTION_MODEL_REL_PATH = 'platforms/amazon/models/en_US.json'
INTERACTION_MODEL_PATH = os.path.join(PROJECT_ROOT, INTERACTION_MODEL_REL_PATH)
MYCITY_PATH = os.path.join(PROJECT_ROOT, 'mycity')
ZIP_FILE_NAME = "lambda_function.zip"
HORIZONTAL_RULE = '* ---------------------------------------'


def zip_lambda_function_directory(zip_target_dir):
    """
    Generates a .zip file containing the contents of the temporary directory
    where the project files have been copied. Note that this .zip file
    must contain the files with no intermediate directory.

    :param zip_target_dir: destination directory for zip file being created
    :return: None
    """
    zip_file = zipfile.ZipFile(os.path.join(zip_target_dir, ZIP_FILE_NAME), 'w')
    original_directory = os.getcwd()
    os.chdir(TEMP_DIR_PATH)
    print('* Compressing lambda_function\n* ', end='')
    for root, dirs, files in os.walk('.'):
        for f in files:
            zip_file.write(os.path.join(root, f))
        for d in dirs:
            print('.', end='', flush=True)
    print('\n* DONE')
    print(HORIZONTAL_RULE)
    zip_file.close()
    os.chdir(original_directory)


def install_pip_dependencies(requirements_path, requirements_path_no_deps):
    """
    Installs all the dependencies for the project's entry point to a
    temporary directory the .zip file is later created from.

    :param requirements_path: path to textfile containing required libraries
    :param requirements_path_no_deps: path to textfile containing required
        libraries (whose dependencies won't be downloaded)
    :return: None
    """
    install_args = [
        "pip",
        "install",
        "-r",
        requirements_path,
        "-t",
        TEMP_DIR_PATH
    ]

    install_args_no_deps = [
        "pip",
        "install",
        "--no-deps",
        "-r",
        requirements_path_no_deps,
        "-t",
        TEMP_DIR_PATH
    ]

    print('* Installing dependencies ...')
    result = run(install_args, stdout=PIPE, stderr=PIPE)
    print_package_names(result.stdout)
    print('* DONE')
    print(HORIZONTAL_RULE)
    print('* Installing dependencies from requirements_no_deps.txt ...')
    result = run(install_args_no_deps, stdout=PIPE, stderr=PIPE)
    print_package_names(result.stdout)
    print('* DONE')
    print(HORIZONTAL_RULE)


def print_package_names(install_output):
    pattern = "Collecting [\w-]+=="
    dependencies = re.findall(pattern, install_output.decode('utf-8'))
    for dependency in dependencies:
        name = dependency[11:len(dependency) - 2]
        print('*   ' + name, end='\n')


def package_lambda_function():
    """
    Creates a temporary directory where the lambda file and all of its
    dependencies are copied before being compressed. Removes the temporary
    directory after creating the .zip file.

    :return: None
    """
    print(HORIZONTAL_RULE)
    print('* Creating temporary build directory ... ')
    # remove/create the temporary directory for the zip file's contents
    if os.path.exists(TEMP_DIR_PATH):
        shutil.rmtree(
            TEMP_DIR_PATH,
            ignore_errors=False,
            onerror=handle_remove_readonly
        )
    os.mkdir(TEMP_DIR_PATH)

    # copy lambda file and mycity directory to temp directory
    shutil.copy(LAMBDA_FUNCTION_PATH, TEMP_DIR_PATH)
    shutil.copytree(MYCITY_PATH, os.path.join(TEMP_DIR_PATH, 'mycity'))

    print('* DONE')
    print(HORIZONTAL_RULE)

    # install dependencies
    install_pip_dependencies(
        os.path.join(os.getcwd(), 'requirements.txt'),
        os.path.join(os.getcwd(), 'requirements_no_deps.txt')
    )

    # build zip file in project root
    zip_lambda_function_directory(PROJECT_ROOT)

    # delete temp directory
    print('* Cleaning up ...')
    shutil.rmtree(
        TEMP_DIR_PATH,
        ignore_errors=False,
        onerror=handle_remove_readonly
    )
    print('* DONE')
    print(HORIZONTAL_RULE)


def update_lambda_code(lambda_function_name, s3_bucket=None):
    """
    Uploads the archive containing our lambda function and dependencies to the
    specified lambda. Requires that the user has configured AWS CLI and that
    the archive exists.

    If the s3_bucket argument is provided, the archive is uploaded to the
    specified s3 bucket and then to the lambda from there.

    :param lambda_function_name:
    :param s3_bucket:
    :return:
    """

    # We only want to attempt to upload if we have a zip file.
    if os.path.isfile(os.path.join(PROJECT_ROOT, ZIP_FILE_NAME)):
        print("* Uploading to Lambda via AWS CLI ...")
        print("*   (please wait, this may take a while)")

        # If the upload fails, catch the exception and alert user.
        try:
            if s3_bucket:
                # The S3 flag was provided, we'll upload to S3 first.
                print("*   UPLOADING TO S3 BUCKET: " + s3_bucket + " ...")
                s3_command_array = [
                    shutil.which("aws"),  # path to user's AWS CLI installation
                    "s3",
                    "cp",
                    PROJECT_ROOT + "/" + ZIP_FILE_NAME,
                    's3://' + s3_bucket + '/' + ZIP_FILE_NAME
                ]
                run(s3_command_array, stdout=PIPE)
                print("*   ...DONE UPLOADING TO S3 BUCKET: " + s3_bucket)
                print("*   UPLOADING TO LAMBDA FROM S3...")

                # modified command array to upload from s3
                update_command_array = [
                    shutil.which("aws"),  # path to user's AWS CLI installation
                    "lambda",
                    "update-function-code",
                    "--function-name",
                    lambda_function_name,
                    "--s3-bucket",
                    s3_bucket,
                    "--s3-key",
                    ZIP_FILE_NAME
                ]
            else:
                # we are uploading to lambda directly
                update_command_array = [
                    shutil.which("aws"),  # path to user's AWS CLI installation
                    "lambda",
                    "update-function-code",
                    "--function-name",
                    lambda_function_name,
                    "--zip-file",
                    "fileb://" + PROJECT_ROOT + "/" + ZIP_FILE_NAME
                ]
            run(update_command_array, stdout=PIPE)
            print("* DONE UPLOADING")
            print(HORIZONTAL_RULE)
        except OSError as e:
            print(
                "! There was a problem uploading to lambda.\n"
                "! Make sure you have configured AWS CLI.\n"
                "! Error output:\n" +
                str(e) + "\n"
            )
    else:
        print("! Unable to upload to Lambda: zip file does not exist.\n")


def update_interaction_model(provided_skill_id):
    """
    Upload the interaction model JSON file stored in
      mycity/platforms/amazon/models/
    to your skill and rebuild the interaction model.

    This is done using the Amazon Skills Kit CLI (ASK CLI), and requires
    setting up the following environment variable in your OS:
      BOSTON_INFO_SKILL_ID
    which contains the skill ID found in the Alexa skills console.

    :param provided_skill_id: The ID of the skill whose interaction model
                              to update.
    :return:
    """
    # Confirm we have a skill ID.
    # Assign the value passed at command line to skill_id
    skill_id = provided_skill_id
    # If no skill ID passed at command line, look for it in environment.
    if skill_id == 'Env_Var':
        if 'BOSTON_INFO_SKILL_ID' in os.environ:
            skill_id = os.environ['BOSTON_INFO_SKILL_ID']
        else:
            print('! Error: Unable to update interaction model.\n'
                  '! Please provide a skill ID with -i or define a\n'
                  '! BOSTON_INFO_SKILL_ID environment variable.')
            print(HORIZONTAL_RULE)
            return
    print("* Updating and rebuilding interaction model via ASK CLI ...")
    # Run the ASK CLI command to update the model.
    try:
        update_command_array = [
            shutil.which("ask"),  # path to user's ASK CLI installation,
            "api",
            "update-model",
            "-s",
            skill_id,
            "-f",
            INTERACTION_MODEL_PATH,
            "-l",
            "en-US"
        ]
        result = run(update_command_array, stdout=PIPE)
        if "Model for en-US submitted" in result.stdout.decode('utf-8'):
            print("* Model for en-US submitted. Building...")
    except OSError as e:
        print(
            "! There was a problem updating the interaction model.\n"
            "! Error output:\n" +
            str(e) + "\n"
        )

    # If the update command was successful, ASK-CLI will immediately kick
    # off a build of the interaction model.
    # We can use ASK-CLI to report on the build's progress.
    build_status_command_array = [
        shutil.which("ask"),  # path to user's ASK CLI installation,
        "api",
        "get-skill-status",
        "-s",
        skill_id
    ]
    result = run(build_status_command_array, stdout=PIPE)
    print("* ", end='', flush=True)
    status = \
        json.loads(result.stdout)['interactionModel']['en-US'][
            'lastUpdateRequest'][
            'status']
    while status != "SUCCEEDED":
        print(".", end='', flush=True)
        time.sleep(1)
        result = run(build_status_command_array, stdout=PIPE)
        status = json.loads(result.stdout)['interactionModel']['en-US'][
            'lastUpdateRequest']['status']
    print("\n* DONE UPLOADING AND BUILDING INTERACTION MODEL")
    print(HORIZONTAL_RULE)


def handle_remove_readonly(func, path, execinfo):
    """
    Passed as the onerror parameter when calling shutil.rmtree.
    See:
    https://stackoverflow.com/a/1214935/2554154
    Handles the case where rmtree fails in Windows due to access problems.

    :param func: function that raised the exception, shutil.rmtree
    :param path: path to temp folder
    :param execinfo: the exception information returned by sys.exc_info()
    :return: None
    :raises: custom exception, temp folder not deleted
    """
    excvalue = execinfo[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        # if we're failing to remove files because they are readonly,
        # update permissions
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise Exception("! Failed to delete temp folder.")
    print('* DONE')
    print(HORIZONTAL_RULE)


def main():
    """
    Defines the command-line option required to initiate building the zipfile.
    Conditionally begins the build process if the required option is present.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Tools to package and deploy the lambda function for " +
                    "the MyCity app."
    )

    parser.add_argument(
        '-p',
        '--package',
        help="Creates a zip file that can be uploaded as an Amazon lambda " +
             "function.",
        action='store_true'
    )

    parser.add_argument(
        '-f',
        '--function',
        help="Provide the function name of your lambda with this option to " +
             "upload the zip file via ASK CLI."
    )

    parser.add_argument(
        '-i',
        '--interaction',
        nargs='?',
        const='Env_Var',
        help="Pass skill id with this flag to upload/build interaction model. " +
             "If no skill ID is provided, attempts to fall back to " +
             "BOSTON_INFO_SKILL_ID environment variable."
    )

    parser.add_argument(
        '-s',
        '--s3bucket',
        help="To upload the Lambda .zip file via an S3 bucket, provide this " +
             "flag followed by the name of your S3 bucket. Recommended for " +
             "slow connections that time out uploading directly to Lambda."
    )

    args = parser.parse_args()

    is_interaction_model_updated = False

    if args.function:
        package_lambda_function()
        update_lambda_code(args.function, args.s3bucket)
    elif args.package:
        package_lambda_function()
    elif args.interaction:
        # Handles the case that we want to update the interaction model without
        # uploading a new lambda zip.
        update_interaction_model(args.interaction)
        is_interaction_model_updated = True
    else:
        print("No known option selected")

    # Handle the interaction model option when we are uploading a zip file.
    if args.interaction and not is_interaction_model_updated:
        update_interaction_model(args.interaction)


if __name__ == "__main__":
    main()
