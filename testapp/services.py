from testapp.models import ReportConfig, EmbedToken, EmbedConfig, EmbedTokenRequestBody
from django.conf import settings
import requests
import json
import msal


class AadService:
    def get_access_token():
        '''Generates and returns Access token
        Returns:
            string: Access token
        '''

        response = None
        try:
            if settings.AUTHENTICATION_MODE.lower() == 'masteruser':

                # Create a public client to authorize the app with the AAD app
                clientapp = msal.PublicClientApplication(settings.CLIENT_ID, authority=settings.AUTHORITY)
                accounts = clientapp.get_accounts(username=settings.POWER_BI_USER)

                if accounts:
                    # Retrieve Access token from user cache if available
                    response = clientapp.acquire_token_silent(settings.SCOPE, account=accounts[0])

                if not response:
                    # Make a client call if Access token is not available in cache
                    response = clientapp.acquire_token_by_username_password(settings.POWER_BI_USER, settings.POWER_BI_PASS, scopes=settings.SCOPE)     

            # Service Principal auth is the recommended by Microsoft to achieve App Owns Data Power BI embedding
            elif settings.AUTHENTICATION_MODE.lower() == 'serviceprincipal':
                authority = settings.AUTHORITY.replace('organizations', settings.TENANT_ID)
                clientapp = msal.ConfidentialClientApplication(settings.CLIENT_ID, client_credential=settings.CLIENT_SECRET, authority=authority)

                # Make a client call if Access token is not available in cache
                response = clientapp.acquire_token_for_client(scopes=settings.SCOPE)

            try:
                return response['access_token']
            except KeyError:
                raise Exception(response['error_description'])

        except Exception as ex:
            raise Exception('Error retrieving Access token\n' + str(ex))

class PbiEmbedService:
    def get_embed_params_for_single_report(self, workspace_id, report_id, user, additional_dataset_id=None):
        '''Get embed params for a report and a workspace
        Args:
            workspace_id (str): Workspace Id
            report_id (str): Report Id
            additional_dataset_id (str, optional): Dataset Id different than the one bound to the report. Defaults to None.
        Returns:
            EmbedConfig: Embed token and Embed URL
        '''

        report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'       
        api_response = requests.get(report_url, headers=self.get_request_header())

        # if api_response.status_code != 200:
        #     abort(api_response.status_code, description=f'Error while retrieving Embed URL\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        report = ReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
        dataset_ids = [api_response['datasetId']]


        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_id is not None:
            dataset_ids.append(additional_dataset_id)

        ## Todo: Use Django ORM and deserialize Model to json
        embed_token = self.get_embed_token_for_single_report_single_workspace(report_id, dataset_ids, user, workspace_id)
        embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, report.__dict__)

        return embed_config
        #return serializers.serialize("json", EmbedConfig.objects.all())

    def get_embed_token_for_single_report_single_workspace(self, report_id, dataset_ids, user, target_workspace_id=None):
        '''Get Embed token for single report, multiple datasets, and an optional target workspace
        Args:
            report_id (str): Report Id
            dataset_ids (list): Dataset Ids
            target_workspace_id (str, optional): Workspace Id. Defaults to None.
        Returns:
            EmbedToken: Embed token
        '''

        request_body = EmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        request_body.reports.append({'id': report_id})

        if target_workspace_id is not None:
            request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Basic usage of roles
        role = 'admin' if user.is_staff else 'user'
        request_body.identities.append({'username': user.username,
                                        'roles': [role, ],
                                        'datasets': dataset_ids
                                        })

        # Generate Embed token for multiple workspaces, datasets, and reports. Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__), headers=self.get_request_header())
        print(api_response)
        # if api_response.status_code != 200:
        #    abort(api_response.status_code, description=f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        embed_token = EmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token
    
    def get_request_header(self):
        '''Get Power BI API request header
        Returns:
            Dict: Request header
        '''

        return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + AadService.get_access_token()}