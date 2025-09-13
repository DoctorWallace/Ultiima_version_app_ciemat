from django.contrib import admin
from .models import (
    Facility,
    AccessProposal,
    Participant,
    ProposalReview,
    ICTSUserProfile,
)

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0

@admin.register(AccessProposal)
class AccessProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "applicant", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "applicant__username", "applicant__email")
    inlines = [ParticipantInline]
    filter_horizontal = ("facilities",)

@admin.register(ICTSUserProfile)
class ICTSUserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_siglas", "center", "phone", "validated", "created_at")
    search_fields = ("user__username", "user__email", "center", "phone")
    list_filter = ("validated", "created_at")

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(ProposalReview)
class ProposalReviewAdmin(admin.ModelAdmin):
    list_display = ("proposal", "reviewer", "decision", "updated_at")
    list_filter = ("decision", "updated_at")
    search_fields = ("proposal__title", "reviewer__username", "reviewer__email")
