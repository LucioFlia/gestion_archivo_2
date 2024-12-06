from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.template.loader import get_template
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (
    Box,
    BoxType,
    BoxLog,
    Documentation,
    DocType,
    Area,
    SystemConfigKeyValues,
    Universe,
)

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pdfkit
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('main')  # Cambia 'main' por la vista principal de tu sistema
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def error_403(request, exception):
    return render(request, "403.html", status=403)



def logout_view(request):
    logout(request)
    return redirect('login')  # Cambia 'login' por el nombre de tu vista de inicio de sesión




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
        delete_id = request.GET.get('delete_id')
        doc_type = get_object_or_404(DocType, id=delete_id)
        doc_type.delete()
        return redirect('create_doc_type')  # Redirect to refresh the list

    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:  # Validate input
            DocType.objects.create(name=name, description=description)
            return redirect('create_doc_type')

    # Fetch all DocType objects
    items = DocType.objects.all().order_by('id')

    context = {
        'items': items,
    }
    return render(request, 'create_doc_type.html', context)

@login_required
def create_box(request):
    user_area = request.user.area
    box_types = BoxType.objects.all()  # Retrieve all available box types
    current_year = datetime.now().year
    destruction_years = list(range(current_year, 2100))
    suggested_year = current_year + 5
    boxes = Box.objects.filter(current_area=user_area, status='open').order_by('-creation_date') 
    return render(request, 'create_box.html', {'box_types': box_types, 
                                               'destruction_years': destruction_years,
                                               'suggested_year': suggested_year,
                                               'boxes': boxes,
                                               'user_area': user_area})



@login_required
def preview_box(request):
    if request.method == "POST":
        # Captura todos los datos enviados desde el formulario
        box_data = request.POST.dict()  # Convierte los datos POST a un diccionario
        box_fields = {k: v for k, v in box_data.items() if not k.startswith("_")}
        return render(request, "preview_box.html", {"box_fields": box_fields})
    return redirect("create_box")



@login_required
def config_keys_values(request):
    if request.user.role != 'admin':  # Verificar si el rol es admin
        raise PermissionDenied("You do not have access to this page.")
    if request.method == "POST":
        key = request.POST.get("key")
        value = request.POST.get("value")
        description = request.POST.get("description")

        # Validar si la clave ya existe
        if SystemConfigKeyValues.objects.filter(key=key).exists():
            configs = SystemConfigKeyValues.objects.all()
            return render(request, "config_keys_values.html", {
                "configs": configs,
                "error": "The key already exists."
            })

        # Crear o actualizar la configuración
        SystemConfigKeyValues.objects.create(key=key, value=value, description=description)
        return redirect("config_keys_values")

    # Mostrar todas las configuraciones
    configs = SystemConfigKeyValues.objects.all()
    return render(request, "config_keys_values.html", {"configs": configs})

@login_required
def main(request):
    # Filter open boxes
    items = Box.objects.filter(status="open").order_by('-name')
    return render(request, "main.html", {"items": items})

# Variable global para indicar si la descarga está lista (podría usarse una solución más robusta como un cache)
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
def save_and_generate_pdf(request):
    
    global is_download_ready
    
    user_area = request.user.area
    if request.method == 'POST':
        box_type_id = request.POST.get('box_type')
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
                user=request.user,
                area=user_area,  # Assuming the user has an area associated
                status='open',
                current_area = user_area,
                destruction_year = destruction_year,
                name=name
            )
            box_fields = {k: v for k, v in box.__dict__.items() if not k.startswith("_")}
        
            path_to_wkhtmltopdf = r"./wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
            template = get_template("box_pdf.html")
            html = template.render({"box_fields": box_fields})
            pdf = pdfkit.from_string(html, False, configuration=config)
            messages.success(request, "The box has been created, and the PDF has been downloaded. Please check your downloads folder.")
            # Descargar el PDF
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = f"attachment; filename=box_{box.id}.pdf"
            is_download_ready = True
            return response
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect("create_box")



@login_required
def add_documentation(request, box_id):
    box = get_object_or_404(Box, id=box_id, status="open")  
    documentations = box.documentations.all() 

    if request.method == "POST":
        print (request.POST)
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
        box.update_total_sheets()  # Actualizar el total de hojas
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

    return render(request, "edit_box_documentation.html", {
        "box": box,
        "documentations": documentations,
    })


from django.shortcuts import get_object_or_404, redirect, render
from .models import Box, Documentation

def edit_documentation(request, box_id, doc_id):
    """
    View to edit a specific documentation for a given box.
    """
    box = get_object_or_404(Box, id=box_id)
    documentation = get_object_or_404(Documentation, id=doc_id, box=box)

    if request.method == "POST":
        # Procesar datos enviados por el usuario
        name = request.POST.get("name")
        sheets = request.POST.get("sheets")
        description = request.POST.get("description")

        # Validar y guardar los cambios
        if name and sheets.isdigit():
            documentation.name = name
            documentation.sheets = int(sheets)
            documentation.description = description
            documentation.save()
            box.update_total_sheets()  # Actualizar el total de hojas
            return redirect("edit_box_documentation", box_id=box.id)
    else:
        # Datos iniciales para el formulario
        initial_data = {
            "name": documentation.name,
            "sheets": documentation.sheets,
            "description": documentation.description,
        }

    return render(request, "edit_documentation.html", {
        "box": box,
        "documentation": documentation,
        "initial_data": initial_data,
    })


def delete_documentation(request, doc_id):
    """
    View to delete a specific documentation.
    """
    documentation = get_object_or_404(Documentation, id=doc_id)
    box = documentation.box  # Guardar referencia a la caja antes de eliminar

    # Eliminar la documentación
    documentation.delete()
    box.update_total_sheets()  # Actualizar el total de hojas en la caja

    # Redirigir de nuevo a la vista de edición de documentaciones
    return redirect("edit_box_documentation", box_id=box.id)