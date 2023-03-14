import boto3
def verify_email_identity(address, ses_client):
    
    response = ses_client.verify_email_identity(
        EmailAddress=address
    )
    print(response)

def verify_identity(emailaddresses, ses_region):
    ses_client = boto3.client("ses", region_name=ses_region)
    response = ses_client.list_identities( IdentityType='EmailAddress')
    identities=response["Identities"]
    for email in emailaddresses:
        if email not in identities:
            verify_email_identity(email, ses_client)
        else:
            print(f"{email} is already verified")