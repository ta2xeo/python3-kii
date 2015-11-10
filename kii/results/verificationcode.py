from .base import BaseResult


class VerificationCodeResult(BaseResult):
    @property
    def verification_code(self):
        return self._result['verificationCode']
