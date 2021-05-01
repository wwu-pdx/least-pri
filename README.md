# Thunder CTF-Least Privilege
## leastprivilege/roles
Least Privilege CTF is an extension of Thunder CTF. Both were built based on Google Cloud Platform. Least Privilege levels have been desgined to help understand Google Cloud Platform's IAM roles and permissions. Related GCP documentaion can be found [here](https://cloud.google.com/iam/docs/understanding-roles). Least Privilege levels do not have "secret". Instead, at each level you should get a success message similar to below:
### Setup:
* First, [create a new google cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) and and enable [billing](https://cloud.google.com/billing/docs/how-to/modify-project) for it. The deployment should ideally be done on a new to ensure that playing the levels won't affect your existing or future work on GCP.  Players new to Google Cloud can get a free $300 credit [here](https://cloud.google.com/free).
* Second, the CTF is played through Cloud Shell which is accessible in the [GCP console](https://console.cloud.google.com) by clicking on the Cloud Shell icon.
![alt text][Icon]

[Icon]:./docs/img/index/cloudshell.png "Cloud Shell Icon"  
Open Cloud Shell and run the following commands to set up the CTF:
```
# Optional: Can skip if cloud shell is started from the project you want to use
gcloud config set project [PROJECT-ID] 
```

```
virtualenv -v env-tctf
source env-tctf/bin/activate
#For reviewers, we suggest you to upload source codes to your own repo or make a copy in Google Cloud Console
git clone https://github.com/[YOUR REPO]/[YOUR-DIRECTORY].git  
cd [YOUR-DIRECTORY]
pip3 install -r requirements.txt
python3 thunder.py activate_project  $GOOGLE_CLOUD_PROJECT
```
A full list of commands can be found by running:
```
python3 thunder.py help
```
### Deploy:
You are now ready to play. Create level with command below:
```
python3 thunder.py create leastprivilege/roles
```
### Level Access:
If deployment is successful, a list of function entrypoints will be printed in Cloud Shell. You can also find them in start/roles.txt . Click each entrypoint link to see its associated level instruction. Note: If level requires creating custom role, you have to create the role with the exact ID specified in level instruction

### Destroy:
Don't forget to destroy levels after you are done using the command below:
```
python3 thunder.py destroy
```

## Other Helpful Info:
* [Understanding Google Cloud IAM Roles](https://cloud.google.com/iam/docs/understanding-roles)
