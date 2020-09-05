from rest_framework.test import APIClient


class CustomAPIClient:

    def __init__(self, url_endpoint):
        self.__url_endpoint = str(url_endpoint) + "/"
        self.__c = APIClient()

    def set_credentials(self, user):
        self.__c.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)

    def create(self, data):
        return self.__c.post(self.__url_endpoint, data)

    def retrieve(self, pk):
        return self.__c.get(self.__url_endpoint + str(pk) + "/")

    def list(self, url_params=None):

        if url_params:
            url_endpoint = self.__url_endpoint + "?"
            count = 0
            for key, value in url_params.items():
                if count != 0:
                    url_endpoint = url_endpoint + "&"
                url_endpoint = url_endpoint + str(key) + "=" + str(value)
                count = count + 1
        else:
            url_endpoint = self.__url_endpoint
        return self.__c.get(url_endpoint)

    def update(self, pk, data):
        return self.__c.put(self.__url_endpoint + str(pk) + "/", data)

    def destroy(self, pk):
        return self.__c.delete(self.__url_endpoint + str(pk) + "/")
