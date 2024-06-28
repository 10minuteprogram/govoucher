from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        profile = user.profile
        extra_data = sociallogin.account.extra_data
        profile.picture_url = extra_data.get('picture')
        profile.save()
        return user
