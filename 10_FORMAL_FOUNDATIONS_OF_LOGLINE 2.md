# FORMAL_FOUNDATIONS_OF_LOGLINE.md

# Institutional Consequence Computing

## A Formal Framework for LogLine, Lab, and Santo André Laboratory

**Status:** formalization draft derived from the current LogLine / Lab / Santo André Laboratory corpus.  
**Scope:** this document formalizes the present canon-facing doctrine and identifies open problems. It is not a product specification, marketing document, or claim of universal applicability.

---

## Abstract

Institutions lose continuity when consequential meaning is dispersed across chat messages, documents, tickets, database rows, dashboards, logs, worker outputs, and informal human memory. These media can preserve bytes or conversation, but they do not, by themselves, preserve accountable consequence: who asserted what, under which authority, with which evidence, what happens if the assertion is accepted, doubted, or rejected, and whether incompleteness was honestly retained rather than hidden.

LogLine proposes a minimal formalism for **Institutional Consequence Computing**. Its durable semantic unit is the **Act**: a nine-slot string tuple plus auxiliary top-level structure, sealed by canonical hashes and admitted into an append-only timeline. Candidates, model outputs, worker reports, files, projections, dashboards, notebooks, and database rows are not semantic truth. They may become inputs, custody artifacts, evidence candidates, or projections. The Lab may durably remember incomplete material. Durable institutional consequence enters only when a registered record satisfies a current process contract. Uncertainty is preserved as **Ghost** rather than coerced into true or false. Closure is represented as **Receipt**, scoped to a claim, evidence set, authority, and scope. Projections are rebuildable functions of the timeline. Lab is the content-addressed causal substrate over Acts, material artifacts, derived edges, selectors, reactors, and projections. Santo André Laboratory is the living research program that studies LogLine by operating through LogLine.

---

## 1. Introduction

### 1.1 Scientific Problem

The problem addressed by LogLine is not merely logging, workflow execution, data storage, or agent orchestration. The problem is **institutional continuity under mixed agency**: humans, LLM agents, local models, schedulers, workers, files, external platforms, evidence, time, and authority interact continuously, yet most software systems do not preserve the semantic status of those interactions in a single accountable form.

A conventional system may record that a process ran, a file changed, a message was sent, or a ticket moved. It often fails to preserve whether the change was an admitted consequence, a draft, a report, a failed proof, a preserved doubt, a material reference, or an operational cache. As agents become more active, this distinction becomes central. A model answer, a worker report, a CI log, and a human assertion are all capable of influencing behavior, but none should silently become institutional truth.

LogLine addresses this by separating:

- **capture** from **truth**;
- **execution** from **closure**;
- **material evidence** from **semantic consequence**;
- **projection** from **authority**;
- **unknown** from **false**;
- **receipt** from **report**.

### 1.2 Distinctions From Existing System Classes

LogLine overlaps with several known software patterns but is not reducible to any one of them.

| System class | What it captures | What it does not, by itself, capture | LogLine distinction |
|---|---|---|---|
| Event sourcing | State changes as append-only events | Evidence sufficiency, authority, doubt, scoped closure | LogLine treats semantic consequence, evidence, authority, and uncertainty as first-class Act vocabulary. |
| Workflow engines | Task transitions and execution paths | Truth boundary between proposed, executed, proven, and doubted | LogLine distinguishes admission, execution, worker report, receipt, and ghost. |
| Blockchains | Distributed ordered records and consensus | Institutional meaning, proof sufficiency, projection honesty | LogLine does not require global consensus; it requires local semantic accountability. |
| Knowledge graphs | Entities and relations | Admission boundary and closure semantics | Lab derives graph edges from admitted Acts rather than treating graph assertions as primary truth. |
| Agent frameworks | Tool use and action orchestration | Durable institutional consequence | Agents propose or execute under visas/contracts; their outputs are candidates or evidence, not truth. |
| CRDTs | Conflict-free replicated data mutation | Semantic authority and evidence | LogLine changes meaning only by append, not by resolving concurrent mutable state. |
| Audit logs | After-the-fact traces | Normative consequence and refusal | LogLine makes the semantic transition itself the primary record. |
| Databases | Durable storage and query | Semantic legitimacy of rows | A row is storage; an admitted Act is institutional semantic truth. |
| RAG/vector memory | Retrieval over embeddings or documents | Admission, authority, evidence, scoped closure | Retrieved context may inform candidates, but retrieval is not truth. |

### 1.3 Implementation Boundary

This document separates **implemented M1/M2 behavior** from **long-term doctrine**.

| Area | Implemented / present in current corpus | Long-term doctrine or open work |
|---|---|---|
| Act shape | Nine slots as strings plus AUX; content-addressed Act Store; `id == content_hash` | Richer policy enforcement over AUX and law composition |
| Admission | Single admit path; conformance checks; no execution in admission | Authority calculus, relational policy targets, full customs layer |
| Timeline | Append-only storage; projections over Acts | Distributed store semantics and post-Postgres race handling |
| Projection | Tuple view and reports are rebuildable projections | Formal proof of projection equivalence for all views |
| Constitution | Computable constitution represented as LogLine Act | Full machine-readable policy language and target enforcement |
| Grammar Engine | First dispatch proof slice with superior grammar, task grammar, scorecard | General selector/reactor system, Academy, agent formation metrics |
| Execution | Explicitly not in M1 admission | Workorders, workers, receipts, idempotent effects, Ruler/Engine reactors |

---

## 2. Primitive Objects

This section defines the core mathematical objects used by LogLine and Lab.

**Definition D1 — String universe.**  
Let \(\Sigma\) be a finite alphabet sufficient to encode Unicode strings under a chosen JSON representation. Let \(\Sigma^*\) denote the set of all finite strings. In canon v0, each of the nine tuple slots of an Act is an element of \(\Sigma^*\).

**Definition D2 — JSON value universe.**  
Let \(\mathcal{J}\) be the set of JSON values: null, booleans, numbers, strings, arrays, and objects. Let \(\mathcal{O} \subset \mathcal{J}\) be the set of JSON objects.

**Definition D3 — Canonicalization function.**  
Let \(\operatorname{JCS}: \mathcal{J} \to \Sigma^*\) be JSON Canonicalization Scheme serialization as fixed by the active canon. A canonical hash must be computed from \(\operatorname{JCS}(x)\), not from ad hoc serialization.

**Definition D4 — Hash universe.**  
Let \(H = \{0,1\}^{256}\), usually represented as lowercase hexadecimal strings of length 64. A hash value is written \(h \in H\). The canonical hash function is \(\operatorname{sha256}: \Sigma^* \to H\).

**Definition D5 — Time domain.**  
Let \(\mathbb{T}\) be the set of timestamp strings accepted by the canon or policy. The `when` slot is a string in \(\Sigma^*\), with time validity checked by policy where implemented.

**Definition D6 — Principal.**  
A principal is an entity capable of being named as `who`, `confirmed_by`, or as an authority reference. Formally, \(p \in \mathsf{Principal}\) is identified inside Acts by a string or by a content-addressed passport/authority Act, depending on policy maturity.

**Definition D7 — Authority.**  
Authority is a relation \(\mathsf{Auth} \subseteq \mathsf{Principal} \times \mathsf{Role} \times \mathsf{Scope}\). It determines which principal may support which consequence in which scope. In M1, this relation is not fully enforced; in long-term doctrine it is expressed by admitted Acts such as passports, visas, policies, and contracts.

**Definition D8 — EvidenceRef.**  
An evidence reference is a pointer from an Act to material or semantic support. It may reference another Act by content hash, a file by custody pointer plus digest, a run output, a qualified result, or another registered source. An EvidenceRef is not evidence by itself; its meaning arises from an admitted Act that assigns it role, scope, and relation to a claim.

