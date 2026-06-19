from __future__ import annotations
import gc
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from django.apps import apps
from django.contrib.auth import get_user_model
from .state_machine import PurchaseState, StateMachine, extract_name, extract_phone
from assistify.apps.orders.services import (
    create_order_from_chat,
    generate_order_tracking_token,
    get_local_catalog_products,
)
from assistify.apps.shopify_service import get_shopify_products, create_shopify_draft_order
from assistify.apps.support.models import SupportTicket
from assistify.apps.support.services import (
    create_support_ticket,
    detect_issue_type,
    extract_ticket_number,
    get_latest_order_for_user,
    get_ticket_for_user,
    is_ticket_tracking_request,
)

logger = logging.getLogger(__name__)

_RE_ORDER_NUM = re.compile(r"ord-\d{4}-[a-f0-9]{4,32}", re.I)
_RE_ARABIC = re.compile(r"[\u0600-\u06FF]")
_RE_EMAIL = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_RE_QUANTITY = re.compile(r"(?:الكمية|عدد|quantity|qty)\s*[:\-]?\s*(\d+)", re.I)
_RE_GARBAGE = re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|[^|]+\|>")
_RE_PRODUCT_NUMBER = re.compile(r"(?:رقم\s*)?(?:product\s*)?(?:number\s*)?(\d+)", re.IGNORECASE)

_PRODUCT_KEYWORDS_SORTED: List[str] = sorted(["blood pressure monitor", "heart rate monitor", "pulse oximeter", "infrared thermometer", "digital thermometer", "nebulizer machine", "electric heating pad", "glucose monitor", "blood pressure", "heart rate", "heating pad", "nebulizer", "oximeter", "thermometer", "glucose", "pulse", "monitor", "mask", "جهاز الضغط", "قياس الضغط", "ضغط", "جهاز السكر", "قياس السكر", "سكر", "ترمومتر", "حرارة", "ميزان حرارة", "اكسجين", "أكسجين", "قياس الأكسجين", "تنفس", "بخاخة", "نيبولايزر", "كمامة", "كمامات"], key=len, reverse=True)

_PURCHASE_TRIGGER_WORDS = frozenset(["عايز أطلب", "عايزة أطلب", "عايز اطلب", "عايزة اطلب", "ممكن اطلبه", "ممكن أطلبه", "اطلبه", "أطلبه", "عايزة اطلبه", "عايز اطلبه", "أطلب", "اطلب", "طلب", "شراء", "أشتري", "اشتري", "purchase", "buy", "order it", "i want to buy", "i want to order", "order", "i'll take it", "أيوه اطلبه", "خلاص اطلب", "تمام", "oki", "okay", "ايوه", "أيوه", "yes"])

_FOLLOW_UP_TRIGGER_WORDS = frozenset(["اطلبه", "أطلبه", "اطلبها", "أطلبها", "ممكن اطلبه", "ممكن أطلبه", "ممكن اطلبها", "عايزة اطلبه", "عايز اطلبه", "عايزة اطلبها", "كام سعره", "كام سعرها", "بكام", "سعره", "سعرها", "تفاصيله", "تفاصيلها", "مواصفاته", "مواصفاتها", "how much", "order it", "buy it", "i want it", "tell me more", "more details", "price"])

_TRACKING_TRIGGER_WORDS = frozenset(["فين طلبي", "تتبع الطلب", "حالة الطلب", "track order", "order status", "الطلب فين", "وصل الطلب", "أين طلبي"])

_OUT_OF_SCOPE_KEYWORDS: List[str] = ["الساعة كام", "الوقت", "الطقس", "الجو", "الدولار", "العملة", "اليورو", "الجنيه الاسترليني", "البيتكوين", "أخبار", "الأخبار", "سياسة", "الانتخابات", "مباراة", "كرة القدم", "كرة", "الدوري", "الحكومة", "الرئيس", "البرلمان", "توقعات الطقس", "what time", "current time", "weather", "temperature outside", "dollar rate", "exchange rate", "currency", "bitcoin", "crypto", "news", "politics", "election", "football", "soccer", "match", "stock market", "stock price"]

_MEDICAL_SYMPTOM_KEYWORDS_AR: List[str] = ["دوخة", "دوخه", "دوار", "صداع", "الصداع", "تعب", "وجع راس", "وجع الراس", "حاسه بتعب", "حاسس بتعب", "حاسة بتعب", "ضيق تنفس", "قلبي بيدق", "عندي ألم", "عندي وجع", "سخونة", "حرارة عالية"]

_MEDICAL_SYMPTOM_KEYWORDS_EN: List[str] = ["feel dizzy", "feeling dizzy", "i feel dizzy", "i feel sick", "i feel unwell", "headache", "i have a headache", "chest pain", "shortness of breath", "i feel tired", "i'm tired", "i am tired", "not feeling well", "feeling weak"]

_LEGAL_KEYWORDS_AR: List[str] = ["أرفع قضية", "ارفع قضية", "قضية", "محكمة", "محامي", "حقوقي", "دعوى", "مقاضاة"]

_LEGAL_KEYWORDS_EN: List[str] = ["sue", "lawsuit", "file a case", "legal action", "attorney", "court", "can i sue"]

_FINANCIAL_KEYWORDS_AR: List[str] = ["أستثمر فلوسي", "استثمر فلوسي", "استثمار", "الأسهم", "البورصة", "فلوسي فين", "عملات", "بيتكوين"]

_FINANCIAL_KEYWORDS_EN: List[str] = ["invest my money", "should i invest", "stock market", "bitcoin", "crypto", "financial advice"]

_HARMFUL_KEYWORDS_AR: List[str] = ["إزاي أعمل حاجة تضر", "أضر حد", "اضر حد", "أضر ناس", "إزاي أهاجم", "قرصنة", "اختراق"]

_HARMFUL_KEYWORDS_EN: List[str] = ["how to hack", "hacking", "how to harm", "how to hurt", "how to attack", "malware", "exploit"]

_BROWSE_PRODUCTS_KEYWORDS_AR: List[str] = ["قولي كل المنتجات", "كل المنتجات", "عرض كل المنتجات", "المنتجات المتوفرة", "ايه المنتجات المتوفرة", "المنتجات الموجودة", "شوف المنتجات", "وريني المنتجات", "عندكم ايه", "المنتجات كلها"]

_BROWSE_PRODUCTS_KEYWORDS_EN: List[str] = ["show all products", "all products", "list products", "available products", "what products do you have", "show me products", "products list", "tell me all products"]

_NO_RECOMMEND_INTENTS = frozenset(["order_tracking", "greeting", "memory_check", "goodbye", "cancel_purchase", "cancellation", "complaint", "damaged_item", "missing_item", "out_of_scope", "unknown", "payment", "feedback", "delay", "purchase", "purchase_intent", "provide_phone", "provide_quantity", "provide_address", "introduce_name", "order_confirmed", "confirmation", "browse_products", "order_created"])

_FOLLOW_UP_INTENTS = frozenset(["purchase", "purchase_intent", "confirmation", "price_inquiry", "product_details", "provide_address", "provide_phone", "provide_quantity", "introduce_name"])

_PRODUCT_INTENTS = frozenset(["recommendation_request", "product_search", "product_inquiry", "product_details", "price_inquiry", "inquiry", "browse_products"])

_VAGUE_SIGNALS = frozenset(["رشحلي", "اقترح", "عايز", "عايزة", "بدور", "suggest", "recommend", "need", "find"])

_RE_GIBBERISH = re.compile(r"^[^a-zA-Z\u0600-\u06FF\d]{3,}$|^(.)\1{4,}$|^[a-z]{6,}$", re.UNICODE)

_MIN_ALPHA_RATIO = 0.4
_INTENT_CONFIDENCE_THRESHOLD = 0.40
_PURCHASE_MIN_CONFIDENCE = 0.70
_SHOPIFY_ENABLED = (
    os.getenv("SHOPIFY_ENABLED", "false")
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)


@dataclass
class ModelContext:
    """
    Backward-compatible context object used by the legacy ML tests
    and any older code that imports ModelContext.
    """

    user_id: Optional[int] = None
    message: str = ""
    intent: Optional[Dict[str, Any]] = None
    sentiment: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "message": self.message,
            "intent": self.intent,
            "sentiment": self.sentiment,
            "recommendations": self.recommendations or [],
            "response": self.response,
        }


def _enrich_with_shopify_variant(
    rec: Dict,
    shopify_products: List[Dict],
) -> Dict:
    if rec.get("variant_id"):
        return rec
    rec_name = (
        rec.get("name")
        or rec.get("title", "")
    ).lower().strip()
    if not rec_name:
        return rec
    best_match = None
    best_score = 0
    for shopify_product in shopify_products:
        shopify_name = (
            shopify_product.get("name")
            or shopify_product.get("title", "")
        ).lower().strip()
        if not shopify_name:
            continue
        if rec_name == shopify_name:
            best_match = shopify_product
            break
        if rec_name in shopify_name or shopify_name in rec_name:
            score = len(
                set(rec_name.split())
                & set(shopify_name.split())
            )
            if score > best_score:
                best_score = score
                best_match = shopify_product
    if not best_match:
        return rec
    enriched = {**rec}
    enriched["variant_id"] = best_match.get("variant_id")
    enriched["shopify_product_id"] = best_match.get("id")
    enriched["shopify_source"] = True
    if not enriched.get("price") and best_match.get("price"):
        enriched["price"] = best_match["price"]
    return enriched

def _safe_shopify_products() -> List[Dict]:
    if not _SHOPIFY_ENABLED:
        return []
    try:
        products = get_shopify_products()
        if isinstance(products, list):
            return products
        logger.warning(
            "Shopify returned an unexpected products payload: %r",
            type(products),
        )
    except Exception as exc:
        logger.warning(
            "Shopify catalogue is unavailable; using local products: %s",
            exc,
        )
    return []

def fetch_all_products() -> List[Dict]:
    try:
        local_products = get_local_catalog_products(limit=50)
    except Exception as exc:
        logger.error(
            "Failed to load local catalogue: %s",
            exc,
            exc_info=True,
        )
        local_products = []
    shopify_products = _safe_shopify_products()
    if local_products:
        if not shopify_products:
            return local_products
        return [
            _enrich_with_shopify_variant(
                product,
                shopify_products,
            )
            for product in local_products
        ]
    normalized_shopify_products: List[Dict] = []
    for product in shopify_products:
        normalized_product = {**product}
        normalized_product.setdefault("source", "shopify")
        normalized_product.setdefault(
            "shopify_product_id",
            product.get("id"),
        )
        normalized_shopify_products.append(normalized_product)
    return normalized_shopify_products

