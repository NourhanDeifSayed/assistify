from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Optional, TYPE_CHECKING

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
    AWAITING_PHONE = "awaiting_phone"
    AWAITING_ADDRESS = "awaiting_address"
    AWAITING_QUANTITY = "awaiting_quantity"
    READY_TO_ORDER = "ready_to_order"


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
            PurchaseState.AWAITING_PHONE: StateMachine._collect_phone,
            PurchaseState.AWAITING_ADDRESS: StateMachine._collect_address,
            PurchaseState.AWAITING_QUANTITY: StateMachine._collect_quantity,
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

        product_name = (
            bundle.last_product_snapshot.get("name")
            or bundle.last_product_snapshot.get("title")
            or "المنتج"
        )

        if not bundle.user_name:
            StateMachine._set_state(
                bundle,
                conv,
                PurchaseState.AWAITING_NAME,
            )

            if bundle.language == "ar":
                bundle.response = (
                    f"تمام، هنبدأ طلب {product_name}. "
                    "محتاجة اسمك الكامل عشان أكمل الطلب."
                )
            else:
                bundle.response = (
                    f"Great, let's start ordering {product_name}. "
                    "Please share your full name."
                )

            bundle.response_conf = 0.95
            return True

        if not bundle.phone:
            StateMachine._set_state(
                bundle,
                conv,
                PurchaseState.AWAITING_PHONE,
            )

            if bundle.language == "ar":
                bundle.response = (
                    f"أهلًا {bundle.user_name}. ممكن رقم الموبايل؟"
                )
            else:
                bundle.response = (
                    f"Hello {bundle.user_name}. "
                    "Could you share your phone number?"
                )

            bundle.response_conf = 0.95
            return True

        if not bundle.address:
            StateMachine._set_state(
                bundle,
                conv,
                PurchaseState.AWAITING_ADDRESS,
            )

            if bundle.language == "ar":
                bundle.response = "تمام، دلوقتي محتاجة عنوان التوصيل."
            else:
                bundle.response = "Great. Now I need your delivery address."

            bundle.response_conf = 0.95
            return True

        if not bundle.quantity:
            StateMachine._set_state(
                bundle,
                conv,
                PurchaseState.AWAITING_QUANTITY,
            )

            if bundle.language == "ar":
                bundle.response = "تمام، كام قطعة تحبي تطلبي؟"
            else:
                bundle.response = "Great. How many units would you like?"

            bundle.response_conf = 0.95
            return True

        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.READY_TO_ORDER,
        )
        return False

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
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.AWAITING_PHONE,
        )

        if conv:
            conv.user_name = name
            try:
                conv.save(
                    update_fields=[
                        "user_name",
                        "purchase_state",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save user name: %s",
                    exc,
                )

        if bundle.phone:
            return StateMachine._collect_phone(bundle, conv)

        if bundle.language == "ar":
            bundle.response = f"أهلًا {name}. ممكن رقم الموبايل؟"
        else:
            bundle.response = (
                f"Nice to meet you, {name}. "
                "Could you share your phone number?"
            )

        bundle.response_conf = 0.95
        return True

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
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.AWAITING_ADDRESS,
        )

        if conv:
            conv.phone = phone
            try:
                conv.save(
                    update_fields=[
                        "phone",
                        "purchase_state",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save phone: %s",
                    exc,
                )

        if bundle.address:
            return StateMachine._collect_address(bundle, conv)

        if bundle.language == "ar":
            bundle.response = "تمام، دلوقتي محتاجة عنوان التوصيل."
        else:
            bundle.response = "Got it. Now I need your delivery address."

        bundle.response_conf = 0.95
        return True

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
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.AWAITING_QUANTITY,
        )

        if conv:
            conv.address = candidate
            try:
                conv.save(
                    update_fields=[
                        "address",
                        "purchase_state",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save address: %s",
                    exc,
                )

        if bundle.quantity:
            return StateMachine._collect_quantity(bundle, conv)

        if bundle.language == "ar":
            bundle.response = "تمام، كام قطعة تحبي تطلبي؟"
        else:
            bundle.response = "Got it. How many units would you like?"

        bundle.response_conf = 0.95
        return True

    @staticmethod
    def _collect_quantity(bundle: "SignalBundle", conv) -> bool:
        quantity = bundle.quantity
        text = bundle.message.strip()

        if not quantity:
            match = re.search(r"\b(\d{1,2})\b", text)
            if match:
                quantity = int(match.group(1))

        if not quantity or not 1 <= quantity <= 99:
            if bundle.language == "ar":
                bundle.response = "ابعت الكمية كرقم من 1 إلى 99."
            else:
                bundle.response = "Please provide a quantity from 1 to 99."

            bundle.response_conf = 0.95
            return True

        bundle.quantity = quantity
        bundle.intent = "provide_quantity"
        bundle.intent_conf = 1.0
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.READY_TO_ORDER,
        )

        if conv:
            conv.quantity = quantity
            try:
                conv.save(
                    update_fields=[
                        "quantity",
                        "purchase_state",
                    ]
                )
            except Exception as exc:
                logger.warning(
                    "Could not save quantity: %s",
                    exc,
                )

        # Returning False lets the orchestrator immediately create the order.
        return False

    @staticmethod
    def _handle_cancel(bundle: "SignalBundle", conv) -> bool:
        bundle.intent = "cancel_purchase"
        bundle.intent_conf = 1.0
        StateMachine._set_state(
            bundle,
            conv,
            PurchaseState.IDLE,
        )

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
