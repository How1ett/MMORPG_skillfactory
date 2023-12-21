from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView, FormView, TemplateView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from mmorpg_site import settings

from .models import Advertisement, Comment
from .forms import AdvertisementForm, CommentForm, CommentFilterForm, EditProfile
# from .tasks import respond_send_email, respond_accept_send_email


class Index(ListView):
    model = Advertisement
    template_name = 'index.html'
    context_object_name = 'advertisements'


class AdvertisementItem(DetailView):
    model = Advertisement
    template_name = 'advertisement_item.html'
    context_object_name = 'advertisement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Comment.objects.filter(author_id=self.request.user.id).filter(advertisement_id=self.kwargs.get('pk')):
            context['respond'] = "Откликнулся"
        elif self.request.user == Advertisement.objects.get(pk=self.kwargs.get('pk')).author:
            context['respond'] = "Мое_объявление"
        return context


class CreateAdvertisement(LoginRequiredMixin, CreateView):
    model = Advertisement
    template_name = 'create_advertisement.html'
    form_class = AdvertisementForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm('board.add_advertisement'):
            return HttpResponseRedirect(reverse('account_profile'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        advertisement = form.save(commit=False)
        advertisement.author = User.objects.get(id=self.request.user.id)
        advertisement.save()
        return redirect(f'/advertisement/{advertisement.id}')


class EditAdvertisement(PermissionRequiredMixin, UpdateView):
    permission_required = 'board.change_advertisement'
    template_name = 'edit_advertisement.html'
    form_class = AdvertisementForm
    success_url = '/create/'

    def dispatch(self, request, *args, **kwargs):
        author = Advertisement.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Только автор имеет право редактировать объявления")

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Advertisement.objects.get(pk=id)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/advertisement/' + str(self.kwargs.get('pk')))


class DeleteAdvertisement(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_advertisement'
    template_name = 'delete_advertisement.html'
    queryset = Advertisement.objects.all()
    success_url = '/index'

    def dispatch(self, request, *args, **kwargs):
        author = Advertisement.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Только автор имеет право удалить объявление")


title = str("")


class Comments(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'comments.html'
    context_object_name = 'comments'

    def get_context_data(self, **kwargs):
        context = super(Comments, self).get_context_data(**kwargs)
        global title
        if self.kwargs.get('pk') and Advertisement.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Advertisement.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = CommentFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            advertisement_id = Advertisement.objects.get(title=title)
            context['filter_comments'] = list(Comment.objects.filter(advertisement_id=advertisement_id).order_by('-time_create'))
            context['comment_advertisement_id'] = advertisement_id.id
        else:
            context['filter_comments'] = list(Comment.objects.filter(advertisement_id__author_id=self.request.user).order_by('-time_create'))
        context['mycomments'] = list(Comment.objects.filter(author_id=self.request.user).order_by('-time_create'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/comments')
        return self.get(request, *args, **kwargs)


@login_required
def comment_accept(request, **kwargs):
    comment = Comment.objects.get(id=kwargs.get('pk'))
    if request.user == comment.advertisement.author:
        comment.moderation = True
        comment.save()
        text = comment.text
        title = f'Добрый день, {comment.author}, ! Ваш комментарий утвержден!'
        html_content = render_to_string(
            'mail_confirm_comment.html', {'user': comment.author, 'text': text[:50], 'post': comment, 'title': f'Добрый день, {comment.author}, ! Ваш комментарий утвержден!'}
        )
        msg = EmailMultiAlternatives(
            subject=title,
            body=f'{text[:50]}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[comment.author.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponseRedirect('/comments')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def comment_delete(request, **kwargs):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=kwargs.get('pk'))
        comment.delete()
        return HttpResponseRedirect('/comments')
    else:
        return HttpResponseRedirect('/accounts/login')


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = User.objects.get(id=self.request.user.id)
        comment.advertisement = Advertisement.objects.get(id=self.kwargs.get('pk'))
        comment.save()
        adv = Advertisement.objects.get(id=self.kwargs.get('pk'))
        author = adv.author
        text = self.request.POST.get('text')
        title = f'Добрый день, {comment.advertisement.author}, ! Новый комментарий к вашему объявлению!'
        html_content = render_to_string(
            'mail.html', {'user': author, 'text': text[:50], 'post': comment, 'title': f'Добрый день, {comment.advertisement.author}, ! Новый комментарий к вашему объявлению!'}
        )
        msg = EmailMultiAlternatives(
            subject=title,
            body=f'{text[:50]}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[author.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return redirect(f'/advertisement/{self.kwargs.get("pk")}')


class AccountProfile(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfile
    success_url = 'accounts/profile'
    template_name = 'account/update_profile.html'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
          queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)