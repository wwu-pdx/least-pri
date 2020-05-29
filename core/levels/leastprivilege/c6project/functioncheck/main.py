from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	from cryptography.fernet import Fernet

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	
	# Get function env variable
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	RESOURCE_PREFIX = os.environ.get('RESOURCE_PREFIX', 'Specified environment variable is not set.')
	LEVEL_NAME = os.environ.get('LEVEL_NAME', 'Specified environment variable is not set.')
	

	key = os.environ.get('fvar2', 'Specified environment variable is not set.').encode("utf-8") 
	fvar1 = os.environ.get('fvar1', 'Specified environment variable is not set.').encode("utf-8") 
	f = Fernet(key)
	PRI = f.decrypt(fvar1).decode("utf-8") 
	
	#pri="".join(PRI.split()).split(',')

	SERVICE_ACCOUNT_KEY_FILE = f'{RESOURCE_PREFIX}-check.json'

	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	# Build cloudresourcemanager REST API python object
	service_r = discovery.build('cloudresourcemanager','v1', credentials=credentials)
	
	#role name
	role_name = f'projects/{PROJECT_ID}/roles/{RESOURCE_PREFIX}_access_role_{NONCE}'

	permissions = []
	msg = ''
	err=''

	try:
		role = service.projects().roles().list(name=name).execute()
		permissions = role['includedPermissions']
	except Exception as e: 
		permissions =[]
		msg ='There is an error'
		err = str(e)

		
		
	# Build iam  REST API python object
	service_i = discovery.build('iam','v1', credentials=credentials)

	
	try:
		permissions = service_i.roles().get(name=roles[0]).execute()["includedPermissions"]
		
		
	except Exception as e: 
		permissions =[]
		err = str(e)
	
	return render_template(f'{RESOURCE_PREFIX}-check.html',  pers=permissions, msg=msg, rn=role_name, err=err,prefix=RESOURCE_PREFIX, level_name=LEVEL_NAME)