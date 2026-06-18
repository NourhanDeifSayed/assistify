from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


PRIVACY_POLICY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assistify Privacy Policy</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.7;
            max-width: 850px;
            margin: 40px auto;
            padding: 0 20px;
            color: #222;
        }

        h1, h2 {
            color: #333;
        }

        .updated {
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Assistify Privacy Policy</h1>

    <p class="updated">Last updated: June 16, 2026</p>

    <p>
        Assistify provides automated customer-support responses through
        Instagram messaging. This policy explains how information is
        collected, used, stored, and deleted.
    </p>

    <h2>Information We Collect</h2>

    <p>
        When a user sends a message to the Assistify Instagram account,
        we may process the Instagram-scoped user ID, message content,
        message identifiers, timestamps, conversation history, and
        technical logs required to provide the service.
    </p>

    <h2>How We Use Information</h2>

    <p>
        We use this information to receive messages, generate automated
        replies, maintain conversation context, troubleshoot errors,
        prevent duplicate responses, and improve service reliability.
    </p>

    <h2>Sharing of Information</h2>

    <p>
        We do not sell personal information. Information may be processed
        through Meta and Instagram services and by technical service
        providers required to operate and secure the application.
    </p>

    <h2>Data Retention</h2>

    <p>
        Information is retained only for as long as reasonably necessary
        to provide the service, maintain security, resolve technical
        issues, or meet applicable legal obligations.
    </p>

    <h2>Data Security</h2>

    <p>
        Reasonable technical and organizational measures are used to
        protect stored information. However, no method of electronic
        storage or transmission is completely secure.
    </p>

    <h2>Data Deletion</h2>

    <p>
        Users may request deletion of their Assistify conversation data
        by sending the message "Delete my data" to the Instagram account
        @asisstify_zewail. After account ownership is verified, the
        associated data will be deleted within a reasonable period.
    </p>

    <h2>Changes to This Policy</h2>

    <p>
        This privacy policy may be updated when the service or its data
        practices change. The updated date will be displayed at the top
        of this page.
    </p>

    <h2>Contact</h2>

    <p>
        For privacy questions, contact Assistify through the Instagram
        account @asisstify_zewail.
    </p>
</body>
</html>
"""


def privacy_policy(request):
    return HttpResponse(
        PRIVACY_POLICY_HTML,
        content_type="text/html; charset=utf-8",
    )


urlpatterns = [
    path(
        "privacy-policy/",
        privacy_policy,
        name="privacy-policy",
    ),
    path("admin/", admin.site.urls),
    path(
        "api/v1/auth/",
        include("assistify.apps.users.urls"),
    ),
    path(
        "api/v1/products/",
        include("assistify.apps.products.urls"),
    ),
    path(
        "api/v1/orders/",
        include("assistify.apps.orders.urls"),
    ),
    path(
        "api/v1/chat/",
        include("assistify.apps.chat.urls"),
    ),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
