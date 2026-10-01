
import { useState } from "react";
import "./App.css";

function App() {

  const [claim, setClaim] = useState("");

  const [submittedClaim, setSubmittedClaim] = useState("");

  const [investigating, setInvestigating] = useState(false);
 const [agentAResult, setAgentAResult] = useState(null);

const [agentBResult, setAgentBResult] = useState(null);
function startInvestigation() {
  if (!claim.trim()) {
    alert("Please enter a claim to investigate.");
    return;
  }

  setSubmittedClaim(claim.trim());

 setAgentAResult({
  position: "Not yet assessed",
  evidence: "No evidence retrieved yet.",
  reasoning: "Awaiting independent evaluation.",
  confidence: "Not assessed"
});

setAgentBResult({
  position: "Not yet assessed",
  evidence: "No evidence retrieved yet.",
  reasoning: "Awaiting independent evaluation.",
  confidence: "Not assessed"
});

  setInvestigating(true);
}

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">Ω</div>

          <div>
            <h2>OmegaTruth</h2>
            <span>Two Agents. One Truth.</span>
          </div>
        </div>

        <nav className="navigation">
          <button className="nav-item active">⌂ Home</button>
          <button className="nav-item">＋ New Investigation</button>
          <button className="nav-item">◷ History</button>
          <button className="nav-item">⌘ Reasoning Trace</button>
          <button className="nav-item">⚙ Settings</button>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot"></span>
          AI Research Lab
          <p>Better questions. Deeper truth.</p>
        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        <header className="topbar">
          <div>
            <p className="eyebrow">OMEGATRUTH / RESEARCH LAB</p>
            <h1>Explore the truth.</h1>
            <p className="subtitle">
              Different perspectives. Explainable conclusions.
            </p>
          </div>

          <div className="profile">
            <span className="online-dot"></span>
            Demo Mode
          </div>
        </header>

        {/* CLAIM INPUT */}

        <section className="hero-card">

          <div className="hero-content">
            <span className="section-label">
              ✦ START AN INVESTIGATION
            </span>

            <h2>
              Every claim deserves
              <br />
              <span className="gradient-text">
                a deeper look.
              </span>
            </h2>

            <p>
              Enter a claim and let two AI agents examine
              opposing perspectives through evidence and reasoning.
            </p>

            <div className="claim-box">

              <input
                type="text"
                placeholder="e.g. Does regular exercise improve sleep quality?"
                value={claim}
                onChange={(event) => setClaim(event.target.value)}
              />

              <button
  className="primary-button"
  onClick={startInvestigation}
>
  {investigating ? "Investigate Again →" : "Investigate →"}
</button>
            </div>

            <span className="demo-note">
              Sample interface · Backend integration pending
            </span>
          </div>

          <div className="hero-decoration">
            <div className="orbit orbit-one"></div>
            <div className="orbit orbit-two"></div>
            <div className="core">Ω</div>
            <span className="orbit-label">TRUTH ENGINE</span>
          </div>

        </section>
                

        {/* INVESTIGATION RESULTS */}

        {investigating && (
          <section className="panel">
            <span className="section-label">
              INVESTIGATION IN PROGRESS
            </span>

            <h2>Claim under examination</h2>

            <p>{submittedClaim}</p>

            <div className="agent-grid">
<article className="agent-card agent-a">
  <h3>Agent A</h3>

  <p>Independent Evaluator</p>

  <div className="agent-report">
    <p><strong>Position:</strong> {agentAResult.position}</p>

    <p><strong>Evidence:</strong> {agentAResult.evidence}</p>

    <p><strong>Reasoning:</strong> {agentAResult.reasoning}</p>

    <p><strong>Confidence:</strong> {agentAResult.confidence}</p>
  </div>

  <span className="agent-status">
   ● Awaiting reasoning engine
  </span>
</article>

<article className="agent-card agent-b">
  <h3>Agent B</h3>

  <p>Independent Evaluator</p>

  <div className="agent-report">
    <p><strong>Position:</strong> {agentBResult.position}</p>

    <p><strong>Evidence:</strong> {agentBResult.evidence}</p>

    <p><strong>Reasoning:</strong> {agentBResult.reasoning}</p>

    <p><strong>Confidence:</strong> {agentBResult.confidence}</p>
  </div>

  <span className="agent-status">
   ● Awaiting reasoning engine
  </span>
</article>

            </div>

            <p className="demo-note">
              Interface demonstration — actual agent reasoning is not connected yet.
            </p>
          </section>
        )}

        {/* AGENT CARDS */}

        <section className="agents-section"></section>

        {/* AGENT CARDS */}

        <section className="agents-section">

          <div className="section-heading">
            <div>
              <span className="section-label">THE RESEARCH TEAM</span>
              <h2>Meet the agents</h2>
            </div>

            <span className="demo-badge">DEMO DATA</span>
          </div>

          <div className="agent-grid">

            <article className="agent-card agent-a">

              <div className="agent-top">
                <div className="agent-avatar">A</div>

                <span className="agent-status">
                  ● Ready
                </span>
              </div>

              <h3>Agent A</h3>
             <p className="agent-role">Independent Evaluator</p>

              <p className="agent-description">
                Examines supporting evidence, factual claims,
                and logical consistency.
              </p>

              <div className="agent-tags">
                <span>Evidence</span>
                <span>Facts</span>
                <span>Logic</span>
              </div>

            </article>

            <article className="agent-card agent-b">

              <div className="agent-top">
                <div className="agent-avatar">B</div>

                <span className="agent-status">
                  ● Ready
                </span>
              </div>

              <h3>Agent B</h3>
              <p className="agent-role">Independent Evaluator</p>

              <p className="agent-description">
                Independently evaluates the topic, develops its own
position, and supports it with relevant evidence..
              </p>

              <div className="agent-tags">
                <span>Contradictions</span>
                <span>Bias</span>
                <span>Alternatives</span>
              </div>

            </article>

          </div>

        </section>
        {/* NEGOTIATION PANEL */}

{investigating && (

  <section className="negotiation-section">

    <div className="section-heading">
      <div>
        <span className="section-label">
          THE REASONING PROCESS
        </span>

        <h2>Agent Negotiation</h2>
      </div>

      <span className="demo-badge">
        PROTOTYPE
      </span>
    </div>

    <div className="negotiation-card">

      <div className="negotiation-step">
        <span className="step-number">01</span>

        <div>
          <h3>Independent Evaluation</h3>

          <p>
            Both agents establish their initial positions
            and assess available evidence independently.
          </p>
        </div>

        <span className="step-status">Pending</span>
      </div>

      <div className="negotiation-step">
        <span className="step-number">02</span>

        <div>
          <h3>Evidence Exchange</h3>

          <p>
            Agents present supporting evidence,
            examine opposing arguments, and identify conflicts.
          </p>
        </div>

        <span className="step-status">Pending</span>
      </div>

      <div className="negotiation-step">
        <span className="step-number">03</span>

        <div>
          <h3>Viewpoint Revision</h3>

          <p>
            Either agent may revise its position
            when credible evidence warrants a change.
          </p>
        </div>

        <span className="step-status">Pending</span>
      </div>

      <div className="negotiation-step">
        <span className="step-number">04</span>

        <div>
          <h3>Evidence-Based Resolution</h3>

          <p>
            The system evaluates whether the claim is supported,
            refuted, qualified, or remains unresolved.
          </p>
        </div>

        <span className="step-status">Pending</span>
      </div>

    </div>

    <p className="demo-note">
      Negotiation workflow preview · Actual reasoning engine not connected yet.
    </p>

  </section>

)}

        {/* BOTTOM DASHBOARD */}

        <section className="bottom-grid">

          <div className="panel">
            <span className="section-label">PROCESS</span>
            <h2>Investigation timeline</h2>

            <div className="timeline">

              <div className="timeline-step">
                <span>01</span>
                <p>Claim Input</p>
              </div>

              <div className="timeline-step">
                <span>02</span>
                <p>Agent Analysis</p>
              </div>

              <div className="timeline-step">
                <span>03</span>
                <p>Negotiation</p>
              </div>

              <div className="timeline-step">
                <span>04</span>
                <p>Resolution</p>
              </div>

            </div>
          </div>

          <div className="panel recent-panel">
            <span className="section-label">ACTIVITY</span>
            <h2>Recent investigations</h2>

            <div className="recent-item">
              <span className="recent-icon">◈</span>
              <div>
                <strong>Exercise and sleep</strong>
                <p>Sample investigation</p>
              </div>
              <span className="recent-status">Demo</span>
            </div>

            <div className="recent-item">
              <span className="recent-icon">◈</span>
              <div>
                <strong>Environmental impact of AI</strong>
                <p>Sample investigation</p>
              </div>
              <span className="recent-status">Demo</span>
            </div>

          </div>

        </section>

        <footer className="footer">
          <span>OMEGATRUTH © 2026</span>
          <span>Transparency · Reasoning · Trust</span>
        </footer>

      </main>

    </div>
  );
}

export default App;
