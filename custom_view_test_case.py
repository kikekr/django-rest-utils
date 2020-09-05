import datetime
import json

from django.db.models import Model

from custom_api_client import CustomAPIClient
from exceptions import ResourceNotFoundException
from utils.dates import serialize_date


class CustomViewTestCase:

    def __init__(self, url_endpoint, test_case):
        self.__c = CustomAPIClient(url_endpoint)
        self.__test_case = test_case

    def __check_list_endpoint_response(self, expected_queryset, pk='id', url_params=None):
        """
        Verify if the response from a listing endpoint corresponds to the appropriate response
        from internal logic
        :expected_queryset Queryset<Model>
        :pk <int>
        :return <bool>
        """
        response = self.__c.list(url_params)
        self.__test_case.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)

        self.__test_case.assertEqual(len(response_content), expected_queryset.count())
        queryset = expected_queryset.model.objects.filter(
            id__in=[x[pk] for x in response_content]).order_by(pk).distinct()

        return self.__test_case.assertEqual(list(queryset), list(expected_queryset.order_by(pk)))

    def __check_list_ordering_endpoint_response(self, expected_queryset, pk='id', url_params=None):
        """
        Verify if the order response from a listing endpoint corresponds to the appropriate order
        response from internal logic
        :expected_queryset Queryset<Model>
        :pk <int>
        :return <bool>
        """
        response = self.__c.list(url_params)
        self.__test_case.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)

        self.__test_case.assertEqual([x[pk] for x in response_content],
                                     [getattr(x, pk) for x in expected_queryset])

    def __compare_dict_obj(self, obj, data):
        for key, value in data.items():
            attr = getattr(obj, key)
            if issubclass(type(attr), Model):
                self.__test_case.assertEqual(attr.id, value)
            elif type(attr) == datetime.datetime:
                self.__test_case.assertEqual(serialize_date(attr), value)
            else:
                self.__test_case.assertEqual(attr, value)

    def test_create_obj_ok(self, data, user, retrieve_function):
        if user is not None:
            self.__c.set_credentials(user)
        response = self.__c.create(data)
        self.__test_case.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        obj_id = content["id"]
        obj = retrieve_function(obj_id)
        self.__test_case.assertEqual(getattr(obj, "id"), obj_id)
        self.__compare_dict_obj(obj, data)

    def test_create_obj_conflict(self, user, data):
        self.__c.set_credentials(user)
        response = self.__c.create(data)
        self.__test_case.assertEqual(response.status_code, 409)

    def test_create_obj_bad_request(self, user, data=None):
        if data is None:
            data = {}
        if user is not None:
            self.__c.set_credentials(user)
        response = self.__c.create(data)
        self.__test_case.assertEqual(response.status_code, 400)

    def test_create_obj_without_credentials(self):
        response = self.__c.create({})
        self.__test_case.assertEqual(response.status_code, 401)

    def test_create_obj_forbidden(self, user, data):
        self.__c.set_credentials(user)
        response = self.__c.create(data)
        self.__test_case.assertEqual(response.status_code, 403)

    def test_list_obj_ok(self, user, expected_queryset, url_params=None):
        self.__c.set_credentials(user)
        self.__check_list_endpoint_response(expected_queryset, url_params=url_params)

    def test_list_obj_ordering_ok(self, user, expected_queryset, url_params=None):
        self.__c.set_credentials(user)
        self.__check_list_ordering_endpoint_response(expected_queryset, url_params=url_params)

    def test_list_obj_without_credentials(self):
        response = self.__c.list()
        self.__test_case.assertEqual(response.status_code, 401)

    def test_retrieve_obj_ok(self, user, obj, pk="id"):
        self.__c.set_credentials(user)
        response = self.__c.retrieve(getattr(obj, pk))
        self.__test_case.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.__compare_dict_obj(obj, content)

    def test_retrieve_obj_not_found(self, user):
        self.__c.set_credentials(user)
        response = self.__c.retrieve(9999999999)
        self.__test_case.assertEqual(response.status_code, 404)

    def test_retrieve_obj_without_credentials(self, obj, pk="id"):
        response = self.__c.retrieve(getattr(obj, pk))
        self.__test_case.assertEqual(response.status_code, 401)

    def test_retrieve_obj_forbidden(self, user, obj, pk="id"):
        self.__c.set_credentials(user)
        response = self.__c.retrieve(getattr(obj, pk))
        self.__test_case.assertEqual(response.status_code, 404)

    def test_delete_obj_ok(self, user, obj, retrieve_function, pk="id"):
        self.__c.set_credentials(user)
        identifier = getattr(obj, pk)
        response = self.__c.destroy(identifier)
        self.__test_case.assertEqual(response.status_code, 204)
        self.__test_case.assertRaises(ResourceNotFoundException, retrieve_function, identifier)

    def test_delete_obj_not_found(self, user):
        self.__c.set_credentials(user)
        response = self.__c.destroy(9999999999)
        self.__test_case.assertEqual(response.status_code, 404)

    def test_delete_obj_without_credentials(self, obj, pk="id"):
        response = self.__c.destroy(getattr(obj, pk))
        self.__test_case.assertEqual(response.status_code, 401)

    def test_delete_obj_forbidden(self, user, obj, retrieve_function, pk="id"):
        self.__c.set_credentials(user)
        identifier = getattr(obj, pk)
        response = self.__c.destroy(identifier)
        self.__test_case.assertEqual(response.status_code, 404)

    def test_update_obj_ok(self, user, obj, data, pk="id"):
        self.__c.set_credentials(user)
        identifier = getattr(obj, pk)
        response = self.__c.update(identifier, data)
        self.__test_case.assertEqual(response.status_code, 200)
        obj.refresh_from_db()
        self.__compare_dict_obj(obj, data)

    def test_update_obj_not_found(self, user, data=None):
        if data is None:
            data = {}
        self.__c.set_credentials(user)
        response = self.__c.update(9999, data)
        self.__test_case.assertEqual(response.status_code, 404)

    def test_update_obj_bad_request(self, user, obj, data, pk="id"):
        self.__c.set_credentials(user)
        identifier = getattr(obj, pk)
        response = self.__c.update(identifier, data)
        self.__test_case.assertEqual(response.status_code, 400)

    def test_update_obj_without_credentials(self, obj, pk="id"):
        identifier = getattr(obj, pk)
        response = self.__c.update(identifier, {})
        self.__test_case.assertEqual(response.status_code, 401)

    def test_update_obj_forbidden(self, user, obj, data, pk="id"):
        self.__c.set_credentials(user)
        identifier = getattr(obj, pk)
        response = self.__c.update(identifier, data)
        self.__test_case.assertEqual(response.status_code, 404)
