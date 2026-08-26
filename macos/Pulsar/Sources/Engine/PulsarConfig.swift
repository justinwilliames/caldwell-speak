import Foundation

/// Singleton config store. Reads from:
///   1. REPO_ROOT/config.json — muted state, expletives toggle, native voice.
///   2. Environment variables — overrides for the native-voice choice + canon.
///
/// Thread-safe: all mutations go through an NSLock. Call `reload()` after
/// writing config.json to pick up new values without restarting the app.
final class PulsarConfig: @unchecked Sendable {
    static let shared = PulsarConfig()

    private let lock = NSLock()
    private var _config: [String: String] = [:]

    // MARK: - Init

    private init() {
        reload()
    }

    // MARK: - Paths

    /// Repo root: honour PULSAR_REPO_ROOT env var first, then default to
    /// ~/code/pulsar. This locates BUNDLED CODE ASSETS (e.g. the drone
    /// portrait frames under assets/portraits) — NOT mutable app state. Mutable
    /// state (config.json, cache/) lives under `storageRoot` in Application
    /// Support so the app works for DMG users with no checkout. Keep this here
    /// only for read-only asset lookups relative to the source tree.
    var repoRoot: URL {
        if let env = ProcessInfo.processInfo.environment["PULSAR_REPO_ROOT"],
           !env.isEmpty {
            return URL(fileURLWithPath: env)
        }
        return URL(fileURLWithPath: NSHomeDirectory())
            .appendingPathComponent("code/pulsar")
    }

