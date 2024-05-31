import pandas as pd
from django.shortcuts import render
from .forms import UploadFileForm
from django.http import JsonResponse
from django.core.exceptions import ValidationError
# Create your views here.


def home(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded.'}, status=400)
        
        file = request.FILES['file']
        
        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            return JsonResponse({'error': 'Unsupported file format. Please upload a CSV or XLS file.'}, status=400)
        
        try:
            summary = handle_uploaded_file(file)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred: ' + str(e)}, status=500)

        if summary is not None:
            return render(request, 'summary.html', {'summary': summary.to_dict('records')})
        else:
            return JsonResponse({'error': 'Unsupported file format. Please upload a CSV or XLS file.'}, status=400)
    
    return render(request, "index.html")




def handle_uploaded_file(file):
    # Determine the file type and read the file into a DataFrame
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
        df = pd.read_excel(file, engine='openpyxl' if file.name.endswith('.xlsx') else 'xlrd')
    else:
        return None
    
    # Rename columns to avoid spaces
    df.rename(columns={'Cust State': 'CustState', 'DPD': 'DPD'}, inplace=True)
    
    # Prepare the summary report
    summary = df.groupby(['CustState', 'DPD']).size().reset_index(name='Count')
    return summary


