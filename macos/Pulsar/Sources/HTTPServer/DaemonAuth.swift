import Foundation
import Hummingbird

/// Local-daemon auth, request provenance, and the append-only speech record for
/// the in-app HTTP server.
///
/// THREAT MODEL (Sentinel R3 runtime observations, 2026-07-30 — both CONFIRMED
/// live against a running app before this file existed):
///   • obs #3 — `curl http://127.0.0.1:7865/history` with no credential returned
///     200 and the full spoken-text history. Every line Pulsar has said this
///     session, readable by ANY process on the Mac.
///   • obs #4 — `curl -X POST -H 'Host: evil.example.com' .../speak` returned
///     200 and spoke. Binding to 127.0.0.1 is not an authorisation boundary: a
///     browser page whose DNS name rebinds to loopback reaches this server, and
///     the old code never looked at where the request claimed to come from.
///
/// Two cheap, independent gates close both:
///   1. **Shared secret** — a random token minted once at startup into
///      `~/.pulsar/daemon-token` (0600 inside a 0700 dir) and required in the
///      `X-Pulsar-Token` header on every route. Only processes running as this
///      user can read the file; a browser page cannot read files at all, so the
///      rebinding/CSRF write path dies here even if gate 2 were bypassed.
///   2. **Host allowlist** — a request whose `Host` is not a loopback literal on
///      our port is rejected with 400 before any handler runs, so the rebinding
///      case fails at the front door with a clear, greppable reason.
///
/// `GET /health` is deliberately EXEMPT. It is the "is the app running?" probe
/// every hook and script fires before doing anything else (say.sh's
/// `daemon_up`, the Stop hook, session-start-voice), it returns no user content,
/// and gating it would mean a token-less client couldn't even discover that it
/// needs a token.
///
/// FAIL-OPEN ON A BROKEN HOME DIR, BY DESIGN: if the token can neither be read
/// nor written (unwritable `$HOME`, weird sandbox), `token` stays nil, the gate
/// logs loudly and lets requests through. The alternative — fail closed — would
/// brick voice entirely for a filesystem problem that has nothing to do with
/// security. The Host gate still applies in that state.
enum DaemonAuth {

    /// Header clients present the shared secret in.
    static let headerName = "X-Pulsar-Token"

    // MARK: - Paths

    /// `~/.pulsar` — deliberately NOT `PulsarConfig.storageRoot`.
    ///
    /// Every client is a POSIX shell script (say.sh, the hooks). They need a
    /// path that is short, home-relative, and free of spaces so it can be
    /// hard-coded without quoting hazards. `~/Library/Application Support/Pulsar`
    /// has a space in it and differs under the `PULSAR_STORAGE` dev override —
    /// both bad properties for a credential path baked into a dozen scripts.
    static var directory: URL {
        URL(fileURLWithPath: NSHomeDirectory())
            .appendingPathComponent(".pulsar", isDirectory: true)
    }

    static var tokenFile: URL {
        directory.appendingPathComponent("daemon-token")
    }

    /// Append-only record of every line the daemon accepted for speech.
    ///
    /// Distinct from `/history`, which is an in-memory ring capped at 200 items
    /// and wiped on every launch (Voyager R2 finding). This file is the durable
    /// one: it survives relaunch, is never truncated by the app, and carries the
    /// category-coercion provenance `/history` throws away.
    static var speechLogFile: URL {
        directory.appendingPathComponent("speech.jsonl")
    }

    // MARK: - Token

    private static let lock = NSLock()
    private static var cachedToken: String?

    /// The active shared secret, or nil when we could not establish one.
    ///
    /// Establishes it on first read rather than trusting call order. The in-app
    /// clients (DaemonAPI, SSEClient, PortraitManager) can fire before
    /// `PulsarHTTPServer.configure()` has run, and a nil token there means a
    /// header-less request that 401s the moment the gate goes live — for
    /// PortraitManager that would cache a placeholder face for the whole
    /// session. `ensureToken()` is idempotent, so reading is always safe.
    static var token: String? {
        ensureToken()
    }

    /// Load the existing token, or mint one. Idempotent; call once from
    /// `PulsarHTTPServer.configure()` BEFORE the listener is armed, so no
    /// request can ever be evaluated against a half-initialised gate.
    ///
    /// Never throws — a failure is logged and leaves the gate open (see the
    /// fail-open note on this type).
    @discardableResult
    static func ensureToken() -> String? {
        lock.lock()
        defer { lock.unlock() }
        if let cachedToken { return cachedToken }

        let fm = FileManager.default

        // Existing token wins — a restart must not invalidate the token every
        // already-installed hook script has cached on disk.
        if let data = try? Data(contentsOf: tokenFile),
           let existing = String(data: data, encoding: .utf8)?
               .trimmingCharacters(in: .whitespacesAndNewlines),
           !existing.isEmpty {
            cachedToken = existing
            return existing
        }

        // Mint a new one. 32 bytes of `SystemRandomNumberGenerator` (arc4random
        // on Darwin), hex-encoded — 256 bits, unguessable, and printable so a
        // shell script can `cat` it with no decoding.
        let fresh = (0..<32).map { _ in String(format: "%02x", UInt8.random(in: 0...255)) }.joined()

        do {
            // 0700 on the dir, 0600 on the file, and the file is CREATED with
            // that mode (not chmod'd after) so there is no window where another
            // local user could read it.
            try fm.createDirectory(
                at: directory,
                withIntermediateDirectories: true,
                attributes: [.posixPermissions: 0o700]
            )
            if fm.fileExists(atPath: tokenFile.path) {
                try? fm.removeItem(at: tokenFile)
            }
            guard fm.createFile(
                atPath: tokenFile.path,
                contents: Data(fresh.utf8),
                attributes: [.posixPermissions: 0o600]
            ) else {
                NSLog("[DaemonAuth] could not write \(tokenFile.path) — auth gate OPEN")
                return nil
            }
        } catch {
            NSLog("[DaemonAuth] token setup failed (\(error)) — auth gate OPEN")
            return nil
        }

        cachedToken = fresh
        NSLog("[DaemonAuth] minted daemon token at \(tokenFile.path)")
        return fresh
    }

    /// True when a token is established and the request presents it.
    /// Constant-time-ish comparison is not worth it here: the secret is a local
    /// file the attacker either can read (game over regardless) or cannot.
    static func isAuthorized(_ request: Request) -> Bool {
        guard let expected = token else { return true }  // fail-open, logged at setup
        return rawHeader(headerName, in: request) == expected
    }

    /// Read a header by its wire name, case-insensitively. Used instead of a
    /// typed `HTTPField.Name` because `X-Pulsar-Token` is ours (not a registered
    /// field), and because HTTPTypes marks `.host` unavailable in favour of
    /// `authority` — so a raw lookup is the only way to see a literal `Host:`.
    static func rawHeader(_ name: String, in request: Request) -> String? {
        let wanted = name.lowercased()
        for field in request.headers where field.name.rawName.lowercased() == wanted {
            return field.value
        }
        return nil
    }

    // MARK: - Host allowlist

    /// Loopback names we accept, with and without the port. The bare forms exist
    /// because a client may legitimately omit a port it considers default; they
    /// are still loopback NAMES, so they carry none of the rebinding risk that
    /// `evil.example.com` does.
    static func isAllowedHost(_ host: String, port: Int) -> Bool {
        let normalized = host.trimmingCharacters(in: .whitespaces).lowercased()
        let allowed: Set<String> = [
            "127.0.0.1:\(port)", "localhost:\(port)", "[::1]:\(port)",
            "127.0.0.1", "localhost", "[::1]",
        ]
        return allowed.contains(normalized)
    }

    // MARK: - Speech record

    private static let speechLogLock = NSLock()

