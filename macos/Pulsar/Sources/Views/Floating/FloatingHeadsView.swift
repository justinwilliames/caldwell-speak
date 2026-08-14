import SwiftUI

struct FloatingHeadsView: View {
    let viewModel: DashboardViewModel
    /// Shared geometry: which side the caption renders on + its horizontal nudge.
    let layout: FloatingLayoutModel

    /// Reports the caption's CURRENT (revealed) height up to the panel controller
    /// so it can grow the window in the locked direction as the text types in
    /// (0 when hidden).
    var onCaptionHeightChange: ((CGFloat) -> Void)?

    /// Reports the caption TEXT once per line so the controller can measure its
    /// full height DETERMINISTICALLY (AppKit) and size the panel to fit the whole
    /// line. Replaces the SwiftUI height feedback, which deadlocked and clipped
    /// long captions at ~3 lines.
    var onCaptionText: ((String) -> Void)?

    /// Full centre portrait size (matches FloatingPortraitView.portraitSize).
    static let centrePortraitSize: CGFloat = 120

    private let orbitRadius: CGFloat = 80

    /// Ring radius that makes the orbiting heads OVERLAP the speaker slightly.
    ///
    /// Centre-to-centre of (half the speaker + half a thumbnail) is exactly
    /// touching; subtracting the overlap tucks them under. The speaker holds
    /// zIndex(20) so it always renders on top and the overlap reads as depth.
    private let speakerOverlap: CGFloat = 12
    private var overlapRadius: CGFloat {
        (Self.centrePortraitSize + thumbnailSize) / 2 - speakerOverlap
    }
    /// In-action sub-agent thumbnail size — the PASSIVE (orbiting) head. Bumped
    /// 40→52 (~30%), then 52→62 (+20%, Justin 2026-08-14) now the portraits carry
    /// real faces worth seeing rather than abstract robot heads. The cluster
    /// spacing and arc step below are derived from this, so they scale with it and
    /// the heads cannot start overlapping as it grows.
    private let thumbnailSize: CGFloat = 62
    /// Lift the whole cluster UP so the swarm hovers over the TOP of the hub,
    /// leaving the below-head zone clear for the name pill + subtitle.
    private let orbitYOffset: CGFloat = -8
    /// The swarm CLUSTERS above the hub rather than fanning across a wide rail:
    /// slots are placed symmetrically around a hub angle (270° = straight up)
    /// with a TIGHT per-slot angular step, so they group as a compact pod. The
    /// per-drone organic drift (FloatingDronePortraitView) then keeps them
    /// mingling so they never read as rigid, evenly-spaced icons.
    private let clusterCenterDegrees: Double = 270   // straight up
    /// Angular gap between adjacent swarm slots while a speaker holds the centre
    /// (the arc orbit). Widened to 44° so the larger 52pt thumbnails still clear
    /// each other on the arc.
    private let clusterStepDegrees: Double = 44
    /// Grid spacing for the IDLE symmetric cluster (no speaker) — sized to the
    /// larger 52pt thumbnails (~10pt gap) so they sit snug as one oval pod without
    /// the heads overlapping.
    /// Centre-to-centre spacing of the IDLE cluster — the passive floating heads.
    ///
    /// DERIVED, never a bare number. It was hardcoded at 63, tuned when heads were
    /// 52pt (an 11pt gap). When the heads grew to 62pt that became a ONE POINT gap
    /// and the swarm visibly collided — and the earlier clearance fix did not help,
    /// because that one only touched the speaking ARC. Idle layout is a separate
    /// code path and knew nothing about head size.
    ///
    /// The gap allows for the per-drone bob (~3.4pt each, so ~7pt of closing between
    /// two neighbours on opposite phases) plus the lit border and its glow.
    private var clusterSpacing: CGFloat { thumbnailSize + 16 }

    /// Fixed head-zone footprint. The head + its orbiting queue thumbnails + glow
    /// live here; the caption grows ABOVE or BELOW it. Height is sized so the
    /// pulsar-pulse glow (ripple frame = portrait+110 ⇒ ~115pt half-extent, plus
    /// the head's soft shadow + bob) fades COMPLETELY before the panel's edge —
    /// the head is centred, giving equal top/bottom clearance so neither
    /// placement (caption-below ⇒ head near top, caption-above ⇒ head near
    /// bottom) clips the glow. The caption still hugs the head via the negative
    /// attach gap below, so this headroom does NOT reopen an empty gap.
    // The head zone is a FIXED frame, so it has to be big enough for the largest
    // swarm the geometry can produce — it does not grow to fit. At 62pt heads the
    // collision-clearance maths pushes the orbit radius to ~104pt, putting the top
    // of a head ~143pt above centre; against the old 240pt zone (120pt half-height)
    // the cluster was clipped off the top of the screen. Sized for radius + half a
    // head + the lit border and its glow, with margin.
    static let headZoneWidth: CGFloat = 320
    static let headZoneHeight: CGFloat = 320

    /// Vertical overlap between the head zone and the caption. The head squircle
    /// (120pt) is centred in the 240pt head zone, so its BOTTOM sits ~60pt above
    /// the head zone's lower edge. This negative gap pulls the caption up so the
    /// bubble's tail nearly touches the squircle bottom, leaving only a few px —
    /// while still reserving `glowMargin` (via captionEdgePadding) so neither
    /// glow hard-cuts. −54 ⇒ tail ~6px below the squircle after the padding.
    /// Negative spacing that pulls the caption bubble back up toward the speaking
    /// head. DERIVED from the head-zone height, not a bare number.
    ///
    /// -54 was hand-fitted when the zone was 240pt tall. The speaking head is
    /// centred in the zone but the bubble hangs below the WHOLE zone, so growing
    /// the zone to 320pt (to stop the swarm being cropped) pushed the bubble
    /// (320-240)/2 = 40pt further from the face. Tying the gap to the zone means a
    /// future resize moves the bubble with the head instead of away from it.
    private var captionAttachGap: CGFloat { -54 - (Self.headZoneHeight - 240) / 2 }
    /// Padding around the caption inside the panel — sized to the bubble's glow
    /// reserve so the outer glow fades fully before the panel edge (top/bottom +
    /// the horizontal side that the tail edge doesn't consume).
    private var captionEdgePadding: CGFloat { SubtitleBubbleView.glowMargin }

