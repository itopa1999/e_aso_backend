

from apps.users.models import Referral, User
from utils.base_result import BaseResult
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled
from utils.log_helpers import OperationLogger


class ValidateReferralCodeCommand:
    @staticmethod
    def execute(user, referral_code):
        op = OperationLogger(
            "ValidateReferralCodeCommand",
            user=user.id if user else "Anonymous",
            referral_code=referral_code
        )
        op.start()
        
        flag, enable = is_feature_enabled(FeatureNames.REFERRAL_SYSTEM.value)
        if not enable:
            op.fail("Referral system is disabled")
            return BaseResult(
                message="Referral system is currently disabled.",
                status_code=400
            )

        try:
            referrer = User.objects.get(referral_code=referral_code)
        except User.DoesNotExist:
            op.fail(f"Invalid referral code: {referral_code}")
            return BaseResult(
                message="Invalid referral code.",
                status_code=400
            )
        if referrer.id == user.id:
            op.fail(f"User {user.id} attempted to use their own referral code")
            return BaseResult(
                message="You cannot use your own referral code.",
                status_code=400
            )
        if user.referral_used:
            op.fail(f"User {user.id} has already used a referral")
            return BaseResult(
                message="You have already referred.",
                status_code=400
            )
        Referral.objects.create(referrer=referrer, referee=user, successful=True)
        user.referral_used = True
        user.save(update_fields=["referral_used"])
        
        referrer.check_referral_qualification
        op.success(f"Referral code {referral_code} applied successfully for user {user.id}")
        
        return BaseResult(
            message="Referral code applied successfully.",
            status_code=200
        )