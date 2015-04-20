from kii import results as rs
from kii.helpers import RequestHelper


class Groups:
    def __init__(self, api):
        self.api = api

    def create_a_group(self, name, owner, members=[]):
        helper = CreateAGroup(self.api, name, owner, members)
        result = helper.request()
        return result

    def get_the_group_information(self, group_id):
        helper = GetTheGroupInformation(self.api, group_id)
        result = helper.request()
        return result

    def delete_a_group(self, group_id):
        helper = GetTheGroupInformation(self.api, group_id)
        result = helper.request()
        return result


class CreateAGroup(RequestHelper):
    method = 'POST'
    result_container = rs.GroupCreationResult

    def __init__(self, api,
                 name,
                 owner,
                 members=[]):

        super().__init__(api)

        self.name = name
        self.owner = owner
        self.members = members

    @property
    def api_path(self):
        return '/apps/{appID}/groups'.format(appID=self.api.app_id)

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Content-Type': 'application/vnd.kii.GroupCreationRequest+json',
            'Authorization': self.authorization,
        })
        return headers

    def request(self):
        params = {
            'name': self.name,
            'owner': self.owner,
            'members': self.members,
        }

        return super().request(json=params)


class GetTheGroupInformation(RequestHelper):
    method = 'GET'
    result_container = rs.GroupInformationResult

    def __init__(self, api, group_id):
        super().__init__(api)
        self.group_id = group_id

    @property
    def api_path(self):
        return '/apps/{appID}/groups/{groupID}'.format(
            appID=self.api.app_id,
            groupID=self.group_id,
        )

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers


class DeleteAGroup(RequestHelper):
    method = 'DELETE'
    result_container = rs.BaseResult

    def __init__(self, api, group_id):
        super().__init__(api)
        self.group_id = group_id

    @property
    def api_path(self):
        return '/apps/{appID}/groups/{groupID}'.format(
            appID=self.api.app_id,
            groupID=self.group_id,
        )

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers
