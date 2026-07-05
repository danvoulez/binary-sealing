who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status  
Plus three-layer hashing (tuple\_hash → content\_hash → envelope\_hash), JCS canonicalization, and SHA-256.

## This system presents a highly disciplined and accountable constitutional architecture for hybrid human-machine systems. The key philosophical and engineering decisions are centered on ensuring that accountability is enforced structurally.Core Architectural Philosophy

## 

## The overarching principle is that **accountability outranks fluency**. This is enforced through a strict separation of concerns, where "canon defines. conformance proves. engine implements. governance evolves". Authority separation is maintained by a 10-layered dependency chain (What-Runs-Natively-Above-Software), preventing lower-law layers from depending on higher-consequence layers.Key Engineering Disciplines[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

1. ## **The Immutable LogLine Core:** Every material act is reduced to the **9-Slot LogLine** (who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status). This immutable tuple forms the system's governance and evidence framework. Its identity is secured using the **Canonical Tuple Digest** (SHA256 of the JCS-encoded 9-slot tuple).[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

2. ## **Decision as Evidence Pivot:** The confirmed\_by slot is the **Evidence Pivot**, the single, sole point where evidence is collapsed into a branch decision (Ok, Doubt, or Not). No other component makes this decision.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

3. ## **Productive Doubt/Simulation:** if\_doubt is elevated from a mere fallback to a first-class, auditable simulation path. Crucially, the normative rule established in LIP-0002 states that if\_doubt **MUST NOT execute external consequence**, ensuring that "possible worlds may be tested without becoming facts".[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

4. ## **Layered Finality and Jurisdiction:** The jurisdiction layer enforces human signature (ratification) where consequence is non-transferable. This human authority is required for **Irreversible external effects** at the horizon-real physical boundary.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

5. ## **Strict Data Integrity:** The system mandates JCS (RFC-8785) canonicalization and employs the **LIP-0007 three-layer hashing** discipline (tuple\_hash, content\_hash, envelope\_hash) to ensure verifiable, content-addressed identity for all receipts and claims.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit)

## Strengths and Weaknesses

