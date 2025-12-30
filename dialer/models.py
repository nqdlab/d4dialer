from django.db import models

class Campaign(models.Model):
    campaign_uuid = models.CharField(max_length=255, unique=True)
    campaign_name = models.CharField(max_length=255)
    campaign_ivr_menu = models.CharField(max_length=255, null=True, blank=True)
    campaign_concurrent_calls = models.IntegerField(default=1)

    def __str__(self):
        return self.campaign_name

class CampaignLead(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='leads')
    phone_number = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.campaign.campaign_name} - {self.phone_number}"