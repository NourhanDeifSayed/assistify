import logging
from django.core.management.base import BaseCommand
from assistify.ml_models.product_recommendation.model import ProductRecommendationModel

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Trains the LightFM recommendation model and saves it to disk.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing LightFM model for training...'))
        model = ProductRecommendationModel()
        
        if getattr(model, 'LIGHTFM_AVAILABLE', False):
            self.stdout.write(self.style.SUCCESS('LightFM is available. Starting training...'))
            try:
                if model.train():
                    self.stdout.write(self.style.SUCCESS('LightFM model trained and saved successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('LightFM model training failed.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred during LightFM training: {e}'))
        else:
            self.stdout.write(self.style.WARNING('LightFM is not available. Skipping training.'))
