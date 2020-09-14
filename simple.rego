package httpapi.authz

import input

default allow = false

# Allow users to get their own salaries.
allow {
  some user_id
  input.method == "GET"
  input.path = ["finance", "salary", user_id]
  access_token.payload.sub == user_id
}

# Allow managers to get all users salaries.
allow {
  input.method == "GET"
  input.path = ["finance", "salary", username]
  access_token.payload["https://my.ns/role"] == "manager"
}

# Helper to get the access_token payload.
access_token = {"payload": payload} {
  [header, payload, signature] := io.jwt.decode(input.access_token)   # note: should use io.jwt.verify_rs256 for prod
}
