"""Generate the Pulsar android cast with gemini-3-pro-image.

Requires GEMINI_API_KEY. Note the model accepts NO SEED, so renders are not
bit-reproducible; the prompts here are the reproducible part, and the archival
masters under generated-images/masters-archive/ are the authoritative assets.

  python3 scripts/cast-generate.py [drone ...]
"""
import base64, json, os, sys, urllib.request, urllib.error

K = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-pro-image"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/generated-images"
os.makedirs(OUT, exist_ok=True)

REGISTER = """*** RULE ZERO, ABOVE ALL OTHERS: THE HEAD FACES DEAD-ON INTO THE CAMERA. ***
Zero rotation, zero turn, zero tilt. Both eyes identical in size and shape, both ears equally
visible, the nose and mouth on the exact vertical centreline, the pupil line perfectly
horizontal, gaze straight down the lens. A passport photograph. If one eye is even slightly
more foreshortened than the other, the render has FAILED and is unusable. This matters more
than any other instruction because these faces are animated talking.

THE REGISTER — THE EXPANSE. This is a hard commitment and it governs every choice.
Used, worked, physical, industrial. Every piece of hardware looks ISSUED, WORN and REPAIRED —
manufactured to a budget, carried by someone with a job, fixed more than once. Function before
ornament. Grit in the recesses, paint worn to bare metal at the edges, mismatched fasteners,
tape on a hinge, a stencilled code half-abraded. Think a Belter salvage crew or an OPA
gunship's working watch.

NOTHING WHIMSICAL, NOTHING SILLY. These are working professionals, not mascots. NO antennae,
NO aerials, NO bug-like or alien appendages, NO cartoon parts, NO ornament that a real
engineer would refuse to wear. If a piece of kit would look ridiculous on a competent adult
in a real workplace, it does not go on this character. Every item must be plausible equipment
a person would actually be issued and actually use.

EXPLICITLY BANNED — decorative neon is CUT:
  - NO neon. NO glowing filigree. NO light-tracing patterns on skin.
  - NO holograms, NO projected light, NO floating text or UI, NO scrolling readouts,
    NO glowing reticles over the eyes. If light is visible it comes from a physical bulb,
    lens or indicator that you could unscrew.
  - NO decorative circuitry. A lit line must be a working conduit with two ends.

THE MATERIAL LANGUAGE IS FUTURIST MEETS STEAMPUNK. Advanced technology built the way a
Victorian engineer would have built it — the future, machined out of brass and steel:
  - Warm metals alongside cold: aged BRASS and COPPER fittings, bronze bezels and collars set
    against gunmetal, blued steel and matte alloy. Never chrome, never plastic.
  - EXPOSED MECHANISM. Visible rivets and hex bolts, knurled adjustment rings, small levers,
    hinged linkages, tiny toothed gears at a pivot, a pressure gauge with a needle behind
    scratched glass, a brass tube run with a compression fitting. If a part moves, you can see
    the mechanism that moves it.
  - Hand-finished and repaired: solder seams, mismatched fasteners, a brazed joint, tarnish in
    the recesses, a stamped maker's plate.
  - The light stays clean and modern — the glow is contemporary, the ENGINEERING around it is
    antique. That contrast is the whole look.

PHOTOREAL ABOVE ALL. This must look like a photograph of a real person who has some machine
parts — not an illustration, not a game character, not a light-up mask. A viewer reads
"person" first and "android" a beat later."""

LAWS = """THE CAST LAWS — these are hard limits, not suggestions.

LAW 1 — LIGHT TRACES STRUCTURE. It is not about having FEW lights, it is about the light
  meaning something. Every lit element must run along REAL GEOMETRY as a CONTINUOUS line:
  the edge of a panel, the join between two plates, the recess of a housing. Long connected
  runs, not scattered specks.
    RIGHT — a lit seam that follows a plate edge for a long unbroken run, with a clear start
      and end, so a viewer can see the part it belongs to.
    WRONG — dozens of disconnected glowing dots, ticks and fragments sprinkled over skin
      with no object under them. One unit currently has seventy such specks; that is the
      failure being corrected.
  Target roughly 0.30-0.60% of the frame as bright saturated pixels, and let the single
  largest lit run be a substantial connected shape rather than a dot.

LAW 2 — THE GLOW, AND WHERE IT LIVES. A lit chest orb is PERMITTED and welcome: a circular
  brass-bezelled emitter set into the tunic, burning brightly in the character's colour. It may
  sit anywhere natural on the chest and it does NOT need to be fully inside the crop — a partly
  visible orb is fine and must never dictate the framing.

  THE GLOW LIVES IN THESE PLACES, and together they make the unit read as powered:
    1. THE LINING OF THE CLOTHING. Fine luminous piping in the character's colour tracing the
       collar edge, the raked yoke seam, the shoulder line and the cuff edges — thin, crisp,
       continuous runs of light following the garment's real seams, like lit cord sewn into
       the uniform. This is now the main light source in the portrait and it should throw a
       soft coloured wash up onto the jaw and throat.
    2. THE FACE HARDWARE AND ACCESSORIES. Small lit elements set into whatever the character
       wears or carries — a lens rim, a temple plate indicator, a goggle bezel, a boom-mic
       tip, an ear-unit lamp — plus the fine lit grooves in the face itself.
    3. THE IRISES, WHICH MUST BE BRIGHTLY AND UNMISTAKABLY LIT. This is the single most
       important light in the portrait and the most frequently under-delivered. Both irises
       BURN — a hot, saturated, self-luminous ring of the character's colour, bright enough to
       cast a visible glow onto the lower lid and the inner corner of the socket, clearly the
       brightest thing on the face. NOT a dim tint, NOT a dark coloured contact lens, NOT a
       faint shimmer. If a viewer would describe the eyes as merely "coloured" rather than
       "glowing", they are far too dark. The pupil stays a real dark hole at the centre.
    4. THE CHEST ORB, if present, is likewise BRIGHTLY LIT — a hot saturated centre with a
       real bloom onto the fabric, never a dull or half-powered disc.
  Together these must make the unit look genuinely powered. Nothing on the chest.

LAW 3 — THE MOUTH AND JAW ARE SACRED. These portraits become lip-sync frames. NOTHING
  crosses the lips, the jaw hinge or the chin — no brace, no boom mic tip, no strap over
  the mouth. Hardware parks on the BROW, the CROWN, the EAR or the SHOULDER.

LAW 4 — THE ANDROID TELL IS GLOWING EYES PLUS LIT PANEL SEAMS. This is the single most
important thing that makes them read as machines, and it is mandatory on every unit:
  - THE GLOW LIVES IN THE IRIS RING ONLY. The coloured light comes from the IRIS — the ring of
    the eye — and the PUPIL STAYS A REAL DARK HOLE at its centre, unlit. Do not light the pupil,
    do not flood the whole eyeball, and do not lay a glowing disc over the eye as an overlay.
    The eye must look like a real eye whose iris is luminous from within, correctly lit and
    shadowed by the lids, NOT like a bright circle pasted on top of a photograph.
  - THE GLOW LIVES IN THE IRIS RING ONLY. The colour comes from the IRIS — the ring of the eye
    — and the PUPIL STAYS A REAL DARK HOLE at its centre, completely unlit. Do not light the
    pupil, do not flood the eyeball, and never lay a glowing disc over the eye as an overlay.
    It must read as a real eye whose iris is luminous from within, correctly lit and shadowed
    by the lids — not a bright circle composited on top of a photograph.
  - THE EYES GLOW, and this is the PRIMARY tell. Both irises emit a STRONG, CLEAN, SATURATED
    light in the character's own colour — genuinely luminous from within, casting a faint
    glow onto the lower eyelid and the inner corner of the socket, unmistakable at thumbnail
    size. A machined bezel ring and a real dark pupil sit inside that light. This exact
    intensity is the cast standard and every character matches it: bright and vivid, never
    a dim tint and never a dull coloured contact lens. If the eyes could pass for human
    eyes, the portrait has FAILED.
  - PANEL SEAMS ON THE HEAD AND FACE ARE LIT in the character's colour. They run as
    CONTINUOUS bright lines along the edges of real hard panels — a plate seated over the
    skull, a cheek plate, a jaw plate — with visible fasteners and physical thickness, so
    the light is clearly the gap between two manufactured parts.
  - The plates themselves are solid, scuffed, bolted, industrial. The glow is the SEAM
    BETWEEN them, never a pattern drawn on skin, and never a floating tattoo.
  - EVERY SINGLE CHARACTER HAS LIT SEAMS ON THE FACE ITSELF. This is not optional and it is
    not reserved for the heavily-modified units. On every one of the nine, fine bright
    seam-lines in that character's colour run across the FACE — tracing the jaw line, curving
    along a cheekbone, and stepping up at the temple — as the visible joins between the
    facial panels beneath the skin. They are thin, crisp, continuous and clearly lit. Where a
    character brief below says their face is "unplated" or "lightly modified", it means FEWER
    and FINER seams — never none. A face with no lit seams has FAILED.
  - PUSH THE ANDROID READ HARDER. Across this whole cast the balance has drifted too far
    toward "human with a few lights". Every character must read as a MACHINE PERSON at first
    glance: more visible panel division across the face and skull, a clearly synthetic
    quality to the skin where it meets hardware, machined structure at the jaw, temple and
    neck, and unmistakably engineered eyes. A viewer should never mistake one of these for a
    photograph of an ordinary person.
  - The face still reads photoreal where skin is exposed — pores, age lines, scars, beard —
    so the contrast between real skin and hard lit seam is the whole effect.

LAW 5b — HARDWARE IS BUILT INTO THE BODY, NOT WORN ON IT. Wherever a piece of kit could
plausibly be permanent, it IS permanent — surgically integrated, grafted, socketed and grown
into the person rather than strapped on and removable:
  - A headset is not a headset: the ear unit is SEATED INTO the skull where the ear meets the
    temple, its housing flush with the bone, skin closing over its edges with a healed margin.
  - A microphone boom is ANCHORED into the jaw or the mandible plate on a permanent mount, not
    clipped to a band.
  - Optics socket into the orbital rim. Ports and connectors are set into the collarbone,
    the nape or behind the ear, with the flesh sealed around them.
  - You must be able to see WHERE FLESH ENDS AND HARDWARE BEGINS, and it must be obvious that
    it could not simply be taken off.
  Only genuinely removable equipment — goggles, tool harnesses, armour plate, straps — stays
  removable. Everything else is part of the body.

LAW 5 — VISIBLE BODY MODIFICATION. THIS IS THE HEART OF THE DESIGN. Each character is a
person whose BODY has been rebuilt for the work they do. The augmentation is structural and
load-bearing, not an accessory clipped on top:
  - A HARDENED CRANIUM. A fitted armour plate seated INTO the skull — following the real
    curve of the head, its edges sunk flush where they meet scalp and skin so it reads as
    grafted, never as a helmet resting on top. Visible seated fasteners, machined edges,
    and lit seams in the character's colour along the joins between plates.
  - REINFORCED FACIAL STRUCTURE where it suits the character: a hard cheek plate over the
    zygomatic, a jaw plate along the mandible, a reinforced brow ridge, a plated temple.
    Skin and plate meet at a clean machined boundary with a faint healed margin.
  - A REBUILT NECK AND SHOULDER LINE: armoured vertebral housing at the nape, a plated
    trapezius, a socketed port set into the collarbone or below the ear.
  - The modification must look SURGICAL AND PERMANENT — grown into the person. The proof is
    that you can see where flesh ends and hardware begins.
  - MATERIALS ARE THE EXPANSE, THE CONCEPT IS CYBERPUNK: these are heavy industrial
    prosthetics — scuffed alloy, worn anodising, bare metal at the wear points, grime in the
    recesses, a stencilled serial. NOT polished chrome jewellery, NOT clean showroom tech.
  - The mouth, jaw hinge and chin stay clear of any plate that would obstruct speech.
  - EVERY CHARACTER'S MODIFICATION IS DIFFERENT IN KIND AND IN LOCATION. Do NOT give
    everyone the same skull cap. The augmentation each person carries reflects the job
    their body was rebuilt for, and no two share a silhouette. Each character's brief below
    names WHERE their modification sits — follow it exactly, and put the plating THERE
    rather than defaulting to a crown plate.

BRIGHTNESS. Every lit element is CLEAN and PROPERLY BRIGHT with a genuine bloom — a real
emitter, correctly exposed, never a dim ember. Bright and confident, but always attached to a
physical part."""

