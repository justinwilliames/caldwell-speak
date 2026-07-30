import Foundation

struct DaemonAPI: Sendable {
    let baseURL: URL

    init(port: Int = Self.defaultPort) {
        baseURL = URL(string: "http://127.0.0.1:\(port)")!
    }

    static var defaultPort: Int {
        if let env = ProcessInfo.processInfo.environment["SPEAK_PORT"], let p = Int(env) { return p }
        return 7865
    }

    /// Build a request carrying the daemon's shared secret. Every route except
    /// GET /health requires it (see DaemonAuth), and that includes the app's own
    /// UI — the server cannot tell "our popover" from "some other local process"
    /// by any other means. Token absent (first launch, before the server has
    /// minted one) → no header, and the gate is open in that same window.
    static func authorized(_ url: URL) -> URLRequest {
        var request = URLRequest(url: url)
        if let token = DaemonAuth.token {
            request.setValue(token, forHTTPHeaderField: DaemonAuth.headerName)
        }
        return request
    }

    /// GET + decode, with the auth header attached.
    private func get<T: Decodable>(_ type: T.Type, url: URL) async throws -> T {
        let (data, _) = try await URLSession.shared.data(for: Self.authorized(url))
        return try JSONDecoder().decode(T.self, from: data)
    }

    // MARK: - Queue Control

    func pause(channel: String? = nil) async throws {
        try await post("queue/pause", body: channelBody(channel))
    }

    func resume(channel: String? = nil) async throws {
        try await post("queue/resume", body: channelBody(channel))
    }

    func skip() async throws {
        try await post("queue/skip")
    }

    func seek(offset: Double) async throws {
        try await post("queue/seek", body: ["offset": offset])
    }

    func clearQueue(channel: String? = nil) async throws {
        try await post("queue/clear", body: channelBody(channel))
    }

    // MARK: - History

    func replay(id: String) async throws {
        try await post("history/replay", body: ["id": id])
    }

    func fetchHistory(limit: Int = 50, offset: Int = 0, channel: String? = nil) async throws -> HistoryResponse {
        var components = URLComponents(url: baseURL.appendingPathComponent("history"), resolvingAgainstBaseURL: false)!
        var queryItems = [
            URLQueryItem(name: "limit", value: "\(limit)"),
            URLQueryItem(name: "offset", value: "\(offset)"),
        ]
        if let channel { queryItems.append(URLQueryItem(name: "channel", value: channel)) }
        components.queryItems = queryItems
        return try await get(HistoryResponse.self, url: components.url!)
    }

    // MARK: - Phrase Cache

    enum CacheSort: String {
        case recent
        case popular
    }

    func fetchCachedPhrases(sort: CacheSort = .recent, limit: Int = 200) async throws -> CachedPhrasesResponse {
        var components = URLComponents(url: baseURL.appendingPathComponent("cache/phrases"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "sort", value: sort.rawValue),
            URLQueryItem(name: "limit", value: "\(limit)"),
        ]
        return try await get(CachedPhrasesResponse.self, url: components.url!)
    }

    func playCachedPhrase(key: String) async throws {
        try await post("cache/play", body: ["key": key])
    }

    // MARK: - Voices

    func fetchVoices() async throws -> [Voice] {
        try await get([Voice].self, url: baseURL.appendingPathComponent("voices"))
    }

    // MARK: - Settings & Usage

    func fetchSettings() async throws -> DaemonSettings {
        try await get(DaemonSettings.self, url: baseURL.appendingPathComponent("settings"))
    }

    func saveSettings(muted: Bool? = nil, expletivesEnabled: Bool? = nil, canonEnabled: Bool? = nil, floatingHeadEnabled: Bool? = nil, subtitlesEnabled: Bool? = nil, showActiveAgents: Bool? = nil, nativeVoice: String? = nil) async throws -> SettingsSaveResponse {
        var body: [String: Any] = [:]
        if let muted { body["muted"] = muted }
        if let expletivesEnabled { body["expletives_enabled"] = expletivesEnabled }
        if let canonEnabled { body["canon_enabled"] = canonEnabled }
        if let floatingHeadEnabled { body["floating_head_enabled"] = floatingHeadEnabled }
        if let subtitlesEnabled { body["subtitles_enabled"] = subtitlesEnabled }
        if let showActiveAgents { body["show_active_agents"] = showActiveAgents }
        if let nativeVoice { body["native_voice"] = nativeVoice }

        var request = Self.authorized(baseURL.appendingPathComponent("settings"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(SettingsSaveResponse.self, from: data)
    }

    // MARK: - Queue Status

    func fetchQueueStatus(channel: String? = nil) async throws -> QueueStatusResponse {
        var components = URLComponents(url: baseURL.appendingPathComponent("queue"), resolvingAgainstBaseURL: false)!
        if let channel {
            components.queryItems = [URLQueryItem(name: "channel", value: channel)]
        }
        return try await get(QueueStatusResponse.self, url: components.url!)
    }

    // MARK: - Private

    @discardableResult
    private func post(_ path: String, body: [String: Any]? = nil) async throws -> Data {
        var request = Self.authorized(baseURL.appendingPathComponent(path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let body {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } else {
            request.httpBody = Data("{}".utf8)
        }
        let (data, _) = try await URLSession.shared.data(for: request)
        return data
    }

    private func channelBody(_ channel: String?) -> [String: Any]? {
        channel.map { ["channel": $0] }
    }
}
