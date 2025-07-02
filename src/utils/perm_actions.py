class PermissionAction:
    all = "all"
    read = "read"
    add = "add"
    edit = "edit"
    destroy = "destroy"

actions = PermissionAction()

actions_list = [
    actions.all,
    actions.read,
    actions.add,
    actions.edit,
    actions.destroy
]

actions_main = [
    actions.read,
    actions.add,
    actions.edit,
    actions.destroy
]

actions_methods = {
    actions.all: ["GET", "POST", "PUT", "DELETE"],
    actions.read: ["GET"],
    actions.add: ["POST"],
    actions.edit: ["PUT"],
    actions.destroy: ["DELETE"]
}

method_map = {
    "GET": actions.read,
    "POST": actions.add,
    "PUT": actions.edit,
    "DELETE": actions.destroy
}
