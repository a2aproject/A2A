# Streaming and Asynchronous Operations for Long-Running Tasks

The Agent2Agent (A2A) protocol handles long-running tasks with multiple steps,
incremental results, or human intervention. A2A enables asynchronous
interactions, allowing clients to receive updates regardless of connection state.

## Streaming with Server-Sent Events (SSE)

A2A uses Server-Sent Events (SSE) for real-time updates, including incremental
results and ongoing status, when clients maintain active HTTP connections.

**Key Characteristics:**

-   **Initiation:** Clients use `message/stream` to send a message and subscribe
    to updates.
-   **Server Capability:** Servers indicate streaming support with
    `capabilities.streaming: true`.
-   **Connection:** Successful subscription opens an HTTP 200 OK connection
    with `Content-Type: text/event-stream` for events.
-   **Event Structure:** The server sends events as JSON-RPC 2.0 Response
    objects (`SendStreamingMessageResponse`), with `id` matching the client's
    request.
-   **Event Types:** The `SendStreamingMessageResponse.result` can contain
    different types of events, depending on the context:
    -   [`Message`](../specification.md#6-message-object): If the client sends
        `message/stream` but does not want to create a Task.
    -   [`Task`](../specification.md#61-task-object): Current task state.
    -   [`TaskStatusUpdateEvent`](../specification.md#722-taskstatusupdateevent-object):
        Changes in task state, including intermediate messages.
    -   [`TaskArtifactUpdateEvent`](../specification.md#723-taskartifactupdateevent-object):
        New or updated artifacts, with `append` and `lastChunk` for
        reassembly.
-   **Stream Termination:** The server sets `final: true` in a
    `TaskStatusUpdateEvent` to end updates and closes the SSE connection.
-   **Resubscription:** Clients use `tasks/resubscribe` to reconnect if the
    connection breaks before `final: true`.

**When to Use Streaming:**

-   Real-time progress monitoring.
-   Incremental delivery of large results.
-   Interactive conversations with immediate feedback.
-   Low-latency updates.

Refer to the Protocol Specification for detailed structures:

-   [`message/stream`](../specification.md#72-messagestream)
-   [`tasks/resubscribe`](../specification.md#79-tasksresubscribe)

## Push Notifications for Disconnected Scenarios

A2A supports push notifications for long-running tasks, or when clients avoid
persistent connections. The A2A Server notifies a client's webhook on
significant task updates.

**Key Characteristics:**

-   **Server Capability:** Servers indicate support with
    `capabilities.pushNotifications: true`.
-   **Configuration:** Clients provide a
    [`PushNotificationConfig`](../specification.md#68-pushnotificationconfig-object).
    -   Included in `message/send` or `message/stream` requests, or set
        separately with `tasks/pushNotificationConfig/set`.
    -   Includes:
        -   `url`: The webhook URL for notifications.
        -   `token`: An optional client-generated token for validation.
        -   `authentication`: Optional authentication details for the server to
            use.
-   **Notification Trigger:** Sent on significant state changes (e.g., terminal,
    `input-required`, or `auth-required`).
-   **Notification Payload:** Contains the `Task ID` and the new `TaskState`.
-   **Client Action:** Clients use `tasks/get` with the `task ID` from the
    notification to retrieve the updated `Task` object.

**The Push Notification Service (Client-Side Webhook Infrastructure):**

-   `PushNotificationConfig.url` points to a client-side service that
    receives HTTP POST notifications.
-   Responsibilities include:
    -   Authenticating the notification from the A2A server.
    -   Validating the notification's relevance.
    -   Relaying the notification to the client system.
-   Can be a simple endpoint for development or a robust service for
    production.

### Security Considerations for Push Notifications

Security is critical due to the asynchronous and outbound nature of push
notifications. Both the A2A Server and the client's webhook receiver share
security responsibilities.

### A2A Server Security: Sending Notifications to Client Webhook

This covers security measures for the A2A Server when sending push notifications.

**Webhook URL Validation:**

-   Servers **MUST NOT** send POST requests to untrusted URLs. Malicious
    clients could provide URLs for SSRF attacks or DDoS amplification.
-   **Mitigation Strategies:**
    -   **Allowlisting:** Use trusted domains or IP ranges.
    -   **Ownership Verification:** The server **SHOULD** verify URLs. It
        could issue an HTTP GET/OPTIONS with a `validationToken`. The webhook
        must respond to prove ownership. The
        [A2A Python samples](https://github.com/a2aproject/a2a-samples)
        demonstrate a simple validation token check mechanism.
    -   **Network Controls:** Restrict outbound HTTP requests with firewalls.

**Authenticating to the Client's Webhook:**

-   The A2A Server **MUST** authenticate using schemes in
    `PushNotificationConfig.authentication`.
-   Common authentication schemes for server-to-server webhooks include:
    -   **Bearer Tokens (OAuth 2.0):** Use an access token in the
        `Authorization` header.
    -   **API Keys:** Include a pre-shared API key in a header (e.g.,
        `X-Api-Key`).
    -   **HMAC Signatures:** Sign the payload with a shared secret and include
        the signature in a header (e.g., `X-Hub-Signature`).
    -   **Mutual TLS (mTLS):** Present a client TLS certificate.

### Client Webhook Receiver Security: Receiving Notifications from A2A Server

This covers security measures for the client's webhook when receiving
notifications.

**Authenticating the A2A Server:**

-   The webhook **MUST** verify incoming notifications originate from the
    legitimate A2A Server.
-   **Verify Signatures/Tokens:**
    -   **JWTs:** Validate the JWT signature against the A2A Server's public
        keys (from JWKS). Validate claims like `iss`, `aud`, `iat`, and `exp`.
        `aud` should identify your webhook.
    -   **HMAC:** Recalculate the signature and compare it to the header.
    -   **API Keys:** Ensure the key is valid.
-   **Validate `PushNotificationConfig.token`:** Check for the client's token
    in a header (e.g., `X-A2A-Notification-Token`).

**Preventing Replay Attacks:**

-   **Timestamps:** Notifications **SHOULD** include a timestamp (e.g., `iat`
    in JWT). Reject old notifications. The timestamp should be part of the
    signed payload.
-   **Nonces/Unique IDs:** Use unique identifiers (nonces or event IDs). Track
    received IDs to prevent duplicates. A JWT's `jti` can serve this purpose.

**Secure Key Management and Rotation:**

-   **Cryptographic Keys:** Implement secure key management, including
    rotation.
-   **JWKS:** The A2A Server publishes public keys via JWKS. Client webhooks
    can fetch keys for verification, facilitating key rotation.

**Example Asymmetric Key Flow (JWT + JWKS):**

1.  The client sets `PushNotificationConfig` with `authentication.schemes:
    ["Bearer"]` and expected `issuer` or `audience`.
2.  A2A Server, when sending a notification:
    -   Generates a JWT, signed with its private key.
    -   Includes claims like `iss`, `aud`, `iat`, `exp`, `jti`, and `taskId`.
    -   The JWT header (`alg` and `kid`) indicates the signing algorithm and
        key identifier.
    -   Makes public keys available through JWKS.
2.  The client webhook, upon receiving the notification:
      endpoint (caching keys is recommended).
    -   Verifies the JWT signature using the public key.
    -   Validates claims (`iss`, `aud`, `iat`, `exp`, `jti`).
    -   Checks the `PushNotificationConfig.token` if provided.

By implementing these security measures, both the A2A Server and the client's
webhook receiver can ensure that push notifications are authentic, secure, and
reliable.