    // MARK: - Caption lifecycle state

    @State private var displayedCaption: String?
    @State private var lingerTask: Task<Void, Never>?
    /// When the current caption first appeared — drives the typewriter's local clock.
    @State private var captionStartedAt: Date?
    /// Which speaker produced the currently-displayed caption. A caption belongs
    /// to ONE speaker; if the active speaker changes (or goes idle), the old
    /// caption is cleared rather than lingered under a different/idle speaker.
    @State private var captionOwner: String?

    /// How long the caption stays after a line completes. Set deliberately LONGER
    /// than AppDelegate.tailAfterIdle (5s) + the panel's 0.9s fade, so the subtitle
    /// stays visible right through the head's fade-out and dissolves WITH it —
    /// rather than snapping out the instant the fade begins (which read as the head
    /// hovering subtitle-less). The panel's alpha fade carries the caption away
    /// before this timer ever clears the text.
    static let lingerAfterIdle: TimeInterval = 6.0

    /// Max thumbnails on the orbit arc WHILE a speaker holds the centre. With a
    /// ten-strong cast, one speaks and nine can orbit, so the cap is nine and the
    /// arc adapts instead: `orbitArcGeometry` shrinks the angular step and grows
    /// the radius together, so nine 52pt heads neither overlap nor wrap the ring.
    /// The idle cluster is uncapped (its 3-row palindrome already packs 10:[3,4,3]).
    static let speakingOrbitCap = 9

    /// Widest arc the swarm may occupy while a speaker holds the centre. Kept
    /// under a full circle so the pod still reads as a cluster ABOVE the hub
    /// rather than a ring around it.
    /// The swarm occupies a SEMI-CIRCLE over the speaker — top, left and right,
    /// never the bottom. 300° wrapped the ring almost the whole way round, which
    /// put heads underneath the speaker where the subtitle bubble sits and
    /// covers them. 200°, centred on straight up, spans from the 8 o'clock
    /// position round to 4 o'clock and leaves the bottom clear for the caption.
    private let maxOrbitSpanDegrees: Double = 200

    var body: some View {
        VStack(spacing: captionAttachGap) {
            if layout.captionEdge == .above {
                captionZone
                headZone
            } else {
                headZone
                captionZone
            }
        }
        // The container must be as wide as the PANEL (== SubtitleBubbleView.maxWidth),
        // not the 240 head zone — otherwise the caption is capped at 240 and a long
        // line stacks into a tall narrow column that overflows the screen (and the
        // panel's height math, which assumes the full width, under-sizes it → crop).
        // The head keeps its own 240 frame and stays centred within this wider box.
        .frame(width: SubtitleBubbleView.maxWidth)
        .frame(maxHeight: .infinity, alignment: layout.captionEdge == .above ? .bottom : .top)
        .onChange(of: captionSource) { _, _ in updateCaption() }
        .onChange(of: viewModel.playback.isPlaying) { _, _ in updateCaption() }
        .onChange(of: currentSpeakerKey) { _, _ in updateCaption() }
        .onChange(of: subtitlesActive) { _, _ in updateCaption() }
        .onAppear { updateCaption() }
    }

    // MARK: - Head zone

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    /// The single source of truth for who is speaking (P3). Everything in the
    /// head zone reads ONLY this — no independent currentAgentCategory /
    /// inFlightDrones / amplitude reads — so the centre, name card, and subtitle
    /// can never desync.
    private var speaker: DashboardViewModel.SpeakerSnapshot? { viewModel.activeSpeaker }

    /// The drone category owning the line, or nil when Pulsar speaks.
    ///
    /// `"pulsar"` normalises to nil. Pulsar became a spawnable category with a real
    /// DroneRegistry entry, so a line can now legitimately arrive tagged
    /// `--agent pulsar` — but every branch in this view encodes "Pulsar is speaking"
    /// as category == nil. Left un-normalised, a pulsar-tagged line took the
    /// orbiting-drone path instead of the hub path: the head stayed small, never
    /// took the centre, and did not animate while the subtitle played. Observed by
    /// Justin on the first Kokoro roll call.
    private var activeDroneCategory: String? {
        guard let c = speaker?.category?.lowercased()
            .trimmingCharacters(in: .whitespaces), !c.isEmpty, c != "pulsar" else { return nil }
        return c
    }

    /// The head zone renders while ANY participant is present — the live team
    /// (Pulsar + running sub-agents), whether or not anyone is currently
    /// speaking. Activity-gated: a running sub-agent (or an active main session)
    /// shows its participant orbiting even when silent; the centre is filled by
    /// whoever is speaking, or stays empty between lines if no one is.
    private var panelHasContent: Bool {
        speaker != nil || viewModel.hasInFlightDrones || viewModel.pulsarIsPresent
    }

    // MARK: - Head zone (true place-swap via matched arcs)

