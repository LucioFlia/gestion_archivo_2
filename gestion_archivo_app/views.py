import csv
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse


from django.template.loader import get_template
#from django.db.models.signals import post_save, post_delete

from django.contrib import messages
#from reportlab.lib.pagesizes import A4
from functools import wraps
import pdfkit
from django.db.models import Q

from .models import (
    Box,
    BoxType,
    BoxLog,
    Documentation,
    DocType,
    Area,
    SystemConfigKeyValues,
    Universe,
    User,
)

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def user_passes_test_with_message(test_func, message="You do not have permission to access this page."):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            messages.error(request, message)
           
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return _wrapped_view
    return decorator


def is_admin(user):
    return user.role == 'admin'

def is_user_or_manager(user):
    return user.role in ['user', 'manager']

@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def area_import(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if csv_file:
            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    name = row.get("name")
                    code = row.get("code")
                    is_deposit = row.get("is_deposit", "False").strip().lower() == "true"

                    if name and code:
                        # Crear el área solo si no existe otra con el mismo código
                        Area.objects.get_or_create(
                            code=code,
                            defaults={"name": name, "is_deposit": is_deposit}
                        )

                messages.success(request, "Areas imported successfully.")
                return redirect("area_list")

            except Exception as e:
                messages.error(request, f"Error importing areas: {str(e)}")

    return render(request, "area_import.html")



@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def area_list(request):
    areas = Area.objects.all()
    return render(request, "area_list.html", {"areas": areas})


@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def area_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        is_deposit = request.POST.get("is_deposit") == "on"

        if name and code:
            Area.objects.create(name=name, code=code, is_deposit=is_deposit)
            return redirect("area_list")

    return render(request, "area_create.html")




@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def area_update(request, area_id):
    area = get_object_or_404(Area, id=area_id)

    if request.method == "POST":
        area.name = request.POST.get("name", area.name)
        area.code = request.POST.get("code", area.code)
        area.is_deposit = request.POST.get("is_deposit") == "on"
        area.save()
        return redirect("area_list")

    return render(request, "area_update.html", {"area": area})


@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def area_delete(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    if request.method == "POST":
        area.delete()
        return redirect("area_list")
    return render(request, "area_delete.html", {"area": area})

@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def user_list(request):
    users = User.objects.all()
    return render(request, "user_list.html", {"users": users})

@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def user_create(request):
    ROLE_CHOICES = User.ROLE_CHOICES
    areas = Area.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        role = request.POST.get("role")
        area_id = request.POST.get("area")
        deposit_id = request.POST.get("deposit")

        if username and password and role:
            area = Area.objects.get(id=area_id) if area_id else None
            deposit = Area.objects.get(id=deposit_id) if deposit_id else None

            User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role,
                area=area,
                deposit=deposit
            )
            return redirect("user_list")

    return render(request, "user_create.html", {"roles": ROLE_CHOICES, "areas": areas})


@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def user_update(request, user_id):
    userd = get_object_or_404(User, id=user_id)
    print(userd)
    areas = Area.objects.all()
    ROLE_CHOICES = User.ROLE_CHOICES

    if request.method == "POST":
        userd.username = request.POST.get("username", userd.username)
        userd.first_name = request.POST.get("first_name", userd.first_name)
        userd.last_name = request.POST.get("last_name", userd.last_name)
        userd.role = request.POST.get("role", userd.role)
        area_id = request.POST.get("area")
        deposit_id = request.POST.get("deposit")
        userd.area = Area.objects.get(id=area_id) if area_id else userd.area
        userd.deposit = Area.objects.get(id=deposit_id) if deposit_id else userd.deposit
        password = request.POST.get("password")
        if password:
            userd.set_password(password)
        userd.save()
        return redirect("user_list")

    return render(request, "user_update.html", {"user_aux": userd, "areas": areas, "roles": ROLE_CHOICES})



@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return render(request, "user_delete.html", {"user": user})

@login_required
@user_passes_test_with_message(is_admin, "Only the admin can access this page.")
def user_import(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if csv_file:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                area = Area.objects.get(id=row["area_id"]) if row.get("area_id") else None
                User.objects.create_user(
                    username=row["username"],
                    email=row["email"],
                    password=row["password"],
                    role=row["role"],
                    area=area
                )
            return redirect("user_list")
    return render(request, "user_import.html")




def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('main') 
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def error_403(request, exception):
    return render(request, "403.html", status=403)



def logout_view(request):
    logout(request)
    return redirect('login') 




@login_required
def create_box_type(request):
    # Handle deletion
    if 'delete_id' in request.GET:
        try:
            delete_id = request.GET.get('delete_id')
            box_type = get_object_or_404(BoxType, id=delete_id)
            box_type.delete()
            messages.success(request, "The box type has been deleted.")
            return redirect('create_box_type')  # Redirect to refresh the list
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('create_box_type')


    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        try:
            if name:  # Validate input
                BoxType.objects.create(name=name, description=description)
                messages.success(request, "The box type has been created.")
                return redirect('create_box_type')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('create_box_type')
            

    # Fetch all BoxType objects
    items = BoxType.objects.all().order_by('id')
    return render(request, "create_box_type.html", {"items": items})


@login_required
def create_box_type_modal(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:  # Validar el nombre
            new_type = BoxType.objects.create(name=name, description=description)
            return JsonResponse({'success': True, 'id': new_type.id, 'name': new_type.name})
        else:
            return JsonResponse({'success': False, 'error': 'The name field is required.'}, status=400)

    return render(request, 'create_box_type_modal.html')


@login_required
def create_doc_type_modal(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('detail', '').strip()

        if name:  # Validar el nombre
            new_type = DocType.objects.create(name=name, description=description)
            return JsonResponse({'success': True, 'id': new_type.id, 'name': new_type.name})
        else:
            return JsonResponse({'success': False, 'error': 'The name field is required.'}, status=400)

    return render(request, 'create_doc_type_modal.html')



@login_required
def create_doc_type(request):
    # Handle deletion
    if 'delete_id' in request.GET:
        try:
            delete_id = request.GET.get('delete_id')
            doc_type = get_object_or_404(DocType, id=delete_id)
            doc_type.delete()
            return redirect('create_doc_type')  # Redirect to refresh the list
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('create_doc_type')

    # Handle form submission
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')

            if name:  # Validate input
                DocType.objects.create(name=name, description=description)
                return redirect('create_doc_type')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('create_doc_type')

    # Fetch all DocType objects
    items = DocType.objects.all().order_by('id')

    context = {
        'items': items,
    }
    return render(request, 'create_doc_type.html', context)

@login_required
def main(request):
    # get the boxes 
    user_area = request.user.area
    user_deposit = request.user.deposit
    user_role = request.user.role
    if user_role == 'admin':
        items = Box.objects.all().order_by('-name')
    elif user_role == 'archive_responsible':
        items = Box.objects.filter(Q(current_area=user_area) | Q(current_area=user_deposit)).order_by('-name')

    else:
        items = Box.objects.filter(area=user_area).order_by('-name')
    
    return render(request, "main.html", {"items": items})

# Variable global para indicar si la descarga está lista 
is_download_ready = False

@login_required
def check_download_status(request):
    global is_download_ready
    # Verificar si la descarga está lista
    #print (is_download_ready)
    response = JsonResponse({"ready": is_download_ready})
    is_download_ready = False
    return response

@login_required
def config_keys_values(request):
    configs = SystemConfigKeyValues.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        # Guardar o editar una clave
        if action == "save":
            config_id = request.POST.get("config_id")
            key = request.POST.get("key")
            value = request.POST.get("value")
            description = request.POST.get("description")

            if config_id:
                # Editar clave existente
                config = get_object_or_404(SystemConfigKeyValues, id=config_id)
                config.key = key
                config.value = value
                config.description = description
                config.save()
                messages.success(request, "Key updated successfully.")
            else:
                # Crear nueva clave
                SystemConfigKeyValues.objects.create(key=key, value=value, description=description)
                messages.success(request, "Key added successfully.")

        # Eliminar una clave
        elif action == "delete":
            config_id = request.POST.get("config_id")
            config = get_object_or_404(SystemConfigKeyValues, id=config_id)
            config.delete()
            messages.success(request, "Key deleted successfully.")

        return redirect('config_keys_values')

    return render(request, 'config_keys_values.html', {'configs': configs})


@login_required
@user_passes_test_with_message(is_user_or_manager, message="Only users and managers can access this page.")

def create_box(request):
    area = request.user.area
    user = request.user
    first_name = request.user.first_name
    box_types = BoxType.objects.all()
    current_year = datetime.now().year
    destruction_years = [(0, 'Never')] + [(year, str(year)) for year in range(current_year, current_year + 25)]
    suggested_year = current_year + 5

    if request.method == 'POST':
        # Capture form data
        box_type = request.POST.get('box_type')
        description = request.POST.get('description')
        destruction_year = request.POST.get('destruction_year')
        name='to be defined'
        box_type = get_object_or_404(BoxType, id=box_type)
        box = Box(
            box_type=box_type,
            description=description,
            user=user,
            area=area,
            destruction_year=destruction_year,
            name=name,
            status='open',
            creation_date=datetime.now()  
        )
        # Pass the temporary Box object to the preview template
        return render(request, 'preview_box.html', {'box': box, 'user': user, 'area': area})
        # Initial form display
    
    boxes = Box.objects.filter(current_area=area, status='open').order_by('-creation_date')
    return render(request, 'create_box.html', {
        'box_types': box_types,
        'destruction_years': destruction_years,
        'suggested_year': suggested_year,
        'boxes': boxes,
        'user_area': area
    })

   





@login_required
def save_and_generate_pdf(request):
    
    global is_download_ready
    
    area = request.user.area
    user = request.user

    if request.method == 'POST':
        box_type_id = request.POST.get('box_type_id')
        description = request.POST.get('description')
        destruction_year = request.POST.get('destruction_year')
        name=request.POST.get('box_name')
       # Retrieve the BoxType object
        box_type = BoxType.objects.get(pk=box_type_id)
        
        try:
            # Create the box
            box = Box.objects.create(
                box_type=box_type,
                description=description,
                user=user,
                area=area,  # Assuming the user has an area associated
                status='open',
                current_area = area,
                destruction_year = destruction_year,
                name=name
            )
            
            
            BoxLog.objects.create(
                log_type='new',
                box=box,
                previous_status='N/A',
                new_status=box.status,
                observations='Box created',
                user=box.user,
                user_area=box.user.area
            )
            path_to_wkhtmltopdf = r"./wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
            #print(box_fieldss )
            template = get_template("box_pdf.html")

            html = template.render({"box": box})

            pdf = pdfkit.from_string(html, False, configuration=config)
            messages.success(request, "The box has been created, and the PDF has been downloaded. Please check your downloads folder.")
            # Download PDF
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = f"attachment; filename=box_{box.name}.pdf"
            is_download_ready = True
            return response
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect("create_box")

@login_required
def save_and_generate_security_seal(request, box_id):
    global is_download_ready
    box = get_object_or_404(Box, id=box_id)
    
    area = request.user.area
    user = request.user
    previous_status = box.status

    if request.method == 'POST':
        box.status = 'closed'
        box.close_date = datetime.now()  
        box.save()
        BoxLog.objects.create(
        log_type='status_change',
        box=box,
        previous_status=previous_status,
        new_status=box.status,
        observations='Box closure approved.',
        user=user,
        user_area=area
        )
        options = {
        'page-size': 'A4',
        'orientation': 'Landscape',  # Forzar apaisado
        'encoding': 'UTF-8',
        'no-outline': None,
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        }
        path_to_wkhtmltopdf = r"./wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
        template = get_template("box_security_seal_pdf.html")
        html = template.render({"box": box, "area": request.user.area, "user": request.user})
        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
        messages.success(request, 'The box has been approved and is now waiting to be sent to the archive.')
        # Download PDF
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=security_seal_box_{box.name}.pdf"
        is_download_ready = True
        return response
    return redirect("main")

@login_required
def print_security_seal(request, box_id):
    global is_download_ready
    box = get_object_or_404(Box, id=box_id)

    if request.method == 'POST':
        path_to_wkhtmltopdf = r"./wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
        template = get_template("box_security_seal_pdf.html")
        html = template.render({"box": box, "area": request.user.area, "user": request.user})
        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
        messages.success(request, 'The security seal has been successfully generated and saved in the Downloads folder.')
        # Download PDF
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=security_seal_box_{box.name}.pdf"
        is_download_ready = True
        return response
    
    return redirect("main")



@login_required
def add_documentation(request, box_id):
    box = get_object_or_404(Box, id=box_id, status="open")  
    documentations = box.documentations.all() 

    if request.method == "POST":
        cuit_number = request.POST.get("cuit_number")
        name = request.POST.get("name")
        doc_type_id = request.POST.get("doc_type")
        description = request.POST.get("description")
        corpus = request.POST.get("corpus")
        sheets = request.POST.get("sheets")

        # Crear la documentación
        doc_type = get_object_or_404(DocType, id=doc_type_id)
        documentation = Documentation(
            cuit_number=cuit_number,
            name=name,
            doc_type=doc_type,
            description=description,
            corpus=corpus,
            sheets=sheets,
            created_by=request.user,
            box=box
        )
        documentation.save()
        BoxLog.objects.create(
            log_type='doc_added',
            box=box,
            doc_added=documentation,
            previous_status=box.status,
            new_status=box.status,
            observations=f"Document (id:{documentation.id}) '{cuit_number}-{name}' of {sheets} sheets added.",
            user=request.user,
            user_area=request.user.area
        )
        box.update_total_sheets()  # Actualizar el total de hojas
        messages.success(request, "The documantation was added.")
        if "save_and_continue" in request.POST:
            return redirect("add_documentation", box_id=box.id)
        elif "save_and_exit" in request.POST:
            return redirect("edit_box_documentation", box_id=box.id)

    # En caso de GET, mostrar el formulario
    return render(request, "add_documentation.html", {
        "box": box,
        "doc_types": DocType.objects.all(),
        "documentations": documentations,
    })
   
def create_doctype_modal(request):
    if request.method == "POST":
        name = request.POST.get("name")
        detail = request.POST.get("detail")

        # Create new DocType
        if name:
            DocType.objects.create(name=name, detail=detail)
            messages.success(request, f"DocType '{name}' added successfully!")
        else:
            messages.error(request, "DocType name is required.")
        return redirect("add_documentation", box_id=request.GET.get("box_id"))

def edit_box_documentation(request, box_id):
    """
    View to display the list of documentation for a specific box with options to add and delete.
    """
    box = get_object_or_404(Box, id=box_id)
    documentations = box.documentations.all()  
    can_manage_box = box.status == 'open' and (request.user.role == 'manager' or request.user.role == 'user')

    return render(request, "edit_box_documentation.html", {
        "box": box,
        "documentations": documentations,
        "can_manage_box": can_manage_box
    })


@login_required
def edit_documentation(request, box_id, doc_id):
    """
    View to edit a specific documentation for a given box.
    """
    box = get_object_or_404(Box, id=box_id)
    documentation = get_object_or_404(Documentation, id=doc_id, box=box)
    doc_types = DocType.objects.all()
    print (doc_types)

    if request.method == "POST":
        # Procesar datos enviados por el usuario
        cuit_number = request.POST.get("cuit_number")
        name = request.POST.get("name")
        doc_type_id = request.POST.get("doc_type")
        description = request.POST.get("description")
        corpus = request.POST.get("corpus")
        sheets = request.POST.get("sheets")

        # Validar y guardar los cambios
        if cuit_number and name and doc_type_id and corpus and sheets.isdigit():
            documentation.cuit_number = int(cuit_number)
            documentation.name = name
            documentation.doc_type_id = doc_type_id
            documentation.description = description
            documentation.corpus = corpus
            documentation.sheets = int(sheets)

            documentation.save()
            box.update_total_sheets()
            
            # Log the update in BoxLog
            BoxLog.objects.create(
                log_type='doc_edited',
                box=box,
                doc_added=documentation,
                previous_status=box.status,
                new_status=box.status,
                observations=f"Document (id:{documentation.id}) '{cuit_number}-{name}' of {sheets} sheets edited.",
                user=request.user,
                user_area=request.user.area
            )
            
            messages.success(request, "The documentation was updated.")
            return redirect("edit_box_documentation", box_id=box.id)
 
    return render(request, "edit_documentation.html", {
        "box": box,
        "documentation": documentation,
        "doc_types": doc_types,
 
    })





def delete_documentation(request, doc_id):
    """
    View to delete a specific documentation.
    """
    documentation = get_object_or_404(Documentation, id=doc_id)
    box = documentation.box  
    documentation.box = None
    # Eliminar la documentación
    documentation.save()
        # Registrar en BoxLog
    BoxLog.objects.create(
        log_type='doc_removed',
        box=box,
        doc_removed=documentation,
        previous_status=box.status,
        new_status=box.status,
        observations=f"Document (id:{documentation.id}) '{documentation.name}' unlinked from box.",
        user=request.user,
        user_area=request.user.area
    )
    box.update_total_sheets()  # Actualizar el total de hojas en la caja

    # Redirigir de nuevo a la vista de edición de documentaciones
    return redirect("edit_box_documentation", box_id=box.id)


@login_required
def request_close_box(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    
    if box.status == 'open':
        box.status = 'waiting_close'
        box.save()
    
        BoxLog.objects.create(
        log_type='status_change',
        box=box,
        previous_status='open',
        new_status=box.status,
        observations='Close request submitted.',
        user=request.user,
        user_area=request.user.area
    )
    return redirect('main')
  
        

@login_required
def approve_close_box(request, box_id):
    box = get_object_or_404(Box, id=box_id)

    if box.status == 'waiting_close' and request.user.role == 'manager':
        return render(request, 'preview_security_seal.html', {'box': box, 'user': request.user, 'area': request.user.area})
        
    else:
        messages.error(request, 'You have not permission to approve close or th box is closed.')

    return redirect('main')



@login_required
def reject_box_close(request, box_id):
    box = get_object_or_404(Box, id=box_id)
  
    if request.method == 'POST' and box.status == 'waiting_close' and request.user.role == 'manager':
        message = request.POST.get('message')

        # Capture the previous status before updating
        previous_status = box.status

        # Update the box status to 'open'
        box.status = 'open'
        box.save()

        # Log the rejection in BoxLog
        BoxLog.objects.create(
            log_type='status_change',
            box=box,
            previous_status=previous_status,
            new_status=box.status,
            observations=f'Closure rejected: {message}',
            user=request.user,
            user_area=request.user.area
        )

        messages.success(request, f'The closure of box "{box.name}" was successfully rejected.')
    else:
        messages.error(request, 'You do not have permission to perform this action.')

    return redirect('main')


def get_ar(user):
    """
        returns the first AR of the user
    """
    if user.is_authenticated and hasattr(user, 'deposit'):
        try:
            archive_responsible = User.objects.filter(
                role='archive_responsible',
                deposit=user.deposit
            ).first()
            return  archive_responsible if archive_responsible else None
        except Exception as e:
            # Optional: Log the exception if needed
            print(f"Error in archive_responsible: {e}")
    return  None

@login_required
def send_box_to_archive(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    
    if box.status == 'closed' and request.user.role == 'manager':
        previous_area = box.area
        box.status = 'waiting_archive'
        archive = get_ar(request.user).area
        box.current_area = archive
        print (archive.name)
        box.save()
        message = request.POST.get('message')
        
        BoxLog.objects.create(
            log_type='area_change',
            box=box,
            previous_status = box.status,
            new_status = box.status,
            area_origin=previous_area,
            area_destination = box.current_area,
            observations=f'Box sent to archive. Message: { message }',
            user=request.user,
            user_area=request.user.area
    )
    return redirect('main')

def box_logs(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    logs = BoxLog.objects.filter(box=box).order_by('-log_date')

    context = {
        'box': box,
        'logs': logs,
    }
    return render(request, 'box_logs.html', context)