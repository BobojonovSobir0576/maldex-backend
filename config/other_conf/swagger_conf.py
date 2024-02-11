SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "JWT [Bearer {JWT}]": {
            "name": "Mal dex backend",
            "type": "apiKey",
            "in": "header",
        }
    },
    "TITLE": "Mal dex backend",
    "DESCRIPTION": "Mal dex backend",
    "VERSION": "0.1.0",
    "USE_SESSION_AUTH": False,
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Mal dex backend",
    "DESCRIPTION": "Mal dex backend",
    "VERSION": "0.1.0"
}
