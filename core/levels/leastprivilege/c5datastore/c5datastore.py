import random
import os

import google.auth
from googleapiclient import discovery
from google.cloud import storage
from google.cloud import datastore

from core.framework import levels
from core.framework.cloudhelpers import deployments, iam, cloudfunctions

from cryptography.fernet import Fernet

LEVEL_PATH = 'leastprivilege/c5datastore'
RESOURCE_PREFIX = 'c5'
FUNCTION_LOCATION = 'us-central1'
LEVEL_NAME ='datastore'
KIND = ''


def create():
    # Create randomized bucket name to avoid namespace conflict
    nonce = str(random.randint(100000000000, 999999999999))
    bucket_name = f'{RESOURCE_PREFIX}-bucket-{nonce}'
    

    # Set role of default cloud function account
    credentials, project_id = google.auth.default()
   
    
    func_path1 = f'core/levels/{LEVEL_PATH}/functionaccess'
    func_path2 = f'core/levels/{LEVEL_PATH}/functioncheck'
    func_name1 = f'{func_path1}/{RESOURCE_PREFIX}-access.json'
    func_name2 = f'{func_path2}/{RESOURCE_PREFIX}-check.json'
    func_upload_url1 = cloudfunctions.upload_cloud_function(func_path1, FUNCTION_LOCATION)
    func_upload_url2 = cloudfunctions.upload_cloud_function(func_path2, FUNCTION_LOCATION)
	
    #Set least privaleges
    fvar2 = Fernet.generate_key()
    f = Fernet(fvar2)
    fvar1 = f.encrypt(b'roles/datastore.viewer')
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce,'func_upload_url1':func_upload_url1,'func_upload_url2':func_upload_url2, 'fvar1': fvar1.decode("utf-8"),'fvar2': fvar2.decode("utf-8"),'level_name': LEVEL_NAME,'resource_prefix':RESOURCE_PREFIX }

    template_files = [
        'core/framework/templates/service_account.jinja',
        'core/framework/templates/iam_policy.jinja',
        'core/framework/templates/cloud_function.jinja']
    deployments.insert(LEVEL_PATH, template_files=template_files,
                       config_template_args=config_template_args)

    print("Level setup started for: " + LEVEL_PATH)
    
    # Create and insert data in datastore
    entities =[{'name': 'admin','password': 'admin1234','active': True},{'name': 'editor','password': '1111','active': True}]
    KIND=f'Users-{nonce}-{project_id}'
    client = datastore.Client()
    for entity in entities:
        entity_key = client.key(KIND)
        task = datastore.Entity(key=entity_key)
        task.update(entity)
        client.put(task)
    print('Datastore entity created')

    sa_key1 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-access')
    sa_key2 = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-check')
    print('Keys generated')
    
    #write key file in function directory
    with open(func_name1, 'w') as f:
        f.write(sa_key1)
    os.chmod(func_name1, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-access has been written to {func_name1}')
    with open(func_name2, 'w') as f:
        f.write(sa_key2)
    os.chmod(func_name2, 0o700)
    print(f'Function file: {RESOURCE_PREFIX}-check has been written to {func_name2}')
    
  
    

    print(f'Level creation complete for: {LEVEL_PATH}')
    
    start_message = (
        f'Find the minimum privilage to list a bucket and access function {RESOURCE_PREFIX}-func-access-{nonce} to check if you have the correct answer')
    levels.write_start_info(
        LEVEL_PATH, start_message, file_name='', file_content='')
    print(f'Step 1.Please use cmd below to update functions and get http trigger url\n gcloud functions deploy {RESOURCE_PREFIX}-func-access-{nonce} --source=core/levels/{LEVEL_PATH}/functionaccess --allow-unauthenticated \n gcloud functions deploy {RESOURCE_PREFIX}-func-check-{nonce} --source=core/levels/{LEVEL_PATH}/functioncheck --allow-unauthenticated ')
    
    print(f'Step 2.Use cmd below to check iam permissions of {RESOURCE_PREFIX}_access \n gcloud iam roles update {RESOURCE_PREFIX}_access_role_{nonce} --project={project_id} --permissions=permission1,permission2\n OR \n gcloud functions call {RESOURCE_PREFIX}-func-check-{nonce} --data \'{{\"permissions\":[\"permission1\",\"permission2\"]}}\' \n OR \n append ?permissions=permission1,permission2 after function url generated in Step 1 ')

    print(f'Step 3.Call {RESOURCE_PREFIX}-func-access-{nonce} with cmd \n gcloud functions call {RESOURCE_PREFIX}-func-access-{nonce} \n OR \n through function url generated in Step 1  \n') 
    
    print(f'Use function below to access level \n') 
    print(f'https://{FUNCTION_LOCATION}-{project_id}.cloudfunctions.net/{RESOURCE_PREFIX}-func-access-{nonce}') 
    
    
   

def destroy():
    #Delete datastore
    print(f'Deleting entities ')
    client = datastore.Client()
    query = client.query(kind=KIND)
    entities = query.fetch()
    for entity in entities:
        client.delete(entity.key)
    print(f'Deleting json key files')
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
