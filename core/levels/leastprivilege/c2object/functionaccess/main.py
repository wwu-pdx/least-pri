from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	
	
	# Only one of the following need to be set:
	SERVICE_ACCOUNT_KEY_FILE = 'c2-access.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	FUNCTION_REGION = os.environ['FUNCTION_REGION']
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	


	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	#Build storage REST API python object
	storage_api = discovery.build('storage', 'v1', credentials=credentials)
	name = f'c2-bucket-{NONCE}'
	err=''
	bucket =''
	try:
		request = storage_api.objects().list(bucket=name).execute()["items"][0]
		buckets = name + ' :  ' + request["name"]

	except Exception as e:
		buckets = 'There is an error'
		err = str(e)


	if buckets == '':
		buckets = "No file listed. Insufficient privilege!"
	
	url=f'https://{FUNCTION_REGION}-{PROJECT_ID}.cloudfunctions.net/c2-func-check-{NONCE}'
	
	
	return render_template('c2-access.html', bucket=buckets, url=url, err=err)

	

