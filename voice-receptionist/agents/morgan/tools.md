# Morgan tools

| Tool | When | Required | Never |
|---|---|---|---|
| get_hours | Open/closed, hours, “are you in?” | none | Invent hours |
| lookup_faq | Process / location / parking / general | query | Invent policy |
| take_message | After read-back of name + phone + reason | caller_name, callback_phone, reason | Guess a number |
| request_transfer | Caller wants a human | reason | Transfer when transfer_number is empty |
| end_call | Task done, caller has nothing else | none | End while they are still asking |
