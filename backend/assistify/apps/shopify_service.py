import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)

SHOP = (
    os.getenv("SHOPIFY_STORE_DOMAIN", "")
    .strip()
    .removeprefix("https://")
    .removeprefix("http://")
    .rstrip("/")
)

TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "").strip()
VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-04").strip()


def validate_shopify_config() -> None:
    """
    Ensure Shopify credentials are configured before making API requests.
    """
    missing_variables = []

    if not SHOP:
        missing_variables.append("SHOPIFY_STORE_DOMAIN")

    if not TOKEN:
        missing_variables.append("SHOPIFY_ACCESS_TOKEN")

    if missing_variables:
        raise RuntimeError(
            "Missing Shopify environment variables: "
            + ", ".join(missing_variables)
        )


def shopify_graphql(
    query: str,
    variables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Send a GraphQL request to the Shopify Admin API.
    """
    validate_shopify_config()

    url = f"https://{SHOP}/admin/api/{VERSION}/graphql.json"

    headers = {
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        json={
            "query": query,
            "variables": variables or {},
        },
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("errors"):
        raise RuntimeError(
            f"Shopify GraphQL errors: {result['errors']}"
        )

    return result


def _extract_products(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert Shopify's GraphQL product response into a simpler structure.
    """
    products = []

    edges = (
        data.get("data", {})
        .get("products", {})
        .get("edges", [])
    )

    for edge in edges:
        node = edge.get("node", {})
        variant_edges = (
            node.get("variants", {})
            .get("edges", [])
        )

        if not variant_edges:
            continue

        variant = variant_edges[0].get("node", {})

        products.append(
            {
                "id": node.get("id"),
                "variant_id": variant.get("id"),
                "name": node.get("title", ""),
                "price": variant.get("price"),
                "description": node.get("description") or "",
            }
        )

    return products


def get_shopify_products() -> list[dict[str, Any]]:
    """
    Retrieve the first products from Shopify.
    """
    query = """
    query GetProducts {
      products(first: 10) {
        edges {
          node {
            id
            title
            description
            variants(first: 1) {
              edges {
                node {
                  id
                  price
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        data = shopify_graphql(query)
        return _extract_products(data)

    except Exception as exc:
        logger.exception(
            "get_shopify_products error: %s",
            exc,
        )
        return []


def search_shopify_products(
    query_text: str,
) -> list[dict[str, Any]]:
    """
    Search Shopify products using Shopify's product search query.
    """
    query = """
    query SearchProducts($query: String!) {
      products(first: 10, query: $query) {
        edges {
          node {
            id
            title
            description
            variants(first: 1) {
              edges {
                node {
                  id
                  price
                }
              }
            }
          }
        }
      }
    }
    """

    cleaned_query = query_text.strip()

    if not cleaned_query:
        return get_shopify_products()

    try:
        data = shopify_graphql(
            query,
            {
                "query": cleaned_query,
            },
        )

        return _extract_products(data)

    except Exception as exc:
        logger.exception(
            "search_shopify_products error: %s",
            exc,
        )
        return []


def create_shopify_draft_order(
    variant_id: str,
    quantity: int,
    customer_name: str,
    phone: str,
    address: str,
    email: str | None = None,
) -> dict[str, Any]:
    """
    Create a Shopify draft order and return its checkout URL.
    """
    mutation = """
    mutation CreateDraftOrder($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          name
          invoiceUrl
          status
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    if not variant_id:
        raise ValueError("variant_id is required.")

    try:
        parsed_quantity = int(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "quantity must be a valid integer."
        ) from exc

    if parsed_quantity < 1:
        raise ValueError(
            "quantity must be at least 1."
        )

    if not customer_name or not customer_name.strip():
        raise ValueError(
            "customer_name is required."
        )

    if not phone or not phone.strip():
        raise ValueError(
            "phone is required."
        )

    if not address or not address.strip():
        raise ValueError(
            "address is required."
        )

    name_parts = customer_name.strip().split(maxsplit=1)

    first_name = name_parts[0]
    last_name = (
        name_parts[1]
        if len(name_parts) > 1
        else ""
    )

    input_data: dict[str, Any] = {
        "lineItems": [
            {
                "variantId": variant_id,
                "quantity": parsed_quantity,
            }
        ],
        "phone": phone.strip(),
        "shippingAddress": {
            "address1": address.strip(),
            "phone": phone.strip(),
            "firstName": first_name,
            "lastName": last_name,
        },
    }

    if email and email.strip():
        input_data["email"] = email.strip().lower()

    result = shopify_graphql(
        mutation,
        {
            "input": input_data,
        },
    )

    draft_create = (
        result.get("data", {})
        .get("draftOrderCreate", {})
    )

    user_errors = draft_create.get(
        "userErrors",
        [],
    )

    if user_errors:
        error_messages = [
            error.get("message", "Unknown Shopify error")
            for error in user_errors
        ]

        raise RuntimeError(
            "Shopify draft order errors: "
            + "; ".join(error_messages)
        )

    draft_order = draft_create.get("draftOrder")

    if not draft_order:
        raise RuntimeError(
            f"No draftOrder returned by Shopify: {result}"
        )

    return {
        "draft_order_id": draft_order.get("id"),
        "draft_order_name": draft_order.get("name"),
        "invoice_url": draft_order.get("invoiceUrl"),
        "status": draft_order.get("status"),
    }


def get_shopify_draft_order_status(
    draft_order_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve the latest status of a Shopify draft order.
    """
    query = """
    query GetDraftOrderStatus($id: ID!) {
      draftOrder(id: $id) {
        id
        name
        status
        invoiceUrl
        completedAt
      }
    }
    """

    if not draft_order_id:
        return None

    try:
        result = shopify_graphql(
            query,
            {
                "id": draft_order_id,
            },
        )

        return (
            result.get("data", {})
            .get("draftOrder")
        )

    except Exception as exc:
        logger.exception(
            "get_shopify_draft_order_status error: %s",
            exc,
        )
        return None


if __name__ == "__main__":
    products = get_shopify_products()

    print(f"Found {len(products)} products:")

    for index, product in enumerate(
        products,
        start=1,
    ):
        print(
            f"  {index}. "
            f"{product['name']} — "
            f"{product['price']} — "
            f"variant: {product['variant_id']}"
        )