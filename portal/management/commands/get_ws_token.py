import globus_sdk
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

# Setup your client at http://developers.globus.org You may use the following
# id for testing.
CLIENT_ID = '795b3536-ad58-4dd5-96f8-499922258a60'

# Requested Scope from Globus Genomics
REQUESTED_SCOPES = ['https://auth.globus.org/scopes/'
                    'ebcaf30d-8148-4f1b-992a-bd089f823ac7/workspace_manager']
REDIRECT_URI = 'https://auth.globus.org/v2/web/auth-code'


class Command(BaseCommand):
    help = 'Request a workspace manager token, for testing the api'

    def handle(self, *args, **options):
        client = globus_sdk.NativeAppAuthClient(client_id=CLIENT_ID)
        # pass refresh_tokens=True to request refresh tokens
        client.oauth2_start_flow(requested_scopes=REQUESTED_SCOPES,
                                 redirect_uri=REDIRECT_URI,
                                 refresh_tokens=True)

        url = client.oauth2_get_authorize_url()

        print('Native App Authorization URL: \n{}'.format(url))

        # Support both python2 and python3
        get_input = getattr(__builtins__, 'raw_input', input)

        auth_code = get_input('Enter the auth code: ').strip()

        token_response = client.oauth2_exchange_code_for_tokens(auth_code)
        tokens = token_response.by_resource_server
        print('Workspace Manager Token {}'.format(
            tokens['fair_research_data_portal']['access_token']))