    /// Append one JSON line for an accepted `/speak`.
    ///
    /// Recorded AFTER the line is enqueued, so the file means "this was spoken",
    /// matching `/history` semantics — muted calls, over-length rejects, and
    /// queue-full drops are deliberately absent.
    ///
    /// `rawCategory` is exactly what the caller sent (nil when untagged);
    /// `resolvedCategory` is what the voice pipeline actually used after the
    /// registry lookup, and `coerced` flags the two diverging. That divergence is
    /// invisible in `/history` today, which is why a drone tagged with a typo
    /// silently speaks as Pulsar with no trace.
    ///
    /// Best-effort and never throwing: an audit write must not be able to break
    /// speech.
    static func appendSpeechRecord(
        text: String,
        rawCategory: String?,
        resolvedCategory: String,
        coerced: Bool,
        voice: String
    ) {
        // `raw_category` is JSON null when the caller sent no `agent` at all —
        // distinguishable from the string "pulsar", which means they asked for
        // Pulsar explicitly.
        let record: [String: Any] = [
            "ts": ISO8601DateFormatter().string(from: Date()),
            "text": text,
            "raw_category": rawCategory ?? NSNull(),
            "resolved_category": resolvedCategory,
            "coerced": coerced,
            "voice": voice,
        ]

        guard let data = try? JSONSerialization.data(
            withJSONObject: record,
            options: [.sortedKeys]
        ) else { return }

        var line = data
        line.append(0x0A)  // newline — one record per line, append-only

        speechLogLock.lock()
        defer { speechLogLock.unlock() }

        let fm = FileManager.default
        if !fm.fileExists(atPath: speechLogFile.path) {
            try? fm.createDirectory(
                at: directory,
                withIntermediateDirectories: true,
                attributes: [.posixPermissions: 0o700]
            )
            // Spoken text is user content — same 0600 as the token.
            _ = fm.createFile(
                atPath: speechLogFile.path,
                contents: line,
                attributes: [.posixPermissions: 0o600]
            )
            return
        }

        guard let handle = FileHandle(forWritingAtPath: speechLogFile.path) else { return }
        defer { try? handle.close() }
        do {
            try handle.seekToEnd()
            try handle.write(contentsOf: line)
        } catch {
            NSLog("[DaemonAuth] speech.jsonl append failed: \(error)")
        }
    }
}

// MARK: - Middleware

/// Front-door gate: Host allowlist for every request, shared-secret token for
/// every request except `GET /health`.
///
/// Registered as router middleware rather than a per-handler check so it also
/// covers routes added later (and 404s) — a new endpoint is protected by
/// default instead of by remembering to add a line.
struct DaemonAuthMiddleware: RouterMiddleware {
    typealias Context = BasicRequestContext

    /// The port we are actually listening on, so the allowlist matches a dev
    /// override (`SPEAK_PORT`) instead of hard-coding 7865.
    let port: Int

    func handle(
        _ request: Request,
        context: Context,
        next: (Request, Context) async throws -> Response
    ) async throws -> Response {
        // 1. Host allowlist. HTTP/1 `Host:` surfaces as `head.authority` after
        //    NIO's HTTPTypes conversion; check the header field too in case a
        //    future transport (HTTP/2 `:authority`) routes it differently. An
        //    ABSENT Host is allowed through — HTTP/1.0 clients omit it, and it
        //    carries no forged claim.
        let claimedHost = request.head.authority ?? DaemonAuth.rawHeader("Host", in: request)
        if let claimedHost, !DaemonAuth.isAllowedHost(claimedHost, port: port) {
            NSLog("[DaemonAuth] rejected non-loopback Host '\(claimedHost)' for \(request.uri.path)")
            return Self.error("Host not allowed", status: .badRequest)
        }

        // 2. /health is the liveness probe every client fires first — open.
        if request.uri.path == "/health" {
            return try await next(request, context)
        }

        // 3. Shared secret on everything else.
        guard DaemonAuth.isAuthorized(request) else {
            NSLog("[DaemonAuth] 401 on \(request.method) \(request.uri.path) — missing/bad \(DaemonAuth.headerName)")
            return Self.error(
                "Missing or invalid \(DaemonAuth.headerName) header",
                status: .unauthorized
            )
        }

        return try await next(request, context)
    }

    private static func error(_ message: String, status: HTTPResponse.Status) -> Response {
        let body = #"{"error":"\#(message)"}"#
        return Response(
            status: status,
            headers: [.contentType: "application/json"],
            body: ResponseBody(byteBuffer: ByteBuffer(string: body))
        )
    }
}
