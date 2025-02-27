from django.urls import path
from .views import (
    CrearListarUnidadCurricular,
    ObtenerActualizarEliminarUnidadCurricular,
    CrearListarPlanAprendizaje,
    ObtenerActualizarEliminarPlanAprendizaje,
    CrearListarObjetivoPlanAprendizaje,
    ObtenerActualizarEliminarObjetivoPlanAprendizaje,
    CrearListarPlanEvaluacion,
    ObtenerActualizarEliminarPlanEvaluacion,
    CrearListarItemPlanEvaluacion,
    ObtenerActualizarEliminarItemPlanEvaluacion,
)

urlpatterns = [
    # URLs para UnidadCurricular
    path('unidades-curriculares/', CrearListarUnidadCurricular.as_view(), name='unidades-curriculares-list-create'),
    path('unidades-curriculares/<pk>/', ObtenerActualizarEliminarUnidadCurricular.as_view(), name='unidades-curriculares-retrieve-update-destroy'),

    # URLs para PlanAprendizaje
    path('planes-aprendizaje/', CrearListarPlanAprendizaje.as_view(), name='planes-aprendizaje-list-create'),
    path('planes-aprendizaje/<pk>/', ObtenerActualizarEliminarPlanAprendizaje.as_view(), name='planes-aprendizaje-retrieve-update-destroy'),

    # URLs para ObjetivoPlanAprendizaje
    path('planes-aprendizaje/<plan_aprendizaje_pk>/objetivos/', CrearListarObjetivoPlanAprendizaje.as_view(), name='objetivos-aprendizaje-list-create'),
    path('objetivos-aprendizaje/<pk>/', ObtenerActualizarEliminarObjetivoPlanAprendizaje.as_view(), name='objetivos-aprendizaje-retrieve-update-destroy'),

    # URLs para PlanEvaluacion
    path('planes-aprendizaje/<plan_aprendizaje_pk>/evaluaciones/', CrearListarPlanEvaluacion.as_view(), name='planes-evaluacion-list-create'),
    path('planes-evaluacion/<pk>/', ObtenerActualizarEliminarPlanEvaluacion.as_view(), name='planes-evaluacion-retrieve-update-destroy'),

    # URLs para ItemPlanEvaluacion
    path('planes-evaluacion/<plan_evaluacion_pk>/items/', CrearListarItemPlanEvaluacion.as_view(), name='items-evaluacion-list-create'),
    path('items-evaluacion/<pk>/', ObtenerActualizarEliminarItemPlanEvaluacion.as_view(), name='items-evaluacion-retrieve-update-destroy'),
]