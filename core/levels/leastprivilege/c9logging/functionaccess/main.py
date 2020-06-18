from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	from google.cloud import logging
	from google.cloud.logging import DESCENDING
	import os
	
	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	FUNCTION_REGION = os.environ['FUNCTION_REGION']
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	RESOURCE_PREFIX = os.environ.get('RESOURCE_PREFIX', 'Specified environment variable is not set.')
	LEVEL_NAME = os.environ.get('LEVEL_NAME', 'Specified environment variable is not set.')

	SERVICE_ACCOUNT_KEY_FILE = f'{RESOURCE_PREFIX}-access.json'
	

	
	
	
	err=[]
	resources = []
	try:
		#Build logging REST API python object
		credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)
		client = logging.Client(credentials=credentials )
		logname = "cloudaudit.googleapis.com%2Factivity"
		filter ="projects.setIamPolicy"
		logger = client.logger(logname)	
		entry = list(logger.list_entries(order_by=DESCENDING, filter_=filter))[0]
		resources.append(entry)

	except Exception as e:
		resources.append('Insufficient privilege!') 
		err.append(str(e))
	
	url=f'https://{FUNCTION_REGION}-{PROJECT_ID}.cloudfunctions.net/{RESOURCE_PREFIX}-func-check-{NONCE}'
	
	
	return render_template(f'{RESOURCE_PREFIX}-access.html', resources=resources, url=url, err=err,prefix=RESOURCE_PREFIX, level_name=LEVEL_NAME,nonce=NONCE)

	