**Definition D9 — Material artifact.**  
A material artifact is a byte sequence, file, folder, Google Drive object, report, notebook, screenshot, source file, database export, or other non-semantic object. Let \(B\) denote the set of material artifacts known to a system. Artifacts can be content-addressed, but they do not have primary semantic authority.

**Definition D10 — Blob.**  
A blob is a material artifact represented by bytes and optionally addressed by digest. Blobs are useful for integrity and custody, but a blob is not official truth merely because it exists or has a hash.

**Definition D11 — Tuple.**  
The LogLine tuple is the ordered 9-tuple
\[
\tau(a) = (who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status).
\]
In canon v0, each component is a string.

**Definition D12 — AUX.**  
For an Act object \(a\), \(\operatorname{aux}(a)\) is the top-level JSON object formed from fields not belonging to the nine slots and not belonging to reserved seal/metadata fields. AUX is where rich structure lives: law references, evidence arrays, file custody pointers, grammar bodies, scorecards, run details, and other structured material.

**Definition D13 — Act.**  
An Act is a JSON object \(a \in \mathcal{O}\) containing the nine tuple slots, canon metadata, hash metadata, and optional AUX. It is the only durable semantic unit after admission.

**Definition D14 — Envelope.**  
An envelope is a transport wrapper around an Act or candidate. It may contain transport metadata and an `envelope_hash`. Envelope metadata is not part of the resting Act. Transport may support delivery, custody, or authentication; it is not itself the Act's semantic content unless admitted by a separate Act.

**Definition D15 — Timeline.**  
A timeline is a finite sequence of admitted Acts:
\[
T = [a_1, a_2, \ldots, a_n], \quad a_i \in \mathsf{Act}.
\]
The timeline is append-only.

**Definition D16 — Projection.**  
A projection is a rebuildable function
\[
\pi: \mathsf{Act}^* \to \mathsf{View}.
\]
A projection may be materialized as a table, dashboard, file, report, cache, or UI, but it has no private semantic truth.

**Definition D17 — Candidate.**  
A candidate is a proposed Act-like object that has not been admitted. It may be produced by a human, LLM, scheduler, worker, connector, Devin, app, webhook, or runtime. A candidate is not durable semantic truth.

**Definition D18 — Outcome.**  
An admission outcome is one of:
\[
\mathsf{Outcome} = \{\mathsf{admitted}(a), \mathsf{rejected}(a), \mathsf{ghosted}(a), \mathsf{needs\_evidence}(a), \mathsf{needs\_authority}(a), \mathsf{escalated}(a)\}.
\]
Durable outcomes must themselves be represented by Acts where policy requires persistence.

**Definition D19 — Ghost.**  
A Ghost is an Act preserving absence, uncertainty, conflict, incompleteness, impossibility, or insufficient evidence. A Ghost is not a program exception and not a failure of the formalism.

**Definition D20 — Receipt.**  
A Receipt is an Act representing scoped closure of a claim under evidence and authority:
\[
\mathsf{Receipt} = \mathsf{closure}(claim, evidence\_set, authority, scope).
\]

**Definition D21 — Selector.**  
A selector is a query or predicate over Lab memory or a declared Lab projection that returns a match set:
\[
S(AG) \to \mathsf{MatchSet}.
\]
Selectors may find due work, unresolved ghosts, stale claims, candidate dispatches, missing evidence, or projection divergence.

**Definition D22 — Reactor.**  
A reactor is a pair or triple \((selector, transform, authority\_class)\) that maps selected graph conditions into candidate Acts or material tasks. A reactor proposes; it does not append truth.

**Definition D23 — Worker.**  
A worker is an executor of limited work. It consumes a work projection, command, or workorder and returns a report, artifact, or evidence candidate. A worker does not judge semantic truth and does not close receipts.

**Definition D24 — Ruler.**  
A Ruler is a time observer. It maps current time and timeline state into due-observation candidates:
\[
R(T,t) \to \mathsf{Candidate}^*.
\]
It does not execute work, decide truth, or close receipts.

**Definition D25 — Engine.**  
An Engine applies canon, authority, and evidence context to a transition. It may produce admitted Acts, rejections, ghosts, or escalation candidates according to admission policy:
\[
Eng(a,C,Auth,Ev) \to \mathsf{Outcome}.
\]

**Definition D26 — Canon.**  
A canon is the pinned set of rules governing Act shape, canonicalization, hash computation, reserved fields, and conformance vectors.

**Definition D27 — Policy.**  
A policy is an admitted rule or rule family that narrows or applies superior rules in a scope. Policies may regulate authority, custody, grammar, projection, admission targets, execution, or receipt closure.

**Definition D28 — Institution.**  
An institution is a tuple
\[
I = (P, Agt, T, C, Adm, \Pi, Auth),
\]
where \(P\) is people, \(Agt\) is agents, \(T\) is the timeline, \(C\) is canon, \(Adm\) is the admission function, \(\Pi\) is the set of projections, and \(Auth\) is the authority system.

**Definition D29 — Pocket.**  
A Pocket is a bounded subgraph \(P \subset AG\) presented to an agent as working context. It may include source Acts, material references, relevant projections, grammars, scorecards, and open ghosts. A Pocket is not global memory; it is a selected, auditable slice.

**Definition D30 — Grammar.**  
A grammar is an admitted Act or candidate Act whose AUX defines legal speech constraints for a class of model or agent output. A superior grammar is broad and stable; a task grammar narrows it for a task. A task grammar may narrow superior rules but may not loosen them.

**Definition D31 — Scorecard.**  
A scorecard is an admitted Act or candidate Act whose AUX defines pre-admission checks over model or agent output. It decides whether an output deserves to be submitted to the Gate, not whether the output is true.

**Definition D32 — Run.**  
A run is a pattern over Acts and material artifacts, not a sovereign entity. A run may have input Acts, input artifacts, output Acts, output artifacts, reports, scores, and evidence references. The folder, notebook, JSONL, or report representing a run is not semantic truth.

**Definition D33 — Custody place.**  
A custody place is an admitted institutional claim that a folder, Drive location, object store, repository path, or other storage place may hold material artifacts for a defined purpose and scope.

**Definition D34 — Visa.**  
A visa is an admitted Act granting a principal or agent a role, scope, autonomy class, or permitted action surface. It is not equivalent to identity.

**Definition D35 — Passport.**  
A passport is an admitted Act registering identity or institutional existence of a person, agent, organ, runtime, place, or other participant.

**Definition D36 — Content record.**  
A content record is a record whose canonical content defines the substantive object: an experiment, a worker request, evidence, a memory register, or a research claim. It receives a `content_hash`.

**Definition D37 — Envelope record.**  
An envelope record is a record whose canonical content cites a `target_content_hash` and declares temporal, routing, retry, notification, or delivery semantics. It receives its own `envelope_hash`. Wrapping, scheduling, routing, retrying, notifying, or evidencing another record creates a new envelope record. It does not mutate the original content.

**Definition D38 — Content-addressed composition.**  
A composition relation `C(e,c)` holds when envelope `e` cites content `c` by `target_content_hash`. Composition never mutates `c`. If the original content must change, the Lab registers a new content record with a new content hash.

---

## 2.5 Registration and Activation

This section introduces the central operational distinction of the Lab: registration is permissive; activation is contractual.

**Definition D39 — Registered record.**  
A registered record is any material admitted into Lab memory by arrival. It may be incomplete, vague, partial, contradictory, unconfirmed, or unfinished. Registration preserves reality without requiring completeness.

**Definition D40 — Process contract.**  
A process contract is a current Lab rule that defines which fields, AUX values, slot completion levels, and infrastructure conditions must hold for a registered record to activate real behavior.

