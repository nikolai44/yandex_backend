from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
import json
from django.views.decorators.csrf import csrf_exempt
import time
import numpy as np

from .models import Citizen, Import


def date_to_another_format(date, from_format, to_format):
	try:
		default_date = time.strptime(date, from_format)
		return time.strftime(to_format, default_date)
	except Exception:
		ValueError


@csrf_exempt
def post_import(request):
	response = {
		"data": {
			"import_id": None
		}
	}
	if request.method != 'POST':
		return HttpResponse("Импорт. Метод не 'POST", status=400)
	data = json.loads(request.body)
	i = Import.objects.create()
	i.save()
	for citizen in data['citizens']:
		try:
			c = Citizen.objects.create(
				citizen_id=citizen['citizen_id'],
				town=citizen['town'],
				street=citizen['street'],
				building=citizen['building'],
				apartment=citizen['apartment'],
				name=citizen['name'],
				gender=citizen['gender'],
				birth_date=date_to_another_format(citizen['birth_date'], "%d.%m.%Y", "%Y-%m-%d"),
				import_group=i,
			)
			c.add_relatives(i, citizen['relatives'])
			c.full_clean()
			c.save()
		except ValidationError or ValueError or Exception as err:
			for c in i.citizens.all():
				c.delete()
			i.delete()
			return HttpResponse(err, status=400)
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
			"relatives": None,
		}
	}
	if request.method != 'PATCH':
		return HttpResponse("Патч. Метод не 'POST'", status=400)
	citizen = Citizen.get_citizen_by_import_id_citizen_id(import_id, citizen_id)
	if citizen is None:
		return HttpResponse(status=400)
	data = json.loads(request.body)
	if 'citizen_id' in data:
		citizen.citizen_id = data['citizen_id']
	if 'town' in data:
		citizen.town = data['town']
	if 'street' in data:
		citizen.street = data['street']
	if 'building' in data:
		citizen.building = data['building']
	if 'apartment' in data:
		citizen.apartment = data['apartment']
	if 'name' in data:
		citizen.name = data['name']
	if 'birth_date' in data:
		citizen.birth_date = date_to_another_format(data['birth_date'], "%d.%m.%Y", "%Y-%m-%d")
	if 'gender' in data:
		citizen.gender = data['gender']
	if 'relatives' in data:
		citizen.add_relatives_by_import_id(import_id, data['relatives'])
	response['data']['citizen_id'] = citizen.citizen_id
	response['data']['town'] = citizen.town
	response['data']['street'] = citizen.street
	response['data']['building'] = citizen.building
	response['data']['apartment'] = citizen.apartment
	response['data']['name'] = citizen.name
	response['data']['birth_date'] = date_to_another_format(citizen.birth_date, "%Y-%m-%d", "%d.%m.%Y")
	response['data']['gender'] = citizen.gender
	response['data']['relatives'] = list(citizen.citizen_id for citizen in citizen.get_relatives())
	citizen.save()
	return JsonResponse(response, status=200)


def get_import(request, import_id):
	response = {
		"data": [
		]
	}
	if request.method != 'GET':
		return HttpResponse("Импорт. Метод не 'GET", status=400)
	citizens = Import.get_citizens_by_import_id(import_id)
	for citizen_db in citizens:
		citizen_json = dict()
		citizen_json['citizen_id'] = citizen_db.citizen_id
		citizen_json['town'] = citizen_db.town
		citizen_json['street'] = citizen_db.street
		citizen_json['building'] = citizen_db.building
		citizen_json['apartment'] = citizen_db.apartment
		citizen_json['name'] = citizen_db.name
		citizen_json['birth_date'] = date_to_another_format(citizen_db.birth_date, "%Y-%m-%d", "%d.%m.%Y")
		citizen_json['gender'] = citizen_db.gender
		citizen_json['relatives'] = list(c.citizen_id for c in citizen_db.get_relatives())
		response['data'].append(citizen_json)
	return JsonResponse(response, status=200)


def get_birthdays(request, import_id):
	response = {
		"data": {
			"1":  [],
			"2":  [],
			"3":  [],
			"4":  [],
			"5":  [],
			"6":  [],
			"7":  [],
			"8":  [],
			"9":  [],
			"10": [],
			"11": [],
			"12": [],
		}
	}
	if request.method != 'GET':
		return HttpResponse("Дни рождения. Метод не 'GET", status=400)
	citizens = Import.get_citizens_by_import_id(import_id)
	birthdays = dict()
	for citizen_db in citizens:
		birthdays[citizen_db.citizen_id] = [0] * 12
		for relative in citizen_db.get_relatives():
			birthdays[citizen_db.citizen_id][relative.birth_date.month - 1] += 1
	for citizen_id in birthdays:
		for month, presents_num_in_month in enumerate(birthdays[citizen_id], start=1):
			if presents_num_in_month > 0:
				data = {
					"citizen_id": citizen_id,
					"presents": presents_num_in_month
				}
				response['data'][str(month)].append(data)
	return JsonResponse(response, status=200)


def get_percentile(request, import_id):
	response = {
		'data': [
		]
	}
	if request.method != 'GET':
		return HttpResponse("Перцентиль. Метод не 'GET", status=400)
	citizens = Import.get_citizens_by_import_id(import_id)
	towns = dict()
	for citizen_db in citizens:
		towns.setdefault(citizen_db.town, []).append(citizen_db.get_age())
	for town in towns:
		array = np.array(towns[town])
		response['data'].append({
			"town": town,
			"p50": np.percentile(array, 50, interpolation='linear').round(2),
			"p75": np.percentile(array, 75, interpolation='linear').round(2),
			"p99": np.percentile(array, 99, interpolation='linear').round(2),
		})
	return JsonResponse(response, status=200)
