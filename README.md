# django-powerbi-embedded

An example of how Power BI Embedded can be integrated into a Django application. This project is based on the official Microsoft flask developer sample that you can find [here](https://github.com/microsoft/PowerBI-Developer-Samples/tree/master/Python/Embed%20for%20your%20customers/AppOwnsData).


### Requirements

1. Python 3
4. Azure tenant
5. A Power BI workspace with at least one report 


### Set up a Power BI app

Follow the steps on [aka.ms/EmbedForCustomer](https://aka.ms/embedforcustomer)


### Usage

This application is capable of serving multiple Power BI Reports. To do so, you have to add reports to the database according to the model defined in [testapp/models.py](./testapp/models.py). In addition, the application uses a simple row level security (RLS) model that defines the *admin* and *user* roles. For this it is necessary to define these roles in the reports you are about to embedd as well. If you don't know how to do this, please refer to the official Microsoft [documentation](https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-rls) on RLS in Power BI. If RLS is not desired, simply comment out lines *100* to *105* in the [testapp/services.py](testapp/services.py) file.

Finally you have to define these environment variables:

- DJANGO_SECRET_KEY 
- AZURE_CLIENT_SECRET 
- AZURE_TENANT_ID 
- AZURE_CLIENT_ID

If you do not want to use environment variables in your [pbi_embedded/settings.py](./pbi_embedded/settings.py) file, you can replace every `os.environ["YOUR_ENVIRONMENT_VARIABLE"]` with hardcoded variables, but please keep in mind that you should not do this in a production environment.


### Contribute

I welcome contributions to django-powerbi-embedded. If you have a bug fix or new feature that you would like to contribute, please fork the repository and submit a pull request.