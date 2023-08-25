from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UserBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", '')
    b = request.GET.get("b", '')
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    contex = {
        "form": UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=contex)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    reply = 'Uploaded file must not be larger than 1 mb.'

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']
            if myfile.size > 1000000:
                form = UploadFileForm()
                reply = 'File size is over 1 mb, please try a smaller file.'
            else:
                fs = FileSystemStorage()
                fs.save(myfile.name, myfile)
                reply = 'File successfully uploaded'
    else:
        form = UploadFileForm()

    context = {
        "reply": reply,
        "form": form,
    }
    return render(request, 'requestdataapp/file-upload.html', context=context)
