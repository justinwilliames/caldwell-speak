import Foundation

// macOS voice fields are GONE from this model. Kokoro is the only engine, so
// `native_voice`, `enhanced_installed` and a 68-entry `available_voices` catalogue
// described a path the app can no longer take — and the UI was still rendering a
// nudge from them, pointing users at System Settings to install a voice nothing
// would ever use.
struct DaemonSettings: Codable, Sendable {
    let muted: Bool?
    /// Whether Potty Mouth mode is on (true) or Polite (false, default).
    let expletivesEnabled: Bool?
    /// Whether the neural Enhanced Daniel is installed (drives the install nudge).
    /// Whether cached "canon" pings are on (notification-style) vs bespoke-only.
    let canonEnabled: Bool?
    /// Whether the animated floating Pulsar head is shown on screen while it
    /// speaks. Default true.
    let floatingHeadEnabled: Bool?
    /// Whether the read-along caption bubble shows below the head. Default true.
    let subtitlesEnabled: Bool?
    /// Whether the orbiting/clustered sub-agent "drones" (the active-agent swarm)
    /// are shown. Default true; when false only Pulsar himself appears. Pulsar's
    /// own voice + head are unaffected.
    let showActiveAgents: Bool?
    /// Installed local voices usable in free mode (drives the voice picker),
    /// each with a "Name (Language, Region)" label.
    /// The synthesiser actually in use — "native" or "kokoro". Already degraded by
    /// the daemon, so this is what will speak, not merely what was selected.
    let voiceEngine: String?
    /// Whether this Mac can run Kokoro at all (Apple Silicon).
    let kokoroSupported: Bool?
    /// Whether the Kokoro model is downloaded and complete.
    let kokoroInstalled: Bool?

    enum CodingKeys: String, CodingKey {
        case muted
        case expletivesEnabled = "expletives_enabled"
        case canonEnabled = "canon_enabled"
        case floatingHeadEnabled = "floating_head_enabled"
        case subtitlesEnabled = "subtitles_enabled"
        case showActiveAgents = "show_active_agents"
        case voiceEngine = "voice_engine"
        case kokoroSupported = "kokoro_supported"
        case kokoroInstalled = "kokoro_installed"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.muted = try container.decodeIfPresent(Bool.self, forKey: .muted)
        self.expletivesEnabled = try container.decodeIfPresent(Bool.self, forKey: .expletivesEnabled)
        self.canonEnabled = try container.decodeIfPresent(Bool.self, forKey: .canonEnabled)
        self.floatingHeadEnabled = try container.decodeIfPresent(Bool.self, forKey: .floatingHeadEnabled)
        self.subtitlesEnabled = try container.decodeIfPresent(Bool.self, forKey: .subtitlesEnabled)
        self.showActiveAgents = try container.decodeIfPresent(Bool.self, forKey: .showActiveAgents)
        self.voiceEngine = try container.decodeIfPresent(String.self, forKey: .voiceEngine)
        self.kokoroSupported = try container.decodeIfPresent(Bool.self, forKey: .kokoroSupported)
        self.kokoroInstalled = try container.decodeIfPresent(Bool.self, forKey: .kokoroInstalled)
    }
}

struct SettingsSaveResponse: Codable, Sendable {
    let saved: Bool?
    let muted: Bool?
    let error: String?
    let field: String?

    enum CodingKeys: String, CodingKey {
        case saved
        case muted
        case error
        case field
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.muted = try container.decodeIfPresent(Bool.self, forKey: .muted)
        self.error = try container.decodeIfPresent(String.self, forKey: .error)
        self.field = try container.decodeIfPresent(String.self, forKey: .field)

        let hasSettingsPayload = muted != nil
        self.saved = try container.decodeIfPresent(Bool.self, forKey: .saved)
            ?? (error == nil && hasSettingsPayload ? true : nil)
    }
}
