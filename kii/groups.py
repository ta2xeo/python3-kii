from kii import results as rs
from kii.helpers import RequestHelper, AuthRequestHelper


class GroupManagement:
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

    def get_a_list_of_groups_filtered_by_a_user(self, is_member=None, owner=None):
        helper = GetAListOfGroupsFilteredByAUser(self.api, is_member=is_member, owner=owner)
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
        if isinstance(owner, rs.UserResult):
            owner = owner.user_id
        self.owner = owner

        def to_user_id(member):
            if isinstance(member, rs.UserResult):
                return member.user_id
            return member

        self.members = list(map(to_user_id, members))

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


class GetTheGroupInformation(AuthRequestHelper):
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


class DeleteAGroup(AuthRequestHelper):
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


class GetAListOfGroupsFilteredByAUser(AuthRequestHelper):
    method = 'GET'
    result_container = rs.BaseResult

    def __init__(self, api, *, is_member=None, owner=None):
        super().__init__(api)
        self.is_member = is_member
        self.owner = owner

    @property
    def api_path(self):
        path = '/apps/{appID}/groups'.format(appID=self.api.app_id)

        if self.is_member is not None:
            return '{0}?is_member={1}'.format(path, self.is_member)
        elif self.owner is not None:
            return '{0}?owner={1}'.format(path, self.owner)
        return path