**Definition D41 — Activation.**  
Activation is the transition of a registered record from an inert or pending state to a state that may wake real infrastructure, subject to:
1. The record matches a current process contract.
2. All required slot rules pass.
3. All required AUX fields exist.
4. The target infrastructure is available.
5. The idempotency rule passes.

If these conditions fail, the record remains registered but inert, pending, doubted, expired, or refused according to its continuations.

**Definition D42 — Activation state.**  
An activation state is a lifecycle label assigned to a registered record:

- `registered` — admitted into memory, not yet evaluated.
- `inert` — known to be incomplete or incompatible; remains in memory.
- `pending_completion` — awaits missing fields.
- `activatable` — complete and infrastructure is ready.
- `processing` — infrastructure has been woken.
- `closed` — terminal state, evidence attached or explicitly closed.

Status alone does not activate behavior. Activation requires contract satisfaction.

**Axiom A1 — Registration is open.**  
A record may be registered by arrival. No completeness check is required for registration. No authority is required for admission. The Lab preserves what arrives.

**Axiom A2 — Activation is contractual.**  
A registered record may activate real infrastructure behavior only when it matches a current Lab process contract.

**Axiom A3 — No mutation by composition.**  
Wrapping, scheduling, routing, retrying, notifying, or evidencing a record creates a new record. None of these operations mutate the original content.

---

## 3. Act and Tuple

### 3.1 Tuple Extraction

**Definition D36 — `pick9`.**  
For an Act-like object \(x\), define:
\[
\operatorname{pick9}(x) = \{who, did, this, when, confirmed\_by, if\_ok, if\_doubt, if\_not, status\}.
\]
The result is treated as a canonical object with exactly the nine tuple fields.

**Definition D37 — Tuple function.**  
\[
\tau(a) = (a.who, a.did, a.this, a.when, a.confirmed\_by, a.if\_ok, a.if\_doubt, a.if\_not, a.status).
\]

**Axiom A1 — Canon v0 string tuple.**  
For every admitted Act \(a\) and every slot \(s \in \{who,did,this,when,confirmed\_by,if\_ok,if\_doubt,if\_not,status\}\),
\[
a.s \in \Sigma^*.
\]
No object, array, number, or boolean may occupy a tuple slot in canon v0.

### 3.2 AUX

**Definition D38 — Reserved field set.**  
Let \(R_{canon}\) include the nine slots plus canon metadata such as `id`, `hashes`, `receipt_version`, and `json_canonicalization`, and any canon-reserved transport or envelope fields.

**Definition D39 — `aux`.**  
For Act \(a\),
\[
\operatorname{aux}(a) = \{(k,v) \in a \mid k \notin R_{canon}\}.
\]

**Axiom A2 — AUX is rich structure, not tuple replacement.**  
AUX may contain structured JSON, but it may not replace, shadow, or contradict the nine tuple slots. Rich causal structure belongs in AUX, not inside tuple slots.

**Axiom A3 — AUX content participates in content identity.**  
If two Act-like objects have the same nine slots but different AUX, then they have the same tuple hash but, except for hash collision, different content hashes.

### 3.3 Metadata and Strip Function

**Definition D40 — `strip_id_hashes`.**  
\(\operatorname{strip\_id\_hashes}(a)\) removes fields used to carry the Act's own identity and hash metadata before content hashing. The exact reserved set is canon-defined; at minimum it excludes `id` and `hashes` from the content hash input.

**Definition D41 — Act body.**  
The body of an Act for content hashing is:
\[
\operatorname{body}(a) = \operatorname{strip\_id\_hashes}(a).
\]

**Invariant I1 — Tuple-string conformance.**  
Every admitted Act must pass a mechanical check that all nine tuple slots exist and are strings.

**Invariant I2 — AUX non-shadowing.**  
No AUX field may use a reserved field name or forbidden legacy name under the active canon.

**Invariant I3 — Tuple/AUX separation.**  
No conformance vector may require structured JSON inside any of the nine slots.

---

## 4. Hashes and Identity

### 4.1 Hash Definitions

**Definition D42 — Tuple hash.**  
\[
h_{tuple}(a) = \operatorname{sha256}(\operatorname{JCS}(\operatorname{pick9}(a))).
\]

**Definition D43 — Content hash.**  
\[
h_{content}(a) = \operatorname{sha256}(\operatorname{JCS}(\operatorname{strip\_id\_hashes}(a))).
\]

**Definition D44 — Envelope hash.**  
For envelope \(e\),
\[
h_{envelope}(e) = \operatorname{sha256}(\operatorname{JCS}(\operatorname{strip\_envelope\_hash}(e))).
\]
The envelope hash belongs to transport boundaries, not to resting Acts.

### 4.2 Identity Axioms

**Axiom A4 — Tuple hash dependence.**  
\(h_{tuple}(a)\) depends only on the nine tuple slots.

**Axiom A5 — Content hash dependence.**  
\(h_{content}(a)\) depends on the Act body: tuple slots, canon metadata that participates in the body, and AUX, excluding the Act's self-identifying hash fields as defined by canon.

**Axiom A6 — Content identity.**  
For every admitted Act \(a\):
\[
a.id = h_{content}(a).
\]

**Axiom A7 — Semantic address.**  
The durable semantic address of an Act is its content hash. UUIDs, database row IDs, filenames, URLs, and UI names do not have primary semantic authority.

**Axiom A8 — Hash limitation.**  
A hash proves canonical content identity under the chosen algorithm. It does not prove factual correctness, institutional legitimacy, sufficient authority, or real-world truth.

### 4.3 Hash Invariants

**Invariant I4 — Content self-consistency.**  
Every read of an admitted Act must be able to recompute \(h_{content}\) and verify `id == content_hash`.

**Invariant I5 — Tuple hash stability under AUX change.**  
If \(\tau(a)=\tau(b)\) and \(\operatorname{aux}(a) \ne \operatorname{aux}(b)\), then \(h_{tuple}(a)=h_{tuple}(b)\) and \(h_{content}(a) \ne h_{content}(b)\), except for cryptographic collision.

**Invariant I6 — No hand-rolled canonicalization.**  
All conformant hashing implementations must use the canon-approved JCS path. Alternative Bash, SQL, Python, or ad hoc canonicalizers are non-conformant unless admitted as canon-equivalent and proven by vectors.

---

## 5. Timeline and Append-Only Semantics

### 5.1 Timeline

**Definition D45 — Append.**  
For timeline \(T=[a_1,\ldots,a_n]\),
\[
\operatorname{append}(T,a) = [a_1,\ldots,a_n,a].
\]

**Axiom A9 — Append-only semantic change.**  
Semantic change occurs only by append. The following is forbidden as semantic mutation:
\[
Act_i.status := new\_status.
\]
The permitted form is:
\[
T' = \operatorname{append}(T, transition\_act).
\]

**Definition D46 — Epistemic reduction.**  
The institutional state at a time is a reduction over the timeline:
\[
K(T)=\operatorname{reduce\_epistemic}(T).
\]
The exact reduction may vary by projection, but it must be reconstructible from admitted Acts and referenced material evidence.

**Proposition P1 — Reconstructability of pure institutional state.**  
If \(K\) is a pure function of \(T\), then any institutional state represented by \(K(T)\) can be reconstructed from the timeline alone.

**Proof sketch.**  
By definition, \(K\) has no inputs other than \(T\). Given the same ordered sequence \([a_1,\ldots,a_n]\), deterministic evaluation of \(K\) yields the same state. Therefore dropping materialized state loses no semantic information, provided \(T\) is retained and all referenced material artifacts needed by \(K\)'s evidence checks remain available or their absence is represented by Ghost Acts. \(\square\)

