from django.urls import path
from . import views
from .views_public import ICTSHomeView

app_name = "icts"

urlpatterns = [
    path("", ICTSHomeView.as_view(), name="home"),

    # Usa la NUEVA vista
    path("dashboard/", views.icts_user_dashboard, name="dashboard"),
    path("user/", views.icts_user_dashboard, name="user_dashboard"),

    path("my/", views.my_proposals, name="my_proposals"),
    path("proposal/new/", views.proposal_create, name="proposal_create"),
    path("proposal/<int:pk>/", views.proposal_detail, name="proposal_detail"),
    path("proposal/<int:pk>/edit/", views.proposal_edit, name="proposal_edit"),
    path("proposal/<int:pk>/submit/", views.proposal_submit, name="proposal_submit"),
    path("proposal/<int:pk>/decide/", views.proposal_decide, name="proposal_decide"),
    path("proposal-evaluation/", views.proposal_evaluation, name="proposal_evaluation"),
    path("reviews/inbox/", views.reviewer_inbox, name="reviewer_inbox"),
    path("reviews/dashboard/", views.reviewer_dashboard_new, name="reviewer_dashboard_new"),
    path("reviews/history/", views.review_history, name="review_history"),
    path("responsable/", views.responsable_dashboard, name="responsable_dashboard"),
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("register/", views.RegisterICTSView.as_view(), name="register"),
    path("users/pending/", views.pending_users, name="pending_users"),
    path("users/admin/", views.users_admin, name="users_admin"),
    path("users/approve/<int:user_id>/", views.approve_user, name="approve_user"),
    path("users/reject/<int:user_id>/", views.reject_user, name="reject_user"),
    path("facilities/<slug:slug>/", views.facility_info, name="facility_info"),
]
