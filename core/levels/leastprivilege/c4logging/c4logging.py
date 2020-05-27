import random
import os

import google.auth
from googleapiclient import discovery
from google.cloud import storage

from core.framework import levels
from core.framework.cloudhelpers import deployments, iam, cloudfunctions

from cryptography.fernet import Fernet

LEVEL_PATH = 'leastprivilege/c4logging'
RESOURCE_PREFIX = 'c4'
FUNCTION_LOCATION = 'us-central1'
LEVEL_NAME ='logging'


def create():
    # Create randomized bucket name to avoid namespace conflict
    nonce = str(random.randint(100000000000, 999999999999))
    bucket_name = f'{RESOURCE_PREFIX}-bucket-{nonce}'
    

    # Set role of default cloud function account
    credentials, project_id = google.auth.default()
    
    
	
    #Set least privaleges
    fvar2 = Fernet.generate_key()
    f = Fernet(fvar2)
    fvar1 = f.encrypt(b'roles/logging.viewer')
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce}
    template_files = [
        'core/framework/templates/service_account.jinja',
        'core/framework/templates/iam_policy.jinja',
        #'core/framework/templates/cloud_function.jinja',
        'core/framework/templates/bucket_acl.jinja']
    
    deployments.insert(LEVEL_PATH, template_files=template_files,
                       config_template_args=config_template_args)

    print("Level setup started for: " + LEVEL_PATH)
    

    
    # Insert secret into bucket
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    secret = levels.make_secret(LEVEL_PATH)
    secret_blob = storage.Blob(f'secret-{secret}.txt', bucket)
    secret_blob.upload_from_string(secret)  

    sa_key1 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-access')
    sa_key2 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-check')

    func_path1 = f'core/levels/{LEVEL_PATH}/functionaccess'
    func_path2 = f'core/levels/{LEVEL_PATH}/functioncheck'
    func_name1 = f'{func_path1}/{RESOURCE_PREFIX}-access.json'
    func_name2 = f'{func_path2}/{RESOURCE_PREFIX}-check.json'
    
    #write key file in function directory
    with open(func_name1, 'w') as f:
        f.write(sa_key1)
    os.chmod(func_name1, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-access has been written to {func_name1}')
    with open(func_name2, 'w') as f:
        f.write(sa_key2)
    os.chmod(func_name2, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-check has been written to {func_name2}')
    
    
    
    func_upload_url1 = cloudfunctions.upload_cloud_function(func_path1, FUNCTION_LOCATION)
    func_upload_url2 = cloudfunctions.upload_cloud_function(func_path2, FUNCTION_LOCATION)

    config_template_args_patch = {'func_upload_url1':func_upload_url1,'func_upload_url2':func_upload_url2, 'fvar1': fvar1.decode("utf-8"),'fvar2': fvar2.decode("utf-8"),'level_name': LEVEL_NAME,'resource_prefix':RESOURCE_PREFIX }
    config_template_args.update(config_template_args_patch)
    template_files_patch = ['core/framework/templates/cloud_function.jinja']
    template_files.extend(template_files_patch)
    
    deployments.patch(LEVEL_PATH, template_files=template_files, config_template_args=config_template_args)

    print(f'Level creation complete for: {LEVEL_PATH}')
    
    start_message = (
        f"""Find the minimum privilage to list a bucket and access function {RESOURCE_PREFIX}-func-access-{nonce} to check if you have the correct answer\n
        Use function below to access level \n
        https://{FUNCTION_LOCATION}-{project_id}.cloudfunctions.net/{RESOURCE_PREFIX}-func-access-{nonce}
        """)
    levels.write_start_info(
        LEVEL_PATH, start_message, file_name='', file_content='')
    
    
    
   

def destroy():
    # Delete starting files
    levels.delete_start_files()
    actpath1=f'core/levels/{LEVEL_PATH}/functionaccess/{RESOURCE_PREFIX}-access.json'
    # Delete key files
    if os.path.exists(actpath1):
        os.remove(actpath1)
    actpath2=f'core/levels/{LEVEL_PATH}/functioncheck/{RESOURCE_PREFIX}-check.json'
    if os.path.exists(actpath2):
        os.remove(actpath2)
    # Delete deployment
    deployments.delete()