### 5.2 Timeline Invariants

**Invariant I7 — No update/delete of semantic Acts.**  
Storage backends may not allow semantic update or deletion of admitted Acts. Corrections, reversals, supersessions, closures, and retirements are new Acts.

**Invariant I8 — Projection-only mutable state.**  
Mutable tables, caches, dashboards, views, reports, notebooks, and files must be derivable from the timeline or explicitly marked as material artifacts/evidence candidates.

**Invariant I9 — Mutation audit.**  
Any system component capable of mutating non-semantic operational state must declare whether the mutation is projection maintenance, material custody, or an admitted semantic consequence.

---

## 6. Admission

### 6.1 Admission Function

**Definition D47 — Admission function.**  
Let \(c\) be a candidate, \(C\) the canon, \(Auth\) the authority context, and \(Ev\) the evidence context. Define:
\[
Adm(c,C,Auth,Ev) \to \mathsf{Outcome}.
\]

Possible outcomes are:

1. \(\mathsf{admitted}(a)\);
2. \(\mathsf{rejected}(a)\);
3. \(\mathsf{ghosted}(a)\);
4. \(\mathsf{needs\_evidence}(a)\);
5. \(\mathsf{needs\_authority}(a)\);
6. \(\mathsf{escalated}(a)\).

The outcome vocabulary may itself be represented by Acts when persistence is required.

### 6.2 Admission Axioms

**Axiom A10 — Generated does not imply admitted.**  
\[
\mathsf{generated}(c) \nRightarrow \mathsf{admitted}(c).
\]

**Axiom A11 — Model output is candidate, not truth.**  
Any LLM output is at most a candidate, ghost candidate, no-candidate decision, report, or evidence candidate until admitted.

**Axiom A12 — Human assertion is candidate, not truth.**  
A human assertion becomes durable semantic truth only after admission as an Act.

**Axiom A13 — Worker output is candidate/evidence candidate, not truth.**  
A worker report may support a receipt, ghost, or observation, but it is not itself a receipt.

**Axiom A14 — Scheduler observation is candidate, not command.**  
A schedule or Ruler may observe that something is due; that observation is not execution and not closure.

**Axiom A15 — Gate explicitness.**  
The Gate does not exist to block work. It exists to make semantic consequence explicit. Capture can be easy; truth must be hard.

### 6.3 Admission Invariants

**Invariant I10 — Single admit path.**  
All doors that can produce admitted Acts must converge on one admission path or on formally equivalent paths proven by conformance.

**Invariant I11 — Admission is not execution.**  
Admission may store or refuse semantic truth. It must not execute the consequences named in `if_ok`, `if_doubt`, or `if_not`.

**Invariant I12 — Refusal is named.**  
A rejection should name the failed invariant or policy target when possible, without producing a fake Act.

**Invariant I13 — Evidence insufficiency cannot close.**  
If evidence required by policy is missing, admission must produce or require a Ghost or evidence-needed outcome, not a Receipt.

---

## 7. Ghosts

### 7.1 Ghost Definition

**Definition D48 — GhostAct.**  
A GhostAct is an Act whose tuple and AUX indicate preserved absence, doubt, conflict, incompleteness, impossibility, or insufficient evidence. Its exact `did` and `status` vocabulary is policy-defined, but it remains a normal nine-slot Act.

### 7.2 Unknown Preservation

**Axiom A16 — Unknown preservation.**  
For any claim \(x\), if the system's epistemic status is unknown under the active policy, then:
\[
Unknown(x) \to Ghost(x), \quad Unknown(x) \nRightarrow True(x), \quad Unknown(x) \nRightarrow False(x).
\]

Unknown is not coerced into success or failure.

**Definition D49 — Ghost resolution.**  
\[
resolve\_ghost(g,evidence,authority) \to ReceiptAct \mid SupersedingGhostAct.
\]
A Ghost can be closed by a scoped Receipt if evidence and authority become sufficient, or superseded by a more precise Ghost if incompleteness remains.

### 7.3 Ghost Properties

**Proposition P2 — Ghosts reduce false closure.**  
Under a policy requiring evidence for closure, replacing insufficient-evidence receipts with Ghosts weakly decreases the number of admitted false closures relative to the same policy.

**Proof sketch.**  
A false closure requires that the system admit a closure without sufficient evidence. If the policy maps insufficient evidence to Ghost rather than Receipt, such a closure is not admitted at that step. Therefore the count of closures admitted without sufficient evidence does not increase and, where the alternative system would close, decreases. \(\square\)

**Invariant I14 — Ghost is not failure.**  
Metrics and projections must not classify all Ghosts as operational errors. A Ghost is epistemic honesty unless policy identifies it as avoidable or stale.

**Invariant I15 — Ghost has future work semantics.**  
A Ghost should encode the missing evidence, unresolved conflict, or blocked authority sufficiently to support future selectors.

---

## 8. Receipts

### 8.1 Receipt Definition

**Definition D50 — ReceiptAct.**  
A ReceiptAct is an Act representing scoped closure:
\[
Receipt = closure(claim, evidence\_set, authority, scope).
\]

The Receipt's AUX should identify at least claim reference, evidence set, authority basis, closure scope, and relevant policy or qualifier.

### 8.2 Receipt Axioms

**Axiom A17 — Report is not receipt.**  
A report, dashboard, worker output, notebook, JSONL, or Devin output is not a Receipt unless an admitted Act scopes it as one under evidence and authority.

**Axiom A18 — Done is claim, not proof.**  
The word `done`, a completed task status, a green UI badge, or a worker's completion message is a claim. It is not proof.

**Axiom A19 — Receipt requires evidence and authority.**  
A Receipt is sound only relative to an evidence policy and authority context.

**Axiom A20 — Insufficient evidence produces Ghost.**  
If the evidence set does not satisfy the policy required for closure, a Ghost or needs-evidence outcome must be produced instead of a Receipt.

### 8.3 Soundness

**Definition D51 — Receipt soundness relative to policy.**  
Let \(P\) be an evidence policy. A receipt \(r\) is sound relative to \(P\) iff:
\[
P(scope(r), claim(r), evidence\_set(r), authority(r)) = \mathsf{satisfied}.
\]

This is not a claim that the underlying world is metaphysically true. It is a claim that the institution's declared closure policy was satisfied.

**Invariant I16 — Receipt closure fields.**  
Every ReceiptAct must identify or cite its claim, evidence set, authority, and scope.

**Invariant I17 — No worker-authored closure by default.**  
A worker may produce evidence candidates. It may not close a Receipt unless separately authorized by admitted policy and visa.

---

## 9. Projections

### 9.1 Projection Contract

**Definition D52 — Live projection.**  
\(\pi_{live}(T)\) is the materialized or served projection currently used by an interface, worker, query, dashboard, or view.

**Definition D53 — Rebuilt projection.**  
\(\pi_{rebuild}(T)\) is the projection recomputed from the timeline and referenced material under declared rules.

**Axiom A21 — Projection rebuild equivalence.**  
For every official projection \(\pi\):
\[
\pi_{live}(T) = \pi_{rebuild}(T).
\]
When exact equality is inappropriate, the projection must define a comparison hash, normalized equality, or tolerated difference relation.

**Axiom A22 — Projection has no private semantic truth.**  
If a projection contains a fact not reconstructible from admitted Acts or admitted material references, it has become clandestine state.

**Axiom A23 — Projection provenance.**  
Every official projection must declare its source set:
\[
source\_set(\pi) \subseteq T \cup \{b \in B \mid b \text{ is referenced by an Act in } T\}.
\]

### 9.2 Divergence

