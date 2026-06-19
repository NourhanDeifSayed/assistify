from __future__ import annotations

import logging
import re
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from .orchestrator import SignalBundle


logger = logging.getLogger(__name__)

_RE_PHONE = re.compile(r"^01[0125][0-9]{8}$")

_CANCEL_WORDS = frozenset(
    [
        "الغاء الطلب",
        "إلغاء الطلب",
        "الغي الطلب",
        "ألغي الطلب",
        "مش عايز",
        "مش عايزة",
        "عايز الغاء",
        "عايزة الغاء",
        "عايز إلغاء",
        "عايزة إلغاء",
        "cancel order",
        "cancel my order",
        "cancel purchase",
        "i want to cancel",
        "please cancel",
    ]
)

_ADDRESS_REJECT_TERMS = frozenset(
    [
        "monitor",
        "thermometer",
        "oximeter",
        "nebulizer",
        "glucose",
        "pulse",
        "blood pressure",
        "heart rate",
        "heating pad",
        "mask",
        "infrared",
        "digital",
        "جهاز",
        "ترمومتر",
        "كمامة",
        "بخاخ",
        "سكر",
        "ضغط",
        "قياس",
        "عايز",
        "عايزة",
        "أطلب",
        "اطلب",
        "طلب",
        "شراء",
        "أشتري",
        "اشتري",
        "buy",
        "order",
        "purchase",
    ]
)

_ADDRESS_INDICATORS = frozenset(
    [
        "شارع",
        "ش ",
        "حي",
        "منطقة",
        "محافظة",
        "بجوار",
        "أمام",
        "خلف",
        "الدور",
        "شقة",
        "عمارة",
        "برج",
        "مبنى",
        "بلوك",
        "القاهرة",
        "الجيزة",
        "الإسكندرية",
        "اسكندرية",
        "المنصورة",
        "الدقهلية",
        "الشرقية",
        "المنوفية",
        "البحيرة",
        "الغربية",
        "أسيوط",
        "سوهاج",
        "قنا",
        "الأقصر",
        "أسوان",
        "مدينة نصر",
        "المعادي",
        "الزيتون",
        "شبرا",
        "هليوبوليس",
        "المهندسين",
        "الدقي",
        "العجوزة",
        "الهرم",
        "فيصل",
        "street",
        "avenue",
        "district",
        "city",
        "cairo",
        "giza",
    ]
)

_RE_NAME_AR = re.compile(
    r"(?:اسمي|أنا\s+اسمي|انا\s+اسمي|اسمي\s+هو|معاك)\s+"
    r"([\u0600-\u06FF]{2,}(?:\s+[\u0600-\u06FF]{2,}){0,2})"
)

_RE_NAME_EN = re.compile(
    r"^(?:my\s+name\s+is|i'm|i\s+am|this\s+is|call\s+me)\s+"
    r"([a-zA-Z]{2,}(?:\s+[a-zA-Z]{2,}){0,2})[.!]?$",
    re.IGNORECASE,
)

_NAME_BLACKLIST = frozenset(
    [
        "اسمي",
        "ايه",
        "إيه",
        "أنا",
        "انا",
        "مين",
        "هو",
        "هي",
        "ده",
        "دي",
        "بكام",
        "سعره",
        "معلومات",
        "تفاصيل",
        "عاوزة",
        "عايزة",
        "عايز",
        "فين",
        "مواصفات",
        "جهاز",
        "طلب",
        "what",
        "who",
        "is",
        "am",
        "the",
        "want",
        "need",
        "name",
        "this",
        "order",
        "product",
        "looking",
        "interested",
    ]
)


class PurchaseState(str, Enum):
    IDLE = "idle"
    AWAITING_NAME = "awaiting_name"
    AWAITING_EMAIL = "awaiting_email"
    AWAITING_PHONE = "awaiting_phone"
    AWAITING_ADDRESS = "awaiting_address"
    AWAITING_QUANTITY = "awaiting_quantity"
    READY_TO_ORDER = "ready_to_order"


def extract_email(text: str) -> Optional[str]:
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if match:
        email = match.group(0).strip().lower()
        try:
            validate_email(email)
            return email
        except ValidationError:
            return None
    return None


