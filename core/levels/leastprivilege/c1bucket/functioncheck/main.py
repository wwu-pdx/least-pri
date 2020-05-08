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
	
	#pri="".join(PRI.split()).split(',')

	credentials = google.oauth2.service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

	# Build cloudresourcemanager REST API python object
	service = discovery.build('cloudresourcemanager','v1', credentials=credentials)
	
	# Service account 
	sa = f'c1-check@{PROJECT_ID}.iam.gserviceaccount.com'

	get_iam_policy_request_body = {}
	
	roles =[]
	pri =[]
	per =[]
	msg = ''
	err=''
	try:
		response = service.projects().getIamPolicy(resource=PROJECT_ID, body=get_iam_policy_request_body).execute()["bindings"]
		for r in response:
			if sa in r['members']:
				roles.append(r['role'])
	except Exception as e: 
		per =[]
		msg ='There is an error'
		err = str(e)
	if len(roles)!=1 or PRI not in roles:
		msg='Not least privilege role, please try again!'
	else:
		msg='Congratulations! You got the least privileges role. '
	
	return render_template('c1-check.html',  per=per, msg=msg, rn=roles[0], err=err)


	# # Build cloudresourcemanager REST API python object
	# service = discovery.build('iam','v1', credentials=credentials)



	# name = f'projects/{PROJECT_ID}/roles/c1_access_role_{NONCE}'  

	# per=[]
	# rolename=''
	# err =''
	# try:
	# 	role = service.projects().roles().get(name=name).execute()
	# 	rolename = role['name']
	# 	#print(roles['name'])
	# 	per = role['includedPermissions']
		
	# except Exception as e: 
	# 	per =[]
	# 	err = str(e)
	
	# msg='Congratulations! You get the least privileges. '
	
	# if len(per)!=len(pri):
	# 	msg='Not least privilege, please try again!'
		
	# else:
	# 	for p in pri:
	# 		if p not in per:
	# 			msg='Not least privilege, please try again!'
	# 			return render_template('c1-check.html',  per=per, msg=msg, rn=rolename, err=err)
	
	# return render_template('c1-check.html',  per=per, msg=msg, rn=rolename, err=err)