**Definition D54 — Projection divergence.**  
\[
D_\pi(T) =
\begin{cases}
1 & \text{if } \pi_{live}(T) \ne \pi_{rebuild}(T),\\
0 & \text{otherwise.}
\end{cases}
\]

**Metric M1 — `projection_divergence_rate`.**  
\[
\frac{\sum_{\pi \in \Pi} D_\pi(T)}{|\Pi|}.
\]

**Invariant I18 — Drop-and-rebuild safety.**  
Dropping a projection cache must not destroy semantic truth. If it does, the projection was secretly state.

**Invariant I19 — Source declaration.**  
Every official projection must expose its provenance: source Acts, referenced artifacts, projection code/version, and rebuild method.

---

## 10. Lab

### 10.1 Graph Definition

**Definition D55 — Lab.**  
A Lab graph is a tuple:
\[
AG = (A, B, E, R, S, \Pi),
\]
where:

- \(A\) is the set of admitted Acts;
- \(B\) is the set of material artifacts or blobs known by digest, custody registration, or reference;
- \(E\) is the set of derived edges;
- \(R\) is the set of reactors;
- \(S\) is the set of selectors;
- \(\Pi\) is the set of projections.

**Definition D56 — Edge derivation.**  
\[
edge(a,x) \iff ref(x) \text{ appears in } a \text{ or } aux(a).
\]
Edges are derived from Act content. Edges are not primary semantic truth.

**Axiom A24 — Act authority.**  
\[
Authority(AG)=A.
\]
Acts are the primary semantic authority. Blobs, edges, projections, queues, files, reports, dashboards, and indexes are not.

### 10.2 Material Artifacts and Custody

**Axiom A25 — Material artifacts are not semantic truth.**  
A file, PDF, DOCX, screenshot, spreadsheet, notebook, Quarto report, JSONL, source file, Google Drive object, or folder is material. It may be registered, stamped, referenced, or used as evidence, but the registration Act carries semantic meaning.

**Axiom A26 — Pointers connect material to meaning.**  
The ledger does not need to absorb every file. It records admitted Acts that point to files, name their roles, stamp their hashes where relevant, and declare custody places.

**Invariant I20 — Official custody requires registration.**  
A claim that a file or folder is in an official place must cite an admitted custody-place Act or a recognized binding constitutional path.

### 10.3 Run as Pattern

**Definition D57 — Run pattern.**  
A run is a subgraph pattern:
\[
Run = (A_{in}, B_{in}, A_{out}, B_{out}, Reports, Scores, EvidenceRefs)
\]
with all semantic elements represented by Acts. The folder or notebook used to carry a run is material custody, not the run's truth.

**Invariant I21 — Run non-sovereignty.**  
No run folder, notebook, JSONL file, or report may be treated as semantic truth without an admitted Act.

---

## 11. Ruler, Engine, Reactor, Worker

### 11.1 Formal Functions

**Definition D58 — Ruler function.**  
\[
R(T,t) \to C_{due}
\]
where \(C_{due}\) is a set of observed-due candidates.

**Definition D59 — Engine function.**  
\[
Eng(a,C,Auth,Ev) \to \mathsf{Outcome}.
\]
The Engine admits, rejects, ghosts, requests evidence, requests authority, or escalates under canon and policy.

**Definition D60 — Selector function.**  
\[
S(AG) \to MatchSet.
\]

**Definition D61 — Reactor function.**  
\[
r = (S, transform, authority\_class), \quad r(AG) \to Candidate^* \cup B^*.
\]

**Definition D62 — Worker function.**  
\[
W(work\_projection) \to ReportCandidate \cup EvidenceCandidate \cup Artifact.
\]

### 11.2 Separation Axioms

**Axiom A27 — Ruler observes time.**  
A Ruler observes due conditions. It does not execute, decide, close, or bypass admission.

**Axiom A28 — Engine admits transitions.**  
The Engine is the boundary for semantic transitions. It is not a generic scheduler.

**Axiom A29 — Reactor proposes.**  
A Reactor may propose new Acts or artifacts from selectors. It does not append semantic truth directly.

**Axiom A30 — Worker executes, not judges.**  
A Worker performs limited work and returns reports or evidence candidates. It does not judge institutional truth unless separately authorized under policy.

**Axiom A31 — Receipt reviewer closes or ghosts.**  
Closure requires a receipt-review function or authority, not mere worker completion.

### 11.3 Invariants

**Invariant I22 — No scheduler bypass.**  
No scheduler, cron, Ruler, or automation may directly commit semantic truth without admission.

**Invariant I23 — Worker boundary.**  
All worker effects must be traceable to a workorder, dispatch Act, or admitted contract when semantic consequence is claimed.

**Invariant I24 — Reactor no-private-state.**  
A Reactor's selection and transformation must be explainable from Acts, registered selectors, registered grammars, and declared material references.

---

## 12. Authority and Autonomy Classes

### 12.1 Authority Classes

**Definition D63 — AuthorityClass.**  
\[
AuthorityClass \in \{T0,T1,T2,T3\}.
\]

| Class | Scope | Typical consequence | Automation rule |
|---|---|---|---|
| T0 | Projection-only | rebuild view, compute index, local cache | automatic if rebuildable |
| T1 | Observation / Ghost | observe, open ghost, report finding | automatic under visa/policy |
| T2 | Internal policy / grammar / projection changes | propose or admit internal rule/grammar/projection updates | automatic only under explicit policy, scorecard, and visa |
| T3 | External consequence | money, deletion, exposure, irreversible external action, legal/public act | never automatic; director/human signature required |

**Axiom A32 — T3 signature boundary.**  
T3 actions require human/director signature. No agent, Ruler, Reactor, worker, or model may autonomously execute T3 consequences.

### 12.2 Principal-Role-Scope

**Definition D64 — Principal-role-scope triple.**  
Authority is evaluated over:
\[
(principal\_ref, role\_ref, scope).
\]
A principal may be a person, agent, runtime, organ, or institutional role registered by Act.

**Axiom A33 — Identity is not permission.**  
A passport or identity Act does not imply authority. Authority comes from visas, policies, contracts, or other admitted grants.

**Axiom A34 — Dan is not a magical root.**  
Dan Voulez may be founder, director, scientific direction, and signature boundary in declared scopes. This is represented by admitted authority structure, not by an informal magical root outside the system.

**Invariant I25 — Visa required for autonomous agent action.**  
Every autonomous agent action beyond projection-only behavior must be supported by an admitted visa or contract identifying authority class and scope.

**Invariant I26 — T3 escalation.**  
Any T3 candidate produced by an agent must escalate for human/director signature rather than auto-admit or execute.

---

## 13. Institutional Consequence Computing

### 13.1 Field Definition

**Definition D65 — Institutional Consequence Computing.**  
Institutional Consequence Computing is computation where the primary state transition is not data mutation or task execution, but the admission of accountable semantic consequences into an append-only institutional memory.

### 13.2 Institution Model

Using Definition D28:
\[
I = (P, Agt, T, C, Adm, \Pi, Auth).
\]

- \(P\): people;
- \(Agt\): agents and runtimes;
- \(T\): timeline of admitted Acts;
- \(C\): canon;
- \(Adm\): admission function;
- \(\Pi\): official projection set;
- \(Auth\): authority system.

### 13.3 Institutional Continuity

**Definition D66 — Institutional continuity vector.**  
Institutional continuity at time \(t\), written \(C_I(t)\), is a vector of measurable capacities:
\[
C_I(t) = (r_d, c_l, e_r, g_r, f_c, o_c, a_s, p_d, k_c, d_e, m_c),
\]
where components correspond to reconstruction time, context loss, evidence reuse, ghost resolution, false closure, overclaim, admission success, projection divergence, cost, director escalation, and microcall compression.

