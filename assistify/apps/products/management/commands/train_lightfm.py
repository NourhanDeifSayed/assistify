import logging
from django.core.management.base import BaseCommand
from assistify.ml_models.product_recommendation.model import ProductRecommendationModel

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates and saves product embeddings for semantic search.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing semantic recommendation model...'))
        try:
            model = ProductRecommendationModel()
            if model.generate_product_embeddings():
                self.stdout.write(self.style.SUCCESS('Product embeddings generated and saved successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to generate product embeddings.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during embedding generation: {e}'))
