import AppKit
import Foundation

/// Opening the Claude Code session a line was spoken from.
///
/// The route is the Claude desktop app's own deep link, `claude://resume?session=<id>`.
/// Verified against the shipping app (2026-08-13): the handler resolves the id to
/// its session, and — when that session already exists — focuses it rather than
/// importing a second copy:
///
///     Resume deep link: importing CLI session b88bfc27-…
///     CLI session b88bfc27-… already imported as local_b88bfc27-…
///     [CCD] LocalSessions.setFocusedSession: sessionId=local_b88bfc27-…
///
/// Which id say.sh sends therefore matters. For a session hosted by the desktop
/// app it sends the HOST session id (minus its `local_` prefix), which is the one
/// that already exists — so the click lands on the running session. For a plain
/// CLI session it sends the CLI session id, and the desktop app imports its
/// transcript on demand. Both are the same URL shape from here.
enum SessionLink {

    /// The deep link for `ref`, or nil when the ref is missing or not a bare id.
    /// The character check is a second gate behind the daemon's own — this string
    /// arrives over HTTP and ends up in a URL the app hands to LaunchServices.
    static func url(for ref: String?) -> URL? {
        guard let ref, !ref.isEmpty, ref.count <= 64,
              ref.allSatisfy({ $0.isASCII && ($0.isLetter || $0.isNumber || $0 == "-" || $0 == "_") })
        else { return nil }
        return URL(string: "claude://resume?session=\(ref)")
    }

    /// True when `ref` can actually be opened — drives whether the UI offers a
    /// click at all, so there is never a dead affordance.
    static func canOpen(_ ref: String?) -> Bool { url(for: ref) != nil }

    /// Open the session. No-op (logged) when the ref isn't openable.
    static func open(_ ref: String?) {
        guard let url = url(for: ref) else {
            NSLog("[Pulsar] session link: no openable ref (\(ref ?? "nil"))")
            return
        }
        NSLog("[Pulsar] session link: opening \(url.absoluteString)")
        NSWorkspace.shared.open(url)
    }
}