def format_shopify_products_response(
    products: List[Dict],
    language: str,
) -> str:
    if not products:
        if language == "ar":
            return "عذراً، لا توجد منتجات متاحة حالياً."
        return "Sorry, no products are currently available."
    if language == "ar":
        lines = ["🛍️ المنتجات المتاحة:\n"]
        for index, product in enumerate(products[:10], 1):
            name = product.get("name") or product.get(
                "title",
                "منتج",
            )
            price = product.get("price", "")
            description = product.get("description", "")
            price_text = ""
            if price:
                try:
                    price_text = f"{int(float(price))} جنيه"
                except Exception:
                    price_text = f"{price} جنيه"
            lines.append(f"{index}️⃣ {name}")
            if price_text:
                lines.append(f"💰 السعر: {price_text}")
            if description:
                shortened = description[:100]
                suffix = "..." if len(description) > 100 else ""
                lines.append(f"📝 {shortened}{suffix}")
            lines.append("")
        lines.append("💬 اختاري رقم المنتج لمعرفة التفاصيل أو الطلب.")
        return "\n".join(lines)
    lines = ["🛍️ Available products:\n"]
    for index, product in enumerate(products[:10], 1):
        name = product.get("name") or product.get(
            "title",
            "Product",
        )
        price = product.get("price", "")
        description = product.get("description", "")
        price_text = ""
        if price:
            try:
                price_text = f"{int(float(price))} EGP"
            except Exception:
                price_text = f"{price} EGP"
        lines.append(f"{index}. {name}")
        if price_text:
            lines.append(f"💰 Price: {price_text}")
        if description:
            shortened = description[:100]
            suffix = "..." if len(description) > 100 else ""
            lines.append(f"📝 {shortened}{suffix}")
        lines.append("")
    lines.append("💬 Choose a product number for details or ordering.")
    return "\n".join(lines)

def is_purchase_trigger(message: str, intent: str) -> bool:
    purchase_triggers = frozenset([
        "أيوه", "ايوه", "تمام", "اطلبه", "أطلبه", "اطلب", "اشتري", "عايزة أشتريه",
        "yes", "order", "buy", "ok", "okay", "oki", "confirmed", "go ahead", "نعم", "أجل",
        "موافق", "حاضر", "تم", "proceed"
    ])
    tl = message.lower().strip()
    if intent in ("confirmation", "purchase", "purchase_intent"):
        return True
    for kw in purchase_triggers:
        if kw in tl:
            return True
    return False

def is_order_tracking_query(message: str, intent: str) -> bool:
    tl = message.lower().strip()
    if intent == "order_tracking":
        return True
    for kw in _TRACKING_TRIGGER_WORDS:
        if kw in tl:
            return True
    return False

def is_browse_products_query(message: str, intent: str) -> bool:
    tl = message.lower().strip()
    if intent == "browse_products":
        return True
    for kw in _BROWSE_PRODUCTS_KEYWORDS_AR:
        if kw in tl:
            return True
    for kw in _BROWSE_PRODUCTS_KEYWORDS_EN:
        if kw in tl:
            return True
    return False

@dataclass
class SignalBundle:
    message: str = ""
    language: str = "en"
    intent: str = "inquiry"
    intent_conf: float = 0.0
    intent_all_probs: Dict[str, float] = field(default_factory=dict)
    is_medical_symptom: bool = False
    is_legal_advice: bool = False
    is_financial_advice: bool = False
    is_harmful: bool = False
    sentiment: str = "neutral"
    sentiment_conf: float = 0.0
    entities: Dict[str, Any] = field(default_factory=lambda: {"user_name": None, "product_name": None, "order_number": None, "created_order_number": None})
    recommendations: List[Dict] = field(default_factory=list)
    recommendation_method: str = "none"
    response: str = ""
    response_conf: float = 0.0
    user_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    quantity: Optional[int] = None
    order_id: Optional[int] = None
    authenticated_user_id: Optional[int] = None
    local_order_number: Optional[str] = None
    tracking_token: Optional[str] = None
    last_product_id: Optional[int] = None
    last_product_variant_id: Optional[str] = None
    last_intent: Optional[str] = None
    purchase_state: PurchaseState = PurchaseState.IDLE
    address: Optional[str] = None
    last_product_snapshot: Optional[Dict] = None
    routing_trace: List[str] = field(default_factory=list)
    all_products: List[Dict] = field(default_factory=list)
    shopify_draft_order_id: Optional[str] = None
    shopify_draft_order_name: Optional[str] = None
    shopify_invoice_url: Optional[str] = None
    shopify_sync_status: str = "not_attempted"
    shopify_sync_error: Optional[str] = None
    checkout_intent: str = ""
    checkout_entities: Dict[str, Any] = field(default_factory=dict)
    next_action: str = ""
    checkout_ai_parse_failed: bool = False
    checkout_mode: str = "ai"
    checkout_fallback_used: bool = False
    ticket_id: Optional[int] = None
    ticket_number: Optional[str] = None
    ticket_status: Optional[str] = None
    human_handoff: bool = False
    complaint_state: str = "idle"
    _conv: Any = None

    def confidence_score(self) -> float:
        return self.intent_conf * 0.5 + self.sentiment_conf * 0.3 + (0.2 if self.recommendations else 0.0)

    def trace(self, stage: str) -> None:
        self.routing_trace.append(stage)

    @property
    def is_any_safety_flag(self) -> bool:
        return self.is_medical_symptom or self.is_legal_advice or self.is_financial_advice or self.is_harmful

class _ModelRegistry:
    _store: Dict[str, Any] = {}

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._store:
            return cls._store[key]
        try:
            if key == "intent":
                from assistify.ml_models.intent_classification.model import IntentClassificationModel
                cls._store[key] = IntentClassificationModel()
            elif key == "sentiment":
                from assistify.ml_models.sentiment_analysis.model import SentimentAnalysisModel
                cls._store[key] = SentimentAnalysisModel()
            elif key == "recommendation":
                from assistify.ml_models.product_recommendation.model import RecommendationModel
                cls._store[key] = RecommendationModel()
            elif key == "generation":
                from assistify.ml_models.response_generation.model import ResponseGenerationModel
                cls._store[key] = ResponseGenerationModel()
            else:
                cls._store[key] = None
        except Exception as exc:
            logger.error("Failed to load model '%s': %s", key, exc, exc_info=True)
            cls._store[key] = None
        return cls._store.get(key)

class _LanguageDetector:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("language_detector")
        tl = bundle.message.lower().strip()
        bundle.language = "ar" if _RE_ARABIC.search(bundle.message) else "en"
        order_match = _RE_ORDER_NUM.search(tl)
        if order_match:
            bundle.entities["order_number"] = order_match.group(0).upper()
        phone = extract_phone(bundle.message)
        if phone:
            bundle.phone = phone
        email_match = _RE_EMAIL.search(bundle.message)
        if email_match:
            bundle.email = email_match.group(0)
        quantity_match = _RE_QUANTITY.search(bundle.message)
        if quantity_match:
            bundle.quantity = int(quantity_match.group(1))
        elif tl.strip().isdigit() and 1 <= int(tl.strip()) <= 99:
            bundle.quantity = int(tl.strip())
        name = extract_name(bundle.message, bundle.language)
        if name:
            bundle.entities["user_name"] = name
        for keyword in _PRODUCT_KEYWORDS_SORTED:
            if keyword in tl:
                bundle.entities["product_name"] = keyword
                break

class _SafetyLayer:
    @staticmethod
    def _check_keywords(text: str, ar_list: List[str], en_list: List[str]) -> bool:
        for kw in ar_list:
            if kw in text:
                return True
        for kw in en_list:
            if kw in text:
                return True
        return False

    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("safety_layer")
        tl = bundle.message.lower().strip()
        if _SafetyLayer._check_keywords(tl, _MEDICAL_SYMPTOM_KEYWORDS_AR, _MEDICAL_SYMPTOM_KEYWORDS_EN):
            bundle.is_medical_symptom = True
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True
        if _SafetyLayer._check_keywords(tl, _LEGAL_KEYWORDS_AR, _LEGAL_KEYWORDS_EN):
            bundle.is_legal_advice = True
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True
        if _SafetyLayer._check_keywords(tl, _FINANCIAL_KEYWORDS_AR, _FINANCIAL_KEYWORDS_EN):
            bundle.is_financial_advice = True
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True
        if _SafetyLayer._check_keywords(tl, _HARMFUL_KEYWORDS_AR, _HARMFUL_KEYWORDS_EN):
            bundle.is_harmful = True
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True
        if any(kw in tl for kw in _OUT_OF_SCOPE_KEYWORDS):
            bundle.intent = "out_of_scope"
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True
        if len(tl) >= 5:
            total = max(len(tl), 1)
            alpha_n = sum(1 for c in tl if c.isalpha() or c.isdigit())
            alpha_ratio = alpha_n / total
            if bool(_RE_GIBBERISH.match(tl)) or alpha_ratio < _MIN_ALPHA_RATIO:
                bundle.intent = "unknown"
                bundle.intent_conf = 1.0
                bundle.recommendations = []
                bundle.recommendation_method = "none"
                return True
        return False

