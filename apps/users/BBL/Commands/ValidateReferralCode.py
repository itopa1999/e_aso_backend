

from apps.users.models import Referral, User
from utils.base_result import BaseResult
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


class ValidateReferralCodeCommand:
    @staticmethod
    def execute(user, referral_code):
        if not is_feature_enabled(FeatureNames.REFERRAL_SYSTEM.value):
            return BaseResult(
                message="Referral system is currently disabled.",
                status_code=400
            )

        try:
            referrer = User.objects.get(referral_code=referral_code)
        except User.DoesNotExist:
            return BaseResult(
                message="Invalid referral code.",
                status_code=400
            )
        if referrer.id == user.id:
            return BaseResult(
                message="You cannot use your own referral code.",
                status_code=400
            )
        if user.referral_used:
            return BaseResult(
                message="You have already referred.",
                status_code=400
            )
        Referral.objects.create(referrer=referrer, referee=user, successful=True)
        user.referral_used = True
        user.save(update_fields=["referral_used"])
        
        referrer.check_referral_qualification
        
        return BaseResult(
            message="Referral code applied successfully.",
            status_code=200
        )