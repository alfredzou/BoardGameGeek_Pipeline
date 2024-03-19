# BoardGameGeek_Pipeline

###  Setup

1. Clone the repository
``` terminal
git clone https://github.com/alfredzou/BoardGameGeek_Pipeline.git
```
1.1 set up google account
2. Go to Google Cloud Console (IAM and admin/Service Accounts). Click create new service account called gcs_bq and assign it the Storage Admin & BigQuery Admin roles
3. In IAM and admin/Service Accounts, click the newly created service account and navigate to KEYS
4. Click "ADD KEY" and create a JSON key. I've renamed the JSON private key as gcs_bq.json
5. Move the saved JSON key to ~/.gcp/gcs_bq.json
5.1 install terraform
5.2 update the variables.tf (project name, region and bucket name). Noting that bucket names must be globally unique
5.25 terraform init
5.3 terraform apply
5.4 create another service account, give it cloud filestore admin and Serverless VPC Access Admin. rename as mage
5.5 enable these apis
Cloud Resource Manager API
Compute Engine API
Identity and Access Management (IAM) API	
Serverless VPC Access API

5.6 secret manager
5.7 create secret call it gcs_bq. upload file which is your gcs_bq.json file.
5.8 IAM give your default Compute Engine default service account Secret Manager Secret Accessor

