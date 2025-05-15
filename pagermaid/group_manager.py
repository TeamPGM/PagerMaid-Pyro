from logging import CRITICAL
from os import path as os_path
from os import sep
from re import findall
from shutil import copyfile
from typing import List

import casbin

from pagermaid import module_dir
from pagermaid.static import all_permissions

# init permissions
if not os_path.exists(f"data{os_path.sep}gm_policy.csv"):
    copyfile(
        f"{module_dir}{os_path.sep}assets{os_path.sep}gm_policy.csv",
        f"data{os_path.sep}gm_policy.csv",
    )
permissions = casbin.Enforcer(
    f"pagermaid{sep}assets{sep}gm_model.conf", f"data{sep}gm_policy.csv"
)
permissions.logger.setLevel(CRITICAL)


class Permission:
    def __init__(self, name: str):
        self.name = name[1:] if name.startswith("-") else name
        self.root = self.name.split(".")[0]
        self.sub = self.name.split(".")[1] if len(self.name.split(".")) > 1 else ""
        self.enable: bool = not name.startswith("-")
        self.act: str = "access" if self.enable else "ejection"


def enforce_permission(user: int, permission: str):
    data = permission.split(".")
    if len(data) != 2:
        raise ValueError("Invalid permission format")
    if permissions.enforce(str(user), data[0], "access") and not permissions.enforce(
        str(user), permission, "ejection"
    ):
        return True
    return bool(
        permissions.enforce(str(user), permission, "access")
        and not permissions.enforce(str(user), permission, "ejection")
    )


def parse_pen(pen: Permission) -> List[Permission]:
    if pen.name.count("*") != 1:
        raise ValueError("Invalid permission format")
    if pen.root not in ["modules", "system", "plugins", "plugins_root"]:
        raise ValueError("Wildcard not allowed in root name")
    datas = []
    for i in all_permissions:
        if (
            pen.root == i.root
            and len(findall(pen.sub.replace("*", r"([\s\S]*)"), i.sub)) > 0
            and i not in datas
        ):
            datas.append(i)
    if not datas:
        raise ValueError("No permission found")
    return datas


def add_user_to_group(user: str, group: str):
    if group not in permissions.get_roles_for_user(user):
        permissions.add_role_for_user(user, group)
        permissions.save_policy()


def remove_user_from_group(user: str, group: str):
    if group in permissions.get_roles_for_user(user):
        permissions.delete_role_for_user(user, group)
        permissions.save_policy()


def add_permission_for_group(group: str, permission: Permission):
    data = parse_pen(permission) if "*" in permission.name else [permission]
    for i in data:
        permissions.add_policy(group, i.name, permission.act, "allow")
    permissions.save_policy()


def remove_permission_for_group(group: str, permission: Permission):
    data = parse_pen(permission) if "*" in permission.name else [permission]
    for i in data:
        permissions.remove_policy(group, i.name, permission.act, "allow")
    permissions.save_policy()


def add_permission_for_user(user: str, permission: Permission):
    data = parse_pen(permission) if "*" in permission.name else [permission]
    for i in data:
        permissions.add_permission_for_user(user, i.name, permission.act, "allow")
    permissions.save_policy()


def remove_permission_for_user(user: str, permission: Permission):
    data = parse_pen(permission) if "*" in permission.name else [permission]
    for i in data:
        permissions.delete_permission_for_user(user, i.name, permission.act, "allow")
    permissions.save_policy()


def rename_group(old_group: str, new_group: str):
    users = permissions.get_users_for_role(old_group)
    for user in users:
        permissions.add_role_for_user(user, new_group)
        permissions.delete_role_for_user(user, old_group)

    old_policies = permissions.get_filtered_policy(0, old_group)
    for policy in old_policies:
        permissions.add_policy(new_group, policy[1], policy[2], policy[3])
        permissions.remove_policy(old_group, policy[1], policy[2], policy[3])
    permissions.save_policy()