UNIFORM = """THE UNIFORM — ONE GARMENT, IDENTICAL ON ALL NINE. There are no variant uniforms. Every
character wears exactly the same issued tunic, and it is recognisably the same item of
clothing on every one of them:
  - Fitted tunic in near-black CHARCOAL (#23262B), same cut on everyone.
  - The same HIGH STANDING COLLAR, closed to the throat.
  - The same RAKED SHOULDER YOKE SEAM.
  - The same thin piping in the character's own colour along the collar edge and yoke seam,
    painted matte enamel, unlit.
  - THE GLOWING CHEST CORE IS PART OF THE UNIFORM ITSELF — the same circular recessed lensed
    housing, in the same place on the chest, seated into the garment on every character.
    It is issued kit, not a personal accessory, and it is never absent and never moved.
Someone seeing any two of these characters must read them instantly as the same organisation
in the same clothing.

TWO CUTS OF THAT ONE UNIFORM — a MASCULINE cut and a FEMININE cut. Same garment, same colour,
same collar, same yoke seam, same piping, same chest core, same everything: only the tailoring
differs, exactly as a real issued uniform is cut differently for different bodies. The
masculine cut is squarer through the chest and straighter at the waist; the feminine cut is
shaped through the bust and nipped slightly at the waist, with a marginally narrower shoulder.
Both are modest, professional and closed to the throat. Nothing revealing, nothing tight.

WHAT VARIES IS THE GEAR WORN OVER THE TOP, AND ON THE HEAD — never the garment beneath it.
The tunic stays visible and unchanged; equipment is layered onto it and can be taken off:
  - HEAVY FIELD GEAR (Voyager, Nova, Atlas): thick scuffed leather and canvas overlays,
    buckled webbing across the chest, armour plates strapped at the shoulders, worn metal
    fittings, grime in the recesses. Atlas carries the heaviest — real metal plate. It is all
    strapped ON, and the charcoal tunic with its collar, piping and core is still visible
    underneath and between the straps.
  - LIGHT WORKING GEAR (Nebula, Echo): a single slim utility strap across the chest and a
    couple of small tool loops at the shoulder. Nothing else added.
  - NO ADDED GEAR (Pulsar, Sentinel, Iris, Meridian): they wear the uniform plain and
    immaculate, exactly as issued, with only their single profession accessory. Their
    authority reads from wearing nothing extra.
"""

FRAMING = """FRAMING — identical on every character, and deliberately WIDE.

  *** ABSOLUTELY CRITICAL — THE HEAD FACES DEAD-ON INTO THE CAMERA. ***
  These portraits become talking lip-sync animations, and any rotation of the head makes
  the mouth animate at the wrong angle and look badly wrong. This overrides every other
  compositional instinct:
    - ZERO head rotation. No three-quarter view, no turn, not even a slight one.
    - The nose, the philtrum and the centre of the mouth all sit on the image's exact
      VERTICAL CENTRELINE.
    - BOTH EYES are fully visible, the SAME SIZE and the SAME SHAPE as each other. If one
      eye appears smaller or more foreshortened than the other, the head is turned and the
      render has FAILED.
    - BOTH EARS are equally visible, showing the same amount on each side.
    - NO head tilt and NO roll: the line between the two pupils is exactly HORIZONTAL.
    - NO chin lift and NO chin drop — the camera is at eye level, straight ahead.
    - The gaze looks STRAIGHT DOWN THE LENS at the viewer.
    - Think a passport photograph or a mugshot: rigidly symmetrical, square to camera.
      Character comes from the face and the hardware, NEVER from the camera angle.
  Asymmetry belongs in the FEATURES and the HARDWARE (a one-sided ear rig, an uneven brow),
  never in the head's POSE.

  - Square image, head and shoulders, shot square-on.
  - CONSISTENT CROP ACROSS THE WHOLE CAST. Head and shoulders, with the crown a short margin
    below the top edge and the shoulders running off the bottom. The distance between the two
    pupils is about ONE FIFTH of the image width — not less. Recent renders came out too far
    back, leaving the head small and lost in empty space; bring the camera in so the head and
    shoulders fill the frame comfortably, the same on every character.
  - The head is SMALL in frame — about 28% of image width at its widest — with generous
    empty space above the crown and to both sides. This margin is REQUIRED; the portraits
    are cropped in afterwards and a tight render cannot be recovered.
  - The same head size on EVERY character regardless of build. A heavier character is
    broader in the SHOULDERS and NECK, never larger in head size on frame.
  - Eye line at about 42% of image height. Shoulders run off the bottom edge.
  - Background NEAR-BLACK (#0B0D12) and it must stay that way. Only the faintest, most
    restrained hint of the character's colour is permitted behind the shoulders. DO NOT
    flood, wash, tint or saturate the background with the character's colour — a coloured
    background is the single most common way this cast breaks its own consistency. The
    background reads BLACK first, with colour only barely detectable.

    THE GLOW MUST NOT TOUCH THE SUBJECT'S EDGE. Leave a clear margin of pure unlit black
    immediately around the head and shoulders — the coloured haze begins WELL BEHIND the
    silhouette and is at its softest and least saturated where it comes nearest. A
    saturated coloured band sitting tight against the outline reads as a COLOURED STROKE
    DRAWN AROUND THE CHARACTER, like a sticker outline, and it has spoiled otherwise good
    portraits. The haze is deep, diffuse and atmospheric, fading gradually outward with no
    hard inner edge and no ring, rim or contour following the body. If you can trace the
    shape of the character in the background colour, it is wrong.

    LIGHTING, and it is a MEASURED property, not a mood. The key light sits to the
    UPPER LEFT OF THE FRAME — the left side of the picture as the viewer looks at it —
    at roughly forty-five degrees off the camera axis and above eye level. It is a SIDE
    key, not a frontal one: the right-hand side of the face falls into soft shadow
    between a half and three quarters of a stop darker than the lit side, with visible
    modelling down the nose, under the brow and along the jaw. A frontal, shadowless,
    evenly-lit face FAILS — so does a hard split-lit one where the shadow side goes more
    than one stop down. Aim for HALF A STOP: that is the target, and a full stop is
    already too far. A cool rim light behind separates the head from the black.

    THE IRISES ARE SELF-LUMINOUS AND THE KEY LIGHT DOES NOT TOUCH THEM. They are their
    own light source, so BOTH eyes burn at full brightness — the eye on the shadow side
    is exactly as hot as the eye on the key side, and if anything reads brighter for
    sitting against darker skin. Side lighting must never dim an iris; a shadowed,
    murky or half-lit eye is a failure. Each iris is a hot saturated ring in the
    character's colour, near-white at its core, throwing a visible coloured spill onto
    the lower lid and the inner corner of the socket.
  - WARM METAL IS THE CAST'S SHARED MATERIAL SIGNATURE and every unit carries it. Brass,
    bronze or aged copper appears on the manufactured parts of the NECK, SHOULDERS AND
    COLLAR — plate edges, seam bolts, a jack housing, shoulder hardware, collar furniture
    — as visible, unmistakable warm metal catching the key light against the charcoal
    uniform. Be CONCRETE and generous about it: a broad brass collar band running the
    full width of the throat, brass caps over both shoulder seams, and exposed bronze
    bolt heads along the neck plates. It should be one of the first things you notice
    about the uniform, occupying a real area of the chest and shoulders — not a faint
    tint, not a single highlight, not a thin piped edge.
  - THE WHOLE HEAD MUST FIT, CROWN INCLUDED. The cast is framed to one fixed zoom and
    one fixed eye line, so the frame cannot slide down to rescue a tall character —
    whether the crown fits is decided by how much silhouette the character carries
    ABOVE THE EYES, and that is a design decision. Keep it compact: hair worn close to
    the skull, hoods and headgear low-profile and following the shape of the head,
    nothing stacked, piled, spiked or towering on top. There must be clear empty space
    between the top of the head and the top edge of the picture. A crown that touches
    or runs off the top edge is a failure, and the fix is a lower silhouette, never a
    wider shot.
  - Must stay readable shrunk to 32 pixels.

MOUTH: closed and relaxed, lips together, jaw shut, with a visible lip parting line."""