class _TicketTrackingStage:
    @staticmethod
    def run(bundle: SignalBundle, conv) -> bool:
        if conv is None:
            return False

        if not is_ticket_tracking_request(bundle.message):
            return False

        bundle.trace("ticket_tracking_stage")

        user = _ComplaintStage._get_user(bundle, conv)

        if user is None:
            bundle.intent = "complaint_auth_required"
            bundle.intent_conf = 1.0
            bundle.response_conf = 0.98
            bundle.response = (
                "Please sign in to track your support tickets."
                if bundle.language == "en"
                else "من فضلك سجل الدخول لمتابعة الشكاوى."
            )
            return True

        ticket_number = extract_ticket_number(bundle.message)

        ticket = get_ticket_for_user(
            user,
            ticket_number=ticket_number,
        )

        if ticket is None:
            bundle.intent = "complaint_not_found"
            bundle.intent_conf = 1.0
            bundle.response_conf = 0.95
            bundle.response = (
                "I could not find a support ticket linked to your account."
                if bundle.language == "en"
                else "لم أجد شكوى مرتبطة بحسابك."
            )
            bundle.ticket_id = None
            bundle.ticket_number = None
            bundle.ticket_status = None
            bundle.human_handoff = False
            return True

        admin_response = (
            ticket.admin_response.strip()
            if ticket.admin_response
            else ""
        )

        assigned_to = (
            ticket.assigned_to.email
            if ticket.assigned_to
            else None
        )

        if bundle.language == "en":
            response_lines = [
                f"🎫 Ticket number: {ticket.ticket_number}",
                f"📌 Issue: {ticket.get_issue_type_display()}",
                f"📍 Status: {ticket.get_status_display()}",
                f"⚠️ Priority: {ticket.get_priority_display()}",
            ]

            if assigned_to:
                response_lines.append(
                    f"👤 Assigned to: {assigned_to}"
                )

            response_lines.append(
                f"💬 Admin response: "
                f"{admin_response or 'No response yet'}"
            )
        else:
            response_lines = [
                f"🎫 رقم الشكوى: {ticket.ticket_number}",
                f"📌 نوع المشكلة: {ticket.get_issue_type_display()}",
                f"📍 الحالة: {ticket.get_status_display()}",
                f"⚠️ الأولوية: {ticket.get_priority_display()}",
            ]

            if assigned_to:
                response_lines.append(
                    f"👤 المسؤول: {assigned_to}"
                )

            response_lines.append(
                f"💬 رد الإدارة: "
                f"{admin_response or 'لا يوجد رد حتى الآن'}"
            )

        active_statuses = {
            SupportTicket.Status.OPEN,
            SupportTicket.Status.IN_PROGRESS,
            SupportTicket.Status.WAITING_FOR_CUSTOMER,
        }

        bundle.intent = "complaint_tracking"
        bundle.intent_conf = 1.0
        bundle.response = "\n".join(response_lines)
        bundle.response_conf = 0.98
        bundle.recommendations = []
        bundle.recommendation_method = "none"

        bundle.ticket_id = ticket.id
        bundle.ticket_number = ticket.ticket_number
        bundle.ticket_status = ticket.status
        bundle.human_handoff = ticket.status in active_statuses
        bundle.complaint_state = getattr(
            conv,
            "complaint_state",
            "idle",
        )

        return True

class _ComplaintStage:
    YES_WORDS = {
        "yes",
        "yeah",
        "correct",
        "right",
        "نعم",
        "ايوه",
        "أيوه",
        "اه",
        "آه",
        "صح",
        "تمام",
    }

    NO_WORDS = {
        "no",
        "wrong",
        "لا",
        "لأ",
        "مش هو",
        "مش ده",
    }

    @staticmethod
    def _get_user(bundle: SignalBundle, conv):
        user_id = (
            bundle.authenticated_user_id
            or getattr(conv, "user_id", None)
        )
        if not user_id:
            return None
        User = get_user_model()
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def _get_order(bundle: SignalBundle, conv, user):
        Order = apps.get_model("orders", "Order")
        order_id = (
            getattr(conv, "complaint_order_id", None)
            or getattr(conv, "order_id", None)
        )
        if order_id:
            queryset = Order.objects.filter(id=order_id)
            if not user.is_staff:
                queryset = queryset.filter(user=user)
            order = queryset.first()
            if order:
                return order
        return get_latest_order_for_user(user)

    @staticmethod
    def _set_common_metadata(bundle: SignalBundle, conv) -> None:
        bundle.human_handoff = True
        bundle.complaint_state = getattr(
            conv,
            "complaint_state",
            "idle",
        )
        bundle.recommendations = []
        bundle.recommendation_method = "none"
        bundle.response_conf = 0.98

    @staticmethod
    def run(bundle: SignalBundle, conv) -> bool:
        if conv is None:
            return False

        bundle.trace("complaint_stage")

        state = getattr(conv, "complaint_state", "idle")
        detected_issue = detect_issue_type(bundle.message)
        normalized_message = bundle.message.strip().lower()

        if state == "idle" and not detected_issue:
            return False

        user = _ComplaintStage._get_user(bundle, conv)

        if user is None:
            bundle.intent = "complaint_auth_required"
            bundle.response = (
                "Please sign in before creating a support ticket."
                if bundle.language == "en"
                else "من فضلك سجل الدخول أولًا قبل إنشاء شكوى."
            )
            bundle.human_handoff = False
            bundle.response_conf = 0.98
            return True

        if state == "idle":
            order = _ComplaintStage._get_order(
                bundle,
                conv,
                user,
            )

            if order is None:
                bundle.intent = "complaint_order_not_found"
                bundle.response = (
                    "I could not find an order linked to your account. "
                    "Please provide your order number."
                    if bundle.language == "en"
                    else
                    "لم أجد طلبًا مرتبطًا بحسابك. "
                    "من فضلك أرسل رقم الطلب."
                )
                bundle.human_handoff = True
                bundle.response_conf = 0.95
                return True

            conv.complaint_state = (
                conv.ComplaintState.AWAITING_ORDER_CONFIRMATION
            )
            conv.complaint_issue_type = detected_issue
            conv.complaint_order_id = order.id
            conv.save(
                update_fields=[
                    "complaint_state",
                    "complaint_issue_type",
                    "complaint_order_id",
                ]
            )

            bundle.intent = "complaint_order_confirmation"
            bundle.response = (
                f"I'm sorry about that. Do you mean order "
                f"{order.order_number}?"
                if bundle.language == "en"
                else
                f"آسف بخصوص المشكلة دي. هل تقصد الطلب "
                f"{order.order_number}؟"
            )

            _ComplaintStage._set_common_metadata(bundle, conv)
            return True

        if state == "awaiting_order_confirmation":
            if normalized_message in _ComplaintStage.YES_WORDS:
                conv.complaint_state = (
                    conv.ComplaintState.AWAITING_DESCRIPTION
                )
                conv.save(update_fields=["complaint_state"])

                bundle.intent = "complaint_description_required"
                bundle.response = (
                    "Please describe the problem in more detail."
                    if bundle.language == "en"
                    else
                    "من فضلك وضّح المشكلة بالتفصيل."
                )

                _ComplaintStage._set_common_metadata(bundle, conv)
                return True

            if normalized_message in _ComplaintStage.NO_WORDS:
                conv.complaint_state = conv.ComplaintState.IDLE
                conv.complaint_issue_type = ""
                conv.complaint_order_id = None
                conv.save(
                    update_fields=[
                        "complaint_state",
                        "complaint_issue_type",
                        "complaint_order_id",
                    ]
                )

                bundle.intent = "complaint_order_required"
                bundle.response = (
                    "Please send the correct order number with the problem."
                    if bundle.language == "en"
                    else
                    "من فضلك أرسل رقم الطلب الصحيح مع وصف المشكلة."
                )

                _ComplaintStage._set_common_metadata(bundle, conv)
                return True

            bundle.intent = "complaint_order_confirmation"
            bundle.response = (
                "Please answer yes or no."
                if bundle.language == "en"
                else "من فضلك أجب بنعم أو لا."
            )

            _ComplaintStage._set_common_metadata(bundle, conv)
            return True

        if state == "awaiting_description":
            description = bundle.message.strip()

            if len(description) < 10:
                bundle.intent = "complaint_description_required"
                bundle.response = (
                    "Please provide more details about the problem."
                    if bundle.language == "en"
                    else
                    "من فضلك اكتب تفاصيل أكثر عن المشكلة."
                )

                _ComplaintStage._set_common_metadata(bundle, conv)
                return True

            Order = apps.get_model("orders", "Order")

            order = Order.objects.filter(
                id=conv.complaint_order_id,
                user=user,
            ).first()

            if order is None:
                bundle.intent = "complaint_order_not_found"
                bundle.response = (
                    "The linked order could not be found."
                    if bundle.language == "en"
                    else "لم يتم العثور على الطلب المرتبط بالشكوى."
                )
                bundle.human_handoff = True
                bundle.response_conf = 0.95
                return True

            issue_type = (
                conv.complaint_issue_type
                or SupportTicket.IssueType.OTHER
            )

            ticket, created = create_support_ticket(
                user=user,
                conversation=conv,
                order=order,
                issue_type=issue_type,
                description=description,
            )

            conv.complaint_ticket = ticket
            conv.complaint_state = conv.ComplaintState.IDLE
            conv.complaint_issue_type = ""
            conv.complaint_order_id = None
            conv.save(
                update_fields=[
                    "complaint_ticket",
                    "complaint_state",
                    "complaint_issue_type",
                    "complaint_order_id",
                ]
            )

            bundle.ticket_id = ticket.id
            bundle.ticket_number = ticket.ticket_number
            bundle.ticket_status = ticket.status
            bundle.intent = (
                "complaint_created"
                if created
                else "complaint_already_exists"
            )

            if created:
                bundle.response = (
                    f"Your support ticket was created successfully. "
                    f"Ticket number: {ticket.ticket_number}."
                    if bundle.language == "en"
                    else
                    f"تم إنشاء الشكوى بنجاح. "
                    f"رقم التذكرة: {ticket.ticket_number}."
                )
            else:
                bundle.response = (
                    f"You already have an active ticket: "
                    f"{ticket.ticket_number}."
                    if bundle.language == "en"
                    else
                    f"لديك بالفعل شكوى مفتوحة برقم "
                    f"{ticket.ticket_number}."
                )

            _ComplaintStage._set_common_metadata(bundle, conv)
            return True

        return False