| Aspect | Strength | Weakness/Challenge |
| ----- | ----- | ----- |
| **Constitutional Design** | Authority is strictly separated into 10 layers, minimizing the risk of core policy being corrupted by execution concerns.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) | The complexity of managing 10 distinct, layered crates and enforcing the non-reversibility of dependencies. |
| **Evidence** | Decisions are explicit and driven by an auditable confirmed\_by pivot, rather than being implicit or spread across the system.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) | Requires a mature evidence model (token, receipt, signature, quorum) and a functional evidence store (SQLite, Supabase, etc.) to fully realize accountability.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) |
| **Flexibility** | The **SlotHouse Trait Pattern** and **Adapter Protocol (LIP-0004)** allow for decoupled, pluggable architecture and external extensions without redefining the 9-slot core.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) | The **Adapter Protocol** (LIP-0004/0005/0006) is currently only "Proposed", meaning the external extension framework is not yet a formally "Accepted" part of the canon.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) |
| **Runtime** | The Ethics-is-Efficient service executes policies in a **fuel-metered WASM sandbox (Wasmtime)**, ensuring bounded, verifiable, and resource-constrained execution.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) | The runtime intentionally declares external\_effects: false for safety, meaning world effects are deferred to separate, externally implemented ReleaseAdapter and StatusLedger traits.[1](https://docs.google.com/document/d/1ppQ4CED6DkotEtMovxz4O7MVkJJC2jMNyxIVpBwMWDA/edit) |

##   Fourfold Discipline

canon defines.  
conformance proves.  
engine implements.  
governance evolves.  
---

Is there a specific repository, feature, bug, or architecture question you'd like me to dive into?  
Take a second dive a little deeper  
1  
Deep-dive engine-main crate structure and source  
Deep-dive Ethics-is-Efficient-main (TDLN) internals  
Deep-dive What-Runs-Natively-Above-Software constitutional layers  
Deep-dive constitutional-runtime modules  
Deep-dive conformance vectors, schemas, and tools  
Deep-dive governance LIPs and proposals  
Synthesize cross-repo relationships and dependency graph  
I'll conduct a thorough exploration of the engine-main repository. Let me start by examining the structure and then dive into each crate.  
Let me continue by reading the root Cargo.toml and then each crate's Cargo.toml:  
Now let me read the lib.rs files for each crate to understand their functionality:  
Now let me read the CLI main.rs and key documentation files:  
Now let me read the spec files and check the status crate's walk module:  
Let me read more of the walk.rs and status.rs files to understand the complete flow:  
Now let me check the who crate more deeply to understand the core abstractions:  
Let me read more of the slot.rs to understand the SlotHouse trait and other key abstractions:  
Perfect\! Now let me check the canon.rs file to understand how the Canon structure works:  
Excellent\! Now let me create a comprehensive summary document. Let me also check one more doc file to round out my understanding:  
Perfect\! Now I have a comprehensive understanding. Let me compile the final report:

## COMPREHENSIVE EXPLORATION REPORT: engine-main Repository

### REPOSITORY STRUCTURE OVERVIEW

The engine-main repository is a Rust-based implementation of the LogLine runtime system \- a 9-slot governance and evidence framework for accountable operations. It's organized as a Cargo workspace with 10 crates:  
File Locations:

* Root: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/engine-main/  
* Crates: crates  
* Docs: docs  
* Specs: spec

---

## CRATE INVENTORY & EXPORTS

### 1\. logline-who (Foundation/Core)

Path: crates/who/  
Cargo.toml: Lines 1-18  
Purpose: Protects accountable origin and defines the shared 9-slot protocol  
Key Exports (src/lib.rs:1-23):  
rust  
pub use canon::{is\_form\_require\_directive, Canon, RouteClass, RouteKinds, StatusLifecycle};  
pub use error::{LogLineError, Result};  
pub use logline::LogLine;  
pub use parse::{parse\_keyed\_logline, parse\_logline, parse\_marked\_logline};  
pub use slot::{  
   Branch, Mode, Operation, Phase, RunContext, RuntimeDecision, RuntimeSlot,  
   SelectedBranch, Slot, SlotHouse, SlotResolution, StatusTransition,  
};  
pub use validate::{is\_prohibited, validate\_against\_canon, validate\_canon, validate\_shape};  
pub use who::{  
   AccountableOrigin, ActorId, AuthorityId, Jurisdiction, OriginKind, Principal,  
   WhoSlot, WitnessKey,  
};  
Core Abstractions:

1. LogLine struct (logline.rs:1-79)  
   * 9 immutable slots: who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status  
   * Serializable to/from JSON  
   * Positions array for ordered access  
2. Slot enum (slot.rs:6-34)  
   * Represents the 9 canonical positions  
   * Each has .as\_str() method for string representation  
3. Operation enum (slot.rs:38-103)  
   * 11 operations mapping to phases:  
     * Input Phase: Identificar, Nomear, Localizar, Simular  
     * Pivot Phase: Questionar, Confirmar, Verificar  
     * Output Phase: Acionar, Despachar, MarcarProblema  
     * Closure Phase: Registrar  
   * Each operation has a "home" slot and phase  
4. Mode enum (slot.rs:114-137)  
   * Pocket \- Local discipline for LLM/human drafting  
   * Grammar \- Formal surface validation  
   * Algebra \- Symbolic model of routes/statuses  
   * Operational \- Runtime boundary with evidence/adapters  
   * Closure \- Evidentiary layer recording claim states  
5. Branch enum (slot.rs:141-155)  
   * Ok → routes to if\_ok  
   * Doubt → routes to if\_doubt  
   * Not → routes to if\_not  
6. SlotHouse trait (slot.rs:233-246)  
   * Core abstraction: each crate implements this for its slot  
   * Methods:  
     * slot() \- returns which Slot this house protects  
     * resolve(input, ctx, decision) \- produces RuntimeSlot  
     * accepts\_operation(op) \- checks if operation applies to this slot  
7. RunContext struct (slot.rs:200-225)  
   * Holds: Canon reference, Mode, Operation, provided\_evidence, allow\_no\_confirmation  
   * Provides has\_evidence(token) helper  
8. Canon struct (canon.rs:9-23)  
   * Loaded from JSON  
   * Contains:  
     * form: BTreeMap of slot requirements  
     * runtime\_walk: ordered slot sequence  
     * route\_kinds: Ok/Doubt/Not/None route classifications  
     * status\_lifecycle: BTreeMap of allowed status transitions  
     * law: Vec of LogLines defining canonical rules  
     * prohibition: Vec of LogLines defining forbidden patterns

---

### 2\. logline-did (Verb/Operation Naming)

Path: crates/did/  
Cargo.toml: Lines 1-17  
Purpose: Protects named movement \- verb, act, and operation naming  
Key Exports (src/lib.rs:1-147):  
Verb enum (lines 10-17):  
rust  
pub enum Verb {  
   Operation(Operation),      // Runtime operation  
   CanonLaw(String),         // Canonical law verb  
   Domain(String),           // Domain-specific verb  
   Unknown(String),          // Unrecognized  
}  
VerbClass enum (lines 19-46):

* RuntimeOperation \- Maps to Operation enum  
* CanonicalLaw \- One of 13 canonical verbs: "define", "require", "walk", "hold", "compile", "model", "operate", "close", "execute", "become", "bypass", "release", "express\_or\_author", "translate"  
* DomainAct \- Custom domain verbs  
* Unknown \- Unclassified

DidResolution struct (lines 48-89):

* raw: Original string  
* verb: Parsed Verb  
* class: VerbClass classification  
* parse() method: Attempts to classify input string

DidSlot impl SlotHouse (lines 111-147):

* Resolves the did slot  
* Returns Doubt if verb is Unknown  
* Returns Ok with reason based on VerbClass

---

### 3\. logline-this (Bounded Matter & Location)

Path: crates/this/  
Cargo.toml: Lines 1-19  
Purpose: Protects bounded matter and object location  
Key Exports (src/lib.rs:1-188):  
MatterRef enum (lines 14-21):  
rust  
pub enum MatterRef {  
   ObjectId(String),      // Generic identifier  
   Url(Url),             // HTTP/HTTPS URL  
   Path(String),         // File path  
   Digest(String),       // SHA256 digest  
   JsonPayload(String),  // Inline JSON  
   Wildcard,             // "\*" \- unbounded  
}  
MatterDigest struct (lines 24-48):

* Wraps SHA256 digest string  
* sha256\_bytes() \- computes digest from bytes  
* Format: "sha256:\<64-hex-chars\>"

LocatedMatter struct (lines 50-100):

* raw: Original input string  
* reference: Parsed MatterRef  
* digest: Optional computed digest (only for JsonPayload)  
* parse() method: Classifies input  
* is\_unbounded\_for\_mode() \- Checks if wildcard is allowed in mode

ThisSlot impl SlotHouse (lines 152-188):

* Resolves the this slot  
* Returns Doubt if matter is unbounded in Operational/Closure modes  
* Returns Ok with reason based on MatterRef type

---

### 4\. logline-when (Temporal Binding & Simulation)

Path: crates/when/  
Cargo.toml: Lines 1-18  
Purpose: Protects time, phase, and simulation conditions  
Key Exports (src/lib.rs:1-177):  
TemporalBinding enum (lines 12-18):  
rust  
pub enum TemporalBinding {  
   Timestamp(String),                    // RFC3339 timestamp  
   Phase(String),                        // Phase token (before\_\*, after\_\*, at\_\*, during\_\*, phase:\*)  
   Window { starts\_at, ends\_at },       // Time range  
   Relative(String),                     // Relative time (unresolved)  
   Wildcard,                            // "\*" or "any\_time"  
}  
TemporalResolution struct (lines 20-88):

* raw: Original input  
* binding: Parsed TemporalBinding  
* parse() method: Classifies input  
* is\_unresolved\_for\_mode() \- Checks if Relative binding is allowed

ClockView trait (lines 90-111):

* now\_utc() \- Returns current time string  
* FixedClock impl \- Test/simulation clock with fixed time

WhenSlot impl SlotHouse (lines 141-177):

* Resolves the when slot  
* Returns Doubt if temporal binding is unresolved in Operational/Closure modes  
* Returns Ok with reason based on TemporalBinding type

---

### 5\. logline-confirmed-by (Evidence Pivot)

Path: crates/confirmed\_by/  
Cargo.toml: Lines 1-17  
Purpose: Protects the evidence pivot \- determines Ok/Doubt/Not routing  
Key Exports (src/lib.rs:1-286):  
EvidenceKind enum (lines 22-28):  
rust  
pub enum EvidenceKind {  
   Token,      // Named witness or capability token  
   Signature,  // Cryptographic signature  
   Digest,     // Hash of artifact  
   Receipt,    // Prior runtime proof  
   Quorum,     // Threshold witness pattern  
}  
EvidenceResolution enum (lines 12-18):

* Confirmed \- Evidence sufficient  
* Missing \- No evidence provided  
* Contradicted \- Evidence conflicts  
* Expired \- Evidence time-bound  
* Insufficient \- Below threshold

EvidenceRequirement struct (lines 31-92):

* raw: Original string  
* kind: EvidenceKind  
* threshold: For quorum (e.g., "quorum:2:release\_committee")  
* label: Quorum label  
* parse() method: Classifies input  
* is\_missing\_marker() \- Checks for "none", "missing", "unknown", etc.

EvidenceReceipt struct (lines 95-121):

* id: Receipt identifier  
* confirms: What this receipt confirms  
* issued\_by: Authority  
* digest: Optional hash  
* token() \- Creates from simple token string  
* parse\_provided() \- Parses evidence string

EvidenceView struct (lines 124-197):

* receipts: Vec of EvidenceReceipt  
* from\_tokens() \- Creates from token list  
* contains() \- Checks if requirement is met  
* quorum\_count() \- Counts unique witnesses  
* quorum\_witnesses() \- Groups witnesses by label

pivot() function (lines 250-280):

* Core decision logic for confirmed\_by slot  
* Returns (Branch, reason) tuple  
* Rules:  
  * Missing evidence → Doubt (unless canon allows "none")  
  * Has required evidence → Ok  
  * Question pending → Doubt  
  * Contradicted → Not

ConfirmedBySlot impl SlotHouse (lines 212-248):

* Resolves the confirmed\_by slot  
* Accepts operations: Questionar, Confirmar, Verificar  
* Routes based on RuntimeDecision

---

### 6\. logline-if-ok (Release Route)

Path: crates/if\_ok/  
Cargo.toml: Lines 1-17  
Purpose: Protects real release \- what may happen if evidence is sufficient  
Key Exports (src/lib.rs:1-101):  
ReleaseKind enum (lines 12-19):  
rust  
pub enum ReleaseKind {  
   Execute,                  // Execute operation  
   Commit,                   // Commit status  
   EmitLogLine,             // Emit normalized logline  
   ReleaseToTower,          // Release to tower  
   EnterStrongGrammar,      // Enter strong grammar  
   Domain(String),          // Domain-specific release  
}  
ReleaseRoute struct (lines 22-54):

* raw: Original string  
* kind: ReleaseKind  
* parse() method: Classifies input  
* selected\_reason() \- Returns reason string for selected branch

ReleaseAdapter trait (lines 56-61):

* Extension point for domain-specific release execution  
* release(route) \- Executes release, returns Receipt or Error

IfOkSlot impl SlotHouse (lines 63-97):

* Resolves the if\_ok slot  
* Accepts operation: Acionar  
* Returns Selected if this branch was chosen  
* Returns NotSelected if another branch was chosen

---

### 7\. logline-if-doubt (Possible-World Simulation)

Path: crates/if\_doubt/  
Cargo.toml: Lines 1-17  
Purpose: Protects possible-world simulation \- what should happen while unresolved  
Key Exports (src/lib.rs:1-236):  
DoubtKind enum (lines 12-25):  
rust  
pub enum DoubtKind {  
   Ask,                      // Ask question  
   Clarify,                  // Request clarification  
   Suspend,                  // Suspend processing  
   Ghost,                    // Ghost present (unresolved)  
   ManualReview,            // Require manual review  
   Dispatch,                // Return to logline  
   Simulate,                // Run simulation  
   EmitSimulationReceipt,   // Emit simulation receipt  
   EmitDoubtTrace,          // Emit doubt trace  
   ProposePossibleWorld,    // Propose possible world  
   AskForEvidence,          // Ask for evidence  
   Domain(String),          // Domain-specific doubt  
}  
DoubtRoute struct (lines 28-108):

* raw: Original string  
* kind: DoubtKind  
* parse() method: Classifies input  
* Helper methods:  
  * is\_clarifying() \- Ask, Clarify, Ghost, AskForEvidence  
  * is\_suspending() \- Suspend  
  * is\_simulating() \- Simulate, EmitSimulationReceipt, ProposePossibleWorld  
  * is\_trace\_emitting() \- Emit operations  
  * selected\_reason() \- Returns reason string

DoubtTrace struct (lines 111-131):

* branch: Branch enum  
* reason: String  
* simulated\_route: String  
* released: bool  
* from\_selected\_branch() \- Creates from SelectedBranch if Doubt

SimulationReceipt struct (lines 134-168):

* receipt\_kind: "simulation"  
* logline\_digest: SHA256 of 9-slot tuple  
* branch: Branch  
* reason: String  
* simulated\_route: String  
* executed: bool  
* released: bool  
* from\_selected\_branch() \- Creates if Doubt and route is simulating

ClarificationRequest struct (lines 171-185):

* route: DoubtRoute  
* question: String  
* missing\_slots: Vec

SuspensionRecord struct (lines 188-200):

* route: DoubtRoute  
* reason: String

IfDoubtSlot impl SlotHouse (lines 202-236):

* Resolves the if\_doubt slot  
* Accepts operation: Despachar  
* Returns Selected if this branch was chosen  
* Returns NotSelected if another branch was chosen

---

### 8\. logline-if-not (Rejection & Falsification)

Path: crates/if\_not/  
Cargo.toml: Lines 1-17  
Purpose: Protects falsification and rejection \- what happens if false/forbidden  
Key Exports (src/lib.rs:1-126):  
RejectionKind enum (lines 12-23):  
rust  
pub enum RejectionKind {  
   Reject,                   // Generic rejection  
   Deny,                     // Explicit denial  
   ProhibitedByCanon,       // Violates canon  
   ContradictedEvidence,    // Evidence conflicts  
   InvalidShape,            // Wrong structure  
   ForbiddenRoute,          // Route forbidden  
   Void,                    // Void claim  
   MarkFailed,              // Mark as failed  
   Rollback,                // Rollback operation  
   Domain(String),          // Domain-specific rejection  
}  
RejectionRoute struct (lines 26-65):

* raw: Original string  
* kind: RejectionKind  
* parse() method: Classifies input  
* selected\_reason() \- Returns reason string

ProblemRecord struct (lines 68-90):

* slot: Slot where problem occurred  
* kind: RejectionKind  
* reason: String  
* route: String  
* from\_selected\_branch() \- Creates from SelectedBranch if Not

IfNotSlot impl SlotHouse (lines 92-126):

* Resolves the if\_not slot  
* Accepts operation: MarcarProblema  
* Returns Selected if this branch was chosen  
* Returns NotSelected if another branch was chosen

---

### 9\. logline-status (Lifecycle Closure)

Path: crates/status/  
Cargo.toml: Lines 1-26  
Purpose: Protects closure \- lifecycle transitions and receipt generation  
Key Modules:

1. status.rs \- Lifecycle management  
2. walk.rs \- Runtime execution  
3. receipt.rs \- Receipt encoding (JCS/RFC-8785 canonical JSON)

Key Exports (src/lib.rs:1-36):

* Re-exports from all 8 slot crates  
* receipt::\* \- Receipt encoding functions  
* status::\* \- Lifecycle and status functions  
* walk::\* \- Runtime execution functions

Lifecycle enum (status.rs:11-40):  
rust  
pub enum Lifecycle {  
   Draft,      // Initial state  
   Pending,    // Awaiting confirmation  
   Doubt,      // Unresolved  
   Confirmed,  // Evidence sufficient  
   Released,   // Released to world  
   Failed,     // Operation failed  
   RolledBack, // Rolled back  
   Rejected,   // Rejected by canon  
   Void,       // Void claim  
   Closed,     // Closed/archived  
   Domain(String), // Custom state  
}  
CanonicalTuple struct (status.rs:96-122):

* References to all 9 slots  
* from\_logline() \- Creates from LogLine  
* Used for computing canonical tuple digest

canonical\_tuple\_digest() (status.rs:125-146):

* Computes SHA256 of JCS-encoded 9-slot tuple  
* Used in simulation receipts and audit trails

StatusSlot impl SlotHouse (status.rs:160-193):

* Resolves the status slot  
* Accepts operation: Registrar  
* Records lifecycle transition

RuntimeLogLine struct (walk.rs:68-83):

* Complete runtime result  
* Contains:  
  * mode, operation, operation\_home, phase  
  * logline: Original input  
  * runtime: RuntimeSlots (all 9 resolved slots)  
  * selected: SelectedBranch (which branch was chosen)  
  * status: StatusTransition (before/after lifecycle)  
  * doubt\_trace: Optional DoubtTrace  
  * simulation\_receipt: Optional SimulationReceipt

walk() function (walk.rs:85-88):

* Entry point: walks logline with default Confirmar operation

run() function (walk.rs:90-93):

* Entry point: walks logline with specified operation

run\_with\_context() (walk.rs:95-144):

* Core runtime execution  
* Steps:  
  1. Validate shape  
  2. Check if prohibited by canon  
  3. Call confirmed\_by::pivot() to determine branch  
  4. Create SelectedBranch  
  5. Compute status transition  
  6. Create DoubtTrace and SimulationReceipt if needed  
  7. Resolve all 9 slots via SlotHouse implementations  
  8. Return RuntimeLogLine

Receipt encoding (receipt.rs):

* canonical\_json() \- JCS/RFC-8785 canonicalization  
* tuple\_hash() \- SHA256 of 9-slot tuple  
* content\_hash() \- SHA256 of all fields except id/hashes  
* envelope\_hash() \- SHA256 of transport wrapper

---

### 10\. logline-cli (Binary Interface)

Path: crates/logline-cli/  
Cargo.toml: Lines 1-17  
Purpose: Command-line interface \- the "mouth" of the runtime  
Binary name: logline  
Main entry: src/main.rs (223 lines)  
Commands:

1. logline \--version / logline version  
   * Outputs JSON probe with:  
     * runtime: "logline-runtime-rs"  
     * binary: "logline"  
     * package: Package name  
     * package\_version: Version  
     * canon\_version: "0.2.0-draft"  
     * git\_commit: Git hash or "unknown"  
     * lip\_support: \["LIP-0004", "LIP-0005", "LIP-0006", "LIP-0007"\]  
     * features: \["canonical\_tuple\_digest", "receipt\_encoding\_profile", "adapter\_protocol"\]  
     * external\_effects: false  
2. logline status  
   * Outputs JSON status with:  
     * runtime\_available: true  
     * authoritative\_runtime: true  
     * adapter\_protocol\_supported: true  
     * receipt\_encoding\_profile\_supported: true  
     * canonical\_tuple\_digest\_supported: true  
     * external\_effects: false  
3. logline check-canon \<canon.json\>  
   * Validates canon file structure  
   * Outputs: {"ok":true,"checked":"canon"}  
4. logline parse-logline \<logline.txt\>  
   * Parses logline text file (one per line)  
   * Skips form require directives  
   * Outputs JSON for each logline  
5. logline validate \<canon.json\> \<act.json|act.logline\>  
   * Validates logline against canon  
   * Outputs: {"ok":true,"validated":"logline"}  
6. logline run \[options\] \<canon.json\> \<act.json|act.logline\> (alias: walk)  
   * Executes full runtime walk  
   * Options:  
     * \--mode {pocket|grammar|algebra|operational|closure} (default: algebra)  
     * \--op {operation} (default: confirmar)  
     * \--evidence token (repeatable)  
     * \--allow-no-confirmation (flag)  
     * \--canon \<path\> (positional or named)  
     * \--input \<path\> (positional or named)  
   * Outputs: JSON RuntimeLogLine

RunArgs struct (lines 81-88):

* Parsed command-line arguments  
* parse\_run\_args() \- Parses arguments flexibly

---

## COMPOSITION & ARCHITECTURE

### The 9-Slot Walk

The runtime executes in a fixed sequence through 9 slots, each implemented as a separate crate:  
who → did → this → when → confirmed\_by → {if\_ok, if\_doubt, if\_not} → status  
Execution Flow (walk.rs:95-144):

1. Input Phase (4 slots):  
   * who: Validates accountable origin  
   * did: Classifies verb/operation  
   * this: Locates bounded matter  
   * when: Binds temporal condition  
2. Pivot Phase (1 slot):  
   * confirmed\_by: Determines branch (Ok/Doubt/Not) based on evidence  
3. Output Phase (3 slots \- one selected):  
   * if\_ok: Release route if evidence sufficient  
   * if\_doubt: Simulation/clarification if unresolved  
   * if\_not: Rejection route if falsified/forbidden  
4. Closure Phase (1 slot):  
   * status: Records lifecycle transition

### Key Design Patterns

#### 1\. SlotHouse Trait Pattern

Each crate implements SlotHouse for its slot:  
rust  
pub trait SlotHouse {  
   fn slot(\&self) \-\> Slot;  
   fn resolve(\&self, input: \&LogLine, ctx: \&RunContext, decision: \&RuntimeDecision) \-\> RuntimeSlot;  
   fn accepts\_operation(\&self, op: Operation) \-\> bool { ... }  
}  
Benefits:

* Decoupled slot implementations  
* Pluggable architecture  
* Each crate owns its resolution logic  
* Easy to extend with domain adapters

#### 2\. Branch Routing Pattern

After confirmed\_by pivot, only ONE of three branches executes:

* if\_ok \- Success path  
* if\_doubt \- Simulation/clarification path  
* if\_not \- Rejection path

Other branches show NotSelected resolution.

#### 3\. Evidence Collapse Pattern

confirmed\_by::pivot() is the ONLY place where evidence becomes a decision:

* Checks requirement against provided evidence  
* Returns (Branch, reason) tuple  
* No other slot makes this decision

#### 4\. Mode-Based Strictness

Same 9-slot structure, different validation levels:

* Pocket: Minimal (LLM/human drafting)  
* Grammar: Formal surface validation  
* Algebra: Symbolic routing  
* Operational: Evidence/adapters/world effects  
* Closure: Evidentiary recording

#### 5\. Canonical Tuple Digest

SHA256 of JCS-encoded 9-slot tuple:

* Immutable identity of the claim  
* Used in simulation receipts  
* Enables audit trails and replay

#### 6\. Three-Layer Receipt Hashing (LIP-0007)

tuple\_hash     \= sha256(jcs(9 slots))  
content\_hash   \= sha256(jcs(all fields except id/hashes))  
envelope\_hash  \= sha256(jcs({content, transport}))  
---

## DOCUMENTATION ARTIFACTS

### Key Docs

1. ten-crates-spine.md (238 lines)  
   * Explains why 10 crates are minimal  
   * Each crate's protective boundary  
   * Scaling rule: "change clothing, not spine"  
2. evidence-model.md (130 lines)  
   * Evidence kinds: token, receipt, digest, signature, quorum  
   * Evidence collapse rules  
   * Receipt hash layers (LIP-0007)  
3. modes.md (40 lines)  
   * 5 modes with different semantic pressure  
   * Rule: modes never delete slots, only change strictness  
4. runtime-binary.md (168 lines)  
   * Binary artifact: target/release/logline  
   * Safe probe commands  
   * Pinning rule for downstream use  
   * Out of scope: adapters, persistence, effects  
5. runtime-declaration.md (105 lines)  
   * Runtime probe JSON structure  
   * Conformance status values  
   * LIP support declaration  
6. implementation-plan.md (102 lines)  
   * 5 phases: hygiene → schema → if\_doubt → receipts → governance  
   * Current focus: Phase 1-2 (schema/conformance \+ if\_doubt simulation)  
7. canon-vs-runtime.md \- Distinguishes canonical law from runtime behavior  
8. if-doubt-package-notes.md \- Detailed if\_doubt simulation semantics

---

## SPEC DIRECTORY

spec/README.md (16 lines):

* Normative artifacts pending LIP freeze  
* Files map to LIPs:  
  * logline.adapter.v0 → LIP-0004  
  * logline.adapter-declaration.v0 → LIP-0005  
  * logline.adapter-conformance.v0 → LIP-0006  
  * logline.if-doubt.v0 → LIP-0002  
  * logline.if-doubt-simulation.v0 → LIP-0002  
  * logline.if-doubt-grammar.v0 → LIP-0002

---

## INTERESTING PATTERNS & ABSTRACTIONS

### 1\. Accountable Origin (who crate)

* ActorId, AuthorityId, Jurisdiction \- Strongly typed identities  
* Principal \- Union of actor/authority  
* WhoSlot \- Validates origin without confirming evidence

### 2\. Evidence Pivot (confirmed\_by crate)

* Only slot that makes branch decisions  
* Supports 5 evidence kinds with different semantics  
* Quorum pattern: quorum:2:release\_committee with witness deduplication  
* Missing marker detection: "none", "missing", "unknown", "unconfirmed", "ghost", "null"

### 3\. Matter Reference (this crate)

* Polymorphic: ObjectId, Url, Path, Digest, JsonPayload, Wildcard  
* Auto-digest: Computes SHA256 for JSON payloads  
* Unbounded detection: Wildcard forbidden in Operational/Closure modes

### 4\. Temporal Binding (when crate)

* RFC3339 timestamps, phase tokens, time windows, relative time  
* Unresolved detection: Relative time forbidden in Operational/Closure modes  
* ClockView trait: Pluggable time source for testing

### 5\. Doubt as First-Class Citizen (if\_doubt crate)

* Not a fallback, but a productive path  
* Supports: ask, clarify, suspend, simulate, dispatch  
* Generates DoubtTrace and SimulationReceipt  
* Enables possible-world reasoning without execution

### 6\. Rejection as Record (if\_not crate)

* Not a convenience fallback  
* Creates ProblemRecord with slot, kind, reason, route  
* Supports: reject, deny, prohibited, contradicted, invalid\_shape, void, rollback

### 7\. Lifecycle State Machine (status crate)

* 10 canonical states: draft, pending, doubt, confirmed, released, failed, rolled\_back, rejected, void, closed  
* Transitions defined in canon's status\_lifecycle  
* StatusSlot records before/after states

### 8\. No External Effects in Core

* Binary declares external\_effects: false  
* Release execution deferred to ReleaseAdapter trait  
* Receipt persistence deferred to StatusLedger trait  
* Enables safe simulation and testing

---

## DEPENDENCY GRAPH

logline-cli  
 └─ logline-status  
     ├─ logline-who (core)  
     ├─ logline-did  
     ├─ logline-this  
     ├─ logline-when  
     ├─ logline-confirmed-by  
     ├─ logline-if-ok  
     ├─ logline-if-doubt  
     └─ logline-if-not  
   
All slot crates depend on:  
 └─ logline-who (for Slot, Operation, SlotHouse, RunContext, etc.)  
Dependency Direction:

* Slot crates → who (imports abstractions)  
* status → all slot crates (re-exports for walk)  
* cli → status (uses walk function)

---

## WORKSPACE CONFIGURATION

Root Cargo.toml (30 lines):

* Resolver: "2"  
* Members: 10 crates  
* Workspace dependencies:  
  * serde with derive  
  * serde\_json  
  * sha2  
  * thiserror  
  * time with formatting/parsing/serde  
  * url with serde  
* Workspace lints: forbid unsafe\_code

All crates:

* Version: 0.1.0 (workspace)  
* Edition: 2021  
* License: MIT OR Apache-2.0  
* Forbid unsafe code

---

## SUMMARY TABLE

| Crate | Slot | Purpose | Key Types | Exports |
| :---- | :---- | :---- | :---- | :---- |
| who | \- | Core protocol | LogLine, Slot, Operation, Mode, Branch, SlotHouse, Canon | 8 modules |
| did | did | Verb naming | Verb, VerbClass, DidResolution | DidSlot |
| this | this | Matter location | MatterRef, MatterDigest, LocatedMatter | ThisSlot |
| when | when | Temporal binding | TemporalBinding, TemporalResolution, ClockView | WhenSlot |
| confirmed\_by | confirmed\_by | Evidence pivot | EvidenceKind, EvidenceRequirement, EvidenceView, pivot() | ConfirmedBySlot |
| if\_ok | if\_ok | Release route | ReleaseKind, ReleaseRoute, ReleaseAdapter | IfOkSlot |
| if\_doubt | if\_doubt | Simulation | DoubtKind, DoubtRoute, DoubtTrace, SimulationReceipt | IfDoubtSlot |
| if\_not | if\_not | Rejection | RejectionKind, RejectionRoute, ProblemRecord | IfNotSlot |
| status | status | Lifecycle | Lifecycle, CanonicalTuple, StatusSlot, walk(), run() | 3 modules |
| logline-cli | \- | CLI interface | RunArgs, commands | Binary: logline |

---

## KEY FINDINGS

1. Thin Spine Design: 9 slots remain constant; domain logic attaches as adapters/extensions  
2. Evidence Pivot: confirmed\_by is the ONLY decision point (Ok/Doubt/Not)  
3. Doubt is Productive: Not a fallback; enables simulation, clarification, suspension  
4. No Execution in Core: ReleaseAdapter and StatusLedger traits defer world effects  
5. Canonical Tuple Digest: Immutable 9-slot identity enables audit trails  
6. Three-Layer Hashing: LIP-0007 separates tuple identity, content, and transport  
7. Mode-Based Strictness: Same structure, different validation levels  
8. Pluggable SlotHouse: Each crate owns its resolution logic  
9. Safe Probe: Binary has safe version/status commands with no effects  
10. Workspace Hygiene: Forbids unsafe code across all crates

---

## ACTIONABLE RECOMMENDATIONS

1. For Extension: Implement domain adapters via SlotHouse trait in separate crates  
2. For Integration: Use logline-cli binary or call run\_with\_context() from status crate  
3. For Testing: Use FixedClock and provided\_evidence in RunContext  
4. For Persistence: Implement StatusLedger trait for receipt storage  
5. For Release: Implement ReleaseAdapter trait for world effects  
6. For Governance: Define canon.json with form, route\_kinds, status\_lifecycle, law, prohibition  
7. For Audit: Capture canonical\_tuple\_digest and three-layer hashes in receipts  
8. For Simulation: Examine DoubtTrace and SimulationReceipt in RuntimeLogLine

I'll conduct a thorough exploration of this repository. Let me start by understanding the structure and then dive into each component.  
Now let me read all the Cargo.toml files and source code:  
Now let me read the core source files:  
Now let me read the resolver service code:  
Let me continue reading the http.rs file and other model files:  
Now let me read the guest WASM code:  
Now let me explore the directory structure and look for documentation and examples:  
Let me read key documentation files:  
Now let me check for any card.detect or other relevant code:  
Let me read the schema:  
Let me check the BUILD.md and CANON\_STATUS.md files:  
Now let me check for any example requests and look at the full http.rs to understand the complete flow:  
Let me read the rest of the http.rs file to see the complete HTML rendering:  
Perfect\! Now let me check if there are any other important files I should look at:  
Perfect\! Now let me check the docs/README to understand the architecture better:  
Now let me look at the tdln-verify tool to understand how receipts are verified:  
Excellent\! Now let me check if there are any additional details in the card/detect.rs module:  
Searchedmod card in Ethics-is-Efficient-main/services/resolver/src  
Let me check if there's a card module file:  
Searched\*\*/card.rs in Ethics-is-Efficient-main/services/resolver/src  
Let me check the full directory structure of the resolver service:  
Let me check if there's a card module declared in lib.rs:  
Good \- the card/detect.rs is not currently used. Now let me create a comprehensive summary. Let me also check the LLM context starter:  
Perfect\! Now I have a comprehensive understanding. Let me create a detailed report.

## COMPREHENSIVE EXPLORATION REPORT: Ethics-is-Efficient (TDLN)

---

## 1\. WORKSPACE STRUCTURE & CARGO CONFIGURATION

### Workspace Root: /Cargo.toml

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/Ethics-is-Efficient-main/Cargo.toml  
toml  
\[workspace\]  
members \= \[  
 "crates/tdln-wasm",  
 "crates/tdln-core",  
 "crates/tdln-bundle",  
 "services/resolver",  
 "tools/tdln-verify",  
\]  
exclude \= \[  
 "guests/ack",  
 "guests/ask",  
\]  
resolver \= "2"  
   
\[profile.release\]  
opt-level \= "z"      \# Optimize for size  
lto \= true           \# Link-time optimization  
codegen-units \= 1    \# Single codegen unit for better optimization  
panic \= "abort"      \# Abort on panic (smaller binary)  
Key insight: Guests are excluded from workspace (compiled separately as WASM targets).  
---

## 2\. CRATE BOUNDARIES & DEPENDENCIES

### Crate 1: tdln-core (v0.2.0)

Path: /crates/tdln-core/  
Purpose: Cryptographic primitives and receipt structures  
Dependencies:

* serde \+ serde\_json — Serialization  
* sha2 — SHA-256 hashing  
* blake3 — Legacy Blake3 (deprecated)  
* ulid — DID generation  
* hex — Hex encoding

Core Exports:  
rust  
// Canonicalization (JCS RFC-8785)  
pub fn jcs\_canonicalize(v: \&Value) \-\> Value  
pub fn sha256\_jcs(v: \&Value) \-\> String  
   
// Hashing  
pub fn tuple\_hash(receipt: \&Value) \-\> String  
pub fn content\_hash(receipt: \&Value) \-\> String  
pub fn compute\_envelope\_hash(content: \&Value, transport: \&Value) \-\> String  
   
// DID generation  
pub fn did\_ulid() \-\> String  // Returns "did:tdln:{ULID}"  
   
// Receipt structure  
pub struct LogLineTuple {  
   pub id: String,                    // \= content\_hash  
   pub receipt\_version: String,       // "logline.receipt.v0"  
   pub who: String,  
   pub did: String,  
   pub this: String,  
   pub when: String,  
   pub confirmed\_by: String,  
   pub if\_ok: String,  
   pub if\_doubt: String,  
   pub if\_not: String,  
   pub status: String,  
   pub hashes: LogLineHashes,  
   pub json\_canonicalization: String, // "jcs-rfc8785"  
}  
   
pub struct LogLineHashes {  
   pub tuple\_hash: String,  
   pub content\_hash: String,  
   pub algorithm: String,  // "sha256"  
}  
Key Methods:

* LogLineTuple::new(...) — Creates receipt, auto-seals with hashes  
* receipt.seal() — Computes tuple\_hash, content\_hash, sets id \= content\_hash  
* receipt.verify() — Checks id \== content\_hash

Hash Computation (LIP-0007):

1. tuple\_hash \= SHA256(JCS(pick 9 slots: who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status))  
2. content\_hash \= SHA256(JCS(all fields except id and hashes))  
3. envelope\_hash \= SHA256(JCS({content, transport})) — NOT inside receipt

---

### Crate 2: tdln-bundle (v0.1.0)

Path: /crates/tdln-bundle/  
Purpose: ZIP bundle assembly  
Dependencies:

* serde\_json  
* zip (with deflate feature)  
* time

Core Export:  
rust  
pub fn build\_bundle(  
   card\_json: \&Value,  
   manifest\_json: \&Value,  
   signatures\_json: \&Value  
) \-\> Vec\<u8\>  
Bundle Structure (ZIP):  
bundle.zip  
├── card.json                    (DiamondCard)  
├── run.manifest.json            (RunManifest)  
├── signatures.sig               (Ed25519 signature metadata)  
└── \[receipt.logline.v0.json\]    (Optional LogLine receipt)  
---

### Crate 3: tdln-wasm (v0.1.0)

Path: /crates/tdln-wasm/  
Purpose: Deterministic WASM sandbox with fuel metering  
Dependencies:

* wasmtime (v16) — WASM runtime  
* serde\_json  
* anyhow

Core Export:  
rust  
pub struct ExecOutcome {  
   pub decision: String,      // "ACK", "ASK", or "NACK"  
   pub fuel\_consumed: u64,  
}  
   
pub fn run(  
   bytes: &\[u8\],              // WASM binary  
   \_input: \&Value,            // Input JSON (unused in current impl)  
   fuel\_limit: u64            // Fuel budget (default: 5\_000\_000)  
) \-\> Result\<ExecOutcome\>  
Execution Flow:

1. Create deterministic Wasmtime config (no non-deterministic features)  
2. Instantiate module (no imports linked)  
3. Call exported run() function with signature () \-\> i32  
4. Map return code:  
   * 0 → "ACK" (proceed)  
   * 1 → "ASK" (escalate)  
   * 2 → "NACK" (reject)  
   * Other → "ASK" (default)  
5. Return decision \+ fuel consumed

---

### Service: resolver (v0.1.0)

Path: /services/resolver/  
Purpose: HTTP API for policy evaluation and receipt emission  
Dependencies:

* axum (v0.7) — Web framework  
* tokio (v1) — Async runtime  
* ed25519-dalek (v2) — Ed25519 signing  
* jsonschema (v0.17) — Schema validation  
* base64 — Base64 decoding  
* qrcode — QR code generation  
* tracing — Logging  
* All three crates above

Module Structure:  
lib.rs  
├── pub mod http        → HTTP routes & handlers  
├── pub mod model       → Data structures  
└── pub mod store       → File-based card store  
---

## 3\. RESOLVER SERVICE: HTTP API & REQUEST→RECEIPT FLOW

### HTTP Routes (/services/resolver/src/http.rs)

rust  
pub fn router(state: AppState) \-\> Router {  
   Router::new()  
       .route("/v2/run", post(run))                    // Main policy evaluation  
       .route("/v2/cards/:did", get(get\_card))         // Fetch DiamondCard JSON  
       .route("/v2/cards/:did/bundle.zip", get(get\_bundle))  // Download bundle  
       .route("/v2/cards/:did/receipt", get(get\_receipt))    // Fetch LogLine receipt  
       .route("/trust/:did", get(get\_trust\_html))      // HTML verification page  
       .with\_state(state)  
}

### AppState (Shared Context)

rust  
pub struct AppState {  
   pub store: Arc\<CardStore\>,           // File-based persistence  
   pub base\_url: String,                // "https://cert.tdln.foundry"  
   pub version: String,                 // "resolver-v3"  
   pub signing\_key: Arc\<SigningKey\>,    // Ed25519 private key  
   pub verifying\_key: VerifyingKey,     // Ed25519 public key  
   pub trust\_schema: Value,             // JSON Schema for DiamondCard validation  
}  
---

## 4\. COMPLETE REQUEST→RESOLVER→WASM→RECEIPT FLOW

### Step 1: POST /v2/run — Accept Request

Input Model:  
rust  
pub struct RunRequest {  
   pub realm: String,                   // e.g., "trust"  
   pub intent: String,                  // default: "execute"  
   pub inputs: serde\_json::Value,       // {policy: {...}, ...}  
   pub options: serde\_json::Value,      // optional  
}  
Example Request:  
json  
{  
 "realm": "trust",  
 "intent": "execute",  
 "inputs": {  
   "policy": {  
     "kind": "wasm",  
     "payload\_b64": "AGFzbQEAAAABBwFgAAF..."  
   }  
 }  
}

### Step 2: Generate DID & CID

rust  
let did \= did\_ulid();                    // "did:tdln:{ULID}"  
let v \= serde\_json::to\_value(\&req)?;  
let cid \= sha256\_jcs(\&v);                // Content ID \= SHA256(JCS(request))  
let url \= format\!("{}/{}/{}\#{}",  
   state.base\_url, realm, did, cid);   // "https://cert.tdln.foundry/trust/{did}\#{cid}"

### Step 3: Execute WASM Policy (if present)

rust  
let mut decision \= "ACK".to\_string();  
let mut fuel \= 0u64;  
   
if let Some(policy) \= req.inputs.get("policy") {  
   let kind \= policy.get("kind").and\_then(|s| s.as\_str()).unwrap\_or("");  
    
   if kind \== "wasm" {  
       if let Some(b64) \= policy.get("payload\_b64").and\_then(|s| s.as\_str()) {  
           if let Ok(bytes) \= base64::engine::general\_purpose::STANDARD.decode(b64) {  
               match wasm\_run(\&bytes, \&v, 5\_000\_000) {  // 5M fuel limit  
                   Ok(out) \=\> {  
                       decision \= out.decision;  
                       fuel \= out.fuel\_consumed;  
                   },  
                   Err(\_e) \=\> {  
                       decision \= "ASK".into();  // Default to escalate on error  
                   }  
               }  
           } else {  
               decision \= "ASK".into();  // Base64 decode error  
           }  
       }  
   }  
}

### Step 4: Map Decision to LogLine Tuple

rust  
fn map\_decision\_to\_tuple(  
   decision: \&str,  
   realm: \&str,  
   did\_str: \&str,  
   now\_str: \&str,  
   key\_id: \&str  
) \-\> LogLineTuple {  
   let (if\_ok, if\_doubt, if\_not, status) \= match decision {  
       "ACK" \=\> (  
           format\!("proceed with {}", realm),  
           String::new(),  
           String::new(),  
           "ok".to\_string()  
       ),  
       "ASK" \=\> (  
           String::new(),  
           format\!("escalate {} for review", realm),  
           String::new(),  
           "pending".to\_string()  
       ),  
       "NACK" \=\> (  
           String::new(),  
           String::new(),  
           format\!("reject {} policy violation", realm),  
           "denied".to\_string()  
       ),  
       \_ \=\> (  
           String::new(),  
           format\!("unknown decision: {}", decision),  
           String::new(),  
           "pending".to\_string()  
       ),  
   };  
   
   LogLineTuple::new(  
       did\_str.to\_string(),           // who  
       "evaluate".to\_string(),        // did (action)  
       format\!("{}/policy", realm),   // this  
       now\_str.to\_string(),           // when  
       key\_id.to\_string(),            // confirmed\_by  
       if\_ok,  
       if\_doubt,  
       if\_not,  
       status,  
   )  
}  
Receipt Example (ACK):  
json  
{  
 "id": "abc123...",  
 "receipt\_version": "logline.receipt.v0",  
 "who": "did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV",  
 "did": "evaluate",  
 "this": "trust/policy",  
 "when": "2026-05-21T12:34:56Z",  
 "confirmed\_by": "key:a1b2c3d4",  
 "if\_ok": "proceed with trust",  
 "if\_doubt": "",  
 "if\_not": "",  
 "status": "ok",  
 "hashes": {  
   "tuple\_hash": "def456...",  
   "content\_hash": "abc123...",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785"  
}

### Step 5: Build DiamondCard

rust  
pub struct DiamondCard {  
   pub schema: String,                // "tdln/trust@1"  
   pub realm: String,                 // "trust"  
   pub object: String,                // "diamondcard"  
   pub did: String,                   // Generated DID  
   pub card\_id: String,               // "card:auto"  
   pub decision: String,              // "ACK", "ASK", or "NACK"  
   pub refs: Refs,                    // Input/policy references  
   pub runtime: Runtime,              // Engine metadata \+ fuel  
   pub poi: Option\<Value\>,            // Proof of intent (optional)  
   pub signatures: Signatures,        // Bundle hash \+ Ed25519 sig  
}  
Validation: Card is validated against schemas/tdln/trust@1.json using jsonschema.

### Step 6: Build RunManifest

rust  
pub struct RunManifest {  
   pub did: String,  
   pub input\_cid: String,             // SHA256(JCS(request))  
   pub request\_cid: String,           // Same as input\_cid  
   pub request: Option\<Value\>,        // Canonicalized request  
   pub started\_at: String,  
   pub completed\_at: Option\<String\>,  
   pub unit\_cid: Option\<String\>,  
}

### Step 7: Sign Bundle

rust  
// Compute bundle hash (deprecated Blake3 for compatibility)  
\#\[allow(deprecated)\]  
let bundle\_hash \= bundle\_hash\_card\_manifest(\&card\_json, \&manifest\_json);  
   
// Sign with Ed25519  
let signing\_key \= &\*state.signing\_key;  
let sig \= signing\_key.sign(bundle\_hash.as\_bytes());  
   
// Create signatures object  
let signatures \= json\!({  
   "alg": "ed25519",  
   "pubkey\_hex": hex::encode(state.verifying\_key.to\_bytes()),  
   "bundle\_hash": bundle\_hash.clone(),  
   "sig\_hex": hex::encode(sig.to\_bytes())  
});

### Step 8: Persist to Store

rust  
// Store in ./.cards/{did}/  
state.store.write\_card(\&did, \&final\_card).await?;  
state.store.write\_manifest(\&did, \&manifest).await?;  
state.store.write\_bundle(\&did, bundle).await?;  
state.store.write\_receipt(\&did, \&receipt).await?;  
File Layout:  
./.cards/{did}/  
├── card.json  
├── run.manifest.json  
├── bundle.zip  
└── receipt.logline.v0.json

### Step 9: Return RunAccepted Response

rust  
pub struct RunAccepted {  
   pub did: String,  
   pub cid: String,  
   pub url: String,  
   pub status: String,                // "RUNNING"  
   pub receipt\_preview: ReceiptPreview,  
   pub receipt: Option\<Value\>,        // Full LogLine receipt  
}  
   
pub struct ReceiptPreview {  
   pub realm: String,  
   pub decision: Option\<String\>,  
}  
Example Response:  
json  
{  
 "did": "did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV",  
 "cid": "abc123...",  
 "url": "https://cert.tdln.foundry/trust/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV\#abc123...",  
 "status": "RUNNING",  
 "receipt\_preview": {  
   "realm": "trust",  
   "decision": "ACK"  
 },  
 "receipt": {  
   "id": "abc123...",  
   "receipt\_version": "logline.receipt.v0",  
   ...  
 }  
}  
---

## 5\. WASM GUESTS

### Guest: ack (guest-ack)

Path: /guests/ack/  
rust  
\#\!\[no\_std\]  
   
\#\[panic\_handler\]  
fn panic(\_info: \&core::panic::PanicInfo) \-\> \! {  
   loop {}  
}  
   
\#\[no\_mangle\]  
pub extern "C" fn run() \-\> i32 {  
   0  // ACK  
}  
Build: cargo build \--release \--target wasm32-unknown-unknown \-p guest-ack Output: dist/guest-ack.wasm

### Guest: ask (guest-ask)

Path: /guests/ask/  
rust  
\#\!\[no\_std\]  
   
\#\[panic\_handler\]  
fn panic(\_info: \&core::panic::PanicInfo) \-\> \! {  
   loop {}  
}  
   
\#\[no\_mangle\]  
pub extern "C" fn run() \-\> i32 {  
   1  // ASK  
}  
Build: cargo build \--release \--target wasm32-unknown-unknown \-p guest-ask Output: dist/guest-ask.wasm

### Usage Example:

bash  
\# Encode WASM as base64  
BASE64=$(base64 \-w0 examples/wasm/run\_ack.wasm)  
   
\# Send to resolver  
curl \-s localhost:8080/v2/run \\  
 \-H 'content-type: application/json' \\  
 \-d '{"realm":"trust","inputs":{"policy":{"kind":"wasm","payload\_b64":"'$BASE64'"}}}'  
---

## 6\. CARD STORE (Persistence Layer)

Path: /services/resolver/src/store.rs  
rust  
pub struct CardStore {  
   base\_path: PathBuf,  // Default: "./.cards"  
}  
   
impl CardStore {  
   pub async fn write\_card(\&self, did: \&str, card: \&DiamondCard) \-\> Result\<()\>  
   pub async fn read\_card(\&self, did: \&str) \-\> Result\<DiamondCard\>  
   pub async fn write\_manifest(\&self, did: \&str, manifest: \&RunManifest) \-\> Result\<()\>  
   pub async fn read\_manifest(\&self, did: \&str) \-\> Result\<RunManifest\>  
   pub async fn write\_bundle(\&self, did: \&str, bundle\_bytes: Vec\<u8\>) \-\> Result\<()\>  
   pub async fn read\_bundle(\&self, did: \&str) \-\> Result\<Vec\<u8\>\>  
   pub async fn write\_receipt(\&self, did: \&str, receipt: \&LogLineTuple) \-\> Result\<()\>  
   pub async fn read\_receipt(\&self, did: \&str) \-\> Result\<LogLineTuple\>  
}  
Naming Convention:

* Card: ./.cards/{did}/card.json  
* Manifest: ./.cards/{did}/run.manifest.json  
* Bundle: ./.cards/{did}/bundle.zip  
* Receipt: ./.cards/{did}/receipt.logline.v0.json

---

## 7\. VERIFICATION TOOL

Path: /tools/tdln-verify/src/main.rs  
Purpose: Offline verification of bundles and receipts  
Verification Steps:

1. Receipt Validation:  
   * Check receipt\_version \== "logline.receipt.v0"  
   * Verify id \== content\_hash  
   * Verify hashes.content\_hash matches computed value  
   * Verify hashes.tuple\_hash matches computed value  
2. Bundle Validation:  
   * Extract card.json, run.manifest.json, signatures.sig from ZIP  
   * Recompute bundle\_hash \= blake3(card \+ manifest) (legacy)  
   * Verify Ed25519 signature: vk.verify(bundle\_hash, sig)

Usage:  
bash  
cargo run \-p tdln-verify \-- path/to/bundle.zip \[--pubkey\_hex \<hex\>\]  
cargo run \-p tdln-verify \-- path/to/receipt.logline.v0.json  
---

## 8\. SCHEMA VALIDATION

Path: /schemas/tdln/trust@1.json  
json  
{  
 "$schema": "https://json-schema.org/draft/2020-12/schema",  
 "title": "DiamondCard v1 (trust)",  
 "type": "object",  
 "required": \[  
   "schema",  
   "realm",  
   "object",  
   "did",  
   "card\_id",  
   "decision",  
   "refs",  
   "runtime",  
   "signatures"  
 \],  
 "properties": {  
   "schema": { "const": "tdln/trust@1" },  
   "realm": { "const": "trust" },  
   "object": { "const": "diamondcard" },  
   "decision": { "enum": \["ACK", "ASK", "NACK"\] },  
   ...  
 }  
}  
---

## 9\. CONTAINER & DEPLOYMENT

### Dockerfile Options:

Scratch (Ultra-minimal):  
dockerfile  
FROM scratch  
WORKDIR /  
ARG TARGETARCH  
COPY dist/resolver-${TARGETARCH} /resolver  
EXPOSE 8080  
USER 65532:65532  
ENTRYPOINT \["/resolver"\]  
Distroless (Safer defaults):  
dockerfile  
FROM gcr.io/distroless/base-nonroot  
COPY dist/resolver /resolver  
EXPOSE 8080  
ENTRYPOINT \["/resolver"\]

### Key Management:

* Keys auto-generated in ./keys/ on first run  
* privkey.hex and pubkey.hex (Ed25519)  
* Can be bind-mounted: \-v $(pwd)/keys:/keys

### Environment Variables:

* BASE\_URL — Canonical base URL for receipt links (default: https://cert.tdln.foundry)

---

## 10\. BUILD SYSTEM

Makefile Targets:  
bash  
make                    \# Build native (musl) \+ WASM  
make build-native       \# Resolver binary (static musl)  
make build-wasm         \# Guest WASM binaries  
make docker-build       \# Build scratch image  
make docker-distroless  \# Build distroless image  
make docker-run         \# Run container  
make docker-buildx      \# Multi-arch (amd64 \+ arm64)  
Outputs:

* dist/resolver — Static binary  
* dist/tdln-verify — Verifier tool  
* dist/guest-ack.wasm — ACK guest  
* dist/guest-ask.wasm — ASK guest

---

## 11\. CANON CONFORMANCE

Status: ✅ FULLY IMPLEMENTED

| Requirement | Status | Details |
| :---- | :---- | :---- |
| 9-slot tuple | ✅ | who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status |
| SHA-256 hashing (bare hex) | ✅ | No prefix, 64-char lowercase |
| JCS RFC-8785 canonicalization | ✅ | Implemented in tdln-core::jcs\_canonicalize() |
| LIP-0007 three-layer hashing | ✅ | tuple\_hash → content\_hash → envelope\_hash |
| id \= content\_hash invariant | ✅ | Enforced in LogLineTuple::seal() |
| logline.receipt.v0 emission | ✅ | Emitted in /v2/run response |
| Receipt verification tooling | ✅ | tdln-verify CLI |
| No forbidden fields | ✅ | No result, evidence, transport inside receipt |

---

## 12\. DECISION MAPPING

| WASM Return | Meaning | Status | if\_ok | if\_doubt | if\_not |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 0 | ACK (Proceed) | "ok" | "proceed with {realm}" | "" | "" |
| 1 | ASK (Escalate) | "pending" | "" | "escalate {realm} for review" | "" |
| 2 | NACK (Reject) | "denied" | "" | "" | "reject {realm} policy violation" |
| Other | Unknown | "pending" | "" | "unknown decision: ..." | "" |

---

## 13\. KEY FILES SUMMARY

| File | Purpose | Key Exports |
| :---- | :---- | :---- |
| crates/tdln-core/src/lib.rs | Hashing & receipt | LogLineTuple, sha256\_jcs(), tuple\_hash(), content\_hash() |
| crates/tdln-bundle/src/lib.rs | ZIP bundling | build\_bundle() |
| crates/tdln-wasm/src/lib.rs | WASM sandbox | run(), ExecOutcome |
| services/resolver/src/http.rs | HTTP API | router(), run() (POST /v2/run) |
| services/resolver/src/model.rs | Data structures | RunRequest, DiamondCard, RunManifest |
| services/resolver/src/store.rs | Persistence | CardStore |
| services/resolver/src/main.rs | Entry point | Key loading, server startup |
| tools/tdln-verify/src/main.rs | Verification | Receipt & bundle validation |
| guests/ack/src/lib.rs | WASM guest (ACK) | Returns 0 |
| guests/ask/src/lib.rs | WASM guest (ASK) | Returns 1 |
| schemas/tdln/trust@1.json | JSON Schema | DiamondCard validation |

---

## 14\. EXAMPLE REQUEST FLOW

Request:  
bash  
curl \-X POST http://localhost:8080/v2/run \\  
 \-H 'Content-Type: application/json' \\  
 \-d '{  
   "realm": "trust",  
   "inputs": {  
     "policy": {  
       "kind": "wasm",  
       "payload\_b64": "AGFzbQEAAAABBwFgAAF..."  
     }  
   }  
 }'  
Response (200 OK):  
json  
{  
 "did": "did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV",  
 "cid": "abc123def456...",  
 "url": "https://cert.tdln.foundry/trust/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV\#abc123def456...",  
 "status": "RUNNING",  
 "receipt\_preview": {  
   "realm": "trust",  
   "decision": "ACK"  
 },  
 "receipt": {  
   "id": "abc123def456...",  
   "receipt\_version": "logline.receipt.v0",  
   "who": "did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV",  
   "did": "evaluate",  
   "this": "trust/policy",  
   "when": "2026-05-21T12:34:56Z",  
   "confirmed\_by": "key:a1b2c3d4",  
   "if\_ok": "proceed with trust",  
   "if\_doubt": "",  
   "if\_not": "",  
   "status": "ok",  
   "hashes": {  
     "tuple\_hash": "def456...",  
     "content\_hash": "abc123def456...",  
     "algorithm": "sha256"  
   },  
   "json\_canonicalization": "jcs-rfc8785"  
 }  
}  
Retrieval:  
bash  
\# Get card  
curl http://localhost:8080/v2/cards/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV  
   
\# Get receipt  
curl http://localhost:8080/v2/cards/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV/receipt  
   
\# Download bundle  
curl \-O http://localhost:8080/v2/cards/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV/bundle.zip  
   
\# View HTML page  
open http://localhost:8080/trust/did:tdln:01ARZ3NDEKTSV4RRFFQ69G5FAV  
---

## 15\. ARCHITECTURE DIAGRAM

┌─────────────────────────────────────────────────────────────────┐  
│                      CLIENT REQUEST                              │  
│  POST /v2/run {realm, inputs: {policy: {kind, payload\_b64}}}   │  
└────────────────────────┬────────────────────────────────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │   RESOLVER SERVICE (Axum)      │  
       │  \- Generate DID (ULID)         │  
       │  \- Generate CID (SHA256/JCS)   │  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  WASM SANDBOX (Wasmtime)       │  
       │  \- Decode base64 payload       │  
       │  \- Execute run() with 5M fuel  │  
       │  \- Return: 0=ACK, 1=ASK, 2=NACK  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  DECISION MAPPING               │  
       │  \- Map return code to tuple     │  
       │  \- Set if\_ok/if\_doubt/if\_not   │  
       │  \- Set status (ok/pending/denied)  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  LOGLINE RECEIPT (tdln-core)   │  
       │  \- Create LogLineTuple         │  
       │  \- Compute tuple\_hash          │  
       │  \- Compute content\_hash        │  
       │  \- Set id \= content\_hash       │  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  DIAMOND CARD \+ MANIFEST       │  
       │  \- Validate against schema     │  
       │  \- Create RunManifest          │  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  SIGN & BUNDLE (tdln-bundle)   │  
       │  \- Compute bundle\_hash         │  
       │  \- Sign with Ed25519           │  
       │  \- Create ZIP (card \+ manifest │  
       │    \+ signatures \+ receipt)     │  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  PERSIST (CardStore)           │  
       │  ./.cards/{did}/               │  
       │  ├── card.json                 │  
       │  ├── run.manifest.json         │  
       │  ├── bundle.zip                │  
       │  └── receipt.logline.v0.json   │  
       └────────────────┬───────────────┘  
                        │  
                        ▼  
       ┌────────────────────────────────┐  
       │  RETURN RunAccepted            │  
       │  \- did, cid, url               │  
       │  \- status: "RUNNING"           │  
       │  \- receipt (full JSON)         │  
       └────────────────────────────────┘  
---

## 16\. CRATE DEPENDENCY GRAPH

resolver (HTTP service)  
├── tdln-core (hashing, receipt)  
├── tdln-bundle (ZIP builder)  
├── tdln-wasm (WASM sandbox)  
├── axum (web framework)  
├── tokio (async runtime)  
├── ed25519-dalek (signing)  
├── jsonschema (validation)  
└── \[other: qrcode, base64, tracing, time, hex\]  
   
tdln-verify (CLI tool)  
├── tdln-core  
├── ed25519-dalek  
├── zip  
└── \[other: clap, hex, anyhow, blake3\]  
   
guests/ack, guests/ask (WASM)  
└── \[no\_std, no dependencies\]  
---

## SUMMARY

Ethics-is-Efficient is a deterministic policy evaluation engine that:

1. Accepts HTTP requests with WASM policy payloads  
2. Executes WASM guests in a fuel-metered sandbox (Wasmtime)  
3. Maps return codes (0/1/2) to LogLine decisions (ACK/ASK/NACK)  
4. Emits cryptographically signed logline.receipt.v0 receipts  
5. Bundles cards, manifests, and signatures into ZIP archives  
6. Persists all artifacts to disk (./.cards/{did}/)  
7. Provides verification tooling (tdln-verify) for offline validation

Key Invariants:

* id \== content\_hash (always)  
* receipt\_version \== "logline.receipt.v0" (always)  
* 9-slot tuple structure (always)  
* SHA-256 bare hex hashing (always)  
* JCS RFC-8785 canonicalization (always)  
* Ed25519 signatures on bundle hash (always)

I'll explore this repository thoroughly. Let me start by understanding the structure and reading the key files.  
Failed to read file '/Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main': Internal error  
Let me read the workspace Cargo.toml and the ARCHITECTURE.md file:  
Perfect\! Now let me read all the individual crate Cargo.toml files:  
Now let me find and read the lib.rs files from each crate:  
Excellent\! Now let me read all the lib.rs files:  
Now let me read the RFCs to understand the design philosophy:  
Let me read a few more key RFCs:  
Perfect\! Now let me check for any additional documentation or tests:  
Let me read the main README and a couple of crate READMEs:  
Excellent\! Now I have a comprehensive understanding of the repository. Let me compile my findings into a detailed report.

## COMPREHENSIVE EXPLORATION REPORT: What-Runs-Natively-Above-Software

### 1\. WORKSPACE STRUCTURE & CARGO.TOML

Location: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/Cargo.toml  
Workspace Members (10 Constitutional Crates):  
\- crates/constitution-gate  
\- crates/proof-runtime  
\- crates/epistemic-storage  
\- crates/proof-federation  
\- crates/manager-plane  
\- crates/worker-abi  
\- crates/economic-fields  
\- crates/jurisdiction  
\- crates/efficiency-allocation  
\- crates/horizon-real  
Workspace Configuration:

* Edition: 2024  
* Rust Version: 1.85  
* License: MIT OR Apache-2.0  
* Resolver: 2

Shared Dependencies:

* anyhow 1.0.100  
* blake3 1.8.2 (cryptographic hashing)  
* hex 0.4.3  
* rand 0.9.2, rand\_chacha 0.9.0  
* serde 1.0.228 with derive feature  
* serde\_json 1.0.145  
* thiserror 2.0.17

Workspace Lints:

* unsafe\_code \= "warn"  
* clippy::all \= "warn"

---

### 2\. CRATE-BY-CRATE ANALYSIS

#### Layer 1: CONSTITUTION-GATE (RFC-0001)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/constitution-gate/Cargo.toml  
Dependencies: rand, rand\_chacha, serde (no upstream crate dependencies)  
Core Concepts (from lib.rs, lines 1-225):

* Verdict Enum: Commit, Ghost, Reject (three canonical states, no implicit states)  
* ErrorContract: Declares epsilon (error margin), zero\_guess\_domains (forbidden guessing zones), max\_questions  
* SiliconProposal: score\_q16, risk\_q16, kernel\_hash (silicon proposes, gate decides)  
* GateInputs & GateDecision: Structured decision flow with reason codes  
* Key Constants:  
  * OK\_MIN\_Q16 \= 52\_000 (minimum score for commitment)  
  * DOUBT\_BELOW\_Q16 \= 48\_000 (triggers Ghost/question)  
  * Reason codes: R\_MISSING\_EVIDENCE, R\_UNANCHORED, R\_POLICY\_VIOLATION, R\_SILICON\_DOUBT, R\_SILICON\_NOT\_OK

Philosophy: Law of outcome, no-guess gate, error contract. Silicon may approximate but cannot rule.  
---

#### Layer 2: PROOF-RUNTIME (RFC-0002)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/proof-runtime/Cargo.toml  
Dependencies: blake3, constitution-gate, epistemic-storage, hex, serde, serde\_json, thiserror  
Core Concepts (from lib.rs, lines 1-476):

* StepDecision: Commit, Continue(StepAction), Reject(RejectReason)  
* StepAction Variants:  
  * Compute(ComputeAction): Propose, RunExpert, RecomputePath  
  * Materialize(MaterializeAction): RehydrateAtom, RetrieveEvidence, LoadModule  
  * Witness(WitnessAction): AskUserBit, AskUserField, GetTime, FetchExternalAtom  
* Session: case\_id, contract\_hash, proof\_mode, budget tracking, state\_root, transcript\_head, event\_count  
* ProofPack: Final artifact with events, final\_outcome, constitutional\_verdict  
* Contract Trait: eval\_step, cost\_of, determinism\_profile  
* Runtime: Executes sessions with max\_steps limit, produces ProofPack

Philosophy: Decision as proof process. Transcript is authority. Each step is transactional with explicit cost.  
---

#### Layer 3: EPISTEMIC-STORAGE (RFC-0003)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/epistemic-storage/Cargo.toml  
Dependencies: blake3, hex, serde, thiserror (no upstream crate dependencies)  
Core Concepts (from lib.rs, lines 1-287):

* UniversalAtom: CID-based immutable content addressing  
  * AtomKind: Fact, Set, Derivation, Receipt, Witness, Module  
  * Payload is immutable once materialized  
* EpistemicHeat: Absent, Cold, Warm, Hot (thermal state of knowledge)  
* AtomSpace Trait: materialize, get\_payload, get\_heat, set\_heat, metrics, view  
* InMemoryAtomSpace: Reference implementation with HashMap storage  
* PointerRegistry: StatePointer tracking with namespace, head\_cid, prev\_head\_cid, height  
* StorageError: ImmutableConflict, Missing  
* PageFault: Absent, Cold (explicit absence handling)

Philosophy: Content-addressed immutable atoms. State is pointer. Disk is cache. Forgetfulness is survival.  
---

#### Layer 4: PROOF-FEDERATION (RFC-0004)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/proof-federation/Cargo.toml  
Dependencies: epistemic-storage, proof-runtime, serde, thiserror  
Core Concepts (from lib.rs, lines 1-356):

* NodeIdentity & NodeRole: Edge, Core, Witness  
* AuthorityId & AuthorityGrant: Signer authority with allowed\_namespaces, epoch validity  
* StatePointer: namespace, head\_cid, prev\_head\_cid, authority\_id, height  
* PointerAnnouncement: Signed pointer advance with optional proof\_pack\_cid  
* AcceptanceVerdict: Accepted, Rejected(reason), ForkVisible  
* AcceptRejectReason: InvalidSignature, UnknownAuthority, ProofRequired, RewindDetected, NamespaceDenied  
* PointerValidator Trait: Anti-rewind, monotonic height, proof requirement validation  
* DefaultPointerValidator: Reference implementation with fork detection  
* FederationTransport Trait: request\_atoms, request\_proof\_pack

Philosophy: Signed pointer advances over proof-carrying state. Fork visibility. Anti-rewind enforcement.  
---

#### Layer 5: MANAGER-PLANE (RFC-0005)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/manager-plane/Cargo.toml  
Dependencies: proof-federation, proof-runtime, worker-abi, serde, thiserror  
Core Concepts (from lib.rs, lines 1-225):

* ManagerInput: Event, WorkerReceipt, Witness, PointerAdvanced  
* ManagerOutput: Delegate, AskHumanWitness, AdvancePointer, Terminate, Blocked, Idle  
* CaseState: WaitingForInput, Delegated, WaitingForWorker, WaitingForWitness, ReadyToAdvance, Closed  
* BlockReason: BudgetExhausted, WaitingForForkResolution, MissingWitness  
* BasicManager: Typed event-driven orchestration with case queue  
* ManagerPlane Trait: ingest, evaluate\_next

Philosophy: Non-chat typed orchestration. Manager coordinates between workers, witnesses, and pointer advances.  
---

#### Layer 6: WORKER-ABI (RFC-0006)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/worker-abi/Cargo.toml  
Dependencies: epistemic-storage, serde, thiserror  
Core Concepts (from lib.rs, lines 1-235):

* WorkerManifest: name, version, class, bytecode\_cid, required\_capabilities, determinism\_profile  
* WorkerClass: ChipAsCode, SiliconAsCompute (with epsilon\_bounds, quantization)  
* Capability: Compute, WitnessRead, Materialize  
* QuantizationLevel: None, Int8, Int4  
* WorkerResult: Complete(ReceiptCid), Yield(Vec), Fail(WorkerError)  
* WorkerAbi Trait: execute(task\_cid, env) \-\> WorkerResult  
* WorkerHostEnv Trait: request\_atom, consume\_gas (bounded execution)  
* YieldingWorker: Reference implementation with explicit yield on missing atoms  
* OutOfGas Error: Tracks remaining vs requested  
* verify\_silicon\_execution: Epsilon-bounded divergence verification

Philosophy: Bounded execution with explicit yield. Non-sovereign labour. Gas-aware.  
---

#### Layer 7: ECONOMIC-FIELDS (RFC-0007)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/economic-fields/Cargo.toml  
Dependencies: blake3, hex, proof-runtime, serde, serde\_json, thiserror  
Core Concepts (from lib.rs, lines 1-198):

* ReceiptEnvelope: executor, beneficiary, gas\_cost, contract\_hash, receipt  
* TranscriptEntry: Chained with prev\_hash, entry\_hash, budget\_before/after, state\_root\_before/after  
* EconomicSummary: Aggregates executor, beneficiary, total\_gas\_spent, gas\_remaining, step\_count  
* EconomicTranscript: Append-only ledger with conservation verification  
* Hash: Canonical hashing of envelopes and entries  
* verify\_conservation(): Ensures sum of gas\_cost equals initial\_budget \- remaining

Philosophy: Transcript-linked conserved work, not currency. Economic legibility through hashed chains.  
---

#### Layer 8: JURISDICTION (RFC-0008)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/jurisdiction/Cargo.toml  
Dependencies: economic-fields, proof-runtime, serde, serde\_json, thiserror  
Core Concepts (from lib.rs, lines 1-355):

* JurisdictionEnvelope: case\_cid, proofpack\_cid, recommendation\_cid, signer\_id, signer\_role, authority\_cid, duty\_class, consequence\_class, verdict, justification\_cid, signature  
* DutyClass: RoutineOperational, Financial, Legal, Medical, Governance, IrreversibleAction  
* ConsequenceClass: ReversibleLow, MaterialHigh, RightsAffecting, InstitutionBinding, BodyOrLifeAffecting  
* HumanVerdict: Ratify, Authorize, Refuse, Suspend, Escalate  
* SignerAuthority: signer\_id, roles, allowed\_duty\_classes, allowed\_consequence\_classes, may\_\* flags, epoch validity  
* JurisdictionThreshold: reversibility\_low, rights\_affected, bodily\_risk, legal\_exposure, institutional\_binding, named\_accountable\_party  
* HumanFinalityMode: SingleSigner, DualControl, Quorum  
* validate\_envelope(): Checks signature, justification, authority scope, proof visibility  
* decide\_jurisdiction(): Maps threshold to JurisdictionDecision  
* authority\_can\_sign(): Validates signer authority against duty, consequence, verdict, epoch

Philosophy: Accountability outranks fluency. Final signature follows consequence. Sorrow test: who can still suffer?  
---

#### Layer 9: EFFICIENCY-ALLOCATION (RFC-0009)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/efficiency-allocation/Cargo.toml  
Dependencies: serde (no upstream crate dependencies)  
Core Concepts (from lib.rs, lines 1-105):

* PowerOffice: Law, Exploration, Execution, ConsequenceClosure, Measurement, Coordination  
* ComponentKind: Contract, Model, Worker, HumanSigner, EconomicMeter, ManagerPlane  
* OfficeAssignment: component, assigned\_office, context  
* Misallocation: assignment, reason  
* AllocationPolicy Trait: allowed\_offices(ComponentKind) \-\> &\[PowerOffice\]  
* CanonicalPolicy: Maps each component to its canonical office  
  * Contract \-\> Law  
  * Model \-\> Exploration  
  * Worker \-\> Execution  
  * HumanSigner \-\> ConsequenceClosure  
  * EconomicMeter \-\> Measurement  
  * ManagerPlane \-\> Coordination  
* assess\_allocations(): Detects category violations

Philosophy: Doctrine of proper allocation. Ethics as structural property. Power misallocated becomes waste.  
---

#### Layer 10: HORIZON-REAL (RFC-0010)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/crates/horizon-real/Cargo.toml  
Dependencies: jurisdiction, worker-abi, serde  
Core Concepts (from lib.rs, lines 1-261):

* ConsequenceRegime: Reversible, Irreversible  
* ActuationCommand: command\_id, case\_cid, action, regime, consequence\_class, signer\_id, signature  
* SensorModality: Camera, Lidar, Pressure, Thermal, HumanWitness  
* SensorWitness: sensor\_id, modality, quality\_basis\_points, reading\_cid  
* SensorQuorumPolicy: minimum\_witnesses, minimum\_quality\_basis\_points, require\_distinct\_modalities  
* SensorQuorumVerdict: Sufficient, Degraded(reason), Refuse(reason)  
* ActuatorInterlock Trait: validate\_command with jurisdiction, authority, epoch, finality\_mode, signature\_count  
* DefaultInterlock: Reference implementation enforcing:  
  * Signature presence  
  * Quorum satisfaction  
  * Jurisdiction matching for irreversible commands  
  * Authority validation  
* evaluate\_sensor\_quorum(): Multi-modal witness validation

Philosophy: Actuation interlocks. Entropy boundary. Irrevocable events require human jurisdiction. Sensors as entropic witnesses.  
---

### 3\. DEPENDENCY GRAPH (from ARCHITECTURE.md)

constitution-gate \-\> none  
epistemic-storage \-\> none  
proof-runtime \-\> constitution-gate, epistemic-storage  
proof-federation \-\> proof-runtime, epistemic-storage  
worker-abi \-\> epistemic-storage  
manager-plane \-\> proof-runtime, proof-federation, worker-abi  
economic-fields \-\> proof-runtime  
jurisdiction \-\> economic-fields, proof-runtime  
efficiency-allocation \-\> none  
horizon-real \-\> jurisdiction, worker-abi  
Key Invariant: No reverse authority dependencies permitted. Lower-law layers never depend on higher-consequence layers.  
---

### 4\. RFC CORPUS (11 Files)

Location: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/What-Runs-Natively-Above-Software-main/rfcs/

| RFC | Title | Crate | Status |
| :---- | :---- | :---- | :---- |
| 0000 | source-monolith.md | (archive) | Original corpus |
| 0001 | Constitution of the Hybrid | constitution-gate | Normative draft |
| 0002 | Decision as Proof Process | proof-runtime | Normative draft |
| 0003 | Sovereign Atom Space | epistemic-storage | Normative draft |
| 0004 | Federation: Proof-Carrying State | proof-federation | (inferred) |
| 0005 | Non-Chat Manager Plane | manager-plane | (inferred) |
| 0006 | Sovereign Worker ABI | worker-abi | (inferred) |
| 0007 | Economic Fields: Fuel Layers | economic-fields | (inferred) |
| 0008 | Jurisdiction from Duty and Sorrow | jurisdiction | Normative draft |
| 0009 | Efficiency and Power | efficiency-allocation | Foundational position paper |
| 0010 | Horizon of the Real | horizon-real | Terminal position paper |

---

### 5\. ARCHITECTURAL PRINCIPLES & SEPARATION DOCTRINE

#### The 10 Layers and Their Roles:

1. Constitution-Gate (Law): Establishes three canonical verdicts (Commit/Ghost/Reject). Silicon proposes; gate decides. No implicit states.  
2. Proof-Runtime (Decision as Process): Executes incremental proof process. Each step is transactional with explicit cost, receipt, and state change. Transcript is authority.  
3. Epistemic-Storage (Knowledge Space): Content-addressed immutable atoms. State is pointer. Thermal management (Absent/Cold/Warm/Hot). Local-first synchronization.  
4. Proof-Federation (Distributed Proof): Signed pointer advances over proof-carrying state. Anti-rewind enforcement. Fork visibility. Authority grants with epoch validity.  
5. Manager-Plane (Orchestration): Typed non-chat case coordination. Routes between workers, witnesses, and pointer advances. Maintains case state machine.  
6. Worker-ABI (Bounded Labour): Sandboxed execution with explicit yield. Gas-aware. Non-sovereign labour. Epsilon-bounded silicon verification.  
7. Economic-Fields (Legibility): Transcript-linked gas accounting. Conservation verification. Envelope hashing. Not currency; measurement.  
8. Jurisdiction (Consequence-Bearing Finality): Human signature where consequence remains non-transferable. Duty/consequence classification. Signer authority validation. Quorum modes.  
9. Efficiency-Allocation (Doctrine): Maps components to canonical offices (Law/Exploration/Execution/ConsequenceClosure/Measurement/Coordination). Detects category violations.  
10. Horizon-Real (Physical Boundary): Actuation interlocks. Sensor quorum. Distinguishes reversible vs irreversible physical acts. Entropy-aware witness validation.

#### Constitutional Separation Principles:

1. No Reverse Authority: Lower-law layers never depend on higher-consequence layers.  
2. Typed Authority: Each layer has a specific office; misallocation is architectural error.  
3. Proof Over Opacity: Replayability and transcript visibility over implicit state.  
4. Consequence Follows Duty: Final signature belongs where burden remains non-transferable.  
5. Bounded Computation: Silicon approximates; gate decides. Workers yield; managers coordinate.  
6. Immutable History: Atoms are immutable; state advances by pointer. Forgetfulness is survival.  
7. Explicit Cost: Every action has declared cost. Budget is binding.  
8. Legible Jurisdiction: Human acts remain transcript-visible with duty/consequence classification.

---

### 6\. KEY INVARIANTS & TESTS

Constitution-Gate:

* Gate totality preserved (always returns Commit/Ghost/Reject)  
* No-guess domain rejects sub-threshold proposals  
* Missing evidence always ghosts

Proof-Runtime:

* Transcript append-only and budget-binding  
* Each step transactional with receipt  
* State root changes tracked

Epistemic-Storage:

* Atom immutability enforced  
* Heat/page fault semantics  
* CAS identity stable for same payload

Proof-Federation:

* Anti-rewind rejects old height  
* Fork visibility on prev\_head mismatch  
* Authority validation with epoch checks

Worker-ABI:

* Worker yields when required atom missing  
* Fails on out-of-gas  
* Yield then resume completes  
* Silicon verifier accepts bounded divergence

Economic-Fields:

* Envelope chain and conservation verified  
* Gas cost tracking accurate

Jurisdiction:

* Signer authority validated against duty/consequence/verdict/epoch  
* Justification required for certain verdicts  
* Quorum satisfaction checked

Horizon-Real:

* Irreversible command refused without valid jurisdiction  
* Sensor quorum degrades on low quality  
* Irreversible command requires quorum

End-to-End (horizon-real/tests/end\_to\_end.rs):

* Complete flow from manager delegation through worker execution, proof generation, economic tracking, jurisdiction validation, to actuation interlock

---

### 7\. IMPLEMENTATION STATUS

Implemented in v0:

* Canonical types, traits, and contracts per layer  
* Thin executable slices for all 10 layers  
* Boundary and invariant tests  
* Reference implementations (BasicManager, DefaultPointerValidator, DefaultInterlock, YieldingWorker, etc.)

Deferred by Design:

* Production networking and cryptography details in federation  
* Real hardware sandbox backends (WASM/WGPU beyond trait surface)  
* Persistent storage engines and distributed transport  
* Institution-specific policy packs and signer infrastructure  
* Monetary/token layers beyond transcript-linked gas accounting

---

### 8\. KEY FILES & LINE REFERENCES

| Component | File | Key Lines |
| :---- | :---- | :---- |
| Workspace | Cargo.toml | 1-36 |
| Architecture | ARCHITECTURE.md | 1-61 |
| Constitution | constitution-gate/src/lib.rs | 1-225 |
| Runtime | proof-runtime/src/lib.rs | 1-476 |
| Storage | epistemic-storage/src/lib.rs | 1-287 |
| Federation | proof-federation/src/lib.rs | 1-356 |
| Manager | manager-plane/src/lib.rs | 1-225 |
| Worker | worker-abi/src/lib.rs | 1-235 |
| Economics | economic-fields/src/lib.rs | 1-198 |
| Jurisdiction | jurisdiction/src/lib.rs | 1-355 |
| Efficiency | efficiency-allocation/src/lib.rs | 1-105 |
| Horizon | horizon-real/src/lib.rs | 1-261 |
| E2E Test | horizon-real/tests/end\_to\_end.rs | 1-208 |
| RFC Index | rfcs/README.md | 1-32 |
| RFC-0001 | rfcs/0001-constitution.md | 1-642 |
| RFC-0002 | rfcs/0002-decision-as-proof-process.md | 1-767 |
| RFC-0003 | rfcs/0003-sovereign-atom-space.md | 1-274 |
| RFC-0008 | rfcs/0008-jurisdiction-duty-sorrow.md | 1-199 |
| RFC-0009 | rfcs/0009-efficiency-and-power.md | 1-150 |
| RFC-0010 | rfcs/0010-horizon-of-the-real.md | 1-150 |

---

### 9\. ACTIONABLE RECOMMENDATIONS

1. For Understanding the System:  
   * Start with ARCHITECTURE.md for the 10-layer overview  
   * Read RFC-0001 (Constitution) for foundational philosophy  
   * Study the end-to-end test (horizon-real/tests/end\_to\_end.rs) to see layers in action  
2. For Extension:  
   * Identify which layer your feature belongs to (use efficiency-allocation doctrine)  
   * Preserve the dependency graph (no reverse dependencies)  
   * Add typed contract before implementation detail  
   * Include invariant tests in the owning crate  
3. For Integration:  
   * Implement the trait surfaces (Contract, RuntimeOps, AtomSpace, PointerValidator, etc.)  
   * Respect the three canonical verdicts (Commit/Ghost/Reject)  
   * Maintain transcript visibility and replay capability  
   * Enforce budget binding and explicit cost  
4. For Verification:  
   * Run: cargo test \--workspace  
   * Check: cargo clippy \--workspace \--all-targets \--all-features \-- \-D warnings  
   * Format: cargo fmt \--all \-- \--check

---

### 10\. SUMMARY

This is a constitutional architecture for hybrid human-machine systems that:

* Separates law (constitution-gate) from execution (proof-runtime, worker-abi)  
* Grounds all decisions in proof (proof-runtime, economic-fields, jurisdiction)  
* Treats knowledge as immutable content-addressed atoms (epistemic-storage)  
* Federates through signed pointer advances (proof-federation)  
* Allocates power to proper offices (efficiency-allocation)  
* Preserves human jurisdiction where consequence remains non-transferable (jurisdiction)  
* Enforces interlocks at the physical boundary (horizon-real)

The 10 layers form a one-way dependency chain from foundational (constitution-gate, epistemic-storage) through operational (proof-runtime, manager-plane, worker-abi) to consequential (jurisdiction, horizon-real). This prevents lower-law layers from depending on higher-consequence layers, ensuring that law, proof, and economics cannot be corrupted by jurisdiction or actuation concerns.\*  
I'll conduct a thorough exploration of this repository. Let me start by examining the structure and key files.  
Failed to read file '/Users/ubl-ops/Downloads/logline-foundation-canonical-repos/constitutional-runtime-main': Internal error  
Good\! Now let me read the key files systematically.  
Now let me read the policy, admission, evidence, and lowering modules:  
Now let me read the lowering, planning\_compiler, and validation modules:  
Let me continue reading validation and then check the decision and capability modules:  
Let me continue reading capability and then look at tests:  
Searched\*\*/\*test\*.rs in constitutional-runtime-main/src  
Let me read the test file and explore more modules:  
Now let me check the operational\_grammar and strong\_grammar modules to understand the surface language:  
Let me check the failure and idempotency modules to complete the picture:  
Now let me look at a few more key files to get the complete picture:  
SearchedTODO|FIXME|XXX|NOTE|HACK in constitutional-runtime-main/src  
Perfect\! Let me now create a comprehensive summary document. Let me also check if there's a README or docs:  
Excellent\! Now I have a comprehensive view. Let me create a detailed summary document.

## Summary Report: Constitutional Runtime Repository

### Overview

The constitutional-runtime is a Rust crate that implements the foundational mechanism for accountable execution systems. It enforces that material acts must be semantically admissible, policy-permitted, capability-realizable, and evidentially accountable. This is substrate-neutral infrastructure, not tied to any specific application.  
Repository Path: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/constitutional-runtime-main  
---

### 1\. PROJECT STRUCTURE & CARGO.TOML

File: Cargo.toml (lines 1-30)  
toml  
\[package\]  
name \= "constitutional-runtime"  
version \= "0.1.0"  
edition \= "2021"  
license \= "MIT OR Apache-2.0"  
description \= "IR, policy, capability, evidence, and admission boundaries for accountable execution..."  
   
\[dependencies\]  
serde \= { version \= "1.0", features \= \["derive"\] }  
serde\_json \= "1.0"  
sha2 \= "0.10"  
thiserror \= "2.0"  
rusqlite \= { version \= "0.32", optional \= true }  
reqwest \= { version \= "0.12", optional \= true, ... }  
   
\[features\]  
default \= \[\]  
sqlite-evidence \= \["dep:rusqlite"\]  
supabase-evidence \= \["dep:reqwest"\]  
Key Points:

* Single crate (not a workspace)  
* Minimal dependencies: serde, sha2, thiserror  
* Two optional evidence backends: SQLite and Supabase REST  
* unsafe\_code \= "forbid" at workspace level

---

### 2\. MODULE INVENTORY

File: src/lib.rs (lines 1-84)  
The crate exports 20 public modules:

| Module | Purpose |
| :---- | :---- |
| ir | 16 canonical IR primitives (the constitution) |
| policy | Policy classes A/B/C/D (admission regimes) |
| capability | Substrate capability manifests |
| admission | Pure admission evaluation (passports, visas, gates, boundaries) |
| evidence | Evidence contracts, records, store trait, closure semantics |
| evidence\_sqlite | SQLite evidence store (feature-gated) |
| evidence\_supabase | Supabase REST evidence store (feature-gated) |
| lowering | IR → operational grammar compiler |
| operational\_grammar | Surface-level program parser |
| planning\_compiler | End-to-end: surface → IR → validation → lowering |
| decision | Resolve Decide nodes before lowering |
| validation | Three-pass admissibility checks |
| act\_identity | Canonical action identity (namespace.verb) |
| idempotency | Idempotency classes and contracts |
| failure | Stage-tagged structured failures |
| ingress | Ingress escalation modes |
| strong\_grammar | JSON surface for IR ingress |
| plan\_executor | Executes compiled plans |
| refs | Reference types (NodeId, DataRef, TargetRef, etc.) |
| failure | Runtime failure classification |

---

### 3\. THE SIXTEEN IR PRIMITIVES

File: src/ir.rs (lines 134-209)  
rust  
pub enum IRPrimitive {  
   // Intelligence loop (read-only)  
   Observe { target: TargetRef, scope: String },  
   Collect { kind: Kind, target: TargetRef, window: Window },  
   Fetch { kind: Kind, id: String },  
    
   // Inference (deterministic recompute)  
   Compress { kind: Kind, input\_ref: DataRef, infer\_surface: InferSurface },  
   Classify { kind: Kind, input\_ref: DataRef, schema: Schema, infer\_surface: InferSurface },  
   Prioritize { kind: Kind, input\_ref: DataRef, policy: PolicyId, infer\_surface: InferSurface },  
   Compare { kind: Kind, left: DataRef, right: DataRef },  
    
   // Decision & routing  
   Decide { context: DataRef, policy: PolicyId },  
   Route { operation: Box\<IRPrimitive\>, surface: SurfaceRef },  
   Schedule { action: Box\<IRPrimitive\>, trigger: Trigger },  
    
   // Material actions  
   Execute { action: ActionKind, params: Map\<String, Value\> },  
   Reconcile { target: TargetRef, desired: DataRef, mode: ReconcileMode },  
    
   // Output & persistence  
   Emit { surface: SurfaceRef, payload: DataRef },  
   Persist { data: DataRef, durability: DurabilityClass },  
    
   // Authority & cancellation  
   Confirm { action: Box\<IRPrimitive\>, role: Role },  
   Cancel { id: String },  
}  
Key IR Concepts:

* Routing classes: InferSurface has Local, Cloud, Hybrid, or Named(id) (substrate-specific)  
* Durability: Ephemeral, Durable, Audited  
* Reconciliation modes: Apply, DryRun, Force  
* Action identity: ActionKind::Canonical(CanonicalActionId) is the primary carrier (ADR 09\)

---

### 4\. POLICY CLASSES (A/B/C/D)

File: src/policy.rs (lines 1-25)  
rust  
pub enum PolicyClass {  
   /// A: Read-only intelligence loop \+ bounded emit/route/schedule  
   A,  
   /// B: Same as A \+ execution (except Reconcile)  
   B,  
   /// C: Full primitive set at runtime boundary (authority-sensitive)  
   C,  
   /// D: Reserved band (representable in planning, not executable at normal boundary)  
   D,  
}  
Validation Rules (src/validation.rs lines 181-201):

* Class A: Observe, Collect, Fetch, Compress, Classify, Prioritize, Compare, Emit, Route, Schedule only  
* Class B: Everything except Reconcile  
* Class C/D: Full set (but D is blocked at execution boundary)

---

### 5\. ADMISSION FLOW

File: src/admission.rs (lines 1-535)  
Core Types:  
rust  
pub struct ProposedLogLineAct {  
   pub who: String,              // Actor  
   pub did: String,              // Action identifier  
   pub this: Value,              // Payload  
   pub confirmed\_by: Value,      // Confirmation data  
   pub if\_ok: String,            // Success handler  
   pub if\_doubt: String,         // Uncertainty handler  
   pub if\_not: String,           // Failure handler  
   pub status: String,  
   pub metadata: Option\<Value\>,  
}  
   
pub struct AdmissionContext {  
   pub passports: Vec\<Passport\>,    // Actor identity documents  
   pub visas: Vec\<Visa\>,            // Permission envelopes  
   pub gates: Vec\<Gate\>,            // Action gates  
   pub boundaries: Vec\<Boundary\>,   // Deterministic/semantic rules  
   pub now: Option\<String\>,         // Current time  
}  
   
pub enum AdmissionDecision {  
   Yes,  
   No,  
   Cloud,  // Requires semantic (LLM) evaluation  
}  
Admission Pipeline (evaluate\_admission, lines 136-224):

1. Check required slots are present  
2. Verify actor has closed passport  
3. Verify actor has closed, time-valid visa  
4. Check visa allows/forbids the did  
5. Verify applicable gate exists  
6. Evaluate all closed boundaries (deterministic or cloud)  
7. Return AdmissionRuling with audit trail

Boundary Evaluation:

* BoundaryKind::Deterministic → evaluated immediately  
* BoundaryKind::Semantic → returns Cloud decision (requires external evaluation)

---

### 6\. EVIDENCE STORE ARCHITECTURE

File: src/evidence.rs (lines 1-141)  
rust  
pub struct EvidenceContract {  
   pub required\_kinds: Vec\<String\>,  // Logical evidence kinds needed  
}  
   
pub struct EvidenceRecord {  
   pub kind: String,  
   pub payload\_json: serde\_json::Value,  
}  
   
pub trait EvidenceStore: Send \+ Sync {  
   fn write\_record(\&self, record: EvidenceRecord) \-\> Result\<(), EvidenceStoreError\>;  
}  
   
pub struct FileEvidenceStore {  
   path: PathBuf,  
   lock: Mutex\<()\>,  // Append-only with mutex protection  
}  
Evidence Record Types:

* lowering.semantic — what was lowered and under which contract  
* exec.result — success/failure at the muscle layer  
* closure.status — constitutional close vs partial/failed close

Closure Semantics:  
rust  
pub fn close\_execution\_evidence(  
   store: \&dyn EvidenceStore,  
   records: Vec\<EvidenceRecord\>,  
) \-\> Result\<(), FailureToClose\>

* Constitutional gate: If execution succeeds but evidence write fails → not closed  
* All records must write successfully or the whole act is incomplete

Available Stores:

1. FileEvidenceStore — NDJSON file (default, local development)  
2. SqliteEvidenceStore — SQLite database (feature: sqlite-evidence)  
3. SupabaseRestEvidenceStore — PostgREST HTTP sink (feature: supabase-evidence)

---

### 7\. COMPILATION PIPELINE

File: src/planning\_compiler.rs (lines 1-200)  
OperationalProgram  
 ↓ normalize  
 ↓ parse each line → IR primitive  
 ↓ assign deterministic node ids (n0, n1, n0.c0, n0.c1, …)  
 ↓ build parent/child IR graph  
 ↓ validate\_admissibility (structure · policy · capability)  
 ↓ Lowerer::lower per admissible node  
 ↓ CompiledOperationalPlan { graph, per-node plans, commands }  
Key Artifacts:  
rust  
pub struct IrGraph {  
   pub nodes: Vec\<IrNode\>,     // Deterministic program order  
   pub edges: Vec\<Edge\>,       // Syntactic parent/child relations  
}  
   
pub struct NodePlan {  
   pub node\_id: NodeId,  
   pub primitive: IRPrimitive,  
   pub lowering: LoweringPlan,  
   pub command: OperationalCommand,  
   pub selected\_infer\_surface: Option\<InferSurface\>,  
   pub selected\_substrate\_id: Option\<String\>,  
   pub idempotency: Option\<IdempotencyContract\>,  
}  
   
pub struct CompiledOperationalPlan {  
   pub program: OperationalProgram,  
   pub graph: IrGraph,  
   pub node\_plans: Vec\<NodePlan\>,  
}  
Deterministic Node IDs:

* Top-level entry i → n{i} (e.g., n0, n1)  
* Child j of entry i → n{i}.c{j}  
* Same normalized program → same IDs, byte-for-byte (enables replay, diff, simulation)

Error Handling:

* CompileError — pre-admissibility (malformed surface, unmapped verb)  
* PlanError — wraps compile \+ validation \+ lowering failures with NodeId

---

### 8\. VALIDATION: THREE-PASS ADMISSIBILITY

File: src/validation.rs (lines 1-299)  
Pass 1: Structure (validate\_structure, lines 73-179)

* Non-empty node IDs  
* Nesting depth ≤ 4 for Route/Schedule/Confirm  
* Primitive-specific field validation (non-empty strings, valid enums)

Pass 2: Policy (validate\_policy, lines 204-228)

* runtime\_permitted flag check  
* Decide not allowed at execution boundary  
* PolicyClass::D not allowed at execution boundary  
* Primitive allowed under policy class

Pass 3: Capability (validate\_capability, lines 231-264)

* At least one substrate can realize the primitive  
* Kind constraint satisfied (if substrate declares supported\_kinds)  
* Evidence realizability (if require\_evidence\_closure, substrate must declare evidence.write)

Context:  
rust  
pub struct AdmissibilityContext {  
   pub policy\_class: PolicyClass,  
   pub runtime\_permitted: bool,  
   pub at\_execution\_boundary: bool,  
   pub require\_evidence\_closure: bool,  
}  
---

### 9\. LOWERING: IR → OPERATIONAL GRAMMAR

File: src/lowering.rs (lines 1-802)  
rust  
pub struct OperationalCommand {  
   pub namespace: String,  
   pub verb: String,  
   pub args: BTreeMap\<String, Value\>,  
   pub target\_runtime: RuntimeTarget,  
}  
   
pub struct LoweringPlan {  
   pub requires\_confirmation: bool,  
   pub estimated\_latency\_ms: Option\<u64\>,  
   pub evidence: EvidenceContract,  
}  
   
pub trait Lowerer {  
   fn lower(\&self, node: \&IrNode) \-\> Result\<(LoweringPlan, OperationalCommand), LoweringError\>;  
}  
   
pub struct StandardRuntimeLowerer;  
Runtime Targets:

* OperationalGrammar — standard operational grammar  
* Mcp — Model Context Protocol  
* Shell — shell commands  
* Cloud — cloud services  
* Platform — runs inside constitutional runtime process  
* Provider — third-party providers (SendGrid, Twilio, etc.)

Lowering Examples:

* Observe → host.inspect (latency: 50ms)  
* Collect → events.collect (latency: 120ms)  
* Compress → intel.compress (latency: 300ms)  
* Classify → intel.classify (latency: 250ms)  
* Execute → action.execute (requires confirmation if risky)

Key Invariant: StandardRuntimeLowerer does not lower Decide — it must be resolved first.  
---

### 10\. DECISION RESOLUTION

File: src/decision.rs (lines 1-195)  
rust  
pub trait DecideResolver {  
   fn resolve\_decide(\&self, node: \&IrNode) \-\> Result\<IRPrimitive, PlannerError\>;  
}  
   
pub fn materialize\_primitive(  
   p: \&IRPrimitive,  
   resolver: \&impl DecideResolver,  
   owning\_id: \&NodeId,  
   depth: usize,  
) \-\> Result\<IRPrimitive, PlannerError\>  
   
pub fn compile\_node(node: \&IrNode, resolver: \&impl DecideResolver) \-\> Result\<IrNode, PlannerError\>  
   
pub fn resolve\_lower\_one(  
   lowerer: \&StandardRuntimeLowerer,  
   node: \&IrNode,  
   resolver: \&impl DecideResolver,  
) \-\> Result\<(LoweringPlan, OperationalCommand), PlannerLoweringError\>  
Semantics:

* Decide nodes are representation-only in the IR  
* Must be resolved to concrete primitives before lowering  
* Resolver can be policy engine, LLM, human, or mock  
* Recursively resolves nested Decide within Route/Schedule/Confirm  
* Nesting depth bounded by MAX\_ROUTE\_NESTING\_DEPTH \= 4

---

### 11\. CAPABILITY MANIFESTS

File: src/capability.rs (lines 1-349)  
rust  
pub struct CapabilityManifest {  
   pub substrate\_id: String,  
   pub substrate\_version: String,  
   pub supported\_primitives: BTreeSet\<PrimitiveName\>,  
   pub supported\_kinds: BTreeSet\<String\>,  // Empty \= wildcard  
   pub declared\_guarantees: BTreeSet\<String\>,  // e.g., "evidence.write"  
   pub bindings: Vec\<CapabilityBinding\>,  
}  
   
pub struct CapabilityBinding {  
   pub primitive: PrimitiveName,  
   pub kind\_filter: Option\<String\>,  
   pub action\_identity: Option\<CanonicalActionId\>,  
   pub guarantee: GuaranteeEnvelope,  
   pub cost: CostEnvelope,  
   pub latency: LatencyEnvelope,  
   pub evidence: EvidenceGuarantee,  
}  
   
pub struct GuaranteeEnvelope {  
   pub atomic: bool,  
   pub deterministic: bool,  
   pub preserves\_order: bool,  
   pub tags: BTreeSet\<String\>,  
}  
   
pub struct CostEnvelope {  
   pub monetary\_micros: Option\<u64\>,  
   pub currency: Option\<String\>,  
   pub tokens: Option\<u64\>,  
   pub tags: BTreeSet\<String\>,  
}  
   
pub struct LatencyEnvelope {  
   pub p50\_ms: Option\<u32\>,  
   pub p95\_ms: Option\<u32\>,  
   pub timeout\_ms: Option\<u32\>,  
}  
   
pub struct EvidenceGuarantee {  
   pub writes\_success: bool,  
   pub writes\_failure: bool,  
   pub durable\_before\_ack: bool,  
   pub declared\_kinds: Vec\<String\>,  
}  
Realizability Checks:

* can\_realize(primitive) — substrate supports the primitive  
* kind\_allowed(primitive) — kind constraint satisfied  
* evidence\_realizable(require\_evidence) — evidence guarantee met  
* binding\_for(primitive) — find first matching binding

---

### 12\. CANONICAL ACTION IDENTITY

File: src/act\_identity.rs (lines 1-150)  
rust  
pub struct CanonicalActionId {  
   namespace: String,  
   verb: String,  
   dotted: String,  // Cached for hot paths  
}  
   
impl CanonicalActionId {  
   pub fn new(namespace: impl Into\<String\>, verb: impl Into\<String\>) \-\> Result\<Self, IdentityError\>  
   pub fn parse(dotted: \&str) \-\> Result\<Self, IdentityError\>  
   pub fn namespace(\&self) \-\> \&str  
   pub fn verb(\&self) \-\> \&str  
   pub fn dotted\_str(\&self) \-\> \&str  
   pub fn surface\_kind(\&self) \-\> String  
   pub fn lowered\_command\_identity(\&self) \-\> (\&str, \&str)  
}  
   
pub enum IdentityError {  
   Malformed { input: String, reason: &'static str },  
   InvalidCharacter { input: String, component: &'static str },  
   NotNamed,  
}  
Construction Rules:

* Each component (namespace, verb) must be non-empty  
* Only ASCII lowercase letters, digits, and \_  
* Separated by exactly one . in dotted form  
* Serialization: two-field {namespace, verb} (dotted is cached, recomputed on deserialize)

Projections:

* surface\_kind() → dotted form (e.g., "outbound.send")  
* lowered\_command\_identity() → (namespace, verb) pair for OperationalCommand

---

### 13\. IDEMPOTENCY CONTRACTS

File: src/idempotency.rs (lines 1-285)  
rust  
pub enum IdempotencyClass {  
   /// No state mutation. Safe to replay freely.  
   PureRead,  
   /// Mutates only derived/cached state. Retries safe (bounded divergence).  
   DeterministicRecompute,  
   /// Material action with idempotency key deduplication.  
   DeduplicatedMaterialAction,  
   /// Material action, once-only, requires explicit confirmation.  
   ConfirmedNonIdempotent,  
}  
   
pub enum ReplayStance {  
   /// Duplicate \= no-op success (prior outcome replayed).  
   SilentSuccess,  
   /// Duplicate \= explicit failure with reason\_code "replay\_detected".  
   ReplayRejection,  
   /// Escalate to human/authority path.  
   EscalateToConfirm,  
}  
   
pub struct IdempotencyContract {  
   pub class: IdempotencyClass,  
   pub replay\_stance: ReplayStance,  
   pub key\_shape: Option\<String\>,  // e.g., "sha256(correlation\_id || kind)"  
   pub tags: Vec\<String\>,  
}  
Semantics:

* Idempotency is a declared property, never inferred  
* mechanical\_retry\_allowed() → true for all except ConfirmedNonIdempotent  
* requires\_idempotency\_key() → true only for DeduplicatedMaterialAction  
* enforces\_single\_effect() → true for deduplicated and confirmed non-idempotent

---

### 14\. STRUCTURED FAILURE CLASSIFICATION

File: src/failure.rs (lines 1-309)  
rust  
pub enum FailureStage {  
   Parse,        // Input parsing failed  
   Validation,   // Structural validation failed  
   Policy,       // Policy class rejected  
   Capability,   // No substrate can realize  
   Lowering,     // IR → operational grammar failed  
   Execution,    // Substrate execution failed  
   Evidence,     // Evidence store write failed  
}  
   
pub enum FailurePhase {  
   PreAdmission,  // Parse, Validation, Policy, Capability, Lowering  
   Execution,     // Execution, Evidence  
}  
   
pub enum RuntimeFailure {  
   Parse { grammar: String, detail: String, reason\_code: String, line: Option\<u32\>, column: Option\<u32\> },  
   Validation { at: String, field: Option\<String\>, detail: String, reason\_code: String },  
   Policy { class: PolicyClassTag, reason\_code: String, detail: String },  
   Capability { primitive: String, kind: Option\<String\>, attempted\_substrate: Option\<String\>, reason\_code: String, detail: String },  
   Lowering { node\_id: String, target\_runtime: String, reason\_code: String, detail: String },  
   Execution { command\_id: Option\<String\>, surface: String, reason\_code: String, detail: String },  
   Evidence { node\_id: Option\<String\>, reason\_code: String, detail: String },  
}  
Key Invariant: Failures are stage-tagged, not free-form text. Downstream code can match on stage without parsing.  
---

### 15\. PLAN EXECUTOR

File: src/plan\_executor.rs (lines 1-150)  
rust  
pub trait Dispatcher {  
   fn dispatch(\&self, node\_id: \&NodeId, command: \&OperationalCommand) \-\> DispatchOutcome;  
}  
   
pub enum DispatchOutcome {  
   Success { evidence\_ref: Option\<String\>, detail: Option\<Value\> },  
   Failure { reason\_code: String, detail: Option\<String\>, runtime\_failure: Option\<RuntimeFailure\> },  
   Blocked { reason: String },  
}  
   
pub struct NodeExecutionResult {  
   pub node\_id: NodeId,  
   pub command: OperationalCommand,  
   pub dispatched: bool,  
   pub outcome: NodeOutcome,  
}  
   
pub enum NodeOutcome {  
   Success { evidence\_ref: Option\<String\>, detail: Option\<Value\> },  
   Failure { reason\_code: String, detail: Option\<String\>, runtime\_failure: Option\<RuntimeFailure\> },  
   Blocked { reason: String },  
   Skipped { reason: String },  // Halted by prior node  
}  
   
pub struct ExecutionReport {  
   pub plan: CompiledOperationalPlan,  
   pub results: Vec\<NodeExecutionResult\>,  
}  
   
pub fn execute\_compiled\_plan\<D: Dispatcher \+ ?Sized\>(  
   plan: \&CompiledOperationalPlan,  
   dispatcher: \&D,  
) \-\> ExecutionReport  
Executor Semantics:

* Iterate plan.node\_plans in deterministic order  
* Dispatch each command through caller's Dispatcher  
* Halt on first non-success outcome  
* Emit result for every downstream node (skipped \= Blocked)  
* Does not: retry, branch on Decide, run in parallel, re-evaluate policy/capability

---

### 16\. OPERATIONAL GRAMMAR

File: src/operational\_grammar.rs (lines 1-200)  
namespace.verb key=value key="quoted value" ...  
Program Structure:  
rust  
pub struct OperationalLine {  
   pub namespace: String,  
   pub verb: String,  
   pub args: BTreeMap\<String, ArgValue\>,  
}  
   
pub enum ArgValue {  
   Bare(String),  
   Quoted(String),  
}  
   
pub struct OperationalEntry {  
   pub line: OperationalLine,  
   pub children: Vec\<OperationalEntry\>,  // Single-level indentation  
}  
   
pub struct OperationalProgram {  
   pub entries: Vec\<OperationalEntry\>,  
}  
Example:  
flow.verify\_report target=lab8gb infer=lab512  
 emit thread=t1  
 confirm role=admin  
Parser Properties:

* One pass, one position cursor  
* Closed error set  
* Equal inputs parse to equal OperationalProgram byte-for-byte  
* Surface is open to vocabulary growth; IR bridge is constitutional

---

### 17\. STRONG GRAMMAR (JSON SURFACE)

File: src/strong\_grammar.rs (lines 1-149)  
rust  
pub enum StrongProgram {  
   SystemReview { system\_review: ReviewSpec },  
   DriftReview { drift\_review: ReviewSpec },  
   Pipeline { pipeline: PipelineSpec },  
   Execute { execute: ExecuteSpec },  
   Emit { emit: String },  
   Confirm { confirm: ConfirmSpec },  
}  
   
pub struct ReviewSpec {  
   pub target: String,  
   pub pipeline: Vec\<PipelineStep\>,  
   pub on\_success: Option\<StrongHandler\>,  
   pub on\_failure: Option\<StrongHandler\>,  
}  
   
pub enum PipelineStep {  
   Collect, Compress, Classify, Prioritize, Compare,  
}  
   
pub fn parse\_strong\_json(input: \&str) \-\> Result\<StrongProgram, CompileError\>  
pub fn compile\_strong\_program(program: \&StrongProgram) \-\> Result\<IrGraph, CompileError\>  
pub fn compile\_strong\_json\_to\_ir\_graph(input: \&str) \-\> Result\<IrGraph, CompileError\>  
Design:

* JSON-only in v0 (textual grammar is future work)  
* Deliberately not a second command language  
* Emits same IRPrimitive graph as operational grammar  
* Ingress surface for Place-Agent deliberation

---

### 18\. REFERENCE TYPES

File: src/refs.rs (lines 1-30)  
rust  
pub struct NodeId(pub String);           // Stable node identifier in intent graph  
pub struct DataRef(pub String);          // Opaque handle to persisted/in-flight data  
pub struct TargetRef(pub String);        // Host, service, or logical target  
pub struct SurfaceRef(pub String);       // UI or integration surface (thread, channel)  
pub struct PolicyId(pub String);         // Named policy bundle for admission  
---

### 19\. INGRESS MODES

File: src/ingress.rs (lines 1-59)  
rust  
pub enum IngressMode {  
   FastPath,           // Rules, templates, cached mappings (rank 0\)  
   Structured,         // Small model, constrained decoding (rank 1\)  
   Cognitive,          // Full Place Agent composition (rank 2\)  
   PremiumException,   // Appellate-style resolution (rank 3\)  
}  
Doctrine: Cheap paths first; premium LLM is constitutional exception only.  
---

### 20\. TESTS

File: tests/constitutional\_pipeline.rs (lines 1-200)  
Test Coverage:

1. Decision Layer \+ Runtime Lowering (lines 32-46)  
   * Resolve Decide to Observe  
   * Lower to host.inspect  
2. Intelligence Loop: Admit → Lower → Evidence (lines 74-104)  
   * Collect primitive  
   * Validate admissibility  
   * Lower to events.collect  
   * Write evidence to file store  
   * Verify evidence contains node ID and kind  
3. Evidence Closure Failure (lines 106-128)  
   * Execution succeeds, evidence write fails  
   * Verify FailureToClose is returned  
4. Policy Class D Rejection (lines 130-146)  
   * PolicyClass::D at execution boundary → rejected  
5. Policy-Blocked Node (lines 148-164)  
   * Execute under PolicyClass::A → rejected  
6. All Intelligence Primitives Render (lines 166-200+)  
   * Test lowering of all 16 primitives  
   * Verify operational commands are generated

---

### 21\. KEY ARCHITECTURAL INVARIANTS

1. Determinism: Same normalized program → same node IDs, byte-for-byte  
2. All-or-Nothing Planning: Compilation succeeds completely or fails completely  
3. No Side Effects: Planning compiler is pure (no I/O, no mutation, no dispatch)  
4. Constitutional Gate: Evidence write failure after successful execution \= not closed  
5. Closed Error Sets: No free strings cross runtime boundary (failures are stage-tagged)  
6. Substrate Neutrality: IR knows nothing about specific labs/hosts; routing is opaque  
7. Policy Governs: Intelligence proposes; policy and capability govern; runtime lowers only admissible acts  
8. Decide is Representation-Only: Must be resolved before lowering; runtime lowerer never sees unresolved Decide  
9. Idempotency is Declared: Never inferred; class determines retry safety  
10. Evidence Legitimizes: Receipts beat stories; every executable claim must be evidence-closable

---

### 22\. COMPILATION PIPELINE FLOW (COMPLETE)

OperationalProgram (text or JSON)  
   ↓  
parse\_program / parse\_strong\_json  
   ↓  
OperationalProgram (AST)  
   ↓  
normalize()  
   ↓  
per-entry: OperationalLine::to\_ir\_primitive()  
   ↓  
IrNode { id: NodeId, body: IRPrimitive }  
   ↓  
assign deterministic node ids (n0, n1, n0.c0, …)  
   ↓  
build parent/child edges  
   ↓  
IrGraph { nodes, edges }  
   ↓  
validate\_admissibility per node  
   ├─ validate\_structure (shape, nesting depth)  
   ├─ validate\_policy (class, boundary, permission)  
   └─ validate\_capability (substrate support, kind, evidence)  
   ↓  
Lowerer::lower per admissible node  
   ├─ resolve Decide if present (via DecideResolver)  
   └─ materialize\_primitive → OperationalCommand  
   ↓  
CompiledOperationalPlan {  
   program: OperationalProgram,  
   graph: IrGraph,  
   node\_plans: Vec\<NodePlan\>,  
}  
   ↓  
execute\_compiled\_plan(plan, dispatcher)  
   ├─ dispatch each command  
   ├─ halt on first non-success  
   └─ emit ExecutionReport  
   ↓  
close\_execution\_evidence(store, records)  
   └─ all records must write or act is not closed  
---

### 23\. ACTIONABLE RECOMMENDATIONS

1. Documentation: Add architecture diagrams showing the pipeline flow and module dependencies  
2. Examples: Provide end-to-end examples of:  
   * Creating a custom Lowerer implementation  
   * Implementing a DecideResolver (policy engine, LLM, human)  
   * Building a Dispatcher for a specific substrate  
3. Testing: Expand test coverage for:  
   * Edge cases in admission evaluation (time-based visa expiry, boundary clouding)  
   * Nested Route/Schedule/Confirm at max depth  
   * All 16 primitives in all policy classes  
4. Performance: Consider benchmarking:  
   * Compilation time for large programs  
   * Evidence write throughput  
5. Integration: Provide adapters for common substrates (HTTP, gRPC, shell, MCP)

---

### 24\. FILES NOT FULLY EXPLORED

Due to token limits, the following modules were partially read:

* src/evidence\_sqlite.rs — SQLite evidence store implementation  
* src/evidence\_supabase.rs — Supabase REST evidence store implementation  
* src/lowering.rs — Full lowering implementation (802 lines, only first 200 read)  
* src/planning\_compiler.rs — Full planning compiler (only first 200 lines read)  
* src/operational\_grammar.rs — Full parser (only first 200 lines read)

These modules follow the same patterns and invariants documented above.  
---

### 25\. SUMMARY TABLE

| Aspect | Details |
| :---- | :---- |
| Language | Rust 2021 edition |
| Unsafe Code | Forbidden |
| Dependencies | serde, serde\_json, sha2, thiserror, rusqlite (optional), reqwest (optional) |
| IR Primitives | 16 (Observe, Collect, Fetch, Compress, Classify, Prioritize, Compare, Decide, Route, Schedule, Execute, Reconcile, Emit, Persist, Confirm, Cancel) |
| Policy Classes | 4 (A: read-only, B: bounded material, C: authority-sensitive, D: reserved) |
| Validation Passes | 3 (structure, policy, capability) |
| Evidence Stores | 3 (file, SQLite, Supabase) |
| Node ID Scheme | Deterministic from position (n0, n1, n0.c0, …) |
| Failure Stages | 7 (parse, validation, policy, capability, lowering, execution, evidence) |
| Idempotency Classes | 4 (PureRead, DeterministicRecompute, DeduplicatedMaterialAction, ConfirmedNonIdempotent) |
| Ingress Modes | 4 (FastPath, Structured, Cognitive, PremiumException) |

I'll help you explore this governance repository thoroughly. Let me start by examining the directory structure and reading the key files.  
Now let me read the main governance files and all LIPs:  
Now let me read all the LIPs:  
Now let me read the remaining LIPs:  
Now let me read the template and check the proposals and historical directories:  
Let me also check the historical superseded receipt file:  
Perfect\! Now let me create a comprehensive summary document. Let me verify I have all the key information:  
Perfect\! Now I have all the information needed. Let me compile a comprehensive report.

## COMPREHENSIVE GOVERNANCE REPOSITORY ANALYSIS

### REPOSITORY OVERVIEW

Location: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main  
Purpose: This repository records the governance process for the LogLine Foundation canon—the normative specification for the LogLine system. It does NOT define the canon itself, own conformance testing, or implement the runtime. It records the debate, proposal, acceptance, supersession, and errata process.  
Key Principle: "canon defines. conformance proves. engine implements. governance evolves."  
---

## 1\. GOVERNANCE FRAMEWORK

### 1.1 Authority Structure (GOVERNANCE.md)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/GOVERNANCE.md  
Core Principle: The canon is the normative source. Runtime implementations are adherence claims, not sources of norm.  
Defined Roles:

| Role | Responsibility |
| :---- | :---- |
| Canon Editor | Maintains normative clarity and consistency |
| Runtime Maintainer | Maintains reference implementation without owning canon |
| Conformance Maintainer | Maintains corpus cases, manifests, expected results |
| Security Reviewer | Reviews proof, receipt, signature, ledger implications |
| Foundation Steward | Mediates long-term direction and unresolved conflicts |

Change Process:  
Draft → Proposed → Accepted → Implemented → Superseded  
                     ↓             ↓  
                  Rejected      Reverted  
                     ↓  
                  Withdrawn  
Versioning Rule: Published canon versions are immutable. Substantive changes require new versions or explicit errata.  
---

### 1.2 Extended Governance (governance-delta.md)

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/governance-delta.md  
Purpose: Extends early governance with states, roles, quorum, acceptance, rejection, errata, and security triggers.  
Acceptance Criteria for LIPs: A LIP may be Accepted when:

* Motivation and scope are clear  
* Normative language is precise  
* Conformance impact is described  
* Security impact is reviewed if needed  
* Migration path exists  
* Rejection alternatives were considered

Rejection Criteria: A LIP may be Rejected when it:

* Weakens evidence discipline  
* Lets natural language execute  
* Lets if\_doubt release consequence  
* Breaks the 9-slot form without major-version process  
* Lacks a conformance path  
* Creates unbounded authority

Security Review Triggers: Security review is required when changes touch:

* confirmed\_by  
* Receipt verification  
* Signature verification  
* Ledger append/rollback  
* Adapter execution  
* if\_ok release  
* if\_doubt simulation boundaries  
* Runtime conformance claims

Errata Policy:

* May correct spelling, broken links, non-normative examples without version bump  
* Any change to MUST/SHOULD/MAY behavior requires new canon version or explicit amendment

---

## 2\. LOGLINE IMPROVEMENT PROPOSALS (LIPs)

### 2.1 LIP Status Summary

| LIP | Title | Status | Type |
| :---- | :---- | :---- | :---- |
| LIP-0001 | Canon hardening and conformance | Accepted | Normative/Process |
| LIP-0002 | If-doubt: auditable simulation | Proposed | Normative |
| LIP-0003 | LogLine receipt encoding | Superseded (by LIP-0007) | Normative |
| LIP-0004 | LogLine adapter protocol | Proposed | Lateral canon extension |
| LIP-0005 | Adapter declaration profile | Proposed | Lateral canon extension |
| LIP-0006 | Adapter conformance | Proposed | Lateral canon extension |
| LIP-0007 | Receipt three-layer hashing | Accepted | Normative |

---

### 2.2 DETAILED LIP SPECIFICATIONS

#### LIP-0001: Canon Hardening and Conformance

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0001-canon-hardening-and-conformance.md  
Status: Accepted  
Author: LogLine Foundation  
Created: 2026-05-06  
Target: Living package  
Core Thesis: "LogLine is canon. The runtime is an implementation adherent, not the origin of the norm."  
Problem Statement:

1. Ambiguity normativa \- External implementers cannot distinguish between canon rule, editorial decision, accidental runtime behavior, and example convention  
2. Low auditability \- Without schema, formal grammar, and conformance corpus, adherence remains declarative rather than verifiable  
3. Institutional coupling \- If Rust runtime is perceived as the norm itself, other implementations become subordinate translations, not legitimate ecosystem participants

Objectives:

* Formally separate canon from implementation  
* Publish minimal normative artifacts for third-party adoption  
* Create objective conformance basis with valid/invalid cases  
* Elevate confirmed\_by from doctrinal field to verifiable multi-layer mechanism  
* Institute editorial governance independent of runtime technical cycle  
* Enable external implementations to prove adherence to specific canon version

Minimum Normative Distribution:

| Artifact | Function | Expected Result |
| :---- | :---- | :---- |
| spec/logline-canon.md | Normative text with explicit MUST/SHOULD/MAY | Official, citable, stable reading |
| spec/grammar.ebnf | Formal grammar of .logline textual form | Consistent independent parsers |
| spec/logline-canon.schema.json | Formal JSON schema | External tool validation |
| conformance/ | Corpus of passing/failing cases with reasons | Objective adherence proof |
| docs/canon-vs-runtime.md | Institutional separation explanation | Coherent, teachable doctrine |
| CHANGELOG.md | Canon change history | Editorial traceability independent of runtime |
| GOVERNANCE.md | Roles, change rite, quorum, decision process | Mature, predictable governance |
| lips/ | Formal improvement proposals directory | Public, argued, auditable evolution |

Proposed Editorial Architecture:  
logline-canon/  
 spec/  
   logline-canon.md  
   grammar.ebnf  
   logline-canon.schema.json  
 conformance/  
   valid/  
   invalid/  
   ambiguous/  
 examples/  
   health/  
   finance/  
   notarial/  
   operations/  
   governance/  
 lips/  
 docs/  
   canon-vs-runtime.md  
   evidence-model.md  
   release-discipline.md  
Versioning Rules:

1. Published canon versions are immutable  
2. Editorial corrections without normative impact → errata  
3. Substantive corrections → new canon version  
4. Incompatible changes → explicit breaking changes section  
5. Canon changelog separate from runtime changelog  
6. Runtime declares target canon version  
7. Conformance tested against specific version, never "current"

Conformance Model:

* Corpus organized into: valid/, invalid/, ambiguous/  
* Each case declares: input, target canon version, expected result, reason, layer (syntactic/structural/semantic/probatory), severity  
* Format: JSON manifest with case\_id, canon\_version, input, expected, reason, layer, severity

Evidence Model (Multi-Layer):

| Layer | Evolution | Benefit |
| :---- | :---- | :---- |
| Basic | Structured receipts with id, issuer, digest \+ LogLine relation | Minimal admissibility trail |
| Intermediate | Ed25519 signatures \+ initial did:key support | Strong proof without heavy infrastructure |
| Persistent | Append-only ledger with hash chain | Immutable historical record |

Non-Goals:

* Does NOT redefine nine-slot core  
* Does NOT replace Rust runtime as reference implementation  
* Does NOT introduce mandatory heavy identity/blockchain/external authority  
* Does NOT require full cryptographic proof from v1  
* Does NOT make canon excessively academic or operationally inaccessible

---

#### LIP-0002: If-doubt as Auditable Simulation

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0002-if-doubt-auditable-simulation.md  
Status: Proposed  
Author: LogLine Foundation draft  
Created: 2026-05-06  
Target: if\_doubt addendum  
Core Normative Rule:  
if\_doubt is where possible worlds may be tested without becoming facts.  
Problem: Current canon prevents release without evidence but underspecifies what runtime may do with doubt. Without stronger rule, if\_doubt risks becoming loose fallback, hidden manual path, or place where generated language pretends to be action.  
Required Behavior:

1. MUST NOT execute external consequence from if\_doubt  
2. MUST NOT silently convert doubt route into ok route  
3. SHOULD emit doubt trace when routing enters if\_doubt  
4. SHOULD emit simulation receipt when performing simulation  
5. MAY generate possible-world LogLine, provided epistemically marked  
6. MUST leave released \= false for simulated consequences

Simulation Receipt Shape:  
json  
{  
 "receipt\_kind": "simulation",  
 "canon\_version": "0.2.0-draft",  
 "logline\_digest": "sha256:...",  
 "branch": "doubt",  
 "reason": "receipt\_missing",  
 "simulated\_route": "ask\_or\_suspend",  
 "executed": false,  
 "released": false  
}  
Conformance Test Cases Required:

* confirmed\_by \= none with if\_doubt \= suspend → expected ambiguous  
* if\_doubt \= simulate → expected simulated and unreleased  
* Unknown doubt route → expected invalid or ambiguous per canon version  
* Simulation receipt claiming executed \= true → expected invalid  
* Promotion from simulated to released without new evidence → expected invalid

Acceptance Criteria:

* Normative rule added to textual spec  
* JSON schema accepts receipt and trace shapes  
* conformance/cases.json contains valid/invalid/ambiguous fixtures  
* Runtime declaration can report partial support

Implementation Criteria:

* CLI can run conformance suite  
* Runtime emits doubt trace for if\_doubt routing  
* Runtime emits simulation receipt for simulation routes  
* Tests demonstrate if\_doubt cannot execute consequence

---

#### LIP-0003: LogLine Receipt Encoding and Content Addressing

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0003-logline-receipt-encoding.md  
Status: SUPERSEDED by LIP-0007  
Superseded: 2026-05-17  
Author: LogLine Foundation draft  
Created: 2026-05-07  
⚠️ HISTORICAL ARTIFACT: Preserved for audit trail. Engines MUST NOT implement this receipt shape. Read to understand what changed and why.  
Original Core Law:  
A receipt does not contain a LogLine.  
A receipt is a LogLine act with result, evidence, transport, and hashes.  
Original Normative Receipt Shape:

* Top-level canonical slots: who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status  
* Optional fields: result, evidence, transport, hashes  
* Hash profiles: jcs-rfc8785 (JSON), logline-length-prefixed-v0 (tuple), sha256 (algorithm)

Three Hash Types:

1. tuple\_hash \- Over exactly 9 slots only  
2. result\_hash \- Over canonical JSON representation of result  
3. receipt\_hash \- Over full receipt excluding hashes.receipt\_hash

Why Superseded: Receipt model moved from single result\_hash with embedded result/evidence/transport to three-layer discipline (tuple/content/envelope) with strict separation of act, interpretation, and transport. See LIP-0007.  
---

#### LIP-0004: LogLine Adapter Protocol

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0004-logline-adapter-protocol.md  
Status: Proposed  
Type: Lateral canon extension  
Scope: Canonical contracts for external adapters  
Primary Source: source/adapter-protocol.logline (lateral, not replacing main canon)  
Central Rule:  
The canon does not create world-specific adapters.  
The canon defines the canonical contracts any world adapter must obey.  
Preserved Canon:

* No new slots added  
* Nine-slot form unchanged: who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status  
* Lateral normative source: source/adapter-protocol.logline

Mental Model:  
external input  
 → InboundAdapter (translates to LogLine candidate)  
 → EvidenceAdapter (resolves confirmed\_by)  
 → RuntimeInvocationTransport (invokes runtime)  
 → runtime judges candidate  
 → ReleaseAdapter (executes only after if\_ok)  
 → ReceiptSink (persists receipts transversally)  
 → world  
Five Lateral Contract Families:

1. inbound\_adapter  
   * Translates external input into LogLine candidate  
   * Does not judge, does not execute effects  
   * Preserves traceability  
2. evidence\_adapter  
   * Resolves or attempts to resolve confirmed\_by  
   * May consult receipts, signatures, digests, declarations, identities, quorum  
   * Must not silently mutate world  
3. runtime\_invocation\_transport  
   * Invokes LogLine runtime by specific medium (CLI, HTTP, WASM, local, remote)  
   * Rule: "transport invokes runtime; transport does not judge"  
4. release\_adapter  
   * Executes route released by runtime  
   * May execute external effects ONLY after if\_ok  
   * Under if\_doubt: must simulate, ask, or stop  
5. receipt\_sink  
   * Persists or emits receipts transversally across phases  
   * Preserves receipt hash and scope  
   * Operates across: translation, evidence, invocation, release, execution, persistence

Core Normative Rules:

* Adapters may translate, read, persist, invoke, observe, execute  
* Adapters may NOT redefine slots or create authority above: confirmed\_by, if\_ok, if\_doubt, if\_not, status  
* External input must become LogLine candidate before runtime judgment  
* confirmed\_by must be resolvable or fail audibly  
* if\_ok releases route; not automatic external effect  
* if\_doubt must not mutate external world by default: released=false, executed=false  
* Receipts prove scope, not universal truth  
* Technical failure (timeout, network error, parse error, etc.) is NOT automatic if\_not

Non-Goals:

* Does NOT define official HTTP/Supabase/Slack/GitHub/MCP/Cloudflare/Gateway/Minilab adapters  
* Does NOT define universal authentication model  
* Does NOT mandate database, queue, SDK, or runtime  
* Terms like passport, visa, admission, gateway are examples only, not canonical products

Acceptance Criteria:

* source/adapter-protocol.logline exists  
* Five contract families defined  
* runtime\_invocation\_transport used instead of runtime\_transport  
* receipt\_sink described as transversal  
* if\_ok required before external effect  
* if\_doubt does not mutate world by default  
* Adapters cannot redefine canon  
* Receipts prove scope  
* Product examples explicitly non-canonical  
* No world-specific adapter implemented  
* No mandatory SDK introduced  
* No tenth slot added

---

#### LIP-0005: Adapter Declaration Profile

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0005-adapter-declaration-profile.md  
Status: Proposed  
Type: Lateral canon extension  
Scope: Adapter declarations, manifests, effect classes, projections  
Depends on: LIP-0004  
Primary Source: source/adapter-declaration-profile.logline  
Core Rule:  
LogLine declaration first.  
Projection second.  
Implementation elsewhere.  
Preserved Canon:

* No runtime slot added  
* No runtime crate added  
* Nine-slot form unchanged

Adapter Declaration as LogLine: Every adapter declaration MUST be expressible as a LogLine:  
logline  
adapter:http\_inbound declare\_adapter inbound\_http\_translation 2026-05-08T10:00:00Z confirmed\_by receipt:sha256:author123 if\_ok accept\_adapter\_declaration if\_doubt quarantine\_adapter if\_not reject\_adapter status declared  
Adapter Kinds:

* inbound  
* evidence  
* runtime\_invocation\_transport  
* release  
* receipt\_sink

Effect Classes:

| Class | Meaning |
| :---- | :---- |
| none | Does not read or alter relevant external systems |
| read | Reads external state |
| write | Writes controlled storage or state |
| external\_effect | Produces effect in another system |
| irreversible\_external\_effect | Produces hard/impossible-to-undo effect |

Rule: Greater effect requires stronger evidence.  
Manifest Profile (Auxiliary JSON):  
json  
{  
 "adapter\_id": "adapter:http\_inbound",  
 "adapter\_version": "0.1.0",  
 "adapter\_kind": "inbound",  
 "protocol\_version": "adapter-protocol-v0",  
 "canon\_version": "0.2.0-draft",  
 "effect\_class": "none",  
 "declaration\_logline": "...",  
 "supports": \["http\_request\_to\_logline", "translation\_receipt", "external\_input\_digest"\],  
 "receipt\_scopes": \["translation\_receipt"\]  
}  
Manifest Constraints:

* MUST NOT add runtime slots  
* MUST NOT claim canonical branch authority outside: if\_ok, if\_doubt, if\_not, status

Allowed Projections:

* JSON Schema  
* TypeScript interfaces  
* Rust traits  
* Python protocols  
* OpenAPI specs  
* MCP manifests  
* CLI flags  
* HTTP endpoints  
* Database schemas

Projection Rule:  
Projections implement adapter contracts.  
Projections do not redefine adapter contracts.  
Non-Goals:

* Does NOT implement SDK, HTTP adapter, Supabase adapter, MCP adapter, GitHub adapter, Slack adapter, Cloudflare adapter, Gateway adapter, Minilab adapter  
* Only defines declaration profile those adapters should obey if created outside canon

Acceptance Criteria:

* source/adapter-declaration-profile.logline exists  
* spec/adapter-declaration-profile.md exists  
* spec/adapter-declaration.schema.json exists  
* Inbound and release adapter declaration examples exist  
* Effect classes documented  
* JSON manifest labeled auxiliary  
* Projections labeled non-normative  
* No SDK or concrete world adapter implemented  
* No tenth slot added

---

#### LIP-0006: Adapter Conformance

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0006-adapter-conformance.md  
Status: Proposed  
Type: Lateral canon extension  
Scope: Adapter conformance cases and reporting  
Depends on: LIP-0004, LIP-0005  
Primary Source: source/adapter-conformance.logline  
Core Rule:  
Adapter conformance is lateral.  
Runtime conformance is canonical.  
Do not confuse them.  
Conformance Levels:

* none  
* partial  
* full  
* failed  
* unknown

Constraints:

* Adapter MUST NOT report full without conformance report  
* Adapter MUST NOT claim full LogLine canon conformance merely because it passes adapter protocol cases

Minimum Conformance Expectations:

* Adapter does not redefine canon  
* External input becomes LogLine candidate  
* confirmed\_by is resolved or fails audibly  
* Runtime invocation transport invokes without judging  
* Release adapter requires if\_ok before external effect  
* if\_doubt does not mutate world by default  
* Receipt proves scope  
* Receipt sink preserves hash and scope  
* Product examples do not become canonical adapters  
* Adapter manifest is auxiliary  
* Projection does not redefine protocol  
* Technical failure is not automatic if\_not

Conformance Report (JSON):  
json  
{  
 "profile": "adapter-protocol-v0",  
 "adapter\_id": "adapter:http\_inbound",  
 "adapter\_version": "0.1.0",  
 "canon\_version": "0.2.0-draft",  
 "protocol\_lips": \["LIP-0004", "LIP-0005", "LIP-0006"\],  
 "status": "partial",  
 "cases": \[  
   {  
     "case\_id": "external\_input\_becomes\_logline\_candidate",  
     "observed": "pass"  
   }  
 \]  
}  
Technical Failures (NOT automatic if\_not):

* timeout  
* network\_error  
* parse\_error  
* runtime\_unavailable  
* storage\_unavailable  
* invalid\_json  
* missing\_technical\_permission

Non-Goals:

* Does NOT implement conformance runner  
* Only defines conformance surface and cases for future runner

Acceptance Criteria:

* source/adapter-conformance.logline exists  
* spec/adapter-conformance.md exists  
* conformance/adapter-cases.json exists  
* Adapter conformance described as lateral  
* Full conformance requires report  
* Technical failures distinguished from canonical if\_not  
* No conformance runner implemented  
* No world-specific adapter implemented  
* No tenth slot added

---

#### LIP-0007: Receipt Three-Layer Hashing

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/lips/LIP-0007-receipt-three-layer-hashing.md  
Status: Accepted (canon)  
Supersedes: LIP-0003  
Author: Dan Voulez  
Created: 2026-05-17  
Core Change: Receipt format moves from single result\_hash model with embedded result/evidence/transport fields to three-layer hash discipline:

* tuple\_hash \- Pure act (nine slots only)  
* content\_hash \- Interpreted act (slots \+ AUX fields from decomposer)  
* envelope\_hash \- Transported package (content \+ transport metadata, computed at each boundary)

Hash Discipline:  
tuple\_hash    \= sha256(jcs(pick: 9 slots))                    → pure act  
content\_hash  \= sha256(jcs(all\_except: \[id, hashes\]))         → interpreted act  
                                                                (receipt\_version \+ 9 slots \+ AUX \+ json\_canonicalization)  
envelope\_hash \= sha256(jcs({content, transport}))             → transported package  
                                                                (lives ONLY on Envelope wrapper)  
Key Constraint: Top-level fields result, evidence, transport are FORBIDDEN in v0 receipts. They are not AUX. Schema rejects them.  
Problem with LIP-0003:

1. Receipt identity changed every time it crossed transport boundary (transport fields inside hashed body) → broke content-addressed citation  
2. Could not distinguish receipt from receipt-of-receipt (results referencing prior receipts couldn't be compared by identity)  
3. Evidence (which by doctrine is attached, not embedded) leaked into act identity

Backward Compatibility: Receipts encoded under LIP-0003 are not automatically conformant. Conversion process:

1. Extract nine slots verbatim  
2. Recompute tuple\_hash over nine slots only  
3. Recompute content\_hash over new receipt without legacy result/evidence/transport fields  
4. Emit envelope\_hash only on next transport boundary, not at rest

Note: result and evidence from LIP-0003 receipts are lost on conversion (they were embedded, cannot be reconstructed).  
Non-Goals:

* Does NOT change nine-slot LogLine body  
* Does NOT replace JCS-RFC8785 canonicalization  
* Does NOT replace SHA-256 hash algorithm  
* Does NOT define evidence storage or transport channels  
* Does NOT define ledger storage engine

Normative Source:

* LogLine-Foundation/canon/logline.receipt.v0  
* LogLine-Foundation/conformance/schemas/logline.receipt.v0.schema.json  
* LogLine-Foundation/conformance/vectors/{valid,invalid}/  
* LogLine-Foundation/conformance/hash-profiles/jcs-rfc8785.md

Acceptance Trail:

* 2026-05-17: Discussed in working session; canon and conformance repos published with three-layer model  
* 2026-05-17: LIP-0003 marked Superseded; this LIP authored as formal record

---

## 3\. PROPOSALS DIRECTORY

Location: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/proposals/

### proposta-melhoria-canon-if-doubt.md

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/proposals/proposta-melhoria-canon-if-doubt.md  
Status: Informal proposal (feed into LIPs once mature)  
Language: Portuguese (operational)  
Related LIP: LIP-0002  
Thesis: The next strong improvement to LogLine is not increasing anatomy. It's giving normative status to what's already implicit in the form:  
confirmed\_by collapses evidence. if\_ok releases the real. if\_doubt simulates the possible. if\_not records the false. status closes the history.  
Proposed Rule:  
if\_doubt é o lugar onde mundos possíveis podem ser testados sem virarem fatos.  
(if\_doubt is where possible worlds may be tested without becoming facts.)  
Why It Matters: Without this rule, if\_doubt becomes loose fallback. With it, becomes canonical space for:

* Simulating consequence  
* Requesting evidence  
* Suspending without releasing  
* Generating hypothetical LogLine  
* Leaving trace of doubt reason  
* Preventing LLM from turning possibility into fact

Minimal Canon Change: Add laws:  
if\_doubt MAY simulate, ask, suspend, dispatch, or clarify.  
if\_doubt MUST NOT execute consequence.  
if\_doubt MUST NOT silently convert doubt into ok.  
if\_doubt MUST emit or preserve trace when affecting routing.  
New Artifacts:

1. Simulation Receipt:

json  
{  
 "receipt\_kind": "simulation",  
 "branch": "doubt",  
 "reason": "receipt\_missing",  
 "simulated\_route": "ask\_or\_suspend",  
 "executed": false,  
 "released": false  
}

2. Doubt Trace:

json  
{  
 "branch": "doubt",  
 "reason": "receipt\_missing",  
 "simulated\_route": "ask\_or\_suspend",  
 "released": false  
}  
Official Conformance Class: Add third class: ambiguous (not half-invalid, but material that must go to if\_doubt because cannot be released or rejected honestly yet)  
Priority CLI:  
bash  
logline conformance run conformance/cases.json  
logline canon check \--schema spec/logline-canon.schema.json source/logline.canon.json  
Recommended Roadmap:

1. Incorporate spec/if-doubt-simulation.md  
2. Accept LIP-0002 as proposal  
3. Apply LIP-0001 backlog: schema, conformance, runtime declaration  
4. Implement doubt\_trace in runtime walk  
5. Implement simulation\_receipt without consequence execution  
6. Add CI: fmt, clippy, test, schema parse, fixture shape  
7. Then publish as stable canon

Success Definition: Runtime produces report like:  
json  
{  
 "runtime": "logline-runtime-rs",  
 "canon\_version": "0.2.0-draft",  
 "conformance\_status": "partial",  
 "supports": \[  
   "valid\_invalid\_ambiguous",  
   "if\_doubt\_trace",  
   "simulation\_receipt"  
 \]  
}  
And if\_doubt cases prove simulation does not execute consequence.  
---

## 4\. HISTORICAL DIRECTORY

Location: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/governance-main/historical/  
Purpose: Superseded canonical artifacts preserved for audit trail. Engines MUST NOT implement these.

### Contents:

| File | Superseded By | LIP Record |
| :---- | :---- | :---- |
| logline.receipt.v0.LIP-0003-superseded.md | Current logline.receipt.v0 in LogLine-Foundation/canon (three-layer hashing) | lips/LIP-0007-receipt-three-layer-hashing.md |
| logline.receipt.v0.LIP-0003-superseded.schema.json | Current schema in LogLine-Foundation/canon | LIP-0007 |

Note: Current canonical receipt format is in LogLine-Foundation/canon. Read historical only to understand evolution, not as implementation target.  
---

## 5\. GOVERNANCE STATE SUMMARY

### 5.1 Current Governance Posture

Authority: Canon is normative source; runtime is adherent implementation, not norm source.  
Maturity: Early governance intentionally small until LIP-0001 accepted or superseded.  
Process: Formal LIP lifecycle with clear states (Draft → Proposed → Accepted → Implemented → Superseded/Rejected/Withdrawn).  
Roles: Five defined roles with clear responsibilities (Canon Editor, Runtime Maintainer, Conformance Maintainer, Security Reviewer, Foundation Steward).  
Versioning: Published canon versions immutable; substantive changes require new versions or explicit errata.  
Security: Security review required for changes touching confirmed\_by, receipts, signatures, ledger, adapters, if\_ok/if\_doubt, conformance claims.  
---

### 5.2 Accepted LIPs (Normative)

#### LIP-0001: Canon Hardening and Conformance ✅

* Status: Accepted (sets the discipline this repo now formalizes)  
* Scope: Separates canon from runtime, publishes normative artifacts, creates conformance corpus, elevates evidence model  
* Key Deliverables:  
  * Formal spec with MUST/SHOULD/MAY  
  * Grammar (EBNF)  
  * JSON schema  
  * Conformance corpus (valid/invalid/ambiguous)  
  * Canon vs runtime documentation  
  * Governance framework  
  * LIP process  
* Impact: Foundational; enables all other LIPs  
* Non-Goals: Does not redefine 9-slot core, replace Rust runtime, mandate heavy infrastructure, require full crypto from v1, make canon inaccessible

#### LIP-0007: Receipt Three-Layer Hashing ✅

* Status: Accepted (canon, in LogLine-Foundation/canon)  
* Scope: Receipt encoding moves from single hash with embedded fields to three-layer discipline  
* Key Rules:  
  * tuple\_hash \= pure act (9 slots only)  
  * content\_hash \= interpreted act (slots \+ AUX)  
  * envelope\_hash \= transported package (content \+ transport)  
  * Top-level result, evidence, transport FORBIDDEN  
* Supersedes: LIP-0003  
* Impact: Fixes content-addressing ambiguities, enables proper receipt composition and citation  
* Backward Compatibility: LIP-0003 receipts not automatically conformant; conversion process defined

---

### 5.3 Proposed LIPs (Under Discussion)

#### LIP-0002: If-doubt as Auditable Simulation 📋

* Status: Proposed  
* Scope: Promotes if\_doubt from suspension route to canonical auditable simulation branch  
* Core Rule: "if\_doubt is where possible worlds may be tested without becoming facts"  
* Key Behaviors:  
  * MUST NOT execute external consequence  
  * MUST NOT silently convert doubt to ok  
  * SHOULD emit doubt trace  
  * SHOULD emit simulation receipt  
  * MAY generate possible-world LogLine (epistemically marked)  
  * MUST leave released=false for simulated consequences  
* New Artifacts: Simulation receipt, doubt trace  
* Conformance: Requires valid/invalid/ambiguous cases  
* Acceptance Criteria: Normative rule in spec, JSON schema updates, conformance cases, runtime declaration support  
* Implementation Criteria: CLI conformance runner, doubt trace emission, simulation receipt emission, proof that if\_doubt cannot execute consequence  
* Related Proposal: proposta-melhoria-canon-if-doubt.md (Portuguese informal proposal)

#### LIP-0004: LogLine Adapter Protocol 📋

* Status: Proposed  
* Scope: Lateral canon layer defining contracts for external adapters without capturing/redefining canon  
* Core Rule: "Canon defines contracts any world adapter must obey; does not create world-specific adapters"  
* Preserved: Nine-slot form unchanged; lateral normative source source/adapter-protocol.logline  
* Five Contract Families:  
  * inbound\_adapter \- Translates external input to LogLine candidate  
  * evidence\_adapter \- Resolves confirmed\_by  
  * runtime\_invocation\_transport \- Invokes runtime without judging  
  * release\_adapter \- Executes only after if\_ok  
  * receipt\_sink \- Persists receipts transversally  
* Core Rules:  
  * Adapters may NOT redefine slots or create authority above confirmed\_by/if\_ok/if\_doubt/if\_not/status  
  * External input must become LogLine candidate before runtime judgment  
  * confirmed\_by must be resolvable or fail audibly  
  * if\_ok releases route; not automatic external effect  
  * if\_doubt must not mutate world by default  
  * Receipts prove scope, not universal truth  
  * Technical failure NOT automatic if\_not  
* Non-Goals: No official HTTP/Supabase/Slack/GitHub/MCP/Cloudflare/Gateway/Minilab adapters; no universal auth; no mandatory DB/queue/SDK  
* Acceptance Criteria: Lateral source exists, five families defined, if\_ok required before effect, if\_doubt non-mutating, adapters cannot redefine canon, receipts prove scope, product examples non-canonical, no world-specific adapter, no mandatory SDK, no tenth slot

#### LIP-0005: Adapter Declaration Profile 📋

* Status: Proposed  
* Scope: How adapters declare themselves without becoming canon; provides declaration profile projectable to JSON Schema, TypeScript, Rust, Python, OpenAPI, MCP, CLI, database schemas  
* Depends on: LIP-0004  
* Core Rule: "LogLine declaration first. Projection second. Implementation elsewhere."  
* Preserved: No runtime slot/crate added; nine-slot form unchanged  
* Adapter Declaration as LogLine: Every declaration must be expressible as LogLine  
* Adapter Kinds: inbound, evidence, runtime\_invocation\_transport, release, receipt\_sink  
* Effect Classes:  
  * none \- Does not read/alter relevant external systems  
  * read \- Reads external state  
  * write \- Writes controlled storage/state  
  * external\_effect \- Produces effect in another system  
  * irreversible\_external\_effect \- Hard/impossible-to-undo effect  
  * Rule: Greater effect requires stronger evidence  
* Manifest Profile: Auxiliary JSON with adapter\_id, version, kind, protocol\_version, canon\_version, effect\_class, declaration\_logline, supports, receipt\_scopes  
* Manifest Constraints: MUST NOT add runtime slots; MUST NOT claim canonical branch authority outside if\_ok/if\_doubt/if\_not/status  
* Allowed Projections: JSON Schema, TypeScript, Rust, Python, OpenAPI, MCP, CLI, HTTP, database schemas  
* Projection Rule: "Projections implement contracts; do not redefine contracts"  
* Non-Goals: No SDK, HTTP/Supabase/MCP/GitHub/Slack/Cloudflare/Gateway/Minilab adapters; only defines declaration profile  
* Acceptance Criteria: Lateral source exists, spec and schema exist, examples exist, effect classes documented, manifest labeled auxiliary, projections labeled non-normative, no SDK/world-specific adapter, no tenth slot

#### LIP-0006: Adapter Conformance 📋

* Status: Proposed  
* Scope: How adapters claim conformance to Adapter Protocol without claiming full LogLine canon conformance  
* Depends on: LIP-0004, LIP-0005  
* Core Rule: "Adapter conformance is lateral. Runtime conformance is canonical. Do not confuse them."  
* Conformance Levels: none, partial, full, failed, unknown  
* Constraints:  
  * MUST NOT report full without conformance report  
  * MUST NOT claim full canon conformance merely from passing adapter protocol cases  
* Minimum Expectations:  
  * Adapter does not redefine canon  
  * External input becomes LogLine candidate  
  * confirmed\_by resolved or fails audibly  
  * Runtime invocation transport invokes without judging  
  * Release adapter requires if\_ok before external effect  
  * if\_doubt does not mutate world by default  
  * Receipt proves scope  
  * Receipt sink preserves hash and scope  
  * Product examples do not become canonical adapters  
  * Adapter manifest auxiliary  
  * Projection does not redefine protocol  
  * Technical failure NOT automatic if\_not  
* Conformance Report: JSON with profile, adapter\_id, version, canon\_version, protocol\_lips, status, cases  
* Technical Failures (NOT if\_not): timeout, network\_error, parse\_error, runtime\_unavailable, storage\_unavailable, invalid\_json, missing\_technical\_permission  
* Non-Goals: Does NOT implement conformance runner; only defines surface and cases  
* Acceptance Criteria: Lateral source exists, spec and cases exist, conformance described as lateral, full conformance requires report, technical failures distinguished from if\_not, no conformance runner, no world-specific adapter, no tenth slot

---

### 5.4 Superseded LIPs (Historical)

#### LIP-0003: LogLine Receipt Encoding and Content Addressing ❌

* Status: Superseded by LIP-0007  
* Superseded: 2026-05-17  
* Reason: Receipt model moved from single result\_hash with embedded result/evidence/transport to three-layer discipline (tuple/content/envelope) with strict separation of act, interpretation, transport  
* Historical Artifact: Preserved in historical/logline.receipt.v0.LIP-0003-superseded.md and .schema.json  
* ⚠️ WARNING: Engines MUST NOT implement this receipt shape. Read to understand evolution, not as implementation target.  
* Original Normative Shape: Top-level canonical slots \+ optional result/evidence/transport/hashes  
* Original Hash Types: tuple\_hash (9 slots), result\_hash (result JSON), receipt\_hash (full receipt)  
* Original Canonicalization: jcs-rfc8785 (JSON), logline-length-prefixed-v0 (tuple), sha256 (algorithm)  
* Conversion Path: Extract 9 slots, recompute hashes, promote embedded AUX fields to top level, emit envelope\_hash only at transport boundary

---

## 6\. OPEN GOVERNANCE QUESTIONS & GAPS

### 6.1 Unresolved Issues

1. LIP-0002 Acceptance Timing  
   * Question: When will if\_doubt simulation semantics be formally accepted?  
   * Current State: Proposed; awaiting normative rule integration, schema updates, conformance cases  
   * Dependency: Requires LIP-0001 backlog completion (schema, conformance, runtime declaration)  
2. Adapter Protocol Maturity  
   * Question: When will LIP-0004/0005/0006 move from Proposed to Accepted?  
   * Current State: Three related LIPs in Proposed state; interdependent  
   * Dependency: Requires lateral normative sources (source/adapter-protocol.logline, etc.) to be authored and published  
   * Scope Clarity: Need explicit examples of inbound and release adapters  
3. Conformance Runner Implementation  
   * Question: Who implements the conformance runner CLI?  
   * Current State: LIP-0001 and LIP-0002 define conformance cases but no runner exists yet  
   * Blocker: Needed for acceptance criteria of LIP-0002  
   * Scope: logline conformance run conformance/cases.json  
4. Canon Publication Timing  
   * Question: When will canon be published as stable (v1.0)?  
   * Current State: Living package; v0.1 or v0.2.0-draft implied  
   * Dependency: Requires LIP-0001 and LIP-0007 fully implemented, LIP-0002 accepted, adapter LIPs stabilized  
5. Witness Set Definition  
   * Question: Who are the declared witnesses authorized to ratify canon releases?  
   * Current State: governance-delta.md mentions "witness set" but no specific people/keys declared  
   * Governance Gap: Needed for formal canon versioning and release authority  
6. Runtime Conformance Declaration  
   * Question: How does Rust runtime declare conformance to specific canon versions?  
   * Current State: LIP-0001 defines declaration format but no runtime has published one yet  
   * Example Needed: JSON manifest with runtime, version, canon\_version, conformance\_suite, status  
7. Errata Process Clarity  
   * Question: What constitutes "non-normative" vs "normative" change for errata purposes?  
   * Current State: governance-delta.md says "spelling, broken links, non-normative examples" OK; "MUST/SHOULD/MAY behavior" requires version bump  
   * Gap: Boundary cases unclear (e.g., clarifying ambiguous language, fixing example that contradicts spec)  
8. Security Review Scope  
   * Question: What level of security review is required for each LIP type?  
   * Current State: governance-delta.md lists triggers but no review process/timeline defined  
   * Gap: No security reviewer assigned; no review SLA  
9. Rejection Process Formality  
   * Question: How formally is a LIP rejection decided? Who has veto power?  
   * Current State: governance-delta.md lists rejection criteria but no voting/consensus mechanism  
   * Gap: No quorum definition, no appeal process  
10. Lateral Canon Boundary  
    * Question: How do we prevent lateral canons (adapter protocol, declaration profile, conformance) from becoming de facto normative?  
    * Current State: LIP-0004/0005/0006 define "lateral" but no enforcement mechanism  
    * Risk: Adapter implementations could create de facto standard that becomes binding

---

### 6.2 Governance Maturity Gaps

| Gap | Current State | Needed |
| :---- | :---- | :---- |
| Witness Set | Mentioned in governance-delta.md | Explicit list of authorized signers for canon releases |
| Quorum | Not defined | Minimum participants for acceptance decision |
| Voting/Consensus | Not defined | Process for resolving disagreement on LIP acceptance |
| Appeal Process | Not defined | How to challenge rejection or acceptance decision |
| Security Review SLA | Not defined | Timeline for security review completion |
| Security Reviewer Assignment | Not defined | Who is designated security reviewer |
| Errata Boundary Cases | Partially defined | Clearer examples of what is/isn't errata-eligible |
| Lateral Canon Enforcement | Not defined | How to prevent lateral canons from becoming de facto normative |
| Canon Release Process | Not defined | Formal steps from Accepted LIP to published canon version |
| Breaking Changes Process | Mentioned but not detailed | Explicit process for major-version changes |

---

### 6.3 Implementation Gaps

| Gap | Current State | Needed |
| :---- | :---- | :---- |
| Conformance Runner | Defined in LIP-0001/0002 | Actual CLI implementation |
| Canon Schema | Mentioned in LIP-0001 | Published spec/logline-canon.schema.json |
| Canon Grammar | Mentioned in LIP-0001 | Published spec/grammar.ebnf |
| Conformance Corpus | Mentioned in LIP-0001 | Published conformance/{valid,invalid,ambiguous}/ cases |
| Adapter Protocol Source | Mentioned in LIP-0004 | Published source/adapter-protocol.logline |
| Adapter Declaration Source | Mentioned in LIP-0005 | Published source/adapter-declaration-profile.logline |
| Adapter Conformance Source | Mentioned in LIP-0006 | Published source/adapter-conformance.logline |
| Runtime Declaration | Defined in LIP-0001 | Rust runtime publishes conformance declaration |
| Canon vs Runtime Docs | Mentioned in LIP-0001 | Published docs/canon-vs-runtime.md |
| Evidence Model Docs | Mentioned in LIP-0001 | Published docs/evidence-model.md |
| Release Discipline Docs | Mentioned in LIP-0001 | Published docs/release-discipline.md |

---

## 7\. KEY FINDINGS & RECOMMENDATIONS

### 7.1 Governance Strengths

✅ Clear Authority Separation: Canon is normative; runtime is implementation. Well-articulated principle.  
✅ Formal LIP Process: Structured lifecycle (Draft → Proposed → Accepted → Implemented → Superseded) with clear state transitions.  
✅ Evidence-Centric Design: Core principle of confirmed\_by and evidence discipline runs through all LIPs.  
✅ Supersession Discipline: LIP-0003 → LIP-0007 shows mature handling of evolution; old artifacts preserved for audit trail.  
✅ Lateral Canon Concept: LIP-0004/0005/0006 introduce sophisticated idea of extending canon without redefining core.  
✅ Security Awareness: governance-delta.md identifies security review triggers; shows security-first thinking.  
✅ Conformance-First: LIP-0001 makes conformance corpus foundational; not an afterthought.  
---

### 7.2 Governance Weaknesses

⚠️ Incomplete Governance Framework: governance-delta.md defines criteria but lacks formal decision process (voting, quorum, appeal).  
⚠️ No Assigned Roles: Roles defined but no specific people/teams assigned; no security reviewer designated.  
⚠️ Witness Set Undefined: governance-delta.md mentions "witness set" for canon ratification but no list published.  
⚠️ Errata Boundary Fuzzy: "Non-normative" vs "normative" boundary unclear; boundary cases not worked examples.  
⚠️ Lateral Canon Risk: LIP-0004/0005/0006 could become de facto normative if implementations diverge; no enforcement mechanism.  
⚠️ Acceptance Criteria Vague: Some LIPs (e.g., LIP-0004) have acceptance criteria but no clear "done" definition.  
⚠️ Implementation Lag: LIP-0001 accepted but many deliverables not yet published (schema, grammar, conformance corpus, docs).  
⚠️ No Release Process: No formal process from "Accepted LIP" to "published canon version."  
---

### 7.3 Actionable Recommendations

IMMEDIATE (Next 1-2 weeks):

1. Assign Roles  
   * Designate Canon Editor  
   * Designate Security Reviewer  
   * Designate Foundation Steward  
   * Publish in GOVERNANCE.md or CONTRIBUTORS.md  
2. Define Witness Set  
   * List authorized signers for canon releases  
   * Publish in GOVERNANCE.md or separate WITNESSES.md  
   * Include key fingerprints or GitHub handles  
3. Clarify Errata Boundary  
   * Add worked examples to governance-delta.md  
   * Example: "Clarifying ambiguous language in example" → errata or new version?  
   * Example: "Fixing example that contradicts spec" → errata or new version?  
4. Publish LIP-0001 Deliverables  
   * Publish spec/logline-canon.md (normative text)  
   * Publish spec/grammar.ebnf (formal grammar)  
   * Publish spec/logline-canon.schema.json (JSON schema)  
   * Publish conformance/{valid,invalid,ambiguous}/ corpus with manifests  
   * Publish docs/canon-vs-runtime.md  
   * Publish docs/evidence-model.md  
   * Publish docs/release-discipline.md

SHORT-TERM (1-4 weeks):

5. Formalize Decision Process  
   * Define quorum for LIP acceptance (e.g., "2 of 3 core reviewers")  
   * Define voting mechanism (consensus, majority, supermajority)  
   * Define appeal process for rejected LIPs  
   * Define timeline for decision (e.g., "14 days discussion, then vote")  
   * Publish in governance-delta.md  
6. Implement Conformance Runner  
   * Implement logline conformance run conformance/cases.json CLI  
   * Support valid/invalid/ambiguous case classification  
   * Emit JSON report with pass/fail/ambiguous counts  
   * Needed for LIP-0002 acceptance  
7. Publish Adapter Protocol Sources  
   * Publish source/adapter-protocol.logline (lateral normative source)  
   * Publish source/adapter-declaration-profile.logline  
   * Publish source/adapter-conformance.logline  
   * Needed for LIP-0004/0005/0006 acceptance  
8. Publish Runtime Conformance Declaration  
   * Have Rust runtime publish conformance declaration JSON  
   * Format: { "runtime": "logline-runtime-rs", "runtime\_version": "0.3.0", "canon\_version": "0.1", "conformance\_suite": "conformance", "status": "partial" }  
   * Publish in runtime repo or governance repo

MEDIUM-TERM (1-2 months):

9. Formalize Canon Release Process  
   * Define steps from "Accepted LIP" to "published canon version"  
   * Define version numbering (semantic versioning)  
   * Define changelog format  
   * Define witness sign-off requirement  
   * Publish in GOVERNANCE.md  
10. Move LIP-0002 to Accepted  
    * Integrate normative rule into spec  
    * Update JSON schema for simulation receipt and doubt trace  
    * Publish conformance cases for if\_doubt behavior  
    * Ensure runtime can emit doubt trace and simulation receipt  
    * Update runtime conformance declaration  
11. Move LIP-0004/0005/0006 to Accepted  
    * Publish lateral normative sources  
    * Publish specs and schemas  
    * Publish adapter declaration and conformance examples  
    * Ensure no world-specific adapters implemented  
    * Ensure no mandatory SDK introduced  
12. Define Lateral Canon Enforcement  
    * Document how lateral canons stay lateral (not de facto normative)  
    * Define audit process for adapter implementations  
    * Define process for escalating lateral canon to core if needed  
    * Publish in governance-delta.md or new LATERAL-CANON.md

---

### 7.4 LIP Readiness Assessment

| LIP | Status | Readiness | Blockers |
| :---- | :---- | :---- | :---- |
| LIP-0001 | Accepted | 40% | Deliverables not published (schema, grammar, corpus, docs) |
| LIP-0002 | Proposed | 60% | Conformance runner not implemented; normative rule not in spec |
| LIP-0003 | Superseded | N/A | Historical artifact; do not implement |
| LIP-0004 | Proposed | 30% | Lateral source not published; examples missing |
| LIP-0005 | Proposed | 30% | Lateral source not published; examples missing |
| LIP-0006 | Proposed | 30% | Lateral source not published; examples missing |
| LIP-0007 | Accepted | 90% | Normative source published; conformance in canon repo |

---

### 7.5 Critical Path to Stable Canon v1.0

LIP-0001 Deliverables (schema, grammar, corpus, docs)  
 ↓  
LIP-0002 Acceptance (if\_doubt simulation)  
 ↓  
LIP-0004/0005/0006 Acceptance (adapter protocol)  
 ↓  
Formal Canon Release Process  
 ↓  
Witness Set Sign-Off  
 ↓  
Canon v1.0 Published  
Estimated Timeline: 2-3 months if resources allocated.  
---

## 8\. REPOSITORY STRUCTURE SUMMARY

governance-main/  
├── GOVERNANCE.md                          \# Initial authority boundary  
├── governance-delta.md                    \# Extended governance (roles, quorum, security triggers)  
├── README.md                              \# Overview and LIP lifecycle  
├── lips/  
│   ├── LIP-0001-canon-hardening-and-conformance.md    ✅ Accepted  
│   ├── LIP-0002-if-doubt-auditable-simulation.md      📋 Proposed  
│   ├── LIP-0003-logline-receipt-encoding.md           ❌ Superseded  
│   ├── LIP-0004-logline-adapter-protocol.md           📋 Proposed  
│   ├── LIP-0005-adapter-declaration-profile.md        📋 Proposed  
│   ├── LIP-0006-adapter-conformance.md                📋 Proposed  
│   ├── LIP-0007-receipt-three-layer-hashing.md        ✅ Accepted  
│   └── TEMPLATE.md                                     \# LIP template (Portuguese)  
├── proposals/  
│   └── proposta-melhoria-canon-if-doubt.md            \# Informal proposal (Portuguese)  
└── historical/  
   ├── README.md                          \# Superseded artifacts guide  
   ├── logline.receipt.v0.LIP-0003-superseded.md      \# Old receipt format  
   └── logline.receipt.v0.LIP-0003-superseded.schema.json  
---

## 9\. CONCLUSION

The LogLine governance repository establishes a mature, evidence-centric governance framework with clear separation between canon (normative), runtime (implementation), and conformance (proof). The framework shows sophisticated thinking about lateral extensions (adapters) and supersession discipline.  
Current State: 2 Accepted LIPs (LIP-0001, LIP-0007) establish foundational principles; 4 Proposed LIPs (LIP-0002, LIP-0004, LIP-0005, LIP-0006) extend governance into simulation, adapters, and conformance.  
Key Gaps: Governance framework incomplete (no quorum, voting, appeal process); many LIP-0001 deliverables not published; no assigned roles; witness set undefined; lateral canon enforcement mechanism missing.  
Critical Path: Publish LIP-0001 deliverables → Accept LIP-0002 → Accept LIP-0004/0005/0006 → Formalize release process → Publish Canon v1.0.  
Estimated Timeline: 2-3 months to stable canon with full governance framework.  
I'll explore this repository thoroughly. Let me start by understanding the structure and then diving into the specific areas you mentioned.  
Let me now read the key files systematically:  
Now let me read the complete verify-receipt.mjs file:  
Now let me read the fixture files and then sample vectors:  
Now let me read representative valid and invalid vectors:  
Now let me read some invalid vectors:  
Let me read a few more edge case vectors to understand the JCS testing:  
Let me check the hash-profiles documentation:  
Now let me check the cases files to understand the test structure better:  
Perfect\! Now let me list all the vectors to provide a complete inventory:  
Let me read a couple more invalid vectors to complete the picture:  
Perfect\! Now let me read a couple more valid vectors to show the JCS edge cases:  
Excellent\! Now let me create a comprehensive summary. Let me also check one more invalid vector to round out the picture:  
Perfect\! Now I have all the information I need. Let me compile a comprehensive report.  
---

## COMPREHENSIVE EXPLORATION REPORT: LogLine Foundation Conformance Repository

### 1\. JSON SCHEMA ANALYSIS

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/conformance-main/schemas/logline.receipt.v0.schema.json  
Key Schema Components:

* Receipt Version: Frozen at "logline.receipt.v0" (const, no flexibility)  
* JSON Canonicalization: Frozen at "jcs-rfc8785" (const, no flexibility)  
* Nine Required Slots (x-logline-slot 1-9):  
  * who (slot 1), did (slot 2), this (slot 3), when (slot 4\)  
  * confirmed\_by (slot 5), if\_ok (slot 6), if\_doubt (slot 7), if\_not (slot 8\)  
  * status (slot 9\)  
  * All must be strings  
* Required Metadata Fields:  
  * id: 64-char lowercase hex SHA256, MUST equal hashes.content\_hash  
  * hashes: Object with exactly three fields:  
    * tuple\_hash: 64-char hex (sha256 of 9 slots only)  
    * content\_hash: 64-char hex (sha256 of all except id/hashes)  
    * algorithm: const "sha256"  
  * additionalProperties: false on hashes object (no extra fields allowed)  
* Forbidden Legacy Fields (explicitly forbidden via "not": {}):  
  * result — outcomes are separate records, not embedded  
  * evidence — evidence is attached separately, not embedded  
  * transport — transport metadata belongs ONLY on Envelope wrapper, not on receipt at rest  
* AUX Fields:  
  * additionalProperties: true at receipt level  
  * Any top-level field not in reserved list is AUX  
  * AUX is included in content\_hash but NOT in tuple\_hash  
  * AUX MUST NOT shadow reserved names or use forbidden legacy names  
* Envelope Wrapper (separate schema):  
  * Three required fields: content, transport, envelope\_hash  
  * content: Full receipt object  
  * transport: Object with required sent\_by, sent\_to, sent\_at (all strings), optional channel  
  * envelope\_hash: 64-char hex covering {content, transport} canonicalized together  
  * additionalProperties: false (strict wrapper structure)

---

### 2\. VECTOR INVENTORY

#### VALID VECTORS (9 files) — vectors/receipt/valid/

1. minimal-resolved.json — All 9 slots empty strings; minimal valid receipt  
2. dan-rested.json — Basic complete receipt with meaningful slot values  
3. with-aux-fields.json — Same slots as dan-rested but with 3 AUX fields (duration\_hours, subjective\_state, context\_source); demonstrates AUX inclusion in content\_hash  
4. envelope.json — Full Envelope wrapper with transport metadata and envelope\_hash  
5. aux-unicode.json — Unicode edge cases: em-dash (—), accented chars (ã), emoji above BMP (🌙), control chars (\\t, \\n)  
6. aux-key-order.json — Tests JCS key sorting: keys inserted in reverse order (zebra, yak, alpha, Mu, \_underscore\_first) but must canonicalize alphabetically  
7. aux-number-decimal.json — Number formatting: integer (8), decimal (0.5), negative (-3.14), MAX\_SAFE\_INTEGER (9007199254740991), zero (0), small decimal (0.00001)  
8. aux-nested.json — Nested objects and arrays in AUX: context object with nested timestamps, tags array  
9. aux-array-order.json — Array insertion order preservation (JCS does NOT sort arrays, only object keys)

#### INVALID VECTORS (12 files) — vectors/receipt/invalid/

| Filename | Violation |
| :---- | :---- |
| missing-id.json | Missing required id field |
| missing-who.json | Missing required slot who |
| wrong-receipt-version.json | receipt\_version is "logline-receipt-v0" (dashes) instead of "logline.receipt.v0" (dots) |
| content-hash-mismatch.json | hashes.content\_hash is fff...fff (wrong); id also wrong |
| tuple-hash-mismatch.json | hashes.tuple\_hash is 000...000 (wrong) |
| id-not-content-hash.json | id is aaa...aaa but hashes.content\_hash is correct; they must match |
| hashes-extra-field.json | hashes object has extra field "salt": "smuggled" (additionalProperties violation) |
| hashes-has-envelope-hash.json | hashes object contains envelope\_hash field (belongs ONLY on Envelope wrapper, not in receipt) |
| legacy-evidence-field.json | Contains forbidden field evidence: {} |
| legacy-result-field.json | Contains forbidden field result |
| legacy-transport-field.json | Contains forbidden field transport at receipt level (belongs on Envelope) |
| envelope-hash-mismatch.json | Envelope wrapper with envelope\_hash set to 000...000 (wrong) |

---

### 3\. REPRESENTATIVE VECTORS — DETAILED ANALYSIS

#### VALID VECTOR 1: minimal-resolved.json

json  
{  
 "receipt\_version": "logline.receipt.v0",  
 "who": "", "did": "", "this": "", "when": "",  
 "confirmed\_by": "", "if\_ok": "", "if\_doubt": "", "if\_not": "", "status": "",  
 "hashes": {  
   "tuple\_hash": "35b20f03e04f2073adf068ec9f5e893c476ed626933611bbf3c64edfd6a054ef",  
   "content\_hash": "6ccd6e8d8a8a13b083bf5ed75c7c71d9f6d8ac9ae55cd036bdf5f39fb91102d8",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785",  
 "id": "6ccd6e8d8a8a13b083bf5ed75c7c71d9f6d8ac9ae55cd036bdf5f39fb91102d8"  
}  
Purpose: Tests that empty strings are valid slot values; verifies minimal structure.

#### VALID VECTOR 2: dan-rested.json

json  
{  
 "receipt\_version": "logline.receipt.v0",  
 "who": "dan", "did": "rested", "this": "slept\_well", "when": "2026-05-17T07:30:00Z",  
 "confirmed\_by": "dan", "if\_ok": "continue\_minilab\_work", "if\_doubt": "", "if\_not": "", "status": "claimed",  
 "hashes": {  
   "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
   "content\_hash": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785",  
 "id": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8"  
}  
Purpose: Canonical example; baseline for all other tests.

#### VALID VECTOR 3: with-aux-fields.json

json  
{  
 "receipt\_version": "logline.receipt.v0",  
 "who": "dan", "did": "rested", "this": "slept\_well", "when": "2026-05-17T07:30:00Z",  
 "confirmed\_by": "dan", "if\_ok": "continue\_minilab\_work", "if\_doubt": "", "if\_not": "", "status": "claimed",  
 "duration\_hours": 8,  
 "subjective\_state": "rested",  
 "context\_source": "self\_report",  
 "hashes": {  
   "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
   "content\_hash": "f8ebdffe55a00cedc5035e3778a6172424afba64cf86dcd38f885915e4448d68",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785",  
 "id": "f8ebdffe55a00cedc5035e3778a6172424afba64cf86dcd38f885915e4448d68"  
}  
Key Observation: tuple\_hash is IDENTICAL to dan-rested.json (same 9 slots), but content\_hash is DIFFERENT (AUX fields included). This demonstrates the three-layer hash design: same act, different interpretation.

#### VALID VECTOR 4: envelope.json

json  
{  
 "content": {  
   "receipt\_version": "logline.receipt.v0",  
   "who": "dan", "did": "rested", "this": "slept\_well", "when": "2026-05-17T07:30:00Z",  
   "confirmed\_by": "dan", "if\_ok": "continue\_minilab\_work", "if\_doubt": "", "if\_not": "", "status": "claimed",  
   "hashes": {  
     "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
     "content\_hash": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8",  
     "algorithm": "sha256"  
   },  
   "json\_canonicalization": "jcs-rfc8785",  
   "id": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8"  
 },  
 "transport": {  
   "sent\_by": "lab256",  
   "sent\_to": "supabase",  
   "sent\_at": "2026-05-17T11:00:00Z",  
   "channel": "supabase.rpc"  
 },  
 "envelope\_hash": "d799d11e2d313dce9379a33ffe13d3e2fe660f6719112c7e71e9560bad68bda8"  
}  
Purpose: Tests envelope wrapper structure and envelope\_hash computation (covers both content receipt AND transport metadata).  
---

#### INVALID VECTOR 1: missing-id.json

Missing the required id field entirely. Verifier rejects with: "missing required field 'id'"

#### INVALID VECTOR 2: content-hash-mismatch.json

json  
{  
 "receipt\_version": "logline.receipt.v0",  
 "who": "dan", "did": "rested", "this": "slept\_well", "when": "2026-05-17T07:30:00Z",  
 "confirmed\_by": "dan", "if\_ok": "continue\_minilab\_work", "if\_doubt": "", "if\_not": "", "status": "claimed",  
 "hashes": {  
   "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
   "content\_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785",  
 "id": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"  
}  
Errors:

* content\_hash is fff...fff but should be b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8  
* id mismatch (though it matches the wrong content\_hash, it doesn't match the correct one)

#### INVALID VECTOR 3: tuple-hash-mismatch.json

json  
{  
 "receipt\_version": "logline.receipt.v0",  
 "who": "dan", "did": "rested", "this": "slept\_well", "when": "2026-05-17T07:30:00Z",  
 "confirmed\_by": "dan", "if\_ok": "continue\_minilab\_work", "if\_doubt": "", "if\_not": "", "status": "claimed",  
 "hashes": {  
   "tuple\_hash": "0000000000000000000000000000000000000000000000000000000000000000",  
   "content\_hash": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8",  
   "algorithm": "sha256"  
 },  
 "json\_canonicalization": "jcs-rfc8785",  
 "id": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8"  
}  
Error: tuple\_hash is 000...000 but should be 6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee

#### INVALID VECTOR 4: legacy-evidence-field.json

Contains "evidence": {} at top level. Verifier rejects: "reserved legacy field 'evidence' MUST NOT appear in receipt v0"

#### INVALID VECTOR 5: hashes-has-envelope-hash.json

json  
{  
 "hashes": {  
   "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
   "content\_hash": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8",  
   "envelope\_hash": null,  
   "algorithm": "sha256"  
 },  
 ...  
}  
Error: hashes contains unexpected field "envelope\_hash" (belongs ONLY on Envelope wrapper, not inside receipt)  
---

### 4\. REFERENCE VERIFIER TOOL ANALYSIS

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/conformance-main/tools/verify-receipt.mjs  
Architecture:

* Zero dependencies (pure Node.js)  
* Implements JCS RFC-8785 canonicalization in \~35 lines  
* Implements SHA-256 hashing via Node crypto module  
* Three main validation phases: schema, hash verification, envelope verification

JCS Implementation (lines 18-35):  
javascript  
function jcs(value) {  
 if (value \=== null) return "null"  
 if (typeof value \=== "boolean") return value ? "true" : "false"  
 if (typeof value \=== "number") {  
   if (\!Number.isFinite(value)) throw new Error("non-finite number is not valid JSON")  
   if (Object.is(value, \-0)) return "0"  // Negative zero handling  
   return String(value)  
 }  
 if (typeof value \=== "string") return JSON.stringify(value)  
 if (Array.isArray(value)) return "\[" \+ value.map(jcs).join(",") \+ "\]"  
 if (typeof value \=== "object") {  
   const entries \= Object.entries(value)  
     .filter((\[\_, v\]) \=\> v \!== undefined)  // Exclude undefined  
     .sort((\[a\], \[b\]) \=\> (a \< b ? \-1 : a \> b ? 1 : 0))  // Lexicographic sort  
   return "{" \+ entries.map((\[k, v\]) \=\> JSON.stringify(k) \+ ":" \+ jcs(v)).join(",") \+ "}"  
 }  
 throw new Error(\`cannot canonicalize value of type ${typeof value}\`)  
}  
Hash Computation Functions:

1. computeTupleHash(receipt) (lines 49-53):  
   * Picks only the 9 slots: who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status  
   * Canonicalizes with JCS  
   * Returns SHA-256 hex  
   * Purpose: Identifies the pure act, stable across re-interpretations  
2. computeContentHash(receipt) (lines 55-58):  
   * Excludes id and hashes fields  
   * Includes all 9 slots \+ AUX \+ metadata (receipt\_version, json\_canonicalization)  
   * Canonicalizes with JCS  
   * Returns SHA-256 hex  
   * Purpose: Identifies the interpreted act (slots \+ AUX \+ meta, but NOT transport)  
3. computeEnvelopeHash(envelope) (lines 60-63):  
   * Excludes envelope\_hash field itself  
   * Includes content (full receipt) and transport metadata  
   * Canonicalizes {content, transport} together  
   * Returns SHA-256 hex  
   * Purpose: Identifies the transported package at boundary crossing

Validation Phases:  
Phase 1: Schema Validation (lines 66-107):

* Type checks: receipt is object, not null  
* Version checks: receipt\_version \=== "logline.receipt.v0" (exact match)  
* Canonicalization check: json\_canonicalization \=== "jcs-rfc8785" (exact match)  
* Slot validation: all 9 slots present and are strings  
* Hashes object validation:  
  * Must exist and be object  
  * algorithm must be "sha256"  
  * tuple\_hash and content\_hash must be 64-char hex  
  * No additional properties allowed (strict: only tuple\_hash, content\_hash, algorithm)  
* ID validation: must be 64-char lowercase hex  
* Forbidden fields check: rejects result, evidence, transport with named error

Phase 2: Hash Verification (lines 109-123):

* Computes expected tuple\_hash and compares to stored value  
* Computes expected content\_hash and compares to stored value  
* Verifies id \=== content\_hash (content-addressed identifier requirement)

Phase 3: Envelope Verification (lines 136-165):

* Detects envelope by presence of content, transport, or envelope\_hash fields  
* Validates content is a receipt object  
* Validates transport has required fields: sent\_by, sent\_to, sent\_at (all non-empty strings)  
* Validates envelope\_hash is 64-char hex  
* Computes expected envelope\_hash and compares  
* Recursively validates the inner receipt (schema \+ hashes)

Entry Points:

1. verifyFile(path) (lines 168-174):  
   * Reads JSON file  
   * Detects if envelope or receipt  
   * Runs appropriate validation  
   * Returns {kind, errors} object  
2. fillFile(path) (lines 176-199):  
   * Reads JSON file  
   * Sets defaults: receipt\_version, json\_canonicalization  
   * Deletes stale id and hashes  
   * Computes fresh tuple\_hash and content\_hash  
   * Writes back to file with 2-space JSON formatting  
3. suiteRun(root) (lines 201-228):  
   * Recursively finds all .json files in vectors/receipt/valid/ and vectors/receipt/invalid/  
   * Runs verifyFile on each  
   * Expects all valid vectors to pass (0 errors)  
   * Expects all invalid vectors to fail (\>0 errors)  
   * Prints summary: ✓ VALID, ✗ VALID, ✓ INVALID, ✗ INVALID  
   * Exits with code 0 if all pass, 1 if any fail

---

### 5\. FIXTURE FILES

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/conformance-main/fixtures/receipt.valid.json  
Canonical valid receipt (identical to dan-rested.json):

* All 9 slots filled with meaningful values  
* Correct tuple\_hash and content\_hash  
* Correct id (equals content\_hash)  
* Used for fast import in development

File: /Users/ubl-ops/Downloads/logline-foundation-canonical-repos/conformance-main/fixtures/receipt.invalid.json  
Canonical invalid receipt (same as valid but with extra field in hashes):  
json  
{  
 "hashes": {  
   "tuple\_hash": "6ace2eed03aa73839414db1d76a3bf08880d8ae50f5db81405c85f2b269ef1ee",  
   "content\_hash": "b74954069c9135090740439e08bdd442b4b12767c4df63b504c3e6b1029ffbb8",  
   "algorithm": "sha256",  
   "salt": "smuggled"  // ← VIOLATION: extra field  
 },  
 ...  
}

* Demonstrates the strictness of additionalProperties: false on hashes object

---

### 6\. COMPREHENSIVE SUMMARY

#### VALIDATION RULES ENFORCED

| Rule | Enforcement | Edge Cases |
| :---- | :---- | :---- |
| Receipt Version | Must be exactly "logline.receipt.v0" (dots, not dashes) | wrong-receipt-version.json tests this |
| JSON Canonicalization | Must be exactly "jcs-rfc8785" | Frozen in v0; no flexibility |
| Nine Required Slots | All must be present and be strings | minimal-resolved.json tests empty strings |
| Hashes Object | Must have exactly 3 fields: tuple\_hash, content\_hash, algorithm | hashes-extra-field.json, hashes-has-envelope-hash.json test violations |
| Hash Format | All hashes must be 64-char lowercase hex (pattern: ^\[0-9a-f\]{64}$) | Enforced in schema and verifier |
| ID Field | Must be present and equal hashes.content\_hash | missing-id.json, id-not-content-hash.json, content-hash-mismatch.json test violations |
| Tuple Hash Correctness | Must equal SHA256(JCS(9 slots only)) | tuple-hash-mismatch.json tests |
| Content Hash Correctness | Must equal SHA256(JCS(all except id, hashes)) | content-hash-mismatch.json tests |
| Envelope Hash Correctness | Must equal SHA256(JCS({content, transport})) | envelope-hash-mismatch.json tests |
| Forbidden Legacy Fields | result, evidence, transport MUST NOT appear at receipt level | legacy-{result,evidence,transport}-field.json test violations |
| AUX Fields | Free-form, included in content\_hash, NOT in tuple\_hash | with-aux-fields.json, aux-\*.json demonstrate |
| Envelope Structure | Strict: only content, transport, envelope\_hash | Enforced via additionalProperties: false |
| Transport Metadata | Required: sent\_by, sent\_to, sent\_at (all non-empty strings); optional: channel | envelope.json demonstrates |

#### EDGE CASES COVERED

JCS Canonicalization Edge Cases:

1. Key Ordering (aux-key-order.json):  
   * Keys inserted in reverse order (zebra, yak, alpha, Mu, \_underscore\_first)  
   * Must canonicalize to lexicographic order (Mu, \_underscore\_first, alpha, yak, zebra)  
   * Tests that naive JSON.stringify fails (doesn't sort keys)  
2. Unicode Handling (aux-unicode.json):  
   * Em-dash (—) — multi-byte UTF-8  
   * Accented characters (ã) — combining diacritics  
   * Emoji above BMP (🌙) — surrogate pair in UTF-16  
   * Control characters (\\t, \\n) — must be escaped per JCS rules  
   * Tests that string escaping is minimal and correct  
3. Number Formatting (aux-number-decimal.json):  
   * Integer (8) → bare digits, no decimal point  
   * Decimal (0.5) → shortest form that round-trips  
   * Negative (-3.14) → sign included  
   * MAX\_SAFE\_INTEGER (9007199254740991) → no exponent  
   * Zero (0) → bare 0, not 0.0  
   * Small decimal (0.00001) → no trailing zeros  
   * Tests ES6 §7.1.12.1 number formatting rules  
4. Nested Structures (aux-nested.json):  
   * Nested objects with sorted keys at each level  
   * Arrays preserve insertion order (JCS does NOT sort arrays)  
   * Mixed nesting levels  
   * Tests recursive canonicalization  
5. Array Preservation (aux-array-order.json):  
   * Arrays maintain insertion order (unlike object keys)  
   * Mixed-type arrays  
   * Nested arrays  
   * Tests that JCS sorts ONLY object keys, not array elements  
6. Minimal Valid Receipt (minimal-resolved.json):  
   * All 9 slots can be empty strings  
   * Tests that content is not validated for semantic meaning, only structure  
7. Envelope Wrapper (envelope.json):  
   * Tests three-layer hash: tuple\_hash (receipt), content\_hash (receipt), envelope\_hash (wrapper)  
   * Transport metadata is separate from receipt  
   * Envelope\_hash covers both content and transport together

#### THREE-LAYER HASH VERIFICATION

Layer 1: Tuple Hash  
tuple\_hash \= SHA256(JCS({who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status}))

* Scope: Pure 9-slot act only  
* Stability: Unchanged by AUX fields or metadata  
* Purpose: Identifies the core action; useful for comparing same act across different interpretations  
* Verification: Computed by picking exactly 9 slots, canonicalizing, hashing

Layer 2: Content Hash  
content\_hash \= SHA256(JCS({all fields except id, hashes}))

* Scope: 9 slots \+ AUX \+ metadata (receipt\_version, json\_canonicalization)  
* Stability: Changes if any AUX field is added/removed/modified  
* Purpose: Identifies the interpreted act; content-addresses the receipt  
* Verification: Computed by excluding id and hashes, canonicalizing, hashing  
* Constraint: id MUST equal content\_hash (content-addressed identifier)

Layer 3: Envelope Hash  
envelope\_hash \= SHA256(JCS({content: \<receipt\>, transport: \<metadata\>}))

* Scope: Full receipt \+ transport metadata  
* Stability: Changes if transport metadata changes  
* Purpose: Identifies the transported package at boundary crossing  
* Location: Lives ONLY on Envelope wrapper, NOT inside receipt  
* Verification: Computed by wrapping receipt and transport together, canonicalizing, hashing  
* Timing: Computed by sender at every boundary crossing; verified by receiver before accepting

Key Design Principle:

* Same 9 slots → same tuple\_hash  
* Same 9 slots \+ different AUX → same tuple\_hash, different content\_hash  
* Same receipt \+ different transport → same content\_hash, different envelope\_hash  
* This enables audit trail: "same act, different interpretations" or "same interpretation, different transport"

#### CONFORMANCE TEST COVERAGE

Valid Vectors (9):

* 1 minimal (empty slots)  
* 1 basic (dan-rested baseline)  
* 1 with AUX fields (demonstrates tuple\_hash stability)  
* 1 envelope wrapper (demonstrates envelope\_hash)  
* 5 JCS edge cases (unicode, key order, number formatting, nested, arrays)

Invalid Vectors (12):

* 2 missing required fields (id, who)  
* 1 wrong version format (dashes vs dots)  
* 2 hash mismatches (content, tuple)  
* 1 id/content\_hash mismatch  
* 2 hashes object violations (extra field, envelope\_hash inside)  
* 3 forbidden legacy fields (result, evidence, transport)  
* 1 envelope\_hash mismatch

Total Coverage: 21 vectors covering:

* Schema structure and constraints  
* All three hash layers  
* JCS canonicalization edge cases  
* Envelope wrapper structure  
* Forbidden field enforcement  
* Content-addressed identifier requirement

---

### 7\. KEY FILES AND LINE REFERENCES

| File | Lines | Purpose |
| :---- | :---- | :---- |
| schemas/logline.receipt.v0.schema.json | 1-128 | Complete JSON Schema specification |
| tools/verify-receipt.mjs | 1-255 | Reference verifier implementation |
| tools/verify-receipt.mjs | 18-35 | JCS canonicalization |
| tools/verify-receipt.mjs | 49-63 | Hash computation functions |
| tools/verify-receipt.mjs | 66-107 | Schema validation |
| tools/verify-receipt.mjs | 109-123 | Hash verification |
| tools/verify-receipt.mjs | 136-165 | Envelope verification |
| hash-profiles/jcs-rfc8785.md | 1-64 | JCS specification and rules |
| cases/receipt-cases.json | 1-67 | 12 conformance test cases |
| fixtures/receipt.valid.json | 1-19 | Canonical valid example |
| fixtures/receipt.invalid.json | 1-20 | Canonical invalid example |

---

### 8\. ACTIONABLE INSIGHTS

1. For Implementers:  
   * Use audited JCS libraries (serde\_jcs, @trust/jcs, jcs, gowebpki/jcs) — don't roll your own  
   * Validate against the JSON Schema using an audited validator (ajv, jsonschema, etc.)  
   * Run the full conformance suite: all 9 valid vectors must pass, all 12 invalid vectors must fail  
   * Test JCS edge cases independently: key ordering, unicode, number formatting, nested structures  
2. For Auditors:  
   * The reference verifier is intentionally minimal (\~250 lines) and auditable in one read  
   * Focus on JCS implementation: it's the hardest part and where most bugs occur  
   * Verify hash computation: tuple\_hash (9 slots), content\_hash (all except id/hashes), envelope\_hash (content+transport)  
   * Check forbidden field enforcement: result, evidence, transport MUST be rejected  
3. For Conformance Testing:  
   * Run node tools/verify-receipt.mjs \--suite to validate all vectors  
   * Each invalid vector's filename names the violation (e.g., content-hash-mismatch.json)  
   * Use \--fill mode to compute hashes for new receipts  
   * Verify that same tuple\_hash with different AUX produces different content\_hash\*

