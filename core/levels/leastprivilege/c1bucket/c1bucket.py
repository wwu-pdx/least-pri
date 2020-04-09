import random
import os

import google.auth
from googleapiclient import discovery
from google.cloud import storage

from core.framework import levels
from core.framework.cloudhelpers import deployments, iam, cloudfunctions

from cryptography.fernet import Fernet

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
	
    #Set least privaleges
    fvar2 = Fernet.generate_key()
    f = Fernet(fvar2)
    fvar1 = f.encrypt(b'storage.buckets.list ')
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce,'func_upload_url1':func_upload_url1,'func_upload_url2':func_upload_url2,'fvar1': fvar1.decode("utf-8"),'fvar2': fvar2.decode("utf-8") }

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
    #funeold = open(funcepath,'r')
    #text = funeold.read().replace('{NOUNCE}',nonce)
    #funeold.close()
    #neweold = open(funcepath,'w')
    #neweold.write(text)
    #neweold.close()

    print(f'Level creation complete for: {LEVEL_PATH}')
    
    start_message = (
        f'Find the minimum privilage to list a bucket and access function c1-func-access-{nonce} to check if you have the correct answer')
    levels.write_start_info(
        LEVEL_PATH, start_message, file_name='', file_content='')
    print(f'Step 1.Please use cmd below to update functions and get http trigger url\n gcloud functions deploy c1-func-access-{nonce} --source=core/levels/leastprivilege/c1bucket/functionaccess --allow-unauthenticated \n gcloud functions deploy c1-func-edit-{nonce} --source=core/levels/leastprivilege/c1bucket/functionedit --allow-unauthenticated ')
    
    print(f'Step 2.Use cmd below to edit iam permissions of c1_access \n gcloud iam roles update c1_access_role_{nonce} --project={project_id} --permissions=permission1,permission2\n OR \n gcloud functions call c1-func-edit-{nonce} --data \'{{\"permissions\":[\"permission1\",\"permission2\"]}}\'')

    print(f'Step 3.Call c1-func-access-{nonce} with cmd \n gcloud functions call c1-func-access-{nonce} \n OR \n use url generated in step 1 and append ?permissions=permission1,permission2 \n') 
    
    
   

def destroy():
    # Delete starting files
    levels.delete_start_files()
    actpath1=f'core/levels/{LEVEL_PATH}/functionaccess/{RESOURCE_PREFIX}-access.json'
    # Delete key files
    if os.path.exists(actpath1):
        os.remove(actpath1)
    actpath2=f'core/levels/{LEVEL_PATH}/functionedit/{RESOURCE_PREFIX}-edit.json'
    if os.path.exists(actpath2):
        os.remove(actpath2)
    # Delete deployment
    deployments.delete()