    @ViewBuilder
    private var headZone: some View {
        ZStack {
            if panelHasContent {
                // Idle queued voices orbit behind everything — but ONLY when there
                // is no live drone swarm. Once real drones are in flight, the
                // participant orbit is the sole representation of who's working; a
                // background queue-preview thumbnail then reads as a spurious drone
                // "hiding" behind the swarm. Suppress it whenever drones are present.
                if !viewModel.hasInFlightDrones {
                    queuedThumbnails
                }

                // ONE list of participants — the live team (Pulsar + running
                // sub-agents). CENTRE = the current speaker; ORBIT = everyone else
                // present (drones + present-but-silent Pulsar). Each is positioned
                // by its TARGET slot — centre or an orbit index — so when the
                // speaker changes, the incoming participant travels orbit→centre
                // and the outgoing one travels centre→orbit on the SAME spring
                // value-change: a genuine pass-the-baton, not a crossfade.
                ForEach(participants) { p in
                    ParticipantSlotView(
                        participant: p,
                        speaker: speaker,
                        orbitOffset: slotOffset(index: p.orbitIndex, total: orbitSlotCount),
                        thumbnailSize: thumbnailSize,
                        reduceMotion: reduceMotion,
                        portraitManager: viewModel.portraitManager,
                        // Clicking the speaker goes to the session it's speaking
                        // from. Only wired for the centre occupant, and only when
                        // that session is actually addressable.
                        openSession: sessionRef.map { ref in { SessionLink.open(ref) } },
                        sessionName: sessionName,
                        onPortraitHover: { hoveringPortrait = $0 }
                    )
                    .id(p.id)
                    .zIndex(p.isCentre ? 20 : Double(7 - p.orbitIndex))
                }

                // WHICH session is talking — revealed only while the pointer is on
                // the speaking drone, so the resting panel stays a face and a line
                // of speech. Sits on the speaker's lower edge like a nameplate,
                // inside the 120pt squircle, so it never collides with the caption
                // bubble that attaches just below it.
                if speaker != nil, let session = sessionName, showSessionPlate {
                    sessionNameplate(session)
                        .offset(y: 50)
                        .zIndex(30)
                        .transition(.opacity.combined(with: .scale(scale: 0.9)))
                }
            }
        }
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.18), value: showSessionPlate)
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.25), value: sessionName)
        // A speaker change tears the portrait's tracking area down without an exit
        // event, so the hover flags would latch on. Clear them on every swap.
        .onChange(of: currentSpeakerKey) { _, _ in clearHover() }
        .onChange(of: speaker == nil) { _, _ in clearHover() }
        .frame(width: Self.headZoneWidth, height: Self.headZoneHeight)
        // [FIX 3 — Reduce Motion] All slot-glide springs are gated on
        // `reduceMotion`. When on, animations are nil (instant snap) so
        // participants teleport rather than spring — no vestibular motion.
        .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.78), value: viewModel.queueItems.map(\.id))
        .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.78), value: sortedDrones.map(\.id))
        // Idle cluster repack: when the count changes (drone joins/leaves) the
        // slot offsets shift. Spring-animate on participant-id list so the repack
        // is a smooth spring rather than a positional snap.
        .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.78), value: participants.map(\.id))
        // Mode switch speaker→idle (and vice-versa): slotOffset toggles between
        // arc and cluster layouts. Spring this transition so drones don't teleport
        // back to the swarm when the centre clears.
        .animation(reduceMotion ? nil : .spring(response: 0.48, dampingFraction: 0.74), value: speaker == nil)
        // The swap itself, P1: arriving drone overshoots slightly into the
        // centre (presence); departing Pulsar eases out slower. Both keyed on
        // who holds the centre so they animate as a matched trade.
        .animation(reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.62), value: activeDroneCategory)
    }

    // MARK: - Session attribution

    /// Pointer is over the speaking portrait / over the nameplate itself. Two
    /// flags rather than one: the plate overlaps the portrait and can be wider
    /// than it, so whichever the pointer is actually inside has to hold the
    /// reveal open — otherwise moving from face to plate flickers it away.
    @State private var hoveringPortrait = false
    @State private var hoveringPlate = false

    private var showSessionPlate: Bool { hoveringPortrait || hoveringPlate }

    private func clearHover() {
        hoveringPortrait = false
        hoveringPlate = false
    }

    /// Name of the session the current-or-lingering line is spoken from. Empty
    /// resolves to nil so an unattributed line shows no plate rather than a blank.
    private var sessionName: String? {
        guard let name = viewModel.playback.sessionName?
            .trimmingCharacters(in: .whitespacesAndNewlines), !name.isEmpty else { return nil }
        return name
    }

    /// The id that reopens that session, or nil when there's nothing to open —
    /// which is also what gates the click, so the plate is never a dead button.
    private var sessionRef: String? {
        let ref = viewModel.playback.sessionRef
        return SessionLink.canOpen(ref) ? ref : nil
    }

    /// The speaker's nameplate: which session this voice is coming from, and —
    /// when the session is addressable — a click that takes you there.
    @ViewBuilder
    private func sessionNameplate(_ name: String) -> some View {
        let tint = droneColor(for: captionCategory)
        let plate = HStack(spacing: 3) {
            if sessionRef != nil {
                Image(systemName: "arrow.up.forward.app.fill")
                    .font(.system(size: 7, weight: .bold))
            }
            Text(name)
                .font(.system(size: 9, weight: .semibold))
                .lineLimit(1)
                .truncationMode(.tail)
        }
        .foregroundStyle(.white.opacity(0.95))
        .padding(.horizontal, 7)
        .padding(.vertical, 2)
        .frame(maxWidth: Self.headZoneWidth - 60)
        .fixedSize(horizontal: true, vertical: false)
        .background(.black.opacity(0.55), in: Capsule())
        .overlay(Capsule().strokeBorder(tint.opacity(0.55), lineWidth: 0.75))
        .shadow(color: .black.opacity(0.35), radius: 3, y: 1)

        if let ref = sessionRef {
            // A Button (not a bare tap gesture): the panel is
            // `isMovableByWindowBackground`, so a plain hit-test region would be
            // swallowed by the window drag. AppKit lets control views take the
            // mouseDown instead of starting a drag.
            Button { SessionLink.open(ref) } label: { plate }
                .buttonStyle(.plain)
                .background(HoverTracker { hovering in
                    hoveringPlate = hovering
                    if hovering { NSCursor.pointingHand.push() } else { NSCursor.pop() }
                })
                .help("Open the “\(name)” session in Claude Code")
        } else {
            plate
                .background(HoverTracker { hoveringPlate = $0 })
                .help("Speaking from “\(name)”")
        }
    }

    // NOTE: rendering of each participant now lives in `ParticipantSlotView`
    // (bottom of this file). That view is a SINGLE stable-identity element per
    // participant id whose position/scale glide between its orbit slot and the
    // centre as `isCentre` flips — so a character is NEVER torn down + rebuilt
    // (and hence never briefly duplicated) when it stops or starts speaking.
    // The old two-branch approach (FloatingPortraitView with an insert/remove
    // transition vs FloatingDronePortraitView) is what produced the "two Echoes"
    // ghost during a swap; it has been removed.

    /// The drone category that themes the CAPTION (tint + name pill). Keyed to
    /// the caption's speaker and survives the linger — so the bubble keeps its
    /// speaker colour + name even after the portrait has dropped back into the
    /// swarm (audio ended). nil = Pulsar (indigo) or no drone line.
    private var captionCategory: String? { viewModel.captionSpeakerCategory }

    /// The set of character keys the PARTICIPANT model already renders (in-flight
    /// drone categories, plus "pulsar" when Pulsar is a present participant). The
    /// queued-voices background layer must NOT re-render any of these, or the same
    /// character shows twice — once as its canonical drone/Pulsar orbit head and
    /// again as a redundant queued thumbnail behind the swarm (the "duplicates in
    /// the background" seen when a queued line's category is already an active
    /// drone). The participant orbit is the canonical representation.
    private var participantCharacterKeys: Set<String> {
        Set(participants.map { $0.category?.lowercased() ?? "pulsar" })
    }

    /// The queued voices eligible for a BACKGROUND thumbnail — the not-playing
    /// queue, with two dedupes applied so the background can never twin a
    /// character that's already on screen:
    ///   1. Drop any whose category is already a live participant (in-flight
    ///      drone, current speaker, or present Pulsar) — the participant orbit is
    ///      the canonical head for those.
    ///   2. Collapse remaining same-category queued items to ONE (a character is
    ///      a character, never a count), mirroring the participant model.
    /// Survives for the genuine no-overlap queue-preview case (a queued voice for
    /// a character with no in-flight drone of that type).
    private var dedupedQueuedItems: [QueueItem] {
        var shown = participantCharacterKeys
        var out: [QueueItem] = []
        for item in viewModel.queueItems where !item.isPlaying {
            let key = item.agent?.lowercased() ?? "pulsar"
            if shown.contains(key) { continue }
            shown.insert(key)
            out.append(item)
        }
        return Array(out.prefix(5))
    }

    /// Idle queued voices keep their existing orbiting thumbnails, behind the
    /// drones — but only the deduped set (see `dedupedQueuedItems`), so a queued
    /// line whose category is already a live participant never renders a second,
    /// "background" copy of that character behind the swarm.
    @ViewBuilder
    private var queuedThumbnails: some View {
        let queued = dedupedQueuedItems
        ForEach(Array(queued.enumerated()), id: \.element.id) { index, item in
            QueueBubbleView(
                item: item,
                index: index,
                total: queued.count,
                thumbnailSize: thumbnailSize,
                orbitRadius: orbitRadius,
                orbitYOffset: orbitYOffset,
                angle: orbitAngle(index: index, total: queued.count),
                voiceColor: viewModel.voiceColor(for: item.voice),
                portraitManager: viewModel.portraitManager
            )
            .zIndex(Double(-1 - index))
        }
    }

    // MARK: - Participant model (one slot per distinct character TYPE)

    /// One participant on screen: Pulsar or a character-TYPE slot (one per
    /// distinct in-flight category — the drones are CHARACTERS, so multiple
    /// sub-agents of a type still show as ONE busy character, never a count).
    /// Identity is stable — Pulsar = "pulsar", a type slot = its category name —
    /// so SwiftUI animates the SAME view between centre and orbit as the speaker
    /// swaps.
    struct Participant: Identifiable {
        let id: String          // "pulsar" or the category name
        let category: String?   // nil = Pulsar
        let color: Color
        let isCentre: Bool
        let orbitIndex: Int     // valid only when !isCentre
    }

    /// The full participant list. Everyone is a PEER:
    ///   • CENTRE = whoever is currently SPEAKING (Pulsar or a drone). If no one
    ///     is speaking (between lines, or silent activity) there is NO centre —
    ///     all present participants orbit.
    ///   • ORBIT = every other PRESENT participant — the in-flight drones plus
    ///     Pulsar when he's present-but-silent. Pulsar is treated exactly like a
    ///     drone: he centres when he speaks, orbits when active-but-quiet.
    private var participants: [Participant] {
        var out: [Participant] = []
        let speakingCategory = activeDroneCategory          // nil = Pulsar (or no one)
        let pulsarSpeaking = speaker != nil && speakingCategory == nil

        // "Show active agents" toggle: when OFF, no drone heads render at all —
        // only Pulsar appears (a drone line then plays voice-only; see also
        // captionSource, which hides the drone bubble to match).
        let showAgents = viewModel.isShowActiveAgents

        // Centre = the active speaker, if anyone is speaking.
        if let speakingCategory {
            if showAgents {
                out.append(Participant(id: speakingCategory, category: speakingCategory,
                                       color: droneColor(for: speakingCategory),
                                       isCentre: true, orbitIndex: 0))
            }
            // else: a drone is speaking but agents are hidden → no head.
        } else if pulsarSpeaking {
            out.append(Participant(id: "pulsar", category: nil,
                                   color: droneColor(for: nil),
                                   isCentre: true, orbitIndex: 0))
        }
        // else: nobody speaking → no centre occupant; all participants orbit.

        // Orbit = every OTHER present participant — the in-flight drone types
        // (excluding the centred speaker) AND Pulsar himself when he's present
        // but NOT the centre speaker. Pulsar is a genuine PEER: when a drone
        // takes the centre (or Pulsar has just finished while drones are still
        // in-flight), Pulsar occupies an orbit slot and GLIDES centre→orbit as
        // the SAME single view (see ParticipantSlotView) — he does NOT vanish.
        // He only leaves the swarm when the whole panel goes idle/hidden, which
        // `panelShouldBeVisible` / the linger logic decides — untouched here.
        var orbitKeys: [(id: String, category: String?)] = []

        // Pulsar orbits whenever he's present (main session active — drones
        // in-flight or audio playing) but isn't the one holding the centre.
        // Gate on `showAgents` too: with agents hidden the swarm is suppressed,
        // so the peer-orbit Pulsar thumbnail is suppressed with it (only a
        // speaking Pulsar shows a head then, via the centre branch above).
        let pulsarOrbits = showAgents && viewModel.pulsarIsPresent && !pulsarSpeaking
        if pulsarOrbits {
            orbitKeys.append((id: "pulsar", category: nil))
        }

        let present = showAgents ? inFlightCategories : []
        for category in DroneRegistry.categories
        where category != speakingCategory && present.contains(category) {
            orbitKeys.append((id: category, category: category))
        }

        // Cap the ARC while someone holds the centre. The idle cluster was
        // hardened for nine, but the speaking state puts the centre head at
        // ~2.4× over the same arc: at eight-plus orbiters the thumbnails reduce
        // to slivers and stack behind the speaker — crowding worst at the exact
        // moment legibility matters most (screenshot-confirmed 2026-07-30).
        // Idle keeps the full nine-slot cluster; the queued-thumbnail row uses
        // the same shape of cap (see dedupedQueuedItems).
        if speaker != nil, orbitKeys.count > Self.speakingOrbitCap {
            orbitKeys = Array(orbitKeys.prefix(Self.speakingOrbitCap))
        }
        for (i, k) in orbitKeys.enumerated() {
            out.append(Participant(id: k.id, category: k.category,
                                   color: droneColor(for: k.category),
                                   isCentre: false, orbitIndex: i))
        }
        return out
    }

    /// How many orbit slots are currently rendered — drives the arc spacing.
    private var orbitSlotCount: Int {
        participants.filter { !$0.isCentre }.count
    }

    /// The set of distinct in-flight categories (lowercased) — presence only.
    private var inFlightCategories: Set<String> {
        Set(viewModel.inFlightDrones.values.map { $0.lowercased() })
    }

    /// In-flight drones in a stable order (by agentId) — kept for the swap-edge
    /// animation key (membership/category set).
    private var sortedDrones: [DroneInFlight] {
        viewModel.inFlightDrones
            .sorted { $0.key < $1.key }
            .map { DroneInFlight(id: $0.key, category: $0.value.lowercased()) }
    }

    // MARK: - Caption zone

    @ViewBuilder
    private var captionZone: some View {
        Group {
            if let caption = displayedCaption {
                SubtitleBubbleView(fullText: caption,
                                   startedAt: captionStartedAt ?? Date(),
                                   holdFull: !viewModel.playback.isPlaying,
                                   tailEdge: layout.captionEdge == .above ? .bottom : .top,
                                   maxHeight: captionMaxHeight,
                                   activeColor: droneColor(for: captionCategory),   // caption tint survives linger
                                   // captionCategory, not the live speaker: the
                                   // name must keep matching its own words while
                                   // the caption lingers after speech ends.
                                   speakerName: (captionCategory ?? "pulsar").capitalized,
                                   speakerRole: DroneRegistry.role(for: captionCategory ?? "pulsar"))
                    .id(caption)
                    .offset(x: layout.captionXOffset)
                    // Use 2× glowMargin horizontally so the plusLighter rim-glow
                    // (blur radius up to ~6pt, margin = 16pt) has a full margin
                    // before the panel edge and doesn't hard-clip on either side.
                    .padding(.horizontal, captionEdgePadding * 2)
                    .padding(layout.captionEdge == .above ? .top : .bottom, captionEdgePadding)
                    .background(
                        GeometryReader { proxy in
                            Color.clear.preference(key: CaptionHeightKey.self, value: proxy.size.height)
                        }
                    )
                    .transition(.opacity.combined(
                        with: .move(edge: layout.captionEdge == .above ? .bottom : .top)))
            }
        }
        .frame(maxWidth: .infinity)
        .animation(.easeInOut(duration: 0.35), value: displayedCaption)
        .animation(.easeInOut(duration: 0.35), value: layout.captionEdge)
        .onPreferenceChange(CaptionHeightKey.self) { height in
            onCaptionHeightChange?(displayedCaption == nil ? 0 : height)
        }
        .onChange(of: displayedCaption) { _, new in
            if let new { onCaptionText?(new) } else { onCaptionHeightChange?(0) }
        }
    }


    /// Cap the bubble height to what the panel can show on screen, so an extreme
    /// line still fits in full rather than being truncated.
    private var captionMaxHeight: CGFloat {
        let screenH = NSScreen.main?.visibleFrame.height ?? 900
        // Leave room for the head zone + comfortable top/bottom margins.
        return max(120, screenH - Self.headZoneHeight - 80)
    }

    // MARK: - Caption lifecycle driver

    private var captionSource: String? {
        // When the swarm is hidden, a drone line shows no head — so it shows no
        // bubble either (voice-only). Pulsar's own captions are unaffected.
        if !viewModel.isShowActiveAgents, isDrone(viewModel.playback.currentAgentCategory) {
            return nil
        }
        return Self.clampedCaption(viewModel.playback.currentText)
    }

    /// NO display truncation and NO ellipsis, ever. Voice lines are capped for
    /// length at the SOURCE (say.sh trims each spoken line to a sentence boundary
    /// under its length budget), so by the time a line reaches the bubble it's
    /// already short enough to show in full. This is just a whitespace trim.
    static func clampedCaption(_ text: String?) -> String? {
        guard let text else { return nil }
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }

    /// A stable identity for the caption's speaker — the drone category, else
    /// "pulsar", else nil when there's no line. Used to detect a genuine speaker
    /// CHANGE so a caption is never lingered under a DIFFERENT speaker. Keyed to
    /// the CAPTION signal (which persists through the linger), NOT to
    /// `activeSpeaker` (which now goes nil the instant audio ends) — otherwise
    /// audio-end would look like a speaker change and kill the linger.
    private var currentSpeakerKey: String? {
        // No current line at all → no owner.
        guard viewModel.playback.currentText?.isEmpty == false else { return nil }
        return captionCategory ?? "pulsar"
    }

    private var subtitlesActive: Bool {
        viewModel.isSubtitlesEnabled && viewModel.isFloatingHeadEnabled
    }

    private func updateCaption() {
        guard subtitlesActive else {
            clearCaption()
            return
        }

        let source = captionSource
        let speaking = viewModel.playback.isPlaying
        let owner = currentSpeakerKey

        // Speaker changed out from under a displayed caption → drop it at once.
        // The old caption belongs to the previous speaker, not whoever is here
        // now (or to the idle state). Don't linger it.
        if displayedCaption != nil, owner != captionOwner {
            clearCaption()
        }

        if speaking, let text = source, !text.isEmpty {
            lingerTask?.cancel(); lingerTask = nil
            if displayedCaption != text { captionStartedAt = Date() }  // new line → restart the typewriter clock
            displayedCaption = text
            captionOwner = owner
        } else if let text = source, !text.isEmpty, displayedCaption != nil, owner == captionOwner {
            // Same speaker, line finished → hold through the linger.
            displayedCaption = text
            scheduleLinger(for: owner)
        } else if source == nil || source?.isEmpty == true {
            clearCaption()
        }
    }

    /// Clear the caption + its lifecycle state in one place.
    private func clearCaption() {
        lingerTask?.cancel(); lingerTask = nil
        displayedCaption = nil
        captionStartedAt = nil
        captionOwner = nil
    }

    private func scheduleLinger(for owner: String?) {
        lingerTask?.cancel()
        lingerTask = Task { @MainActor in
            try? await Task.sleep(nanoseconds: UInt64(Self.lingerAfterIdle * 1_000_000_000))
            guard !Task.isCancelled else { return }
            // Only clear if the SAME speaker is still (not) speaking — a new
            // speaker would have already replaced the caption + owner.
            if !viewModel.playback.isPlaying, captionOwner == owner {
                clearCaption()
            }
        }
    }

    /// Place slot `index` of `total` as a COMPACT CLUSTER centred on the hub
    /// angle (straight up): slots fan symmetrically around the centre with a
    /// tight fixed step, so a few drones sit as a snug pod rather than spread
    /// across a wide rail. One slot sits dead-centre; the swarm drift does the
    /// rest of the mingling.
    private func orbitAngle(index: Int, total: Int) -> Double {
        guard total > 0 else { return 0 }
        // Symmetric offset from centre: e.g. total=3 → offsets -1,0,+1;
        // total=4 → -1.5,-0.5,+0.5,+1.5.
        let offset = Double(index) - Double(total - 1) / 2.0
        let degrees = clusterCenterDegrees + offset * orbitArcGeometry(total).stepDegrees
        return degrees * .pi / 180
    }

    /// Angular step and radius for an arc of `total` slots.
    ///
    /// A fixed 44° step fanned four drones out nicely and wrapped nine right round
    /// the hub. So the step shrinks to keep the whole swarm inside
    /// `maxOrbitSpanDegrees`, and the radius then grows to whatever keeps adjacent
    /// 52pt heads from touching at that step — chord = 2·r·sin(step/2), which must
    /// clear the thumbnail plus a small gap. Small swarms are unchanged; only a
    /// large one pushes the ring outwards.
    private func orbitArcGeometry(_ total: Int) -> (stepDegrees: Double, radius: CGFloat) {
        guard total > 1 else { return (clusterStepDegrees, overlapRadius) }

        // The ring sits at a FIXED radius that tucks the heads under the speaker,
        // and the fan is capped to a semi-circle over the top. Neither gives way.
        //
        // Earlier versions grew the radius until neighbours cleared each other,
        // which is what pushed the swarm out into a wide, detached ring. Justin's
        // call (2026-08-14): "drones can also overlap when they are swarming
        // behind a speaker" — so crowding is allowed, and the ONLY thing that
        // gives is the angle between them. The speaker holds zIndex(20) and each
        // orbiter is z-ordered behind it, so overlap reads as a pocket of heads
        // behind the speaker rather than a collision.
        let span = maxOrbitSpanDegrees / Double(total - 1)
        return (min(clusterStepDegrees, span), overlapRadius)
    }

    /// The base slot offset for orbit participant `index` of `total`. Two modes:
    ///   • A speaker holds the centre → the ARC orbit above the hub (arriving /
    ///     departing speakers still pass along it).
    ///   • Idle (no speaker) → a SYMMETRIC CLUSTER: the whole swarm squeezes into
    ///     a vertically + horizontally balanced pod centred in the head zone.
    private func slotOffset(index: Int, total: Int) -> CGSize {
        let raw: CGSize
        if speaker != nil {
            let angle = orbitAngle(index: index, total: total)
            let r = orbitArcGeometry(total).radius
            raw = CGSize(width: cos(angle) * r,
                         height: sin(angle) * r + orbitYOffset)
        } else {
            let offs = symmetricClusterOffsets(total)
            raw = index < offs.count ? offs[index] : .zero
        }
        return clampToPanel(raw)
    }

    /// Keep every head inside the panel, whatever the geometry above asks for.
    ///
    /// The head zone is a FIXED frame and nothing else was checking against it:
    /// biasing the idle pod upward (to keep it clear of the subtitle) pushed the
    /// top row straight off the top of the screen. Both layout paths now pass
    /// through here, so a future change to either one cannot put a head outside
    /// the panel — the clamp is the backstop, not the layout's good manners.
    ///
    /// The margin covers half a head plus the lit border and its glow.
    private func clampToPanel(_ o: CGSize) -> CGSize {
        let margin = thumbnailSize / 2 + 8
        let maxX = Self.headZoneWidth / 2 - margin
        let maxY = Self.headZoneHeight / 2 - margin
        return CGSize(width: min(max(o.width, -maxX), maxX),
                      height: min(max(o.height, -maxY), maxY))
    }

    /// Symmetric-cluster slot offsets for the idle swarm, centred on the head
    /// zone. Balanced rows (a horizontal AND a vertical mirror) that adapt to the
    /// live count. Rows are chosen so the MIDDLE is the WIDEST and the top /
    /// bottom taper in — an OVAL/hexagonal blob, not an hourglass "H":
    ///   1:[1]  2:[2]  3:[3]  4:[2,2]  5:[1,3,1]  6:[3,3]  7:[2,3,2]
    /// 8+ compute a 3-row palindrome with the middle row widest (8:[2,4,2],
    /// 9:[3,3,3], 10:[3,4,3]) so a full nine-drone review — Meridian included —
    /// packs without any slot falling off the table into .zero-stacking.
    /// Row counts are a palindrome so the pod mirrors top-to-bottom; each row is
    /// horizontally centred. Slot order follows participant order, so a change in
    /// the live set re-packs the pod symmetrically.
    private func symmetricClusterOffsets(_ total: Int) -> [CGSize] {
        let rows: [Int]
        switch max(total, 0) {
        case 0: return []
        case 1: rows = [1]
        case 2: rows = [2]
        case 3: rows = [3]
        case 4: rows = [2, 2]
        case 5: rows = [1, 3, 1]      // plus/diamond — wide middle, not a pinched X
        case 6: rows = [3, 3]
        case 7: rows = [2, 3, 2]      // hexagon+centre oval
        default:
            let side = max(2, total / 3)
            rows = [side, total - 2 * side, side]
        }
        var offsets: [CGSize] = []
        let rowCount = rows.count
        for (r, count) in rows.enumerated() {
            // Bias the whole pod UPWARD. Rows centred on the hub put a row below
            // it, straight under the subtitle bubble. Shifting up by half the pod
            // keeps every head above the caption line.
            let y = (CGFloat(r) - CGFloat(rowCount - 1) / 2) * clusterSpacing
                  + orbitYOffset - CGFloat(rowCount - 1) * clusterSpacing / 4
            for c in 0..<count {
                let x = (CGFloat(c) - CGFloat(count - 1) / 2) * clusterSpacing
                offsets.append(CGSize(width: x, height: y))
            }
        }
        return offsets
    }
}

