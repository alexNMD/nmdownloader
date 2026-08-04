from requests import RequestException


class NotificationError(RequestException): ...


class DiscordNotificationError(NotificationError): ...
