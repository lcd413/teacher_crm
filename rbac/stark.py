from stark.service import v1
from rbac import models
class UserConfig(v1.StarkConfig):
    def display_roles(self, obj=None, is_header=False):
        if is_header:
            return '具有的所有角色'

        html = []
        role_list = obj.roles.all()
        for role_obj in role_list:
            html.append(role_obj.name)

        return ",".join(html)
    list_display = ['username','email',display_roles]
v1.site.register(models.User,UserConfig)

class RoleConfig(v1.StarkConfig):
    def display_permissions(self, obj=None, is_header=False):
        if is_header:
            return '具有的所有权限'

        html = []
        permissions_list = obj.permissions.all()
        for obj in permissions_list:
            html.append(obj.name)

        return ",".join(html)
    list_display = ['title',display_permissions]
v1.site.register(models.Role,RoleConfig)

class MenuConfig(v1.StarkConfig):
    list_display = ['title']
v1.site.register(models.Menu,MenuConfig)

class GroupConfig(v1.StarkConfig):
    list_display = ['caption','menu']
v1.site.register(models. Group,GroupConfig)

class PermissionConfig(v1.StarkConfig):
    list_display = ['title','url','menu_gp','code','group']
v1.site.register(models. Permission,PermissionConfig)

