from django.shortcuts import render ,HttpResponse ,redirect
import pandas as pd
from .models import csv_data
from django.db.models import Q 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required



class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('userdata') 
    template_name = 'account/singup.html'


class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True 

@login_required
def csv_upload(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        try:
            batch_size = 1000 
            csv_reader = pd.read_csv(file, chunksize=batch_size)
            for chunk in csv_reader:
                chunk = chunk.dropna(how='all')
                if chunk.empty:
                    break
                csv_data_list = []
                for _, row in chunk.iterrows():
                    csv_data_list.append(
                        csv_data(
                            name=row['name'],
                            domain=row['domain'],
                            year_founded=row['year founded'],
                            industry=row['industry'],
                            size_range=row['size range'],
                            locality=row['locality'],
                            country=row['country'],
                            linkedin_url=row['linkedin url'],
                            current_employee_estimate=row['current employee estimate'],
                            total_employee_estimate=row['total employee estimate']
                        )
                    )

                csv_data.objects.bulk_create(csv_data_list)

            return HttpResponse("uploaddata")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")
    else:
        return render(request, 'upload.html')
    
    
def search_csv_data(query_params):
    queryset = csv_data.objects.all()
    total_count = queryset.count()  # Initial count of all records

    if 'keyword' in query_params:
        keyword = query_params['keyword']
        queryset_keyword = queryset.filter(
            Q(name__icontains=keyword)
        )
        count_keyword = queryset_keyword.count()
        total_count += count_keyword
        queryset = queryset_keyword

    if 'industry' in query_params:
        queryset_industry = queryset.filter(industry__icontains=query_params['industry'])
        count_industry = queryset_industry.count()
        total_count += count_industry
        queryset = queryset_industry

    if 'year_founded' in query_params:
        queryset_year = queryset.filter(year_founded=query_params['year_founded'])
        count_year = queryset_year.count()
        total_count += count_year
        queryset = queryset_year

    if 'city' in query_params:
        queryset_city = queryset.filter(locality__icontains=query_params['city'])
        count_city = queryset_city.count()
        total_count += count_city
        queryset = queryset_city

    if 'state' in query_params:
        queryset_state = queryset.filter(locality__icontains=query_params['state'])
        count_state = queryset_state.count()
        total_count += count_state
        queryset = queryset_state

    if 'country' in query_params:
        queryset_country = queryset.filter(country__icontains=query_params['country'])
        count_country = queryset_country.count()
        total_count += count_country
        queryset = queryset_country

    if 'employee_from' in query_params:
        queryset_employee_from = queryset.filter(
            total_employee_estimate__gte=query_params['employee_from']
        )
        count_employee_from = queryset_employee_from.count()
        total_count += count_employee_from
        queryset = queryset_employee_from

    if 'employee_to' in query_params:
        queryset_employee_to = queryset.filter(
            total_employee_estimate__lte=query_params['employee_to']
        )
        count_employee_to = queryset_employee_to.count()
        total_count += count_employee_to
        queryset = queryset_employee_to

    results = queryset.values()
    count = queryset.count()

    return results, total_count


def querybuilder(request):
    data = csv_data.objects.all().values('year_founded', 'industry', 'size_range', 'locality', 'country').distinct()

    message = ""

    if request.method == "POST":
        query_params = {
            'keyword': request.POST.get('keyword'),
            'industry': request.POST.get('industry'),
            'year_founded': request.POST.get('year_founded'),
            'city': request.POST.get('locality'),
            'state': request.POST.get('locality'),  
            'country': request.POST.get('country'),
            'employee_from': request.POST.get('employee_from'),
            'employee_to': request.POST.get('employee_to'),
        }

        filtered_data, data_count = search_csv_data(query_params)

        message = f"{data_count} data records found.\n\n"

    messages.info(request, message)

    return render(request, 'quirybuilder.html', {'data': data})

@login_required
def userdata(request):
    user1 = User.objects.all()
    return render(request, "userdata.html", {'user1': user1})

@login_required
def delete_user_by_id(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return redirect('userdata') 
        except User.DoesNotExist:
            pass  
    return redirect('userdata')
