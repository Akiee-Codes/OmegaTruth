import { useState } from "react";
import "./App.css";

const API = "https://omegatruth-backend.onrender.com";

function SourceList({ items, empty }) {
  if (!items?.length) return <p className="muted">{empty}</p>;

  return (
    <div className="sources">
      {items.map((s, i) => (
        <div className="source" key={(s.url || s.title || i) + i}>
          <div className="source-top">
            <strong>{s.source || "Web source"}</strong>
            <span>{s.role}</span>
          </div>

          <h4>{s.title}</h4>

          {s.snippet && <p>{s.snippet}</p>}

          {s.published && <small>{s.published}</small>}

          {s.url && (
            <a href={s.url} target="_blank" rel="noreferrer">
              Open source ↗
            </a>
          )}
        </div>
      ))}
    </div>
  );
}

function App() {
  const [claim, setClaim] = useState("");
  const [data, setData] = useState(null);
  const [page, setPage] = useState("home");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function investigate() {
    if (!claim.trim()) return;

    setLoading(true);
    setError("");

    try {
      const r = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: claim.trim(),
        }),
      });

      const body = await r.json();

      if (!r.ok) {
        throw new Error(body.detail || "Backend request failed");
      }

      setData(body);
      setPage("investigation");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function newInvestigation() {
    setData(null);
    setClaim("");
    setError("");
    setPage("home");
  }

  const nav = data
    ? [
        ["investigation", "01", "Positions"],
        ["evidence", "02", "Independent evidence"],
        ["conclusion", "03", "Exchange & conclusion"],
      ]
    : [];

  return (
    <div className="app">
      <header className="header">
        <button
          className="brand brandbutton"
          onClick={() => (data ? setPage("dashboard") : setPage("home"))}
        >
          Ω OMEGATRUTH
        </button>

        <div className="header-center">
          Multi-agent evidence negotiation
        </div>

        <div className="header-actions">
          {data && (
            <button
              className="navbutton"
              onClick={() => setPage("dashboard")}
            >
              Dashboard
            </button>
          )}

          {data && (
            <button className="ghost" onClick={newInvestigation}>
              New investigation
            </button>
          )}
        </div>
      </header>

      {!data && page === "home" && (
        <main className="landing home-page">
          <div className="hero">
            <span className="eyebrow">
              TWO AGENTS · INDEPENDENT RESEARCH · NEGOTIATION
            </span>

            <h1>
              Give us <em>any claim.</em>
              <br />
              Let the evidence argue.
            </h1>

            <p>
              Agent A searches for supporting evidence. Agent B independently
              searches for contradictions and limitations. They exchange
              evidence, reassess, and produce an evidence-based conclusion.
            </p>

            <div className="input-row">
              <input
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && investigate()}
                placeholder="e.g. Does regular exercise improve sleep quality?"
              />

              <button onClick={investigate} disabled={loading}>
                {loading ? "Investigating…" : "Investigate →"}
              </button>
            </div>

            <div className="examples">
              <span>Try:</span>

              <button
                onClick={() =>
                  setClaim("Does regular exercise improve sleep quality?")
                }
              >
                exercise & sleep
              </button>

              <button
                onClick={() => setClaim("Is remote work more productive?")}
              >
                remote work
              </button>

              <button
                onClick={() => setClaim("Does caffeine improve concentration?")}
              >
                caffeine & focus
              </button>
            </div>

            {error && <div className="error">{error}</div>}
          </div>

          <div className="flow">
            <div>
              <b>A</b>
              <span>Support</span>
              <small>Independent search</small>
            </div>

            <i>→</i>

            <div>
              <b>↔</b>
              <span>Exchange</span>
              <small>Evidence shared</small>
            </div>

            <i>→</i>

            <div>
              <b>B</b>
              <span>Challenge</span>
              <small>Independent search</small>
            </div>

            <i>→</i>

            <div>
              <b>✓</b>
              <span>Resolve</span>
              <small>Reassessment</small>
            </div>
          </div>
        </main>
      )}

      {data && page === "dashboard" && (
        <main className="page dashboard-page">
          <div className="page-heading">
            <span className="eyebrow dark">DASHBOARD</span>

            <h1>Your investigation</h1>

            <p>
              Move between the investigation pages without losing any results.
              Nothing refreshes until you start a new investigation.
            </p>
          </div>

          <div className="dashboard-card card">
            <span className="claimbar-label">CURRENT CLAIM</span>

            <h2>{data.question}</h2>

            <div className="dashboard-grid">
              <button
                className="dashboard-option"
                onClick={() => setPage("investigation")}
              >
                <b>01</b>
                <span>Agent positions</span>
                <small>
                  See the two independently generated positions.
                </small>
              </button>

              <button
                className="dashboard-option"
                onClick={() => setPage("evidence")}
              >
                <b>02</b>
                <span>Independent evidence</span>
                <small>
                  See each agent's research separately.
                </small>
              </button>

              <button
                className="dashboard-option"
                onClick={() => setPage("conclusion")}
              >
                <b>03</b>
                <span>Exchange & conclusion</span>
                <small>
                  See evidence exchange, viewpoint changes, and the final
                  result.
                </small>
              </button>

              <button
                className="dashboard-option reasoning-option"
                onClick={() => setPage("reasoning")}
              >
                <b>↳</b>
                <span>Transparent reasoning</span>
                <small>
                  Open the full negotiation trace and audit trail.
                </small>
              </button>
            </div>

            <button className="new-large" onClick={newInvestigation}>
              ＋ Start a new investigation
            </button>
          </div>
        </main>
      )}

      {data && page !== "dashboard" && (
        <main className="page investigation-page">
          <div className="page-nav">
            {nav.map(([key, num, label]) => (
              <button
                key={key}
                className={page === key ? "active" : ""}
                onClick={() => setPage(key)}
              >
                {num && <b>{num}</b>} {label}
              </button>
            ))}
          </div>

          {page === "investigation" && (
            <>
              <div className="claimbar">
                <span>CLAIM UNDER EXAMINATION</span>
                <h2>{data.question}</h2>
              </div>

              <section className="agents">
                <article className="agent card a">
                  <div className="agenthead">
                    <div className="avatar">A</div>

                    <div>
                      <h2>Agent A</h2>
                      <span>Supporting investigator</span>
                    </div>

                    <strong>{data.agent_x.position}</strong>
                  </div>

                  <div className="position">
                    {data.agent_x.claimText}
                  </div>

                  <p>{data.agent_x.reasoning}</p>

                  <div className="confidence">
                    Initial confidence:{" "}
                    {Math.round(data.agent_x.confidence * 100)}%
                  </div>
                </article>

                <article className="agent card b">
                  <div className="agenthead">
                    <div className="avatar">B</div>

                    <div>
                      <h2>Agent B</h2>
                      <span>Counter-investigator</span>
                    </div>

                    <strong>{data.agent_y.position}</strong>
                  </div>

                  <div className="position">
                    {data.agent_y.claimText}
                  </div>

                  <p>{data.agent_y.reasoning}</p>

                  <div className="confidence">
                    Initial confidence:{" "}
                    {Math.round(data.agent_y.confidence * 100)}%
                  </div>
                </article>
              </section>

              <div className="next-row">
                <button onClick={() => setPage("evidence")}>
                  Continue to independent evidence →
                </button>
              </div>
            </>
          )}

          {page === "evidence" && (
            <>
              <div className="claimbar">
                <span>02 · INDEPENDENT EVIDENCE</span>

                <h2>{data.question}</h2>

                <p>
                  These sources were retrieved independently before either
                  agent saw the other agent's evidence.
                </p>
              </div>

              <section className="agents evidence-page-grid">
                <article className="agent card a">
                  <div className="agenthead">
                    <div className="avatar">A</div>

                    <div>
                      <h2>Agent A evidence</h2>
                      <span>Supporting search only</span>
                    </div>
                  </div>

                  <h3>Evidence supporting the claim</h3>

                  <SourceList
                    items={data.agent_x.evidence}
                    empty="No supporting evidence was retrieved."
                  />
                </article>

                <article className="agent card b">
                  <div className="agenthead">
                    <div className="avatar">B</div>

                    <div>
                      <h2>Agent B evidence</h2>
                      <span>Counter-search only</span>
                    </div>
                  </div>

                  <h3>Evidence challenging the claim</h3>

                  <SourceList
                    items={data.agent_y.evidence}
                    empty="No counter-evidence was retrieved."
                  />
                </article>
              </section>

              <div className="next-row split">
                <button onClick={() => setPage("investigation")}>
                  ← Positions
                </button>

                <button onClick={() => setPage("conclusion")}>
                  Continue to exchange & conclusion →
                </button>
              </div>
            </>
          )}

          {page === "conclusion" && (
            <>
              <div className="claimbar">
                <span>03 · EVIDENCE EXCHANGE & FINAL CONCLUSION</span>

                <h2>{data.question}</h2>
              </div>

              <section className="card exchange">
                <div className="sectiontitle">
                  <span>EVIDENCE EXCHANGE</span>
                  <h2>What each agent received</h2>
                </div>

                <div className="exchangegrid">
                  <div>
                    <h3>Agent A receives Agent B's evidence</h3>

                    <SourceList
                      items={
                        data.negotiation.evidence_exchange.agent_a_received
                      }
                      empty="Nothing was retrieved by Agent B."
                    />
                  </div>

                  <div>
                    <h3>Agent B receives Agent A's evidence</h3>

                    <SourceList
                      items={
                        data.negotiation.evidence_exchange.agent_b_received
                      }
                      empty="Nothing was retrieved by Agent A."
                    />
                  </div>
                </div>
              </section>

              <section className="final conclusion-card">
                <span>FINAL RESOLUTION</span>

                <h1>{data.negotiation.status}</h1>

                <p>{data.negotiation.reason}</p>

                <div className="viewpoint-grid">
                  {data.negotiation.revisions.map((r, i) => (
                    <div className="viewpoint" key={i}>
                      <h3>{r.agent}</h3>

                      <p>
                        <b>Initial:</b> {r.initial_position}
                      </p>

                      <p>
                        <b>After evidence exchange:</b>{" "}
                        {r.revised_position}
                      </p>

                      <p>{r.reason}</p>
                    </div>
                  ))}
                </div>

                <div className="final-statement">
                  <span>CONCLUSION</span>
                  <p>{data.negotiation.reason}</p>
                </div>
              </section>

              <div className="next-row split">
                <button onClick={() => setPage("evidence")}>
                  ← Independent evidence
                </button>

                <button onClick={() => setPage("dashboard")}>
                  ← Dashboard
                </button>
              </div>
            </>
          )}

          {page === "reasoning" && (
            <>
              <div className="claimbar">
                <span>TRANSPARENT REASONING</span>

                <h2>{data.question}</h2>

                <p>
                  This audit page is intentionally separate from the main
                  investigation pages.
                </p>
              </div>

              <section className="card reasoning-card">
                <div className="sectiontitle">
                  <span>NEGOTIATION TRACE</span>

                  <h2>How the agents changed their viewpoints</h2>
                </div>

                <div className="trace">
                  {data.negotiation.negotiation.map((x, i) => (
                    <div className="traceitem" key={i}>
                      <b>{String(i + 1).padStart(2, "0")}</b>
                      <p>{x}</p>
                    </div>
                  ))}
                </div>

                <div className="revisions">
                  {data.negotiation.revisions.map((r, i) => (
                    <div key={i}>
                      <h3>{r.agent}</h3>

                      <p>
                        <b>Initial:</b> {r.initial_position}
                      </p>

                      <p>
                        <b>Revised:</b> {r.revised_position}
                      </p>

                      <p>{r.reason}</p>
                    </div>
                  ))}
                </div>

                <div className="limits">
                  <h3>Transparency & limitations</h3>

                  {data.negotiation.limitations.map((x, i) => (
                    <p key={i}>• {x}</p>
                  ))}
                </div>
              </section>

              <div className="next-row">
                <button onClick={() => setPage("dashboard")}>
                  ← Back to dashboard
                </button>
              </div>
            </>
          )}
        </main>
      )}
    </div>
  );
}

export default App;