// MARK: - Participant slot (single stable-identity view: glides centre ↔ orbit)

/// ONE on-screen element per participant id. It is NEVER two mutually-exclusive
/// branches — instead it layers BOTH representations (the full-size speaker
/// portrait and the small orbit thumbnail) in a single view and cross-fades
/// between them by opacity, while the whole element ANIMATES its offset + scale
/// between the centre and its orbit slot as `isCentre` flips.
///
/// Because the view's identity (`.id(p.id)`) is stable across the centre↔orbit
/// transition, SwiftUI does NOT tear the centre view down and insert a new
/// thumbnail (the old bug — that overlap rendered the SAME character twice, the
/// "multiple Echo"). The same element glides: an outgoing speaker travels
/// centre→its orbit slot while the incoming one travels its slot→centre, and
/// they pass cleanly — the real "matched arc".
///
/// - Centre: full portrait + glow + live lip-sync (amplitude from the speaker),
///   scale 1, offset .zero.
/// - Orbit: the drone thumbnail with its signature drift, scaled to the
///   thumbnail size, offset to its orbit slot.
private struct ParticipantSlotView: View {
    let participant: FloatingHeadsView.Participant
    /// The active speaker snapshot — drives the CENTRE occupant's live amplitude
    /// (lip-sync) and voice label. Only meaningful while `participant.isCentre`.
    let speaker: DashboardViewModel.SpeakerSnapshot?
    /// This participant's orbit-slot offset (arc while a speaker holds the
    /// centre, cluster when idle) — where the thumbnail sits when NOT centre,
    /// and where the element rests/departs to.
    let orbitOffset: CGSize
    let thumbnailSize: CGFloat
    let reduceMotion: Bool
    let portraitManager: PortraitManager
    /// Opens the session the CENTRE speaker is speaking from. nil when there's no
    /// addressable session — the portrait is then inert, as before.
    var openSession: (() -> Void)?
    /// That session's display name, for the portrait's tooltip.
    var sessionName: String?
    /// Pointer entered/left the CENTRE portrait — drives the session nameplate's
    /// hover reveal. Never fired for orbiting participants.
    var onPortraitHover: ((Bool) -> Void)?

