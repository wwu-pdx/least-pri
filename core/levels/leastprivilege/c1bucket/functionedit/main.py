def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	
	request_json = request.get_json(silent=True)
	request_args = request.args
	if request_json and 'permissions' in request_json:
		permissions = request_json['permissions']
	elif request_args and 'permissions' in request_args:
		permissions = request_args['permissions']
	else:
		permissions = ['cloudfunctions.functions.list', 'storage.buckets.list']
	# Set account key file:
	SERVICE_ACCOUNT_KEY_FILE = 'c1-edit.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	


	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)


	# Build cloudresourcemanager REST API python object
	service = discovery.build('iam','v1', credentials=credentials)


	name = f'projects/{PROJECT_ID}/roles/c1_access_role_{NOUNCE}'  

	role_body = {'includedPermissions': permissions,}

	re = service.projects().roles().patch(name=name, body=role_body).execute()
	return re