class _OrderTrackingStage:
    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("order_tracking_stage")
        in_active_flow = bundle.purchase_state != PurchaseState.IDLE
        if in_active_flow:
            tl = bundle.message.lower().strip()
            has_explicit_tracking = any(
                keyword in tl
                for keyword in _TRACKING_TRIGGER_WORDS
            )
            if not has_explicit_tracking:
                return False
        elif not is_order_tracking_query(
            bundle.message,
            bundle.intent,
        ):
            return False
        order_obj = None
        if bundle.order_id:
            try:
                Order = apps.get_model("orders", "Order")
                order_obj = (
                    Order.objects
                    .prefetch_related("tracking_updates")
                    .filter(pk=bundle.order_id)
                    .first()
                )
            except Exception as exc:
                logger.warning(
                    "Could not load local order %s: %s",
                    bundle.order_id,
                    exc,
                )
        requested_order_number = bundle.entities.get(
            "order_number"
        )
        if (
            order_obj
            and requested_order_number
            and order_obj.order_number.lower()
            != requested_order_number.lower()
        ):
            order_obj = None
        if order_obj:
            bundle.local_order_number = order_obj.order_number
            bundle.entities["order_number"] = order_obj.order_number
            bundle.intent = "order_tracking"
            bundle.intent_conf = 1.0
            bundle.purchase_state = PurchaseState.IDLE
            bundle.response_conf = 0.98
            status_label = order_obj.get_status_display()
            tracking_number = (
                order_obj.tracking_number
                or (
                    "غير متوفر حالياً"
                    if bundle.language == "ar"
                    else "Not available yet"
                )
            )
            latest_update = (
                order_obj.tracking_updates
                .order_by("-date", "-id")
                .first()
            )
            latest_location = (
                latest_update.location
                if latest_update
                else (
                    "غير متوفر"
                    if bundle.language == "ar"
                    else "Not available"
                )
            )
            invoice_url = bundle.shopify_invoice_url
            if not invoice_url and bundle.last_product_snapshot:
                invoice_url = bundle.last_product_snapshot.get(
                    "shopify_invoice_url"
                )
            if bundle.language == "ar":
                bundle.response = (
                    f"📦 رقم الطلب: {order_obj.order_number}\n"
                    f"📍 الحالة: {status_label}\n"
                    f"🚚 رقم التتبع: {tracking_number}\n"
                    f"🏢 آخر موقع: {latest_location}"
                )
                if invoice_url:
                    bundle.response += (
                        f"\n💳 رابط الدفع: {invoice_url}"
                    )
            else:
                bundle.response = (
                    f"📦 Order number: {order_obj.order_number}\n"
                    f"📍 Status: {status_label}\n"
                    f"🚚 Tracking number: {tracking_number}\n"
                    f"🏢 Latest location: {latest_location}"
                )
                if invoice_url:
                    bundle.response += (
                        f"\n💳 Payment link: {invoice_url}"
                    )
            return True
        draft_order_id = bundle.shopify_draft_order_id
        draft_order_name = bundle.shopify_draft_order_name
        invoice_url = bundle.shopify_invoice_url
        if not draft_order_id and bundle.last_product_snapshot:
            draft_order_id = bundle.last_product_snapshot.get(
                "shopify_draft_order_id"
            )
            draft_order_name = bundle.last_product_snapshot.get(
                "shopify_draft_order_name"
            )
            invoice_url = bundle.last_product_snapshot.get(
                "shopify_invoice_url"
            )
        if draft_order_id and invoice_url:
            if bundle.language == "ar":
                bundle.response = (
                    f"طلبك {draft_order_name} متجهز "
                    f"ولسه في انتظار الدفع.\n"
                    f"رابط الدفع: {invoice_url}"
                )
            else:
                bundle.response = (
                    f"Your order {draft_order_name} is ready "
                    f"and awaiting payment.\n"
                    f"Payment link: {invoice_url}"
                )
            bundle.response_conf = 0.98
            bundle.intent = "order_tracking"
            bundle.intent_conf = 1.0
            bundle.purchase_state = PurchaseState.IDLE
            return True
        if bundle.language == "ar":
            bundle.response = (
                "معنديش طلب محفوظ ليكي حالياً. "
                "اختاري منتج وابدأي طلب جديد."
            )
        else:
            bundle.response = (
                "I don't have any saved order for you. "
                "Please select a product and start a new order."
            )
        bundle.response_conf = 0.98
        bundle.intent = "order_tracking"
        bundle.intent_conf = 1.0
        return True

