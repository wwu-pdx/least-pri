import random
import os

import google.auth
from googleapiclient import discovery
from google.cloud import storage

from core.framework import levels
from core.framework.cloudhelpers import deployments, iam, cloudfunctions

LEVEL_PATH = 'leastprivilege/c1bucket'
RESOURCE_PREFIX = 'c1'
FUNCTION_LOCATION = 'us-central1'


def create():
    # Create randomized bucket name to avoid namespace conflict
    nonce = str(random.randint(100000000000, 999999999999))
    bucket_name = f'{RESOURCE_PREFIX}-bucket-{nonce}'
    

    # Set role of default cloud function account
    credentials, project_id = google.auth.default()
    
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce}

    template_files = [
        'core/framework/templates/service_account.jinja',
        'core/framework/templates/iam_policy.jinja',
        'core/framework/templates/bucket_acl.jinja']
    deployments.insert(LEVEL_PATH, template_files=template_files,
                       config_template_args=config_template_args)

    print("Level setup started for: " + LEVEL_PATH)
    

    
    # Insert secret into bucket
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    secret_blob = storage.Blob('secret.txt', bucket)
    secret = levels.make_secret(LEVEL_PATH)
    secret_blob.upload_from_string(secret)  


    print(f'Level creation complete for: {LEVEL_PATH}')
    start_message = (
        f'List bucket content to find the secret')
    levels.write_start_info(
        LEVEL_PATH, start_message, file_name='', file_content='')
    print(f'Instruction for the level can be accessed at thunder-ctf.cloud/levels/{LEVEL_PATH}.html')
    
    
    # Create service account key file
    sa_key = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-access')
    print('key generated')
    #write key file in function directory
    func_path = f'core/levels/{LEVEL_PATH}/function'
    with open(func_path, 'w+') as f:
        f.write(sa_key)
    os.chmod(func_path, 0o400)
    print(f'Function file: {RESOURCE_PREFIX}-access has been written to {func_path}')
    func_upload_url = cloudfunctions.upload_cloud_function(func_path, FUNCTION_LOCATION)
    template_func = ['core/framework/templates/cloud_function.jinja']
    config_template_func = {'nonce': nonce, 'func_upload_url': func_upload_url}
    deployments.insert(LEVEL_PATH, template_files=template_func,config_template_args=config_template_func)
    print(f'Function deployed')

def destroy():
    # Delete starting files
    levels.delete_start_files()
    # Delete deployment
    deployments.delete()
