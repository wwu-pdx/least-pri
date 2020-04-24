from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	from cryptography.fernet import Fernet
	
	# Only one of the following need to be set:
	SERVICE_ACCOUNT_KEY_FILE = 'c1-access.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	
	# Get function env variable
	key = os.environ.get('fvar2', 'Specified environment variable is not set.').encode("utf-8") 
	fvar1 = os.environ.get('fvar1', 'Specified environment variable is not set.').encode("utf-8") 
	f = Fernet(key)
	PRI = f.decrypt(fvar1).decode("utf-8") 

	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	#Build storage REST API python object
	storage_api = discovery.build('storage', 'v1', credentials=credentials)
	try:
		buckets = storage_api.buckets().list(project=PROJECT_ID).execute()["items"][0]["name"]
	except:
		buckets = ''
	
	given_permissions.sort()	
	re=',\n'.join(str(x) for x in given_permissions)
	
	pri="".join(PRI.split()).split(',')
	pri.sort()

	if buckets == '':
		return "No bucket listed. Insufficient privilege!\n Your current testable permissions are:\n ["+re+"]"
	
	return render_template('c1.html', pri=pri, buckets=buckets)