def extract_name(message: str, language: str) -> Optional[str]:
    text = (message or "").strip()

    if not text:
        return None

    pattern = _RE_NAME_AR if language == "ar" else _RE_NAME_EN
    match = pattern.search(text)

    if not match:
        return None

    name = " ".join(match.group(1).split()).strip()
    lowered_words = {word.lower() for word in name.split()}

    if not name or len(name.split()) > 3:
        return None

    if lowered_words & {word.lower() for word in _NAME_BLACKLIST}:
        return None

    return name


def extract_phone(message: str) -> Optional[str]:
    text = str(message or "").strip()
    digits_only = re.sub(r"\s+", "", text)
    digits_only = re.sub(r"^\+?20", "", digits_only)
    digits_only = re.sub(r"[()\-]", "", digits_only)

    if _RE_PHONE.fullmatch(digits_only):
        return digits_only

    compact_text = re.sub(r"[\s()\-]", "", text)
    match = re.search(r"01[0125]\d{8}", compact_text)

    if match:
        return match.group(0)

    return None


def is_valid_address(text: str) -> bool:
    candidate = str(text or "").strip()

    if len(candidate) < 8:
        return False

    lowered = candidate.lower()

    if any(term in lowered for term in _ADDRESS_REJECT_TERMS):
        return False

    if lowered.isdigit():
        return False

    if any(indicator in lowered for indicator in _ADDRESS_INDICATORS):
        return True

    return len(lowered.split()) >= 2


