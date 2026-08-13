import Foundation

/// Which synthesiser produces a line's audio. The façade both `/speak` and the
/// canon picker call, so neither knows or cares which engine is live.
///
/// `native` (macOS `say`) is the default and the permanent floor: it needs no
/// download, ships on every Mac, and carries the full 9-drone cast. `kokoro` is
/// opt-in, and only reachable once the user has downloaded the model.
///
/// The contract that makes this safe to ship: **Kokoro can never make Pulsar
/// mute.** Any failure — missing weights, a corrupt voice, an MLX error, a model
/// that won't load — falls through to `say` for that line and logs why. A voice
/// assistant that goes silent because an optional engine broke is worse than one
/// that sounds slightly less good.
enum VoiceEngine: String, CaseIterable, Sendable {
    case native
    case kokoro

    /// Human label for Settings.
    var label: String {
        switch self {
        case .native: return "macOS (built-in)"
        case .kokoro: return "Kokoro (on-device neural)"
        }
    }

    /// The engine the user has chosen, coerced to something that actually works.
    ///
    /// Selecting `kokoro` without the model on disk resolves to `native` rather
    /// than erroring — that state is reachable normally (the user enabled Kokoro,
    /// then deleted the folder, or an update moved Application Support) and the
    /// right response is to keep talking.
    static var active: VoiceEngine {
        let chosen = VoiceEngine(rawValue: PulsarConfig.shared.voiceEngineRaw) ?? .native
        guard chosen == .kokoro, KokoroVoiceClient.isInstalled() else { return .native }
        return .kokoro
    }

    /// What the user selected, ignoring whether it can currently run. The Settings
    /// toggle reflects this; everything on the speak path uses `active`.
    static var selected: VoiceEngine {
        VoiceEngine(rawValue: PulsarConfig.shared.voiceEngineRaw) ?? .native
    }

    /// Synthesise a line to a temp audio file. Mirrors `NativeVoiceClient.synth`'s
    /// signature exactly — callers are engine-agnostic.
    ///
    /// Returns AIFF on the native path and WAV on the Kokoro path. Everything
    /// downstream (`extractEnvelope`, `afplay`, the history store) is
    /// container-agnostic, which is what makes the swap this cheap.
    static func synth(text: String, agent: String? = nil) async throws -> URL {
        guard active == .kokoro else {
            return try await NativeVoiceClient.synth(text: text, agent: agent)
        }
        do {
            return try await KokoroVoiceClient.synth(text: text, agent: agent)
        } catch {
            NSLog("[VoiceEngine] Kokoro synth failed (\(error.localizedDescription)) — falling back to say")
            return try await NativeVoiceClient.synth(text: text, agent: agent)
        }
    }

    /// The voice name recorded against a line in the durable speech log, so that
    /// log says what actually spoke rather than always naming a macOS voice.
    ///
    /// Note `DroneRegistry.category(forVoice:)` reverse-maps a macOS voice name back
    /// to a drone and would NOT resolve a Kokoro id — it currently has no callers,
    /// so nothing breaks, but wire a category through rather than a voice name if
    /// you ever revive it.
    static func voice(forAgent category: String?) -> String {
        active == .kokoro
            ? KokoroVoiceClient.voice(forAgent: category)
            : NativeVoiceClient.voice(forAgent: category)
    }
}