    /// Mutable app-state root. Defaults to a per-user Application Support dir
    /// (`~/Library/Application Support/Pulsar/`) so state lives OUTSIDE the code
    /// checkout — the app runs identically for DMG users with no source tree.
    /// Dev override: set `PULSAR_STORAGE` to point storage at a checkout's
    /// `cache/`+`config.json` instead.
    ///
    /// Directory is created on first access (best-effort).
    var storageRoot: URL {
        // Dev override wins.
        if let env = ProcessInfo.processInfo.environment["PULSAR_STORAGE"],
           !env.isEmpty {
            let url = URL(fileURLWithPath: env)
            try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
            return url
        }

        let appSupport = FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)
            .first!
            .appendingPathComponent("Pulsar", isDirectory: true)
        try? FileManager.default.createDirectory(at: appSupport, withIntermediateDirectories: true)
        return appSupport
    }

    var configPath: URL {
        storageRoot.appendingPathComponent("config.json")
    }

    var cacheDir: URL {
        storageRoot.appendingPathComponent("cache")
    }

    var phraseCacheDir: URL {
        cacheDir.appendingPathComponent("phrases")
    }

    /// Per-history-item audio retention store. Distinct from the phrase
    /// (dedupe) cache: EVERY played line is copied here keyed by its history
    /// id so `/history/replay` works for every entry, not just cache-eligible
    /// canon. Lifecycle-coupled to the in-memory history list (wiped at launch,
    /// evicted when an item drops off history) — see AudioQueueActor.
    var historyAudioDir: URL {
        cacheDir.appendingPathComponent("history")
    }

    // MARK: - Config values

    var isMuted: Bool {
        let val = lock.withLock { _config["PULSAR_MUTED"] } ?? "0"
        return ["1", "true", "yes", "on"].contains(val.lowercased())
    }

    /// Whether Potty Mouth mode is on. Default OFF (Polite). When ON, canon
    /// picks from the potty pool and bespoke /speak lines are delivered as-is
    /// (no scrubbing). When OFF, bespoke lines are scrubbed clean before being
    /// cached or spoken, making Polite authoritative regardless of caller text.
    var expletivesEnabled: Bool {
        let val = lock.withLock { _config["PULSAR_EXPLETIVES"] } ?? "0"
        return ["1", "true", "yes", "on"].contains(val.lowercased())
    }

    /// The user's chosen local (free-mode) voice. Empty = auto (Daniel Enhanced
    /// when installed, else basic Daniel). Set via the Settings voice picker.
    var nativeVoiceChoice: String {
        (lock.withLock { _config["PULSAR_NATIVE_VOICE"] }
            ?? ProcessInfo.processInfo.environment["PULSAR_NATIVE_VOICE"]
            ?? "").trimmingCharacters(in: .whitespaces)
    }

    /// Config key for the synthesiser choice. Named here so KokoroModelManager can
    /// reset it without duplicating the string.
    static let voiceEngineKey = "PULSAR_VOICE_ENGINE"
    static let panelOriginKey = "PULSAR_PANEL_ORIGIN"

    /// Which synthesiser the user picked, as a raw string ("native" / "kokoro").
    /// Empty when unset, which callers must read as "native" — a fresh install has
    /// to speak with no download, so Kokoro is never the default.
    ///
    /// Deliberately a String rather than the `VoiceEngine` enum: `scripts/run-tests.sh`
    /// compiles this file standalone with `swiftc` (no SwiftPM, no Kokoro module),
    /// so a type dependency here would drag the whole MLX graph into the test
    /// harness and break it. `VoiceEngine.active` does the parsing, and also checks
    /// the model is actually on disk before honouring "kokoro".
    /// Where the user last put the floating panel, as "x,y" in screen coordinates.
    ///
    /// The anchor used to live only in memory, so every relaunch threw the panel
    /// back to the top-left corner — which the user noticed precisely because a
    /// run of rebuilds kept moving it. A window position is a preference; it
    /// belongs on disk.
    var panelOrigin: CGPoint? {
        let raw = lock.withLock { _config[Self.panelOriginKey] } ?? ""
        let parts = raw.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
        guard parts.count == 2 else { return nil }
        return CGPoint(x: parts[0], y: parts[1])
    }

    func setPanelOrigin(_ p: CGPoint) {
        try? set(Self.panelOriginKey, value: "\(Int(p.x)),\(Int(p.y))")
    }

    var voiceEngineRaw: String {
        (lock.withLock { _config[Self.voiceEngineKey] }
            ?? ProcessInfo.processInfo.environment[Self.voiceEngineKey]
            ?? "").trimmingCharacters(in: .whitespaces).lowercased()
    }

    /// Sentence gap for the Kokoro path, in milliseconds. Kokoro renders a line as
    /// one continuous utterance, so a full stop barely registers; KokoroVoiceClient
    /// splits on sentence boundaries and inserts this much silence between them.
    /// 320ms chosen by ear (Justin, 13 Aug 2026) — enough to land each sentence
    /// without sounding like it is buffering. 0 disables splitting entirely.
    var kokoroSentenceGapMs: Int {
        guard let raw = lock.withLock({ _config["PULSAR_KOKORO_GAP_MS"] }),
              let v = Int(raw.trimmingCharacters(in: .whitespaces)), v >= 0, v <= 2000
        else { return 320 }
        return v
    }

    /// Enforced quiet period between Kokoro syntheses, in milliseconds. Stops a
    /// burst of queued lines (a nine-drone roll call) from running GPU work
    /// back-to-back with no chance for memory to be returned in between. 350ms by
    /// default; playback of a single line is seconds long, so synthesis still runs
    /// well ahead of the speaker and the delay is not normally audible. 0 disables.
    var kokoroCooldownMs: Int {
        guard let raw = lock.withLock({ _config["PULSAR_KOKORO_COOLDOWN_MS"] }),
              let v = Int(raw.trimmingCharacters(in: .whitespaces)), v >= 0, v <= 5000
        else { return 350 }
        return v
    }

    /// Whether the cached "canon" fallback is allowed — the Stop hook's
    /// turn-end floor for turns the model didn't compose a bespoke line on.
    /// Off = bespoke-only: only the model's freshly composed lines speak (the
    /// default register). Speech is free (local `say`), so this is a style
    /// choice, not a cost lever. Default ON — a fresh install must never end a
    /// turn in total silence, and the opt-out idiom here has to match the other
    /// display flags below or the meaning of a missing key flips with the flag.
    var canonEnabled: Bool {
        let val = lock.withLock { _config["PULSAR_CANON_ENABLED"] } ?? "1"
        return !["0", "false", "no", "off", ""].contains(val.lowercased())
    }

    /// Whether the animated floating Pulsar head is shown on screen while it
    /// speaks. Default ON preserves today's behaviour. When OFF, the floating
    /// window is never created/shown (the voice still plays).
    var floatingHeadEnabled: Bool {
        let val = lock.withLock { _config["PULSAR_FLOATING_HEAD"] } ?? "1"
        return !["0", "false", "no", "off", ""].contains(val.lowercased())
    }

    /// Whether the read-along caption bubble is shown below the floating head
    /// while it speaks. Default ON. Gated by `floatingHeadEnabled` at the view
    /// layer — head off means no bubble regardless of this flag.
    var subtitlesEnabled: Bool {
        let val = lock.withLock { _config["PULSAR_SUBTITLES"] } ?? "1"
        return !["0", "false", "no", "off", ""].contains(val.lowercased())
    }

    /// Whether the orbiting/clustered sub-agent "drones" (the active-agent swarm)
    /// are shown. Default ON. When OFF only Pulsar himself appears; the drones'
    /// voices still play but no drone heads are rendered.
    var showActiveAgents: Bool {
        let val = lock.withLock { _config["PULSAR_SHOW_AGENTS"] } ?? "1"
        return !["0", "false", "no", "off", ""].contains(val.lowercased())
    }

    // MARK: - Mutate + reload

    /// Read config.json from disk and coerce every value to a String, tolerating
    /// Bool/number values so one non-string value can't nuke the whole config (a
    /// bad hand-edit — or a Bool written by an older build — must not silently
    /// revert mute or persona). Returns nil only when the file is
    /// missing/unreadable/not-an-object, so callers can distinguish "no file" from
    /// "empty file". SHARED by `reload()` and `set()` — they must agree on the
    /// tolerant read, or a read-modify-write through a strict cast wipes siblings.
    private func loadCoerced() -> [String: String]? {
        guard let data = try? Data(contentsOf: configPath),
              let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
        else { return nil }
        var coerced: [String: String] = [:]
        for (k, v) in raw {
            if let s = v as? String { coerced[k] = s }
            else if let b = v as? Bool { coerced[k] = b ? "1" : "0" }
            else if let n = v as? NSNumber { coerced[k] = n.stringValue }
        }
        return coerced
    }

    /// Re-read config.json from disk. Call after any write.
    func reload() {
        guard let coerced = loadCoerced() else { return }  // keep last-known, never blank
        lock.withLock { _config = coerced }
    }

    /// Write a single key back to config.json and reload. Reads the existing file
    /// with the SAME tolerant coercion as `reload()` (via `loadCoerced()`), so a
    /// sibling key holding a Bool/number value is preserved rather than wiped —
    /// the old strict `[String: String]` cast returned nil on any non-string
    /// value and clobbered every other key on the next write.
    /// The read-modify-write is held under one lock: Hummingbird runs handlers as
    /// concurrent Tasks, so two `/settings` POSTs touching DIFFERENT keys would
    /// otherwise interleave read→write and silently drop one key's update (a
    /// lost-update race, found by adversarial review 2026-07-30).
    private static let writeLock = NSLock()

    func set(_ key: String, value: String) throws {
        try Self.writeLock.withLock {
            var current = loadCoerced() ?? [:]
            current[key] = value
            let data = try JSONSerialization.data(withJSONObject: current, options: .prettyPrinted)
            try data.write(to: configPath)
        }
        reload()
    }

    // MARK: - One-shot legacy migration (Caldwell → Pulsar / legacy dir)

    /// Legacy Application-Support dir the pre-rename `caldwell-speak` build wrote
    /// its state into. Sibling of `storageRoot` under the same Application Support
    /// root, so a `PULSAR_STORAGE` dev override redirects both in lockstep (the
    /// legacy dir is looked for beside wherever storage currently resolves).
    var legacyStorageRoot: URL {
        storageRoot.deletingLastPathComponent()
            .appendingPathComponent("caldwell-speak", isDirectory: true)
    }

    /// Sentinel marking the one-shot migration as done. Idempotency gates on THIS
    /// file's existence, never on key-presence — a user caught mid-hybrid (both
    /// CALDWELL_* and PULSAR_* keys live) must not re-run and clobber a newer
    /// PULSAR_* value the user re-toggled after the rename.
    private var migrationSentinel: URL {
        storageRoot.appendingPathComponent(".migrated")
    }

    /// One-shot, idempotent migration from the pre-rename `caldwell-speak` layout
    /// and from any lingering `CALDWELL_*` keys in the live config.
    ///
    /// MUST run BEFORE the server arms / `restoreInFlight()` and BEFORE the first
    /// `/settings` POST, so the merge can't race a live write. Wrapped in do/catch
    /// end-to-end: a failed migration NEVER blocks startup or corrupts the live
    /// config — worst case it's retried next launch (the sentinel is written last,
    /// only on success). Non-destructive: the legacy dir is COPIED, never moved.
    ///
    /// Rules:
    ///   • Gate on the `.migrated` sentinel. If present, no-op.
    ///   • If the new config.json is absent OR still carries `CALDWELL_*` keys,
    ///     seed from the legacy dir's config.json (+ cache/ if the new cache is
    ///     absent) by COPY.
    ///   • Rewrite every `CALDWELL_<X>` → `PULSAR_<X>`; on conflict the existing
    ///     `PULSAR_<X>` WINS (respects a post-rename re-toggle). Drop the old
    ///     `CALDWELL_*` keys.
    ///   • Persist via the hardened `set()`; write the sentinel LAST.
    func migrateLegacyConfigIfNeeded() {
        let fm = FileManager.default

        // Sentinel gate — already migrated, nothing to do.
        if fm.fileExists(atPath: migrationSentinel.path) { return }

        do {
            // Snapshot the current live config (tolerant read). nil = no file yet.
            let existing = loadCoerced()
            let hasLegacyKeys = (existing ?? [:]).keys.contains { $0.hasPrefix("CALDWELL_") }

            // Only do work if the new config is absent OR still half-migrated.
            // A fully-migrated config with no CALDWELL_* keys just gets a sentinel
            // so we never scan again.
            if existing != nil && !hasLegacyKeys {
                try? "ok".write(to: migrationSentinel, atomically: true, encoding: .utf8)
                return
            }

            // (1) Seed from the legacy dir if the new config is absent.
            let legacyConfig = legacyStorageRoot.appendingPathComponent("config.json")
            if existing == nil, fm.fileExists(atPath: legacyConfig.path) {
                // Copy the legacy config into place so loadCoerced() can read it.
                if fm.fileExists(atPath: configPath.path) { try? fm.removeItem(at: configPath) }
                try? fm.copyItem(at: legacyConfig, to: configPath)
            }

            // Copy the legacy cache/ if the new cache is absent (best-effort).
            let legacyCache = legacyStorageRoot.appendingPathComponent("cache", isDirectory: true)
            if !fm.fileExists(atPath: cacheDir.path), fm.fileExists(atPath: legacyCache.path) {
                try? fm.copyItem(at: legacyCache, to: cacheDir)
            }

            // (2) Load whatever config we now have (seeded or pre-existing).
            var merged = loadCoerced() ?? [:]

            // (3) Rewrite CALDWELL_<X> → PULSAR_<X>, PULSAR_ wins on conflict,
            //     drop the old keys.
            for (k, v) in merged where k.hasPrefix("CALDWELL_") {
                let newKey = "PULSAR_" + k.dropFirst("CALDWELL_".count)
                if merged[newKey] == nil {          // PULSAR_ wins on conflict
                    merged[newKey] = v
                }
                merged.removeValue(forKey: k)
            }

            // (4) Persist the merged dict under the SAME write lock `set()` uses.
            //     The comment here used to claim this went "via set()" while the
            //     code did a raw unlocked write — harmless in practice (migration
            //     runs once at startup, before the daemon serves) but it was a
            //     second, unguarded write path into the same file, which is
            //     exactly how lost-update races get reintroduced later.
            try Self.writeLock.withLock {
                let data = try JSONSerialization.data(withJSONObject: merged, options: .prettyPrinted)
                try data.write(to: configPath)
            }
            reload()

            // (5) Sentinel LAST — only on success.
            try "ok".write(to: migrationSentinel, atomically: true, encoding: .utf8)
        } catch {
            // Never fatal: leave the live config as-is, no sentinel, retry next
            // launch. Startup proceeds regardless.
            NSLog("PulsarConfig: legacy migration skipped (\(error.localizedDescription))")
        }
    }
}

// Convenience — avoids `defer` boilerplate.
extension NSLock {
    @discardableResult
    func withLock<T>(_ body: () -> T) -> T {
        lock(); defer { unlock() }
        return body()
    }
}
