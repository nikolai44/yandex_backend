from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.views.decorators.csrf import csrf_exempt
import time

from .models import Citizen, Import

# Create your views here.


def import_validation(data):
	return True


@csrf_exempt
def import_request(request):
	response = {
		"data": {
			"import_id": None
		}
	}
	if request.method != 'POST':
		return HttpResponse(status=400)
	data = json.loads(request.body)
	if import_validation(data) is False:
		return HttpResponse(status=400)

	i = Import.objects.create()
	i.save()
	for citizen in data['citizens']:
		try:
			birth_date = time.strptime(citizen['birth_date'], "%d.%m.%Y")
			birth_date = time.strftime("%Y-%m-%d", birth_date)
			c = Citizen.objects.create(
				citizen_id=citizen['citizen_id'],
				town=citizen['town'],
				street=citizen['street'],
				building=citizen['building'],
				apartment=citizen['apartment'],
				name=citizen['name'],
				gender=citizen['gender'],
				birth_date=birth_date,
				import_group=i,
			)
			c.relatives_add(i, citizen['relatives'])
			c.save()
		except Exception:
			for c in i.citizens.all():
				c.delete()
			i.delete()
			return HttpResponse(status=400)
	response["data"]["import_id"] = i.import_id
	return JsonResponse(response, status=201)


@csrf_exempt
def patch_citizen(request, import_id, citizen_id):
	response = {
		"data": {
			"citizen_id": None,
			"town": None,
			"street": None,
			"building": None,
			"apartment": None,
			"name": None,
			"birth_date": None,
			"gender": None,
			"relatives": None
		}
	}
	if request.method != 'PATCH':
		return HttpResponse(status=400)
	citizen = Citizen.get_citizen_by_import_id_citizen_id(import_id, citizen_id)
	if citizen is None:
		return HttpResponse(status=400)
	data = json.loads(request.body)
	if 'citizen_id' in data.keys():
		citizen.citizen_id = data['citizen_id']
	if 'town' in data.keys():
		citizen.town = data['town']
	if 'street' in data.keys():
		citizen.street = data['street']
	if 'building' in data.keys():
		citizen.building = data['building']
	if 'apartment' in data.keys():
		citizen.apartment = data['apartment']
	if 'name' in data.keys():
		citizen.name = data['name']
	if 'birth_date' in data.keys():
		citizen.birth_date = data['birth_date']
	if 'gender' in data.keys():
		citizen.gender = data['gender']
	if 'relatives' in data.keys():
		citizen.add_relatives_by_import_id(import_id, data['relatives'])
	response['data']['citizen_id'] = citizen.citizen_id
	response['data']['town'] = citizen.town
	response['data']['street'] = citizen.street
	response['data']['building'] = citizen.building
	response['data']['apartment'] = citizen.apartment
	response['data']['name'] = citizen.name
	response['data']['birth_date'] = citizen.birth_date
	response['data']['gender'] = citizen.gender
	response['data']['relatives'] = list(citizen.citizen_id for citizen in citizen.get_relatives())

	citizen.save()
	return JsonResponse(response, status=200)


def get_import(request, import_id):
	response = {
		"data": [
			{}
		]
	}
	citizens = Import.get_citizens_by_import_id(import_id)
	for citizen in citizens:
		pass