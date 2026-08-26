import Foundation

/// Which synthesiser produces a line's audio. The façade both `/speak` and the
/// canon picker call.
///
/// **Kokoro is the only engine.** Justin, 2026-08-14: "remove MacOS voices — make
/// Kokoro compulsory." The macOS `say` path is gone: no `native` case, no silent
/// fallback, no per-line downgrade.
///
/// That deletes the old safety contract ("Kokoro can never make Pulsar mute"), and
/// the trade is deliberate. A fallback that swaps in a completely different voice
/// mid-cast is not a graceful degradation — it is the cast silently becoming
/// somebody else, which is exactly the bug that surfaced this change: an app built
/// from a branch without Kokoro spoke ten drones in macOS voices and looked like it
/// was working. A line that cannot be spoken in the character's own voice now fails
/// loudly and is recorded as failed, which is the honest outcome.
///
/// The model is a hard requirement. If the weights are absent the app must say so
/// and offer the download — not quietly speak in a voice nobody cast.
enum VoiceEngine: String, CaseIterable, Sendable {
    case kokoro

    /// Human label for Settings.
    var label: String {
        switch self {
        case .kokoro: return "Kokoro (on-device neural)"
        }
    }

    /// There is one engine. Kept as a property so call sites read unchanged.
    static var active: VoiceEngine { .kokoro }

    /// Ditto — there is nothing to select between.
    static var selected: VoiceEngine { .kokoro }

    /// Is the engine actually able to speak right now? False means the weights are
    /// missing and the user needs to download them; the app must surface that
    /// rather than substituting a voice nobody cast.
    static var isReady: Bool { KokoroVoiceClient.isInstalled() }

    /// Synthesise a line to a temp audio file.
    ///
    /// Returns WAV. Everything
    /// downstream (`extractEnvelope`, `afplay`, the history store) is
    /// container-agnostic, which is what makes the swap this cheap.
    static func synth(text: String, agent: String? = nil) async throws -> URL {
        // No fallback. A failure here propagates, the queue records the line as
        // failed, and the log says why — rather than the character being replaced
        // by a macOS voice that sounds nothing like them.
        do {
            return try await KokoroVoiceClient.synth(text: text, agent: agent)
        } catch {
            NSLog("[VoiceEngine] Kokoro synth failed: \(error.localizedDescription) — "
                  + "NOT falling back; Kokoro is the only engine.")
            throw error
        }
    }

    /// The Kokoro voice id recorded against a line in the durable speech log, so
    /// the log says what actually spoke.
    static func voice(forAgent category: String?) -> String {
        KokoroVoiceClient.voice(forAgent: category)
    }
}
