from django.contrib import admin
from django.urls import path, include
from gestion_archivo_app.views import main, create_box, create_box_type, create_doc_type, create_box_type_modal, config_keys_values, preview_box, save_and_generate_pdf, check_download_status
from gestion_archivo_app.views import add_documentation, create_doc_type_modal, edit_box_documentation,edit_documentation, delete_documentation, login_view, logout_view
from django.shortcuts import redirect
from gestion_archivo_app.views import user_list, user_create, user_update, user_delete, user_import
from gestion_archivo_app.views import area_list, area_create, area_update, area_delete, area_import, request_close_box, approve_close_box, send_box_to_archive


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
     path('logout/', logout_view, name='logout'),

    path('main/', main, name='main'),
    path('', lambda request: redirect('main', permanent=False)),
    path('create/box-type/', create_box_type, name='create_box_type'),
    path('create/doc-type/', create_doc_type, name='create_doc_type'),
    path('create/box/', create_box, name='create_box'),
    path('config_keys_values/', config_keys_values, name='config_keys_values'),
    path('preview/box/', preview_box, name='preview_box'),
    path('save-and-generate-pdf/', save_and_generate_pdf, name='save_and_generate_pdf'),
    path('download/status/', check_download_status, name='check_download_status'),
    path('box/<int:box_id>/add-documentation/', add_documentation, name='add_documentation'),
    path('create/box_type/modal/', create_box_type_modal, name='create_box_type_modal'),
    path('create/doc-type/modal/', create_doc_type_modal, name='create_doc_type_modal'),
    path("box/<int:box_id>/edit-box_documentation/", edit_box_documentation, name="edit_box_documentation"),
    path("box/<int:box_id>/edit-documentation/<int:doc_id>/", edit_documentation, name="edit_documentation"),
    path("documentation/<int:doc_id>/delete/", delete_documentation, name="delete_documentation"),
    path("users/", user_list, name="user_list"),
    path("users/create/", user_create, name="user_create"),
    path("users/update/<int:user_id>/", user_update, name="user_update"),
    path("users/delete/<int:user_id>/", user_delete, name="user_delete"),
    path("users/import/", user_import, name="user_import"),
    path("areas/", area_list, name="area_list"),
    path("areas/create/", area_create, name="area_create"),
    path("areas/update/<int:area_id>/", area_update, name="area_update"),
    path("areas/delete/<int:area_id>/", area_delete, name="area_delete"),
    path("areas/import/", area_import, name="area_import"),
    path("box/<int:box_id>/request-close/", request_close_box, name="request_close_box"),
    path("box/<int:box_id>/approve-close/", approve_close_box, name="approve_close_box"),
    path("box/<int:box_id>/send-to-archive/", send_box_to_archive, name="send_box_to_archive"),
]





    
    
