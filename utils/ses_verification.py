import boto3
ses_client = boto3.client("ses", region_name="us-east-1")
def verify_email_identity(address):
    
    response = ses_client.verify_email_identity(
        EmailAddress=address
    )
    print(response)

def verify_identity(emailaddresses):
    response = ses_client.list_identities( IdentityType='EmailAddress')
    identities=response["Identities"]
    print(identities)
    for email in emailaddresses:
        if email not in identities:
            verify_email_identity(email)
        else:
            print(f"{email} is already verified")