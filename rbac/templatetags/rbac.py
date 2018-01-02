import re
from django.template import Library
from django.conf import settings
register = Library()

@register.inclusion_tag("rbac/xxxxx.html")
def menu_html(request):
    """
    去Session中获取菜单相关信息，匹配当前URL，生成菜单
    :param request:
    :return:
{'id': 1, 'title': '用户列表', 'url': '/userinfo/', 'menu_gp_id': None, 'menu_id': 1, 'menu_title': '菜单管理'}
{'id': 2, 'title': '添加用户', 'url': '/userinfo/add/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'}
{'id': 3, 'title': '删除用户', 'url': '/userinfo/del/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'}
{'id': 4, 'title': '修改用户', 'url': '/userinfo/edit/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'}
{'id': 5, 'title': '订单列表', 'url': '/order/', 'menu_gp_id': None, 'menu_id': 2, 'menu_title': '菜单2'}
{'id': 6, 'title': '添加订单', 'url': '/order/add/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'}
{'id': 7, 'title': '删除订单', 'url': '/order/del/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'}
{'id': 8, 'title': '修改订单', 'url': '/order/edit/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'}


				   # 前提：一组一个菜单

					request.path_info

				   menu_dict = {
					   菜单ID: {
							组ID: {
								menu: { 'permissions__title': '用户列表', 'permissions__url': '/userinfo/',  'permissions__is_menu': True,group_id: 1, menu_id:3,menu__title:1}
								urls:[
									'/userinfo/',
									'/userinfo/add/',
									'/userinfo/edit/\d+',
									'/userinfo/del/\d+',
								]
							},
							组ID: {
								menu: { 'permissions__title': '订单列表', 'permissions__url': '/order/',  'permissions__is_menu': True,group_id: 2, menu_id:3,menu__title:1}
								urls:[
									'/order/',
									'/order/add/',
									'/order/edit/\d+',
									'/order/del/\d+',
								]
							},
					   }
				   }

    """
    menu_list = request.session[settings.PERMISSION_MENU_KEY]
    # for i in menu_list:
    #     print(i)
    current_url = request.path_info

    menu_dict = {}
    for item in menu_list:
        if not item['menu_gp_id']:
            menu_dict[item['id']] = item

    for item in menu_list:
        regex = "^{0}$".format(item['url'])
        if re.match(regex,current_url):
            menu_gp_id = item['menu_gp_id']
            if menu_gp_id:
                menu_dict[menu_gp_id]['active'] = True
            else:
                menu_dict[item['id']]['active'] = True
    '''{1: {'id': 1, 'title': '用户列表', 'url': '/userinfo/', 'menu_gp_id': None, 'menu_id': 1, 'menu_title': '菜单管理', 'active': True}, 
        5: {'id': 5, 'title': '订单列表', 'url': '/order/', 'menu_gp_id': None, 'menu_id': 2, 'menu_title': '菜单2'}
        }
'''
    result = {}
    for item in menu_dict.values():
        active = item.get('active')
        menu_id = item['menu_id']
        if menu_id in result:
            result[menu_id]['children'].append({ 'title': item['title'], 'url': item['url'],'active':active})
            if active:
                result[menu_id]['active'] = True
        else:
            result[menu_id] = {
                'menu_id':item['menu_id'],
                'menu_title':item['menu_title'],
                'active':active,
                'children':[
                    { 'title': item['title'], 'url': item['url'],'active':active}
                ]
            }

    return {'menu_dict':result}
