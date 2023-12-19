from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.core.serializers import serialize
import requests
import pandas as pd
from bs4 import BeautifulSoup
from .models import District,Province,Municipality

def municipality_list(request):
    url = 'https://www.nepalgov.com/list-of-municipalities-and-rural-municipalities-english/#'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    table1 = soup.find('table', id='tablepress-4')
    headers = ['Province', 'District', 'Name', 'Type']

    mydata = pd.DataFrame(columns=headers)

    for j in table1.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(mydata)
        mydata.loc[length] = row
    mydata['District'] = mydata['District'].str.title()
    for index, row in mydata.iterrows():
            district_name=row['District']
            district_object=District.objects.get(name=district_name)
            Municipality.objects.create(
            name= row['Name'],
            district=district_object,
            type= row['Type'],
            )
    return HttpResponse("Data scraped and saved successfully!")


def get_district(request,id):
    import json
    districts = District.objects.filter(province_id=id)
    data_json = serialize('json', districts)
    data_list = json.loads(data_json)
    data = [{'id': item['pk'], 'name': item['fields']['name']} for item in data_list]
    # data = [{'id': district, 'name': district} for district in districts]
    
    return JsonResponse(data, safe=False)

def get_municipality(request, id):
    import json
    municipalities = Municipality.objects.filter(district_id=id)
    data_json = serialize('json', municipalities)
    data_list = json.loads(data_json)
    data = [{'id': item['pk'], 'name': item['fields']['name']} for item in data_list]
    return JsonResponse(data, safe=False)

        