class _CheckoutAIStage:
    @staticmethod
    def _build_checkout_prompt(bundle: SignalBundle, product_name: str) -> str:
        if bundle.language == "ar":
            collection_status = (
                f"البيانات الحالية:\n"
                f"- الاسم: {bundle.user_name if bundle.user_name else 'غير متوفر'}\n"
                f"- الهاتف: {bundle.phone if bundle.phone else 'غير متوفر'}\n"
                f"- العنوان: {bundle.address if bundle.address else 'غير متوفر'}\n"
                f"- الكمية: {bundle.quantity if bundle.quantity else 'غير متوفر'}\n"
            )
            return (
                f"أنت مساعد ذكي لمتجر Shopify لبيع المنتجات الطبية.\n"
                f"المنتج المختار: {product_name}\n"
                f"{collection_status}\n"
                f"رسالة المستخدم: {bundle.message}\n"
                f"أخرج JSON فقط (بدون أي كلام آخر) بالشكل التالي:\n"
                '{\n"checkout_intent": "start_checkout | provide_name | provide_phone | provide_address | provide_quantity | confirm_order | cancel_order | track_order | unknown",\n'
                f'"entities": {{ \n"name": "اسم المستخدم إذا ذكره في هذه الرسالة، وإلا null",\n"phone": "رقم الهاتف إذا ذكره في هذه الرسالة، وإلا null",\n"address": "العنوان إذا ذكره في هذه الرسالة، وإلا null",\n"quantity": "الكمية إذا ذكرها في هذه الرسالة (رقم فقط)، وإلا null"\n}} ,\n'
                f'"next_action": "ask_name | ask_phone | ask_address | ask_quantity | create_shopify_draft_order | track_order | cancel | clarify"\n}} \n'
                f"قواعد مهمة:\n"
                f"- لا تخرج أي شيء بجانب الـ JSON.\n"
                f"- لا تخترع بيانات غير موجودة في الرسالة.\n"
                f"- إذا كانت كل البيانات مكتملة: next_action = \"create_shopify_draft_order\"\n"
                f"- إذا قال المستخدم أيوه/تمام/موافق/yes/ok: checkout_intent = \"confirm_order\" و next_action حسب البيانات الناقصة."
            )
        else:
            collection_status = (
                f"Current data:\n"
                f"- Name: {bundle.user_name if bundle.user_name else 'not available'}\n"
                f"- Phone: {bundle.phone if bundle.phone else 'not available'}\n"
                f"- Address: {bundle.address if bundle.address else 'not available'}\n"
                f"- Quantity: {bundle.quantity if bundle.quantity else 'not available'}\n"
            )
            return (
                f"You are a smart assistant for a Shopify medical products store.\n"
                f"Selected product: {product_name}\n"
                f"{collection_status}\n"
                f"User message: {bundle.message}\n"
                f"Output ONLY JSON (no extra text) in the following format:\n"
                f'{{ \n"checkout_intent": "start_checkout | provide_name | provide_phone | provide_address | provide_quantity | confirm_order | cancel_order | track_order | unknown",\n'
                f'"entities": {{ \n"name": "user name if mentioned in this message, else null",\n"phone": "phone number if mentioned in this message, else null",\n"address": "address if mentioned in this message, else null",\n"quantity": "quantity if mentioned in this message (number only), else null"\n}} ,\n'
                f'"next_action": "ask_name | ask_phone | ask_address | ask_quantity | create_shopify_draft_order | track_order | cancel | clarify"\n}} \n'
                f"Important rules:\n"
                f"- Output ONLY JSON, no other text.\n"
                f"- Do not invent data not present in the message.\n"
                f"- If all data is collected: next_action = \"create_shopify_draft_order\"\n"
                f"- If user says yes/okay/sure/proceed: checkout_intent = \"confirm_order\" and next_action based on missing data."
            )

    @staticmethod
    def _parse_ai_response(raw_response: str) -> Optional[Dict]:
        try:
            raw_response = raw_response.strip()
            json_match = re.search(r'\{.*?"checkout_intent".*?\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(raw_response)
        except json.JSONDecodeError:
            try:
                json_block = re.search(r'\{[^{}]+\}', raw_response, re.DOTALL)
                if json_block:
                    return json.loads(json_block.group(0))
            except Exception:
                pass
            return None

    @staticmethod
    def _apply_entities_to_bundle(bundle: SignalBundle, ai_output: Dict) -> None:
        entities = ai_output.get("entities", {})
        if not isinstance(entities, dict):
            return
        extracted_name = entities.get("name")
        if extracted_name and str(extracted_name).lower() not in ("null", "none", "") and not bundle.user_name:
            bundle.user_name = str(extracted_name).strip()
            bundle.entities["user_name"] = bundle.user_name
        extracted_phone = entities.get("phone")
        if extracted_phone and str(extracted_phone).lower() not in ("null", "none", "") and not bundle.phone:
            bundle.phone = str(extracted_phone).strip()
        extracted_address = entities.get("address")
        if extracted_address and str(extracted_address).lower() not in ("null", "none", "") and not bundle.address:
            bundle.address = str(extracted_address).strip()
        extracted_qty = entities.get("quantity")
        if extracted_qty and str(extracted_qty).lower() not in ("null", "none", "") and not bundle.quantity:
            try:
                qty = int(str(extracted_qty).strip())
                if 1 <= qty <= 99:
                    bundle.quantity = qty
            except (ValueError, TypeError):
                pass

    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("checkout_ai_stage")
        
        active_checkout_states = {
            PurchaseState.AWAITING_NAME,
            PurchaseState.AWAITING_PHONE,
            PurchaseState.AWAITING_ADDRESS,
            PurchaseState.AWAITING_QUANTITY,
            PurchaseState.READY_TO_ORDER,
        }
        
        in_active_flow = bundle.purchase_state in active_checkout_states
        
        is_new_purchase = (
            bundle.purchase_state == PurchaseState.IDLE
            and bundle.last_product_snapshot is not None
            and is_purchase_trigger(bundle.message, bundle.intent)
        )
        
        if not in_active_flow and not is_new_purchase:
            return False
            
        if in_active_flow:
            bundle.checkout_mode = "state_machine"
            bundle.checkout_fallback_used = True
            bundle.checkout_ai_parse_failed = False
            checkout_intent, next_action = _CheckoutAIStage._fallback_intent(bundle)
            bundle.checkout_intent = checkout_intent
            bundle.next_action = next_action
            
            if bundle.checkout_intent == "cancel_order" or bundle.next_action == "cancel":
                bundle.intent = "cancel_purchase"
                bundle.intent_conf = 1.0
                bundle.purchase_state = PurchaseState.IDLE
                if bundle.language == "ar":
                    bundle.response = "تم إلغاء الطلب 😊 أقدر أساعدك في أي حاجة تانية؟"
                else:
                    bundle.response = "Order cancelled. How else can I help you?"
                bundle.response_conf = 0.95
                return True
                
            if bundle.checkout_intent == "track_order" or bundle.next_action == "track_order":
                return _OrderTrackingStage.run(bundle)
                
            return False
            
        product_name = ""
        if bundle.last_product_snapshot:
            product_name = (
                bundle.last_product_snapshot.get("name")
                or bundle.last_product_snapshot.get("title", "المنتج")
            )
            
        ai_output = None
        gen_model = _ModelRegistry.get("generation")
        
        if gen_model and product_name:
            try:
                prompt = _CheckoutAIStage._build_checkout_prompt(bundle, product_name)
                result = gen_model.generate(prompt, {"language": bundle.language, "temp": 0.1})
                raw_output = result.get("response", "")
                ai_output = _CheckoutAIStage._parse_ai_response(raw_output)
                
                if ai_output:
                    bundle.checkout_mode = "ai"
                    bundle.checkout_fallback_used = False
                    bundle.checkout_intent = ai_output.get("checkout_intent", "unknown")
                    bundle.checkout_entities = ai_output.get("entities", {})
                    bundle.next_action = ai_output.get("next_action", "clarify")
                    _CheckoutAIStage._apply_entities_to_bundle(bundle, ai_output)
                else:
                    bundle.checkout_ai_parse_failed = True
                    bundle.checkout_mode = "ai"
                    bundle.checkout_fallback_used = True
                    logger.warning("CheckoutAI: failed to parse AI response for message: %s", bundle.message[:100])
            except Exception as exc:
                bundle.checkout_ai_parse_failed = True
                bundle.checkout_mode = "ai"
                bundle.checkout_fallback_used = True
                logger.error("CheckoutAI: generation error: %s", exc)
        else:
            bundle.checkout_mode = "ai"
            bundle.checkout_fallback_used = True
            logger.debug(
                "CheckoutAI skipped: generation model or product is unavailable."
            )
            
        if bundle.checkout_ai_parse_failed or not ai_output:
            checkout_intent, next_action = _CheckoutAIStage._fallback_intent(bundle)
            bundle.checkout_intent = checkout_intent
            bundle.next_action = next_action
            
        if bundle.checkout_intent == "cancel_order" or bundle.next_action == "cancel":
            bundle.intent = "cancel_purchase"
            bundle.intent_conf = 1.0
            bundle.purchase_state = PurchaseState.IDLE
            if bundle.language == "ar":
                bundle.response = "تم إلغاء الطلب 😊 أقدر أساعدك في أي حاجة تانية؟"
            else:
                bundle.response = "Order cancelled. How else can I help you?"
            bundle.response_conf = 0.95
            return True
            
        if bundle.checkout_intent == "track_order" or bundle.next_action == "track_order":
            return _OrderTrackingStage.run(bundle)
            
        if is_new_purchase:
            return StateMachine.start_purchase_flow(bundle, bundle._conv if hasattr(bundle, '_conv') else None)
            
        return False

    @staticmethod
    def _fallback_intent(bundle: SignalBundle) -> Tuple[str, str]:
        tl = bundle.message.lower().strip()
        cancel_words = frozenset(["الغاء", "إلغاء", "الغي", "ألغي", "cancel", "مش عايز", "مش عايزة"])
        if any(w in tl for w in cancel_words):
            return "cancel_order", "cancel"
        tracking_words = frozenset(["فين طلبي", "track", "order status", "الطلب فين", "أين طلبي"])
        if any(w in tl for w in tracking_words):
            return "track_order", "track_order"
        purchase_words = frozenset(["تمام", "أيوه", "ايوه", "yes", "ok", "okay", "oki", "اطلبه", "أطلبه", "اطلب", "شراء"])
        if any(w in tl for w in purchase_words):
            if not bundle.user_name:
                return "confirm_order", "ask_name"
            if not bundle.phone:
                return "confirm_order", "ask_phone"
            if not bundle.address:
                return "confirm_order", "ask_address"
            if not bundle.quantity:
                return "confirm_order", "ask_quantity"
            return "confirm_order", "create_shopify_draft_order"
        return "unknown", "clarify"

class _ProductSelectionStage:
    @staticmethod
    def _extract_product_number(message: str) -> Optional[int]:
        text = (message or "").strip()
        patterns = (
            r"(?:product|item)\s*(?:number|no\.?|#)?\s*[:\-]?\s*(\d{1,3})\b",
            r"(?:number|no\.?|#)\s*[:\-]?\s*(\d{1,3})\b",
            r"(?:المنتج|منتج)\s*(?:رقم)?\s*[:\-]?\s*(\d{1,3})\b",
            r"(?:رقم)\s*[:\-]?\s*(\d{1,3})\b",
        )
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        stripped = text.strip()
        if stripped.isdigit() and 1 <= int(stripped) <= 999:
            return int(stripped)
        return None

    @staticmethod
    def _has_purchase_intent(message: str, intent: str) -> bool:
        tl = message.lower().strip()
        if intent in ("confirmation", "purchase", "purchase_intent"):
            return True
        purchase_words = frozenset([
            "اطلب", "أطلب", "اطلبه", "أطلبه", "اطلبي", "أطلبي",
            "عايز", "عايزة", "شراء", "اشتري", "أشتري",
            "order", "buy", "purchase", "i want",
        ])
        return any(w in tl for w in purchase_words)

    @staticmethod
    def run(bundle: SignalBundle, conv=None) -> bool:
        bundle.trace("product_selection_stage")
        product_number = _ProductSelectionStage._extract_product_number(bundle.message)
        if product_number is None:
            return False
        if bundle.purchase_state != PurchaseState.IDLE:
            return False
        shopify_products = fetch_all_products()
        if not shopify_products:
            if bundle.language == "ar":
                bundle.response = "عذراً، لا توجد منتجات متاحة حالياً."
            else:
                bundle.response = "Sorry, no products are currently available."
            bundle.response_conf = 0.98
            bundle.intent = "product_selection_error"
            bundle.intent_conf = 1.0
            return True
        if product_number < 1 or product_number > len(shopify_products):
            if bundle.language == "ar":
                bundle.response = f"عذراً، رقم المنتج {product_number} غير موجود. في {len(shopify_products)} منتج متاح، يرجى اختيار رقم من 1 إلى {len(shopify_products)}"
            else:
                bundle.response = f"Sorry, product number {product_number} not found. There are {len(shopify_products)} products available, please choose a number from 1 to {len(shopify_products)}"
            bundle.response_conf = 0.98
            bundle.intent = "product_selection_error"
            bundle.intent_conf = 1.0
            return True
        selected_index = product_number - 1
        selected_product = shopify_products[selected_index].copy()
        bundle.last_product_id = (
            selected_product.get("product_id")
            or selected_product.get("id")
        )
        bundle.last_product_variant_id = selected_product.get("variant_id")
        bundle.last_product_snapshot = selected_product
        bundle.recommendations = [selected_product]
        bundle.intent = "product_selected"
        bundle.intent_conf = 1.0
        bundle.recommendation_method = "catalog_selected"
        bundle.response_conf = 0.98
        product_name = selected_product.get("name") or selected_product.get("title", "المنتج")
        price = selected_product.get("price", "")
        def fmt_price(p, lang):
            try:
                return f"{int(float(p))} {'جنيه' if lang == 'ar' else 'EGP'}"
            except Exception:
                return f"{p} {'جنيه' if lang == 'ar' else 'EGP'}"
        if _ProductSelectionStage._has_purchase_intent(bundle.message, bundle.intent):
            bundle.intent = "purchase_intent"
            bundle.intent_conf = 1.0
            return StateMachine.start_purchase_flow(bundle, conv)
        price_text = fmt_price(price, bundle.language) if price else ""
        if bundle.language == "ar":
            bundle.response = f"تمام 👌 اخترتي {product_name}\n💰 السعر: {price_text}\n\nتحبي تطلبيه؟"
        else:
            bundle.response = f"Great 👌 You selected {product_name}\n💰 Price: {price_text}\n\nDo you want to order it?"
        return True

class _BrowseProductsStage:
    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("browse_products_stage")
        if is_browse_products_query(bundle.message, bundle.intent):
            shopify_products = fetch_all_products()
            bundle.all_products = shopify_products
            bundle.recommendations = shopify_products
            bundle.response = format_shopify_products_response(shopify_products, bundle.language)
            bundle.response_conf = 0.98
            bundle.intent = "browse_products"
            bundle.intent_conf = 1.0
            bundle.recommendation_method = "local_catalog"
            return True
        return False

class _ProductSearchStage:
    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("product_search_stage")
        if bundle.intent == "product_search":
            shopify_products = fetch_all_products()
            bundle.recommendations = shopify_products
            bundle.response = format_shopify_products_response(shopify_products, bundle.language)
            bundle.response_conf = 0.98
            bundle.recommendation_method = "local_catalog_search"
            return True
        return False

class _IntentStage:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("intent_stage")
        model = _ModelRegistry.get("intent")
        if not model:
            bundle.intent = "inquiry"
            bundle.intent_conf = 0.1
            return
        try:
            result = model.predict(bundle.message, last_intent=bundle.last_intent)
            bundle.intent = result.get("intent", "inquiry")
            bundle.intent_conf = float(result.get("confidence", 0.5))
            if "all_probs" in result:
                bundle.intent_all_probs = result["all_probs"]
        except Exception as exc:
            logger.error("Intent stage error: %s", exc, exc_info=True)
            bundle.intent = "inquiry"
            bundle.intent_conf = 0.1

class _SentimentStage:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("sentiment_stage")
        model = _ModelRegistry.get("sentiment")
        if not model:
            bundle.sentiment = "neutral"
            bundle.sentiment_conf = 0.5
            return
        try:
            result = model.predict(bundle.message)
            bundle.sentiment = result.get("sentiment", "neutral")
            bundle.sentiment_conf = float(result.get("confidence", 0.5))
        except Exception as exc:
            logger.error("Sentiment stage error: %s", exc, exc_info=True)
            bundle.sentiment = "neutral"
            bundle.sentiment_conf = 0.5

class _RecommendationStage:
    @staticmethod
    def run(bundle: SignalBundle, user_id: Optional[int]) -> None:
        bundle.trace("recommendation_stage")
        model = _ModelRegistry.get("recommendation")
        if not model:
            return
        try:
            product_entity = bundle.entities.get("product_name")
            query = bundle.message if product_entity in ["جهاز", "قياس", "monitor", "device"] else (product_entity or bundle.message)
            recs, method = model.recommend(user_id=user_id, query=query, intent=bundle.intent, sentiment=bundle.sentiment)
            if recs:
                try:
                    shopify_products = _safe_shopify_products()
                    if shopify_products:
                        enriched = []
                        for rec in recs:
                            enriched_rec = _enrich_with_shopify_variant(rec, shopify_products)
                            enriched.append(enriched_rec)
                            if enriched_rec.get("variant_id"):
                                logger.debug(
                                    "Enriched recommendation '%s' with variant_id: %s",
                                    enriched_rec.get("name", ""),
                                    enriched_rec.get("variant_id"),
                                )
                            else:
                                logger.warning(
                                    "Could not find Shopify match for recommendation: '%s'",
                                    rec.get("name", ""),
                                )
                        recs = enriched
                except Exception as enrich_exc:
                    logger.warning("Failed to enrich recommendations with Shopify data: %s", enrich_exc)
            bundle.recommendations = recs
            bundle.recommendation_method = method
        except Exception as exc:
            logger.error("Recommendation stage error: %s", exc, exc_info=True)

class _ModelRouterStage:
    def should_recommend(self, bundle: SignalBundle) -> bool:
        if bundle.intent in _NO_RECOMMEND_INTENTS:
            return False
        if bundle.intent in _PRODUCT_INTENTS:
            return True
        if bundle.intent_conf < _INTENT_CONFIDENCE_THRESHOLD and bundle.entities.get("product_name"):
            return True
        return True

    def is_vague(self, bundle: SignalBundle) -> bool:
        if bundle.intent != "recommendation_request":
            return False
        if bundle.entities.get("product_name"):
            return False
        tl = bundle.message.lower().strip()
        return any(word in tl for word in _VAGUE_SIGNALS)

def _missing_order_fields(bundle: SignalBundle) -> List[str]:
    missing = []
    if not bundle.user_name:
        missing.append("user_name")
    if not bundle.phone:
        missing.append("phone")
    if not bundle.address:
        missing.append("address")
    if not bundle.quantity:
        missing.append("quantity")
    return missing

def _save_order_data_to_conversation(bundle: SignalBundle, conv) -> None:
    if not conv:
        return
    try:
        update_fields = []
        if bundle.user_name and bundle.user_name != getattr(conv, "user_name", None):
            conv.user_name = bundle.user_name
            update_fields.append("user_name")
        if bundle.phone and bundle.phone != getattr(conv, "phone", None):
            conv.phone = bundle.phone
            update_fields.append("phone")
        if bundle.email and bundle.email != getattr(conv, "email", None):
            conv.email = bundle.email
            update_fields.append("email")
        if bundle.quantity and bundle.quantity != getattr(conv, "quantity", None):
            conv.quantity = bundle.quantity
            update_fields.append("quantity")
        if bundle.address and bundle.address != getattr(conv, "address", None):
            conv.address = bundle.address
            update_fields.append("address")
        if bundle.order_id and bundle.order_id != getattr(conv, "order_id", None):
            conv.order_id = bundle.order_id
            update_fields.append("order_id")
        if update_fields:
            conv.save(update_fields=update_fields)
    except Exception as exc:
        logger.error("Failed to save order data: %s", exc, exc_info=True)

def _get_authenticated_order_user(
    bundle: SignalBundle,
    conv,
):
    conversation_user = getattr(conv, "user", None)
    if (
        conversation_user is not None
        and getattr(
            conversation_user,
            "is_authenticated",
            False,
        )
    ):
        return conversation_user
    if bundle.authenticated_user_id:
        try:
            User = get_user_model()
            return User.objects.filter(
                pk=bundle.authenticated_user_id
            ).first()
        except Exception as exc:
            logger.warning(
                "Could not load authenticated user %s: %s",
                bundle.authenticated_user_id,
                exc,
            )
    return None

def _create_shopify_order_and_confirm(
    bundle: SignalBundle,
    conv,
) -> bool:
    missing_fields = _missing_order_fields(bundle)
    if missing_fields:
        logger.warning(
            "Cannot create order; missing fields: %s",
            ", ".join(missing_fields),
        )
        return False
    if not bundle.last_product_snapshot:
        bundle.last_product_snapshot = {}
    snapshot = bundle.last_product_snapshot
    local_order = None
    existing_local_order_id = snapshot.get("local_order_id")
    if existing_local_order_id:
        try:
            Order = apps.get_model("orders", "Order")
            local_order = Order.objects.filter(
                pk=existing_local_order_id,
            ).first()
        except Exception as exc:
            logger.warning(
                "Could not reload local order %s: %s",
                existing_local_order_id,
                exc,
            )
    order_user = _get_authenticated_order_user(
        bundle,
        conv,
    )
    order_email = (
        bundle.email
        or getattr(order_user, "email", "")
        or "customer@example.com"
    )
    try:
        if local_order is None:
            product_id = (
                snapshot.get("product_id")
                or bundle.last_product_id
                or snapshot.get("local_product_id")
            )
            local_order = create_order_from_chat(
                product_id=product_id,
                phone=bundle.phone,
                address=bundle.address,
                quantity=bundle.quantity,
                email=order_email,
                user=order_user,
                product_snapshot=snapshot,
            )
    except Exception as exc:
        logger.error(
            "Local order creation failed: %s",
            exc,
            exc_info=True,
        )
        if bundle.language == "ar":
            bundle.response = (
                "عذراً، تعذر إنشاء الطلب في النظام. "
                "راجعي بيانات الهاتف والعنوان ثم حاولي مرة أخرى."
            )
        else:
            bundle.response = (
                "Sorry, the order could not be created. "
                "Please check the phone number and address, then try again."
            )
        bundle.response_conf = 0.95
        return True
    tracking_token = generate_order_tracking_token(
        local_order,
    )
    bundle.order_id = local_order.pk
    bundle.local_order_number = local_order.order_number
    bundle.tracking_token = tracking_token
    bundle.entities["created_order_number"] = (
        local_order.order_number
    )
    bundle.entities["order_number"] = local_order.order_number
    snapshot.update(
        {
            "local_order_id": local_order.pk,
            "local_order_number": local_order.order_number,
            "tracking_token": tracking_token,
        }
    )
    shopify_result = None
    existing_draft_id = (
        bundle.shopify_draft_order_id
        or snapshot.get("shopify_draft_order_id")
    )
    existing_draft_name = (
        bundle.shopify_draft_order_name
        or snapshot.get("shopify_draft_order_name")
    )
    existing_invoice_url = (
        bundle.shopify_invoice_url
        or snapshot.get("shopify_invoice_url")
    )
    if (
        existing_draft_id
        and existing_draft_name
        and existing_invoice_url
    ):
        shopify_result = {
            "status": "created",
            "draft_order_id": existing_draft_id,
            "draft_order_name": existing_draft_name,
            "invoice_url": existing_invoice_url,
        }
        bundle.shopify_sync_status = "reused"
    elif not _SHOPIFY_ENABLED:
        bundle.shopify_sync_status = "disabled"
    else:
        variant_id = (
            bundle.last_product_variant_id
            or snapshot.get("variant_id")
        )
        if not variant_id:
            product_name = (
                snapshot.get("name")
                or snapshot.get("title")
                or ""
            )
            if product_name:
                try:
                    matched = _enrich_with_shopify_variant(
                        {"name": product_name},
                        _safe_shopify_products(),
                    )
                    variant_id = matched.get("variant_id")
                    if variant_id:
                        bundle.last_product_variant_id = variant_id
                        snapshot["variant_id"] = variant_id
                except Exception as exc:
                    logger.warning(
                        "Optional Shopify variant lookup failed: %s",
                        exc,
                    )
        if variant_id:
            try:
                candidate_result = create_shopify_draft_order(
                    variant_id=variant_id,
                    quantity=bundle.quantity,
                    customer_name=bundle.user_name,
                    phone=bundle.phone,
                    address=bundle.address,
                    email=order_email,
                )
                if candidate_result.get("status") == "created":
                    shopify_result = candidate_result
                    bundle.shopify_sync_status = "created"
                else:
                    bundle.shopify_sync_status = "failed"
                    bundle.shopify_sync_error = (
                        "Shopify did not create a draft order."
                    )
                    logger.warning(
                        "Optional Shopify draft was not created: %r",
                        candidate_result,
                    )
            except Exception as exc:
                bundle.shopify_sync_status = "failed"
                bundle.shopify_sync_error = str(exc)[:300]
                logger.warning(
                    "Optional Shopify draft creation failed; "
                    "local order %s remains valid: %s",
                    local_order.order_number,
                    exc,
                )
        else:
            bundle.shopify_sync_status = "skipped"
    if shopify_result:
        bundle.shopify_draft_order_id = shopify_result[
            "draft_order_id"
        ]
        bundle.shopify_draft_order_name = shopify_result[
            "draft_order_name"
        ]
        bundle.shopify_invoice_url = shopify_result[
            "invoice_url"
        ]
        snapshot.update(
            {
                "shopify_draft_order_id": (
                    bundle.shopify_draft_order_id
                ),
                "shopify_draft_order_name": (
                    bundle.shopify_draft_order_name
                ),
                "shopify_invoice_url": (
                    bundle.shopify_invoice_url
                ),
            }
        )
    snapshot["shopify_sync_status"] = (
        bundle.shopify_sync_status
    )
    if conv and hasattr(conv, "last_product_data"):
        try:
            current_data = {}
            if conv.last_product_data:
                current_data = (
                    json.loads(conv.last_product_data)
                    if isinstance(conv.last_product_data, str)
                    else (conv.last_product_data or {})
                )
            current_data.update(snapshot)
            conv.last_product_data = json.dumps(
                current_data,
                ensure_ascii=False,
            )
            conv.purchase_state = PurchaseState.IDLE.value
            update_fields = [
                "last_product_data",
                "purchase_state",
            ]
            if hasattr(conv, "order_id"):
                conv.order_id = local_order.pk
                update_fields.append("order_id")
            conv.save(
                update_fields=list(set(update_fields)),
            )
        except Exception as exc:
            logger.warning(
                "Could not persist order data to conversation: %s",
                exc,
            )
    bundle.purchase_state = PurchaseState.IDLE
    bundle.intent = "order_created"
    bundle.intent_conf = 1.0
    bundle.response_conf = 0.98
    first_item = local_order.items.first()
    product_name = (
        snapshot.get("name")
        or snapshot.get("title")
        or (first_item.product_name if first_item else "Product")
    )
    if bundle.language == "ar":
        bundle.response = (
            f"تم إنشاء طلبك بنجاح 🎉\n"
            f"📦 المنتج: {product_name}\n"
            f"🔢 رقم الطلب: {local_order.order_number}\n"
        )
        if shopify_result:
            bundle.response += (
                f"💳 رابط الدفع: "
                f"{bundle.shopify_invoice_url}\n"
            )
        else:
            bundle.response += (
                "💵 طريقة الدفع: الدفع عند الاستلام\n"
            )
        bundle.response += (
            "احتفظي برقم الطلب لمتابعة حالته."
        )
    else:
        bundle.response = (
            f"Your order was created successfully 🎉\n"
            f"📦 Product: {product_name}\n"
            f"🔢 Order number: {local_order.order_number}\n"
        )
        if shopify_result:
            bundle.response += (
                f"💳 Payment link: "
                f"{bundle.shopify_invoice_url}\n"
            )
        else:
            bundle.response += (
                "💵 Payment method: Cash on delivery\n"
            )
        bundle.response += (
            "Keep the order number to track its status."
        )
    logger.info(
        "Local order %s created; Shopify sync status=%s",
        local_order.order_number,
        bundle.shopify_sync_status,
    )
    return True

class _ResponseDirector:
    _MEDICAL_AR = "أنا مش بديل للطبيب، ولو الأعراض شديدة أو مستمرة يُفضل استشارة طبيب. أقدر أساعدك بمنتجات متابعة صحية زي جهاز قياس الضغط أو جهاز قياس السكر لو حابة."
    _MEDICAL_EN = "I'm not a substitute for a doctor. If symptoms are severe or persistent, please consult a healthcare professional. I can help with health-monitoring products like blood pressure or glucose monitors."
    _LEGAL_AR = "أنا مش مؤهل لتقديم استشارات قانونية. يُفضل مراجعة محامي متخصص."
    _LEGAL_EN = "I'm not qualified to give legal advice. Please consult a qualified attorney."
    _FINANCIAL_AR = "أنا مش مؤهل لتقديم استشارات مالية. يُفضل مراجعة مستشار مالي متخصص."
    _FINANCIAL_EN = "I'm not qualified to give financial advice. Please consult a financial advisor."
    _HARMFUL_AR = "مش قادر أساعد في ده 😊 تحب أساعدك في منتجات المتجر؟"
    _HARMFUL_EN = "I can't help with that 😊 Can I assist you with our store products?"

    @staticmethod
    def run(bundle: SignalBundle, conv) -> None:
        bundle.trace("response_director")
        ar = bundle.language == "ar"
        if bundle.response:
            return
        if bundle.is_medical_symptom:
            bundle.response = _ResponseDirector._MEDICAL_AR if ar else _ResponseDirector._MEDICAL_EN
            bundle.response_conf = 1.0
            return
        if bundle.is_legal_advice:
            bundle.response = _ResponseDirector._LEGAL_AR if ar else _ResponseDirector._LEGAL_EN
            bundle.response_conf = 1.0
            return
        if bundle.is_financial_advice:
            bundle.response = _ResponseDirector._FINANCIAL_AR if ar else _ResponseDirector._FINANCIAL_EN
            bundle.response_conf = 1.0
            return
        if bundle.is_harmful:
            bundle.response = _ResponseDirector._HARMFUL_AR if ar else _ResponseDirector._HARMFUL_EN
            bundle.response_conf = 1.0
            return
        if bundle.intent == "out_of_scope":
            bundle.response = ("أنا مخصص للمساعدة في الطلبات والمنتجات فقط 😊 تحب أساعدك في حاجة تخص المتجر؟" if ar else "I'm here to help with products and orders only 😊 Can I help you with something from our store?")
            bundle.response_conf = 1.0
            bundle.recommendations = []
            return
        if bundle.intent == "unknown":
            bundle.response = ("ممكن توضحي سؤالك أكتر عشان أقدر أساعدك؟" if ar else "Could you clarify your question so I can help you better?")
            bundle.response_conf = 1.0
            bundle.recommendations = []
            return
        if bundle.intent in ("order_confirmed", "order_created") and bundle.response:
            return
        if bundle.intent in ("browse_products", "product_search", "order_tracking") and bundle.response:
            return
        order_status = None
        if bundle.intent == "order_tracking":
            order_num = bundle.entities.get("order_number")
            if order_num:
                try:
                    Order = apps.get_model("orders", "Order")
                    order_obj = Order.objects.filter(order_number__iexact=order_num).first()
                    if order_obj:
                        order_status = order_obj.get_status_display()
                except Exception as exc:
                    logger.warning("Could not fetch order status: %s", exc)
        missing_fields = []
        if bundle.purchase_state != PurchaseState.IDLE:
            if not bundle.user_name: missing_fields.append("الاسم")
            if not bundle.phone: missing_fields.append("رقم الهاتف")
            if not bundle.address: missing_fields.append("العنوان")
            if not bundle.quantity: missing_fields.append("الكمية")
        context = {
            "language": bundle.language,
            "intent": bundle.intent,
            "intent_confidence": bundle.intent_conf,
            "sentiment": bundle.sentiment,
            "user_name": bundle.user_name,
            "recommendations": bundle.recommendations,
            "purchase_state": bundle.purchase_state.value,
            "last_intent": bundle.last_intent,
            "entities": bundle.entities,
            "missing_fields": missing_fields,
            "order_status": order_status,
            "order_id": bundle.entities.get("order_number") or bundle.order_id,
            "ticket_id": None,
            "selected_product": bundle.last_product_snapshot,
            "last_product": bundle.last_product_snapshot,
            "phone": bundle.phone,
            "address": bundle.address,
            "quantity": bundle.quantity,
        }
        gen_model = _ModelRegistry.get("generation")
        if gen_model:
            result = gen_model.generate(bundle.message, context)
            raw = result.get("response", "")
            bundle.response = _RE_GARBAGE.sub("", raw).strip()
            bundle.response_conf = result.get("confidence", 0.0)
        else:
            bundle.response = ("أنا هنا للمساعدة 😊 أقدر أساعدك في إيه؟" if ar else "I'm here to help! How can I assist you?")
            bundle.response_conf = 0.0

class _ConversationManager:
    @staticmethod
    def load(bundle: SignalBundle, conversation_id: Optional[int]):
        conv = None
        if not conversation_id:
            return conv
        try:
            Conversation = apps.get_model("chat", "Conversation")
            conv = Conversation.objects.get(id=conversation_id)
            bundle.user_name = bundle.user_name or conv.user_name
            bundle.phone = bundle.phone or getattr(conv, "phone", None)
            bundle.email = bundle.email or getattr(conv, "email", None)
            bundle.quantity = bundle.quantity or getattr(conv, "quantity", None)
            bundle.order_id = bundle.order_id or getattr(conv, "order_id", None)
            bundle.address = bundle.address or getattr(conv, "address", None)
            bundle.last_product_id = conv.last_product_id
            bundle.last_intent = conv.last_intent
            raw_snapshot = getattr(conv, "last_product_data", None)
            if raw_snapshot:
                try:
                    snapshot = json.loads(raw_snapshot) if isinstance(raw_snapshot, str) else raw_snapshot
                    bundle.last_product_snapshot = snapshot
                    if isinstance(snapshot, dict):
                        bundle.shopify_draft_order_id = snapshot.get("shopify_draft_order_id")
                        bundle.shopify_draft_order_name = snapshot.get("shopify_draft_order_name")
                        bundle.shopify_invoice_url = snapshot.get("shopify_invoice_url")
                        bundle.local_order_number = snapshot.get("local_order_number")
                        bundle.tracking_token = snapshot.get("tracking_token")
                        if not bundle.last_product_variant_id:
                            bundle.last_product_variant_id = snapshot.get("variant_id")
                except (ValueError, TypeError):
                    bundle.last_product_snapshot = None
            raw_state = getattr(conv, "purchase_state", None) or "idle"
            bundle.purchase_state = (
                PurchaseState(raw_state)
                if raw_state in PurchaseState._value2member_map_
                else PurchaseState.IDLE
            )
        except Exception as exc:
            logger.warning("Could not load conversation %s: %s", conversation_id, exc)
        return conv

    @staticmethod
    def save(bundle: SignalBundle, conv, new_user_name: Optional[str]) -> None:
        if not conv:
            return
        try:
            update_fields = ["last_intent", "language"]
            conv.last_intent = bundle.intent
            conv.language = bundle.language
            resolved_name = new_user_name or bundle.user_name
            if resolved_name and resolved_name != getattr(conv, "user_name", None):
                conv.user_name = resolved_name
                bundle.user_name = resolved_name
                update_fields.append("user_name")
            if bundle.phone and bundle.phone != getattr(conv, "phone", None):
                conv.phone = bundle.phone
                update_fields.append("phone")
            if bundle.email and bundle.email != getattr(conv, "email", None):
                conv.email = bundle.email
                update_fields.append("email")
            if bundle.quantity and bundle.quantity != getattr(conv, "quantity", None):
                conv.quantity = bundle.quantity
                update_fields.append("quantity")
            if bundle.address and bundle.address != getattr(conv, "address", None):
                conv.address = bundle.address
                update_fields.append("address")
            if bundle.order_id and bundle.order_id != getattr(conv, "order_id", None):
                conv.order_id = bundle.order_id
                update_fields.append("order_id")
            if bundle.purchase_state.value != getattr(conv, "purchase_state", None):
                conv.purchase_state = bundle.purchase_state.value
                update_fields.append("purchase_state")
            selected_product_methods = {
                "catalog_selected",
                "shopify_selected",
                "last_product_snapshot",
                "conversation_context",
            }
            should_persist_selected_product = (
                bundle.recommendation_method in selected_product_methods
                or bundle.purchase_state != PurchaseState.IDLE
                or bundle.order_id is not None
            )
            if should_persist_selected_product and bundle.last_product_id:
                if bundle.last_product_id != conv.last_product_id:
                    conv.last_product_id = bundle.last_product_id
                    update_fields.append("last_product_id")
            if (
                should_persist_selected_product
                and bundle.last_product_snapshot is not None
            ):
                snapshot_data = bundle.last_product_snapshot.copy()
                if bundle.shopify_draft_order_id:
                    snapshot_data["shopify_draft_order_id"] = bundle.shopify_draft_order_id
                    snapshot_data["shopify_draft_order_name"] = bundle.shopify_draft_order_name
                    snapshot_data["shopify_invoice_url"] = bundle.shopify_invoice_url
                if bundle.order_id:
                    snapshot_data["local_order_id"] = bundle.order_id
                if bundle.local_order_number:
                    snapshot_data["local_order_number"] = bundle.local_order_number
                if bundle.tracking_token:
                    snapshot_data["tracking_token"] = bundle.tracking_token
                if bundle.last_product_variant_id:
                    snapshot_data["variant_id"] = bundle.last_product_variant_id
                new_snap_json = json.dumps(snapshot_data, ensure_ascii=False)
                old_snap_raw = getattr(conv, "last_product_data", None)
                old_snap_json = (
                    json.dumps(old_snap_raw, ensure_ascii=False)
                    if isinstance(old_snap_raw, dict)
                    else (old_snap_raw or "")
                )
                if new_snap_json != old_snap_json:
                    try:
                        conv.last_product_data = new_snap_json
                        update_fields.append("last_product_data")
                    except AttributeError:
                        pass
            conv.save(update_fields=list(set(update_fields)))
        except Exception as exc:
            logger.warning("Could not save conversation: %s", exc)

class ModelOrchestrator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def process_message(
        self,
        message: str,
        conversation_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        text = message or kwargs.get("text", "")
        if not text.strip():
            return {"success": False, "error": "Empty message"}
        bundle = SignalBundle(
            message=text,
            authenticated_user_id=user_id,
        )
        _LanguageDetector.run(bundle)
        is_blocked = _SafetyLayer.run(bundle)
        conv = _ConversationManager.load(bundle, conversation_id)
        bundle._conv = conv
        if is_blocked:
            _ResponseDirector.run(bundle, conv)
            _ConversationManager.save(bundle, conv, None)
            return self._build_result(bundle)
        _IntentStage.run(bundle)
        _SentimentStage.run(bundle)
        complaint_handled = _ComplaintStage.run(bundle, conv)
        if complaint_handled:
            _ConversationManager.save(
                bundle,
                conv,
                bundle.entities.get("user_name"),
            )
            return self._build_result(bundle)
        ticket_tracking_handled = _TicketTrackingStage.run(
            bundle,
            conv,
        )
        if ticket_tracking_handled:
            _ConversationManager.save(
                bundle,
                conv,
                bundle.entities.get("user_name"),
            )
            return self._build_result(bundle)
        tracking_handled = _OrderTrackingStage.run(bundle)
        if tracking_handled:
            _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
            return self._build_result(bundle)
        if bundle.purchase_state == PurchaseState.IDLE:
            browse_handled = _BrowseProductsStage.run(bundle)
            if browse_handled:
                _ConversationManager.save(
                    bundle,
                    conv,
                    bundle.entities.get("user_name"),
                )
                return self._build_result(bundle)
            product_selection_handled = _ProductSelectionStage.run(
                bundle,
                conv,
            )
            if product_selection_handled:
                _ConversationManager.save(
                    bundle,
                    conv,
                    bundle.entities.get("user_name"),
                )
                return self._build_result(bundle)
            product_search_handled = _ProductSearchStage.run(bundle)
            if product_search_handled:
                _ConversationManager.save(
                    bundle,
                    conv,
                    bundle.entities.get("user_name"),
                )
                return self._build_result(bundle)
        checkout_ai_result = _CheckoutAIStage.run(bundle)
        if checkout_ai_result:
            _save_order_data_to_conversation(bundle, conv)
            _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
            return self._build_result(bundle)
        sm_handled = False
        if bundle.purchase_state != PurchaseState.IDLE:
            sm_handled = StateMachine.run(bundle, conv)
        if sm_handled:
            _save_order_data_to_conversation(bundle, conv)
            _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
            return self._build_result(bundle)
        if bundle.purchase_state == PurchaseState.READY_TO_ORDER:
            order_created = _create_shopify_order_and_confirm(bundle, conv)
            if order_created:
                _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
                return self._build_result(bundle)
        router = _ModelRouterStage()
        lock_product = (
            bundle.last_product_snapshot
            and not bundle.recommendations
            and not bundle.entities.get("product_name")
        )
        if lock_product:
            bundle.recommendations = [bundle.last_product_snapshot]
            bundle.recommendation_method = "last_product_snapshot"
            bundle.last_product_id = bundle.last_product_snapshot.get("product_id") or bundle.last_product_id
            if not bundle.last_product_variant_id:
                bundle.last_product_variant_id = bundle.last_product_snapshot.get("variant_id")
            bundle.trace("product_context_lock")
        elif router.should_recommend(bundle) and not router.is_vague(bundle):
            _RecommendationStage.run(bundle, user_id)
        elif router.is_vague(bundle):
            bundle.entities["_vague"] = True
        if not bundle.recommendations and bundle.last_product_id:
            if bundle.last_product_snapshot:
                bundle.recommendations = [bundle.last_product_snapshot]
                bundle.recommendation_method = "last_product_snapshot"
            else:
                try:
                    Product = apps.get_model("products", "Product")
                    product = Product.objects.get(id=bundle.last_product_id)
                    bundle.recommendations = [{
                        "product_id": product.id,
                        "name": product.name,
                        "price": float(product.price),
                        "description": product.description,
                        "score": 1.0,
                        "emoji": getattr(product, "emoji", "📦"),
                    }]
                    bundle.recommendation_method = "conversation_context"
                except Exception as exc:
                    logger.warning("Could not load last product: %s", exc)
        if bundle.recommendations:
            bundle.last_product_id = bundle.recommendations[0].get("product_id") or bundle.last_product_id
            if not bundle.last_product_variant_id:
                bundle.last_product_variant_id = bundle.recommendations[0].get("variant_id")
        if bundle.recommendations and bundle.recommendation_method not in ("last_product_snapshot", "conversation_context"):
            bundle.last_product_snapshot = bundle.recommendations[0]
        if bundle.entities.get("user_name"):
            bundle.user_name = bundle.entities["user_name"]
        _save_order_data_to_conversation(bundle, conv)
        _ResponseDirector.run(bundle, conv)
        _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
        return self._build_result(bundle)

    def _build_result(self, bundle: SignalBundle) -> Dict[str, Any]:
        shopify_draft_order_id = bundle.shopify_draft_order_id
        shopify_draft_order_name = bundle.shopify_draft_order_name
        shopify_invoice_url = bundle.shopify_invoice_url
        if bundle.last_product_snapshot:
            shopify_draft_order_id = shopify_draft_order_id or bundle.last_product_snapshot.get("shopify_draft_order_id")
            shopify_draft_order_name = shopify_draft_order_name or bundle.last_product_snapshot.get("shopify_draft_order_name")
            shopify_invoice_url = shopify_invoice_url or bundle.last_product_snapshot.get("shopify_invoice_url")
        local_order_number = (
            bundle.local_order_number
            or bundle.entities.get("created_order_number")
            or bundle.entities.get("order_number")
        )
        tracking_token = bundle.tracking_token
        if bundle.last_product_snapshot:
            local_order_number = (
                local_order_number
                or bundle.last_product_snapshot.get(
                    "local_order_number"
                )
            )
            tracking_token = (
                tracking_token
                or bundle.last_product_snapshot.get(
                    "tracking_token"
                )
            )
        return {
            "success": True,
            "response": bundle.response,
            "intent": bundle.intent,
            "sentiment": bundle.sentiment,
            "confidence": {
                "intent": round(bundle.intent_conf, 3),
                "sentiment": round(bundle.sentiment_conf, 3),
            },
            "recommendations": bundle.recommendations,
            "order_id": bundle.order_id,
            "order_number": local_order_number,
            "tracking_token": tracking_token,
            "metadata": {
                "recommendation_method": bundle.recommendation_method,
                "user_name": bundle.user_name,
                "detected_language": bundle.language,
                "purchase_state": bundle.purchase_state.value,
                "intent_confidence": round(bundle.intent_conf, 3),
                "sentiment": bundle.sentiment,
                "sentiment_confidence": round(bundle.sentiment_conf, 3),
                "pipeline_confidence": round(bundle.confidence_score(), 3),
                "routing_trace": bundle.routing_trace,
                "response_confidence": round(bundle.response_conf, 3),
                "shopify_draft_order_id": shopify_draft_order_id,
                "shopify_draft_order_name": shopify_draft_order_name,
                "shopify_invoice_url": shopify_invoice_url,
                "shopify_sync_status": bundle.shopify_sync_status,
                "checkout_intent": bundle.checkout_intent,
                "next_action": bundle.next_action,
                "checkout_ai_parse_failed": bundle.checkout_ai_parse_failed,
                "checkout_mode": bundle.checkout_mode,
                "checkout_fallback_used": bundle.checkout_fallback_used,
                "complaint_state": bundle.complaint_state,
                "ticket_id": bundle.ticket_id,
                "ticket_number": bundle.ticket_number,
                "ticket_status": bundle.ticket_status,
                "human_handoff": bundle.human_handoff,
                "order_id": bundle.order_id,
                "order_number": local_order_number,
                "tracking_token": tracking_token,
            },
        }

    def _analyze_intent_safe(self, message: str, last_intent: str = None) -> Dict[str, Any]:
        bundle = SignalBundle(message=message, last_intent=last_intent)
        _IntentStage.run(bundle)
        return {"intent": bundle.intent, "confidence": bundle.intent_conf}

    def _analyze_sentiment_safe(self, message: str) -> Dict[str, Any]:
        bundle = SignalBundle(message=message)
        _SentimentStage.run(bundle)
        return {"sentiment": bundle.sentiment, "confidence": bundle.sentiment_conf}

    def _classify_intent_safe(self, message: str) -> Dict[str, Any]:
        return self._analyze_intent_safe(message)

    def _get_recommendations_stable(self, user_id: Optional[int], intent: str, query: str) -> Tuple[List[Dict], str]:
        bundle = SignalBundle(message=query, intent=intent)
        bundle.entities["product_name"] = query
        _RecommendationStage.run(bundle, user_id)
        return bundle.recommendations, bundle.recommendation_method

    def get_model_status(self) -> Dict[str, Any]:
        return {
            "status": "operational",
            "intent_model": _ModelRegistry.get("intent") is not None,
            "sentiment_model": _ModelRegistry.get("sentiment") is not None,
            "recommendation_model": _ModelRegistry.get("recommendation") is not None,
            "generation_model": _ModelRegistry.get("generation") is not None,
        }

    def detect_language(self, text: str) -> str:
        return "ar" if _RE_ARABIC.search(text) else "en"

    def extract_entities(self, text: str, lang: str) -> Dict[str, Any]:
        bundle = SignalBundle(message=text)
        _LanguageDetector.run(bundle)
        return bundle.entities

    def _classify_intent(self, message):
        from .intent_classification.model import IntentClassificationModel
        return IntentClassificationModel().predict(message)

    def _analyze_sentiment(self, message):
        from .sentiment_analysis.model import SentimentAnalysisModel
        return SentimentAnalysisModel().predict(message)

    def _get_recommendations(self, intent, user_id=None, **kwargs):
        from .product_recommendation.model import ProductRecommendationModel

        model = ProductRecommendationModel()
        result = model.predict(intent=intent)

        if isinstance(result, dict):
            return result.get("recommendations", [])

        return result or []

    def _generate_response(
        self,
        message,
        intent=None,
        sentiment=None,
        recommendations=None,
        **kwargs,
    ):
        from .response_generation.model import ResponseGenerationModel

        intent_value = intent.get("intent") if isinstance(intent, dict) else intent
        sentiment_value = (
            sentiment.get("sentiment")
            if isinstance(sentiment, dict)
            else sentiment
        )

        context = {
            "intent": intent_value,
            "sentiment": sentiment_value,
            "recommendations": recommendations or [],
        }

        return ResponseGenerationModel().generate(message, context=context)

    def __del__(self):
        gc.collect()