import { useState } from "react";
import React from "react";
export default function ReloadButton({ initialTs, onDone }) {
    const [busy, setBusy] = useState(false);
    const BASE_URL = "https://legendary-halibut-pwwxp7xvwxwf995-8000.app.github.dev";

    const pollUntilNew = async () => {
      const metricsUrl = `${BASE_URL}/api/metrics`;
      while (true) {
        await new Promise((res) => setTimeout(res, 2000)); // 2-sec poll
        console.log("🔄 Polling metrics at:", metricsUrl);
        const m = await fetch(metricsUrl).then((r) => {
          if (!r.ok) throw new Error(`Metrics fetch failed (${r.status})`);
          return r.json();
        });
        if (m.generated && m.generated !== initialTs) return;
      }
    };
    
    const handleClick = async () => {
      setBusy(true);
      const reloadUrl = `${BASE_URL}/api/reload`;
      try {
        console.log("🚀 Triggering reload at:", reloadUrl);
        const r = await fetch(reloadUrl, { method: "POST" });
        if (!r.ok) throw new Error(`Reload failed (${r.status})`);
        await pollUntilNew();  // wait until metrics timestamp changes
        await onDone();        // refresh UI
      } catch (e) {
        console.error(e);
        alert(e.message || "Reload failed – check server log.");
      } finally {
        setBusy(false);
      }
    };
    

  return (
    <button
      onClick={handleClick}
      disabled={busy}
      className={`px-4 py-1 rounded text-white ${
        busy ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
      }`}
    >
      {busy ? "Regenerating…" : "Regenerate Data"}
    </button>
  );
}
