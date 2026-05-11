"""
Agent registry — defines all available Valorant agents.
Add or update agents here as the game gets patched.
"""
from models.agent import Agent, Ability

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make(agent_id: str, display: str, role: str, abilities: list[tuple]) -> Agent:
    """
    abilities: list of (key, name, description, icon_filename)
    """
    ab_list = [
        Ability(key=key, name=name, description=desc, icon_filename=icon)
        for key, name, desc, icon in abilities
    ]
    return Agent(id=agent_id, display_name=display, role=role, abilities=ab_list)


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

ALL_AGENTS: list[Agent] = [

    # ── Duelists ──────────────────────────────────────────────────────────
    _make("jett", "Jett", "Duelist", [
        ("C", "Cloudburst", "Throws a smoke cloud", "cloudburst.png"),
        ("Q", "Updraft", "Propels upward instantly", "updraft.png"),
        ("E", "Tailwind", "Dashes in move direction", "tailwind.png"),
        ("X", "Blade Storm", "Throws deadly knives", "bladestorm.png"),
    ]),
    _make("reyna", "Reyna", "Duelist", [
        ("C", "Leer", "Casts a nearsighting eye", "leer.png"),
        ("Q", "Devour", "Consumes soul orb to heal", "devour.png"),
        ("E", "Dismiss", "Consumes orb to become intangible", "dismiss.png"),
        ("X", "Empress", "Enters frenzy mode", "empress.png"),
    ]),
    _make("phoenix", "Phoenix", "Duelist", [
        ("C", "Blaze", "Creates a flame wall", "blaze.png"),
        ("Q", "Curveball", "Flashes around corners", "curveball.png"),
        ("E", "Hot Hands", "Throws a fireball", "hothands.png"),
        ("X", "Run It Back", "Marks current location as respawn", "runitback.png"),
    ]),
    _make("raze", "Raze", "Duelist", [
        ("C", "Boom Bot", "Deploys a bot that seeks enemies", "boombot.png"),
        ("Q", "Blast Pack", "Throws a satchel charge", "blastpack.png"),
        ("E", "Paint Shells", "Throws cluster grenade", "paintshells.png"),
        ("X", "Showstopper", "Fires a massive rocket", "showstopper.png"),
    ]),
    _make("yoru", "Yoru", "Duelist", [
        ("C", "Fakeout", "Deploys decoy footsteps", "fakeout.png"),
        ("Q", "Blindside", "Flips a flash through surfaces", "blindside.png"),
        ("E", "Gatecrash", "Sends a teleport anchor", "gatecrash.png"),
        ("X", "Dimensional Drift", "Enters undetectable dimension", "dimensionaldrift.png"),
    ]),
    _make("neon", "Neon", "Duelist", [
        ("C", "Fast Lane", "Sends two electric walls", "fastlane.png"),
        ("Q", "Relay Bolt", "Throws bouncing lightning bolt", "relaybolt.png"),
        ("E", "High Gear", "Charges up to sprint", "highgear.png"),
        ("X", "Overdrive", "Fires a channeled lightning beam", "overdrive.png"),
    ]),
    _make("iso", "Iso", "Duelist", [
        ("C", "Contingency", "Assembles an energy wall", "contingency.png"),
        ("Q", "Double Tap", "Enters focus state to shield", "doubletap.png"),
        ("E", "Undercut", "Sends a molecular bolt", "undercut.png"),
        ("X", "Kill Contract", "Opens a rift duel arena", "killcontract.png"),
    ]),
    _make("waylay", "Waylay", "Duelist", [
        ("C", "Haste", "Dashes forward briefly", "haste.png"),
        ("Q", "Ricochet", "Bounces a light wave off surfaces", "ricochet.png"),
        ("E", "Radiance", "Creates a slowing light zone", "radiance_waylay.png"),
        ("X", "Convergence", "Channels a massive light beam", "convergence.png"),
    ]),

    # ── Controllers ───────────────────────────────────────────────────────
    _make("omen", "Omen", "Controller", [
        ("C", "Shrouded Step", "Teleports a short distance", "shroudedstep.png"),
        ("Q", "Paranoia", "Sends a blinding shadow bolt", "paranoia.png"),
        ("E", "Dark Cover", "Casts a long-range smoke orb", "darkcover.png"),
        ("X", "From the Shadows", "Teleports anywhere on the map", "fromtheshadows.png"),
    ]),
    _make("brimstone", "Brimstone", "Controller", [
        ("C", "Incendiary", "Launches an incendiary grenade", "incendiary.png"),
        ("Q", "Stim Beacon", "Drops a stim beacon", "stimbeacon.png"),
        ("E", "Sky Smoke", "Deploys orbital smoke strikes", "skysmoke.png"),
        ("X", "Orbital Strike", "Calls a devastating orbital laser", "orbitalstrike.png"),
    ]),
    _make("viper", "Viper", "Controller", [
        ("C", "Snake Bite", "Fires a canister of acid", "snakebite.png"),
        ("Q", "Poison Cloud", "Throws a gas emitter", "poisoncloud.png"),
        ("E", "Toxic Screen", "Creates a long toxic gas wall", "toxicscreen.png"),
        ("X", "Viper's Pit", "Covers the area in toxic gas", "viperspit.png"),
    ]),
    _make("astra", "Astra", "Controller", [
        ("C", "Nova Pulse", "Explodes a placed star", "novapulse.png"),
        ("E", "Nebula", "Transforms a star into smoke", "nebula.png"),
        ("Q", "Gravity Well", "Creates a pulling vortex", "gravitywell.png"),
        ("X", "Cosmic Divide", "Channels an infinite cosmic wall", "cosmicdivide.png"),
    ]),
    _make("harbor", "Harbor", "Controller", [
        ("C", "Cove", "Throws a water shield sphere", "cove.png"),
        ("Q", "High Tide", "Sends a wall of water", "hightide.png"),
        ("E", "Cascade", "Creates a wave of water", "cascade.png"),
        ("X", "Reckoning", "Creates crashing water geysers", "reckoning.png"),
    ]),
    _make("clove", "Clove", "Controller", [
        ("C", "Meddle", "Throws a decay orb", "meddle.png"),
        ("Q", "Pick-Me-Up", "Steals health from kills", "pickmeup.png"),
        ("E", "Ruse", "Places a smoke cloud", "ruse.png"),
        ("X", "Not Dead Yet", "Resurrects self after death", "notdeadyet.png"),
    ]),
    _make("miks", "Miks", "Controller", [
        ("C", "Harmonize", "Boosts an ally and Miks", "harmonize.png"),
        ("Q", "M-Pulse", "Heals or Stuns", "mpulse.png"),
        ("E", "Waveform", "Places a smoke cloud", "waveform.png"),
        ("X", "Bassquake", "Cone that bumps and deafens", "bassquake.png"),
    ]),

    # ── Initiators ────────────────────────────────────────────────────────
    _make("sova", "Sova", "Initiator", [
        ("C", "Shock Bolt", "Fires an electric arrow", "shockbolt.png"),
        ("Q", "Owl Drone", "Deploys a recon drone", "owldrone.png"),
        ("E", "Recon Bolt", "Shoots a recon tracking arrow", "reconbolt.png"),
        ("X", "Hunter's Fury", "Fires three long-range blasts", "huntersfury.png"),
    ]),
    _make("breach", "Breach", "Initiator", [
        ("C", "Aftershock", "Fires a slow-burst charge", "aftershock.png"),
        ("Q", "Flashpoint", "Sets a blinding flash charge", "flashpoint.png"),
        ("E", "Fault Line", "Creates a seismic blast", "faultline.png"),
        ("X", "Rolling Thunder", "Sends a cascading quake", "rollingthunder.png"),
    ]),
    _make("skye", "Skye", "Initiator", [
        ("C", "Regrowth", "Heals nearby allies", "regrowth.png"),
        ("Q", "Trailblazer", "Sends a leaping tigress", "trailblazer.png"),
        ("E", "Guiding Light", "Sends a hawk flash", "guidinglight.png"),
        ("X", "Seekers", "Releases seeking orbs", "seekers.png"),
    ]),
    _make("kay_o", "KAY/O", "Initiator", [
        ("C", "FRAG/ment", "Throws an explosive fragment", "fragment.png"),
        ("Q", "FLASH/drive", "Tosses a flash grenade", "flashdrive.png"),
        ("E", "ZERO/point", "Throws a suppressing blade", "zeropoint.png"),
        ("X", "NULL/cmd", "Overloads with energy pulse", "nullcmd.png"),
    ]),
    _make("fade", "Fade", "Initiator", [
        ("C", "Seize", "Throws a nightmare orb", "seize.png"),
        ("Q", "Haunt", "Sends a crawling eye", "haunt.png"),
        ("E", "Prowler", "Releases a prowling beast", "prowler.png"),
        ("X", "Nightfall", "Sends a wave of nightmare energy", "nightfall.png"),
    ]),
    _make("gekko", "Gekko", "Initiator", [
        ("C", "Dizzy", "Launches a glob that blinds", "dizzy.png"),
        ("Q", "Wingman", "Sends Wingman to plant/defuse", "wingman.png"),
        ("E", "Thrash", "Deploys Thrash to lunge", "thrash.png"),
        ("X", "Mosh Pit", "Launches Mosh that detonates", "moshpit.png"),
    ]),
    _make("tejo", "Tejo", "Initiator", [
        ("C", "Stealth Drone", "Deploys a scouting drone", "stealthdrone.png"),
        ("Q", "Guided Salvo", "Fires guided missiles", "guidedsalvo.png"),
        ("E", "Special Delivery", "Throws a concussive grenade", "specialdelivery.png"),
        ("X", "Armageddon", "Fires a massive missile barrage", "armageddon.png"),
    ]),

    # ── Sentinels ─────────────────────────────────────────────────────────
    _make("cypher", "Cypher", "Sentinel", [
        ("C", "Cyber Cage", "Drops a remote cyber cage", "cybercage.png"),
        ("Q", "Spy Cam", "Places a hidden camera", "spycam.png"),
        ("E", "Trapwire", "Places a tripwire trap", "trapwire.png"),
        ("X", "Neural Theft", "Extracts info from enemies", "neuraltheft.png"),
    ]),
    _make("killjoy", "Killjoy", "Sentinel", [
        ("C", "Nanoswarm", "Throws a stealth grenade", "nanoswarm.png"),
        ("Q", "Alarmbot", "Deploys a seeking bot", "alarmbot.png"),
        ("E", "Turret", "Deploys a turret", "turret.png"),
        ("X", "Lockdown", "Detains enemies in a radius", "lockdown.png"),
    ]),
    _make("sage", "Sage", "Sentinel", [
        ("C", "Slow Orb", "Throws a slowing orb", "sloworb.png"),
        ("Q", "Healing Orb", "Heals self or an ally", "healingorb.png"),
        ("E", "Barrier Orb", "Creates a solid wall", "barrierorb.png"),
        ("X", "Resurrection", "Revives a dead ally", "resurrection.png"),
    ]),
    _make("chamber", "Chamber", "Sentinel", [
        ("C", "Trademark", "Places an anchored trap", "trademark.png"),
        ("Q", "Headhunter", "Activates a heavy pistol", "headhunter.png"),
        ("E", "Rendezvous", "Places two teleport anchors", "rendezvous.png"),
        ("X", "Tour de Force", "Channels a custom sniper rifle", "tourdeforce.png"),
    ]),
    _make("deadlock", "Deadlock", "Sentinel", [
        ("C", "Barrier Mesh", "Throws a barrier disk", "barriermesh.png"),
        ("Q", "Sonic Sensor", "Deploys a concussive sensor", "sonicsensor.png"),
        ("E", "GravNet", "Throws a grenade that traps", "gravnet.png"),
        ("X", "Annihilation", "Sends a nanowire pulse", "annihilation.png"),
    ]),
    _make("vyse", "Vyse", "Sentinel", [
        ("C", "Shear", "Places a hidden vine trap", "shear.png"),
        ("Q", "Arc Rose", "Throws a metallic flash", "arcrose.png"),
        ("E", "Razorvine", "Creates a metallic vine zone", "razorvine.png"),
        ("X", "Steel Garden", "Disarms all enemies in range", "steelgarden.png"),
    ]),
    _make("veto", "Veto", "Sentinel", [
        ("C", "Chokehold", "Places a trap on the ground", "chokehold.png"),
        ("Q", "Crosscut", "places a tp on the ground", "crosscut.png"),
        ("E", "Interceptor", "Catches thrown utility", "interceptor.png"),
        ("X", "Evolution", "Health regen and utility invulnerability", "evolution.png"),
    ]),
]

# Quick lookup by ID
AGENT_BY_ID: dict[str, Agent] = {a.id: a for a in ALL_AGENTS}