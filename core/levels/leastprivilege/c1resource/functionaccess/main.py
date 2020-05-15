from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	FUNCTION_REGION = os.environ['FUNCTION_REGION']
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	RESOURCE_PREFIX = os.environ.get('RESOURCE_PREFIX', 'Specified environment variable is not set.')

	SERVICE_ACCOUNT_KEY_FILE = f'{RESOURCE_PREFIX}-access.json'
	


	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	#Build resource REST API python object
	resource_api = discovery.build('cloudresourcemanager', 'v2', credentials=credentials)
	err=''
	resources=[]
	try:
		response= resource_api.resources().list(deployment="thunder", project=PROJECT_ID).execute()["resources"]
		for r in response:
			if r["type"] in ["storage.v1.bucket", "compute.v1.instance"]:
				resources.append(r["name"])
	except Exception as e:
		resources = ["There is an error"]
		err = str(e)


	if len(resources) == 0:
		resources = ["No bucket listed. Insufficient privilege!"]
	
	url=f'https://{FUNCTION_REGION}-{PROJECT_ID}.cloudfunctions.net/{RESOURCE_PREFIX}-func-check-{NONCE}'
	
	
	return render_template(f'{RESOURCE_PREFIX}-access.html', bucket=buckets, url=url, err=err,prefix=RESOURCE_PREFIX)

	

