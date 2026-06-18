# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from assistify.apps.products.models import Product, ProductBenefit, Offer
from assistify.apps.users.models import User
from assistify.apps.orders.models import Order, OrderItem


PRODUCTS = [
    {
        "key": "bp_monitor",
        "name": "جهاز قياس ضغط الدم الرقمي",
        "description": (
            "جهاز رقمي لقياس ضغط الدم الانقباضي والانبساطي ومعدل النبض من أعلى الذراع، "
            "بشاشة كبيرة وذاكرة لحفظ القراءات، ومناسب للمتابعة المنزلية اليومية."
        ),
        "price": Decimal("2699.00"),
        "emoji": "🩺",
        "features": [
            "قياس ضغط الدم والنبض",
            "شاشة رقمية كبيرة وواضحة",
            "ذاكرة لحفظ 60 قراءة",
            "تنبيه عند اكتشاف عدم انتظام النبض",
            "تشغيل بضغطة زر واحدة",
        ],
        "suitable_for": ["مرضى ضغط الدم", "كبار السن", "المتابعة المنزلية"],
        "use_cases": [
            "متابعة ضغط الدم يوميًا",
            "تسجيل القراءات قبل زيارة الطبيب",
            "متابعة النبض في المنزل",
        ],
        "benefits": [
            "سهل الاستخدام في المنزل",
            "يساعد على متابعة تغيرات الضغط بانتظام",
            "شاشة واضحة تناسب كبار السن",
        ],
        "related": ["pulse_oximeter", "heart_rate_monitor"],
    },
    {
        "key": "pulse_oximeter",
        "name": "جهاز قياس الأكسجين والنبض",
        "description": (
            "جهاز يوضع على الإصبع لقياس نسبة تشبع الأكسجين في الدم ومعدل النبض خلال ثوانٍ، "
            "مزود بشاشة ملونة وإيقاف تلقائي."
        ),
        "price": Decimal("1499.00"),
        "emoji": "💓",
        "features": [
            "قياس نسبة الأكسجين في الدم",
            "قياس معدل النبض",
            "شاشة ملونة واضحة",
            "إيقاف تلقائي",
            "حجم صغير وسهل الحمل",
        ],
        "suitable_for": [
            "مرضى الجهاز التنفسي",
            "كبار السن",
            "الرياضيون",
            "المتابعة المنزلية",
        ],
        "use_cases": [
            "متابعة تشبع الأكسجين",
            "متابعة النبض",
            "الاستخدام أثناء التعافي من أمراض الجهاز التنفسي",
        ],
        "benefits": [
            "قراءة سريعة",
            "لا يحتاج إلى عينة دم",
            "مناسب للمنزل والسفر",
        ],
        "related": ["bp_monitor", "nebulizer"],
    },
    {
        "key": "digital_thermometer",
        "name": "ترمومتر رقمي",
        "description": (
            "ترمومتر رقمي صغير لقياس درجة حرارة الجسم، مزود بتنبيه صوتي عند اكتمال القياس "
            "وشاشة سهلة القراءة."
        ),
        "price": Decimal("899.00"),
        "emoji": "🌡️",
        "features": [
            "قراءة رقمية واضحة",
            "تنبيه صوتي",
            "ذاكرة لآخر قراءة",
            "إيقاف تلقائي",
            "غطاء للحماية",
        ],
        "suitable_for": ["الأطفال", "الكبار", "الاستخدام المنزلي"],
        "use_cases": ["قياس درجة الحرارة", "متابعة حالات الحمى"],
        "benefits": [
            "سهل الاستخدام",
            "حجم صغير وسهل التخزين",
            "مناسب لجميع أفراد الأسرة",
        ],
        "related": ["infrared_thermometer", "first_aid_kit"],
    },
    {
        "key": "smart_scale",
        "name": "ميزان رقمي ذكي",
        "description": (
            "ميزان رقمي بشاشة واضحة لقياس الوزن، مع إمكانية متابعة مؤشر كتلة الجسم "
            "من خلال التطبيق المتوافق."
        ),
        "price": Decimal("2399.00"),
        "emoji": "⚖️",
        "features": [
            "قياس دقيق للوزن",
            "شاشة LED واضحة",
            "تشغيل تلقائي عند الوقوف",
            "سطح زجاجي قوي",
            "إمكانية متابعة مؤشر كتلة الجسم",
        ],
        "suitable_for": ["متابعة الوزن", "البرامج الغذائية", "الاستخدام العائلي"],
        "use_cases": ["متابعة الوزن أسبوعيًا", "متابعة التقدم في الحمية"],
        "benefits": [
            "تصميم أنيق",
            "قراءة واضحة",
            "مناسب للاستخدام اليومي",
        ],
        "related": ["bp_monitor", "heating_pad"],
    },
    {
        "key": "heart_rate_monitor",
        "name": "جهاز متابعة معدل ضربات القلب",
        "description": (
            "جهاز قابل للارتداء لمتابعة معدل ضربات القلب والنشاط اليومي، "
            "مع إمكانية مزامنة البيانات مع الهاتف."
        ),
        "price": Decimal("3899.00"),
        "emoji": "❤️",
        "features": [
            "متابعة معدل ضربات القلب",
            "متابعة النشاط اليومي",
            "مقاوم لرذاذ الماء",
            "بطارية تدوم عدة أيام",
            "مزامنة مع الهاتف",
        ],
        "suitable_for": ["الرياضيون", "متابعة النشاط", "الاستخدام اليومي"],
        "use_cases": ["متابعة النبض أثناء التمرين", "متابعة النشاط اليومي"],
        "benefits": [
            "متابعة مستمرة",
            "تصميم خفيف",
            "عرض البيانات على الهاتف",
        ],
        "related": ["pulse_oximeter", "smart_scale"],
    },
    {
        "key": "glucose_monitor",
        "name": "جهاز قياس سكر الدم",
        "description": (
            "جهاز سريع لقياس مستوى الجلوكوز في الدم، مزود بذاكرة لحفظ النتائج، "
            "ويأتي مع قلم وخز وشرائط بداية."
        ),
        "price": Decimal("1799.00"),
        "emoji": "🩸",
        "features": [
            "نتيجة سريعة خلال ثوانٍ",
            "يحتاج إلى عينة دم صغيرة",
            "ذاكرة لحفظ القراءات",
            "شاشة سهلة القراءة",
            "يشمل قلم وخز وشرائط بداية",
        ],
        "suitable_for": ["مرضى السكري", "كبار السن", "المتابعة المنزلية"],
        "use_cases": [
            "قياس السكر قبل الطعام وبعده",
            "متابعة سكر الصيام",
            "تسجيل القراءات اليومية",
        ],
        "benefits": [
            "حجم صغير وسهل الحمل",
            "يساعد على متابعة مستوى السكر يوميًا",
            "تشغيل بسيط وسريع",
        ],
        "related": ["glucose_strips", "bp_monitor"],
    },
    {
        "key": "nebulizer",
        "name": "جهاز استنشاق نيبولايزر",
        "description": (
            "جهاز ضاغط لتحويل الدواء السائل إلى رذاذ دقيق يصل إلى الجهاز التنفسي، "
            "ويأتي مع ماسك للكبار وماسك للأطفال وملحقات الاستنشاق."
        ),
        "price": Decimal("3200.00"),
        "emoji": "🌬️",
        "features": [
            "ماسك للكبار وماسك للأطفال",
            "تشغيل هادئ نسبيًا",
            "حجرة دواء قابلة للتنظيف",
            "خرطوم وقطعة فم",
            "تصميم مناسب للمنزل",
        ],
        "suitable_for": [
            "مرضى الربو",
            "مرضى حساسية الصدر",
            "الأطفال",
            "مرضى الجهاز التنفسي",
        ],
        "use_cases": [
            "جلسات الاستنشاق الموصوفة طبيًا",
            "إيصال أدوية التنفس في صورة رذاذ",
        ],
        "benefits": [
            "مناسب للكبار والأطفال",
            "يساعد على توصيل الدواء للجهاز التنفسي",
            "ملحقاته سهلة الفك والتنظيف",
        ],
        "related": ["pulse_oximeter", "infrared_thermometer"],
    },
    {
        "key": "infrared_thermometer",
        "name": "ترمومتر بالأشعة تحت الحمراء",
        "description": (
            "ترمومتر لقياس درجة حرارة الجسم من الجبهة دون لمس، "
            "يعطي النتيجة خلال ثانية ومزود بتنبيه عند ارتفاع الحرارة."
        ),
        "price": Decimal("1250.00"),
        "emoji": "🌡️",
        "features": [
            "قياس دون لمس",
            "نتيجة خلال ثانية",
            "تنبيه لارتفاع الحرارة",
            "شاشة مضيئة",
            "ذاكرة للقراءات السابقة",
        ],
        "suitable_for": ["الأطفال", "الكبار", "العيادات", "الاستخدام المنزلي"],
        "use_cases": [
            "قياس الحرارة بسرعة",
            "متابعة الحمى",
            "القياس أثناء نوم الأطفال",
        ],
        "benefits": [
            "قياس سريع",
            "مناسب لأكثر من فرد",
            "سهل التنظيف",
        ],
        "related": ["digital_thermometer", "first_aid_kit"],
    },
    {
        "key": "heating_pad",
        "name": "وسادة حرارية كهربائية",
        "description": (
            "وسادة حرارية كهربائية بثلاث درجات حرارة ومؤقت إيقاف تلقائي، "
            "مناسبة للتدفئة الموضعية للظهر والرقبة والكتفين."
        ),
        "price": Decimal("1100.00"),
        "emoji": "🔥",
        "features": [
            "ثلاث درجات حرارة",
            "إيقاف تلقائي للأمان",
            "غطاء ناعم قابل للفك والغسل",
            "حجم مناسب للظهر والكتفين",
            "إمكانية استخدام حرارة رطبة",
        ],
        "suitable_for": ["الاستخدام المنزلي", "التدفئة الموضعية"],
        "use_cases": ["تدفئة الظهر والرقبة", "الاسترخاء بعد المجهود"],
        "benefits": [
            "تحكم سهل في الحرارة",
            "مؤقت أمان",
            "غطاء مريح",
        ],
        "related": ["posture_corrector", "smart_scale"],
    },
    {
        "key": "posture_corrector",
        "name": "حزام تصحيح وضعية الظهر",
        "description": (
            "حزام خفيف قابل للتعديل يساعد على دعم الكتفين والظهر وتحسين وضعية الجلوس، "
            "ويمكن ارتداؤه أسفل الملابس."
        ),
        "price": Decimal("650.00"),
        "emoji": "🧍",
        "features": [
            "مقاس قابل للتعديل",
            "خامة جيدة التهوية",
            "يمكن ارتداؤه أسفل الملابس",
            "أشرطة كتف مبطنة",
        ],
        "suitable_for": ["العمل المكتبي", "الطلاب", "الجلوس لفترات طويلة"],
        "use_cases": ["دعم وضعية الجلوس", "تذكير الكتفين بالوضع الصحيح"],
        "benefits": ["خفيف وسهل الارتداء", "قابل للتعديل", "مناسب للاستخدام اليومي"],
        "related": ["heating_pad", "smart_scale"],
    },
    {
        "key": "glucose_strips",
        "name": "شرائط قياس سكر الدم - 50 شريط",
        "description": (
            "عبوة تحتوي على 50 شريط اختبار للاستخدام مع جهاز قياس السكر المتوافق، "
            "مغلفة للحفاظ على دقة القياس وسهولة التخزين."
        ),
        "price": Decimal("650.00"),
        "emoji": "🧪",
        "features": [
            "عبوة 50 شريط",
            "امتصاص سريع للعينة",
            "تغليف محكم",
            "مناسبة للاستخدام اليومي",
        ],
        "suitable_for": ["مستخدمي جهاز قياس السكر", "مرضى السكري"],
        "use_cases": ["القياس اليومي للسكر", "المتابعة قبل وبعد الوجبات"],
        "benefits": ["كمية مناسبة للمتابعة المنتظمة", "سهولة الاستخدام والتخزين"],
        "related": ["glucose_monitor"],
    },
    {
        "key": "first_aid_kit",
        "name": "حقيبة إسعافات أولية منزلية",
        "description": (
            "حقيبة منظمة تحتوي على مستلزمات أساسية للتعامل الأولي مع الجروح والخدوش البسيطة، "
            "مثل الشاش والضمادات واللاصق الطبي والمقص والقفازات."
        ),
        "price": Decimal("850.00"),
        "emoji": "🧰",
        "features": [
            "شاش وضمادات معقمة",
            "لاصق طبي",
            "قفازات للاستخدام مرة واحدة",
            "مقص وملقط",
            "حقيبة منظمة وسهلة الحمل",
        ],
        "suitable_for": ["المنزل", "السيارة", "السفر", "المكاتب"],
        "use_cases": [
            "الإسعاف الأولي للجروح البسيطة",
            "الاستخدام أثناء السفر",
        ],
        "benefits": [
            "المستلزمات الأساسية في مكان واحد",
            "سهلة التخزين والحمل",
            "مناسبة للطوارئ البسيطة",
        ],
        "related": ["digital_thermometer", "infrared_thermometer"],
    },
]