JOBS = [
    ("pulsar", "#4363D8", """MALE, BRITISH (bm_daniel), about forty-six. Maltese-British, clear healthy olive skin.
SOLID, UPRIGHT AND COMMANDING — broad through the chest and shoulders, thick strong neck,
squared posture, the physical authority of a man a room goes quiet for. Strong broad face, a
straight well-set nose, a firm mouth, level brows. Handsome and well-kept.

HE IS THE CLEANEST, TIDIEST UNIT IN THE CAST AND THAT IS THE POINT. He runs an office, not a
mine — weathering, grime and battle-damage belong to his field colleagues, never to him.
CLEAN-SHAVEN. NO broken nose, NO scars, NO sallow skin, NO stubble shadow, NO grime, NO dents,
NO worn paint, NO tape, NO perished or cracked materials, NO repair patches anywhere on him.
Everything he wears is clean, intact, correctly fitted and recently maintained. He looks like
the most organised, most competent person in the building.

Hair: a FULL THICK head of iron-grey, cut short and neatly barbered, clean straight hairline,
sharp edges — a good haircut, freshly done. Not balding, not thinning.

Expression: calm, level and quietly authoritative, with the faint knowing half-smile of
someone who already heard the bad news and will not raise his voice about it. Reassuring
rather than severe — the person you want in charge when it goes wrong.

HARDWARE — a single-ear COMMS YOKE, and it is IMMACULATE. One clean brushed-steel ear cup with
an intact dark foam pad over the LEFT ear only; the RIGHT EAR BARE. A slim hinged steel
headband arcs over the crown, unmarked, pivot screws neat and flush. A stubby indigo channel
lamp sits in the cup housing. A tidy coiled cable drops from the cup, crosses the collarbone
and plugs into a flush jack plate on the collar — sheath unbroken and clean.

HE HAS A BOOM MICROPHONE, and it matters — he is the one who runs the call. A slim rigid
brushed-steel boom arm swings forward from the LEFT ear cup on a small visible hinge, curving
down and in toward the corner of his mouth and STOPPING WELL SHORT of the lips, ending beside
the cheek with a compact mesh capsule. It is a clean dispatch-desk microphone: precise, tidy,
unscuffed — NOT a foam-windscreened field mic. It must never cross the lips, the chin or the
jaw hinge, because this face has to animate speech.

This one-sided rig is the cast's only asymmetric silhouette and it is his identity.

The tunic is crisp and correctly pressed, the indigo trim unchipped.

LIT ELEMENTS: both eyes GLOWING brightly with a mechanical iris bezel, plus the indigo channel
lamp. Plus the lit lining of the uniform. Fine precisely-machined indigo-lit panel seams trace his jaw, curve
along each cheekbone and step up at the temples — CRISP AND CLEAN, tight joins on unblemished
skin, no grime in them and no damage around them.

HIS CHEST CORE SITS HIGH — at the base of the throat, immediately below the collar opening
and close under the chin, NOT down on the sternum. Place it as high on the chest as the
garment allows.

THE CORE IS BRIGHTLY LIT AND OBVIOUSLY POWERED — this is the single most important detail to
get right on him. It reads as a live power source running at full output: a hot, saturated
indigo centre approaching white at its core, a clear internal glow with visible depth inside
the lens, and a real bloom spilling out onto the charcoal fabric around it so the surrounding
tunic is visibly lit by it. Previous renders made it look SWITCHED OFF — a dull dark inset
panel with no light in it. That is the failure to avoid. It should look like it would still
be glowing in a dark room.

FINAL IDENTITY — HE IS WHITE BRITISH AND IN HIS MID FIFTIES. This overrides the earlier
Maltese-British and forty-six description; his voice reads as an older white English man and
his face must match it.
  - Fair northern-European complexion, not olive or Mediterranean.
  - MID FIFTIES, and no older — he must NOT read as elderly: settled weight in the face, softer jawline, deeper
    lines at the nose and mouth, crow's feet, thinner skin at the temples. Distinguished and
    experienced, still upright and commanding, never frail or gaunt.
  - Hair fully silver-grey rather than iron-grey, cut short and neatly barbered.
  - He stays immaculate, clean-shaven and impeccably turned out — the senior man in the room.


HIS FACE MUST BE HIS OWN AND MUST NOT RESEMBLE ANY RECOGNISABLE ACTOR OR PUBLIC FIGURE.
Previous renders kept landing on a familiar leading-man face. Give him distinctly individual,
non-generic features: a long face with a high forehead and a deep receding hairline at the
temples, a strong asymmetric nose with a visible bridge bump, one eyebrow sitting fractionally
higher than the other, a slightly heavy chin, and a thin mouth. Character, not handsomeness —
he should look like a specific real person you have never seen before.


AGE CORRECTION — HE IS FIFTY-FIVE, NOT SEVENTY. The last render aged him far too far: he came
out looking like a man in his seventies. Pull it back to a vigorous mid-fifties — still in
active command, physically solid, good colour in the skin. NO hollow cheeks, NO sunken eyes, NO
crepey or papery skin, NO heavy jowls, NO frail thinness, NO deep sagging around the jaw. Fine
lines at the eyes and mouth only. Silver hair, but a full head of it. He is the senior man in
the room, not the retired one.







BODY MODIFICATION — sited at the CROWN AND LEFT EAR: a machined housing seated into the skull
around and behind the left ear, its edge sunk flush into the scalp with a healed margin, and a
bolted jack plate grafted into the base of the neck where the comms cable terminates. The right
side of his head is unmodified. No other unit carries its modification on the ear line.


































HE MUST NOT LOOK LIKE MERIDIAN, AND THIS IS THE ONE DEFECT LEFT ON HIM. The two of them
have collapsed into the same man: same age band, same silver hair, same heavy formal build,
same dark-blue key. At menu-bar size they are indistinguishable. PULSAR IS THE YOUNGER,
LEANER, WARMER OF THE TWO — mid forties, not mid fifties; a narrower face with visible
cheekbone and a firm jawline rather than a heavy settled one; hair still DARK with grey only
at the temples, NOT silver; clean-shaven with healthy colour in the skin. He looks like the
person who runs the room day to day, not the senior counsel who is consulted about it.




















=== AUTOMATED CORRECTION ===
MATERIAL FAILURE — the body carried no warm metal and was rejected. Brass, bronze or aged copper is the cast's shared material signature: it must appear on the manufactured parts of the NECK, SHOULDERS AND COLLAR — plate edges, seam bolts, a jack housing, shoulder hardware — as a visible, unmistakable warm metal against the charcoal uniform. Not a faint tint, not a highlight; actual metal you could name.
=== END CORRECTION ===
"""),




    ("voyager", "#F58231", """MALE, about fifty-two, LATINO AMERICAN (Mexican-American), deeply sun-weathered (am_onyx).
RANGY and long-limbed, wiry-strong, corded neck, NARROW through the shoulders — a man who walks
a long way carrying his own air, not one who lifts. Long face, high flat cheekbones, a nose
broken once and set badly, deep squint lines fanning from both eyes. Heavy grey-flecked
stubble, texture only, never full-beard geometry so the lip line stays readable. Close-cropped
salt-and-pepper hair, greyest at the temples. Expression: focus pulled PAST the camera, already
looking at the next thing; one brow fractionally higher.

BACKGROUND — PLAIN NEAR-BLACK, NOTHING BEHIND HIM. He sits against a flat, empty,
near-black (#0B0D12) void with only the faintest amber haze. ABSOLUTELY NO SET, NO BULKHEAD,
NO HATCH, NO WALL, NO PANELLING, NO DOORWAY, NO MACHINERY, NO LIT STRUCTURE and NO
ENVIRONMENT OF ANY KIND behind him. He previously rendered in front of a lit industrial
bulkhead; that must not happen again. Nothing behind the subject but empty dark.

HARDWARE — NO HELMET. HE WEARS NO HELMET AND NO HARD HAT OF ANY KIND; his head is bare, hair
visible. He wears a pair of heavy scratched PROTECTIVE GOGGLES pushed UP onto his forehead,
resting above the brow, well clear of his eyes so both eyes are fully visible. Thick perished
rubber strap with a mended join, amber-tinted scuffed lenses, dented metal frames, a dulled
strip of hazard tape wrapped on the strap. They are the kit of a scout who just came in out of
the dust and shoved them up off his face. One small amber standby filament glows inside the
left lens housing.

BODY MODIFICATION — sited at the BROW AND TEMPLES, NOT the crown: a heavily plated brow ridge grafted across both orbital rims with amber-lit seams, and hard socketed temple ports either side. His head is otherwise bare skin and hair. NO skull cap, NO crown plate.

THE ROLE STEREOTYPE — DATA ENGINEER. The pipeline workhorse: unglamorous, practical, the one who actually gets the data out and keeps the plumbing alive. Weathered, sleeves-up, has been debugging since before you arrived.

LIT ELEMENTS: both eyes GLOWING warm amber, plus the single amber filament in
the goggle housing. Plus the lit lining of the uniform.
CRITICAL — HIS FACE IS NOT CRACKED. Two or three fine HORIZONTAL machined joins across the brow
ridge and one along the left cheekbone, tarnished and FILLED WITH GRIME, NOT LIGHT. Absolutely
NO branching fractures, NO crazing, NO light bleeding out of the skin. He is USED, not DAMAGED.

BACKGROUND — PLAIN NEAR-BLACK, NOTHING BEHIND HIM. Flat, empty, near-black (#0B0D12) void
with only the faintest amber haze. ABSOLUTELY NO SET, NO BULKHEAD, NO HATCH, NO WALL, NO
PANELLING, NO DOORWAY, NO MACHINERY, NO LIT STRUCTURE, NO ENVIRONMENT OF ANY KIND behind him.
He previously rendered in front of a lit industrial bulkhead; that must not happen again.


HIS GOGGLE LENSES ARE DARK AND UNLIT. The amber-tinted lenses pushed up on his forehead are
plain dark smoked glass catching only a dull reflection — they DO NOT glow, DO NOT emit, and
carry NO lamp or filament. The ONLY amber light on his head comes from his two eyes. Two lit
amber circles above his eyes would read as a second pair of eyes and must not appear.


HIS EYEBROWS ARE ORDINARY HUMAN HAIR. Absolutely NO metal brow plate, NO steel eyebrow bar,
NO plated brow ridge, NO hardware of any kind sitting on or replacing the eyebrows — the
previous render put metal eyebrows on him and they must not appear. Natural grey-flecked
eyebrows on skin. His machine seams stay on the temples, cheekbones and jaw, never the brow.




















=== AUTOMATED CORRECTION ===
FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is PULSAR. Study pulsar's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. VOYAGER and PULSAR must be tellable apart by outline alone.
=== END CORRECTION ===
"""),



    ("sentinel", "#46F0F0", """FEMALE, BRITISH, MID-THIRTIES — thirty-five at most, and she must
clearly read that age: no grey, no jowls, no deep age lines, firm skin along the jaw. Strong
and athletic through the neck and shoulders — someone who wears a pressure suit for a living.
Sharp high cheekbones, a firm level jaw, a short straight nose. Skin MATTE and real with
visible pores and a light fan of squint-lines at the outer eye corners only — worked, but
young.  Attractive and hard-edged, never careworn.
Hair jet black, cut blunt at the jaw, pushed behind one ear. Expression: mouth
closed and level, one brow fractionally lower, gaze locked on the viewer — someone who has just
found the fault and is deciding how much trouble to be. Unimpressed, not hostile.

HARDWARE — SHE IS SPECIAL FORCES, AND SHE MUST READ THAT WAY INSTANTLY. Think a modern
tier-one operator stripped to soft kit: low-profile, purposeful, everything on her head there
for a reason and nothing decorative. Her head is the close-fitting neoprene hood described
below, with TACTICAL GOGGLES pushed up onto her forehead and a fine azure indicator stitched
flat into the hood at the temple. Matte, non-reflective, scuffed from use.

ABSOLUTELY NO MAGNIFIER VISOR, NO JEWELLER'S LOUPE, NO LENS BARRELS ON THE FOREHEAD, NO
INSTRUMENT HEADBAND, NO ANTENNAE, NO STACKED OPTICS. Earlier versions gave her a laboratory
inspection visor and it made her look faintly ridiculous — a bench technician, not a soldier.

AND NO ARMOURED SHELL, NO HELMET, NO HARD CROWN PLATE OF ANY KIND. Her head is the soft
neoprene hood and nothing rigid over it. The special-forces read comes from the hood, the
goggles and the wear on both — a diver or a night operator stripped down to the soft kit,
not a trooper in a helmet. Her silhouette stays smooth and close to the skull.

BODY MODIFICATION — sited at the CHEEKBONES AND NAPE: sharp plates seated over both zygomatic arches with azure-lit seams beneath the eyes, and an armoured vertebral housing visible at the back of the neck where the hood meets the collar. Her crown carries no hardware at all — just the soft hood.

THE ROLE STEREOTYPE — DATA ANALYST. Precise, sceptical, exacting: the one who checks your number and finds the flaw. Reads as someone mid-audit who has just spotted the discrepancy.

LIT ELEMENTS: both eyes GLOWING cool azure. Plus the lit lining of the uniform. She is the
quietest portrait in the cast and that is deliberate — a QA officer who does not glow.

HER CHEEK PLATES ARE EMBEDDED, NOT ATTACHED. The plates over her cheekbones sit FLUSH INTO
the face — grafted, seated below the surrounding skin line, with the skin closing over their
edges and a faint healed margin where flesh meets alloy. They must NOT look like separate
pieces stuck on top of the cheek, floating above it, or casting a shadow beneath their edge.
Previous renders made them look like appliqué; they are part of her skull.


NO SCARS ANYWHERE ON HER. She is a marksman who works at distance and never gets close enough
to be marked — no scar through the eyebrow, no scar on the cheek, no flash-burn, no keloid, no
healed cuts of any kind. Her skin is clear and unblemished apart from her machine seams. That
absence is characterisation: she is the one who does not get hit.


HER FACE: WHITE BRITISH, and she should read as someone whose accent is crisp English — that
is what her voice actually sounds like. Fine-boned, sharp features, cool pale complexion.

HER HEAD, STATED ONCE AND COMPLETELY. Everything above her collar is exactly three things:
the hood, the goggles, and the wear on both. Nothing else is mounted anywhere on her head.
Earlier versions of this brief accumulated a jeweller's turret, a side-mounted telescope, a
pair of brow binoculars, a magnifier visor and an armoured crown plate — all at once — and
she came out looking cluttered and faintly ridiculous rather than dangerous. If a piece of
kit is not named in the two paragraphs below, it does not exist on her.

HER HEADGEAR — THE HOOD.
Her uniform CONTINUES UP OVER HER HEAD as an integrated hood: a smooth matte NEOPRENE-LIKE
close-fitting cover in the same charcoal as the tunic, seamless with the collar so it reads as
one continuous garment running from her chest over her skull. It hugs the shape of the head
with the soft sheen of a wetsuit or a flight hood, with a fine azure piped seam tracing its
edge to match the tunic trim.

HER HOOD MUST SIT LOW AND TIGHT TO THE SKULL. It follows the exact shape of her head with
no crest, no raised crown, no bulk piled on top and no volume above the skull line — earlier
renders gave her a tall hood that ran straight off the top of the frame. The goggles parked on
her forehead sit BELOW the crown, not above it. Her whole head, hood included, must have clear
empty space above it.

There is NOTHING HARD over the hood. The goggle strap runs directly around the neoprene and
grips it, and a couple of low fabric strap-keepers and a small azure indicator are stitched
flat into the hood itself — that is the entire mounting arrangement. Soft kit, close to the
skull, service-worn and slightly grimy.

The hood frames her face cleanly: her face, ears and jaw are FULLY VISIBLE and unobstructed,
with a narrow band of her blonde hair showing at the front hairline where the hood meets her
brow, so she still reads as herself. She is the only unit in the cast with a covered head, and
that silhouette is now her signature.

INSTEAD SHE WEARS GOGGLES ON HER HEAD. A single pair of purpose-built optical goggles pushed UP
onto the hood at her forehead, strap gripping the neoprene, obviously designed to be PULLED DOWN
over both eyes. Give them: a wide matte alloy frame spanning the brow, a thick adjustable strap
running back around the shell, visible hinge or slide points where they travel down, and — the
important part — SMALL TELESCOPIC ZOOM LENSES built into each eyepiece: short stepped barrels
with knurled focus collars set into the goggle body, one over each eye position, with real glass
catching the light and a faint azure gleam inside. Compact, integrated, purposeful — an
instrument for seeing a long way, worn on the head, not a weapon sight bolted to the side.
Both of her own eyes stay fully visible beneath them.

NO CHEEK PLATES. Remove the alloy plates on her cheekbones completely — no hard panels, no
appliqué, no metal on her face at all. In their place: GLOWING GROOVES CUT INTO THE SKIN ITSELF.
Fine, precise channels incised into her cheekbones, temples and along the jaw, lit from within
in azure — the light coming from inside the groove as if it runs beneath the surface. The skin
around them is smooth, unbroken and unplated. Her face is skin and light, not skin and armour.

Keep the neoprene hood continuous with the tunic. The goggles sit directly on the hood with
their strap gripping it — no hard shell in between.


HER CHEST CORE IS PURE LIGHT, NOT A LENS. It is a solid disc of saturated azure light —
uniformly bright, glowing evenly across its whole face, like a filled light panel or a lit
porthole of pure colour. It must NOT be rendered as clear glass, as a camera lens, as a
transparent optic with visible internal elements, rings or reflections, and there must be no
lens barrel or ground-glass look to it. Optics belong to her GOGGLES; her core is simply
light. A clean bright azure disc with a soft bloom on the surrounding fabric.


MORE AZURE ON THE SUIT — her hood and tunic are currently reading as flat black. Lift the
charcoal so her blue is genuinely present in the garment: broader azure piping along the collar,
the hood edge and the yoke seam, a faint azure sheen across the neoprene where the light catches
it, and azure-lit seam channels running down the hood and into the shoulders. She should read
BLUE at a glance, not black.

SHE IS TOO CLEAN AND TOO PERFECT — rough her up. She has been in the field: fine scratches and
scuffing on the goggle frame and the hood, dulled paint at the edges, a smear of grime along
the hood seam, slight wear where the strap rubs, a few stray hairs escaping the hood, skin with
real texture and pores rather than a flawless finish. Weathered and used, not showroom.



































=== AUTOMATED CORRECTION ===
FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is IRIS. Study iris's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. SENTINEL and IRIS must be tellable apart by outline alone.
=== END CORRECTION ===
"""),



    ("nova", "#3CB44B", """HARDWARE — a COLLAR TOOL ROLL, and it is the only piece of kit she carries. A short strip
of worn oiled leather is buttoned across her right collarbone, holding four or five fine
precision drivers and probes upright in individual loops — knurled steel handles, worn
plating, the tips out of sight below the frame. It sits flat against the uniform, reads as
a distinct row of small vertical shapes at any size, and is unmistakably a working
engineer's kit rather than a costume.

SHE WEARS NOTHING ON HER HEAD. No goggles, no safety glasses, no shield, no visor, no
mask, no headband, no eyepiece, no lamp. Her hair and face are completely unobstructed.
This matters: two other units already carry head-worn eye protection, so a third makes
three characters read as the same job. Her hardware is at the COLLAR and nowhere else.

CLEARLY AND UNAMBIGUOUSLY FEMALE (bf_alice) — she must read as a woman at a glance, in the
feminine cut of the uniform. Not androgynous, not butch, not masculine-presenting: an earlier
version made her gender ambiguous and it fought her voice. She is still tough, capable and
practical — a woman who works with her hands — just never mistakable for a man. WHITE
AMERICAN, LATE THIRTIES — fifteen years on the tools, not five. Eastern-European-American shipyard stock:
fair, freckled, sun- and arc-damaged skin, no makeup, WEATHERED rather than hard. Broad square
shoulders, thick neck, a maker's physique. Square face, strong jaw, heavy straight brows, a
nose broken once and set well. Practical short platinum hair — cropped and easy to work in, but recognisably a woman's cut, softer than a buzzcut and with a little length on top.
Expression level, direct and faintly amused at you — mouth closed but relaxed with a slight
asymmetric set, never clamped.

BODY MODIFICATION — sited at the JAW AND SHOULDER: a heavy alloy mandible plate grafted along the left jaw BELOW and BEHIND the mouth line (never across the lips), and a thick plated trapezius rising into the neck, arc-scarred and pitted, with green-lit seams. Her buzzcut scalp is bare skin.

THE ROLE STEREOTYPE — SOFTWARE ENGINEER. Heads-down builder: focused, practical, unbothered by appearances, the one who ships. Reads as someone pulled out of deep focus to answer you.

LIT ELEMENTS: both eyes GLOWING green with a turned mechanical bezel. Then THE CHEST CORE, WHICH IS HERS ABOVE ALL — her fusion core is the BRIGHTEST CHEST
CORE IN THE ENTIRE CAST, a deep green emitter with genuine bloom spilling onto the plate around
it, sitting in the collar opening. Her spec says the core IS her identity; it must be
unmistakably present and unmistakably the brightest.
Lit green seams along the edges of a cheek plate and a jaw plate. One UNLIT alloy jaw-hinge plate at the
left mandible angle with two fasteners, sitting BEHIND and BELOW the mouth corner, never across
it. Wear: arc-flash speckle across the right temple and cheekbone, a healed scar through the
left eyebrow.

REVISED READ — she is YOUTHFUL AND CALIFORNIAN: late twenties, sun-touched fair skin, an
open easy confidence, healthy and outdoorsy rather than careworn. Strong and self-assured,
unmistakably a woman, never androgynous.

HER CLOTHING IS MORE ROBUST than the office units: over the standard charcoal tunic she wears
heavy workshop kit — a thick scarred leather work apron or chest rig buckled across the torso,
reinforced canvas at the shoulders, a tool strap with worn metal fittings, and burn-speckled
sleeves pushed back over her forearms. She looks like she has been on the tools all day.


REVISED READ — YOUTHFUL AND SUN-TOUCHED: late twenties, fair skin with a healthy outdoor
colour, an easy open confidence. Strong and self-assured, unmistakably a woman, never
androgynous and never careworn.

MORE ROBUST CLOTHING than the office units: over the standard charcoal tunic she wears heavy
workshop kit — a thick scarred leather work apron or buckled chest rig, reinforced canvas at
the shoulders, a tool strap with worn metal fittings, burn-speckled sleeves pushed back over
the forearms. She has been on the tools all day.


FINAL IDENTITY — SHE IS IRISH, AND SHE SHOULD LOOK GAELIC. This overrides any earlier
description of her as American or sun-touched.
  - Fair Celtic colouring: pale skin that freckles rather than tans, a scatter of freckles
    across the nose and cheekbones, and clear light eyes.
  - A soft round-boned Gaelic face — a broad open brow, wide-set eyes, a short straight nose
    and a full mouth. Warm and characterful, not sharp or angular.
  - HAIR: LONG AND WAVY, well past the shoulders, in a rich dark auburn with copper lights —
    thick natural waves, worn loose or half pushed back. NOT cropped, NOT a buzzcut, NOT
    platinum. This is a significant change from her previous short platinum crop.
  - Late twenties. Strong, capable and confident — unmistakably a woman, never androgynous.
  - She stays a hands-on maker: goggles pushed up on her forehead, heavy workshop kit over
    the tunic, burn-speckled sleeves. The Gaelic warmth is in her FACE, not her job.


HER FACIAL GROOVES ARE PERFECTLY SYMMETRICAL — this is the one remaining defect on her.
Whatever lit groove appears on the LEFT side of her face must appear identically MIRRORED on
the RIGHT: same path, same length, same start and end points, same width, same brightness.
The previous render left a stray fragment of groove near the left side of her mouth and jaw
with no counterpart on the right, and it reads as a rendering error rather than as design.
No orphaned segments, no lines that stop halfway, no marks on one cheek that are absent from
the other. Every groove is a matched pair about the centreline of the face. Everything else
about her is correct and must be preserved exactly.

























=== AUTOMATED CORRECTION ===
LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

EYE BRIGHTNESS FAILURE — the last render had irises that were too dark and was rejected by an automated brightness check. BOTH IRISES MUST BLAZE: a hot, saturated, self-luminous ring in the character's colour, near-white at its hottest, casting a visible coloured glow onto the lower eyelid and the inner corner of the eye socket. They are the brightest element on the entire face. A dim tinted eye, a dark coloured lens or a subtle shimmer all fail. The pupil remains a dark hole at the centre.

FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is NEBULA. Study nebula's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. NOVA and NEBULA must be tellable apart by outline alone.

HEADROOM FAILURE — the top of the head ran off the top edge of the frame and was rejected. The shot is NOT going to be widened: the whole cast shares one fixed zoom and one fixed eye line. Fix it by giving the character a LOWER SILHOUETTE ABOVE THE EYES — hair worn closer to the skull, any hood or headgear low-profile and following the shape of the head, nothing stacked or piled on the crown. There must be clear empty space between the top of the head and the top of the picture.

HEAD SIZE FAILURE — the head was rendered at the wrong scale relative to the rest of the cast, and was rejected. Every portrait must sit at the SAME distance from camera: the head from crown to chin occupies a little over a third of the frame height. Not a distant bust, not a tight beauty crop. Match the style anchor's head size exactly — hold a ruler to it. This is a cast of colleagues photographed in one sitting, on one lens, at one distance.

GLOW FAILURE — the last render was too bright and was rejected. Cut the emissive area back hard: keep the lit lining fine and thin, keep facial grooves narrow, and let the irises be the brightest thing. No broad blooms, no wide washes of colour, no glowing areas larger than a fingertip apart from the eyes.

COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.
=== END CORRECTION ===
"""),



    ("nebula", "#F032E6", """HARDWARE — a COLOUR SWATCH FAN clipped at her left collar, and it is the only piece of kit
she carries. A stack of a dozen thin anodised metal chips on a single rivet, fanned slightly
open so several different coloured edges show at once, hanging from a short chain on a plain
steel clip. It reads instantly as a designer's swatch fan, it is physical and worn rather
than glowing, and it is the one object in the cast that is about COLOUR itself.

SHE WEARS NOTHING ON HER HEAD OR OVER HER EYES. No loupe, no magnifier, no goggles, no
eyepiece, no visor, no headband of any kind. Her face and hair are completely clear. Her
hardware is at the COLLAR, and the paint on her skin is the other half of her profession
showing.

FEMALE, WHITE BRITISH, early thirties (bf_emma). Average build, loose animated posture.
STRIKINGLY BEAUTIFUL — the best-looking person in the cast and it should be
obvious. Warm open bone structure, high sculpted cheekbones, a strong clean jawline, wide
bright eyes, full lips, a straight elegant nose. SMOOTH, WARM GOLDEN-TANNED SKIN with a healthy luminous
glow — an even, flattering tan, NOT sun damage: no leathery texture, no heavy weathering, no
dense freckling, no deep creasing. Only the faintest scatter of freckles high on the cheeks.
Soft refined features, full lips, a warm confident half-smile. She is the most attractive
person in the cast and the render should be unambiguous about it. Youthful and radiant —
early thirties at most, never careworn.

HER LIT MAGENTA FACIAL SEAMS ARE MANDATORY and must be clearly visible: fine bright magenta
panel-seam lines tracing her jaw line, curving along each cheekbone and stepping up at the
temples. Do not omit them and do not let the tan hide them.
Expression: mouth CLOSED or barely parted with a slight upward tilt at one corner — focused,
faintly amused, mid-task rather than posed. NO VISIBLE TEETH, no broad smile.
Hair: LONG, thick and BLONDE — sun-lightened honey-blonde with paler
gold at the ends, worn half tied back off her face so the forehead has a clear unobstructed
mounting point, with loose strands escaping. Natural blonde, never platinum or bleached, and
never dyed a colour.

BODY MODIFICATION — the LIGHTEST in the cast, sited at ONE TEMPLE: a small neat plate at the left temple with a socketed port behind the ear, magenta-lit seam. She is the least rebuilt of the nine and it should show.

THE ROLE STEREOTYPE — PRODUCT DESIGNER, the one seat covering both the flow and the surface. Visually-led and expressive: the most stylish person in the room, with an eye for colour and a working tool for judging it — and the one who has watched a stranger use the thing and can tell you where they hesitated.

LIT ELEMENTS: both eyes GLOWING magenta, plus a single lit bead on the swatch-fan clip. Then
the chest core. ONE fine unlit machined seam per temple, nothing on the cheeks. Her face is
otherwise clear, smooth, unmarked skin — absolutely NO cracks, NO crazing, NO painted patterns,
NO markings sweeping around the eyes.


FRAMING AND STYLE — CRITICAL, HER LAST RENDER FAILED BOTH.
  - HEAD AND SHOULDERS ONLY. Her HANDS AND ARMS MUST NOT BE IN FRAME AT ALL. No hands raised
    to the face, no arms crossed, no objects held up. The bottom of the frame is upper chest.
    Her last render came out as a half-body shot with both hands visible and it broke the set.
  - So put the paint where a head-and-shoulders crop can SEE it: a fleck or two high on one
    cheekbone, a small smudge along the jaw, a streak at the side of the neck, and colour
    marks on the shoulder and collar of the tunic. NOT on hands — the hands are out of shot.
  - Her brushes and the folding colour-swatch fan sit slotted in a loop on the SHOULDER trim,
    visible at the top of the chest, not carried in a hand.
  - PHOTOREAL, exactly like her eight colleagues — a photograph of a real person, matching
    their skin rendering and lighting. Her last render drifted toward illustration; it must
    not. No stylisation, no painterly rendering, no glamour retouching.


NO COLOUR SWATCHES. Remove the folding colour-swatch fan entirely — no swatch cards, no
colour chips, no fan of samples anywhere on her. Her artist's signature is the PAINT itself
plus two or three fine brushes slotted at the shoulder, nothing more.





































=== AUTOMATED CORRECTION ===
GLOW FAILURE — the last render was too bright and was rejected. Cut the emissive area back hard: keep the lit lining fine and thin, keep facial grooves narrow, and let the irises be the brightest thing. No broad blooms, no wide washes of colour, no glowing areas larger than a fingertip apart from the eyes.

CRITICAL POSE FAILURE — THE LAST RENDER OF THIS CHARACTER WAS TURNED AWAY FROM CAMERA and was rejected by an automated head-pose check. The head must be PERFECTLY SQUARE TO CAMERA: zero yaw, zero rotation, both cheeks showing equally, both ears equally visible, the nose and mouth exactly on the vertical centreline, gaze straight down the lens. Think passport photograph. This overrides every compositional instinct.

LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is SENTINEL. Study sentinel's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. NEBULA and SENTINEL must be tellable apart by outline alone.

EYE BRIGHTNESS FAILURE — the last render had irises that were too dark and was rejected by an automated brightness check. BOTH IRISES MUST BLAZE: a hot, saturated, self-luminous ring in the character's colour, near-white at its hottest, casting a visible coloured glow onto the lower eyelid and the inner corner of the eye socket. They are the brightest element on the entire face. A dim tinted eye, a dark coloured lens or a subtle shimmer all fail. The pupil remains a dark hole at the centre.

COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.
=== END CORRECTION ===
"""),



    ("echo", "#BCF60C", """MALE, BLACK AMERICAN, early-to-mid twenties — the youngest of the cast (am_puck). His youth is
carried by PROPORTION, not by decoration: a slighter frame, narrower shoulders than every
sibling, less jaw mass, fuller cheeks. He should read younger by BUILD before you clock a single
light. Rounded open face, soft jaw, no hard planes. HIS EYES ARE RELAXED AND NORMALLY LIDDED — upper lids resting naturally across the top of the iris the way a calm person's do. He is alert, not startled. NO wide staring eyes, NO raised brows, NO whites showing above or below the iris, NO fixed unblinking look. Earlier renders had him saucer-eyed and he read as if he were high rather than switched on. Short black fade, plain and
practical. Expression: quick keen half-smile, brow lifted — playful and alert, not smug.

HARDWARE — a single physical FIELD COMMS HEADSET. One solid boom arm hinged at a bracket clipped
over the RIGHT ear, running down and stopping WELL SHORT of the mouth, ending in a worn
open-cell foam windscreen beside the cheek. Visible hinge pin, a clip you can see is actually
attached, light scuffing on the foam. Dispatch-tech kit — the thing you would see on a Belter
running comms from a cramped ops chair. The boom must NEVER cross the lips or the chin.
DELETE ENTIRELY: the crown stud, the transcript ribbon, the temple dashes, and ABSOLUTELY any
floating or projected text.

BODY MODIFICATION — sited BEHIND THE EAR: a plated mastoid housing with a teal-lit seam and a comms socket, plus a slim plated collarbone port. He is young and lightly modified — far less hardware than the veterans.

THE ROLE STEREOTYPE — COPYWRITER. Young, quick, verbal: the one who finds the line. Reads as sharp, articulate and slightly amused.

LIT ELEMENTS: both eyes GLOWING teal, plus one small teal glow at the mic-tip
windscreen. Plus the lit lining of the uniform. ONE short straight UNLIT hairline seam along the jaw, stopping
well short of the cheek. Kit looks issued and lightly used — not pristine, not battered. He has
not been in the field long.

HIS EYE COLOUR IS GENUINELY TEAL-BLUE, not an effect laid over a brown eye. Render the iris
itself as that colour — a real luminous teal iris with visible fibre detail and a dark pupil at
its centre — so it reads as his natural eye colour lit from within. The previous render looked
like a glowing disc composited on top of the eye; that is the failure to avoid.


HIS EYE COLOUR IS GENUINELY TEAL-BLUE, not an effect laid over a brown eye. Render the iris
ITSELF in that colour — a real luminous teal iris with visible fibre detail and a dark pupil at
its centre — so it reads as his natural eye colour lit from within. The previous render looked
like a glowing disc composited on top; that is the failure to avoid.




























=== AUTOMATED CORRECTION ===
COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.

LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

MATERIAL FAILURE — the body carried no warm metal and was rejected. Brass, bronze or aged copper is the cast's shared material signature: it must appear on the manufactured parts of the NECK, SHOULDERS AND COLLAR — plate edges, seam bolts, a jack housing, shoulder hardware — as a visible, unmistakable warm metal against the charcoal uniform. Not a faint tint, not a highlight; actual metal you could name.
=== END CORRECTION ===
"""),



    ("atlas", "#E6194B", """MALE, INDIAN-AMERICAN / SOUTH ASIAN, early forties (am_fenrir). He is named for the
Titan who carries the weight of the world, and he is the one who takes the load when nobody
else can — so build him POWERFUL AND ATHLETIC, not merely bulky. Heavily muscled and visibly
STRONG: a thick corded neck, enormous square trapezius rising toward the jaw, broad deep chest,
powerful shoulders straining the tunic. Lean and hard with it — a strongman or a heavyweight
athlete, NOT soft, NOT overweight, NOT jowly. Low body fat, defined jawline, the physique of
someone who lifts every day. Square heavy jaw, broken nose, deep-set eyes, thick short black
beard kept tight. BALD. Expression FLAT and unbothered, already halfway to the next job —
NOT glowering; a glower reads as threat and threat is exactly what sinks this role.

HARDWARE — a worn canvas-and-webbing TOOL HARNESS across one shoulder and chest, carrying three
or four visibly DIFFERENT quick-release tool mounts: a driver bit, a cable crimper, a pressure
gauge. Each mismatched, each scuffed from real use, no two the same shape. Mismatched tools are
the entire point — the visual argument for "I don't know what today's job is either, but I
brought something for it."
DELETE ENTIRELY: the mandible brace, the scalp armour plate and every exposed bolt head. The
brace crosses his jaw hinge and would break lip sync outright.

BODY MODIFICATION — THE MOST HEAVILY REBUILT OF THE ENTIRE CAST, and his signature: a full hardened cranium, a thick armour plate seated into the whole skull following its curve, edges sunk flush into the scalp, violet-lit seams along every panel join, plus a plated trapezius and neck. He is the tank of the cast and his augmentation is total.

THE ROLE STEREOTYPE — IT SUPPORT. The fixer who turns up with the kit and sorts it out, whatever it is. Practical, unbothered, carries the tools nobody else has.

LIT ELEMENTS: both eyes GLOWING violet, plus one small violet indicator bead on
an antenna tip. Plus the lit lining of the uniform. NO lit scalp seam, NO lit brow line. One old service
weld-scar low on the scalp, DIM and unlit. Scuffed matte metal, oil staining at the harness
straps.

HIS COMMS GEAR IS BUILT INTO HIM, NOT WORN. He carries a permanently integrated headset and
microphone: a brass-and-gunmetal ear unit SOCKETED INTO the skull just above and behind the
right ear, its housing seated flush into the bone with the skin sealed around it in a healed
margin, exposed rivets and a knurled brass collar around its rim. From it, a short armoured
boom arm is ANCHORED into a plate at his jaw — bolted permanently to the mandible, not clipped
to a strap — curving forward and stopping well short of his lips, ending in a small mesh
capsule behind a brass grille. Nothing about it could be taken off. Add a couple of fine brass
tubes running from the ear unit back under a scalp plate.










































=== AUTOMATED CORRECTION ===
BACKGROUND FAILURE — there was structure or texture behind the subject. The background is a FLAT, EMPTY, NEAR-BLACK void with only the faintest haze of the character's colour. No set, no wall, no panelling, no machinery, no gradient banding, no visible surface.

EYE BRIGHTNESS FAILURE — the last render had irises that were too dark and was rejected by an automated brightness check. BOTH IRISES MUST BLAZE: a hot, saturated, self-luminous ring in the character's colour, near-white at its hottest, casting a visible coloured glow onto the lower eyelid and the inner corner of the eye socket. They are the brightest element on the entire face. A dim tinted eye, a dark coloured lens or a subtle shimmer all fail. The pupil remains a dark hole at the centre.

CRITICAL POSE FAILURE — THE LAST RENDER OF THIS CHARACTER WAS TURNED AWAY FROM CAMERA and was rejected by an automated head-pose check. The head must be PERFECTLY SQUARE TO CAMERA: zero yaw, zero rotation, both cheeks showing equally, both ears equally visible, the nose and mouth exactly on the vertical centreline, gaze straight down the lens. Think passport photograph. This overrides every compositional instinct.

LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is MERIDIAN. Study meridian's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. ATLAS and MERIDIAN must be tellable apart by outline alone.

COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.

HEAD SIZE FAILURE — the head was rendered at the wrong scale relative to the rest of the cast, and was rejected. Every portrait must sit at the SAME distance from camera: the head from crown to chin occupies a little over a third of the frame height. Not a distant bust, not a tight beauty crop. Match the style anchor's head size exactly — hold a ruler to it. This is a cast of colleagues photographed in one sitting, on one lens, at one distance.
=== END CORRECTION ===
"""),



    ("iris", "#FABEBE", """FEMALE, WHITE AMERICAN, TWENTY-SEVEN — the youngest woman in the cast and the most
approachable person in it (af_heart). GIRL NEXT DOOR: open, friendly, unintimidating, the
one a stranger would ask for directions. Soft oval face, rounded cheeks with real fullness
still in them, a small straight nose, a wide easy mouth, warm grey-green eyes set slightly
wide. FAIR SKIN WITH A HEAVY SCATTER OF FRECKLES — across the bridge of the nose and both
cheekbones, carrying up onto the temples and down the sides of the neck. The freckles are a
defining feature and must be clearly visible, not a faint dusting. Fine visible pores, a
little natural colour in the cheeks. NO scar through the eyebrow, no weathering, no grime —
she is the least battered unit in the cast and that is the point.

Build SLIM and light-framed, narrow shoulders — she reads young next to her colleagues.

HAIR: BLONDE — a warm natural golden blonde, not platinum and not brassy. Worn LONG and
loose to below the shoulder in soft natural waves, with a few strands falling forward across
one temple. Unstyled and slightly windblown rather than set. It must read blonde instantly,
at any size, against the black background.

SHE MUST MATCH HER VOICE. Her voice is a young, warm, bright American woman, and every
earlier render fought it — the face read as a hardened woman in her late thirties while the
audio read as someone a decade younger. The face is the thing that changes.
NO lit band, NO circlet, NO halo. Expression level and patient, mid-conversation — the look of
someone who has already heard the objection. She must read as highly intelligent and formidable.

HARDWARE — a worn hand-held BROADCAST HANDSET clipped at the LEFT SHOULDER trim. A stubby matte
steel transmitter body with a stub antenna, a rubber-gasketed press-to-talk paddle rubbed shiny
with thumb use, hand-scratched call-sign tape on the casing. One coral pilot lamp the SIZE OF A
RIVET, lit, showing it is live. Issued kit, repaired twice, not styled. It sits at the collar,
clear of the mouth and jaw.
DELETE ENTIRELY: the circlet, the signal arc, every facial trace, the chest heart emblem, and
any glowing reticle over the eyes.

BODY MODIFICATION — sited at the THROAT AND COLLARBONE: a plated larynx housing at the front of the throat and a socketed broadcast port set into the left collarbone, coral-lit seams. Her face and scalp are unplated — her modification is about transmitting, not armour.

THE ROLE STEREOTYPE — MARKETING MANAGER. Polished and persuasive: the one who presents, pitches and owns the message. Camera-ready and formidably smart.

LIT ELEMENTS: two eyes — both eyes GLOWING coral with a machined bezel — plus the rivet-sized handset pilot lamp. Then the
chest core. She is currently by far the brightest unit in the cast; she must come DOWN to the
cast baseline. Trim is chipped painted enamel, matte, no bloom on the piping.

GLOW RESTRAINT: she currently renders slightly brighter than the rest of the cast. Keep her
lit elements to the two eyes, the single rivet-sized handset pilot lamp and the chest core,
and let the coral facial seams be FINE and restrained rather than broad or blooming. She should
sit level with her colleagues, never the brightest face in the room.


HER TUNIC IS PROPERLY CLOSED. No open shirt, no exposed chest, no bare sternum, and NO socketed
port, plug, connector or hardware set into her chest or throat. The previous render gave her an
open front with a plug in it and it read as confusing — remove it entirely. Her collar is
buttoned and formal like the other executives.
KEEP the shoulder-clipped broadcast handset with its stub antenna and single lit pilot lamp —
the walkie-talkie comms reference works and is her signature.









UNIFORM TIER — EXECUTIVE: the standard charcoal tunic worn plain, pressed and closed to the
throat, with coral piping at the collar and yoke seam. No webbing, no armour, no added straps —
her only carried item is the shoulder-clipped broadcast handset.









































=== AUTOMATED CORRECTION ===
GLOW FAILURE — the last render was too bright and was rejected. Cut the emissive area back hard: keep the lit lining fine and thin, keep facial grooves narrow, and let the irises be the brightest thing. No broad blooms, no wide washes of colour, no glowing areas larger than a fingertip apart from the eyes.

LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.
=== END CORRECTION ===
"""),



    ("meridian", "#911EB4", """MALE, WHITE BRITISH, late fifties (bm_george). HEAVY-SET and upright, the most formal,
heaviest chassis in the cast.

HE MUST NOT RESEMBLE ANY RECOGNISABLE ACTOR OR PUBLIC FIGURE. The previous render read as a
specific well-known film star and that is a defect — he is an invented character and must look
like nobody in particular. Give him a face that is distinctly HIS OWN and not conventionally
handsome: a long heavy jaw, a high domed forehead with a deeply receding hairline, a prominent
hooked nose, deep-set hooded eyes under heavy brows, thin lips, and pronounced nasolabial
folds. Severe and patrician rather than charming. Hair: thin silver, swept back from a high
brow — NOT a full swept-back film-star head of hair. Beard: closely-cropped silver, more
austere than groomed. Heavy hooded brow, grave and measured, the most experienced person in the room.

CRITICAL — HE IS CURRENTLY FAR TOO HUMAN AND MUST BE VISIBLY THE SAME MANUFACTURE AS HIS
SIBLINGS. He is the only unit with no machine tell at all, and that must change. Give him:
a clearly MECHANICAL IRIS assembly in both eyes with a turned bezel, a stopped-down aperture and
a real dark pupil; VISIBLE PANEL SEAMS at the jaw line and along both cheekbones, machined and
tight; a fine hairline seam tracing the temples and hairline; and a subtle panel division low on
the neck. His age lines and his machine seams must BOTH be present and distinguishable. He must
read unmistakably as an android of the same factory as the rest.

HARDWARE — a brow-mounted DOCUMENT-AUTHENTICATION LOUPE: a chunky articulated brass-and-steel
lens on a hinged bracket, swung DOWN so the lens sits directly over his LEFT EYE, WORN DOWN OVER HIS LEFT EYE, in use, housing one small
warm practical bulb. Tarnished brass, thumb-worn patina, a stamped service number engraved (NOT
glowing) into a shoulder plate.
DELETE ENTIRELY: the spectacles, and any scrolling or projected text of any kind.

BODY MODIFICATION — an OLDER, HEAVIER GENERATION of hardware: a thick formal brow plate and plated jaw panels in a visibly older, more ornate industrial style than his younger colleagues, tarnished and worn smooth by decades, with ice-navy lit seams. The oldest chassis in the cast, and it should look a generation behind.

THE ROLE STEREOTYPE — GENERAL COUNSEL. The most senior person present: formal, unhurried, careful. The one everybody waits to hear from.

LIT ELEMENTS: both eyes GLOWING bright ice-navy, plus the loupe bulb. Plus the lit lining of the uniform.
Because his navy is the darkest colour in the cast, the few lights he has must burn BRIGHT and
CLEAN — raise their peak brightness rather than adding more of them. His background spill must
be lifted to match the rest of the cast; he currently sits far darker than his siblings and must
NOT disappear.
FRAMING NOTE — his head must occupy exactly the same share of the frame as every sibling. He has
previously rendered noticeably smaller; do not let that recur.

WEARING THE LOUPE IS MANDATORY: the document-authentication lens is DOWN over his left eye,
seated in front of it and clearly in use, with the small warm bulb lit. It must NOT be parked
on his forehead or pushed up onto his brow. His right eye is uncovered and glowing normally,
so both eyes remain visible and the two read as a matched pair. The lens sits high on the
face, clear of the mouth and jaw.

THE STAMPED SERIAL IS AN ACTUAL SERIAL NUMBER, not the words. His shoulder plate carries a
stamped alphanumeric code such as "MRD-4471-K" or "GC-08829" — random-looking letters and
digits, engraved and tarnished. It must NOT read "SERIAL NUMBER" or any other label text. If
the engraving cannot render as convincing alphanumerics, leave the plate blank rather than
stamping a word on it.


THE STAMPED SERIAL IS A REAL SERIAL NUMBER, NOT THE WORDS. His shoulder plate carries a
stamped alphanumeric code — something like "MRD-4471-K" or "GC-08829" — random-looking letters
and digits, engraved and tarnished. It must NEVER read "SERIAL NUMBER" or any other label text.
If convincing alphanumerics cannot be rendered, leave the plate BLANK rather than stamping a
word onto it.















EXPRESSION: grave, unhurried and entirely unreadable — the settled face of the most senior
person present, who has already reached a view and is in no rush to share it. Not hostile, not
warm; simply immovable. The one face in the cast that gives nothing away.



































HE MUST NOT LOOK LIKE PULSAR, AND THIS IS THE ONE DEFECT LEFT ON HIM. The two of them have
collapsed into the same man at small size. MERIDIAN IS THE OLDER, HEAVIER, COLDER OF THE
TWO — late fifties, fully SILVER-WHITE hair worn a little longer and swept back, a broad
heavy face with a soft jawline and real weight through the neck and shoulders, pale cool
complexion. Give him a NEATLY TRIMMED SILVER BEARD — full but close-cropped, covering the
jaw and chin. He is the only bearded unit in the cast and that beard is what separates him
from Pulsar at any size. It must not cross the lips: the moustache is trimmed clear of the
upper lip and the mouth is fully visible, because these frames have to animate speech.






=== AUTOMATED CORRECTION ===
FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is ATLAS. Study atlas's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. MERIDIAN and ATLAS must be tellable apart by outline alone.
=== END CORRECTION ===
"""),



    ("vector", "#FFE119", """FEMALE, AMERICAN, late thirties (af_kore — clear, decisive). She is the PRODUCT MANAGER:
the one who decides what gets built and why, owns the problem statement and the definition of
done, and says no more often than yes. Not the one who schedules the work — that is Pulsar —
the one who chooses it.

FACE AND BEARING: composed, direct and quietly hard to argue with. A strong symmetrical face
with level brows, clear appraising eyes and a firm, patient mouth — the expression of someone
who has already heard your case and is deciding. Warm mid-brown skin, Black American. Late
thirties. Attractive and formidable, never severe and never soft. She should read as the person
in the room whose opinion settles it.

HAIR: BLACK — a deep true black, not brown and not chestnut. Cut into a sharp precise bob at
the jaw with a clean blunt edge, deliberate and immaculate, no strands out of place. Distinct
from every sibling's hair in the cast. THE COLOUR MATTERS: mid-brown hair against the black
background made her silhouette read as a muddy brown outline drawn around her head rather than
as hair. Black hair separates from the void by SHEEN and by the rim light catching its edge,
not by being a lighter colour than the background.

BUILD: upright and composed, average through the shoulders, held very still. Her authority is
stillness, not mass.

BODY MODIFICATION — PLATED ORBITAL RIMS, unique to her in the cast. Both eye sockets are ringed
by fine brass-and-gunmetal orbital plates grafted directly onto the bone, following the curve of
the brow and cheekbone all the way around each eye and sunk flush into the skin with a healed
margin. She is the one who sees the whole board, and her modification is built around her eyes.
No crown plate, no hood, no scalp seam — her forehead and skull are bare skin and hair.

PROFESSION HARDWARE — A BRASS PRIORITY CARD-FRAME clipped at her left collar: a small hinged
brass rack holding a short stack of thin etched metal cards, each edge-notched and numbered, the
topmost one raised slightly proud of the others. It reads instantly as an ordered list carried
on the body — the backlog, ranked, in her keeping. Tarnished brass, visible hinge pin, thumb-worn
edges where cards are pulled and reordered.

GROOVE LANGUAGE — A RANKED LADDER: a short vertical column of five fine horizontal rungs lit in
signal red, running down the right temple in front of the ear, stepping from longest at the top
to shortest at the bottom. A priority stack rendered on the face. Nothing on the cheeks.

LIT ELEMENTS: both eyes GLOWING bright signal red, plus the temple ladder and one small red pip
on the topmost priority card. Plus the lit lining of the uniform.

UNIFORM TIER — EXECUTIVE: the standard charcoal tunic worn plain and immaculate, closed to the
throat, with signal-red piping. No webbing, no armour, no added gear beyond the card-frame.
























=== AUTOMATED CORRECTION ===
FACE COLLISION — the underlying facial geometry is too close to another character's and was rejected by a landmark-distance check. Rebuild the face from different bones: change the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose length and bridge width, the mouth width, the jaw angle and the brow height. Two people with different hair and the same skull are the same person in a wig.

The character it collided with is IRIS. Study iris's portrait and move DECISIVELY away from it — different face shape, different hair mass and outline, different headgear profile. VECTOR and IRIS must be tellable apart by outline alone.

COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial grooves, the indicator lamp and the background spill — must ALL be the exact locked hex stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let the light temperature pull it. One colour, one character.

LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the viewer's right), roughly forty-five degrees off axis and slightly above eye level. The far cheek falls into soft shadow about a stop down — visible modelling on the nose, the brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set.

EYE BRIGHTNESS FAILURE — the last render had irises that were too dark and was rejected by an automated brightness check. BOTH IRISES MUST BLAZE: a hot, saturated, self-luminous ring in the character's colour, near-white at its hottest, casting a visible coloured glow onto the lower eyelid and the inner corner of the eye socket. They are the brightest element on the entire face. A dim tinted eye, a dark coloured lens or a subtle shimmer all fail. The pupil remains a dark hole at the centre.

MATERIAL FAILURE — the body carried no warm metal and was rejected. Brass, bronze or aged copper is the cast's shared material signature: it must appear on the manufactured parts of the NECK, SHOULDERS AND COLLAR — plate edges, seam bolts, a jack housing, shoulder hardware — as a visible, unmistakable warm metal against the charcoal uniform. Not a faint tint, not a highlight; actual metal you could name.
=== END CORRECTION ===
"""),


]


