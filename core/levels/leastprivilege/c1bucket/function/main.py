
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	import lst_pri as lst_pri
	
	
	
	# Only one of the following need to be set:
	SERVICE_ACCOUNT_KEY_FILE = 'c1-access.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']


	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	# Change current working directory to top level of repo
	# os.chdir(os.path.dirname(os.getcwd()+'/'+os.path.dirname(__file__)))
	# Load testable permissions into list
	with open('testable-permissions.txt') as f:
		testable_permissions = f.read().split('\n')
	# Split testable permissions list into lists of 100 items each
	chunked_permissions = (
		[testable_permissions[i * 100:(i + 1) * 100] for i in range((len(testable_permissions)+99) // 100)])

	# Build cloudresourcemanager REST API python object
	crm_api = discovery.build('cloudresourcemanager',
							  'v1', credentials=credentials)

	# For each list of 100 permissions, query the api to see if the service account has any of the permissions
	given_permissions = []
	for permissions_chunk in chunked_permissions:
		response = crm_api.projects().testIamPermissions(resource=PROJECT_ID, body={
			'permissions': permissions_chunk}).execute()
		# If the service account has any of the permissions, add them to the output list
		if 'permissions' in response:
			given_permissions.extend(response['permissions'])
	
	given_permissions.sort()
	lst_pri.sort()	
	re='\n'.join(str(x) for x in given_permissions)
	

	
	if given_permissions == lst_pri:
		return "<p>congratulations!</p>"
	else:
		return "<p>Not least privilege, please try again!\n Your current permissions are:\n "+re+"</p>"
