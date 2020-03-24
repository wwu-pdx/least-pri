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
    # Create service account key file
    
    func_path1 = f'core/levels/{LEVEL_PATH}/functionaccess'
    func_path2 = f'core/levels/{LEVEL_PATH}/functionedit'
    func_name1 = f'{func_path1}/{RESOURCE_PREFIX}-access.json'
    func_name2 = f'{func_path2}/{RESOURCE_PREFIX}-edit.json'
    func_upload_url1 = cloudfunctions.upload_cloud_function(func_path1, FUNCTION_LOCATION)
    func_upload_url2 = cloudfunctions.upload_cloud_function(func_path2, FUNCTION_LOCATION)
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce,'func_upload_url1':func_upload_url1,'func_upload_url2':func_upload_url2}

    template_files = [
        'core/framework/templates/service_account.jinja',
        'core/framework/templates/iam_policy.jinja',
        'core/framework/templates/cloud_function.jinja',
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

    sa_key1 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-access')
    sa_key2 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-edit')
    print('keys generated')
    
    #write key file in function directory
    with open(func_name1, 'w') as f:
        f.write(sa_key1)
    os.chmod(func_name1, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-access has been written to {func_name1}')
    with open(func_name2, 'w') as f:
        f.write(sa_key2)
    os.chmod(func_name2, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-edit has been written to {func_name2}')
    
    funcepath= f'core/levels/{LEVEL_PATH}/functionedit/main.py'
    funeold = open(funcepath,'r')
    text = funeold.read().replace('{NOUNCE}',nonce)
    funeold.close()
    neweold = open(funcepath,'w')
    neweold.write(text)
    neweold.close()

    print(f'Level creation complete for: {LEVEL_PATH}')
    
    start_message = (
        f'Find the minimum privilage to list a bucket')
    levels.write_start_info(
        LEVEL_PATH, start_message, file_name='', file_content='')
    print(f'use cmd below to update deploy/update function')
    print(f'gcloud functions deploy c1-func-access-{nonce} --source=core/levels/leastprivilege/c1bucket/functionaccess')
    print(f'gcloud functions deploy c1-func-edit-{nonce} --source=core/levels/leastprivilege/c1bucket/functionedit')
    print(f'use code below to edit iam permissions')
    print(f'gcloud iam roles update c1_access_role_{nonce} --project={project_id} --permissions=permission1,permission2')
    
    
   

def destroy():
    # Delete starting files
    levels.delete_start_files()
    actpath1=f'core/levels/{LEVEL_PATH}/functionaccess/{RESOURCE_PREFIX}-access.json'
    if os.path.exists(actpath1):
        os.remove(actpath1)
    actpath2=f'core/levels/{LEVEL_PATH}/functionedit/{RESOURCE_PREFIX}-edit.json'
    if os.path.exists(actpath2):
        os.remove(actpath2)
    # Delete deployment
    deployments.delete()
