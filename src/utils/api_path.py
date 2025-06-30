# api_path.py

class RoutePaths:
    API_PREFIX = "/comepass/api/v1"

    class Auth:
        init = "/auth"
        login = "/login"
        refresh_token = "/refresh-token"
        check_access = "/check-access"
        check_role = "/check-role"
    class ChatTopic:
        init = "/chat-gpt"
        list = "/topic"
        add = "/topic"
        list_by_user = "/topic/user/{user_id}"
    class ChatMessage:
        init = "/chat-gpt"
        list = "/messages"
        add = "/messages/topic-{topic_id}"
        list_by_topic = "/messages/topic-{topic_id}"
        list_by_topic_user = "/messages/topic-{topic_id}/user-{user_id}"
    class Users:
        init = "/users"
        list = "/"
        add = "/"
        retrieve = "/{user_id}"
        edit = "/{user_id}"
        delete = "/{user_id}"
        change_password = "/{user_id}/change-password"
    class Role:
        init = "/roles"
        list = "/"
        add = "/"
        retrieve = "/{role_id}"
        edit = "/{role_id}"
        delete = "/{role_id}"
    class Permission:
        init = "/permissions"
        list = "/"

route_model_map = {
    "/chat-gpt/topic": "ChatTopic",
    "/chat-gpt/messages": "ChatMessage",
    "/users": "Users",
}

route_model_pk_map = [
    (r"/chat-gpt/topic$", "ChatTopic", None),
    (r"/chat-gpt/messages$", "ChatMessage", None),
    (r"/chat-gpt/messages/topic-(?P<topic_id>\d+)$", "ChatTopic", "topic_id"),
    (r"/users$", "Users", None),
    (r"/users/(?P<user_id>\d+)$", "Users", "user_id"),
]
