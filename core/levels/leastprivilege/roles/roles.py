import random
import os

import google.auth
from googleapiclient import discovery
from google.cloud import storage

from core.framework import levels
from core.framework.cloudhelpers import deployments, iam, cloudfunctions

from cryptography.fernet import Fernet

LEVEL_PATH = 'leastprivilege/roles'
#RESOURCE_PREFIX = 'c6'
FUNCTION_LOCATION = 'us-central1'
#LEVEL_NAME ='project'
LEVEL_NAMES = {'pr':'projects','pd1':'storage'}
fvars = {'pr':'roles/viewer',
         'pd1':'roles/storage.objectViewer'
         #{'ct1':['storage.buckets.list','compute.instances.list']}
        }

def create():

    # Create randomized bucket name to avoid namespace conflict
    nonce = str(random.randint(100000000000, 999999999999))
    bucket_name_pd1 = f'pd1-bucket-{nonce}'
    

    # Set role of default cloud function account
    credentials, project_id = google.auth.default()

   
    
    print("Level initialization finished for: " + LEVEL_PATH)
    # Insert deployment
    config_template_args = {'nonce': nonce}

    template_files = [
        'core/framework/templates/service_account.jinja',
        'core/framework/templates/iam_policy.jinja',
        'core/framework/templates/bucket_acl.jinja',
        'core/framework/templates/ubuntu_vm.jinja']

    deployments.insert(LEVEL_PATH, template_files=template_files,
                       config_template_args=config_template_args)

    print("Level setup started for: " + LEVEL_PATH)
    
    # Insert secret into bucket
    storage_client = storage.Client()
    secret = levels.make_secret(LEVEL_PATH)
    bucket_pd1 = storage_client.get_bucket(bucket_name_pd1)
    secret_blob_pd1 = storage.Blob('secret_pd1.txt', bucket_pd1)
    secret_blob_pd1.upload_from_string(secret)

    
    template_files_patch = ['core/framework/templates/cloud_function.jinja']
    template_files.extend(template_files_patch)
    print( 'Use function entrypoints below to access levels')

    for RESOURCE_PREFIX in LEVEL_NAMES:

        LEVEL_NAME = LEVEL_NAMES[RESOURCE_PREFIX]
        fvar = fvars[RESOURCE_PREFIX]

        #print(f'Level creation for: {LEVEL_PATH}/{RESOURCE_PREFIX}/{LEVEL_NAME}')
        #Generate account key files
        sa_keya = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-access')
        sa_keyc = iam.generate_service_account_key(f'{RESOURCE_PREFIX}-check')
        
        func_patha = f'core/levels/{LEVEL_PATH}/{RESOURCE_PREFIX}/functionaccess'
        func_pathc = f'core/levels/{LEVEL_PATH}/{RESOURCE_PREFIX}/functioncheck'
        func_namea = f'{func_patha}/{RESOURCE_PREFIX}-access.json'
        func_namec = f'{func_pathc}/{RESOURCE_PREFIX}-check.json'

        #write key file in function directory
        with open(func_namea, 'w') as f:
            f.write(sa_keya)
        os.chmod(func_namea, 0o700)
        #print(f'Function file: {RESOURCE_PREFIX}-access has been written to {func_namea}')
        with open(func_namec, 'w') as f:
            f.write(sa_keyc)
        os.chmod(func_namec, 0o700)
        #print(f'Function file: {RESOURCE_PREFIX}-check has been written to {func_namec}')
        
        #Generate function urls
        func_template_argsc = {'fvar': fvar}
        func_upload_urla = cloudfunctions.upload_cloud_function(func_patha, FUNCTION_LOCATION)
        func_upload_urlc = cloudfunctions.upload_cloud_function(func_pathc, FUNCTION_LOCATION,template_args=func_template_argsc)
        
        #Update deployment with functions
        config_template_args_patch = {f'funca_upload_url_{RESOURCE_PREFIX}':func_upload_urla, f'funcc_upload_url_{RESOURCE_PREFIX}':func_upload_urlc, 
                                       
                                        f'level_name_{RESOURCE_PREFIX}': LEVEL_NAME, f'resource_prefix_{RESOURCE_PREFIX}':RESOURCE_PREFIX }
        config_template_args.update(config_template_args_patch)
        
        print(
            f"""
            https://{FUNCTION_LOCATION}-{project_id}.cloudfunctions.net/{RESOURCE_PREFIX}-f-access-{nonce}
            """)
        
    deployments.patch(LEVEL_PATH, template_files=template_files, config_template_args=config_template_args)
    print('Patching completed')

def destroy():
    # Delete starting files
    levels.delete_start_files()
    for RESOURCE_PREFIX in LEVEL_NAMES:
        actpatha=f'core/levels/{LEVEL_PATH}/{RESOURCE_PREFIX}/functionaccess/{RESOURCE_PREFIX}-access.json'
        # Delete key files
        if os.path.exists(actpatha):
            os.remove(actpatha)
        actpathc=f'core/levels/{LEVEL_PATH}/{RESOURCE_PREFIX}/functioncheck/{RESOURCE_PREFIX}-check.json'
        if os.path.exists(actpathc):
            os.remove(actpathc)
    # Delete deployment
    deployments.delete()