    /// Full centre portrait size — ONE definition, shared with the geometry that
    /// positions the ring around it. A private copy here and another in
    /// FloatingHeadsView is how the ring and the speaker drift apart.
    private var centrePortraitSize: CGFloat { FloatingHeadsView.centrePortraitSize }

    private var isCentre: Bool { participant.isCentre }
    private var category: String { participant.category ?? "pulsar" }

    /// The scale the ORBIT representation must be drawn at so, together with the
    /// centre-scale animation, the thumbnail reads at `thumbnailSize`. The centre
    /// portrait is 120pt; when orbiting we scale the whole element down to the
    /// thumbnail's fraction of that.
    private var orbitScale: CGFloat { thumbnailSize / centrePortraitSize }

    var body: some View {
        ZStack {
            // CENTRE representation — full portrait + glow + lip-sync. Faded in
            // only while this participant holds the centre. Rendered at native
            // 120pt; the element scale stays 1 when centre.
            // [FIX 1 — perf] Only run the expensive 60Hz FloatingPortraitView
            // (aura/glow/bob TimelineView) for the centre participant. Orbiting
            // participants are opacity-0 here anyway, so there is no visual change
            // — but previously 7 slots × 60Hz ran simultaneously. Now only the
            // active centre fires; the orbit uses the cheap thumbnail below.
            // [FIX 2 — voiceLabel] Use the participant's OWN identity for the
            // fallback initial rather than the active speaker's label. Without
            // this, all orbit heads show the speaker's initial on portrait
            // fallback, which is wrong even at opacity-0 (it leaks through the
            // crossfade).
            if isCentre {
                let portrait = FloatingPortraitView(
                    voiceName: speaker?.voiceLabel ?? (participant.category?.capitalized ?? "Pulsar"),
                    amplitude: speaker?.amplitude ?? 0,
                    voiceColor: participant.color,
                    portraitManager: portraitManager,
                    droneName: category,
                    glowColor: participant.color
                )
                .allowsHitTesting(true)

                Group {
                    if let openSession {
                        // Click the talking head → its session. A Button rather
                        // than a tap gesture so the panel's move-by-background
                        // doesn't swallow the mouseDown.
                        Button(action: openSession) { portrait }
                            .buttonStyle(.plain)
                            .help(sessionName.map { "Open the “\($0)” session in Claude Code" }
                                  ?? "Open this session in Claude Code")
                    } else {
                        portrait
                    }
                }
                // Hover is tracked over the FACE, not the portrait's full frame —
                // that frame is 230pt to give the glow ripple room, which would
                // arm the reveal across most of the panel. The squircle is 120pt.
                .overlay(
                    HoverTracker { hovering in
                        onPortraitHover?(hovering)
                        if openSession != nil {
                            if hovering { NSCursor.pointingHand.push() } else { NSCursor.pop() }
                        }
                    }
                    .frame(width: centrePortraitSize, height: centrePortraitSize)
                )
                // Explicit opacity transition so the portrait fades in/out cleanly
                // as a participant enters/leaves the centre, matching the thumbnail
                // fade on the orbit layer below.
                .transition(.opacity)
            }

            // ORBIT representation — the drone thumbnail with signature drift.
            // Faded in only while this participant is orbiting. Its own
            // slotOffset is ZEROed here because the CONTAINER carries the offset
            // (so the SAME element glides); the drift still animates locally.
            FloatingDronePortraitView(
                category: category,
                isActiveSpeaker: false,
                liveAmplitude: 0,
                thumbnailSize: centrePortraitSize,   // drawn full then element-scaled
                slotOffset: .zero,
                index: participant.orbitIndex,
                reduceMotion: reduceMotion,
                portraitManager: portraitManager
            )
            .opacity(isCentre ? 0 : 1)
            .allowsHitTesting(!isCentre)
        }
        // Element scale: full at centre, thumbnail-fraction when orbiting. The
        // crossfade above swaps the visible treatment; this scale + the offset
        // below carry the single element between the two footprints.
        .scaleEffect(isCentre ? 1 : orbitScale)
        // Element position: dead-centre when speaking, the orbit slot otherwise.
        // Animated by the ZStack-level springs in `headZone` (keyed on the
        // speaker / activeDroneCategory / participant-list), so the glide is a
        // spring, not a snap.
        .offset(isCentre ? .zero : orbitOffset)
        // A participant genuinely JOINING or LEAVING the swarm (a sub-agent
        // starts / finishes) still animates in/out — but this is entry/exit of
        // the whole element, NOT the centre↔orbit swap, so it can never produce
        // a duplicate of an existing character.
        .transition(.asymmetric(
            insertion: .scale(scale: 0.1).combined(with: .opacity).combined(with: .offset(y: 30)),
            removal: .scale(scale: 0.6).combined(with: .opacity).combined(with: .offset(y: -24))
        ))
    }
}

