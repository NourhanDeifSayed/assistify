import logging
import re
import gc
from typing import Dict, Any, Optional
from django.apps import apps
from django.db import transaction

logger = logging.getLogger(__name__)


class ModelOrchestrator:
    _instance = None
    _models = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    def _get_model(self, model_type: str):
        if self._models.get(model_type):
            return self._models[model_type]
        try:
            if model_type == "intent":
                from assistify.ml_models.intent_classification.model import IntentClassificationModel
                self._models["intent"] = IntentClassificationModel()
            elif model_type == "sentiment":
                from assistify.ml_models.sentiment_analysis.model import SentimentAnalysisModel
                self._models["sentiment"] = SentimentAnalysisModel()
            elif model_type == "recommendation":
                from assistify.ml_models.product_recommendation.model import RecommendationModel
                self._models["recommendation"] = RecommendationModel()
            return self._models.get(model_type)
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {e}", exc_info=True)
            return None

    def detect_language(self, text: str) -> str:
        return "ar" if re.search(r"[\u0600-\u06FF]", text) else "en"

    def _is_valid_email(self, text: str) -> bool:
        return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", text.strip()))

    def _is_valid_phone(self, text: str) -> bool:
        cleaned = re.sub(r"[^\d+]", "", text.strip())
        return bool(re.match(r"^(\+20|0)?1[0125]\d{8}$", cleaned))

    def _normalize_payment_method(self, text: str):
        tl = text.lower().strip()
        if tl in ["cod", "cash", "cash on delivery", "كاش", "الدفع عند الاستلام", "استلام"]:
            return "cod"
        if tl in ["card", "visa", "mastercard", "بطاقة", "فيزا", "ماستر"]:
            return "card"
        return None

    def extract_entities(self, text: str, lang: str) -> Dict[str, Any]:
        entities = {
            "user_name": None,
            "product_name": None,
            "order_number": None
        }
        tl = text.lower().strip()

        m = re.search(r"ord-\d{4}-\d{1,5}", tl)
        if m:
            entities["order_number"] = m.group(0).upper()

        blacklist = {
            "اسمي", "ايه", "إيه", "أنا", "انا", "مين", "هو", "هي", "ده", "دي",
            "بكام", "سعره", "معلومات", "تفاصيل", "عاوزة", "عايزة", "عايز", "فين",
            "مواصفات", "جهاز", "طلب", "what", "who", "is", "am", "the",
            "want", "need", "name", "this", "order", "product",
        }

        if lang == "ar":
            m = re.search(r"(?:اسمي|أنا|انا|اسمي هو|معاك)\s+([آ-ي]{2,}(?:\s+[آ-ي]{2,})?)", tl)
            if m:
                n = m.group(1).strip()
                if n not in blacklist and "؟" not in tl and len(n.split()) <= 3:
                    entities["user_name"] = n
        else:
            m = re.search(r"(?:my name is|i'm|i am|this is)\s+([a-zA-Z]{2,}(?:\s+[a-zA-Z]{2,})?)", tl)
            if m:
                n = m.group(1).strip()
                if n.lower() not in blacklist and "?" not in tl and len(n.split()) <= 3:
                    entities["user_name"] = n

        medical_keywords = [
            "blood pressure monitor", "heart rate monitor", "pulse oximeter",
            "infrared thermometer", "digital thermometer", "nebulizer machine",
            "electric heating pad", "glucose monitor",
            "nebulizer", "oximeter", "thermometer", "heating pad",
            "blood pressure", "heart rate", "glucose", "pulse", "monitor", "mask",
            "جهاز", "سكر", "ضغط", "قياس", "ترمومتر", "كمامة", "بخاخة",
        ]
        for kw in medical_keywords:
            if kw in tl:
                entities["product_name"] = kw
                break

        return entities

    def _resolve_product(self, entities: Dict, context: Dict):
        Product = apps.get_model("products", "Product")
        pname = entities.get("product_name")
        if pname:
            qs = Product.objects.filter(is_active=True, name__icontains=pname)
            if qs.exists():
                return qs.first()

        last_id = context.get("last_product_id")
        if last_id:
            try:
                return Product.objects.get(id=last_id)
            except Product.DoesNotExist:
                pass
        return None

    _PRODUCT_TERMS = {
        "monitor", "thermometer", "oximeter", "nebulizer", "glucose", "pulse",
        "blood pressure", "heart rate", "heating pad", "mask", "infrared", "digital",
        "جهاز", "ترمومتر", "كمامة", "بخاخ", "سكر", "ضغط", "قياس",
    }

    _ONE_WORD_REJECTS = {
        "yes", "no", "ok", "okay", "sure", "nope", "اه", "لا", "أيوه", "تمام",
        "buy", "order", "cancel", "stop", "الغاء",
    }

    def _is_valid_address(self, text: str) -> bool:
        tl = text.lower().strip()
        words = tl.split()
        has_number = bool(re.search(r"\d", tl))
        if len(words) < 2 and not has_number:
            return False
        if any(pt in tl for pt in self._PRODUCT_TERMS):
            return False
        if len(words) == 1 and tl in self._ONE_WORD_REJECTS:
            return False
        return True

    def process_message(self, message: str, conversation_id: Optional[int] = None,
                        user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        text = message or kwargs.get("text", "")
        if not text:
            return {"success": False, "error": "Empty message"}

        lang = self.detect_language(text)
        entities = self.extract_entities(text, lang)
        tl = text.lower().strip()

        Conversation = apps.get_model("chat", "Conversation")
        conv = None

        ctx = {
            "language": lang,
            "user_name": None,
            "product_name": entities["product_name"],
            "order_number": entities["order_number"],
            "last_product_id": None,
            "last_intent": None,
            "purchase_state": None,
            "address": None,
            "customer_email": None,
            "customer_phone": None,
            "payment_method": None,
        }

        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id)
                ctx.update({
                    "user_name": conv.user_name,
                    "last_product_id": conv.last_product_id,
                    "last_intent": conv.last_intent,
                    "purchase_state": getattr(conv, "purchase_state", None),
                    "address": getattr(conv, "address", None),
                    "customer_email": getattr(conv, "customer_email", None),
                    "customer_phone": getattr(conv, "customer_phone", None),
                    "payment_method": getattr(conv, "payment_method", None),
                })
                if entities["user_name"]:
                    conv.user_name = entities["user_name"]
                    ctx["user_name"] = entities["user_name"]
                    conv.save()
            except Exception:
                pass

        intent = self._analyze_intent_safe(text, ctx.get("last_intent")).get("intent", "inquiry")

        cancel_words = ["الغاء", "مش عايز", "cancel", "stop"]

        if ctx["purchase_state"] == "awaiting_address":
            if any(w in tl for w in cancel_words):
                intent = "cancel_purchase"
                if conv:
                    conv.purchase_state = None
                    conv.address = None
                    conv.customer_email = None
                    conv.customer_phone = None
                    conv.payment_method = None
                    conv.save()
                ctx["purchase_state"] = None
            elif self._is_valid_address(text):
                intent = "provide_address"
                ctx["address"] = text.strip()
                ctx["purchase_state"] = "awaiting_email"
                if conv:
                    conv.address = text.strip()
                    conv.purchase_state = "awaiting_email"
                    conv.save()

        elif ctx["purchase_state"] == "awaiting_email":
            if any(w in tl for w in cancel_words):
                intent = "cancel_purchase"
                if conv:
                    conv.purchase_state = None
                    conv.address = None
                    conv.customer_email = None
                    conv.customer_phone = None
                    conv.payment_method = None
                    conv.save()
                ctx["purchase_state"] = None
            elif self._is_valid_email(text):
                intent = "provide_email"
                ctx["customer_email"] = text.strip()
                ctx["purchase_state"] = "awaiting_phone"
                if conv:
                    conv.customer_email = text.strip()
                    conv.purchase_state = "awaiting_phone"
                    conv.save()

        elif ctx["purchase_state"] == "awaiting_phone":
            if any(w in tl for w in cancel_words):
                intent = "cancel_purchase"
                if conv:
                    conv.purchase_state = None
                    conv.address = None
                    conv.customer_email = None
                    conv.customer_phone = None
                    conv.payment_method = None
                    conv.save()
                ctx["purchase_state"] = None
            elif self._is_valid_phone(text):
                intent = "provide_phone"
                ctx["customer_phone"] = text.strip()
                ctx["purchase_state"] = "awaiting_payment_method"
                if conv:
                    conv.customer_phone = text.strip()
                    conv.purchase_state = "awaiting_payment_method"
                    conv.save()

        elif ctx["purchase_state"] == "awaiting_payment_method":
            if any(w in tl for w in cancel_words):
                intent = "cancel_purchase"
                if conv:
                    conv.purchase_state = None
                    conv.address = None
                    conv.customer_email = None
                    conv.customer_phone = None
                    conv.payment_method = None
                    conv.save()
                ctx["purchase_state"] = None
            else:
                payment_method = self._normalize_payment_method(text)
                if payment_method:
                    intent = "provide_payment_method"
                    ctx["payment_method"] = payment_method
                    ctx["purchase_state"] = "ready_to_create_order"
                    if conv:
                        conv.payment_method = payment_method
                        conv.purchase_state = "ready_to_create_order"
                        conv.save()

        if ctx["purchase_state"] not in {
            "awaiting_address",
            "awaiting_email",
            "awaiting_phone",
            "awaiting_payment_method",
            "ready_to_create_order",
        }:
            if ctx["order_number"]:
                intent = "order_tracking"
            elif any(w in tl for w in ["اسمي ايه", "اسمي إيه", "أنا مين", "who am i"]):
                intent = "memory_check"
            elif intent == "recommendation_reasoning" or any(w in tl for w in ["ليه", "اشمعنى", "why"]):
                intent = "recommendation_reasoning"
            elif intent == "product_details" or any(w in tl for w in ["تفاصيل", "معلومات", "عنه", "بكام", "details", "price"]):
                intent = "product_details"

        recs, rec_method = [], "none"
        should_recommend = intent in ("recommendation_request", "product_search") or (
            entities["product_name"] and intent not in (
                "product_details", "purchase", "recommendation_reasoning",
                "order_tracking", "greeting", "memory_check", "provide_address",
                "provide_email", "provide_phone", "provide_payment_method",
                "introduce_name", "goodbye", "cancel_purchase",
            )
        )

        is_vague = (
            intent == "inquiry" and entities["product_name"]
            and not any(w in tl for w in ["رشحلي", "اقترح", "عايز", "بدور", "suggest", "recommend", "need"])
        )

        if should_recommend and not is_vague:
            recs, rec_method = self._get_recommendations_stable(user_id, intent, entities["product_name"] or text)
            if recs and conv:
                conv.last_product_id = recs[0]["product_id"]
                conv.save()
                ctx["last_product_id"] = recs[0]["product_id"]

        if is_vague:
            ctx.update({"is_vague": True, "vague_product": entities["product_name"]})

        ctx.update({
            "intent": intent,
            "sentiment": "neutral",
            "recommendations": recs,
            "message": text
        })

        response_data = self._generate_smart_response(text, ctx, conv, entities)

        if conv:
            conv.last_intent = intent
            conv.language = lang
            conv.save()

        return {
            "success": True,
            "response": response_data["response"],
            "intent": intent,
            "recommendations": recs,
            "metadata": {
                "recommendation_method": rec_method,
                "user_name": ctx.get("user_name"),
                "detected_language": lang,
                "purchase_state": ctx.get("purchase_state"),
            },
        }

    def _analyze_intent_safe(self, message: str, last_intent: str = None) -> Dict[str, Any]:
        try:
            model = self._get_model("intent")
            if model:
                return model.predict(message, last_intent=last_intent)
        except Exception as e:
            logger.error(f"Intent prediction error: {e}")
        return {"intent": "inquiry", "confidence": 0.1}

    def _get_recommendations_stable(self, user_id, intent, query):
        recs, method = [], "none"
        try:
            model = self._get_model("recommendation")
            if model:
                res = model.predict(user_id=user_id, query=query, intent=intent)
                recs = res.get("recommendations", [])
                method = res.get("method", "ml_recommendation")
        except Exception as e:
            logger.error(f"Recommendation error: {e}")

        if not recs:
            try:
                Product = apps.get_model("products", "Product")
                from django.db.models import Q
                objs = Product.objects.filter(
                    Q(is_active=True) & (Q(name__icontains=query) | Q(description__icontains=query))
                )[:3]
                recs = [
                    {
                        "product_id": p.id,
                        "name": p.name,
                        "price": float(p.price),
                        "currency": "EGP",
                        "emoji": getattr(p, "emoji", "📦") or "📦",
                        "reasoning": f"ده جهاز {p.name} ممتاز ومناسب لاحتياجك."
                    }
                    for p in objs
                ]
                method = "database_fallback"
            except Exception:
                pass

        return recs, method

    def _generate_smart_response(self, message: str, ctx: Dict, conv=None, entities: Dict = None) -> Dict[str, Any]:
        lang = ctx.get("language", "en")
        intent = ctx.get("intent", "inquiry")
        name = ctx.get("user_name")
        recs = ctx.get("recommendations", [])
        order_num = ctx.get("order_number")
        last_pid = ctx.get("last_product_id")
        is_vague = ctx.get("is_vague", False)
        entities = entities or {}

        g = f"يا {name}" if name else ""
        ge = name or ""

        if is_vague:
            vp = ctx.get("vague_product", "")
            if lang == "ar":
                return {"response": f"ممكن توضحلي أكتر {g}؟ تقصد جهاز لـ {vp} ولا تفاصيل تانية؟ 😊"}
            return {"response": f"Could you clarify {ge}? Do you need a device for {vp}? 😊"}

        if intent == "order_tracking":
            if order_num:
                try:
                    Order = apps.get_model("orders", "Order")
                    order = Order.objects.get(order_number=order_num)
                    status_map = {
                        "PLACED": "تم استلام طلبك",
                        "PROCESSING": "جاري تجهيز طلبك",
                        "SHIPPED": "طلبك في الطريق",
                        "IN_TRANSIT": "مع المندوب",
                        "DELIVERED": "تم التوصيل",
                        "CANCELLED": "ملغي",
                    }
                    s = status_map.get(order.status.upper(), "قيد التنفيذ")
                    d = order.estimated_delivery.strftime("%d/%m/%Y") if order.estimated_delivery else "قريباً"
                    if lang == "ar":
                        return {"response": f"حالة الطلب {order_num}: **{s}**. متوقع يوصل: {d} 🚚"}
                    return {"response": f"Order {order_num}: **{order.status}**. Estimated delivery: {d} 🚚"}
                except Exception:
                    if lang == "ar":
                        return {"response": f"مش لاقي طلب برقم {order_num}. تأكد من الرقم."}
                    return {"response": f"Couldn't find order {order_num}. Please verify the number."}
            if lang == "ar":
                return {"response": "ممكن تقولي رقم الطلب؟ (يبدأ بـ ORD)"}
            return {"response": "Please provide your order number (starts with ORD)."}

        if intent == "recommendation_reasoning" and last_pid:
            try:
                Product = apps.get_model("products", "Product")
                p = Product.objects.get(id=last_pid)
                f = getattr(p, "features", [])
                s = getattr(p, "suitable_for", [])
                if lang == "ar":
                    return {"response": f"رشحتلك {p.name} عشان {', '.join(f[:2]) or 'جودته العالية'} ومناسب لـ {', '.join(s[:2]) or 'الاستخدام اليومي'}."}
                return {"response": f"I recommended {p.name} for its {', '.join(f[:2]) or 'high quality'}, perfect for {', '.join(s[:2]) or 'daily use'}."}
            except Exception:
                pass

        if intent == "product_details" and last_pid:
            try:
                Product = apps.get_model("products", "Product")
                p = Product.objects.get(id=last_pid)
                fl = "\n".join(f"- {x}" for x in getattr(p, "features", []))
                sl = ", ".join(getattr(p, "suitable_for", []))
                if lang == "ar":
                    return {"response": f"**{p.name}** — {p.price} ج.م.\n**المميزات:**\n{fl or 'دقة عالية'}\n**مناسب لـ:** {sl or 'المنزل'}\nحابب تطلبه؟"}
                return {"response": f"**{p.name}** — {p.price} EGP.\n**Features:**\n{fl or 'High precision'}\n**Suitable for:** {sl or 'Home use'}\nWant to order it?"}
            except Exception:
                pass

        if intent == "memory_check":
            if name:
                if lang == "ar":
                    return {"response": f"أيوة فاكرك — إنت {name}! 😊"}
                return {"response": f"Of course — you are {name}! 😊"}
            if lang == "ar":
                return {"response": "لسه متعرفناش. ممكن تقولي اسمك؟"}
            return {"response": "We haven't met yet. What's your name?"}

        if intent == "introduce_name" and name:
            if lang == "ar":
                return {"response": f"أهلاً {g}! نورت Assistify 😊 أقدر أساعدك إزاي؟"}
            return {"response": f"Nice to meet you, {ge}! How can I help? 😊"}

        if intent == "greeting":
            if lang == "ar":
                return {"response": f"أهلاً {g} في Assistify! 😊 أقدر أرشحلك أجهزة طبية أو أتابع طلباتك. تحب نبدأ بإيه؟"}
            return {"response": f"Hello {ge}! Welcome to Assistify 😊 I can recommend devices or track orders. How can I help?"}

        if intent == "purchase":
            product = self._resolve_product(entities, ctx)
            if product:
                if conv:
                    conv.last_product_id = product.id
                    conv.purchase_state = "awaiting_address"
                    conv.save()
                ctx["last_product_id"] = product.id
                if lang == "ar":
                    return {"response": f"اختيار ممتاز! **{product.name}** بسعر {product.price} ج.م. ممكن تقولي عنوان التوصيل؟"}
                return {"response": f"Great choice! **{product.name}** at {product.price} EGP. Please provide your delivery address."}
            if lang == "ar":
                return {"response": "أنا جاهز أساعدك في الشراء. قولي اسم الجهاز اللي حابب تطلبه."}
            return {"response": "Ready to help you buy. Which device would you like?"}

        if intent == "cancel_purchase":
            if lang == "ar":
                return {"response": "تم إلغاء عملية الشراء الحالية. لو حابب نبدأ من جديد قولي اسم الجهاز 😊"}
            return {"response": "The current purchase flow has been cancelled. If you'd like to start again, tell me the product name 😊"}

        if ctx.get("purchase_state") == "awaiting_address":
            if lang == "ar":
                return {"response": "ممكن تقولي عنوان التوصيل بالتفصيل؟"}
            return {"response": "Please provide your delivery address."}

        if intent == "provide_address" or ctx.get("purchase_state") == "awaiting_email":
            if lang == "ar":
                return {"response": "تمام. ابعتلي الإيميل اللي تحب نسجل به الطلب."}
            return {"response": "Great. Please provide the email address for the order."}

        if intent == "provide_email" or ctx.get("purchase_state") == "awaiting_phone":
            if lang == "ar":
                return {"response": "كويس جدًا. ابعتلي رقم الموبايل."}
            return {"response": "Great. Now please provide your phone number."}

        if intent == "provide_phone" or ctx.get("purchase_state") == "awaiting_payment_method":
            if lang == "ar":
                return {"response": "تمام. تحب طريقة الدفع تكون كاش عند الاستلام ولا بطاقة؟"}
            return {"response": "Perfect. Would you like to pay by cash on delivery or card?"}

        if (intent == "provide_payment_method" or ctx.get("purchase_state") == "ready_to_create_order") and last_pid:
            try:
                Product = apps.get_model("products", "Product")
                Order = apps.get_model("orders", "Order")
                OrderItem = apps.get_model("orders", "OrderItem")
                p = Product.objects.get(id=last_pid)

                with transaction.atomic():
                    new_order = Order.objects.create(
                        user=conv.user if conv and conv.user else None,
                        customer_email=ctx["customer_email"] or (conv.user.email if conv and conv.user else "guest@assistify.com"),
                        phone=ctx["customer_phone"] or "",
                        payment_method=ctx["payment_method"] or Order.PaymentMethod.COD,
                        delivery_address=ctx["address"] or "",
                        subtotal=p.price,
                        shipping_fee=50,
                        total=p.price + 50,
                        status=Order.Status.PLACED,
                    )

                    OrderItem.objects.create(
                        order=new_order,
                        product=p,
                        product_name=p.name,
                        product_emoji=getattr(p, "emoji", "") or "",
                        unit_price=p.price,
                        quantity=1
                    )

                    if conv:
                        conv.purchase_state = None
                        conv.address = None
                        conv.customer_email = None
                        conv.customer_phone = None
                        conv.payment_method = None
                        conv.save()

                if lang == "ar":
                    payment_label = "الدفع عند الاستلام" if new_order.payment_method == "cod" else "بطاقة"
                    return {
                        "response": (
                            f"تم تسجيل الطلب بنجاح 🎉\n"
                            f"رقم الطلب: **{new_order.order_number}**\n"
                            f"المنتج: {p.name}\n"
                            f"العنوان: {new_order.delivery_address}\n"
                            f"الإيميل: {new_order.customer_email}\n"
                            f"الرقم: {new_order.phone}\n"
                            f"طريقة الدفع: {payment_label}\n"
                            f"الإجمالي: {new_order.total} ج.م."
                        )
                    }

                return {
                    "response": (
                        f"Order placed successfully 🎉\n"
                        f"Order number: **{new_order.order_number}**\n"
                        f"Product: {p.name}\n"
                        f"Address: {new_order.delivery_address}\n"
                        f"Email: {new_order.customer_email}\n"
                        f"Phone: {new_order.phone}\n"
                        f"Payment method: {new_order.payment_method}\n"
                        f"Total: {new_order.total} EGP"
                    )
                }
            except Exception as e:
                logger.error(f"Order error: {e}")
                if lang == "ar":
                    return {"response": "حصلت مشكلة أثناء تسجيل الطلب. ممكن تحاول تاني؟"}
                return {"response": "Something went wrong. Please try again."}

        if recs:
            p = recs[0]
            if lang == "ar":
                return {"response": f"لقيت لك: **{p['name']}**.\n{p.get('reasoning', '')}\nسعره {p['price']} ج.م. تفاصيل أكتر؟"}
            return {"response": f"Found: **{p['name']}**.\n{p.get('reasoning', '')}\nPrice: {p['price']} EGP. Want details?"}

        if lang == "ar":
            return {"response": "تمام، أنا معاك 😊 سألني عن أي جهاز أو طلب وأنا هساعدك."}
        return {"response": "I'm here 😊 Ask me about any device or order and I'll help!"}

    def __del__(self):
        gc.collect()