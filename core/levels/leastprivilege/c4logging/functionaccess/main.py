from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	from google.cloud import logging
	import os

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	FUNCTION_REGION = os.environ['FUNCTION_REGION']
	NONCE = '{{nonce}}'
	RESOURCE_PREFIX = '{{resource_prefix}}'
	LEVEL_NAME = '{{level_name}}'

	SERVICE_ACCOUNT_KEY_FILE = f'{RESOURCE_PREFIX}-access.json'
	


	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	#Build logging REST API python object
	client = logging.Client(credentials=credentials )
	name = f'{RESOURCE_PREFIX}-bucket-{NONCE}'
	err=[]
	resources = []
	try:
		logger = client.logger('log_name')
		for entry in logger.list_entries():
			resources.append(entry)

	except Exception as e:
		resources.append('Insufficient privilege!') 
		err.append(str(e))
	
	url=f'https://{FUNCTION_REGION}-{PROJECT_ID}.cloudfunctions.net/{RESOURCE_PREFIX}-func-check-{NONCE}'
	
	
	return render_template(f'{RESOURCE_PREFIX}-access.html', resources=resources, url=url, err=err,prefix=RESOURCE_PREFIX, level_name=LEVEL_NAME)

	