/// Reports pointer enter/exit for the view it backs.
///
/// SwiftUI's `.onHover` is not dependable here: Pulsar is a background (menu-bar)
/// app and the floating panel is non-activating, so hover has to keep working
/// while another app is frontmost. This uses an explicit `.activeAlways` tracking
/// area, which does. `hitTest` returns nil so the tracker can never intercept a
/// click meant for the button it sits behind.
private struct HoverTracker: NSViewRepresentable {
    let onChange: (Bool) -> Void

    func makeNSView(context: Context) -> TrackingView {
        let view = TrackingView()
        view.onChange = onChange
        return view
    }

    func updateNSView(_ view: TrackingView, context: Context) {
        view.onChange = onChange
    }

    final class TrackingView: NSView {
        var onChange: ((Bool) -> Void)?
        private var area: NSTrackingArea?

        override func updateTrackingAreas() {
            super.updateTrackingAreas()
            if let area { removeTrackingArea(area) }
            let fresh = NSTrackingArea(
                rect: .zero,
                options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect],
                owner: self)
            addTrackingArea(fresh)
            area = fresh
        }

        override func mouseEntered(with event: NSEvent) { onChange?(true) }
        override func mouseExited(with event: NSEvent)  { onChange?(false) }

        /// A pure observer — never a hit-test target.
        override func hitTest(_ point: NSPoint) -> NSView? { nil }

