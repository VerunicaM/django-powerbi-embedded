from django.shortcuts import render, redirect
from django.contrib import auth

def logout(request):
    auth.logout(request)
    return redirect('/')

def login(request):
    if request.method == "GET":
        return render(request, "auth/login.html")
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # make sure the username & password is good
        user = auth.authenticate(username=username, password=password)

        if user is not None: # User was found & password matched
            if user.is_active:
                #associate the user with the session
                auth.login(request, user)

                #read the destination
                next = ""
                if "next" in request.GET:
                    next = request.GET["next"]
                if next == None or next == "":
                    next = "/"
                return redirect(next)
            else:
                #account disabled
                return render(request, "auth/login.html", { "warning": "Your account is disabled" })
        else:
            # bad username and password
            return render(request, "auth/login.html", { "warning": "Invalid username and or password" })