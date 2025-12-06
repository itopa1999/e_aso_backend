from apps.users.models import User, UserAgent
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger
from django.db.models import Count
from http import HTTPStatus


class UserAgentAnalysisQuery:
    """Simple user agent analysis with counts"""
    
    @staticmethod
    def query(user_email=None, request=None):
        op = OperationLogger(
            "UserAgentAnalysisQuery",
            email=user_email or "all_users"
        )
        op.start()
        
        try:
            # Get base queryset
            if user_email:
                user = User.objects.filter(email__icontains=user_email).first()
                if not user:
                    op.fail(f"User not found: {user_email}")
                    return BaseResultWithData(
                        message=f"User not found: {user_email}",
                        data=None,
                        status_code=HTTPStatus.NOT_FOUND
                    )
                user_agents = UserAgent.objects.filter(user=user).order_by('-last_seen')
            else:
                user_agents = UserAgent.objects.all().order_by('-last_seen')
            
            # Calculate distinct counts
            total_devices = user_agents.count()
            total_users = user_agents.values('user').distinct().count()
            total_ips = user_agents.values('ip_address').distinct().count()
            
            # Count by type
            by_device_type = user_agents.values('device_type').annotate(count=Count('id')).order_by('-count')
            by_browser = user_agents.values('browser').annotate(count=Count('id')).order_by('-count')
            by_os = user_agents.values('os').annotate(count=Count('id')).order_by('-count')
            
            # Active status
            active_devices = user_agents.filter(is_active=True).count()
            inactive_devices = user_agents.filter(is_active=False).count()
            
            # Build response
            analysis_data = {
                "summary": {
                    "total_devices": total_devices,
                    "total_users": total_users,
                    "total_unique_ips": total_ips,
                    "active_devices": active_devices,
                    "inactive_devices": inactive_devices,
                },
                "breakdown": {
                    "by_device_type": [
                        {"type": item['device_type'] or "Unknown", "count": item['count']}
                        for item in by_device_type
                    ],
                    "by_browser": [
                        {"browser": item['browser'] or "Unknown", "count": item['count']}
                        for item in by_browser
                    ],
                    "by_os": [
                        {"os": item['os'] or "Unknown", "count": item['count']}
                        for item in by_os
                    ],
                },
            }
            
            # Add user filter info if specified
            if user_email:
                analysis_data["user"] = {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
                op.success(f"Analysis for user {user_email} completed")
            else:
                op.success("Global analysis completed")
            
            return BaseResultWithData(
                message="Analysis completed",
                data=analysis_data,
                status_code=HTTPStatus.OK
            )
            
        except Exception as e:
            op.fail(f"Error: {str(e)}")
            return BaseResultWithData(
                message=f"Error: {str(e)}",
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

