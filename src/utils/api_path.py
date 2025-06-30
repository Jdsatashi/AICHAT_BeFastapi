# api_path.py

class RoutePaths:
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
