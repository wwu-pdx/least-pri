#Thunder CTF - Least Privilege
## leastprivilege/roles
Least Privilege CTF is an extension of Thunder CTF. Both were built based on Google Cloud Platform. Least Privilege levels have been desgined to help understand Google Cloud Platform's IAM roles and permissions. Related GCP documentaion can be found [here](https://cloud.google.com/iam/docs/understanding-roles). Least Privilege levels do not have "secret". Instead, at each level you should get a success message similar to below:
### Setup:
* First, [create a new google cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) and and enable [billing](https://cloud.google.com/billing/docs/how-to/modify-project) for it. The deployment should ideally be done on a new to ensure that playing the levels won't affect your existing or future work on GCP.  Players new to Google Cloud can get a free $300 credit [here](https://cloud.google.com/free).
* Second, the CTF is played through Cloud Shell which is accessible in the [GCP console](https://console.cloud.google.com) by clicking on the Cloud Shell icon.
![alt text][Icon]

[Icon]:./docs/img/index/cloudshell.png "Cloud Shell Icon"  
Open Cloud Shell and run the following commands to set up the CTF:
   
