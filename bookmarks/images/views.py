from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

from common.decorators import ajax_required
from actions.utils import create_action

from .forms import ImageCreateForm
from .models import Image


# Create your views here.
@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 20)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)

    if request.is_ajax():
        context = {
            'section': 'images',
            'images': images,
        }
        return render(request,
                      'images/image/list_ajax.html',
                      context)

    context = {
        'section': 'images',
        'images': images,
    }
    return render(request,
                  'images/image/list.html',
                  context)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, "Imagge added")

            return redirect(new_item.get_absolute_url())

    else:
        form = ImageCreateForm(data=request.GET)

    context = {
        'section': 'images',
        'form': form
    }

    return render(request,
                  'images/image/create.html',
                  context)


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)

    context = {
        'section': 'images',
        'image': image,
    }

    return render(request,
                  'images/image/detail.html',
                  context)


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('actions')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass

    return JsonResponse({'status': 'ok'})
