from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.oauth2.service_account
	from google.oauth2.credentials import Credentials
	import os
	from cryptography.fernet import Fernet

	SERVICE_ACCOUNT_KEY_FILE = 'c1-check.json'

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']

	# Get function env variable
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	

	key = os.environ.get('fvar2', 'Specified environment variable is not set.').encode("utf-8") 
	fvar1 = os.environ.get('fvar1', 'Specified environment variable is not set.').encode("utf-8") 
	f = Fernet(key)
	PRI = f.decrypt(fvar1).decode("utf-8") 
	
	pri="".join(PRI.split()).split(',')
	#pri.sort()

	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)


	# Build cloudresourcemanager REST API python object
	service = discovery.build('iam','v1', credentials=credentials)


	name = f'projects/{PROJECT_ID}/roles/c1_access_role_{NONCE}'  

	per=[]
	rolename=''
	try:
		roles = service.projects().roles().get(name=name).execute()
		rolename = roles['name']
		#print(roles['name'])
		per = roles['includedPermissions']
		# for permission in roles['includedPermissions']:
			# per += permission+'   '
			# #print(permission)
	except Exception as e: 
		per =str(e)
	
	msg='Congratulations! You get the least privileges. '
	
	if len(per)!=len(pri):
		msg='Not least privilege, please try again!'
		
	else:
		for p in pri:
			if p not in per:
				msg='Not least privilege, please try again!'
				return render_template('c1-check.html', pri=pri, per=per, msg=msg, rn=rolename)
	# if ''.join(per) == ''.join(pri):
		# msg='Congratulations! You get the least privileges. '
	# else:
		# msg='Not least privilege, please try again!'

	return render_template('c1-check.html', pri=pri, per=per, msg=msg, rn=rolename)