class StateMachine:
    @staticmethod
    def run(bundle: "SignalBundle", conv) -> bool:
        if bundle.purchase_state == PurchaseState.IDLE:
            logger.debug(
                "StateMachine.run called with IDLE state; skipping."
            )
            return False

        lowered = bundle.message.lower().strip()

        if any(word in lowered for word in _CANCEL_WORDS):
            return StateMachine._handle_cancel(bundle, conv)

        handlers = {
            PurchaseState.AWAITING_NAME: StateMachine._collect_name,
            PurchaseState.AWAITING_EMAIL: StateMachine._collect_email,
            PurchaseState.AWAITING_PHONE: StateMachine._collect_phone,
            PurchaseState.AWAITING_ADDRESS: StateMachine._collect_address,
            PurchaseState.AWAITING_QUANTITY: StateMachine._collect_quantity,
            PurchaseState.READY_TO_ORDER: StateMachine._confirm_order,
        }

        handler = handlers.get(bundle.purchase_state)

        if handler:
            return handler(bundle, conv)

        return False

    @staticmethod
    def start_purchase_flow(bundle: "SignalBundle", conv) -> bool:
        bundle.intent = "purchase_intent"
        bundle.intent_conf = 1.0
        bundle.response = ""

        # Clear stale checkout fields for a new order
        bundle.phone = ""
        bundle.email = ""
        bundle.address = ""
        bundle.quantity = None

        if conv:
            conv.phone = None
            conv.email = None
            conv.address = None
            conv.quantity = None
            conv.order_id = None
            conv.purchase_state = PurchaseState.IDLE.value
            conv.save(update_fields=["phone", "email", "address", "quantity", "order_id", "purchase_state"])

        if not bundle.last_product_snapshot:
            if bundle.language == "ar":
                bundle.response = (
                    "مش عارف تقصد أي منتج تحديدًا. "
                    "ممكن تختار رقم المنتج من القائمة؟"
                )
            else:
                bundle.response = (
                    "I'm not sure which product you mean. "
                    "Please choose a product number from the catalog."
                )

            bundle.response_conf = 0.95
            return True

        # Check stock of the selected product first
        from assistify.apps.products.models import Product
        product_id = bundle.last_product_id or (bundle.last_product_snapshot.get("product_id") if bundle.last_product_snapshot else None)
        product = None
        if product_id:
            product = Product.objects.filter(id=product_id).first()
        if product and product.stock <= 0:
            if bundle.language == "ar":
                bundle.response = f"عذراً، منتج '{product.name}' غير متوفر في المخزن حالياً."
            else:
                bundle.response = f"Sorry, '{product.name}' is currently out of stock."
            bundle.response_conf = 0.95
            return True

        # Now start collecting fields
        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _transition_to_next_missing_field(bundle: "SignalBundle", conv) -> bool:
        if not bundle.user_name:
            StateMachine._set_state(bundle, conv, PurchaseState.AWAITING_NAME)
            if bundle.language == "ar":
                bundle.response = "محتاجة اسمك الكامل عشان أكمل الطلب."
            else:
                bundle.response = "Please share your full name."
            bundle.response_conf = 0.95
            return True

        if not bundle.email:
            StateMachine._set_state(bundle, conv, PurchaseState.AWAITING_EMAIL)
            if bundle.language == "ar":
                bundle.response = "ممكن تقوليلي البريد الإلكتروني بتاعك عشان نبعتلك تأكيد الطلب؟"
            else:
                bundle.response = "Could you please share your email address so we can send the order confirmation?"
            bundle.response_conf = 0.95
            return True

        if not bundle.phone:
            StateMachine._set_state(bundle, conv, PurchaseState.AWAITING_PHONE)
            if bundle.language == "ar":
                bundle.response = f"تمام يا {bundle.user_name}. ممكن رقم الموبايل؟"
            else:
                bundle.response = f"Hello {bundle.user_name}. Could you share your phone number?"
            bundle.response_conf = 0.95
            return True

        if not bundle.address:
            StateMachine._set_state(bundle, conv, PurchaseState.AWAITING_ADDRESS)
            if bundle.language == "ar":
                bundle.response = "تمام، دلوقتي محتاجة عنوان التوصيل بالتفصيل."
            else:
                bundle.response = "Great. Now I need your detailed delivery address."
            bundle.response_conf = 0.95
            return True

        if not bundle.quantity:
            StateMachine._set_state(bundle, conv, PurchaseState.AWAITING_QUANTITY)
            if bundle.language == "ar":
                bundle.response = "تمام، كام قطعة تحبي تطلبي؟"
            else:
                bundle.response = "Great. How many units would you like?"
            bundle.response_conf = 0.95
            return True

        # All fields are present! Transition to READY_TO_ORDER and show summary.
        StateMachine._set_state(bundle, conv, PurchaseState.READY_TO_ORDER)
        
        product_price = Decimal("0.00")
        product_name = "المنتج"
        if bundle.last_product_snapshot:
            product_price = Decimal(str(bundle.last_product_snapshot.get("price", "0.00")))
            product_name = bundle.last_product_snapshot.get("name") or bundle.last_product_snapshot.get("title") or product_name
        
        total_price = (product_price * Decimal(str(bundle.quantity))) + Decimal("50.00")
        
        if bundle.language == "ar":
            bundle.response = (
                f"إليك تفاصيل طلبك:\n"
                f"- المنتج: {product_name}\n"
                f"- الكمية: {bundle.quantity}\n"
                f"- الاسم: {bundle.user_name}\n"
                f"- البريد الإلكتروني: {bundle.email}\n"
                f"- الهاتف: {bundle.phone}\n"
                f"- العنوان: {bundle.address}\n"
                f"- طريقة الدفع: الدفع عند الاستلام\n"
                f"- السعر الإجمالي: {total_price} جنيه\n\n"
                f"هل تؤكد هذا الطلب؟ (اكتب 'نعم' أو 'تأكيد' لإتمام الطلب، أو 'إلغاء' للتراجع)"
            )
        else:
            bundle.response = (
                f"Here is a summary of your order:\n"
                f"- Product: {product_name}\n"
                f"- Quantity: {bundle.quantity}\n"
                f"- Customer Name: {bundle.user_name}\n"
                f"- Email: {bundle.email}\n"
                f"- Phone: {bundle.phone}\n"
                f"- Address: {bundle.address}\n"
                f"- Payment Method: Cash on delivery\n"
                f"- Total Price: EGP {total_price}\n\n"
                f"Do you confirm this order? (Please reply with 'yes' or 'confirm' to place the order, or 'cancel' to stop)"
            )
        bundle.response_conf = 0.95
        return True

    @staticmethod
    def _collect_name(bundle: "SignalBundle", conv) -> bool:
        name = bundle.user_name or extract_name(
            bundle.message,
            bundle.language,
        )

        if not name:
            candidate = bundle.message.strip()

            if (
                len(candidate) >= 2
                and not candidate.isdigit()
                and not extract_phone(candidate)
                and not any(
                    word in candidate.lower()
                    for word in _ADDRESS_REJECT_TERMS
                )
                and len(candidate.split()) <= 4
            ):
                name = candidate

        if not name:
            if bundle.language == "ar":
                bundle.response = "ممكن تقولي اسمك الكامل؟"
            else:
                bundle.response = "Could you please share your full name?"

            bundle.response_conf = 0.95
            return True

        bundle.user_name = name
        bundle.intent = "introduce_name"
        bundle.intent_conf = 1.0

        if conv:
            conv.user_name = name
            try:
                conv.save(
                    update_fields=[
                        "user_name",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save user name: %s",
                    exc,
                )

        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _collect_email(bundle: "SignalBundle", conv) -> bool:
        email = extract_email(bundle.message)

        if not email:
            if bundle.language == "ar":
                bundle.response = "البريد الإلكتروني غير صحيح. من فضلك اكتب بريد إلكتروني صحيح (مثل: name@example.com)."
            else:
                bundle.response = "Invalid email format. Please provide a valid email address (e.g., name@example.com)."
            bundle.response_conf = 0.95
            return True

        bundle.email = email
        bundle.intent = "provide_email"
        bundle.intent_conf = 1.0

        if conv:
            conv.email = email
            try:
                conv.save(update_fields=["email"])
            except Exception as exc:
                logger.warning("Could not save email: %s", exc)

        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _collect_phone(bundle: "SignalBundle", conv) -> bool:
        phone = bundle.phone or extract_phone(bundle.message)

        if not phone:
            if bundle.language == "ar":
                bundle.response = (
                    "الرقم ده مش صحيح. ابعت رقم موبايل مصري "
                    "زي 01012345678."
                )
            else:
                bundle.response = (
                    "That does not look like a valid Egyptian phone number. "
                    "Please use a number such as 01012345678."
                )

            bundle.response_conf = 0.95
            return True

        bundle.phone = phone
        bundle.intent = "provide_phone"
        bundle.intent_conf = 1.0

        if conv:
            conv.phone = phone
            try:
                conv.save(
                    update_fields=[
                        "phone",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save phone: %s",
                    exc,
                )

        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _collect_address(bundle: "SignalBundle", conv) -> bool:
        candidate = (
            bundle.address
            if bundle.address and is_valid_address(bundle.address)
            else bundle.message.strip()
        )

        if not is_valid_address(candidate):
            if bundle.language == "ar":
                bundle.response = (
                    "ممكن تبعت عنوان تفصيلي أكتر؟ "
                    "مثال: القاهرة - مدينة نصر - شارع عباس."
                )
            else:
                bundle.response = (
                    "Could you share a more detailed address? "
                    "For example: Cairo, Nasr City, Abbas Street."
                )

            bundle.response_conf = 0.95
            return True

        bundle.address = candidate
        bundle.intent = "provide_address"
        bundle.intent_conf = 1.0

        if conv:
            conv.address = candidate
            try:
                conv.save(
                    update_fields=[
                        "address",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save address: %s",
                    exc,
                )

        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _collect_quantity(bundle: "SignalBundle", conv) -> bool:
        quantity = bundle.quantity
        text = bundle.message.strip()

        if not quantity:
            match = re.search(r"(?<!-)\b(\d{1,2})\b", text)
            if match:
                quantity = int(match.group(1))

        if not quantity or not 1 <= quantity <= 99:
            if bundle.language == "ar":
                bundle.response = "ابعت الكمية كرقم من 1 إلى 99."
            else:
                bundle.response = "Please provide a quantity from 1 to 99."

            bundle.response_conf = 0.95
            return True

        # Check stock of the product for requested quantity
        from assistify.apps.products.models import Product
        product_id = bundle.last_product_id or (bundle.last_product_snapshot.get("product_id") if bundle.last_product_snapshot else None)
        product = None
        if product_id:
            product = Product.objects.filter(id=product_id).first()
        if product:
            if product.stock < quantity:
                if bundle.language == "ar":
                    bundle.response = f"عذراً، الكمية المطلوبة غير متوفرة. الكمية المتاحة حالياً هي {product.stock} فقط."
                else:
                    bundle.response = f"Sorry, the requested quantity is not available. The currently available stock is only {product.stock}."
                bundle.response_conf = 0.95
                return True

        bundle.quantity = quantity
        bundle.intent = "provide_quantity"
        bundle.intent_conf = 1.0

        if conv:
            conv.quantity = quantity
            try:
                conv.save(
                    update_fields=[
                        "quantity",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save quantity: %s",
                    exc,
                )

        return StateMachine._transition_to_next_missing_field(bundle, conv)

    @staticmethod
    def _confirm_order(bundle: "SignalBundle", conv) -> bool:
        text = bundle.message.strip().lower()
        confirm_words = {"yes", "confirm", "place order", "نعم", "تأكيد", "اكد الطلب", "موافق", "تمام"}
        cancel_words = {"cancel", "stop", "إلغاء", "الغي الطلب", "تراجع"}

        if any(w in text for w in confirm_words):
            # Explicit confirmation received, returning False lets orchestrator create the order.
            return False

        if any(w in text for w in cancel_words):
            return StateMachine._handle_cancel(bundle, conv)

        # Neither confirm nor cancel. Show summary again and ask them to confirm.
        product_name = "المنتج"
        product_price = Decimal("0.00")
        if bundle.last_product_snapshot:
            product_price = Decimal(str(bundle.last_product_snapshot.get("price", "0.00")))
            product_name = bundle.last_product_snapshot.get("name") or bundle.last_product_snapshot.get("title") or product_name
        
        total_price = (product_price * Decimal(str(bundle.quantity))) + Decimal("50.00")

        if bundle.language == "ar":
            bundle.response = (
                f"لم أفهم ردك بشكل واضح. يرجى تأكيد الطلب:\n"
                f"- المنتج: {product_name}\n"
                f"- الكمية: {bundle.quantity}\n"
                f"- الاسم: {bundle.user_name}\n"
                f"- البريد الإلكتروني: {bundle.email}\n"
                f"- الهاتف: {bundle.phone}\n"
                f"- العنوان: {bundle.address}\n"
                f"- السعر الإجمالي: {total_price} جنيه\n\n"
                f"يرجى الرد بـ 'تأكيد' أو 'نعم' لإتمام الطلب، أو 'إلغاء' للتراجع."
            )
        else:
            bundle.response = (
                f"I didn't quite get that. Please confirm your order:\n"
                f"- Product: {product_name}\n"
                f"- Quantity: {bundle.quantity}\n"
                f"- Customer Name: {bundle.user_name}\n"
                f"- Email: {bundle.email}\n"
                f"- Phone: {bundle.phone}\n"
                f"- Address: {bundle.address}\n"
                f"- Total Price: EGP {total_price}\n\n"
                f"Please reply with 'yes' or 'confirm' to place the order, or 'cancel' to stop."
            )
        bundle.response_conf = 0.95
        return True

    @staticmethod
    def _handle_cancel(bundle: "SignalBundle", conv) -> bool:
        bundle.intent = "cancel_purchase"
        bundle.intent_conf = 1.0
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.IDLE,
        )

        if conv:
            conv.phone = None
            conv.email = None
            conv.address = None
            conv.quantity = None
            conv.save(update_fields=["phone", "email", "address", "quantity"])

        if bundle.language == "ar":
            bundle.response = "تم إلغاء الطلب. أقدر أساعدك في حاجة تانية؟"
        else:
            bundle.response = "Order cancelled. How else can I help you?"

        bundle.response_conf = 0.95
        return True

    @staticmethod
    def _set_state(
        bundle: "SignalBundle",
        conv,
        state: PurchaseState,
    ) -> None:
        bundle.purchase_state = state

        if not conv:
            return

        conv.purchase_state = state.value

        try:
            conv.save(update_fields=["purchase_state"])
        except Exception as exc:
            logger.warning(
                "Could not save purchase state: %s",
                exc,
            )
