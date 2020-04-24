
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
	
	# Load testable permissions into list
	with open('testable-permissions.txt') as f:
		testable_permissions = f.read().split('\n')
	# Split testable permissions list into lists of 100 items each
	chunked_permissions = (
		[testable_permissions[i * 100:(i + 1) * 100] for i in range((len(testable_permissions)+99) // 100)])

	# Build cloudresourcemanager REST API python object
	crm_api = discovery.build('cloudresourcemanager','v1', credentials=credentials)

	# For each list of 100 permissions, query the api to see if the service account has any of the permissions
	given_permissions = []
	for permissions_chunk in chunked_permissions:
		try:
			response = crm_api.projects().testIamPermissions(resource=PROJECT_ID, body={'permissions': permissions_chunk}).execute()
			# If the service account has any of the permissions, add them to the output list
			if 'permissions' in response:
				given_permissions.extend(response['permissions'])
		except:
			print(permissions_chunk)
	
	given_permissions.sort()	
	re=',\n'.join(str(x) for x in given_permissions)
	
	pri="".join(PRI.split()).split(',')
	pri.sort()

	if buckets == '':
		return "No bucket listed. Insufficient privilege!\n Your current testable permissions are:\n ["+re+"]"
	
	

	if ''.join(given_permissions) == ''.join(pri):
		return "Bucket name : \n"+buckets+"\n Congratulations!\n Your current testable permissions are:\n ["+re+"]"
	else:
		return "Bucket name : \n"+buckets+"\n Not least privilege, please try again!\n Your current testable permissions are:\n ["+re+"]"

