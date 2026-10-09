from abc import ABC, abstractmethod


class SMSProvider(ABC):
    @abstractmethod
    def send_sms(self, phone, message):
        """
        ارسال پیامک به شماره تلفن.
        """
        raise NotImplementedError