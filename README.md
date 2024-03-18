# BoardGameGeek_Pipeline

###  Setup

1. Clone the repository
``` terminal
git clone https://github.com/alfredzou/BoardGameGeek_Pipeline.git
```
1.1 set up google account
2. Go to Google Cloud Console (IAM and admin/Service Accounts). Click create new service account called bgg and assign it the Storage Admin & Big Query admin roles
3. In IAM and admin/Service Accounts, click the newly created service account and navigate to KEYS
4. Click "ADD KEY" and create a JSON key. I've renamed the JSON private key as bgg.json
5. Move the saved JSON key to ~/.gcp/bgg.json
5.1 install terraform
5.2 update the variables.tf (project name, region and bucket name). Noting that bucket names must be globally unique
5.3 terraform apply
5.4 create another service account, give it cloud filestore admin and Serverless VPC Access Admin. rename as mage