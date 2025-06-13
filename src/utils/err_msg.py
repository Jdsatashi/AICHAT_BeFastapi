class ErrorMessage:
    pw_wrong = "password incorrect"
    pw_not_match = "confirm password does not match"
    not_found = "not found"
    inactive = "is inactive"
    invalid = "is invalid"
    expired = "expired"
    unexpected = "unexpected error"

err_msg = ErrorMessage()


err_code = {
    err_msg.pw_wrong: 400,
    err_msg.pw_not_match: 400,
    err_msg.not_found: 404,
    err_msg.inactive: 400,
    err_msg.invalid: 400,
    err_msg.expired: 400,
    err_msg.unexpected: 500,
}


