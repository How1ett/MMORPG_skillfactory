from django import forms
from .models import Advertisement, Comment
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        widgets = {'title': forms.TextInput(attrs={'size': '100'})}
        fields = ('category', 'title', 'content',)

    def __init__(self, *args, **kwargs):
        super(AdvertisementForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Категория"
        self.fields['title'].label = "Заголовок"
        self.fields['content'].label = "Текст объявления"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Текст отклика:"


class CommentFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(CommentFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Advertisement.objects.filter(author_id=user.id).order_by('-time_create').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )


class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
