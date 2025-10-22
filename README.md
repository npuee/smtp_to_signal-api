Bridge between smtp server bbernhard/signal-cli-rest-api docker container.

Why: I lot of stuff do not have webhooks and only send to email(like unview cameras, monitoring etc.). This allows send email to signal-cli bot to send signal message to group or number. 


Adjust setting.json accordingly.

signal-cli should be working and accesible. 
Build docker container: docker build -t IMAGE_NAME . 
