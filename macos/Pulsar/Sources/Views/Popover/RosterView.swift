import AppKit
import SwiftUI

/// "Meet the team" — the full cast of Pulsar + his sub-agent drones. Each entry
/// shows the character's portrait (its `<name>-mouth-0` frame), NAME · ROLE, its
/// signature colour, and a one-line description of what it does. Names, roles,
/// and colours come from `DroneRegistry`; Pulsar (the Orchestrator) is prepended
/// since he isn't a drone in the registry.
struct RosterView: View {
    /// One roster row's data — portrait key, display name, role, colour, blurb.
    private struct CastMember: Identifiable {
        let id: String        // portrait/frame prefix, e.g. "pulsar", "voyager"
        let name: String
        let role: String
        let color: Color
        let blurb: String
    }

    /// Pulsar first (Chief of Staff, indigo), then the drones from the
    /// registry in canonical order. Blurbs describe each character's job.
    private var cast: [CastMember] {
        var out: [CastMember] = [
            CastMember(id: "pulsar", name: "Pulsar", role: "Chief of Staff",
                       color: .orbitLight,
                       blurb: "Runs the show — plans the work, delegates, and narrates the session.")
        ]
        let blurbs: [String: String] = [
            "voyager":  "Gets the data out — searches the code, follows the pipelines, reports what's there.",
            "sentinel": "Checks the numbers — audits, catches bugs and security holes, tests every claim.",
            "nova":     "Ships it — implements features, refactors, and gets the code compiling.",
            "nebula":   "Makes it look right — design, images, icons, and visual polish.",
            "echo":     "Finds the words — docs, changelogs, copy, and clear prose.",
            "atlas":    "Fixes whatever's broken — the one who picks up the job nobody else has time for.",
            "iris":     "Runs marketing — brand, paid media, search, SEO, content, and the full lifecycle.",
            "meridian": "Keeps it defensible — legal, compliance, licences, and where the exposure hides.",
            "vector":   "Decides what gets built — and, more often, what doesn't.",
        ]
        // `unknown` is an internal fallback for rendering an unrecognised agent in
        // the swarm — NOT a showcased team member. Keep it out of "Meet the team".
        // `pulsar` is prepended above with his own copy, and he is now ALSO a real
        // DroneRegistry entry (he became spawnable), so looping the registry
        // without excluding him listed him twice.
        // Ordered by seniority, not by registry order (which is a colour/motion
        // list and says nothing about the org). Pulsar is prepended above as Chief
        // of Staff; the rest run leadership → product → engineering → design →
        // go-to-market, with counsel last as the specialist who is consulted rather
        // than staffed on the work.
        let seniority = ["meridian", "vector", "sentinel", "voyager", "nova",
                         "atlas", "nebula", "iris", "echo"]
        let ranked = DroneRegistry.drones
            .filter { $0.category != "unknown" && $0.category != "pulsar" }
            .sorted { a, b in
                let ia = seniority.firstIndex(of: a.category) ?? seniority.count
                let ib = seniority.firstIndex(of: b.category) ?? seniority.count
                return ia == ib ? a.category < b.category : ia < ib
            }
        for drone in ranked {
            out.append(CastMember(
                id: drone.category,
                name: drone.category.capitalized,
                // `role` is now a real job title, already correctly cased —
                // `.capitalized` here would render "IT Support" as "It Support".
                role: drone.role,
                color: drone.color,
                blurb: blurbs[drone.category] ?? ""))
        }
        return out
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 10) {
                Text("MEET THE TEAM")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .tracking(0.5)
                    .padding(.horizontal, 4)

                // The cast is fictional, and the app says so BEFORE the faces —
                // above the fold on the default tab, at .secondary weight. First
                // placement put it after nine cards at .tertiary/.caption2, i.e.
                // three scrolls down in the lowest-contrast style in the app: the
                // one string whose job is "these aren't real people" was the
                // least readable text on screen (caught the same cycle it landed).
                Text("Invented characters — names, voices and faces given to "
                     + "sub-agents so you can tell the work apart. None is a real "
                     + "person.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.horizontal, 4)
                    .padding(.bottom, 2)

                ForEach(cast) { member in
                    row(member)
                }
            }
            .padding(16)
        }
    }

    @ViewBuilder
    private func row(_ member: CastMember) -> some View {
        HStack(alignment: .top, spacing: 12) {
            portrait(member)

            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 6) {
                    Text(member.name.uppercased())
                        .font(.system(size: 12, weight: .bold, design: .rounded))
                        .tracking(0.6)
                        .foregroundStyle(.primary)
                    Text("·")
                        .foregroundStyle(.tertiary)
                    Text(member.role.uppercased())
                        .font(.system(size: 10.5, weight: .semibold, design: .rounded))
                        .tracking(0.8)
                        // Not the raw accent: it is the only channel carrying this
                        // label and six of ten accents fail WCAG on this surface.
                        .foregroundStyle(member.color.legible(on: .textBackgroundColor))
                }
                Text(member.blurb)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    // Two lines, always: rows must stay the same height or the
                    // roster reads as ragged. The copy above is written to fit,
                    // and this stops a future edit silently pushing a row taller.
                    .lineLimit(2)
                    .truncationMode(.tail)
                    .fixedSize(horizontal: false, vertical: true)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .padding(10)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(member.color.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .strokeBorder(member.color.opacity(0.25), lineWidth: 1)
                )
        )
    }

    /// The character's portrait, clipped to the same squircle the floating head
    /// uses, with its signature colour glow. Falls back to a coloured monogram if
    /// the frame image is missing.
    @ViewBuilder
    private func portrait(_ member: CastMember) -> some View {
        let size: CGFloat = 46
        let squircle = RoundedRectangle(cornerRadius: size * 0.22, style: .continuous)
        Group {
            if let img = NSImage(named: "\(member.id)-mouth-0") {
                Image(nsImage: img)
                    .resizable()
                    .interpolation(.high)
                    .aspectRatio(contentMode: .fill)
            } else {
                squircle
                    .fill(member.color.opacity(0.3))
                    .overlay(
                        Text(String(member.name.prefix(1)))
                            .font(.system(size: size * 0.4, weight: .bold))
                            .foregroundStyle(member.color)
                    )
            }
        }
        .frame(width: size, height: size)
        .clipShape(squircle)
        .overlay(squircle.strokeBorder(member.color.opacity(0.6), lineWidth: 1.5))
        .shadow(color: member.color.opacity(0.5), radius: 6)
    }
}