OFFERS = {
    "pulse_oximeter": {
        "discount_percent": 20,
        "discounted_price": Decimal("1199.00"),
    },
    "smart_scale": {
        "discount_percent": 15,
        "discounted_price": Decimal("2039.00"),
    },
    "heart_rate_monitor": {
        "discount_percent": 25,
        "discounted_price": Decimal("2924.00"),
    },
}

# ثابتة بدل random حتى تكون نتيجة الـDemo متوقعة في كل تشغيل.
DEMO_INTERACTIONS = {
    "user_1": ["bp_monitor", "pulse_oximeter", "glucose_monitor"],
    "user_2": ["glucose_monitor", "glucose_strips", "bp_monitor"],
    "user_3": ["nebulizer", "pulse_oximeter", "infrared_thermometer"],
    "user_4": ["smart_scale", "heart_rate_monitor", "heating_pad"],
    "user_5": ["digital_thermometer", "first_aid_kit", "posture_corrector"],
}


class Command(BaseCommand):
    help = (
        "Seed Assistify with Arabic medical products, offers, "
        "and deterministic demo interactions."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding medical products...")

        products_by_key = {}

        for data in PRODUCTS:
            product, created = Product.objects.update_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "currency": "EGP",
                    "emoji": data["emoji"],
                    "is_active": True,
                    "features": data["features"],
                    "suitable_for": data["suitable_for"],
                    "use_cases": data["use_cases"],
                },
            )
            products_by_key[data["key"]] = product

            product.benefits.all().delete()
            ProductBenefit.objects.bulk_create(
                [
                    ProductBenefit(product=product, text=text, order=index)
                    for index, text in enumerate(data["benefits"])
                ]
            )

            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {status}: {product.name} — {product.price} EGP"
                )
            )

        self.stdout.write("Linking related products...")
        for data in PRODUCTS:
            product = products_by_key[data["key"]]
            related = [
                products_by_key[key]
                for key in data.get("related", [])
                if key in products_by_key
            ]
            product.related_products.set(related)

        self.stdout.write("Seeding offers...")
        active_offer_products = set()

        for product_key, offer_data in OFFERS.items():
            product = products_by_key[product_key]
            active_offer_products.add(product.id)

            offer, created = Offer.objects.update_or_create(
                product=product,
                defaults={
                    "discount_percent": offer_data["discount_percent"],
                    "discounted_price": offer_data["discounted_price"],
                    "is_active": True,
                },
            )
            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {status}: {product.name} — "
                    f"{offer.discount_percent}% off"
                )
            )

        Offer.objects.exclude(product_id__in=active_offer_products).update(
            is_active=False
        )

        self.stdout.write("Seeding deterministic interactions for LightFM...")

        for index, (username, product_keys) in enumerate(
            DEMO_INTERACTIONS.items(), start=1
        ):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )

            if created:
                user.set_password("password123")
                user.save(update_fields=["password"])
                self.stdout.write(f"  Created user: {username}")

            marker_address = f"DEMO_INTERACTION_{username}"

            order = Order.objects.filter(
                user=user,
                customer_email=user.email,
                delivery_address=marker_address,
            ).first()

            if order is None:
                order = Order.objects.create(
                    user=user,
                    customer_email=user.email,
                    subtotal=Decimal("0.00"),
                    shipping_fee=Decimal("50.00"),
                    total=Decimal("50.00"),
                    delivery_address=marker_address,
                    phone=f"0100000000{index}",
                )

            order.items.all().delete()

            subtotal = Decimal("0.00")

            for product_key in product_keys:
                product = products_by_key[product_key]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_emoji=product.emoji,
                    unit_price=product.price,
                    quantity=1,
                )

                subtotal += Decimal(str(product.price))

            order.subtotal = subtotal
            order.shipping_fee = Decimal("50.00")
            order.total = subtotal + order.shipping_fee
            order.save(update_fields=["subtotal", "shipping_fee", "total"])

            self.stdout.write(
                f"  {username}: {len(product_keys)} product interactions"
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Done: {Product.objects.filter(is_active=True).count()} "
                "active medical products are ready for the demo."
            )
        )