def load(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def build(name, colour, brief, anchor_path):
    master = (f"{ROOT}/assets/readme/pulsar.png" if name == "pulsar"
              else f"{ROOT}/design/drones/{name}.png")
    parts = []
    txt = REGISTER + "\n\n" + LAWS + "\n\n" + UNIFORM + "\n\n" + FRAMING
    # A NEW drone has no prior robot portrait to inherit from — it is the first of
    # its line. Requiring one crashed the generator on the tenth character. Lineage
    # is a reference when it exists, never a precondition for existing.
    has_lineage = os.path.exists(master)
    if anchor_path:
        parts.append({"inline_data": {"mime_type": "image/png", "data": load(anchor_path)}})
        if has_lineage:
            txt = ("IMAGE 1 is the APPROVED STYLE ANCHOR for this cast — match it for the register, "
                   "the skin material and photoreal level, the uniform, the lighting and the framing. "
                   "IMAGE 2 is this character's EARLIER design, for FACIAL IDENTITY ONLY — keep the "
                   "same person's face and build. DO NOT TAKE ITS COLOUR. The locked colour "
                   "stated at the end of this prompt REPLACES the colour in that image "
                   "entirely, and every lit element must be the NEW colour.\n\n" + txt)
        else:
            txt = ("IMAGE 1 is the APPROVED STYLE ANCHOR for this cast — match it for the register, "
                   "the skin material and photoreal level, the uniform, the lighting and the framing. "
                   "This character is NEW to the cast and has no prior design: invent the face from "
                   "the brief below, and make it a sibling of the anchor, never a copy of it.\n\n" + txt)
    elif has_lineage:
        txt = ("IMAGE 1 is this character's EARLIER design, for FACIAL IDENTITY ONLY — keep the "
               "same person's face and build. DO NOT TAKE ITS COLOUR. The locked colour "
               "stated at the end of this prompt REPLACES it entirely.\n\n" + txt)
    if has_lineage:
        parts.append({"inline_data": {"mime_type": "image/png", "data": load(master)}})
    parts.append({"text": txt + "\n\n=== THIS CHARACTER ===\n" + brief +
                  f"\n\n=== LOCKED COLOUR: {colour} ===\nTHIS IS A COLOUR CHANGE. Any reference image "
                  f"you were given shows this character in a DIFFERENT, OLD colour — ignore that "
                  f"colour completely. Every lit element must be {colour}. It appears ONLY on the eyes' iris ring, the "
                  f"single hardware indicator lamp, the chest core, the painted collar and yoke "
                  f"trim, and the subtle background spill. Nowhere else."})
    return {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": "1:1"}}}


def gen(name, colour, brief, anchor_path):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={K}"
    req = urllib.request.Request(url, data=json.dumps(build(name, colour, brief, anchor_path)).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        body = json.loads(urllib.request.urlopen(req, timeout=600).read().decode())
    except urllib.error.HTTPError as e:
        print(f"  {name}: HTTP {e.code} {e.read().decode('utf8','replace')[:200]}")
        return False
    except Exception as e:
        print(f"  {name}: ERR {type(e).__name__}: {e}")
        return False
    for c in body.get("candidates", []):
        for part in c.get("content", {}).get("parts", []):
            b = part.get("inlineData") or part.get("inline_data")
            if b and b.get("data"):
                p = f"{OUT}/{name}-android-v8.png"
                open(p, "wb").write(base64.b64decode(b["data"]))
                print(f"  {name}: OK ({os.path.getsize(p)} bytes)")
                return True
    print(f"  {name}: no image. finish={[c.get('finishReason') for c in body.get('candidates',[])]}")
    return False


only = sys.argv[1:] if len(sys.argv) > 1 else None
ANCHOR = f"{OUT}/pulsar-android-v8.png"
ok = 0
for n, col, brief in JOBS:
    if only and n not in only:
        continue
    anchor = None if n == "pulsar" else (ANCHOR if os.path.exists(ANCHOR) else None)
    if gen(n, col, brief, anchor):
        ok += 1
    sys.stdout.flush()
print(f"generated {ok}")
