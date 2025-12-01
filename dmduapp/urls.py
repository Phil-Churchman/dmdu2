from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [

    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", views.signup, name="signup"),
    path("change_password/", views.change_password, name="change_password"),

    path("home/", views.versions, name="versions"),
    path("guest/", views.explore, {'guest': True}, name="guest"),
    # path("home/", views.versions, name="versions"),
    path("", views.versions, name="versions"),
    path("versions/", views.versions, name="versions"),
    path("add_version/", views.add_version, {"blank": False}, name="add_version"),
    path("add_version_blank/", views.add_version, {"blank": True}, name="add_version"),
    path("edit_version/<int:id>", views.edit_version, name="edit_version"),
    path("cancel/", views.cancel, name="cancel"),
    path("set_version/<int:id>/", views.set_version, name="set_version"),
    path("versions_archive/", views.versions_archive, name="versions_archive"),
    path("archive_version/<int:id>", views.archive_version, name="archive_version"),
    path("del_version/<int:id>/", views.del_version, name="del_version"),
    
    path("copy_version/<int:id>", views.copy_version, name="copy_version"),


    path("methods/", views.methods, name="methods"),
    path("explore/", views.explore, {'guest': False}, name="explore"),
    path("parameters/", views.parameters, name="parameters"),
    path("edit_method/<int:id>/", views.edit_method, name="edit_method"),
    path("edit_variables/", views.edit_variables, name="edit_variables"),
    path("view_method/<str:index>/<int:guest>", views.view_method, name="view_method"),
    path("del_method/<int:id>/", views.del_method, name="del_method"),
    path("add_method/", views.add_method, name="add_method"),
    # path("edit_params/", views.edit_params, name="edit_params"),

    path("edit-param-post/", views.edit_param_post, name="edit_param_post"),
    path("edit-methods-post/", views.edit_methods_post, name="edit_methods_post"),
    path("export_method_params/", views.export_method_params, name="export_method_params"),
    path("reset_lookup/", views.reset_lookup, name="reset_lookup"),

    path("import_version/", views.import_version, name="import_version"),
    path("simple_view_toggle/<int:id>/", views.simple_view_toggle, name="simple_view_toggle"),

]
