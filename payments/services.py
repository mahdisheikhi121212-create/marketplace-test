import requests

from django.conf import settings


class ZarinPalService:

    def __init__(self):

        self.merchant_id = (
            settings.ZARINPAL_MERCHANT_ID
        )

        self.request_url = (
            settings.ZARINPAL_REQUEST_URL
        )

        self.verify_url = (
            settings.ZARINPAL_VERIFY_URL
        )

        self.start_pay_url = (
            settings.ZARINPAL_STARTPAY_URL
        )

        self.callback_url = (
            settings.ZARINPAL_CALLBACK_URL
        )

        self.sandbox = (
            settings.ZARINPAL_SANDBOX
        )


    def _validate_configuration(self):

        required = [
            self.merchant_id,
            self.request_url,
            self.verify_url,
            self.start_pay_url,
            self.callback_url,
        ]

        if not all(required):
            raise ValueError(
                "ZarinPal configuration is incomplete."
            )


    def request_payment(
        self,
        payment
    ):

        amount = int(
            payment.amount
        )


        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )


        # حالت توسعه
        if self.sandbox:

            return {
                "data": {
                    "authority":
                    f"TEST-AUTH-{payment.id}"
                },
                "errors": []
            }


        self._validate_configuration()


        payload = {

            "merchant_id":
            self.merchant_id,

            "amount":
            amount,

            "description":
            (
                f"Payment for order "
                f"{payment.order.order_number}"
            ),

            "callback_url":
            self.callback_url,
        }


        response = requests.post(
            self.request_url,
            json=payload,
            timeout=15,
        )


        response.raise_for_status()


        return response.json()



    def get_payment_url(
        self,
        authority
    ):

        if not authority:
            raise ValueError(
                "Payment authority is required."
            )


        if self.sandbox:

            return (
                f"{self.callback_url}"
                f"?Authority={authority}"
                f"&Status=OK"
            )


        return (
            self.start_pay_url
            +
            authority
        )



    def verify_payment(
        self,
        payment,
        authority
    ):

        amount = int(
            payment.amount
        )


        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )


        if not authority:
            raise ValueError(
                "Payment authority is required."
            )


        # حالت توسعه
        if self.sandbox:

            return {
                "data": {
                    "code": 100,
                    "ref_id":
                    f"TEST-REF-{payment.id}"
                },
                "errors": []
            }


        self._validate_configuration()


        payload = {

            "merchant_id":
            self.merchant_id,

            "amount":
            amount,

            "authority":
            authority,
        }


        response = requests.post(
            self.verify_url,
            json=payload,
            timeout=15,
        )


        response.raise_for_status()


        return response.json()
