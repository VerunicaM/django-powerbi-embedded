from django.shortcuts import render
from django.conf import settings
from testapp.models import *
from testapp.services import PbiEmbedService
from django.http import JsonResponse
from django.views.generic import TemplateView
from testapp.models import Report


# Create your views here.
def index(request):
    reports = Report.objects.all()
    return render(request, 'testapp/index.html', context={"reports": reports})

def get_embed_info(request):
    '''Returns report embed configuration'''

    try:
        workspace_id = request.GET.get('workspace_id')
        report_id = request.GET.get('report_id')
        embed_info = PbiEmbedService().get_embed_params_for_single_report(workspace_id=workspace_id, report_id=report_id, user=request.user)
        return JsonResponse(embed_info.__dict__)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

class ReportView(TemplateView):
    template_name = 'testapp/report.html'