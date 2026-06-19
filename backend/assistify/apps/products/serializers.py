from rest_framework import serializers
from .models import Product, ProductBenefit, Offer
class ProductBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBenefit
        fields = ("id", "text", "order")
class RelatedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "currency", "emoji", "description")
class ProductSerializer(serializers.ModelSerializer):
    benefits = ProductBenefitSerializer(many=True, read_only=True)
    related_products = RelatedProductSerializer(many=True, read_only=True)
    offer = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "currency",
            "emoji",
            "is_active",
            "category",
            "stock",
            "image",
            "benefits",
            "related_products",
            "offer",
            "created_at",
            "updated_at",
        )
    def get_offer(self, obj):
        try:
            offer = obj.offer
            if offer.is_active:
                return OfferSerializer(offer).data
        except Offer.DoesNotExist:
            pass
        return None
class ProductWriteSerializer(serializers.ModelSerializer):
    benefits = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    related_product_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Product.objects.all(), write_only=True, required=False, source="related_products"
    )
    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "price", "currency", "emoji",
            "is_active", "category", "stock", "image", "benefits", "related_product_ids",
        )
    def create(self, validated_data):
        benefits_data = validated_data.pop("benefits", [])
        related = validated_data.pop("related_products", [])
        product = Product.objects.create(**validated_data)
        product.related_products.set(related)
        for i, text in enumerate(benefits_data):
            ProductBenefit.objects.create(product=product, text=text, order=i)
        return product
    def update(self, instance, validated_data):
        benefits_data = validated_data.pop("benefits", None)
        related = validated_data.pop("related_products", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if related is not None:
            instance.related_products.set(related)
        if benefits_data is not None:
            instance.benefits.all().delete()
            for i, text in enumerate(benefits_data):
                ProductBenefit.objects.create(product=instance, text=text, order=i)
        return instance
class OfferSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_emoji = serializers.CharField(source="product.emoji", read_only=True)
    original_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    class Meta:
        model = Offer
        fields = (
            "id",
            "product",
            "product_name",
            "product_emoji",
            "original_price",
            "discount_percent",
            "discounted_price",
            "is_active",
            "valid_until",
        )

    def validate(self, attrs):
        discount_percent = attrs.get("discount_percent")
        discounted_price = attrs.get("discounted_price")
        product = attrs.get("product")
        valid_until = attrs.get("valid_until")

        if product:
            original_price = product.price
        elif self.instance:
            original_price = self.instance.product.price
        else:
            original_price = None

        if discount_percent is not None and (discount_percent < 0 or discount_percent > 100):
            raise serializers.ValidationError(
                {"discount_percent": "Discount percentage must be between 0 and 100."}
            )

        if discounted_price is not None and discounted_price < 0:
            raise serializers.ValidationError(
                {"discounted_price": "Discounted price must be greater than or equal to 0."}
            )

        if discounted_price is not None and original_price is not None and discounted_price >= original_price:
            raise serializers.ValidationError(
                {"discounted_price": "Discounted price must be less than the original product price."}
            )

        import datetime
        if valid_until and valid_until < datetime.date.today():
            raise serializers.ValidationError(
                {"valid_until": "Expiration date cannot be in the past."}
            )

        return attrs