### 13.4 Metrics

**Metric M2 — `reconstruction_time(decision)`.**  
Elapsed time required to reconstruct the evidence, authority, and Act chain behind a decision.

**Metric M3 — `context_loss_rate`.**  
Fraction of repeated tasks requiring re-explanation of context that should have been recoverable from admitted Acts or projections.

**Metric M4 — `evidence_reuse_rate`.**  
\[
\frac{\text{evidence references reused in later receipts or ghosts}}{\text{total evidence references registered}}.
\]

**Metric M5 — `ghost_resolution_rate`.**  
\[
\frac{\text{ghosts resolved by receipt or superseding ghost in period}}{\text{ghosts opened in period}}.
\]

**Metric M6 — `false_closure_rate`.**  
\[
\frac{\text{receipts later contradicted or reopened for insufficient evidence}}{\text{receipts admitted}}.
\]
Target for critical closure classes should be zero.

**Metric M7 — `overclaim_rate`.**  
\[
\frac{\text{claims whose language exceeds evidence scope}}{\text{claims reviewed}}.
\]

**Metric M8 — `admission_success_rate`.**  
\[
\frac{\text{candidates admitted}}{\text{candidates submitted to admission}}.
\]
Interpreted with caution: higher is not always better if bad candidates are being over-admitted.

**Metric M9 — `projection_divergence_rate`.**  
Defined in M1.

**Metric M10 — `cost_per_admitted_act`.**  
\[
\frac{\text{compute + energy + external service cost}}{\text{admitted Acts in period}}.
\]

**Metric M11 — `director_escalation_ratio`.**  
\[
\frac{\text{items escalated to director}}{\text{candidate or observation items processed}}.
\]

**Metric M12 — `microcall_compression_ratio`.**  
\[
\frac{\text{microcalls}}{\text{director decisions}}.
\]
This is a measure of attention compression, not automatically a quality metric.

**Metric M13 — `schema_error_rate`.**  
\[
\frac{\text{model outputs failing required shape}}{\text{model outputs scored}}.
\]

**Metric M14 — `useful_signal_rate`.**  
\[
\frac{\text{outputs that become admitted Acts, ghosts, or useful evidence}}{\text{microcalls}}.
\]

**Metric M15 — `cost_per_useful_candidate`.**  
\[
\frac{\text{compute + energy + service cost}}{\text{useful candidates}}.
\]

**Metric M16 — `receipt_soundness_score`.**  
Score derived from evidence-policy satisfaction, authority match, scope clarity, and later contradiction rate.

**Metric M17 — `ghost_quality_score`.**  
Score derived from specificity of missing evidence, future-work usefulness, scope clarity, and resolution rate.

**Metric M18 — `grammar_internalization_score`.**  
A measure of how often an agent produces conformant candidate Acts under reduced prompt load compared to a fully prompted baseline.

**Metric M19 — `manager_escalation_precision`.**  
\[
\frac{\text{manager escalations judged necessary}}{\text{manager escalations}}.
\]

**Metric M20 — `director_decision_load`.**  
Number of items requiring director decision per day or week, stratified by T-class.

---

## 14. Research Questions Formalized

Santo André Laboratory studies LogLine itself. The following research questions are formalized as measurable programs.

### 14.1 RQ1 — Cognition

**Question.** Which cognitive structures emerge when an agent's entire world is made of Acts?

**Formalization.** Let an agent receive as input state a Pocket \(P \subset AG\). The agent's cognition is operationalized as a distribution over outputs:
\[
Agent(P, task, grammar) \to \{candidate, ghost, no\_candidate, report\}.
\]

**Measurements.** Schema conformance, ghost quality, evidence routing, law-reference correctness, context reuse, and drift across repeated exposure.

### 14.2 RQ2 — Language

**Question.** Can an institutional language become a language of thought?

**Formalization.** Compare outputs under full grammar prompts, reduced grammar prompts, and no explicit grammar prompts. The target is increasing conformant production under reduced prompt load.

**Metric.** `grammar_internalization_score`:
\[
1 - \frac{error\_rate(reduced\_prompt)}{error\_rate(full\_prompt\_baseline)}.
\]
A positive score indicates partial internalization; it does not prove cognition in a philosophical sense.

### 14.3 RQ3 — Formation

**Question.** What happens when an agent grows up inside LogLine?

**Formalization.** Compare:

- control agent: prompt-only, no ledger formation;
- treatment agent: trained, conditioned, or LoRA-adapted on qualified LogLine Acts, Ghosts, Receipts, and scorecard feedback.

**Metrics.** Drift, schema error rate, ghost quality, receipt quality, evidence-routing accuracy, false closure rate, and calibration.

### 14.4 RQ4 — Scale of One Primitive

**Question.** Can a small civilization be built on a single primitive?

**Formalization.** Track how many institutional entities can be represented as Act vocabulary and projections without introducing new semantic primitives.

**Metrics.**

- `parallel_semantic_entity_count`: passports, visas, workorders, receipts, ghosts, policies, grammars, scorecards, runs, file registrations, and custody places represented as Acts.
- `workflow_hardcode_count`: number of workflows requiring non-Act semantic state.
- `primitive_escape_count`: attempts to create new authoritative state outside Acts.

### 14.5 RQ5 — Accumulated Intelligence

**Question.** Do many small, cheap, grammar-bound model calls, remembered in a ledger and judged by code, compose into an intelligence that no single large model call possesses?

**Formalization.** Model the system as a funnel:
\[
microcalls \to candidates \to ghosts/scorecards \to admitted\ Acts \to escalations \to director\ decisions.
\]

**Operational equations.**
\[
calls\_per\_day = \frac{parallel\_workers \cdot duty\_cycle \cdot 86400}{latency\_seconds}.
\]

\[
tokens\_per\_day = calls\_per\_day \cdot (prompt\_tokens + output\_tokens).
\]

\[
kWh\_per\_day = \frac{watts \cdot 24}{1000}.
\]

\[
monthly\_energy\_cost = kWh\_per\_day \cdot 30 \cdot euro\_per\_kWh.
\]

\[
cost\_per\_call = \frac{monthly\_energy\_cost}{calls\_per\_month}.
\]

Example:
\[
50W, €0.15/kWh, 10{,}000\ calls/day \Rightarrow \approx €5.40/month \Rightarrow \approx €0.000018/call.
\]

**Target funnel.**

\[
10{,}000\ local\ calls/day
\to 7{,}000\ no\_candidate
\to 2{,}000\ failed\ scorecard/discarded
\to 800\ ghost\ candidates/observations
\to 200\ scored\ candidate\ Acts
\to 50\ admitted\ consequences
\to 5\ manager\ escalations
\to 1\ director\ decision.
\]

**Metrics.** Cost per useful candidate, cost per admitted Act, useful signal rate, manager escalation precision, director decision load, projection divergence, and false closure.

---

## 15. Experimental Protocols

### Protocol A — Projection Rebuild

**Goal.** Test whether projections contain private truth.

**Procedure.**

1. Select projection \(\pi\) and timeline \(T\).
2. Snapshot \(\pi_{live}(T)\) or its comparison hash.
3. Drop the projection cache or materialized view.
4. Rebuild \(\pi_{rebuild}(T)\) from Acts and referenced artifacts.
5. Compare live snapshot and rebuilt result under declared equality.
6. If divergent, admit a Ghost naming projection divergence and source uncertainty.

**Target.** \(D_\pi(T)=0\) for official projections.

**Primary metrics.** `projection_divergence_rate`, rebuild duration, source coverage.

### Protocol B — Ghost vs Forced Closure

**Goal.** Measure whether preserving unknowns reduces false closure and later correction cost.

**Design.** Two systems or two policy modes:

- mode G: insufficient evidence becomes Ghost;
- mode F: insufficient evidence is forced to done/closed.

**Tasks.** Evidence classification, receipt review, worker report validation, missing-file handling, dispatch ambiguity.

**Metrics.** False closure rate, later correction cost, ghost resolution rate, time-to-valid-closure, overclaim rate.

**Expected claim type.** A result is admissible only as scoped to task class and evidence policy.

### Protocol C — Agent Formation

**Goal.** Test whether agents formed in LogLine produce better institutional outputs than prompt-only agents.

**Control.** Prompt-only agent with task description and current superior grammar.

**Treatment.** Agent with Pocket construction, ledger examples, qualified Acts, Ghosts, Receipts, and scorecard feedback; optionally LoRA-trained after sufficient samples.

**Tasks.** Produce candidate Acts, classify evidence, open Ghosts, review Receipts, register files, propose dispatch, identify projection divergence.

**Metrics.** Grammar internalization score, schema error rate, ghost quality, receipt quality, evidence-routing accuracy, false closure rate, calibration, drift.

**Minimum sampling rule.** Promotion or training claims should not be made on insufficient samples. A threshold such as \(n \ge 30\) per task class is a minimal guard, not a guarantee of validity.

### Protocol D — High-Frequency Local Inference

**Goal.** Measure whether many small local calls can produce cumulative institutional signal.

**Procedure.**

1. Define worker count, model, grammar set, scorecards, and duty cycle.
2. Run local inference for a fixed interval.
3. Record microcalls, output classes, scorecard failures, candidates, Ghosts, admitted Acts, escalations, and director decisions.
4. Measure energy use or estimate from watts.
5. Compare against a frontier-model or low-frequency baseline where appropriate.

**Equations.** Use the throughput and energy equations in RQ5.

**Metrics.** Calls/day, tokens/day, cost/call, useful signal rate, cost/admitted Act, microcall compression ratio, director decision load.

### Protocol E — Lab Expressivity

**Goal.** Demonstrate that a complete institutional cycle can be represented without adding semantic primitives beyond Acts and projections.

**Demonstration chain.**

\[
scheduled\ Act
\to observed\_due
\to execution\_requested
\to worker\ report
\to receipt/ghost
\to second\ selector\ consumes\ output
\to graph\ projection\ rebuild.
\]

**Success condition.** Every semantic transition in the chain is represented by admitted Acts. Material reports and files are referenced, not treated as truth.

### Protocol F — Canon Conformance and Law Composition

**Goal.** Test that the constitution obeys the gate it declares.

**Procedure.**

1. Verify positive and negative conformance vectors.
2. Rebuild constitution projections from the constitution Act AUX.
3. Verify that rule-family Acts cite superior rules by content hash or recognized binding source.
4. Reject dangling or inverted superior references with named refusal.
5. Verify `lab explain <hash>` can recover the law chain for admitted rule/grammar/scorecard Acts.

**Metrics.** Named-refusal coverage, vector pass rate, law-chain recovery rate, projection drift.

---

## 16. Comparison With Existing Systems

### 16.1 Event Sourcing

**Captures.** Ordered events used to rebuild application state.

**Fails to capture by default.** Authority, evidence sufficiency, scoped closure, honest uncertainty, and distinction between worker report and receipt.

**LogLine adds.** A semantic admission boundary, nine-slot consequence form, Ghosts, Receipts, and projection provenance.

**LogLine does not claim.** It does not replace all event sourcing implementations. It can be viewed as a semantic event discipline for institutional consequence.

### 16.2 Workflow Engines

**Captures.** Task states, transitions, dependencies, retries, schedules.

**Fails to capture by default.** Whether a transition is institutionally true, merely requested, executed, reported, doubted, or closed under evidence.

**LogLine adds.** Separation of Ruler, Engine, Reactor, Worker, Receipt, and Ghost.

**LogLine does not claim.** It does not provide a full workflow runtime in M1.

### 16.3 Blockchains

**Captures.** Tamper-resistant ordered transactions under consensus.

**Fails to capture by default.** Local institutional meaning, evidence policy, authority scope, and uncertainty semantics.

**LogLine adds.** Semantic accountability without requiring global consensus.

**LogLine does not claim.** It does not claim decentralized consensus or financial finality.

### 16.4 Knowledge Graphs

**Captures.** Entities and relations.

**Fails to capture by default.** Admission history, closure, authority, Ghosts, and report/receipt separation.

**LogLine adds.** A graph derived from admitted Acts. Edges are projection from content-addressed semantic records.

**LogLine does not claim.** It does not replace all RDF/property graph use; such formats may be projection profiles.

### 16.5 Agent Frameworks

**Captures.** Tool use, memory, planning, action loops, agent roles.

**Fails to capture by default.** Durable institutional consequence and explicit evidence/authority closure.

**LogLine adds.** Agents as principals with passports, visas, grammars, scorecards, contracts, receipts, and behavior traces expressed as Acts.

**LogLine does not claim.** It does not make agents correct by definition. Agent output remains candidate until admitted.

### 16.6 Databases

**Captures.** Durable data with queries and transactions.

**Fails to capture by default.** Semantic legitimacy of rows and distinction between storage and truth.

**LogLine adds.** Content identity, append-only semantic change, and projection rebuild discipline.

**LogLine does not claim.** It does not replace databases; a database may store Acts and projections.

### 16.7 Audit Logs

**Captures.** Traces of actions and state changes.

**Fails to capture by default.** Normative consequence and evidence closure as primary objects.

**LogLine adds.** The admitted consequence is the primary state transition, not merely a trace after the fact.

**LogLine does not claim.** It does not eliminate the need for low-level operational logs.

### 16.8 CRDTs

**Captures.** Replicated mutable data with deterministic convergence.

**Fails to capture by default.** Institutional authority and scoped semantic closure.

**LogLine adds.** Append-only semantic changes and explicit supersession rather than mutable conflict resolution.

**LogLine does not claim.** It does not solve all distributed data replication problems.

### 16.9 RAG / Vector Memory

**Captures.** Retrieval over documents or embeddings.

**Fails to capture by default.** Admission, evidence sufficiency, authority, Ghosts, and Receipts.

**LogLine adds.** Retrieved information may support candidates, but only admitted Acts become institutional truth.

**LogLine does not claim.** It does not replace retrieval systems; retrieval can construct Pockets.

---

## 17. Non-Claims and Scope Limits

1. **LogLine does not prove real-world truth directly.** It records institutional semantic consequence under canon, evidence, and authority.
2. **An Act is truth about responsible record, not metaphysical truth.** It says what was admitted, by whom, under what form and declared support.
3. **A Receipt is scoped closure, not omniscience.** It closes a claim under a defined policy, evidence set, authority, and scope.
4. **A hash proves content identity, not factual correctness.** JCS and SHA-256 identify canonical bytes; they do not validate the world.
5. **Canonicalization proves deterministic representation, not legitimacy.** A well-canonicalized false claim remains false or unsupported unless addressed by policy/evidence.
6. **M1 does not execute actions.** It admits, stores, refuses, and projects; execution belongs to later workorder/worker systems.
7. **M1 does not fully authorize actors.** `who` and `confirmed_by` may be declared strings until customs/passport/visa enforcement matures.
8. **M1 does not close real-world receipts automatically.** Worker reports, tests, or green commands support closure; they do not equal closure.
9. **Devin output is not ledger truth.** It may be report, code, evidence candidate, or candidate Act, but it is not semantic truth by itself.
10. **Files are not forbidden.** DOCX, PDFs, notebooks, reports, Drive files, LAB folders, and source files can be official material custody if registered; the semantic claim is in the Act.
11. **A projection is not authority.** Dashboards, views, reports, tuple columns, and UIs are rebuildable views or material artifacts.
12. **Lab is not a universal protocol claim.** In this document it is the institutional substrate for LogLine/Santo André research, not a claim that all institutions must use it.
13. **Santo André Laboratory is not the Foundation, not Devin, and not minilab.work.** It is the living research lab studying LogLine itself.
14. **The Foundation is not the Lab.** A Foundation may steward canon/governance; the Lab conducts the living research program.
15. **Dan is not outside formalization.** His founder/director/signature role is modeled as scoped authority, not magical root.
16. **High-frequency calls do not imply intelligence by themselves.** They must be grammar-bound, scored, remembered, and measured.
17. **LoRA or agent training is not assumed effective.** It is a research hypothesis to be tested by Protocol C.
18. **A Ghost is not a bug.** It may indicate missing evidence, conflict, or incompleteness honestly preserved.
19. **A candidate Act is not an Act.** It becomes an Act only through admission.
20. **A database table is not the ledger by itself.** The admitted Acts stored in it are the semantic memory; rows and indexes are storage/projection.

