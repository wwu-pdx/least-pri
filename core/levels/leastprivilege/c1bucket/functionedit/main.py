def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	
	# request_json = request.get_json(silent=True)
	# request_args = request.args
	# if request_json and 'permissions' in request_json:
		# permissions = request_json['permissions']
	# elif request_args and 'permissions' in request_args:
		# permissions = request_args['permissions'].split(',')
	# else:
		# #Set to oringal permissions
		# permissions = ['storage.buckets.list','storage.objects.list','storage.buckets.delete','iam.roles.get']
	# Set account key file:
	SERVICE_ACCOUNT_KEY_FILE = 'c1-edit.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']

	# Get function env variable
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	

	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)


	# Build cloudresourcemanager REST API python object
	service = discovery.build('iam','v1', credentials=credentials)


	name = f'projects/{PROJECT_ID}/roles/c1_access_role_{NONCE}'  

	per=''
	try:
		roles = service.projects().roles().get(name=name).execute()
		per=roles['name']+':  '
		print(roles['name'])
		for permission in roles['includedPermissions']:
			per += permission+'   '
			print(permission)
	except Exception as e: 
		per =str(e)
	return per
