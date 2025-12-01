from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.template import loader
from django.shortcuts import render, redirect
from django.urls import reverse
import os, copy, io
from .models import *
from .forms import *
from .utilities import *
import datetime
from io import BytesIO

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user) # dont logout the user.
            # messages.success(request, "Password changed.")
            return redirect("/")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "registration/change_password.html", {'form':form})

def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form':form})

def home(request):
    if request.user.is_authenticated:
        context = {}
        template = loader.get_template('home.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/accounts/login/")

@login_required
def versions(request, **kwargs):
    template = loader.get_template('versions.html')
    user = request.user
    versions = list(Version.objects.filter(user=user, archive=False))
    if Master.objects.filter(ref="default").count() == 0:
        lookup = json.dumps(pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Lookup").to_dict())
        methods = json.dumps(pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Methods").to_dict())
        Master.objects.create(methods=methods, lookup=lookup)
    
    if len(versions) == 0:
        version = Version.objects.create(user=request.user)
        create_methods(version, True, None)
        versions = list(Version.objects.filter(user=user, archive=False))
    version, currentversion = current_version(request)
    if currentversion == None:
        version = versions[0]
        currentversion = CurrentVersion.objects.create(user=user, version=version)
        return HttpResponseRedirect('/versions/')
    elif version == None:
        version = versions[0]
        currentversion.delete()
        currentversion = CurrentVersion.objects.create(user=user, version=version)
        return HttpResponseRedirect('/versions/')

    if currentversion != None:
        state = "/versions/"
        setattr(currentversion, "state", state)
        currentversion.save()
    for i in versions:
        if i == version:
            i.current = True
            i.save()
        else:
            i.current = False
            i.save()

    if version != None:
        version_name = version.name
    else:
        version_name = ""
    if request.method == 'POST':
        id = request.POST.get("select_version")
        if id == "None":
            if currentversion != None:
                currentversion.delete()
        version = Version.objects.get(id=id)
        setattr(currentversion, "version", version)
        currentversion.save()
        return HttpResponseRedirect('/versions/')
    else:
        if version == None:
            context = {
            'versions': versions,
            'version_not_selected': True,
            'version': None,
            'superuser': request.user.is_superuser,
            }            
        else:
            context = {
            'versions': versions,
            'version_not_selected': len(versions) == 0,
            'version': version_name,
            'superuser': request.user.is_superuser,
            }          
        return HttpResponse(template.render(context, request))

@login_required    
def add_version(request, **kwargs):
    blank = kwargs["blank"]
    versions = Version.objects.filter(user=request.user, archive=False).order_by("name")
    version, currentversion = current_version(request)
    if request.method == 'POST':    
        post = copy.deepcopy(request.POST)
        post.update({"user": request.user})  
        form = VersionForm(post, user=request.user, new=True, version=None, blank=blank)
      
        if form.is_valid():
            version = form.save()
            create_methods(version, blank, None)
            # create_standard_elements = post.get("create_standard_elements")
            # if create_standard_elements == "on": create_standard_elements = True
            # else: create_standard_elements = False
            x, currentversion = current_version(request)
            if currentversion != None:
                currentversion.delete()
            currentversion = CurrentVersion.objects.create(user=request.user, version=version)

            # create_params(version, request.user)

            currentversion.save()
            return HttpResponseRedirect("/versions/")
        else:
            # [version, state, currentversion] = current_version(request)
            context = {}
            context['form'] = form
            context['blank'] = blank
            # context["version"] = version
            return render(request, 'add_version.html', context)


    form = VersionForm(user=request.user, version=version, new=True, blank=blank)
    context = {
        'superuser': request.user.is_superuser,
        'blank': blank,
        'form': form,
        'version_not_selected': len(versions) == 0,
    }
    return render(request, 'add_version.html', context)

@login_required
def edit_version(request, id):

    # Check object belongs to logged-in user
    try:
        if Version.objects.get(id=id).user != request.user:
            return HttpResponseRedirect("/versions/")
    except:
        return HttpResponseRedirect("/versions/")
    version = Version.objects.get(id=id)
    x, currentversion = current_version(request)
    state = currentversion.state
    if request.method == 'POST':
        post = copy.deepcopy(request.POST)
        post.update({"user": request.user}) 
        form = VersionForm(post, instance=version, user=request.user, new=False, version=version, blank=False) 
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(state)
    else:
        form = VersionForm(instance=version, user=request.user, new=False, version=version, blank=False)

    context = {
        'superuser': request.user.is_superuser,
        "form": form,
        "id": id,
        "name": version.name,
        "version": version.name
    }
    return render(request, 'edit_version.html', context)    

@login_required
def cancel(request):
    [version, currentversion] = current_version(request)
    state = currentversion.state
    return HttpResponseRedirect(state)

@login_required
def set_version(request, id):
    if Version.objects.get(id=id).user != request.user:
        return HttpResponseRedirect("/versions/")

    version, currentversion = current_version(request)
    if currentversion != None:
        if currentversion.version != None:
            if CurrentVersion.objects.get(user=request.user).version.id == id:
                return HttpResponseRedirect("/versions/")
    version = Version.objects.get(id=id)
    # check_params(version)
    if currentversion != None:
        currentversion.delete()
    currentversion = CurrentVersion.objects.create(user=request.user, version=version)

    # create_params(version, request.user)
    
    currentversion.save()
    return HttpResponseRedirect("/versions/")

@login_required
def versions_archive(request):
    template = loader.get_template('versions_archive.html')
    user = request.user
    versions = Version.objects.filter(user=user, archive=True)
    version, currentversion = current_version(request)
    state = "/versions_archive/"
    if currentversion != None:
        setattr(currentversion, "state", state)
        currentversion.save()
    if version != None:
        version_name = version.name
    else:
        version_name = ""
    # form = VersionForm
    for i in versions:
        if i == version:
            i.current = True
            i.save()
        else:
            i.current = False
            i.save()
    context = {
        'superuser': request.user.is_superuser,
        # 'form': form,
        'versions': versions,
        'version_not_selected': not check_version_selected(version),
        'version': version_name,
        }

    return HttpResponse(template.render(context, request))

@login_required
def archive_version(request, id):
    try:
        if Version.objects.get(id=id).user != request.user:
            return HttpResponseRedirect("/versions/")
    except:
        return HttpResponseRedirect("/versions/")
    x, currentversion = current_version(request)
    state = currentversion.state
    version=Version.objects.get(id=id)
    archived = version.archive
    if archived == False:
        if x != "None":
            if x == version:
                currentversion.delete()
        setattr(version, "archive", True)
        version.save()
        return HttpResponseRedirect("/versions/")
    else:
        setattr(version, "archive", False)
        version.save()
        return HttpResponseRedirect("/versions_archive/")

@login_required
def del_version(request, id):
    try:
        if Version.objects.get(id=id).user != request.user:
            return HttpResponseRedirect("/versions/")
    except:
        return HttpResponseRedirect("/versions/")
    x, currentversion = current_version(request)
    state = currentversion.state
    Version.objects.get(id=id).delete()
    
    return HttpResponseRedirect(state)

@login_required
def copy_version(request, id):
    version, currentversion = current_version(request)
    try:
        if Version.objects.get(id=id).user != request.user:
            return HttpResponseRedirect("/versions/")
    except:
        return HttpResponseRedirect("/versions/")
    
    old_ver = Version.objects.get(id=id)
    if request.method == "POST":
        form = VersionForm(request.POST, user=request.user, version=old_ver, new=False, blank=False)
        id = request.POST["id"]
        if form.is_valid():
            new_ver = form.save()
            make_copy(old_ver, new_ver)
            if currentversion != None:
                currentversion.delete()
            currentversion = CurrentVersion.objects.create(user=request.user, version=new_ver)
            return HttpResponseRedirect("/versions/")
    else:
        form = VersionForm(user=request.user, initial={'name': old_ver.name,
                                                       "user": request.user,
                                                       "notes": old_ver.notes,
                                                       "value_1": old_ver.value_1,
                                                       "value_2": old_ver.value_2,
                                                       "value_3": old_ver.value_3,
                                                       "value_4": old_ver.value_4,
                                                       "value_5": old_ver.value_5,
                                                       "value_6": old_ver.value_6,
                                                       "value_7": old_ver.value_7,
                                                       "value_8": old_ver.value_8,
                                                       "value_9": old_ver.value_9,
                                                       "value_10": old_ver.value_10
                                                       }, version=old_ver, new=False, blank=False)
    
    context = {
        'superuser': request.user.is_superuser,
        'form': form,
        "id": id,
        "name": Version.objects.get(id=id).name,
        "version": old_ver,
    }
    return render(request, 'copy_version.html', context)

@login_required
def methods(request):

    [version, currentversion] = current_version(request)
    # setattr(currentversion, "state", state)
    # form = MethodForm
    state = "/methods/"
    setattr(currentversion, "state", state)
    currentversion.save()

    template = loader.get_template('methods.html')

    methods = sorted(Method.objects.filter(version=version), key = lambda x: x.name)
 
    context = {
        # 'form': form,
        'methods': methods,
        'version': version.name,
        'superuser': request.user.is_superuser,
        }
    # currentversion.save()
    return HttpResponse(template.render(context, request))

@login_required
def edit_method(request, id):
    try:
        if Method.objects.get(id=id).version.user != request.user:
            return HttpResponseRedirect("/methods/") 
    except:
        return HttpResponseRedirect("/methods/")    

    [version, currentversion] = current_version(request)
    state = currentversion.state

    method = Method.objects.get(id=id)
    version = method.version
    if request.method == 'POST':
        post = copy.deepcopy(request.POST)
        post.update({"version": version})
        form = MethodForm(post, instance=method, version=version) 
        # form = CategoryForm(post, version=version) 
        if form.is_valid():
            form.save()
            # version = update_all(version)
            version.save()
            # currentversion = add_backup(version, currentversion)
            currentversion.save()
            return HttpResponseRedirect(state)
    else:
        form = MethodForm(instance=method, version=version, initial={"version": version})
    context = {
        'superuser': request.user.is_superuser,
        "form": form,
        "id": id,
        "version": version,
    }
    try:
        links = json.loads(method.links)
        for link in links:
            if link[1][:4] != "http":
                link[1] = "https://" + link[1]
        
            context["links"] = links
    except:
        context["links"] = ""

    return render(request, 'edit_method.html', context)     

@login_required
def edit_variables(request):
    [version, currentversion] = current_version(request)
    state = currentversion.state

    # try:
    #     if Lookup.objects.get(id=version.id).version.user != request.user:
    #         return HttpResponseRedirect("/versions/") 
    # except:
    #     return HttpResponseRedirect("/versions/")    

    variables = Lookup.objects.get(version=version)
    version = variables.version
    if request.method == 'POST':
        post = copy.deepcopy(request.POST)
        post.update({"version": version})
        form = LookupForm(post, instance=variables, user=request.user) 
        if form.is_valid():
            form.save()
            version.save()
            currentversion.save()
            return HttpResponseRedirect(state)
    else:
        form = LookupForm(instance=variables, user=request.user)
    context = {
        'superuser': request.user.is_superuser,
        "form": form,
        "version": version,
        }
    if request.user.is_superuser:
        context["note"] = "(*): Uncheck if use case req't<br>Notes:<br>-  Method requirement is where importance is defined by the method and the degree fulfilled by the use case<br>-  Use case requirement is where importance is defined by the use case and the degree fulfilled by the method<br>-  Variable factor = (1 - importance) + (importance * degree fulfilled)<br>-  Method suitability = Product of variable factors"
    else:
        context["note"] = "Notes:<br>-  Importance is defined by the method and the degree fulfilled by the use case<br>-  Variable factor = (1 - importance) + (importance * degree fulfilled)<br>-  Method suitability = Product of variable factors"

    return render(request, 'edit_variables.html', context)     

def view_method(request, index, guest):

    methods = json.loads(Master.objects.get(ref="default").methods)
    lookup = json.loads(Master.objects.get(ref="default").lookup)
    if guest == 1:
        guest = True
    else:
        guest = False

    method = {}
    for i in methods.keys():
        method[i] = methods[i][index]
    variables = []

    for i in lookup["Variable"].keys():
        if lookup["Variable"][i] != "NONE":
            variables.append([lookup["Variable"][i], method[lookup["Value"][i]]])
            # method[lookup["Variable"][i]] = method[lookup["Value"][i]]
        del method[lookup["Value"][i]]
    # print (method.items())
    try:
        links = json.loads(method["Links"])
        for i in range(len(links)):
            if links[i][1][:4] != "http":
                links[i] = [links[i][0], "https://" + links[i][1]]
    except:
        links = ""
    dmdu = method["DMDU"]
    del method["Links"]
    del method["DMDU"]
    method = [[i, j] for i,j in method.items()]
    context = {
        "method": method,
        "lookup": lookup,
        "links": links,
        "guest": guest,
        "dmdu": dmdu,
        "variables": variables
    }
    return render(request, 'view_method.html', context) 
    
@login_required
def del_method(request, id):

    try:
        if Method.objects.get(id=id).version.user != request.user:
            return HttpResponseRedirect("/methods/")
    except:
        return HttpResponseRedirect("/methods/")
    method = Method.objects.get(id=id)

    method.delete()

    return HttpResponseRedirect("/methods/")

@login_required
def add_method(request):
    [version, currentversion] = current_version(request)
    context = {
        'superuser': request.user.is_superuser,
    }    
    
    if request.method == 'POST':
        post = copy.deepcopy(request.POST)
        post.update({"version": version})
        methods = list(Method.objects.filter(version=version))
        indexes = [int(i.index) for i in methods]
        new_index = 0
        while True:
            if new_index in indexes:
                new_index +=1
            else:
                break
        post.update({"index": str(new_index)})
        form=MethodForm(post, version=version)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/methods/")

        else:
            context['form'] = form
            context["version"] = version
            return render(request, 'add_method.html', context)

    else:
        form = MethodForm(version=version, initial={"version": version})
        # form.initial = {"enabled": True}   
        context['form'] = form
        context["version"] = version
        return render(request, 'add_method.html', context)

def explore(request, **kwargs):
    if kwargs["guest"]:
        lookup = pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Lookup").to_dict()
        lookup_list = []
        index = 0
        for i in lookup["Value"].keys():
            lookup_list.append({"index": index, "name": lookup["Value"][i],"value": "50", "variable": lookup["Variable"][i],"option_reqt": lookup["Is option reqt"][i]})
            index += 1
        methods_df = pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Methods")
        methods = []
        for index, row in methods_df.iterrows():
            if row['Enabled']:
                methods.append({
                    "version": None,
                    "index": str(index),
                    "name": row['Method'],
                    "name_clean": row['Method'].replace("/", "_"),
                    "description": row['Description'],
                    "long_description": row['Long Description'],
                    "links": row['Links'],
                    "dmdu": row['DMDU'],
                    "value_1": row['value_1'],
                    "value_2": row['value_2'],
                    "value_3": row['value_3'],
                    "value_4": row['value_4'],
                    "value_5": row['value_5'],
                    "value_6": row['value_6'],
                    "value_7": row['value_7'],
                    "value_8": row['value_8'],
                    "value_9": row['value_9'],
                    "value_10": row['value_10'],
            }) 
        context = {
            'superuser': None,
            'version': False,
            'variables': lookup_list,
            'methods': methods,
            'guest': True
        }
    else:
       
        [version, currentversion] = current_version(request)
        currentversion.state = "/explore/"
        currentversion.save()

        methods = list(Method.objects.filter(version=version, enabled=True).values())
        # print(methods)

        # lookup = Lookup.objects.get(version=version)
        variables = get_variables(version)

        context = {
            'superuser': request.user.is_superuser,
            'version': version,
            'variables': variables,
            'methods': methods,
            'guest': False
        }        
    return render(request, 'explore.html', context)

@login_required
def parameters(request):
    [version, currentversion] = current_version(request)
    state = "/parameters/"
    setattr(currentversion, "state", state)
    currentversion.save()
    if Master.objects.filter(ref="default").count() != 0:
        lookup = json.loads(Master.objects.get(ref="default").lookup)
    else:    
        lookup = pd.read_excel(os.path.join(settings.BASE_DIR, "master.xlsx"), engine='openpyxl', sheet_name="Lookup").to_dict()
    variables = get_variables(version)

    # var_count = 0
    # for variable in variables:
    #     if variable["variable"] != "NONE":
    #        var_count +=1
    # col_width = str(100 / (var_count + 1)) +"%"

    methods = list(Method.objects.filter(version=version, enabled=True).values())

    var_names = []

    for variable in variables:
        if variable["variable"] !="NONE":
            var_names.append(variable["variable"])      

    for method in methods:
        vals = []        
        for variable in variables:
            if variable["variable"] !="NONE":

                vals.append({"val": str(method[variable["name"]]), "index": str(variable["index"]), "name": variable["name"]})       
        method["vals"] = vals

    context = {
        'superuser': request.user.is_superuser,
        'version': version,
        # 'variables': variables,
        'methods': methods,
        # 'col_width': col_width,
        'var_names': var_names
    } 
    return render(request, 'parameters.html', context)

@login_required
def edit_param_post(request):
    [version, currentversion] = current_version(request)
    if request.method == 'POST':

        [state, variables] = json.loads(request.POST["post_data"])
        version.value_1 = variables[0]["value"]
        version.value_2 = variables[1]["value"]
        version.value_3 = variables[2]["value"]
        version.value_4 = variables[3]["value"]
        version.value_5 = variables[4]["value"]
        version.value_6 = variables[5]["value"]
        version.value_7 = variables[6]["value"]
        version.value_8 = variables[7]["value"]
        version.value_9 = variables[8]["value"]
        version.value_10 = variables[9]["value"]
        version.save()
        return HttpResponseRedirect(state)
    else:
        return HttpResponseRedirect("/version/")

@login_required
def edit_methods_post(request):
    [version, currentversion] = current_version(request)
    if request.method == 'POST':
        [x, output] = json.loads(request.POST["post_data"])
        state = currentversion.state
        for method in list(Method.objects.filter(version=version)):
            for j in list(output[method.index].keys()):
                setattr(method, j, output[method.index][j])
            method.save()
        return HttpResponseRedirect(state)
    else:
        return HttpResponseRedirect("/version/")

@login_required
def export_method_params(request):
    [version, currentversion] = current_version(request)

    methods = list(Method.objects.filter(version=version))
    
    data = []
    for method in methods:
        data.append([method.name, method.dmdu, method.description, method.long_description, method.links, method.enabled, method.value_1, method.value_2, method.value_3, method.value_4, method.value_5, method.value_6, method.value_7, method.value_8, method.value_9, method.value_10])
    methods_df = pd.DataFrame(data, columns=["Method", "DMDU", "Description", "Long Description", "Links", "Enabled", "value_1", "value_2", "value_3", "value_4", "value_5", "value_6", "value_7", "value_8", "value_9", "value_10"])
    # 2. Create a BytesIO buffer
    lookup = Lookup.objects.get(version=version)

    data = [["value_1", lookup.value_1, lookup.value_1_is_option_reqt, version.value_1],
            ["value_2", lookup.value_2, lookup.value_2_is_option_reqt, version.value_2],
            ["value_3", lookup.value_3, lookup.value_3_is_option_reqt, version.value_3],
            ["value_4", lookup.value_4, lookup.value_4_is_option_reqt, version.value_4],
            ["value_5", lookup.value_5, lookup.value_5_is_option_reqt, version.value_5],
            ["value_6", lookup.value_6, lookup.value_6_is_option_reqt, version.value_6],
            ["value_7", lookup.value_7, lookup.value_7_is_option_reqt, version.value_7],
            ["value_8", lookup.value_8, lookup.value_8_is_option_reqt, version.value_8],
            ["value_9", lookup.value_9, lookup.value_9_is_option_reqt, version.value_9],
            ["value_10", lookup.value_10, lookup.value_10_is_option_reqt, version.value_10],
            ]
    lookup_df = pd.DataFrame(data, columns=["Value", "Variable", "Is option reqt", "Setting"])

    output = BytesIO()
    # 3. Write the DataFrame to the buffer as an Excel file
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        methods_df.to_excel(writer, index=False, sheet_name='Methods')
        lookup_df.to_excel(writer, index=False, sheet_name='Lookup')

    # 4. Set the buffer position to the beginning
    output.seek(0)

    # 5. Create the HTTP response with proper headers
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
    return response

@login_required
def reset_lookup(request):
    if Master.objects.filter(ref="default").count() > 0:
        Master.objects.get(ref="default").delete()
    return HttpResponseRedirect("/versions/")

@login_required
def import_version(request):

    [v, currentversion] = current_version(request)
    versions = Version.objects.filter(user=request.user, archive=False).order_by("name")

    if request.method == 'POST':
        # form = VersionImportForm(request.POST, request.FILES, user=request.user, other_users=False)
        form = VersionForm(request.POST, request.FILES, user=request.user, new=True, blank=False, version=None)

        if form.is_valid():
            
            if request.FILES:

                myfile = request.FILES.get('myfile')

                version = form.save()
                create_methods(version, False, myfile)

                if currentversion != None:
                    currentversion.delete()
                currentversion = CurrentVersion.objects.create(user=request.user, version=version)
                currentversion.save()
                return HttpResponseRedirect("/versions/")

        # "Node": ( Node, ["category", "version", "node_standard"], ["version", "category", "node_code"]),

        context = {
            'superuser': request.user.is_superuser,
            'form': form,
            'version_not_selected': len(versions) == 0,
    }
        return render(request, 'import_version.html', context)
    else:
        context = {
            'superuser': request.user.is_superuser,
        }
        form = VersionForm(user=request.user, new=True, blank=False, version=None, initial={"user": request.user})

        context = {
            'superuser': request.user.is_superuser,
            'form': form,
            'version_not_selected': len(versions) == 0,
    }
    return render(request, 'import_version.html', context)