        /// The panel can hide mid-hover (no exit event follows), so drop the
        /// reveal as the view leaves the window rather than leaving it latched.
        override func viewDidMoveToWindow() {
            super.viewDidMoveToWindow()
            if window == nil { onChange?(false) }
        }
    }
}

/// One in-flight sub-agent drone, identified by its agentId, with its category.
private struct DroneInFlight: Identifiable {
    let id: String        // agentId
    let category: String
}

/// Carries the caption's CURRENT (revealed) laid-out height to the controller.
private struct CaptionHeightKey: PreferenceKey {
    static let defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = max(value, nextValue())
    }
}


// MARK: - Queue Bubble

struct QueueBubbleView: View {
    let item: QueueItem
    let index: Int
    let total: Int
    let thumbnailSize: CGFloat
    let orbitRadius: CGFloat
    let orbitYOffset: CGFloat
    let angle: Double
    let voiceColor: Color
    let portraitManager: PortraitManager

    var body: some View {
        TimelineView(.animation) { timeline in
            let time = timeline.date.timeIntervalSinceReferenceDate
            let phase = Double(index) * 1.7
            let bobX = sin(time * 0.9 + phase) * 2.0
            let bobY = cos(time * 0.7 + phase * 0.6) * 1.5

            PortraitView(
                voiceName: item.voice,
                amplitude: 0,
                size: thumbnailSize,
                voiceColor: voiceColor,
                portraitManager: portraitManager,
                // Render the pending line's own drone face (nil agent = Pulsar).
                droneName: item.agent ?? "pulsar"
            )
            .shadow(color: voiceColor.opacity(0.3), radius: 4)
            .scaleEffect(index == 0 ? 1.05 : 1.0)
            .offset(
                x: cos(angle) * orbitRadius + bobX,
                y: sin(angle) * orbitRadius + orbitYOffset + bobY
            )
        }
        .transition(
            .asymmetric(
                insertion: .scale(scale: 0.1)
                    .combined(with: .opacity)
                    .combined(with: .offset(y: 30)),
                removal: .scale(scale: 1.4)
                    .combined(with: .opacity)
                    .combined(with: .offset(y: -60))
            )
        )
    }
}
