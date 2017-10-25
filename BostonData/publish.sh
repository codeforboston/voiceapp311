rm lambda_function.zip
python deploy_tools.py -p
aws lambda update-function-code --function-name BostonData --zip-file fileb://lambda_function.zip