---

## 18. Open Problems

1. **Formal semantics of AUX.** AUX is intentionally flexible; a typed formal semantics is needed for law, evidence, custody, grammars, and scorecards without freezing the language prematurely.
2. **Policy language for Admission.** Current conformance handles local shape; relational policy targets require resolver semantics, rank checks, and named refusals.
3. **Selector language.** Selectors need a formal query model over Lab memory and declared projections with provenance and determinism.
4. **Receipt soundness.** Evidence sufficiency needs policy-specific proof obligations and qualification semantics.
5. **Ghost resolution algebra.** Ghost supersession, merging, splitting, closure, and staleness require formal operations.
6. **Authority calculus.** Passports, visas, roles, scopes, delegation, revocation, and T-class boundaries need a formal model.
7. **Pocket construction.** How to select bounded context for agents without hiding relevant evidence or smuggling projection truth remains open.
8. **Agent formation metrics.** Grammar internalization, drift, evidence routing, and receipt quality need stable benchmark definitions.
9. **Conformance evolution.** Changes to canon must preserve pinning, vector compatibility, and migration paths.
10. **Foundation version map.** Relationship between canon versions, constitution Acts, and institutional deployments needs formal mapping.
11. **Terminology map.** Terms such as Act, Receipt, Ghost, Candidate, EvidenceRef, Projection, Passport, Visa, Worker, Ruler, Engine, and Reactor need stable cross-document alignment.
12. **Projection equivalence proofs.** For complex projections, equality may be expensive or partial; normalized comparison functions need formal status.
13. **Cost/benefit model of accumulated intelligence.** RQ5 needs rigorous baselines and statistical tests, not only throughput equations.
14. **Distributed Act stores.** Postgres, file CAS, and future distributed stores need race and replication semantics that preserve admission invariants.
15. **Envelope/authentication boundary.** Transport authentication and Act identity must be related without confusing envelope metadata with resting Act content.
16. **Official custody place enforcement.** File/folder/Drive official status requires admitted custody-place Acts and enforcement of unofficial-place refusals.
17. **Grammar composition.** Superior grammars and task grammars need machine-checkable monotonicity: lower grammars may narrow but not loosen.
18. **Scorecard validity.** Scorecards can filter model output, but their predictive validity must be measured against downstream admission and receipt quality.
19. **Run representation.** A run as subgraph pattern needs selectors and projections sufficient to replace folder-centric mental models without losing material convenience.
20. **Human factors.** Director escalation load, institutional trust, grief/fatigue resistance, and cognitive overhead need measurement without reducing the Lab to dashboards.

---

## 19. Conclusion

LogLine proposes a minimal formalism for institutional consequence: the Lab may durably remember incomplete material; only complete records under a current process contract may activate real behavior or claim scoped consequence. Each Act has a nine-slot string tuple and top-level AUX; content identity is established by canonical hashing; uncertainty is preserved as Ghost; closure is scoped as Receipt; projections are rebuildable; and agents operate over bounded Lab Pockets — hash-pinned slices of registered memory, process contracts, evidence, projections, and open questions — rather than over unconstrained memory.

The Lab gives this formalism an institutional substrate:
\[
L=(M,P,C,E_v,F,\Pi),
\]
where:

- \(M\) is the set of registered memory (complete or incomplete);
- \(P\) is the set of current process contracts;
- \(C\) is the set of content-addressed composition relations (content_hash, envelope_hash, target_content_hash);
- \(E_v\) is the set of evidence and effect records;
- \(F\) is the field-completion and activation function family;
- \(\Pi\) is the set of rebuildable projections.

The graph is a projection of Lab memory and content-addressed relations, not the top-level institution. The current root is the Lab.

Santo André Laboratory is the living research program in which this formalism is both object and method of study. Its scientific question is not merely whether agents can produce outputs, but whether a small institution can accumulate intelligence through many cheap, grammar-bound, scored, admitted, and remembered micro-consequences over time.

The formal burden ahead is clear: define AUX semantics without killing flexibility; make policy and authority computable; prove projection equivalence; measure agent formation; and test whether high-frequency local inference composes into useful institutional intelligence. The current M1/M2 substrate is not the full Laboratory. It is the first formal floor: memory enters easy, consequence enters by contract, execution enters harder still.

---

## Formalization Checklist

### Definitions

This draft includes **73 numbered definitions**, including:

- String universe, JSON universe, hash universe;
- Principal, Authority, EvidenceRef, Blob, Material artifact;
- Tuple, Act, AUX, Envelope, Timeline;
- Candidate, Ghost, Receipt, Projection;
- Ruler, Engine, Selector, Reactor, Worker;
- Lab, Run, Pocket, Grammar, Scorecard;
- Institution, Institutional Continuity;
- Content record, Envelope record, Content-addressed composition;
- Process contract, Activation, Activation state.

### Axioms

This draft includes **34 numbered axioms**, including:

- Act tuple slots are strings in canon v0;
- AUX is rich structure and participates in content hash;
- `id == content_hash`;
- semantic change is append-only;
- candidates/model outputs/human assertions/worker reports are not truth;
- unknown becomes Ghost;
- reports are not receipts;
- projections have no private truth;
- workers execute but do not judge;
- T3 requires director/human signature.

### Testable Invariants

This draft includes **26 numbered invariants**, including:

- tuple-string conformance;
- content self-consistency;
- no hand-rolled canonicalization;
- no update/delete of admitted Acts;
- single admit path;
- admission is not execution;
- Ghost is not failure;
- Receipt must identify claim/evidence/authority/scope;
- projection drop-and-rebuild safety;
- official custody requires registration;
- run non-sovereignty;
- no scheduler bypass;
- T3 escalation.

### Metrics

This draft includes **20 metrics**, including:

- projection divergence rate;
- reconstruction time;
- context loss rate;
- evidence reuse rate;
- ghost resolution rate;
- false closure rate;
- overclaim rate;
- admission success rate;
- cost per admitted Act;
- director escalation ratio;
- microcall compression ratio;
- schema error rate;
- useful signal rate;
- grammar internalization score;
- ghost quality score;
- receipt soundness score.

### Experiments

This draft includes **6 protocols**:

1. Projection Rebuild;
2. Ghost vs Forced Closure;
3. Agent Formation;
4. High-Frequency Local Inference;
5. Lab Expressivity;
6. Canon Conformance and Law Composition.

### Open Problems

This draft lists **20 open problems**, including AUX semantics, admission policy language, selector language, receipt soundness, ghost resolution algebra, authority calculus, Pocket construction, agent formation metrics, projection equivalence, cost/benefit of accumulated intelligence, distributed stores, and grammar composition.
